#!/usr/bin/env node

import { Command } from 'commander';
import { templateCommand } from './commands/template.js';
import { registerCommand } from './commands/register.js';
import { listCommand } from './commands/list.js';
import { infoCommand } from './commands/info.js';
import { checkCommand } from './commands/check.js';
import { createCommand } from './commands/create.js';
import { watchCommand } from './commands/watch.js';

const program = new Command();

program
  .name('pdocs')
  .description('Project Documentation CLI for managing YAML-based documentation')
  .version('1.0.0');

// Template command
program
  .command('template [type]')
  .description('Get or list document templates')
  .option('-o, --output <file>', 'Write template to file instead of stdout')
  .option('-l, --list', 'List all available templates')
  .option('--vars <key=value...>', 'Template variables for substitution')
  .option('--from <url>', 'Fetch template from URL (supports github: shorthand)')
  .action(templateCommand);

// Register command
program
  .command('register <file>')
  .description('Register a document in the registry')
  .option('-t, --type <type>', 'Force document type (auto-detected if omitted)')
  .option('--validate', 'Validate before registering (default: true)', true)
  .option('--force', 'Register even if already registered')
  .action(registerCommand);

// List command
program
  .command('list [type]')
  .description('List registered documents')
  .option('--status <status>', 'Filter by status (valid, invalid, pending)')
  .option('--json', 'Output as JSON')
  .option('--tree', 'Show as tree structure grouped by type')
  .action(listCommand);

// Info command
program
  .command('info')
  .description('Show project documentation overview')
  .option('--json', 'Output as JSON')
  .option('--detailed', 'Include per-document details')
  .action(infoCommand);

// Check command
program
  .command('check [path]')
  .description('Validate documents against their schemas')
  .option('-t, --type <type>', 'Document type (auto-detected if omitted)')
  .option('--strict', 'Fail on warnings')
  .option('--json', 'Output as JSON')
  .option('--recursive', 'Check all files in directory')
  .option('--fix', 'Auto-fix fixable issues')
  .option('--dry-run', 'Show what would be fixed without making changes')
  .action(checkCommand);

// Create command
program
  .command('create <type> <output-dir>')
  .description('Create a new document from template')
  .option('--vars <key=value...>', 'Template variables (key=value)')
  .option('--auto-id', 'Auto-generate document ID')
  .option('--register', 'Register after creation (default: true)', true)
  .option('--from <url>', 'Fetch template from URL (supports github: shorthand)')
  .option('--name <name>', 'Custom filename (without extension)')
  .action(createCommand);

// Watch command
program
  .command('watch [path]')
  .description('Watch for changes and validate continuously')
  .option('--debounce <ms>', 'Wait time before re-validating', '500')
  .action(watchCommand);

program.parse();
