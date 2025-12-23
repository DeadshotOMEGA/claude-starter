---
name: writing-hooks
description: Configure Claude Code hooks in settings.json for event-driven automation. Use when setting up or modifying lifecycle hooks.
---

# Hooks Writing

Configure event handlers that run shell commands at specific lifecycle points.

## Contents

- [Location](#location)
- [Hook Events](#hook-events)
- [Structure](#structure)
- [Environment Variables](#environment-variables)
- [Script Requirements](#script-requirements)
- [Matchers](#matchers)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Location

Hooks are configured in `settings.json` under the `hooks` key:

- Project: `.claude/settings.json`
- User: `~/.claude/settings.json`

## Hook Events

| Event | When Triggered | Common Use Cases |
|-------|----------------|------------------|
| `SessionStart` | Claude session begins | Load context, setup environment |
| `SessionEnd` | Claude session ends | Cleanup, save state, persist data |
| `UserPromptSubmit` | User sends a message | Intercept/transform input, add context |
| `PreToolUse` | Before a tool executes | Validate, modify, or block tool calls |
| `PostToolUse` | After a tool executes | Log, notify, post-process results |
| `SubagentStop` | Subagent completes | Notifications, cleanup |
| `Stop` | Claude stops responding | Sound alerts, notifications |
| `Notification` | Claude sends notification | Sound alerts, external integrations |

## Structure

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "path/to/script.sh"
          }
        ]
      }
    ]
  }
}
```

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `EventName` | Yes | One of the hook events above |
| `matcher` | No | Filter by tool name (for PreToolUse/PostToolUse) |
| `type` | Yes | Always `"command"` currently |
| `command` | Yes | Shell command or script path |

## Environment Variables

Hooks receive context via environment variables:

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Project root directory |
| `$CLAUDE_SESSION_ID` | Current session identifier |

Additional variables depend on the event type and are passed as JSON to stdin.

## Script Requirements

### Executable
Scripts must be executable:
```bash
chmod +x .claude/hooks/my-script.sh
```

### Exit Codes
- `0` — Success, continue normally
- Non-zero — For `PreToolUse`, blocks the operation

### Output
- stdout → Sent back to Claude as feedback
- stderr → Logged for debugging

### Performance
Keep hooks fast (< 1 second). Long-running hooks block Claude.

## Matchers

Use `matcher` to filter which tools trigger the hook:

```json
{
  "PreToolUse": [
    {
      "matcher": "Task",
      "hooks": [{ "type": "command", "command": "..." }]
    },
    {
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": "..." }]
    }
  ]
}
```

Omit `matcher` to trigger for all tools.

## Best Practices

### Use Project-Relative Paths
```json
"command": "$CLAUDE_PROJECT_DIR/.claude/hooks/my-hook.sh"
```

### Handle Errors Gracefully
Scripts should handle errors and provide useful feedback:
```bash
#!/bin/bash
if ! do_something; then
    echo "Hook failed: reason" >&2
    exit 0  # Don't block Claude unless intentional
fi
```

### Log for Debugging
Write to a log file for troubleshooting:
```bash
echo "[$(date)] Hook triggered" >> .claude/hooks/debug.log
```

### Test Manually First
Run scripts directly before relying on hooks:
```bash
CLAUDE_PROJECT_DIR="$(pwd)" .claude/hooks/my-hook.sh
```

### Avoid Blocking Operations
Don't block Claude with slow hooks. Use background processes if needed:
```bash
my_slow_command &
```

## Examples

### Notification on Stop
Play a sound when Claude finishes:

```json
{
  "Stop": [{
    "hooks": [{
      "type": "command",
      "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notifications/sound.sh"
    }]
  }]
}
```

### Intercept Agent Spawning
Log or validate subagent creation:

```json
{
  "PreToolUse": [{
    "matcher": "Task",
    "hooks": [{
      "type": "command",
      "command": ".claude/hooks/pre-tool-use/agent-interceptor.js"
    }]
  }]
}
```

### Session Lifecycle
Initialize and cleanup context:

```json
{
  "SessionStart": [{
    "hooks": [{
      "type": "command",
      "command": ".claude/hooks/lifecycle/session-init.sh"
    }]
  }],
  "SessionEnd": [{
    "hooks": [{
      "type": "command",
      "command": ".claude/hooks/lifecycle/session-cleanup.sh"
    }]
  }]
}
```

### Add Context to User Prompts
Inject additional context before Claude processes:

```json
{
  "UserPromptSubmit": [{
    "hooks": [{
      "type": "command",
      "command": ".claude/hooks/user-prompt-submit/add-context.sh"
    }]
  }]
}
```

## References

See `references/hook-events.md` for detailed event payloads.
