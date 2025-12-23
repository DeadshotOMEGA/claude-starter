# CLAUDE.md Audit Criteria

Scoring criteria for `CLAUDE.md` files based on official memory documentation.

## Structure (5 points)

### Hierarchy Compliance (3 points)
- **3 pts:** Placed at correct tier in hierarchy (Personal, Projects Root, Project, Module)
- **2 pts:** Correct tier but content could be better separated
- **1 pt:** Some confusion about tier placement
- **0 pts:** Wrong tier or duplicates content across tiers

### Section Organization (1 point)
- **1 pt:** Clear sections with markdown headings
- **0 pts:** Wall of text, no structure

### Appropriate Length (1 point)
- **1 pt:** 20-50 lines (most files)
- **0 pts:** <10 lines (too thin) or >100 lines (too verbose)

**Hierarchy Tiers:**

| Tier | Location | Content Type |
|------|----------|--------------|
| Personal | `~/.claude/CLAUDE.md` | User preferences, style, environment |
| Projects Root | `~/projects/.claude/CLAUDE.md` | Cross-project coding standards |
| Project | `project/CLAUDE.md` | Project's stack, patterns, domain |
| Module | `src/module/CLAUDE.md` | Module-specific context |

**Common Issues:**
- Project-specific patterns in personal CLAUDE.md
- Personal preferences in project CLAUDE.md
- Duplicating content across tiers
- Module context in project root CLAUDE.md

## Clarity (4 points)

### Purpose Statement (1 point)
- **1 pt:** Clear 1-line purpose if module/directory level
- **0 pts:** No purpose statement or unclear

### Imperative Language (1 point)
- **1 pt:** Direct statements ("Use X for Y", "Never do Z")
- **0 pts:** Wishy-washy language ("You might want to...", "Consider...")

### Non-Obvious Information (1 point)
- **1 pt:** Focuses on project-specific, non-standard patterns
- **0 pts:** Explains things Claude already knows

### Visual Markers (1 point)
- **1 pt:** Uses markers for warnings (⚠️), security (🔒), notes (📝)
- **0 pts:** No visual markers

**Good Language:**
- "Use admin client for database writes"
- "Include tenant_id in all queries"
- "⚠️ Never bypass RLS"

**Bad Language:**
- "You might want to consider using the admin client for writes"
- "It's generally a good idea to include tenant_id"

## Technical (5 points)

### Content Separation (2 points)
- **2 pts:** No duplicate content across tier levels
- **1 pt:** Some duplication but mostly separated
- **0 pts:** Significant duplication across tiers

### Import Usage (1 point)
- **1 pt:** Uses `@path/to/file` imports for large referenced files
- **0 pts:** Duplicates content that should be imported

### Specificity (1 point)
- **1 pt:** Contains project/module-specific patterns and conventions
- **0 pts:** Generic information applicable everywhere

### Path-Specific Rules (1 point)
- **1 pt:** Uses `.claude/rules/*.md` for path-specific guidance instead of cramming in CLAUDE.md
- **0 pts:** Path-specific rules embedded in CLAUDE.md

**Import Example:**
```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

**Rules vs CLAUDE.md:**
- **CLAUDE.md:** Project-wide context
- **Rules:** Path-specific guidance (e.g., testing conventions for `**/*.test.ts`)

## Operational (4 points)

### Actionable Guidance (2 points)
- **2 pts:** Provides specific, actionable instructions
- **1 pt:** Some actionable content but also fluff
- **0 pts:** Vague or non-actionable

### Common Commands (1 point)
- **1 pt:** Lists frequently used commands (build, test, lint)
- **0 pts:** Missing common commands

### Workflow Shortcuts (1 point)
- **1 pt:** Documents shortcuts, conventions, or non-obvious workflows
- **0 pts:** No workflow documentation

**Good Actionable Content:**
```markdown
## Common Commands
- `bun test` — Run test suite
- `bun run build` — Build project
- `gh pr create` — Create pull request

## Repository Patterns
- Use `adminClient` for writes, `serverClient` for reads
- Include `tenant_id` in all queries
```

## Maintainability (2 points)

### No Hardcoded Values (1 point)
- **1 pt:** No hardcoded file paths, URLs, or values that will change
- **0 pts:** Contains hardcoded values

### Link to Docs (1 point)
- **1 pt:** Links to detailed documentation instead of duplicating
- **0 pts:** Duplicates documentation content

**Good:**
```markdown
See architecture docs in `docs/architecture.md`
```

**Bad:**
```markdown
[50 lines explaining architecture that should be in docs/]
```

## Red Flags (Automatic Deductions)

- **-2 pts:** >100 lines (too verbose)
- **-2 pts:** Duplicates content from another tier
- **-1 pt:** Explains basics Claude knows (what TypeScript is, etc.)
- **-1 pt:** <10 lines (too thin, probably missing useful context)
- **-1 pt:** No structure (wall of text)
- **-1 pt:** Wishy-washy language instead of imperatives

## Excellent CLAUDE.md Checklist

An 18-20 point CLAUDE.md has:

- ✅ Placed at correct tier in hierarchy
- ✅ 20-50 lines (concise but useful)
- ✅ Clear sections with markdown headings
- ✅ 1-line purpose statement (if module/directory level)
- ✅ Imperative language ("Use X", "Never Y")
- ✅ Visual markers (⚠️, 🔒, 📝)
- ✅ No duplicate content across tiers
- ✅ Uses `@imports` for large referenced files
- ✅ Project/module-specific information only
- ✅ Delegates path-specific rules to `.claude/rules/`
- ✅ Actionable, specific instructions
- ✅ Lists common commands
- ✅ Documents workflow shortcuts
- ✅ No hardcoded values
- ✅ Links to docs instead of duplicating
- ✅ Focuses on non-obvious information

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| Too long (>100 lines) | Cut to 20-50 lines, link to docs for details |
| Duplicates tier content | Move content to appropriate tier |
| Explains basics | Remove explanations of standard concepts |
| No structure | Add markdown headings for sections |
| Wishy-washy language | Make imperative ("Use X" not "Consider X") |
| No visual markers | Add ⚠️ for warnings, 🔒 for security |
| Missing common commands | Add commands users run frequently |
| Hardcoded paths | Use relative paths or variables |
| Duplicates docs | Link to docs instead of copying |
| Generic content | Make project/module-specific |
| Path-specific rules in CLAUDE.md | Move to `.claude/rules/` with path patterns |
| Too thin (<10 lines) | Add key patterns, common mistakes, workflow shortcuts |

## Module-Level Example

**Good:**
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

**Bad:**
```markdown
# repositories/

This folder contains all the repository files. Repositories are a design
pattern that abstracts database access. We use the repository pattern
because it separates concerns and makes testing easier. The repository
pattern was invented by Martin Fowler and is part of Domain-Driven Design...

[50 more lines explaining the repository pattern]
```

## Project-Level Example

**Good:**
```markdown
## Common Commands
- `bun test` — Run test suite
- `bun run build` — Build project
- `bun run dev` — Start dev server

## Code Standards
- ALWAYS use `bun` instead of `npm`
- NEVER use `any` type—look up actual types
- ALWAYS throw errors early—no fallbacks

## Project Structure
See @docs/architecture.md for detailed architecture overview.
```
