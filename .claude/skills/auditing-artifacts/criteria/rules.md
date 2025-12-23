# Rules Audit Criteria

Scoring criteria for `.claude/rules/*.md` files based on official rules documentation.

## Structure (5 points)

### Frontmatter Correctness (3 points)
- **3 pts:** Optional `paths` frontmatter correctly formatted if present
- **2 pts:** Has frontmatter but formatting issues
- **1 pt:** Frontmatter present but incorrect pattern
- **0 pts:** Invalid YAML or required paths missing when needed

### File Organization (1 point)
- **1 pt:** Rules organized in subdirectories by domain (frontend/, backend/, general/)
- **0 pts:** All rules in flat directory when categorization would help

### Appropriate Length (1 point)
- **1 pt:** 5-10 bullet points max per file
- **0 pts:** <3 bullets (too thin) or >15 bullets (should split)

**Path Frontmatter:**

**With path pattern:**
```yaml
---
paths: "**/*.test.{ts,tsx,js,jsx}"
---
```

**Without (always active):**
```markdown
# Security Rules

- Never log sensitive data
- Validate all user input
```

**Common Issues:**
- Path patterns too broad (triggers unnecessarily)
- Path patterns too narrow (never triggers)
- Missing `paths` when rule is file-type specific
- Using CLAUDE.md when rule should be path-specific

## Clarity (4 points)

### Domain Focus (1 point)
- **1 pt:** Rule covers single, clear domain (testing, git, database, etc.)
- **0 pts:** Mixes multiple unrelated domains

### Imperative Language (1 point)
- **1 pt:** Direct statements ("Use X", "Never Y")
- **0 pts:** Wishy-washy language

### Specific Patterns (1 point)
- **1 pt:** Provides concrete patterns to follow
- **0 pts:** Vague guidelines

### Brevity (1 point)
- **1 pt:** Concise bullets (1 line each)
- **0 pts:** Verbose explanations

**Good:**
```markdown
---
paths: "src/lib/repositories/**/*.ts"
---

# Repository Conventions

- Use `adminClient` for writes, `serverClient` for reads
- Include `tenant_id` in all queries
- Throw errors for "not found" - don't return null
```

**Bad:**
```markdown
# Various Rules

- When writing tests, you should consider... [50 words]
- For database access, it might be good to... [30 words]
- Git commits should probably... [20 words]
```

## Technical (5 points)

### Path Pattern Specificity (2 points)
- **2 pts:** Path pattern is specific enough to avoid over-triggering
- **1 pt:** Path pattern works but could be more specific
- **0 pts:** Path pattern too broad or too narrow

### Multiple Patterns (1 point)
- **1 pt:** Uses comma-separated patterns when needed for multiple file types
- **0 pts:** Separate rules when one rule with multiple patterns would work

### Glob Usage (1 point)
- **1 pt:** Uses globs correctly (`**/*.ts`, `src/**/*`)
- **0 pts:** Incorrect glob syntax

### Symlink Awareness (1 point)
- **1 pt:** Uses symlinks appropriately for shared rules across projects
- **0 pts:** Duplicates rules instead of symlinking

**Path Pattern Examples:**

**Too broad:**
```yaml
paths: "**/*.ts"  # Every TypeScript file
```

**Better:**
```yaml
paths: "src/lib/repositories/**/*.ts"  # Only repository files
```

**Multiple patterns:**
```yaml
paths: "**/*.test.ts, **/*.spec.ts, **/__tests__/**"
```

## Operational (4 points)

### Actionability (2 points)
- **2 pts:** Rules are specific and immediately actionable
- **1 pt:** Some actionable content but also fluff
- **0 pts:** Vague or non-actionable

### No Duplication (1 point)
- **1 pt:** Doesn't duplicate content from CLAUDE.md or other rules
- **0 pts:** Duplicates content that exists elsewhere

### Trigger Appropriateness (1 point)
- **1 pt:** Rule triggers when it should (correct path pattern or always-on)
- **0 pts:** Triggers too often or not often enough

**Actionable vs Vague:**

