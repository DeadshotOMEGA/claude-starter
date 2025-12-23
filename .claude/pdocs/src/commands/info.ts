import chalk from 'chalk';
import { loadRegistry, getRegistryFilePath } from '../lib/registry.js';
import type { DocType, DocStatus } from '../types.js';

interface InfoOptions {
  json?: boolean;
  detailed?: boolean;
}

/**
 * Get status icon
 */
function getStatusIcon(status: DocStatus): string {
  switch (status) {
    case 'valid':
      return chalk.green('✓');
    case 'invalid':
      return chalk.red('✗');
    case 'pending':
      return chalk.yellow('○');
    default:
      return chalk.gray('?');
  }
}

/**
 * Info command handler
 */
export async function infoCommand(options: InfoOptions): Promise<void> {
  const registry = await loadRegistry();

  // JSON output
  if (options.json) {
    const output = {
      registry_path: getRegistryFilePath(),
      version: registry.version,
      updated: registry.updated,
      stats: registry.stats,
      documents: options.detailed ? registry.documents : undefined,
    };
    console.log(JSON.stringify(output, null, 2));
    return;
  }

  // Group documents by type
  const byType: Record<DocType, { valid: number; invalid: number; pending: number }> = {} as any;

  for (const doc of Object.values(registry.documents)) {
    if (!byType[doc.type]) {
      byType[doc.type] = { valid: 0, invalid: 0, pending: 0 };
    }
    if (doc.status === 'valid') byType[doc.type].valid++;
    else if (doc.status === 'invalid') byType[doc.type].invalid++;
    else byType[doc.type].pending++;
  }

  // Collect issues
  const issues: Array<{ path: string; message: string }> = [];
  for (const [path, doc] of Object.entries(registry.documents)) {
    if (doc.status === 'invalid') {
      issues.push({ path, message: 'Validation failed' });
    } else if (doc.status === 'pending') {
      issues.push({ path, message: 'Pending validation' });
    }
  }

  // Display
  console.log(chalk.bold('\n📁 Project Documentation\n'));

  // Overall status
  const { total, valid, invalid, pending } = registry.stats;
  const statusColor = invalid > 0 ? chalk.red : pending > 0 ? chalk.yellow : chalk.green;
  console.log(`Status: ${statusColor(`${valid}/${total} documents valid`)}`);
  console.log();

  // By type
  if (Object.keys(byType).length > 0) {
    console.log(chalk.bold('By Type:'));
    for (const [type, counts] of Object.entries(byType)) {
      const total = counts.valid + counts.invalid + counts.pending;
      let statusStr = '';
      if (counts.valid > 0) statusStr += chalk.green(`${counts.valid} ✓`);
      if (counts.invalid > 0) statusStr += (statusStr ? ', ' : '') + chalk.red(`${counts.invalid} ✗`);
      if (counts.pending > 0) statusStr += (statusStr ? ', ' : '') + chalk.yellow(`${counts.pending} ○`);

      console.log(`  ${chalk.cyan(type.padEnd(18))} ${total.toString().padStart(3)} (${statusStr})`);
    }
    console.log();
  }

  // Issues
  if (issues.length > 0) {
    console.log(chalk.bold('Issues:'));
    for (const issue of issues.slice(0, 10)) {
      console.log(`  ${chalk.yellow('⚠')} ${issue.path}`);
      console.log(`    ${chalk.dim(issue.message)}`);
    }
    if (issues.length > 10) {
      console.log(chalk.dim(`  ... and ${issues.length - 10} more`));
    }
    console.log();
  }

  // Detailed view
  if (options.detailed && Object.keys(registry.documents).length > 0) {
    console.log(chalk.bold('All Documents:'));
    for (const [path, doc] of Object.entries(registry.documents)) {
      const icon = getStatusIcon(doc.status);
      console.log(`  ${icon} ${path}`);
      console.log(chalk.dim(`     Type: ${doc.type}, Registered: ${doc.registered.split('T')[0]}`));
    }
    console.log();
  }

  // Registry info
  console.log(chalk.dim(`Registry: ${getRegistryFilePath()}`));
  console.log(chalk.dim(`Updated: ${registry.updated}`));
  console.log();
}
