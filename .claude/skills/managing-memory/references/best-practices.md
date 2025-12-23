# Memory and Rules Best Practices

Guidelines for writing effective memory files and rules that maximize Claude Code's understanding and consistency.

---

## Writing Rules

### Be Specific

Vague instructions lead to inconsistent behavior. Provide concrete, actionable guidance.

| Avoid | Prefer |
|-------|--------|
| "Format code properly" | "Use 2-space indentation, no trailing semicolons" |
| "Write good tests" | "Each test file must have at least one test per public function" |
| "Handle errors" | "Throw errors early; never use silent fallbacks" |
| "Use TypeScript" | "Use TypeScript strict mode; never use `any` type" |

### Use Bullet Points

Structure improves parsing and application:

```markdown
**Error Handling**
- Throw errors at boundaries, not deep in call stack
- Include context in error messages
- Log errors with structured metadata
- Never swallow exceptions silently
```

### Group Under Headings

Organize related instructions for easier reference:

```markdown
**Code Style**
- 2-space indentation
- Single quotes for strings
- No trailing commas

**Naming**
- camelCase for variables and functions
- PascalCase for classes and types
- SCREAMING_SNAKE for constants

**Imports**
- Group by: built-in, external, internal
- Sort alphabetically within groups
```

### Review and Update

Memory files are living documents:

- Review after major project changes
- Remove outdated instructions
- Add lessons learned from code reviews
- Update when dependencies change

### One Topic Per Rule File

Keep rule files focused:

```
.claude/rules/
├── testing.md          # Testing conventions only
├── security.md         # Security rules only
├── api-design.md       # API conventions only
└── database.md         # Database patterns only
```

Not:
```
.claude/rules/
└── everything.md       # All rules in one file (hard to maintain)
```

---

## Organization

### Keep Rules Focused

Each file should address a single domain:

**Good**: `testing.md` contains only testing rules
**Bad**: `testing.md` also has deployment instructions

### Use Descriptive Filenames

Filename should indicate content:

| Good | Bad |
|------|-----|
| `typescript-conventions.md` | `rules1.md` |
| `api-error-handling.md` | `misc.md` |
| `component-patterns.md` | `stuff.md` |

### Use Path Scoping Sparingly

Only scope when rules are truly file-specific:

**Appropriate scoping**:
- Test files need different rules than production code
- Frontend and backend have different conventions
- Config files have unique formatting requirements

**Avoid over-scoping**:
- Don't scope general style rules to every file type
- Don't create separate rules for each directory if they share conventions

### Organize with Subdirectories

For large projects, use subdirectories:

```
.claude/rules/
├── global/
│   ├── code-style.md
│   └── security.md
├── frontend/
│   ├── react.md
│   └── styling.md
└── backend/
    ├── api.md
    └── database.md
```

---

## @Import Syntax

Import shared content from other files to avoid duplication.

### Syntax

```markdown
@path/to/file.md
```

### Path Resolution

- **Relative paths**: Resolved from current file location
- **Absolute paths**: Resolved from project root

### Examples

```markdown
# Import shared standards
@../shared/code-style.md

# Import from project root
@/docs/api-standards.md

# Import sibling file
@./common-patterns.md
```

### Constraints

| Constraint | Value |
|------------|-------|
| Maximum depth | 5 hops (prevents infinite loops) |
| Inside code blocks | Not evaluated (literal text) |
| Non-existent files | Warning, continues processing |

### Warning: Context Size

Imports add to context size. Consider:

- Total imported content size
- Whether content is always needed
- If selective loading would be better

### When to Use Imports

**Good use cases**:
- Shared code style across multiple rule files
- Common security checklist included in relevant rules
- Standard header/footer for all rules

**Avoid**:
- Splitting small files unnecessarily
- Importing entire documentation files
- Creating deep import chains

---

## Common Patterns

### Commands Section

Document build, test, and lint commands:

```markdown
**Commands**
- `bun test` - Run test suite
- `bun run build` - Build for production
- `bun run dev` - Start development server
- `bun run lint` - Run linter
- `bun typecheck` - TypeScript type checking
```

### Code Style

Project-specific conventions:

```markdown
**TypeScript**
- Strict mode enabled
- No `any` type - look up actual types
- Prefer `interface` for objects, `type` for unions
- Export types from dedicated `types.ts` files

**Formatting**
- 2-space indentation
- 100-character line limit
- Single quotes for strings
- Trailing commas in multiline
```

### Architecture

Key patterns and file organization:

```markdown
**File Organization**
- Feature-based folder structure
- Co-locate tests with source files
- Shared utilities in `lib/`
- Types in `types/` or co-located

**Patterns**
- Repository pattern for data access
- Service layer for business logic
- DTOs for API boundaries
- Dependency injection via constructors
```

### Testing

Test naming, structure, and approaches:

```markdown
**Testing Strategy**
- Integration tests for business logic
- Unit tests for pure utilities
- E2E tests for critical user flows

**Test Structure**
- Arrange-Act-Assert pattern
- Descriptive test names: "should X when Y"
- One concept per test
- Setup in beforeEach, teardown in afterEach

**Mocking**
- Mock external services
- Never mock the thing under test
- Use factories for test data
```

---

## Anti-Patterns to Avoid

### Contradictory Instructions

Avoid conflicting rules across files:

```markdown
# In code-style.md
- Use semicolons

# In typescript.md
- No semicolons
```

Resolution: Consolidate style rules in one file.

### Overly Long Rule Files

Keep individual files under 500 lines:

- Split by subtopic if too long
- Use imports for shared content
- Move detailed references to `references/` directory

### Duplicate Information

Don't repeat the same instruction in multiple places:

- Use imports for shared content
- Reference other files instead of copying
- Maintain single source of truth

### Vague Triggers

Don't write rules that are hard to apply:

```markdown
# Bad
- Write clean code
- Follow best practices
- Be consistent

# Good
- Functions must not exceed 50 lines
- Extract repeated code into shared utilities
- Match existing naming patterns in the file
```

---

## Memory File Checklist

### Before Committing

- [ ] Instructions are specific and actionable
- [ ] No contradictions with other memory files
- [ ] Commands are accurate and tested
- [ ] Path scoping is appropriate (not over-scoped)
- [ ] File is focused on one topic
- [ ] No sensitive information (secrets, credentials)

### Periodic Review

- [ ] Remove outdated instructions
- [ ] Update for dependency changes
- [ ] Add lessons from recent code reviews
- [ ] Verify commands still work
- [ ] Check for duplicated content

---

## Related

- [Memory Hierarchy](./memory-hierarchy.md) - Memory file types and locations
- [Rules Syntax](./rules-syntax.md) - Path scoping and frontmatter
