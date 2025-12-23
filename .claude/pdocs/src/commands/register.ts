import { existsSync } from 'fs';
import chalk from 'chalk';
import { registerDocument, getDocument } from '../lib/registry.js';
import { detectDocType, resolveTypeAlias, getSkillForType } from '../lib/detection.js';
import type { DocType } from '../types.js';

interface RegisterOptions {
  type?: string;
  validate?: boolean;
  force?: boolean;
}

/**
 * Register command handler
 */
export async function registerCommand(
  filePath: string,
  options: RegisterOptions
): Promise<void> {
  // Check file exists
  if (!existsSync(filePath)) {
    console.error(chalk.red(`Error: File not found: ${filePath}`));
    process.exit(1);
  }

  // Determine document type
  let docType: DocType | null = null;

  if (options.type) {
    docType = resolveTypeAlias(options.type);
    if (!docType) {
      console.error(chalk.red(`Error: Unknown document type '${options.type}'.`));
      process.exit(1);
    }
  } else {
    docType = detectDocType(filePath);
    if (!docType) {
      console.error(chalk.red(`Error: Could not detect document type for '${filePath}'.`));
      console.log(chalk.dim('Use --type to specify the document type explicitly.'));
      process.exit(1);
    }
  }

  // Check if already registered
  const existing = await getDocument(filePath);
  if (existing && !options.force) {
    console.log(chalk.yellow(`Document already registered: ${filePath}`));
    console.log(chalk.dim(`Type: ${existing.type}, Status: ${existing.status}`));
    console.log(chalk.dim('Use --force to re-register.'));
    return;
  }

  // Get associated skill
  const skill = getSkillForType(docType) ?? undefined;

  // TODO: Validate if requested
  // For now, skip validation (Phase 2)
  const status = options.validate ? 'pending' : 'pending';

  // Register
  await registerDocument(filePath, docType, skill, status);

  console.log(chalk.green(`Registered: ${filePath}`));
  console.log(chalk.dim(`Type: ${docType}`));
  if (skill) {
    console.log(chalk.dim(`Skill: ${skill}`));
  }
}
