---
name: writing-investigations
description: Write investigation documents that bundle all context needed for implementation. Use when creating investigation.md files or context bundles for features/fixes.
---

# Investigation Writing

Create investigation documents that consolidate all context needed for implementation.

## Purpose

Investigation docs bundle:
- All relevant file paths with line numbers
- Data flows and patterns
- Integration points
- Gotchas and edge cases

This prevents repeated exploration and gives implementers everything in one place.

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Goal** — One sentence: what we're building or fixing
2. **Related Docs** — Links to specs, requirements, designs
3. **Key Files** — Categorized file paths with line numbers
4. **Database Tables** — Schema relevant to the task
5. **Data Flow** — Step-by-step flow with file references
6. **Patterns to Follow** — Existing patterns to match
7. **Integration Points** — External connections
8. **Notes** — Gotchas, edge cases, important context

## File Reference Format

Always include line numbers for precision:
```
path/to/file.ts:45 – [What this location handles]
path/to/file.ts:89-145 – [Range for larger sections]
```

## Best Practices

- Be exhaustive — include every relevant file
- Group files by purpose (Entry Points, Core Logic, UI, API, etc.)
- Include both the "what" and "why" for patterns
- Note anything that would surprise an implementer
