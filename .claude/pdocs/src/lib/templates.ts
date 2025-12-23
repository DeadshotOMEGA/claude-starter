import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import type { DocType, TemplateResult } from '../types.js';
import { resolveTypeAlias, getSkillForType } from './detection.js';

/**
 * Base paths for template discovery
 */
function getBasePath(): string {
  // Find .claude directory by traversing up
  let current = process.cwd();
  while (current !== '/') {
    if (existsSync(join(current, '.claude'))) {
      return current;
    }
    current = dirname(current);
  }
  return process.cwd();
}

/**
 * Template search paths in priority order
 */
function getTemplatePaths(type: DocType, basePath: string): string[] {
  const skill = getSkillForType(type);
  const paths: string[] = [];

  // 1. Skills have authority (tied to SKILL.md)
  if (skill) {
    paths.push(join(basePath, '.claude', 'skills', skill, 'template.md'));
  }
  paths.push(join(basePath, '.claude', 'skills', `writing-${type}`, 'template.md'));
  paths.push(join(basePath, '.claude', 'skills', type, 'template.md'));

  // 2. Standalone templates (legacy/shared)
  paths.push(join(basePath, '.claude', 'file-templates', `${type}.template.md`));
  paths.push(join(basePath, '.claude', 'file-templates', `${type}.md`));

  return paths;
}

/**
 * Resolve and load a template by type
 */
export async function getTemplate(typeOrAlias: string): Promise<TemplateResult | null> {
  const docType = resolveTypeAlias(typeOrAlias);
  if (!docType) {
    return null;
  }

  const basePath = getBasePath();
  const searchPaths = getTemplatePaths(docType, basePath);

  for (const templatePath of searchPaths) {
    if (existsSync(templatePath)) {
      const content = await readFile(templatePath, 'utf-8');
      const isSkill = templatePath.includes('/skills/');
      const skill = isSkill ? templatePath.split('/skills/')[1]?.split('/')[0] : undefined;

      return {
        path: templatePath,
        content,
        source: isSkill ? 'skill' : 'file-template',
        skill,
      };
    }
  }

  return null;
}

/**
 * List all available templates
 */
export async function listTemplates(): Promise<Array<{ type: DocType; path: string; source: string }>> {
  const basePath = getBasePath();
  const results: Array<{ type: DocType; path: string; source: string }> = [];
  const seen = new Set<DocType>();

  // Check all known types
  const types: DocType[] = [
    'plan', 'investigation', 'requirements', 'feature-spec',
    'api-contract', 'user-story', 'user-flow', 'agent',
    'skill', 'claudemd', 'rule', 'command', 'readme', 'changelog'
  ];

  for (const type of types) {
    if (seen.has(type)) continue;

    const template = await getTemplate(type);
    if (template) {
      seen.add(type);
      results.push({
        type,
        path: template.path,
        source: template.source,
      });
    }
  }

  return results;
}

/**
 * Apply variable substitution to template content
 */
export function applyTemplateVars(
  content: string,
  vars: Record<string, string>
): string {
  let result = content;

  for (const [key, value] of Object.entries(vars)) {
    // Replace {key}, {{key}}, [key], and ${key} patterns
    const patterns = [
      new RegExp(`\\{${key}\\}`, 'g'),
      new RegExp(`\\{\\{${key}\\}\\}`, 'g'),
      new RegExp(`\\[${key}\\]`, 'g'),
      new RegExp(`\\$\\{${key}\\}`, 'g'),
    ];

    for (const pattern of patterns) {
      result = result.replace(pattern, value);
    }
  }

  return result;
}

/**
 * Fetch remote template
 */
export async function fetchRemoteTemplate(url: string): Promise<string> {
  // Handle GitHub shorthand
  let resolvedUrl = url;
  if (url.startsWith('github:')) {
    const path = url.slice(7);
    resolvedUrl = `https://raw.githubusercontent.com/${path}`;
  }

  const response = await fetch(resolvedUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch template: ${response.status} ${response.statusText}`);
  }

  return response.text();
}
