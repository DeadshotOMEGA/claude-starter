---
name: managing-memory
description: Reference documentation for Claude Code memory hierarchy, imports, and shortcuts. For memory management workflows (audit, migrate, create rules), use the orchestrate-memory agent instead.
---

# Managing Memory Reference

Quick reference for Claude Code's memory system. For full workflows, use the `orchestrate-memory` agent.

## Use the Agent Instead

For memory management tasks, spawn the orchestrate-memory agent:

```
Task(subagent_type="orchestrate-memory", prompt="[your request]")
```

**Agent handles:**
- Auditing existing memory for conflicts/gaps
- Migrating monolithic CLAUDE.md to modular rules
- Socratic guidance for creating new rules
- Analyzing codebase for convention suggestions

This skill provides **reference material** the agent uses.

## Memory Hierarchy

**Precedence (highest to lowest):**
1. Project local (`CLAUDE.local.md`)
2. Project rules (`.claude/rules/*.md`)
3. Project memory (`.claude/CLAUDE.md`)
4. User rules (`~/.claude/rules/*.md`)
5. User memory (`~/.claude/CLAUDE.md`)
6. Enterprise policy (system-level)

See [references/memory-hierarchy.md](references/memory-hierarchy.md) for complete documentation.

## Import Syntax

CLAUDE.md files can import other files:

```markdown
See @README for project overview and @package.json for commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal: @~/.claude/my-project-instructions.md
```

**Rules:**
- Relative and absolute paths allowed
- Home directory (`~`) expansion supported
- Max depth: 5 recursive hops
- Not evaluated inside code blocks

## Quick Shortcuts

| Shortcut | Action |
|----------|--------|
| `# instruction` | Add memory (prompts for location) |
| `/memory` | Edit memory files in editor |
| `/memory` | View loaded memory sources |

## Validation Scripts

```bash
# Audit all memory sources
python3 scripts/audit.py

# Validate specific file
python3 scripts/validate.py [path]

# Assist migration
python3 scripts/migrate.py
```

## References

- [references/memory-hierarchy.md](references/memory-hierarchy.md) — Loading order, precedence, conflict resolution
- [references/rules-syntax.md](references/rules-syntax.md) — Rule file frontmatter and patterns
- [references/best-practices.md](references/best-practices.md) — Memory organization patterns

## Templates

- `templates/rule.md` — Basic rule template
- `templates/code-style.md` — Code style rule template
- `templates/workflow.md` — Workflow rule template

## Related

| Task | Use |
|------|-----|
| Memory workflows | `orchestrate-memory` agent |
| Write CLAUDE.md | `writing-claudemd` skill |
| Write rules | `writing-rules` skill |
