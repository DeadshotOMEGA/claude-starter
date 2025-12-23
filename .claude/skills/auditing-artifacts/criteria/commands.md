# Command Audit Criteria

Scoring criteria for `.claude/commands/*.md` files based on official slash-commands documentation.

## Structure (5 points)

### Frontmatter Completeness (3 points)
- **3 pts:** All required + relevant optional fields present and valid
  - Required: `description`
  - Optional (when applicable): `argument-hint`, `allowed-tools`, `model`, `disable-model-invocation`
- **2 pts:** Required fields present, missing useful optional fields
- **1 pt:** Required fields present but poorly formatted
- **0 pts:** Missing required frontmatter or invalid YAML

### Content Organization (2 points)
- **2 pts:** Logical flow, clear sections, well-structured
- **1 pt:** Readable but could be better organized
- **0 pts:** Confusing structure or disorganized

**Common Issues:**
- Missing `argument-hint` when command takes arguments
- Missing `allowed-tools` when command should restrict tool access
- Invalid YAML syntax (tabs instead of spaces, unquoted special characters)
- Frontmatter not enclosed in `---` delimiters

## Clarity (4 points)

### Purpose Statement (1 point)
- **1 pt:** `description` field clearly states what command does
- **0 pts:** Vague or unclear description

### Usage Examples (1 point)
- **1 pt:** Shows example invocation with $ARGUMENTS placeholder
- **0 pts:** No usage examples

### Edge Cases (1 point)
- **1 pt:** Handles error cases or explains constraints
- **0 pts:** No error handling or edge case documentation

### Output Format (1 point)
- **1 pt:** Clearly states what Claude should produce
- **0 pts:** Unclear what output to expect

**Good Description Examples:**
- "Review GitHub PR with code quality, security, and test coverage analysis"
- "Search codebase for a term and summarize findings with relevant file locations"

**Bad Description Examples:**
- "Does PR review"
- "Search stuff"

## Technical (5 points)

### Argument Handling (2 points)
- **2 pts:** Proper use of `$ARGUMENTS` or positional args ($1, $2, $3); clear `argument-hint`
- **1 pt:** Uses arguments but hint is unclear or missing
- **0 pts:** Takes arguments but doesn't document or handle them

### Tool/Permissions (1 point)
- **1 pt:** Appropriate use of `allowed-tools` if command has limited scope
- **0 pts:** Should restrict tools but doesn't, or restricts inappropriately

### Model Configuration (1 point)
- **1 pt:** Uses `model` field when specific model needed (haiku for speed, opus for reasoning)
- **0 pts:** Missing `model` when non-default would improve performance

### Bash Execution (1 point)
- **1 pt:** Uses `!` prefix for direct bash when appropriate, or uses `disable-model-invocation: true` correctly
- **0 pts:** Doesn't use direct bash when it should

**Technical Patterns:**

**Positional Arguments:**
```markdown
Run tests for $1 component in $2 environment
```

**Direct Bash (`disable-model-invocation: true`):**
```markdown
---
description: Run linter
disable-model-invocation: true
---

!bun run lint
```

**Tool Restriction:**
```markdown
---
description: Search codebase (read-only)
allowed-tools: Grep, Glob, Read
---
```

## Operational (4 points)

### Delegation Strategy (2 points)
- **2 pts:** Delegates complex workflows to agents/skills appropriately
- **1 pt:** Could delegate but doesn't
- **0 pts:** Should definitely delegate but handles everything inline

### File References (1 point)
- **1 pt:** Uses `@path/to/file` notation for pattern references
- **0 pts:** Missing file references when patterns should be followed

### Error Handling (1 point)
- **1 pt:** Instructs Claude on error scenarios (tests fail, file not found, etc.)
- **0 pts:** No error handling guidance

**Delegation Best Practices:**
- Commands < 50 lines: OK to handle inline
- Commands > 50 lines or complex multi-step: Delegate to skill or agent
- Research tasks: Delegate to codebase-explorer or research agents

## Maintainability (2 points)

### No Hardcoded Values (1 point)
- **1 pt:** No hardcoded paths, file names, or magic numbers
- **0 pts:** Contains hardcoded values that will break

### Dependencies Documented (1 point)
- **1 pt:** External commands or tools documented (gh, bun, etc.)
- **0 pts:** Uses external tools without mentioning them

**Anti-Patterns:**
- Hardcoded file paths: `src/components/Button.tsx` (use arguments or glob)
- Hardcoded PR numbers: `gh pr view 123` (use $ARGUMENTS)
- Undocumented dependencies: Uses `gh` without mentioning GitHub CLI required

## Red Flags (Automatic Deductions)

- **-2 pts:** Command > 100 lines (should be a skill)
- **-1 pt:** No `argument-hint` when command clearly takes arguments
- **-1 pt:** Description doesn't match content
- **-1 pt:** Contains XML/HTML tags in description

## Excellent Command Checklist

An 18-20 point command has:

- ✅ Complete frontmatter with relevant optional fields
- ✅ Clear, descriptive `description` field
- ✅ Proper `argument-hint` if command takes input
- ✅ `allowed-tools` if command has limited scope
- ✅ `model` field if specific model improves performance
- ✅ Clear usage example with $ARGUMENTS
- ✅ Structured prompt (numbered steps or clear sections)
- ✅ Expected output format documented
- ✅ Error handling instructions
- ✅ File references using `@` notation for patterns
- ✅ Delegates complex work to agents/skills
- ✅ No hardcoded values
- ✅ < 50 lines (or delegates to skill if longer)
- ✅ Dependencies documented if using external tools

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| No argument hint | Add `argument-hint: <required-arg> [optional-arg]` |
| Missing expected output | Add "Output:" section describing deliverables |
| Too long (>50 lines) | Delegate to skill or agent |
| Uses arguments but no hint | Add `argument-hint` field to frontmatter |
| Should restrict tools | Add `allowed-tools: Read, Grep, Glob` (for read-only) |
| Could use faster model | Add `model: haiku` for simple tasks |
| No file references | Add `@path/to/example` for pattern following |
| No error handling | Add instructions for failure scenarios |
| Hardcoded paths | Use $ARGUMENTS or glob patterns instead |
