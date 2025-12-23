import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import type { Registry, RegistryDocument, DocType, DocStatus } from '../types.js';

/**
 * Get the registry file path
 */
function getRegistryPath(): string {
  let current = process.cwd();
  while (current !== '/') {
    if (existsSync(join(current, '.claude'))) {
      return join(current, '.claude', 'pdocs', 'registry.json');
    }
    current = dirname(current);
  }
  return join(process.cwd(), '.claude', 'pdocs', 'registry.json');
}

/**
 * Create a new empty registry
 */
function createEmptyRegistry(): Registry {
  return {
    version: '1.0',
    updated: new Date().toISOString(),
    documents: {},
    id_sequences: {},
    stats: {
      total: 0,
      valid: 0,
      invalid: 0,
      pending: 0,
    },
  };
}

/**
 * Load the registry from disk
 */
export async function loadRegistry(): Promise<Registry> {
  const registryPath = getRegistryPath();

  if (!existsSync(registryPath)) {
    return createEmptyRegistry();
  }

  const content = await readFile(registryPath, 'utf-8');
  return JSON.parse(content) as Registry;
}

/**
 * Save the registry to disk
 */
export async function saveRegistry(registry: Registry): Promise<void> {
  const registryPath = getRegistryPath();
  const dir = dirname(registryPath);

  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }

  registry.updated = new Date().toISOString();
  updateStats(registry);

  await writeFile(registryPath, JSON.stringify(registry, null, 2), 'utf-8');
}

/**
 * Update registry statistics
 */
function updateStats(registry: Registry): void {
  const docs = Object.values(registry.documents);
  registry.stats = {
    total: docs.length,
    valid: docs.filter((d) => d.status === 'valid').length,
    invalid: docs.filter((d) => d.status === 'invalid').length,
    pending: docs.filter((d) => d.status === 'pending').length,
  };
}

/**
 * Register a document in the registry
 */
export async function registerDocument(
  filePath: string,
  docType: DocType,
  skill?: string,
  status: DocStatus = 'pending'
): Promise<void> {
  const registry = await loadRegistry();

  registry.documents[filePath] = {
    type: docType,
    skill,
    registered: new Date().toISOString(),
    status,
  };

  await saveRegistry(registry);
}

/**
 * Update document status
 */
export async function updateDocumentStatus(
  filePath: string,
  status: DocStatus
): Promise<void> {
  const registry = await loadRegistry();

  if (registry.documents[filePath]) {
    registry.documents[filePath].status = status;
    registry.documents[filePath].lastValidated = new Date().toISOString();
    await saveRegistry(registry);
  }
}

/**
 * Unregister a document
 */
export async function unregisterDocument(filePath: string): Promise<boolean> {
  const registry = await loadRegistry();

  if (registry.documents[filePath]) {
    delete registry.documents[filePath];
    await saveRegistry(registry);
    return true;
  }

  return false;
}

/**
 * Get a document from the registry
 */
export async function getDocument(
  filePath: string
): Promise<RegistryDocument | null> {
  const registry = await loadRegistry();
  return registry.documents[filePath] ?? null;
}

/**
 * List documents by type or status
 */
export async function listDocuments(options?: {
  type?: DocType;
  status?: DocStatus;
}): Promise<Array<{ path: string; doc: RegistryDocument }>> {
  const registry = await loadRegistry();
  let results = Object.entries(registry.documents).map(([path, doc]) => ({
    path,
    doc,
  }));

  if (options?.type) {
    results = results.filter((r) => r.doc.type === options.type);
  }

  if (options?.status) {
    results = results.filter((r) => r.doc.status === options.status);
  }

  return results;
}

/**
 * Get the next ID in a sequence
 */
export async function getNextId(sequenceKey: string): Promise<number> {
  const registry = await loadRegistry();
  const current = registry.id_sequences[sequenceKey] ?? 0;
  const next = current + 1;

  registry.id_sequences[sequenceKey] = next;
  await saveRegistry(registry);

  return next;
}

/**
 * Format an ID with a pattern
 * Pattern: "P-{num}" -> "P-07"
 */
export function formatId(pattern: string, num: number): string {
  return pattern.replace('{num}', num.toString().padStart(2, '0'));
}

/**
 * Get registry path for external use
 */
export function getRegistryFilePath(): string {
  return getRegistryPath();
}
