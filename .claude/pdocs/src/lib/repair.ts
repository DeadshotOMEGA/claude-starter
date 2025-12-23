import { readFile, writeFile } from 'fs/promises';
import { existsSync, readdirSync } from 'fs';
import { join, dirname, basename } from 'path';
import type { DocType, ValidationError, ValidationWarning } from '../types.js';
import { getValidationRules, loadManifest } from './manifests.js';
import { getSkillForType } from './detection.js';
import { extractLinks } from './links.js';

/**
 * Repair result for a single file
 */
export interface RepairResult {
  fixed: boolean;
  changes: string[];
  content?: string;
  errors: string[];
}

/**
 * Fixable issue types
 */
type FixableIssue = 'missing-section' | 'broken-link' | 'trailing-whitespace' | 'missing-newline';

/**
 * Determine if an error is fixable
 */
function isFixable(error: ValidationError): FixableIssue | null {
  if (error.rule === 'required-section') {
    return 'missing-section';
  }
  if (error.rule === 'broken-link') {
    return 'broken-link';
  }
  return null;
}

/**
 * Add a missing section to document
 */
function addMissingSection(content: string, sectionName: string): string {
  // Find the last ## section and add after it
  const lines = content.split('\n');
  let lastSectionIndex = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('## ')) {
      lastSectionIndex = i;
    }
  }

  // New section content
  const newSection = `\n## ${sectionName}\n\n<!-- TODO: Add content for ${sectionName} -->\n`;

  if (lastSectionIndex === -1) {
    // No sections found, add at end
    return content + '\n' + newSection;
  }

  // Find the end of the last section (next section or EOF)
  let insertIndex = lines.length;
  for (let i = lastSectionIndex + 1; i < lines.length; i++) {
    if (lines[i].startsWith('## ')) {
      insertIndex = i;
      break;
    }
  }

  // Insert new section
  lines.splice(insertIndex, 0, '', `## ${sectionName}`, '', `<!-- TODO: Add content for ${sectionName} -->`);

  return lines.join('\n');
}

/**
 * Find similar files for broken link suggestions
 */
function findSimilarFiles(brokenPath: string, searchDir: string): string[] {
  const suggestions: string[] = [];
  const brokenName = basename(brokenPath).toLowerCase();

  try {
    const walk = (dir: string, depth: number = 0): void => {
      if (depth > 3) return; // Limit search depth

      const entries = readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules') {
          continue;
        }

        const fullPath = join(dir, entry.name);

        if (entry.isDirectory()) {
          walk(fullPath, depth + 1);
        } else if (entry.isFile()) {
          const entryName = entry.name.toLowerCase();
          // Check for similar names
          if (
            entryName === brokenName ||
            entryName.includes(brokenName.replace(/\.[^.]+$/, '')) ||
            brokenName.includes(entryName.replace(/\.[^.]+$/, ''))
          ) {
            suggestions.push(fullPath);
          }
        }
      }
    };

    walk(searchDir);
  } catch {
    // Ignore errors during search
  }

  return suggestions.slice(0, 3);
}

/**
 * Fix broken links if possible
 */
function fixBrokenLink(
  content: string,
  error: ValidationError,
  documentPath: string
): { content: string; fixed: boolean; message: string } {
  if (!error.line) {
    return { content, fixed: false, message: 'No line number for broken link' };
  }

  const lines = content.split('\n');
  const lineIndex = error.line - 1;
  const line = lines[lineIndex];

  // Extract the broken target from the error message
  const match = error.message.match(/→ (.+)$/);
  if (!match) {
    return { content, fixed: false, message: 'Could not parse broken link' };
  }

  const brokenTarget = match[1];
  const docDir = dirname(documentPath);

  // Look for similar files
  const suggestions = findSimilarFiles(brokenTarget, docDir);

  if (suggestions.length === 1) {
    // Single suggestion - auto-fix
    const relativePath = suggestions[0].replace(docDir + '/', '');
    const fixedLine = line.replace(brokenTarget, relativePath);
    lines[lineIndex] = fixedLine;

    return {
      content: lines.join('\n'),
      fixed: true,
      message: `Fixed link: ${brokenTarget} → ${relativePath}`,
    };
  }

  return { content, fixed: false, message: 'Multiple or no alternatives found' };
}

/**
 * Fix trailing whitespace
 */
function fixTrailingWhitespace(content: string): { content: string; count: number } {
  const lines = content.split('\n');
  let count = 0;

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trimEnd();
    if (trimmed !== lines[i]) {
      lines[i] = trimmed;
      count++;
    }
  }

  return { content: lines.join('\n'), count };
}

/**
 * Ensure file ends with newline
 */
function ensureTrailingNewline(content: string): { content: string; fixed: boolean } {
  if (!content.endsWith('\n')) {
    return { content: content + '\n', fixed: true };
  }
  return { content, fixed: false };
}

/**
 * Repair a document by fixing known issues
 */
export async function repairDocument(
  filePath: string,
  docType: DocType,
  errors: ValidationError[],
  options?: {
    dryRun?: boolean;
    verbose?: boolean;
  }
): Promise<RepairResult> {
  if (!existsSync(filePath)) {
    return {
      fixed: false,
      changes: [],
      errors: ['File not found'],
    };
  }

  let content = await readFile(filePath, 'utf-8');
  const changes: string[] = [];
  const unfixable: string[] = [];
  let modified = false;

  // Fix trailing whitespace first (doesn't require error matching)
  const whitespaceResult = fixTrailingWhitespace(content);
  if (whitespaceResult.count > 0) {
    content = whitespaceResult.content;
    changes.push(`Fixed trailing whitespace on ${whitespaceResult.count} line(s)`);
    modified = true;
  }

  // Ensure trailing newline
  const newlineResult = ensureTrailingNewline(content);
  if (newlineResult.fixed) {
    content = newlineResult.content;
    changes.push('Added trailing newline');
    modified = true;
  }

  // Process each error
  for (const error of errors) {
    const fixableType = isFixable(error);

    if (!fixableType) {
      unfixable.push(`${error.rule}: ${error.message}`);
      continue;
    }

    switch (fixableType) {
      case 'missing-section': {
        // Extract section name from message
        const sectionMatch = error.message.match(/Missing required section: (.+)$/);
        if (sectionMatch) {
          const sectionName = sectionMatch[1];
          content = addMissingSection(content, sectionName);
          changes.push(`Added section: ${sectionName}`);
          modified = true;
        }
        break;
      }

      case 'broken-link': {
        const linkResult = fixBrokenLink(content, error, filePath);
        if (linkResult.fixed) {
          content = linkResult.content;
          changes.push(linkResult.message);
          modified = true;
        } else {
          unfixable.push(`broken-link: ${error.message} (${linkResult.message})`);
        }
        break;
      }
    }
  }

  // Write changes if not dry run
  if (modified && !options?.dryRun) {
    await writeFile(filePath, content, 'utf-8');
  }

  return {
    fixed: modified,
    changes,
    content: options?.dryRun ? content : undefined,
    errors: unfixable,
  };
}

/**
 * Get list of fixable issues for user information
 */
export function getFixableIssues(): Array<{ type: string; description: string }> {
  return [
    { type: 'missing-section', description: 'Add stub sections with TODO comments' },
    { type: 'broken-link', description: 'Auto-correct links when single similar file exists' },
    { type: 'trailing-whitespace', description: 'Remove trailing whitespace from lines' },
    { type: 'missing-newline', description: 'Ensure file ends with newline' },
  ];
}
