# Rules Syntax Reference

Complete reference for `.claude/rules/` file syntax and path-scoped rule configuration.

---

## Basic Structure

Rules are **Markdown files** stored in the `.claude/rules/` directory. Each file contains instructions that apply either globally or to specific file patterns.

### Directory Layout

```
.claude/
└── rules/
    ├── testing.md
    ├── security.md
    ├── api/
    │   └── endpoints.md
    └── frontend/
        ├── components.md
        └── styling.md
```

### File Format

Each rule file is a standard Markdown file with optional YAML frontmatter:

```markdown
---
paths:
  - src/**/*.ts
  - lib/**/*.ts
---

# TypeScript Conventions

- Use strict mode
- Avoid `any` type
- Prefer interfaces over type aliases for objects
```

---

## YAML Frontmatter

Optional frontmatter at the start of rule files enables path scoping.

### Syntax

```yaml
---
paths:
  - pattern1
  - pattern2
---
```

### Required Format

- Must start with `---` on first line
- Must end with `---` on its own line
- `paths` field contains array of glob patterns
- All other content follows after closing `---`

### Without Frontmatter

Files without frontmatter apply **globally** to all files in the project:

```markdown
# Global Security Rules

- Never commit secrets
- Validate all user input
- Use parameterized queries
```

---

## Glob Patterns for Path Scoping

The `paths` field accepts standard glob patterns to scope rules to specific files.

### Basic Patterns

| Pattern | Matches |
|---------|---------|
| `*.ts` | TypeScript files in project root only |
| `**/*.ts` | TypeScript files anywhere in project |
| `src/*` | Direct children of src/ |
| `src/**/*` | All files recursively under src/ |
| `*.{ts,tsx}` | TypeScript and TSX files in root |

### Advanced Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.test.ts` | All test files |
| `src/**/*.{ts,tsx}` | TS/TSX files under src/ |
| `{src,lib}/**/*.ts` | TS files under src/ or lib/ |
| `!**/node_modules/**` | Exclude node_modules |
| `api/**/*.ts` | API directory TypeScript files |

### Brace Expansion

Use braces for OR logic in patterns:

```yaml
paths:
  - "**/*.{js,ts,jsx,tsx}"       # All JavaScript/TypeScript
  - "{src,packages}/**/*"        # Multiple directories
  - "*.{json,yaml,yml}"          # Config files
```

### Multiple Patterns

List multiple patterns for complex scoping:

```yaml
paths:
  - src/**/*.ts
  - tests/**/*.test.ts
  - lib/**/*.ts
```

Rules apply when **any** pattern matches the current file.

### Comma-Separated (Alternative Syntax)

Patterns can also be comma-separated in a single string:

```yaml
paths:
  - "src/**/*.ts, tests/**/*.test.ts"
```

---

## Subdirectory Organization

Organize rules into subdirectories for large projects:

```
.claude/rules/
├── code-style.md           # Global style rules
├── security.md             # Security rules
├── api/
│   ├── rest.md             # REST API conventions
│   └── graphql.md          # GraphQL conventions
├── frontend/
│   ├── components.md       # Component patterns
│   ├── state.md            # State management
│   └── testing.md          # Frontend testing
└── backend/
    ├── database.md         # Database conventions
    └── services.md         # Service patterns
```

### Benefits

- Logical grouping of related rules
- Easier navigation in large projects
- Team members can own specific rule areas

---

## Symlink Support

Rules directory supports symbolic links for shared configurations:

```bash
# Link shared rules from another location
ln -s /path/to/shared-rules/security.md .claude/rules/security.md

# Link entire subdirectory
ln -s /path/to/shared-rules/api .claude/rules/api
```

### Use Cases

- Share rules across multiple repositories
- Maintain company-wide standards in a central repo
- Override specific rules while inheriting others

---

## User-Level Rules

Personal rules that apply to all projects:

### Location

```
~/.claude/rules/
└── *.md
```

### Behavior

- Loaded for every project
- Lower priority than project rules
- Not shared with team (personal preferences)

### Example

```markdown
# ~/.claude/rules/preferences.md

- Use vim-style examples
- Prefer functional patterns
- Include performance considerations
```

---

## Rule Loading Behavior

### When Rules Load

1. **Session start** - All applicable rules load
2. **File access** - Path-scoped rules evaluated against accessed file
3. **Directory change** - Rules re-evaluated for new context

### Matching Logic

For path-scoped rules:
1. Get current file path (relative to project root)
2. Test against each pattern in `paths`
3. If **any** pattern matches, rule content is active
4. Unscoped rules (no frontmatter) always active

### Precedence

When rules conflict:
1. More specific path patterns take precedence
2. Later-loaded files override earlier ones
3. Project rules override user rules

---

## Examples

### Testing Rules (Scoped)

```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - tests/**/*
---

# Testing Conventions

- Use descriptive test names
- One assertion per test when possible
- Mock external dependencies
- Test edge cases explicitly
```

### Component Rules (Scoped)

```markdown
---
paths:
  - src/components/**/*.tsx
  - src/components/**/*.ts
---

# Component Standards

- Use functional components
- Props interface above component
- Export component as default
- Co-locate styles with components
```

### API Rules (Scoped)

```markdown
---
paths:
  - src/api/**/*
  - src/routes/**/*
---

# API Conventions

- Use RESTful naming
- Validate request bodies with Zod
- Return consistent error shapes
- Log all 5xx errors
```

### Global Rules (Unscoped)

```markdown
# Project Standards

These rules apply to all files.

**Code Quality**
- No `any` types
- No `console.log` in production code
- Maximum 300 lines per file

**Git**
- Conventional commits
- Meaningful commit messages
```

---

## Related

- [Memory Hierarchy](./memory-hierarchy.md) - Overall memory system
- [Best Practices](./best-practices.md) - Writing effective rules
