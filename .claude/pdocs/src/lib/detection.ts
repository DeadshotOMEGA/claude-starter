import type { DocType } from '../types.js';

/**
 * Path patterns for document type detection
 */
const PATH_PATTERNS: Array<{ pattern: RegExp; type: DocType }> = [
  { pattern: /\.claude\/agents\/.*\.md$/, type: 'agent' },
  { pattern: /\.claude\/skills\/.*\/SKILL\.md$/, type: 'skill' },
  { pattern: /CLAUDE\.md$/, type: 'claudemd' },
  { pattern: /\.claude\/rules\/.*\.md$/, type: 'rule' },
  { pattern: /\.claude\/commands\/.*\.md$/, type: 'command' },
  { pattern: /docs\/plans\/.*\/plan\.(md|yaml)$/, type: 'plan' },
  { pattern: /investigation.*\.(md|yaml)$/, type: 'investigation' },
  { pattern: /requirements.*\.(md|yaml)$/, type: 'requirements' },
  { pattern: /docs\/feature-spec\/.*\.(md|yaml)$/, type: 'feature-spec' },
  { pattern: /api-contract.*\.(yaml|json)$/, type: 'api-contract' },
  { pattern: /docs\/user-stories\/.*\.(md|yaml)$/, type: 'user-story' },
  { pattern: /docs\/user-flows\/.*\.md$/, type: 'user-flow' },
  { pattern: /README\.md$/, type: 'readme' },
  { pattern: /CHANGELOG\.md$/, type: 'changelog' },
];

/**
 * Type aliases for flexible matching
 */
export const TYPE_ALIASES: Record<string, DocType> = {
  'plan': 'plan',
  'implementation-plan': 'plan',
  'investigation': 'investigation',
  'investigation-topic': 'investigation',
  'context': 'investigation',
  'requirements': 'requirements',
  'feature-requirements': 'requirements',
  'reqs': 'requirements',
  'feature': 'feature-spec',
  'feature-spec': 'feature-spec',
  'api': 'api-contract',
  'api-contract': 'api-contract',
  'story': 'user-story',
  'user-story': 'user-story',
  'flow': 'user-flow',
  'user-flow': 'user-flow',
  'agent': 'agent',
  'subagent': 'agent',
  'skill': 'skill',
  'claude': 'claudemd',
  'claudemd': 'claudemd',
  'rule': 'rule',
  'command': 'command',
  'readme': 'readme',
  'changelog': 'changelog',
};

/**
 * Map document types to their associated skills
 */
export const TYPE_TO_SKILL: Record<DocType, string | null> = {
  'plan': 'writing-plans',
  'investigation': 'writing-investigations',
  'requirements': 'writing-requirements',
  'feature-spec': 'writing-feature-docs',
  'api-contract': 'writing-api-endpoints',
  'user-story': null,
  'user-flow': null,
  'agent': 'writing-subagents',
  'skill': 'writing-skills',
  'claudemd': 'writing-claudemd',
  'rule': 'writing-rules',
  'command': 'writing-commands',
  'readme': 'writing-readmes',
  'changelog': 'changelog',
};

/**
 * Detect document type from file path
 */
export function detectDocType(filePath: string): DocType | null {
  for (const { pattern, type } of PATH_PATTERNS) {
    if (pattern.test(filePath)) {
      return type;
    }
  }
  return null;
}

/**
 * Resolve a type alias to canonical type
 */
export function resolveTypeAlias(alias: string): DocType | null {
  const normalized = alias.toLowerCase().trim();
  return TYPE_ALIASES[normalized] ?? null;
}

/**
 * Get the skill associated with a document type
 */
export function getSkillForType(docType: DocType): string | null {
  return TYPE_TO_SKILL[docType];
}

/**
 * Get all known document types
 */
export function getAllDocTypes(): DocType[] {
  return Object.values(TYPE_ALIASES).filter(
    (v, i, a) => a.indexOf(v) === i
  ) as DocType[];
}
