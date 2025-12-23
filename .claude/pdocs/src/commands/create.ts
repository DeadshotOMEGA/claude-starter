import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, basename, dirname } from 'path';
import chalk from 'chalk';
import { getTemplate, applyTemplateVars, fetchRemoteTemplate } from '../lib/templates.js';
import { resolveTypeAlias, getSkillForType } from '../lib/detection.js';
import { registerDocument } from '../lib/registry.js';
import { generateNextId, peekNextId } from '../lib/ids.js';
import { loadManifestForType } from '../lib/manifests.js';
import type { DocType } from '../types.js';

interface CreateOptions {
  vars?: string[];
  autoId?: boolean;
  register?: boolean;
  from?: string;
  name?: string;
}

/**
 * Parse key=value pairs from vars array
 */
function parseVars(vars: string[] = []): Record<string, string> {
  const result: Record<string, string> = {};
  for (const v of vars) {
    const [key, ...rest] = v.split('=');
    if (key && rest.length > 0) {
      result[key.trim()] = rest.join('=');
    }
  }
  return result;
}

/**
 * Get default filename for a document type
 */
function getDefaultFilename(docType: DocType): string {
  const filenames: Partial<Record<DocType, string>> = {
    plan: 'plan.md',
    investigation: 'investigation.md',
    requirements: 'requirements.md',
    'feature-spec': 'feature-spec.md',
    'api-contract': 'api-contract.yaml',
    'user-story': 'user-story.md',
    'user-flow': 'user-flow.md',
    agent: 'agent.md',
    skill: 'SKILL.md',
    claudemd: 'CLAUDE.md',
    rule: 'rule.md',
    command: 'command.md',
    readme: 'README.md',
    changelog: 'CHANGELOG.md',
  };

  return filenames[docType] ?? `${docType}.md`;
}

/**
 * Resolve output path - handles directories and files
 */
function resolveOutputPath(outputDir: string, docType: DocType, name?: string): string {
  // If outputDir ends with .md or .yaml, treat as full path
  if (outputDir.endsWith('.md') || outputDir.endsWith('.yaml') || outputDir.endsWith('.json')) {
    return outputDir;
  }

  // Otherwise it's a directory - add default filename
  const filename = name ? `${name}.md` : getDefaultFilename(docType);
  return join(outputDir, filename);
}

/**
 * Create command handler
 */
export async function createCommand(
  type: string,
  outputDir: string,
  options: CreateOptions
): Promise<void> {
  // Validate type
  const docType = resolveTypeAlias(type);
  if (!docType) {
    console.error(chalk.red(`Error: Unknown document type '${type}'.`));
    console.log(chalk.dim('Available types: plan, investigation, requirements, feature-spec, api-contract, user-story, agent, skill, rule, command, readme, changelog'));
    process.exit(1);
  }

  // Get template
  let templateContent: string;
  let templateSource: string;

  if (options.from) {
    try {
      console.log(chalk.dim(`Fetching template from: ${options.from}`));
      templateContent = await fetchRemoteTemplate(options.from);
      templateSource = options.from;
    } catch (error) {
      console.error(chalk.red(`Error fetching remote template: ${(error as Error).message}`));
      process.exit(1);
    }
  } else {
    const template = await getTemplate(type);
    if (!template) {
      console.error(chalk.red(`Error: No template found for type '${type}'.`));
      console.log(chalk.dim('Use "pdocs template --list" to see available templates.'));
      process.exit(1);
    }
    templateContent = template.content;
    templateSource = template.path;
  }

  // Prepare variables for substitution
  const vars = parseVars(options.vars);

  // Auto-generate ID if requested
  if (options.autoId) {
    const { id, sequenceNum } = await generateNextId(docType);
    vars['id'] = id;
    vars['ID'] = id;
    vars['num'] = sequenceNum.toString();
    console.log(chalk.dim(`Generated ID: ${id}`));
  }

  // Add common variables
  vars['date'] = new Date().toISOString().split('T')[0];
  vars['datetime'] = new Date().toISOString();
  vars['type'] = docType;

  // Try to get output path from manifest
  const manifest = await loadManifestForType(docType);
  let outputPath = resolveOutputPath(outputDir, docType, options.name);

  // If manifest specifies default_path and vars are available, use it as hint
  if (manifest?.output?.default_path && Object.keys(vars).length > 0) {
    // Apply vars to the manifest's default path pattern
    const suggestedPath = applyTemplateVars(manifest.output.default_path, vars);
    console.log(chalk.dim(`Hint: Manifest suggests path pattern: ${manifest.output.default_path}`));
  }

  // Apply variable substitution to template
  const content = applyTemplateVars(templateContent, vars);

  // Create output directory if needed
  const dir = dirname(outputPath);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
    console.log(chalk.dim(`Created directory: ${dir}`));
  }

  // Check if file already exists
  if (existsSync(outputPath)) {
    console.error(chalk.red(`Error: File already exists: ${outputPath}`));
    console.log(chalk.dim('Use a different path or delete the existing file.'));
    process.exit(1);
  }

  // Write the file
  await writeFile(outputPath, content, 'utf-8');
  console.log(chalk.green(`Created: ${outputPath}`));
  console.log(chalk.dim(`Template: ${templateSource}`));

  // Register if requested (default: true)
  if (options.register !== false) {
    const skill = getSkillForType(docType);
    await registerDocument(outputPath, docType, skill ?? undefined, 'pending');
    console.log(chalk.dim(`Registered in pdocs registry (status: pending)`));
    console.log(chalk.dim(`Run "pdocs check ${outputPath}" to validate.`));
  }

  // Show next steps
  console.log();
  console.log(chalk.bold('Next steps:'));
  console.log(chalk.dim(`  1. Edit ${outputPath} to fill in content`));
  console.log(chalk.dim(`  2. Run "pdocs check ${outputPath}" to validate`));

  // Show remaining template placeholders
  const remainingPlaceholders = content.match(/\{[^}]+\}|\{\{[^}]+\}\}|\$\{[^}]+\}/g);
  if (remainingPlaceholders) {
    const unique = [...new Set(remainingPlaceholders)];
    console.log();
    console.log(chalk.yellow(`Note: ${unique.length} template placeholder(s) remain:`));
    for (const p of unique.slice(0, 5)) {
      console.log(chalk.dim(`  - ${p}`));
    }
    if (unique.length > 5) {
      console.log(chalk.dim(`  ... and ${unique.length - 5} more`));
    }
  }
}
