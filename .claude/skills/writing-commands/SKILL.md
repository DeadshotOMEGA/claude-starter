---
name: writing-commands
description: Write slash command definitions for .claude/commands/. Use when creating or updating custom slash commands.
---

# Command Writing

Create slash commands that users invoke with `/command-name`.

## Contents

- [File Locations](#file-locations)
- [Frontmatter](#frontmatter)
- [Content Structure](#content-structure)
- [Naming Conventions](#naming-conventions)
- [Using Arguments](#using-arguments)
- [Referencing Files](#referencing-files)
- [Best Practices](#best-practices)
- [Template](#template)

## File Locations

| Location | Scope |
|----------|-------|
| `.claude/commands/*.md` | Project commands (shared via git) |
| `~/.claude/commands/*.md` | Personal commands (available everywhere) |

## Frontmatter

```yaml
---
description: Short description shown in /help
argument-hint: <required-arg> [optional-arg]
allowed-tools: Read, Grep, Glob, Bash
model: claude-3-5-haiku-20241022
disable-model-invocation: false
---
```

| Field | Required | Purpose |
|-------|----------|---------|
| `description` | Yes | Shows in `/help` listing |
| `argument-hint` | No | Placeholder shown after command name |
| `allowed-tools` | No | List of tools command can use (restricts tool access) |
| `model` | No | Specific model string (e.g., `claude-3-5-haiku-20241022`) |
| `disable-model-invocation` | No | Prevents SlashCommand tool from calling this command |

## Content Structure

The markdown body is the prompt Claude receives when the user runs the command.

```markdown
---
description: Create a new component with tests
argument-hint: <ComponentName>
---

Create a new React component named $ARGUMENTS:

1. Create component file in src/components/
2. Create test file in src/components/__tests__/
3. Add to index.ts export

Follow patterns from @src/components/Button/Button.tsx
```

## Naming Conventions

| File | Command | Display |
|------|---------|---------|
| `review.md` | `/review` | `/review (project)` |
| `fix-build.md` | `/fix-build` | `/fix-build (project)` |
| `plan/requirements.md` | `/plan:requirements` | `/plan:requirements (project:plan)` |
| `frontend/test.md` | `/test` | `/test (project:frontend)` |
| `~/.claude/commands/review.md` | `/review` | `/review (user)` |

**Rules:**
- Filename becomes command name
- Use hyphens for multi-word commands
- Subdirectories create namespaces shown in description (e.g., `(project:frontend)`)
- Commands in subdirectories can share names (distinguished by namespace in `/help`)
- Project commands override user commands with same name

## Using Arguments

### All Arguments with `$ARGUMENTS`

Use `$ARGUMENTS` placeholder to capture all user input:

```markdown
---
description: Search codebase for a term
argument-hint: <search-term>
---

Search the codebase for "$ARGUMENTS":

1. Use Grep to find all occurrences
2. Summarize the findings
3. Identify the most relevant files
```

**User invokes:** `/search authentication tokens`
**Claude receives:** `Search the codebase for "authentication tokens":...`

### Positional Arguments with `$1`, `$2`, `$3`

Access specific arguments individually using positional parameters:

```markdown
---
description: Review PR with priority and assignee
argument-hint: <pr-number> <priority> <assignee>
---

Review PR #$1 with priority $2 and assign to $3.

1. Fetch PR details: gh pr view $1
2. Focus areas based on $2 priority level
3. Tag $3 in review comments
```

**User invokes:** `/review-pr 456 high alice`
**Claude receives:** `Review PR #456 with priority high and assign to alice...`

Use positional arguments when you need to:
- Access arguments individually in different parts of your command
- Provide defaults for missing arguments
- Build structured commands with specific parameter roles

## Referencing Files

Use `@` notation to reference files Claude should read:

```markdown
Follow patterns from @src/components/Button/Button.tsx
Use the template at @.claude/file-templates/component.md
```

Claude will read these files when executing the command.

## Bash Execution

Execute bash commands before the command runs using `!` prefix. The output is included in context.

**Requirements:**
- Must include `allowed-tools` with `Bash` tool
- Can specify specific bash commands to allow

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create a single git commit.
```

**Alternative: Disable Model Invocation**

For simple bash-only commands, use `disable-model-invocation: true` to run bash without LLM:

```markdown
---
description: Run linter
disable-model-invocation: true
---

!bun run lint
```

## Thinking Mode

Commands can trigger extended thinking by including keywords:

```markdown
---
description: Complex architectural analysis
---

Think harder about the architectural implications of this change.

Provide ultrathink analysis of the design patterns used.
```

Keywords that trigger thinking:
- "think harder"
- "ultrathink"
- "extended thinking"

## SlashCommand Tool

Claude can execute commands programmatically using the `SlashCommand` tool.

**Enable automatic invocation:**
```markdown
> Run /write-unit-test when you are about to start writing tests.
```

**Supported commands:**
- User-defined custom commands only (not built-in commands)
- Must have `description` frontmatter field populated
- Can be disabled with `disable-model-invocation: true`

**Disable specific command:**
```yaml
---
description: Internal command
disable-model-invocation: true
---
```

**Disable all SlashCommand tool:**
```
/permissions
# Add to deny rules: SlashCommand
```

## Best Practices

### One Command = One Workflow
Keep commands focused on a single task or workflow.

**Good:** `/review` — Review code changes
**Bad:** `/do-everything` — Review, fix, test, and deploy

### Include Expected Output
Tell Claude what to produce:

```markdown
Output:
- Summary of changes
- List of issues found
- Suggested fixes
```

### Reference Existing Patterns
Point to examples in the codebase:

```markdown
Follow patterns from @src/components/ExistingComponent.tsx
```

### Keep Prompts Under 50 Lines
Long prompts are hard to maintain. Use Skills for complex workflows.

### Use Argument Hints Clearly
Show what input is expected:

| Good | Bad |
|------|-----|
| `<ComponentName>` | `<name>` |
| `<PR-number>` | `<num>` |
| `[--verbose]` | `[v]` |

### Restrict Tools When Appropriate
Use `allowed-tools` to limit tool access for safety:

```yaml
---
allowed-tools: Read, Grep, Glob  # Read-only
---
```

### Use Appropriate Model
Specify model when non-default would improve performance:

```yaml
---
model: claude-3-5-haiku-20241022  # Fast, simple tasks
---
```

## Skills vs Commands

**Use commands for:**
- Quick, frequently used prompts
- Simple prompt snippets you use often
- Frequently used instructions in one file
- Explicit control over when it runs (manual invocation)

**Use Skills for:**
- Complex workflows with multiple steps
- Capabilities requiring scripts or utilities
- Knowledge organized across multiple files
- Team workflows you want to standardize
- Automatic discovery (Claude decides when to use)

| Aspect | Slash Commands | Agent Skills |
|--------|----------------|--------------|
| **Complexity** | Simple prompts | Complex capabilities |
| **Structure** | Single .md file | Directory with SKILL.md + resources |
| **Discovery** | Explicit (`/command`) | Automatic (based on context) |
| **Files** | One file only | Multiple files, scripts, templates |
| **Sharing** | Via git | Via git or plugins |

**Example:**

**As command:**
```markdown
# .claude/commands/review.md
Review this code for security, performance, and style.
```
Usage: `/review` (manual)

**As Skill:**
```
.claude/skills/code-review/
├── SKILL.md (overview and workflows)
├── SECURITY.md (security checklist)
├── PERFORMANCE.md (performance patterns)
└── scripts/run-linters.sh
```
Usage: "Can you review this code?" (automatic)

## Template

```markdown
---
description: [What this command does]
argument-hint: [<required>] [[optional]]
allowed-tools: [optional: Read, Grep, Glob]
model: [optional: claude-3-5-haiku-20241022]
---

[Clear instruction for Claude]

$ARGUMENTS

[Specific steps to follow]

[Expected output format]

[Pattern references with @]
```

## Examples

### Simple Command
```markdown
---
description: Run tests and report failures
---

Run the test suite and provide a summary:

1. Execute: bun test
2. If tests pass, confirm success
3. If tests fail, analyze failures and suggest fixes
```

### Command with Arguments
```markdown
---
description: Review a specific PR
argument-hint: <PR-number>
---

Review GitHub PR #$ARGUMENTS:

1. Fetch PR details: gh pr view $ARGUMENTS
2. Get the diff: gh pr diff $ARGUMENTS
3. Review for:
   - Code quality
   - Security issues
   - Test coverage
4. Provide summary with actionable feedback
```

### Command with Positional Arguments
```markdown
---
description: Review PR with priority and assignee
argument-hint: <pr-number> <priority> <assignee>
---

Review PR #$1 with priority $2 and assign to $3:

1. Fetch PR: gh pr view $1
2. Review depth based on $2 priority
3. Tag $3 in comments
4. Provide feedback tailored to priority level
```

### Command with Bash Execution
```markdown
---
description: Create git commit
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
---

## Context

- Status: !`git status`
- Diff: !`git diff HEAD`
- Branch: !`git branch --show-current`

## Task

Create a git commit based on the changes above.
```

### Command with Tool Restrictions
```markdown
---
description: Search codebase (read-only)
allowed-tools: Read, Grep, Glob
argument-hint: <search-term>
---

Search for "$ARGUMENTS" in codebase:

1. Use Grep to find occurrences
2. Use Read to examine relevant files
3. Summarize findings
```

### Namespaced Command
File: `.claude/commands/plan/requirements.md`
Invoked: `/plan:requirements`

```markdown
---
description: Gather requirements for a new feature
argument-hint: <feature-name>
---

Gather requirements for "$ARGUMENTS":

1. Ask clarifying questions about scope
2. Identify stakeholders and users
3. Document functional requirements
4. Document technical requirements
5. Save to docs/plans/$ARGUMENTS/requirements.md

Use template: @.claude/file-templates/requirements.template.md
```