**Actionable:**
```markdown
- Use UTC for all timestamps
- Always include `tenant_id` in queries
- Throw errors for "not found" - don't return null
```

**Vague:**
```markdown
- Handle timestamps properly
- Make sure queries work correctly
- Error handling is important
```

## Maintainability (2 points)

### No Hardcoded Values (1 point)
- **1 pt:** No hardcoded file paths, URLs, or magic values
- **0 pts:** Contains hardcoded values

### Links to Detailed Docs (1 point)
- **1 pt:** Links to detailed documentation if rules need explanation
- **0 pts:** Tries to explain everything inline

**Good:**
```markdown
- Follow API conventions in @docs/api-patterns.md
```

**Bad:**
```markdown
- API conventions: [30 lines of explanation]
```

## Red Flags (Automatic Deductions)

- **-2 pts:** >15 bullet points (should split into multiple rules)
- **-2 pts:** Duplicates content from CLAUDE.md
- **-1 pt:** Mixes multiple unrelated domains
- **-1 pt:** Path pattern too broad (matches everything)
- **-1 pt:** <3 bullets (too thin, combine with another rule)
- **-1 pt:** Verbose explanations instead of concise bullets
- **-1 pt:** Wishy-washy language

## Excellent Rule Checklist

An 18-20 point rule has:

- ✅ Optional `paths` frontmatter if file-type specific
- ✅ Organized in subdirectory by domain if many rules
- ✅ 5-10 bullet points (concise)
- ✅ Single domain focus
- ✅ Imperative language ("Use X", "Never Y")
- ✅ Specific, concrete patterns
- ✅ Brief bullets (1 line each)
- ✅ Specific path pattern (not too broad/narrow)
- ✅ Uses multiple patterns with commas if needed
- ✅ Correct glob syntax
- ✅ Actionable, immediately applicable
- ✅ No duplication from CLAUDE.md or other rules
- ✅ Triggers appropriately for intended files
- ✅ No hardcoded values
- ✅ Links to docs for details

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| Path pattern too broad | Make more specific (e.g., `**/*.ts` → `src/lib/**/*.ts`) |
| No path pattern for file-specific | Add `paths:` frontmatter |
| >15 bullets | Split into multiple rule files by subtopic |
| <3 bullets | Combine with related rule or add more guidance |
| Mixes domains | Split into separate rules (testing.md, git.md, etc.) |
| Verbose bullets | Condense to 1 line each |
| Wishy-washy language | Make imperative ("Use X" not "Consider X") |
| Vague guidance | Provide specific patterns and examples |
| Duplicates CLAUDE.md | Remove and keep only in appropriate tier |
| Multiple patterns needed | Use comma-separated: `paths: "*.test.ts, *.spec.ts"` |
| Hardcoded paths | Use relative paths or imports |
| Missing docs link | Add `@docs/reference.md` for detailed info |

## Rule Categories

| File | Paths | Purpose |
|------|-------|---------|
| `testing.md` | `**/*.test.*` | Test conventions, mocking patterns |
| `git-workflow.md` | — (always on) | Git flow, commits, branches |
| `database.md` | `**/repositories/**` | DB access patterns, RLS |
| `api.md` | `**/api/**` | API conventions, errors |
| `security.md` | — (always on) | Security rules |
| `components.md` | `**/components/**` | React patterns, a11y |
| `releases.md` | — (always on) | Release workflow, versioning |

## Subdirectory Organization

When you have many rules, organize by domain:

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

## Example Rules

**Testing Rules:**
```markdown
---
paths: "**/*.test.{ts,tsx,js,jsx}, **/*.spec.{ts,tsx,js,jsx}"
---

# Testing Conventions

- Write tests first when fixing bugs (capture the failure)
- Use descriptive test names explaining expected behavior
- Prefer integration tests over unit tests for business logic
- Mock external services, not internal modules
```

**Database Rules:**
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

**Security Rules (Always Active):**
```markdown
# Security Rules

- Never log sensitive data (passwords, tokens, PII)
- Validate all user input at system boundaries
- Use parameterized queries for database access
- Check authorization before any data access
```
