import type { DocType } from '../types.js';
import { loadRegistry, saveRegistry } from './registry.js';
import { loadManifestForType } from './manifests.js';

/**
 * Default ID patterns for document types
 */
const DEFAULT_PATTERNS: Record<DocType, { pattern: string; key: string }> = {
  plan: { pattern: 'P-{num}', key: 'plan' },
  investigation: { pattern: 'INV-{num}', key: 'investigation' },
  requirements: { pattern: 'REQ-{num}', key: 'requirements' },
  'feature-spec': { pattern: 'F-{num}', key: 'feature' },
  'api-contract': { pattern: 'API-{num}', key: 'api' },
  'user-story': { pattern: 'US-{num}', key: 'user-story' },
  'user-flow': { pattern: 'UF-{num}', key: 'user-flow' },
  agent: { pattern: 'AGT-{num}', key: 'agent' },
  skill: { pattern: 'SKL-{num}', key: 'skill' },
  claudemd: { pattern: 'CMD-{num}', key: 'claudemd' },
  rule: { pattern: 'RUL-{num}', key: 'rule' },
  command: { pattern: 'COM-{num}', key: 'command' },
  readme: { pattern: 'RDM-{num}', key: 'readme' },
  changelog: { pattern: 'CHG-{num}', key: 'changelog' },
};

/**
 * Get ID pattern and sequence key for a document type
 * Checks manifest first, falls back to defaults
 */
export async function getIdConfig(docType: DocType): Promise<{
  pattern: string;
  sequenceKey: string;
}> {
  // Try manifest first
  const manifest = await loadManifestForType(docType);
  if (manifest?.id_pattern && manifest?.id_sequence_key) {
    return {
      pattern: manifest.id_pattern,
      sequenceKey: manifest.id_sequence_key,
    };
  }

  // Fall back to defaults
  const defaults = DEFAULT_PATTERNS[docType];
  return {
    pattern: defaults.pattern,
    sequenceKey: defaults.key,
  };
}

/**
 * Format a number into an ID using a pattern
 * Supports:
 * - {num} - plain number (7)
 * - {num:2} - padded number (07)
 * - {num:3} - 3-digit padded (007)
 */
export function formatIdFromPattern(pattern: string, num: number): string {
  return pattern.replace(/\{num(?::(\d+))?\}/g, (_, pad) => {
    if (pad) {
      return num.toString().padStart(parseInt(pad, 10), '0');
    }
    return num.toString().padStart(2, '0');
  });
}

/**
 * Generate the next ID for a document type
 * Increments the sequence and returns the formatted ID
 */
export async function generateNextId(docType: DocType): Promise<{
  id: string;
  sequenceNum: number;
}> {
  const { pattern, sequenceKey } = await getIdConfig(docType);
  const registry = await loadRegistry();

  const currentNum = registry.id_sequences[sequenceKey] ?? 0;
  const nextNum = currentNum + 1;

  // Update sequence in registry
  registry.id_sequences[sequenceKey] = nextNum;
  await saveRegistry(registry);

  return {
    id: formatIdFromPattern(pattern, nextNum),
    sequenceNum: nextNum,
  };
}

/**
 * Preview what the next ID would be without incrementing
 */
export async function peekNextId(docType: DocType): Promise<string> {
  const { pattern, sequenceKey } = await getIdConfig(docType);
  const registry = await loadRegistry();

  const currentNum = registry.id_sequences[sequenceKey] ?? 0;
  return formatIdFromPattern(pattern, currentNum + 1);
}

/**
 * Parse an existing ID to extract its sequence number
 * Returns null if the ID doesn't match the expected pattern
 */
export function parseIdNumber(id: string, pattern: string): number | null {
  // Convert pattern to regex
  // "P-{num}" -> /^P-(\d+)$/
  const regexStr = pattern
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    .replace(/\\{num(?::\\d+)?\\}/g, '(\\d+)');

  const regex = new RegExp(`^${regexStr}$`);
  const match = id.match(regex);

  return match ? parseInt(match[1], 10) : null;
}

/**
 * Reset a sequence to a specific value (useful for migrations)
 */
export async function setSequence(sequenceKey: string, value: number): Promise<void> {
  const registry = await loadRegistry();
  registry.id_sequences[sequenceKey] = value;
  await saveRegistry(registry);
}
