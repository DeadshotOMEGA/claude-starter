import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { parse as parseYaml } from 'yaml';
import type { SkillManifest, DocType } from '../types.js';
import { getSkillForType } from './detection.js';

/**
 * Get base path for .claude directory
 */
function getBasePath(): string {
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
 * Load a skill manifest
 */
export async function loadManifest(skillName: string): Promise<SkillManifest | null> {
  const basePath = getBasePath();
  const manifestPath = join(basePath, '.claude', 'skills', skillName, 'manifest.yaml');

  if (!existsSync(manifestPath)) {
    return null;
  }

  const content = await readFile(manifestPath, 'utf-8');
  return parseYaml(content) as SkillManifest;
}

/**
 * Load manifest for a document type
 */
export async function loadManifestForType(docType: DocType): Promise<SkillManifest | null> {
  const skillName = getSkillForType(docType);
  if (!skillName) {
    return null;
  }
  return loadManifest(skillName);
}

/**
 * Extract required sections from a SKILL.md file
 * Parses "## Required Sections" and extracts section names
 */
export async function extractRequiredSectionsFromSkill(skillName: string): Promise<string[]> {
  const basePath = getBasePath();
  const skillPath = join(basePath, '.claude', 'skills', skillName, 'SKILL.md');

  if (!existsSync(skillPath)) {
    return [];
  }

  const content = await readFile(skillPath, 'utf-8');
  const sections: string[] = [];

  // Find "Required Sections" or similar heading
  const requiredMatch = content.match(/##\s*Required Sections[\s\S]*?(?=\n##|\n---|\Z)/i);
  if (requiredMatch) {
    // Extract numbered or bulleted items
    const itemMatches = requiredMatch[0].matchAll(/(?:^\d+\.\s*\*\*|^-\s*\*\*)([^*]+)\*\*/gm);
    for (const match of itemMatches) {
      sections.push(match[1].trim());
    }

    // Also try simpler format: "1. **Name**" or "- **Name**"
    if (sections.length === 0) {
      const simpleMatches = requiredMatch[0].matchAll(/(?:^\d+\.\s*|^-\s*)([A-Z][^:\n]+)/gm);
      for (const match of simpleMatches) {
        const name = match[1].trim().replace(/\*\*/g, '');
        if (name && !name.includes('(') && name.length < 50) {
          sections.push(name);
        }
      }
    }
  }

  return sections;
}

/**
 * Get validation rules from manifest or SKILL.md
 */
export async function getValidationRules(docType: DocType): Promise<{
  requiredSections: string[];
  patternRules: Array<{ id: string; pattern: string; message: string }>;
}> {
  const skillName = getSkillForType(docType);
  if (!skillName) {
    return { requiredSections: [], patternRules: [] };
  }

  // Try manifest first
  const manifest = await loadManifest(skillName);
  if (manifest?.structure?.required_sections) {
    return {
      requiredSections: manifest.structure.required_sections.map(s => s.name),
      patternRules: manifest.validation?.rules?.filter(r => r.pattern).map(r => ({
        id: r.id,
        pattern: r.pattern!,
        message: r.message,
      })) ?? [],
    };
  }

  // Fall back to extracting from SKILL.md
  const sections = await extractRequiredSectionsFromSkill(skillName);
  return {
    requiredSections: sections,
    patternRules: [],
  };
}

/**
 * Check if a manifest file exists for a skill
 */
export async function hasManifest(skillName: string): Promise<boolean> {
  const basePath = getBasePath();
  const manifestPath = join(basePath, '.claude', 'skills', skillName, 'manifest.yaml');
  return existsSync(manifestPath);
}
