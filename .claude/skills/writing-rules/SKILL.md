---
name: writing-rules
description: Write modular rule files for .claude/rules/ with path-based activation. Use when creating rules, adding testing conventions, writing git workflow rules, or setting up path-scoped guidance. Triggers on "rules", "conventions", "path-specific", "testing rules", "git rules".
---

# Rules Writing

Create modular rule files that activate based on file paths or contexts.

## Contents

- [File Location](#file-location)
- [User-Level Rules](#user-level-rules)
- [Frontmatter](#frontmatter)
- [Content Structure](#content-structure)
- [Path Patterns](#path-patterns)
- [Best Practices](#best-practices)
- [Symlinks for Shared Rules](#symlinks-for-shared-rules)
- [Subdirectory Organization](#subdirectory-organization)
- [Common Rule Categories](#common-rule-categories)
- [Template](#template)

## File Location

Rules live in `.claude/rules/` and are auto-loaded based on path patterns:

```
.claude/rules/
├── testing.md         # Activates for test files
├── git-workflow.md    # Always active (no path filter)
├── database.md        # Activates for repository files
└── security.md        # Always active
```

## User-Level Rules

Personal rules that apply to all your projects live in `~/.claude/rules/`:

```
~/.claude/rules/
├── preferences.md     # Your coding preferences
├── workflows.md       # Your preferred workflows
└── shortcuts.md       # Personal shortcuts
```

**Behavior:**
- Loaded before project rules (project rules take precedence)
- Apply across all projects you work on
- Not shared with team (personal only)

**Use for:**
- Personal coding style preferences
- Editor/tooling shortcuts you use everywhere
- Debugging patterns you prefer

## Frontmatter

Optional YAML frontmatter controls when the rule activates:

```yaml
---
paths: "**/*.test.{ts,tsx,js,jsx}, **/*.spec.{ts,tsx,js,jsx}"
---
```

| Field | Purpose |
|-------|---------|
| `paths` | Glob pattern(s) for when this rule activates. Comma-separated for multiple patterns. |

**Omit `paths`** for rules that should always be active in this project.

## Content Structure

Keep rules concise and actionable:

```markdown
---
paths: "src/lib/repositories/**/*.ts"
---

# Repository Conventions

- Use admin client for writes, server client for reads
- Include tenant_id in all queries
- Throw errors for "not found" - don't return null
- Use typed results from generated types
```

## Path Patterns

Use glob patterns to target specific files:

| Pattern | Matches |
|---------|---------|
| `**/*.test.ts` | All TypeScript test files |
| `src/components/**/*.tsx` | All TSX files in components |
| `**/api/**/*.ts` | All TypeScript API files |
| `src/lib/repositories/**` | Everything in repositories folder |
| `*.md` | Markdown files in root only |

**Multiple patterns:** Comma-separated
```yaml
paths: "**/*.test.ts, **/*.spec.ts, **/__tests__/**"
```

## Best Practices

### One Rule Per Domain
Keep rules focused on a single concern:
- `testing.md` — Test conventions only
- `git-workflow.md` — Git/branching rules only
- `database.md` — Database access patterns only

### Use Specific Paths
Avoid over-triggering by being specific:

**Too broad:**
```yaml
paths: "**/*.ts"  # Triggers for ALL TypeScript files
```

**Better:**
```yaml
paths: "src/lib/repositories/**/*.ts"  # Only repository files
```

### Imperative Statements
State rules directly:

**Good:** "Use UTC for all timestamps"
**Bad:** "You should consider using UTC for timestamps"

### Keep It Short
5-10 bullet points max per file. Link to detailed docs if needed.

### No Duplication
If a rule applies everywhere, put it in CLAUDE.md instead.

## Symlinks for Shared Rules

Share common rules across multiple projects using symlinks:

```bash
# Symlink a shared rules directory
ln -s ~/shared-claude-rules .claude/rules/shared

# Symlink individual rule files
ln -s ~/company-standards/security.md .claude/rules/security.md
```

**Benefits:**
- Maintain rules in one location, use in many projects
- Updates propagate automatically
- Keep company standards synchronized

**Notes:**
- Symlinks are resolved and contents loaded normally
- Circular symlinks are detected and handled gracefully
- Works with both files and directories

## Subdirectory Organization

Organize rules into subdirectories for larger projects:

```
.claude/rules/
├── frontend/
│   ├── react.md
│   └── styles.md
├── backend/
│   ├── api.md
│   └── database.md
└── general/
    ├── git-workflow.md
    └── security.md
```

All `.md` files are discovered recursively regardless of depth.

## Common Rule Categories

| File | Paths | Purpose |
|------|-------|---------|
| `testing.md` | `**/*.test.*` | Test conventions, mocking patterns |
| `git-workflow.md` | — | Git flow, commit formats, branch naming |
| `database.md` | `**/repositories/**` | DB access patterns, RLS rules |
| `api.md` | `**/api/**` | API conventions, error handling |
| `security.md` | — | Always-on security rules |
| `components.md` | `**/components/**` | React patterns, accessibility |
| `releases.md` | — | Release workflow, versioning |

## Template

```markdown
---
paths: "[glob pattern]"
---

# [Domain] Conventions

- [Rule 1]: [Brief explanation if needed]
- [Rule 2]
- [Rule 3]

## [Subsection if needed]

- [More specific rules]
```

## Examples

### Testing Rules
```markdown
---
paths: "**/*.test.{ts,tsx,js,jsx}, **/*.spec.{ts,tsx,js,jsx}"
---

# Testing Conventions

- Write tests first when fixing bugs (capture the failure)
- Use descriptive test names that explain expected behavior
- Prefer integration tests over unit tests for business logic
- Mock external services, not internal modules
```

### Database Rules
```markdown
---
paths: "src/lib/repositories/**/*.ts"
---

# Repository Conventions

- Use `adminClient` for writes, `serverClient` for reads
- Always include `tenant_id` in queries
- Return typed results; throw on errors (never return null)
- Use generated types from `database.types.ts`
```

### Always-Active Security Rules
```markdown
# Security Rules

- Never log sensitive data (passwords, tokens, PII)
- Validate all user input at system boundaries
- Use parameterized queries for database access
- Check authorization before any data access
```
