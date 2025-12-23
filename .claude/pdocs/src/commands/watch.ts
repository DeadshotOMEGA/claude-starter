import { watch } from 'chokidar';
import { existsSync, statSync } from 'fs';
import chalk from 'chalk';
import { validateDocument } from '../lib/validation.js';
import { detectDocType, getSkillForType } from '../lib/detection.js';
import { getDocument, updateDocumentStatus } from '../lib/registry.js';
import type { DocType, ValidationResult } from '../types.js';

interface WatchOptions {
  debounce?: string;
}

/**
 * Debounce function for file change handling
 */
function debounce(
  fn: (filePath: string) => Promise<void>,
  delay: number
): (filePath: string) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return (filePath: string) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      fn(filePath);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Format compact validation result for watch output
 */
function formatWatchResult(
  filePath: string,
  result: ValidationResult,
  docType: DocType
): void {
  const timestamp = new Date().toLocaleTimeString();

  if (result.valid) {
    if (result.warnings.length > 0) {
      console.log(
        chalk.yellow(`[${timestamp}] ⚠️  ${filePath} - ${result.warnings.length} warning(s)`)
      );
      for (const warning of result.warnings) {
        console.log(chalk.dim(`    ${warning.message}`));
      }
    } else {
      console.log(chalk.green(`[${timestamp}] ✓ ${filePath}`));
    }
  } else {
    console.log(
      chalk.red(`[${timestamp}] ❌ ${filePath} - ${result.errors.length} error(s)`)
    );
    for (const error of result.errors) {
      console.log(chalk.red(`    ${error.message}`));
      if (error.suggestion) {
        console.log(chalk.dim(`    → ${error.suggestion}`));
      }
    }
  }
}

/**
 * Check if a file should be watched
 */
function shouldWatch(filePath: string): boolean {
  // Skip hidden files, node_modules, etc.
  if (filePath.includes('node_modules') || filePath.includes('.git')) {
    return false;
  }

  // Only watch markdown and YAML files
  return (
    filePath.endsWith('.md') ||
    filePath.endsWith('.yaml') ||
    filePath.endsWith('.yml')
  );
}

/**
 * Validate a file and output results
 */
async function validateFile(filePath: string): Promise<void> {
  if (!shouldWatch(filePath) || !existsSync(filePath)) {
    return;
  }

  const stat = statSync(filePath);
  if (stat.isDirectory()) {
    return;
  }

  const docType = detectDocType(filePath);
  if (!docType) {
    // Unknown type, skip silently
    return;
  }

  try {
    const result = await validateDocument(filePath, docType);
    formatWatchResult(filePath, result, docType);

    // Update registry if document is registered
    const existing = await getDocument(filePath);
    if (existing) {
      await updateDocumentStatus(filePath, result.valid ? 'valid' : 'invalid');
    }
  } catch (error) {
    console.log(
      chalk.red(`[${new Date().toLocaleTimeString()}] Error validating ${filePath}:`)
    );
    console.log(chalk.dim(`    ${(error as Error).message}`));
  }
}

/**
 * Watch command handler
 */
export async function watchCommand(
  pathArg: string | undefined,
  options: WatchOptions
): Promise<void> {
  const debounceMs = parseInt(options.debounce ?? '500', 10);

  // Default paths to watch
  const paths = pathArg ? [pathArg] : ['docs/', '.claude/'];

  // Filter to existing paths
  const existingPaths = paths.filter((p) => existsSync(p));

  if (existingPaths.length === 0) {
    console.error(chalk.red('Error: No valid paths to watch.'));
    console.log(chalk.dim('Checked: ' + paths.join(', ')));
    process.exit(1);
  }

  console.log(chalk.cyan('\n📂 Watching for document changes...\n'));
  console.log(chalk.dim(`   Paths: ${existingPaths.join(', ')}`));
  console.log(chalk.dim(`   Debounce: ${debounceMs}ms`));
  console.log(chalk.dim('   Press Ctrl+C to stop\n'));

  // Create debounced validation function
  const debouncedValidate = debounce(validateFile, debounceMs);

  // Create watcher
  const watcher = watch(existingPaths, {
    ignored: [
      '**/node_modules/**',
      '**/.git/**',
      '**/dist/**',
      '**/build/**',
    ],
    persistent: true,
    ignoreInitial: false,
    awaitWriteFinish: {
      stabilityThreshold: 100,
      pollInterval: 50,
    },
  });

  // Handle events
  watcher
    .on('add', (filePath: string) => {
      if (shouldWatch(filePath)) {
        console.log(chalk.dim(`[${new Date().toLocaleTimeString()}] New file: ${filePath}`));
        debouncedValidate(filePath);
      }
    })
    .on('change', (filePath: string) => {
      if (shouldWatch(filePath)) {
        debouncedValidate(filePath);
      }
    })
    .on('unlink', (filePath: string) => {
      if (shouldWatch(filePath)) {
        console.log(
          chalk.dim(`[${new Date().toLocaleTimeString()}] Removed: ${filePath}`)
        );
      }
    })
    .on('error', (error: unknown) => {
      console.error(chalk.red(`Watcher error: ${(error as Error).message}`));
    });

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log(chalk.dim('\n\nStopping watcher...'));
    watcher.close().then(() => {
      console.log(chalk.dim('Watcher stopped.'));
      process.exit(0);
    });
  });

  // Keep process running
  await new Promise(() => {});
}
