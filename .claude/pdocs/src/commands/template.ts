import { writeFile } from 'fs/promises';
import chalk from 'chalk';
import { getTemplate, listTemplates, applyTemplateVars, fetchRemoteTemplate } from '../lib/templates.js';
import { resolveTypeAlias } from '../lib/detection.js';

interface TemplateOptions {
  output?: string;
  list?: boolean;
  vars?: string[];
  from?: string;
}

/**
 * Parse key=value pairs from vars array
 */
function parseVars(vars: string[] = []): Record<string, string> {
  const result: Record<string, string> = {};
  for (const v of vars) {
    const [key, ...rest] = v.split('=');
    if (key && rest.length > 0) {
      result[key] = rest.join('=');
    }
  }
  return result;
}

/**
 * Template command handler
 */
export async function templateCommand(
  type: string | undefined,
  options: TemplateOptions
): Promise<void> {
  // Handle --list flag
  if (options.list) {
    const templates = await listTemplates();

    if (templates.length === 0) {
      console.log(chalk.yellow('No templates found.'));
      return;
    }

    console.log(chalk.bold('\nAvailable Templates:\n'));
    console.log(chalk.dim('  Type                 Source         Path'));
    console.log(chalk.dim('  ────────────────────────────────────────────────────────'));

    for (const t of templates) {
      const typeStr = t.type.padEnd(20);
      const sourceStr = t.source.padEnd(14);
      console.log(`  ${chalk.cyan(typeStr)} ${chalk.gray(sourceStr)} ${chalk.dim(t.path)}`);
    }

    console.log();
    return;
  }

  // Require type if not listing
  if (!type) {
    console.error(chalk.red('Error: Template type is required.'));
    console.log(chalk.dim('Use --list to see available templates.'));
    process.exit(1);
  }

  // Handle remote fetch
  if (options.from) {
    try {
      const content = await fetchRemoteTemplate(options.from);
      const vars = parseVars(options.vars);
      const result = Object.keys(vars).length > 0 ? applyTemplateVars(content, vars) : content;

      if (options.output) {
        await writeFile(options.output, result, 'utf-8');
        console.log(chalk.green(`Template written to: ${options.output}`));
      } else {
        console.log(result);
      }
      return;
    } catch (error) {
      console.error(chalk.red(`Error fetching remote template: ${(error as Error).message}`));
      process.exit(1);
    }
  }

  // Validate type
  const docType = resolveTypeAlias(type);
  if (!docType) {
    console.error(chalk.red(`Error: Unknown template type '${type}'.`));
    console.log(chalk.dim('Use --list to see available templates.'));
    process.exit(1);
  }

  // Get template
  const template = await getTemplate(type);

  if (!template) {
    console.error(chalk.red(`Error: No template found for type '${type}'.`));
    console.log(chalk.dim('Use --list to see available templates.'));
    process.exit(1);
  }

  // Apply variables
  const vars = parseVars(options.vars);
  const content = Object.keys(vars).length > 0
    ? applyTemplateVars(template.content, vars)
    : template.content;

  // Output
  if (options.output) {
    await writeFile(options.output, content, 'utf-8');
    console.log(chalk.green(`Template written to: ${options.output}`));
    console.log(chalk.dim(`Source: ${template.path}`));
  } else {
    console.log(content);
  }
}
