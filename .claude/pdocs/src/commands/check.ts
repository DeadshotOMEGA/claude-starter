import { existsSync, statSync, readdirSync } from 'fs';
import { join } from 'path';
import chalk from 'chalk';
import { validateDocument } from '../lib/validation.js';
import { detectDocType, resolveTypeAlias, getSkillForType } from '../lib/detection.js';
import { loadRegistry, updateDocumentStatus, getDocument } from '../lib/registry.js';
import { repairDocument, getFixableIssues } from '../lib/repair.js';
import type { DocType, ValidationResult, ValidationError } from '../types.js';

interface CheckOptions {
  type?: string;
  strict?: boolean;
  json?: boolean;
  recursive?: boolean;
  fix?: boolean;
  dryRun?: boolean;
}

/**
 * Find all markdown/yaml files in a directory
 */
function findDocumentFiles(dirPath: string): string[] {
  const files: string[] = [];

  function walk(dir: string) {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        // Skip node_modules, .git, etc.
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
          walk(fullPath);
        }
      } else if (entry.isFile()) {
        if (entry.name.endsWith('.md') || entry.name.endsWith('.yaml') || entry.name.endsWith('.yml')) {
          files.push(fullPath);
        }
      }
    }
  }

  walk(dirPath);
  return files;
}

/**
 * Format verbose error output
 */
function formatVerboseError(
  filePath: string,
  result: ValidationResult,
  docType: DocType,
  showFixHint: boolean = true
): string {
  const lines: string[] = [];

  lines.push(chalk.red(`\n❌ ${filePath}\n`));

  for (const error of result.errors) {
    lines.push(chalk.red(`  ${error.rule.toUpperCase()}: ${error.message}`));
    lines.push('');

    if (error.suggestion) {
      lines.push(chalk.dim(`  ${error.suggestion}`));
      lines.push('');
    }

    if (error.docs) {
      lines.push(chalk.dim(`  Reference: ${error.docs}`));
      lines.push('');
    }

    if (error.line) {
      lines.push(chalk.dim(`  Line: ${error.line}`));
      lines.push('');
    }

    lines.push(chalk.dim('  ─────────────────────────────────────────────────────────────'));
  }

  for (const warning of result.warnings) {
    lines.push(chalk.yellow(`  WARNING: ${warning.message}`));
    if (warning.line) {
      lines.push(chalk.dim(`  Line: ${warning.line}`));
    }
    lines.push('');
  }

  const skill = getSkillForType(docType);
  if (skill) {
    lines.push(chalk.dim(`  Skill: ${skill}`));
    lines.push(chalk.dim(`  Docs: .claude/skills/${skill}/SKILL.md`));
  }

  if (showFixHint && result.errors.some(e => ['required-section', 'broken-link'].includes(e.rule))) {
    lines.push('');
    lines.push(chalk.dim('  💡 Some issues may be auto-fixable. Run with --fix to attempt repair.'));
  }

  return lines.join('\n');
}

/**
 * Format repair result
 */
function formatRepairResult(
  filePath: string,
  changes: string[],
  unfixable: string[],
  dryRun: boolean
): string {
  const lines: string[] = [];

  if (changes.length > 0) {
    const prefix = dryRun ? '[DRY RUN] Would fix' : '✓ Fixed';
    lines.push(chalk.green(`\n${prefix}: ${filePath}\n`));
    for (const change of changes) {
      lines.push(chalk.green(`  • ${change}`));
    }
  }

  if (unfixable.length > 0) {
    lines.push(chalk.yellow(`\n  Cannot auto-fix:`));
    for (const issue of unfixable) {
      lines.push(chalk.yellow(`    • ${issue}`));
    }
  }

  return lines.join('\n');
}

/**
 * Check command handler
 */
