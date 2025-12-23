import chalk from 'chalk';
import { listDocuments, loadRegistry } from '../lib/registry.js';
import { resolveTypeAlias } from '../lib/detection.js';
import type { DocType, DocStatus } from '../types.js';

interface ListOptions {
  status?: string;
  json?: boolean;
  tree?: boolean;
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
 * Group documents by type
 */
function groupByType(
  docs: Array<{ path: string; doc: { type: DocType; status: DocStatus } }>
): Record<string, typeof docs> {
  const groups: Record<string, typeof docs> = {};

  for (const d of docs) {
    const type = d.doc.type;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(d);
  }

  return groups;
}

/**
 * List command handler
 */
export async function listCommand(
  type: string | undefined,
  options: ListOptions
): Promise<void> {
  // Parse type filter
  let typeFilter: DocType | undefined;
  if (type) {
    typeFilter = resolveTypeAlias(type) ?? undefined;
    if (!typeFilter) {
      console.error(chalk.red(`Error: Unknown document type '${type}'.`));
      process.exit(1);
    }
  }

  // Parse status filter
  let statusFilter: DocStatus | undefined;
  if (options.status) {
    const validStatuses = ['valid', 'invalid', 'pending'];
    if (!validStatuses.includes(options.status)) {
      console.error(chalk.red(`Error: Invalid status '${options.status}'.`));
      console.log(chalk.dim(`Valid statuses: ${validStatuses.join(', ')}`));
      process.exit(1);
    }
    statusFilter = options.status as DocStatus;
  }

  // Get documents
  const docs = await listDocuments({ type: typeFilter, status: statusFilter });

  // JSON output
  if (options.json) {
    console.log(JSON.stringify(docs, null, 2));
    return;
  }

  // No documents
  if (docs.length === 0) {
    if (typeFilter || statusFilter) {
      console.log(chalk.yellow('No documents match the specified filters.'));
    } else {
      console.log(chalk.yellow('No documents registered.'));
      console.log(chalk.dim('Use "pdocs register <file>" to register documents.'));
    }
    return;
  }

  // Tree view
  if (options.tree) {
    const groups = groupByType(docs);

    console.log(chalk.bold('\nRegistered Documents:\n'));

    for (const [docType, typeDocs] of Object.entries(groups)) {
      console.log(chalk.cyan(`${docType}/ (${typeDocs.length})`));
      for (const d of typeDocs) {
        const icon = getStatusIcon(d.doc.status);
        console.log(`  ${icon} ${d.path}`);
      }
      console.log();
    }

    return;
  }

  // Default list view
  console.log(chalk.bold('\nRegistered Documents:\n'));
  console.log(chalk.dim('  Status  Type                 Path'));
  console.log(chalk.dim('  ─────────────────────────────────────────────────────'));

  for (const d of docs) {
    const icon = getStatusIcon(d.doc.status);
    const typeStr = d.doc.type.padEnd(20);
    console.log(`  ${icon}      ${chalk.cyan(typeStr)} ${d.path}`);
  }

  console.log();
  console.log(chalk.dim(`  Total: ${docs.length} documents`));
  console.log();
}
