import { existsSync } from 'fs';
import { join, dirname, resolve } from 'path';
import type { ValidationError, ValidationWarning } from '../types.js';

/**
 * Link types found in markdown documents
 */
interface ExtractedLink {
  text: string;
  target: string;
  line: number;
  type: 'internal' | 'external' | 'anchor';
}

/**
 * Link verification result
 */
export interface LinkVerificationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  stats: {
    total: number;
    internal: number;
    external: number;
    anchors: number;
    broken: number;
  };
}

/**
 * Extract all links from markdown content
 */
export function extractLinks(content: string): ExtractedLink[] {
  const links: ExtractedLink[] = [];
  const lines = content.split('\n');

  // Match markdown links: [text](target)
  const linkRegex = /\[([^\]]*)\]\(([^)]+)\)/g;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let match;

    while ((match = linkRegex.exec(line)) !== null) {
      const target = match[2].split('#')[0].trim(); // Remove anchor
      const fullTarget = match[2].trim();

      let type: 'internal' | 'external' | 'anchor';

      if (fullTarget.startsWith('#')) {
        type = 'anchor';
      } else if (
        fullTarget.startsWith('http://') ||
        fullTarget.startsWith('https://') ||
        fullTarget.startsWith('mailto:')
      ) {
        type = 'external';
      } else {
        type = 'internal';
      }

      links.push({
        text: match[1],
        target: fullTarget,
        line: i + 1,
        type,
      });
    }
  }

  return links;
}

/**
 * Extract heading anchors from markdown content
 */
function extractAnchors(content: string): Set<string> {
  const anchors = new Set<string>();
  const lines = content.split('\n');

  // Match headings: # Heading, ## Heading, etc.
  const headingRegex = /^(#{1,6})\s+(.+)$/;

  for (const line of lines) {
    const match = headingRegex.exec(line);
    if (match) {
      // Convert heading to GitHub-style anchor
      const anchor = match[2]
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Remove special chars
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-'); // Collapse multiple hyphens

      anchors.add(anchor);
    }
  }

  return anchors;
}

/**
 * Verify internal links exist
 */
function verifyInternalLink(
  link: ExtractedLink,
  documentPath: string
): ValidationError | null {
  const docDir = dirname(documentPath);

  // Handle the path part (before any anchor)
  const pathPart = link.target.split('#')[0];
  const anchorPart = link.target.includes('#')
    ? link.target.split('#')[1]
    : null;

  if (!pathPart) {
    // This is just an anchor reference, handled separately
    return null;
  }

  // Resolve relative path from document location
  const targetPath = resolve(docDir, pathPart);

  if (!existsSync(targetPath)) {
    return {
      rule: 'broken-link',
      message: `Broken link: "${link.text}" → ${link.target}`,
      line: link.line,
      suggestion: `File not found: ${targetPath}`,
    };
  }

  return null;
}

/**
 * Verify anchor links within the same document
 */
function verifyAnchorLink(
  link: ExtractedLink,
  anchors: Set<string>
): ValidationError | null {
  const anchor = link.target.slice(1); // Remove leading #

  // Normalize anchor
  const normalizedAnchor = anchor
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');

  if (!anchors.has(normalizedAnchor)) {
    return {
      rule: 'broken-anchor',
      message: `Broken anchor link: "${link.text}" → ${link.target}`,
      line: link.line,
      suggestion: `No heading found matching anchor "${anchor}"`,
    };
  }

  return null;
}

/**
 * Verify all links in a document
 */
export function verifyLinks(
  content: string,
  documentPath: string,
  options?: {
    checkExternal?: boolean;
  }
): LinkVerificationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  const links = extractLinks(content);
  const anchors = extractAnchors(content);

  const stats = {
    total: links.length,
    internal: 0,
    external: 0,
    anchors: 0,
    broken: 0,
  };

  for (const link of links) {
    switch (link.type) {
      case 'internal': {
        stats.internal++;
        const error = verifyInternalLink(link, documentPath);
        if (error) {
          errors.push(error);
          stats.broken++;
        }
        break;
      }

      case 'anchor': {
        stats.anchors++;
        const error = verifyAnchorLink(link, anchors);
        if (error) {
          errors.push(error);
          stats.broken++;
        }
        break;
      }

      case 'external': {
        stats.external++;
        // External links are not checked by default (would require network)
        // but we can add a warning for potentially broken patterns
        if (link.target.includes('localhost') || link.target.includes('127.0.0.1')) {
          warnings.push({
            rule: 'localhost-link',
            message: `Link to localhost: "${link.text}" → ${link.target}`,
            line: link.line,
          });
        }
        break;
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    stats,
  };
}

/**
 * Check cross-document anchor links
 * For links like [text](file.md#section), verify the anchor exists in the target file
 */
export async function verifyCrossDocumentAnchors(
  content: string,
  documentPath: string
): Promise<ValidationWarning[]> {
  const warnings: ValidationWarning[] = [];
  const links = extractLinks(content);

  for (const link of links) {
    if (link.type === 'internal' && link.target.includes('#')) {
      const [pathPart, anchorPart] = link.target.split('#');
      const docDir = dirname(documentPath);
      const targetPath = resolve(docDir, pathPart);

      if (existsSync(targetPath)) {
        try {
          const { readFile } = await import('fs/promises');
          const targetContent = await readFile(targetPath, 'utf-8');
          const targetAnchors = extractAnchors(targetContent);

          const normalizedAnchor = anchorPart
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-');

          if (!targetAnchors.has(normalizedAnchor)) {
            warnings.push({
              rule: 'cross-doc-anchor',
              message: `Anchor may not exist in target: "${link.text}" → ${link.target}`,
              line: link.line,
            });
          }
        } catch {
          // Ignore read errors
        }
      }
    }
  }

  return warnings;
}
