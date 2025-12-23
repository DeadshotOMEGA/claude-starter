---
name: writing-claudemd
description: Write and maintain CLAUDE.md memory files for directories, modules, and projects. Use when creating CLAUDE.md files, setting up project memory, configuring memory hierarchy, or writing context documentation. Triggers on "CLAUDE.md", "memory file", "project context", "module context".
---

# CLAUDE.md Writing

Create and maintain context files that help Claude understand code structure and conventions.

## Contents

- [File Hierarchy](#file-hierarchy)
- [Content Separation](#content-separation)
- [Required Sections](#required-sections)
- [Best Practices](#best-practices)
- [Importing Files](#importing-files)
- [Quick Shortcuts](#quick-shortcuts)
- [Formatting](#formatting)
- [Template](#template)

## File Hierarchy

CLAUDE.md files work in a hierarchy - Claude reads all applicable levels:

| Tier | Location | Purpose |
|------|----------|---------|
| Personal | `~/.claude/CLAUDE.md` | User preferences, style, environment |
| Projects Root | `~/projects/.claude/CLAUDE.md` | Cross-project coding standards |
| Project-Specific | `project/CLAUDE.md` or `project/.claude/CLAUDE.md` | That project's stack, patterns, domain |
| Directory/Module | `src/module/CLAUDE.md` | Specific module context |

**Priority:** More specific files override general ones for conflicting guidance.

## Content Separation

Never duplicate content between tiers. Place content at the appropriate level:

| Content Type | Location |
|--------------|----------|
| Personal preferences (style, shortcuts) | Personal (`~/.claude/`) |
| Coding conventions used everywhere | Projects Root |
| Project-specific patterns | Project's CLAUDE.md |
| Module-specific context | Module's CLAUDE.md |

**Rule:** If it applies to multiple projects, move it up. If it's project-specific, keep it local.

## Required Sections

Every CLAUDE.md should have:

1. **Purpose** — 1 line: what this directory/module handles
2. **Key Patterns** — Conventions to follow (2-5 bullets)
3. **Critical Guidelines** — Warnings, security, must-follow rules
4. **File Structure** — What files exist and why (if not obvious)
5. **Notes** — Critical context that doesn't fit above (1-2 lines max)

## Best Practices

### Keep It Concise
Claude reads CLAUDE.md files every message. Long files waste context.

- 20-50 lines for most files
- Link to detailed docs instead of duplicating
- Focus on "what would cause mistakes without this"

### Use Visual Markers
Help Claude scan quickly:
- `⚠️` for warnings and common mistakes
- `🔒` for security considerations
- `📝` for important conventions

### Be Imperative
State rules directly:

**Good:** "Use admin client for database writes"
**Bad:** "You might want to consider using the admin client for writes"

### Focus on Non-Obvious Information
Don't explain what Claude already knows. Focus on:
- Project-specific conventions
- Non-standard patterns
- Common pitfalls unique to this codebase
- Where to find things

## Importing Files

CLAUDE.md files can import other files using `@path/to/file` syntax:

```markdown
See @README for project overview and @package.json for available commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Individual preferences: @~/.claude/my-project-instructions.md
```

**Import rules:**
- Relative and absolute paths allowed
- Home directory expansion (`~`) supported
- Max depth: 5 recursive hops
- Not evaluated inside code spans or code blocks

**Use imports to:**
- Reference existing docs instead of duplicating
- Allow team members to add personal instructions via home directory
- Share common instructions across worktrees

## Quick Shortcuts

**Add memories with `#` shortcut:**
```
# Always use bun instead of npm
```
Prompts for location (project, user, or local).

**Edit with `/memory` command:**
Opens file in default editor with validation.

**View loaded files:**
Run `/memory` to see all active memory sources.

## Formatting

```markdown
# [Directory/Module Name]

## Purpose
[1 line: What this directory/module handles]

## Key Patterns
- [Pattern 1]: [Brief description]
- [Pattern 2]: [Brief description]

## Critical Guidelines
- ⚠️ [Warning about common mistakes]
- 🔒 [Security consideration if applicable]
- 📝 [Important convention to follow]

## File Structure
- `[file].ts` - [Purpose]
- `[subfolder]/` - [What it contains]

## Notes
[Any critical context that doesn't fit above, 1-2 lines max]
```

## Template

Use `template.md` in this Skill directory for new CLAUDE.md files.

## Examples

### Good: Module-Level Context
```markdown
# repositories/

## Purpose
Database access layer using Supabase clients.

## Key Patterns
- Use `adminClient` for writes, `serverClient` for reads
- Include `tenant_id` in all queries
- Return typed results, throw on errors (never return null)

## Critical Guidelines
- ⚠️ Never bypass RLS - use admin client only when necessary
- 🔒 Validate tenant_id before all operations
```

### Bad: Too Verbose
```markdown
# repositories/

This folder contains all the repository files. Repositories are a design
pattern that abstracts database access. We use the repository pattern
because it separates concerns and makes testing easier...

[20 more lines of explanation Claude doesn't need]
```
