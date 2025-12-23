**Slash Commands Directory**

Commands are Markdown files invoked via `/command-name` or `/namespace:command-name`.

## Directory Organization

| Directory | Purpose | Example Command |
|-----------|---------|-----------------|
| `git/` | Git operations, commits, hooks | `/git:git`, `/git:sync-registry` |
| `orchestration/` | Workflow orchestration, agent delegation | `/orchestration:orchestrate`, `/orchestration:workflow` |
| `development/` | Code review, testing, debugging, build fixes | `/development:review`, `/development:test` |
| `documentation/` | Doc updates, code explanation, maintenance | `/documentation:update-docs`, `/documentation:explain-code` |
| `initialization/` | Project and workspace setup | `/initialization:start`, `/initialization:init-better` |
| `investigation/` | Bug investigation, interviews | `/investigation:investigate-fix`, `/investigation:interview` |
| `utility/` | Auditing, command creation, Playwright tests | `/utility:audit`, `/utility:new-command` |

## Creating Commands

- Use `$ARGUMENTS` placeholder for user input
- Use `$1`, `$2`, `$3` for positional arguments
- Keep prompts focused on a single workflow
- Structure: context → steps → expected output format

## Required Frontmatter

```yaml
---
description: Short description shown in /help
argument-hint: <required-arg> [optional-arg]
allowed-tools: Read, Grep, Glob
model: haiku
---
```

## Conventions

- Filename becomes command name: `review.md` → `/development:review`
- Subdirectories create namespaces: `git/git.md` → `/git:git`
- Personal commands go in `~/.claude/commands/`
