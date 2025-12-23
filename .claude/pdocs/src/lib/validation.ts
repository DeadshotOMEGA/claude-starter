import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import type { DocType, ValidationResult, ValidationError, ValidationWarning } from '../types.js';
import { getValidationRules, loadManifest } from './manifests.js';
import { getSkillForType } from './detection.js';
import { verifyLinks, verifyCrossDocumentAnchors } from './links.js';

/**
 * Extract sections from a markdown document
 * Returns array of section names (## headings)
 */
function extractSections(content: string): string[] {
  const sections: string[] = [];
  const lines = content.split('\n');

  for (const line of lines) {
    // Match ## Section Name or ### Subsection
    const match = line.match(/^#{2,3}\s+(.+)$/);
    if (match) {
      sections.push(match[1].trim());
    }
  }

  return sections;
}

/**
 * Check if a section exists (case-insensitive, partial match)
 */
function hasSection(sections: string[], required: string): boolean {
  const normalizedRequired = required.toLowerCase().replace(/[^a-z0-9]/g, '');

  for (const section of sections) {
    const normalizedSection = section.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (normalizedSection.includes(normalizedRequired) || normalizedRequired.includes(normalizedSection)) {
      return true;
    }
  }

  return false;
}

/**
 * Validate required sections
 */
function validateRequiredSections(
  content: string,
  requiredSections: string[]
): ValidationError[] {
  const errors: ValidationError[] = [];
  const foundSections = extractSections(content);

  for (const required of requiredSections) {
    if (!hasSection(foundSections, required)) {
      errors.push({
        rule: 'required-section',
        message: `Missing required section: ${required}`,
        suggestion: `Add a "## ${required}" section to the document`,
      });
    }
  }

  return errors;
}

/**
 * Validate pattern rules
 */
function validatePatternRules(
  content: string,
  rules: Array<{ id: string; pattern: string; message: string }>
): ValidationError[] {
  const errors: ValidationError[] = [];

  for (const rule of rules) {
    try {
      const regex = new RegExp(rule.pattern, 'm');
      if (!regex.test(content)) {
        errors.push({
          rule: rule.id,
          message: rule.message,
        });
      }
    } catch {
      // Invalid regex, skip
    }
  }

  return errors;
}

/**
 * Run custom validation scripts
 */
async function runValidationScripts(
  filePath: string,
  content: string,
  skillName: string
): Promise<{ errors: ValidationError[]; warnings: ValidationWarning[] }> {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  const manifest = await loadManifest(skillName);
  if (!manifest?.validation?.scripts) {
    return { errors, warnings };
  }

  // Get base path
  let basePath = process.cwd();
  let current = process.cwd();
  while (current !== '/') {
    if (existsSync(join(current, '.claude'))) {
      basePath = current;
      break;
    }
    current = dirname(current);
  }

  for (const script of manifest.validation.scripts) {
    const scriptPath = join(basePath, '.claude', 'skills', skillName, script.path);

    if (!existsSync(scriptPath)) {
      warnings.push({
        rule: 'script-missing',
        message: `Validation script not found: ${script.path}`,
      });
      continue;
    }

    try {
      const result = await new Promise<string>((resolve, reject) => {
        const proc = spawn('bun', ['run', scriptPath, filePath], {
          cwd: basePath,
          stdio: ['pipe', 'pipe', 'pipe'],
        });

        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        proc.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        proc.stdin.write(content);
        proc.stdin.end();

        proc.on('close', (code) => {
          if (code === 0) {
            resolve(stdout);
          } else {
            reject(new Error(stderr || `Script exited with code ${code}`));
          }
        });

        proc.on('error', reject);
      });

      // Parse JSON output
      try {
        const parsed = JSON.parse(result);
        if (parsed.errors) {
          errors.push(...parsed.errors);
        }
        if (parsed.warnings) {
          warnings.push(...parsed.warnings);
        }
      } catch {
        // Not JSON, treat as plain text error
        if (result.trim()) {
          warnings.push({
            rule: 'script-output',
            message: result.trim(),
          });
        }
      }
    } catch (error) {
      warnings.push({
        rule: 'script-error',
        message: `Script failed: ${(error as Error).message}`,
      });
    }
  }

  return { errors, warnings };
}

/**
 * Validation options
 */
export interface ValidationOptions {
  checkLinks?: boolean;
  checkCrossDocAnchors?: boolean;
}

/**
 * Validate a document
 */
export async function validateDocument(
  filePath: string,
  docType: DocType,
  options: ValidationOptions = { checkLinks: true }
): Promise<ValidationResult> {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  // Check file exists
  if (!existsSync(filePath)) {
    return {
      valid: false,
      errors: [{ rule: 'file-exists', message: `File not found: ${filePath}` }],
      warnings: [],
    };
  }

  // Read content
  const content = await readFile(filePath, 'utf-8');

  // Get validation rules
  const rules = await getValidationRules(docType);

  // Validate required sections
  if (rules.requiredSections.length > 0) {
    errors.push(...validateRequiredSections(content, rules.requiredSections));
  }

  // Validate pattern rules
  if (rules.patternRules.length > 0) {
    errors.push(...validatePatternRules(content, rules.patternRules));
  }

  // Verify links (default: enabled)
  if (options.checkLinks !== false && filePath.endsWith('.md')) {
    const linkResults = verifyLinks(content, filePath);
    errors.push(...linkResults.errors);
    warnings.push(...linkResults.warnings);

    // Optionally check cross-document anchors
    if (options.checkCrossDocAnchors) {
      const crossDocWarnings = await verifyCrossDocumentAnchors(content, filePath);
      warnings.push(...crossDocWarnings);
    }
  }

  // Run custom scripts
  const skillName = getSkillForType(docType);
  if (skillName) {
    const scriptResults = await runValidationScripts(filePath, content, skillName);
    errors.push(...scriptResults.errors);
    warnings.push(...scriptResults.warnings);
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate multiple documents
 */
export async function validateDocuments(
  documents: Array<{ path: string; type: DocType }>
): Promise<Map<string, ValidationResult>> {
  const results = new Map<string, ValidationResult>();

  for (const doc of documents) {
    const result = await validateDocument(doc.path, doc.type);
    results.set(doc.path, result);
  }

  return results;
}