export async function checkCommand(
  pathArg: string | undefined,
  options: CheckOptions
): Promise<void> {
  const results: Array<{
    path: string;
    type: DocType;
    result: ValidationResult;
  }> = [];

  // Determine what to check
  if (pathArg) {
    // Check specific path
    if (!existsSync(pathArg)) {
      console.error(chalk.red(`Error: Path not found: ${pathArg}`));
      process.exit(1);
    }

    const stat = statSync(pathArg);

    if (stat.isDirectory()) {
      // Check all files in directory
      const files = findDocumentFiles(pathArg);

      if (files.length === 0) {
        console.log(chalk.yellow(`No document files found in: ${pathArg}`));
        return;
      }

      for (const file of files) {
        let docType: DocType | null = null;

        if (options.type) {
          docType = resolveTypeAlias(options.type);
        } else {
          docType = detectDocType(file);
        }

        if (docType) {
          const result = await validateDocument(file, docType);
          results.push({ path: file, type: docType, result });

          // Update registry status
          const existing = await getDocument(file);
          if (existing) {
            await updateDocumentStatus(file, result.valid ? 'valid' : 'invalid');
          }
        }
      }
    } else {
      // Check single file
      let docType: DocType | null = null;

      if (options.type) {
        docType = resolveTypeAlias(options.type);
        if (!docType) {
          console.error(chalk.red(`Error: Unknown document type '${options.type}'.`));
          process.exit(1);
        }
      } else {
        docType = detectDocType(pathArg);
        if (!docType) {
          console.error(chalk.red(`Error: Could not detect document type for '${pathArg}'.`));
          console.log(chalk.dim('Use --type to specify the document type explicitly.'));
          process.exit(1);
        }
      }

      const result = await validateDocument(pathArg, docType);
      results.push({ path: pathArg, type: docType, result });

      // Update registry status
      const existing = await getDocument(pathArg);
      if (existing) {
        await updateDocumentStatus(pathArg, result.valid ? 'valid' : 'invalid');
      }
    }
  } else {
    // Check all registered documents
    const registry = await loadRegistry();
    const docs = Object.entries(registry.documents);

    if (docs.length === 0) {
      console.log(chalk.yellow('No documents registered.'));
      console.log(chalk.dim('Use "pdocs register <file>" to register documents.'));
      return;
    }

    for (const [path, doc] of docs) {
      if (!existsSync(path)) {
        results.push({
          path,
          type: doc.type,
          result: {
            valid: false,
            errors: [{ rule: 'file-exists', message: 'File not found' }],
            warnings: [],
          },
        });
        continue;
      }

      const result = await validateDocument(path, doc.type);
      results.push({ path, type: doc.type, result });

      // Update status
      await updateDocumentStatus(path, result.valid ? 'valid' : 'invalid');
    }
  }

  // Handle --fix option
  if (options.fix) {
    const invalid = results.filter(r => !r.result.valid);

    if (invalid.length === 0) {
      console.log(chalk.green('\n✓ No issues to fix\n'));
      return;
    }

    console.log(chalk.cyan(`\n🔧 Attempting to fix ${invalid.length} document(s)...\n`));

    let totalFixed = 0;
    let totalChanges = 0;

    for (const r of invalid) {
      const repairResult = await repairDocument(r.path, r.type, r.result.errors, {
        dryRun: options.dryRun,
      });

      if (repairResult.fixed || repairResult.changes.length > 0) {
        console.log(formatRepairResult(r.path, repairResult.changes, repairResult.errors, !!options.dryRun));
        totalFixed++;
        totalChanges += repairResult.changes.length;
      } else if (repairResult.errors.length > 0) {
        console.log(chalk.yellow(`\n⚠️  ${r.path}`));
        console.log(chalk.yellow('  No auto-fixes available:'));
        for (const err of repairResult.errors) {
          console.log(chalk.dim(`    • ${err}`));
        }
      }
    }

    console.log();
    if (options.dryRun) {
      console.log(chalk.dim(`Dry run complete: ${totalChanges} change(s) would be made to ${totalFixed} file(s)`));
      console.log(chalk.dim('Run without --dry-run to apply changes.'));
    } else {
      console.log(chalk.green(`Fixed ${totalChanges} issue(s) in ${totalFixed} file(s)`));

      // Re-validate after fixes
      if (totalFixed > 0) {
        console.log(chalk.dim('\nRe-validating fixed files...'));
        let stillInvalid = 0;
        for (const r of invalid) {
          const recheck = await validateDocument(r.path, r.type);
          if (!recheck.valid) {
            stillInvalid++;
          } else {
            await updateDocumentStatus(r.path, 'valid');
          }
        }
        if (stillInvalid > 0) {
          console.log(chalk.yellow(`${stillInvalid} file(s) still have issues after repair.`));
        } else {
          console.log(chalk.green('All fixed files now valid!'));
        }
      }
    }

    console.log();
    return;
  }

  // Output results
  if (options.json) {
    const output = results.map(r => ({
      path: r.path,
      type: r.type,
      valid: r.result.valid,
      errors: r.result.errors,
      warnings: r.result.warnings,
    }));
    console.log(JSON.stringify(output, null, 2));
    return;
  }

  // Summary
  const valid = results.filter(r => r.result.valid);
  const invalid = results.filter(r => !r.result.valid);
  const warnings = results.filter(r => r.result.warnings.length > 0);

  if (invalid.length === 0 && (options.strict ? warnings.length === 0 : true)) {
    console.log(chalk.green(`\n✓ All ${results.length} documents valid\n`));

    if (warnings.length > 0 && !options.strict) {
      console.log(chalk.yellow(`  ${warnings.length} document(s) have warnings\n`));
    }

    return;
  }

  // Show errors with verbose formatting
  for (const r of invalid) {
    console.log(formatVerboseError(r.path, r.result, r.type, !options.fix));
  }

  // Show warnings for valid docs if strict
  if (options.strict) {
    for (const r of valid.filter(v => v.result.warnings.length > 0)) {
      console.log(chalk.yellow(`\n⚠️  ${r.path}\n`));
      for (const w of r.result.warnings) {
        console.log(chalk.yellow(`  ${w.message}`));
      }
    }
  }

  // Summary line
  console.log();
  console.log(
    chalk.dim(`Summary: ${invalid.length} error(s), ${warnings.length} warning(s)`)
  );
  console.log();

  // Exit with error code if there are errors
  if (invalid.length > 0) {
    process.exit(1);
  }

  // Exit with error if strict and warnings
  if (options.strict && warnings.length > 0) {
    process.exit(1);
  }
}
