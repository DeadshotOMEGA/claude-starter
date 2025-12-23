---
paths: "**/.claude/settings.json, **/.claude/**/settings.json"
---

# Hooks Configuration

When configuring hooks in `settings.json`:

- **Always use `$CLAUDE_PROJECT_DIR` prefix** for hook command paths
- Never use relative paths like `.claude/hooks/...`
- The variable ensures hooks work regardless of current working directory

## Correct Format

```json
{
  "type": "command",
  "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/lifecycle/my-hook.mjs"
}
```

## Incorrect Format

```json
{
  "type": "command",
  "command": ".claude/hooks/lifecycle/my-hook.mjs"
}
```

## Why This Matters

Relative paths fail when Claude's working directory differs from the project root, causing "not found" errors like:
```
/bin/sh: 1: .claude/hooks/lifecycle/my-hook.mjs: not found
```
