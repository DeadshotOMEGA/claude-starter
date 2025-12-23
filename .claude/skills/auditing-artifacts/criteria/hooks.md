# Hook Audit Criteria

Scoring criteria for hook configurations in `settings.json` and hook scripts based on official hooks documentation: @docs/hooks.md

## Structure (5 points)

### Hook Configuration Completeness (3 points)
- **3 pts:** All required fields present and valid
  - Required: event name, `type: "command"`, `command` path
  - Optional: `matcher` (for PreToolUse/PostToolUse)
- **2 pts:** Required fields present, missing useful matcher
- **1 pt:** Required fields with formatting issues
- **0 pts:** Missing required fields or invalid JSON

### Organization (1 point)
- **1 pt:** Hooks logically organized by event type
- **0 pts:** Disorganized hook configuration

### Script File Structure (1 point)
- **1 pt:** Hook scripts in `.claude/hooks/` directory, organized by event
- **0 pts:** Scripts in random locations or root directory

**Common Issues:**
- Missing `type` field
- Invalid event name
- Command path not executable
- No matcher when filtering would be useful

## Clarity (4 points)

### Event Selection (1 point)
- **1 pt:** Appropriate event for the hook's purpose
- **0 pts:** Wrong event or unclear why event chosen

### Matcher Usage (1 point)
- **1 pt:** Uses matcher to filter tools when appropriate (PreToolUse/PostToolUse)
- **0 pts:** No matcher when filtering would prevent unnecessary execution

### Documentation (1 point)
- **1 pt:** Hook purpose documented (comment in settings.json or script header)
- **0 pts:** No documentation of what hook does

### Script Clarity (1 point)
- **1 pt:** Script has clear purpose, logging, and error messages
- **0 pts:** Opaque script with no feedback

**Event Types:**

| Event | Use Case |
|-------|----------|
| `SessionStart` | Load context, setup environment |
| `SessionEnd` | Cleanup, save state, persist data |
| `UserPromptSubmit` | Intercept/transform input, add context |
| `PreToolUse` | Validate, modify, or block tool calls |
| `PostToolUse` | Log, notify, post-process results |
| `SubagentStop` | Notifications, cleanup after agent |
| `Stop` | Sound alerts, notifications when Claude stops |
| `Notification` | Sound alerts, external integrations |

## Technical (5 points)

### Script Executable (1 point)
- **1 pt:** Script has execute permissions (`chmod +x`)
- **0 pts:** Script not executable

### Exit Codes (2 points)
- **2 pts:** Proper exit codes (0 for success, non-zero to block for PreToolUse)
- **1 pt:** Has exit codes but not used correctly
- **0 pts:** No proper exit code handling

### Environment Variables (1 point)
- **1 pt:** Uses `$CLAUDE_PROJECT_DIR` and other env vars correctly
- **0 pts:** Hardcodes paths instead of using env vars

### Performance (1 point)
- **1 pt:** Hook completes quickly (<1 second) or runs in background
- **0 pts:** Blocking operation that slows Claude

**Script Requirements:**

**Executable:**
```bash
chmod +x .claude/hooks/my-hook.sh
```

**Exit Codes:**
- `0` - Success, continue normally
- Non-zero - For PreToolUse, blocks the operation

**Environment Variables:**
- `$CLAUDE_PROJECT_DIR` - Project root
- `$CLAUDE_SESSION_ID` - Session identifier

## Operational (4 points)

### Error Handling (2 points)
- **2 pts:** Script handles errors gracefully with useful feedback
- **1 pt:** Some error handling but incomplete
- **0 pts:** No error handling, script fails silently

### Output Streams (1 point)
- **1 pt:** Uses stdout for feedback to Claude, stderr for logging
- **0 pts:** No output or wrong streams used

### Path Safety (1 point)
- **1 pt:** Uses project-relative paths with `$CLAUDE_PROJECT_DIR`
- **0 pts:** Hardcoded or absolute paths

**Error Handling Example:**

**Good:**
```bash
#!/bin/bash
if ! do_something; then
    echo "Hook failed: reason" >&2
    exit 0  # Don't block Claude unless intentional
fi
```

**Bad:**
```bash
#!/bin/bash
do_something  # Just fails silently
```

## Maintainability (2 points)

### Logging (1 point)
- **1 pt:** Logs execution to debug file for troubleshooting
- **0 pts:** No logging, hard to debug

### Testing (1 point)
- **1 pt:** Hook can be tested manually before deployment
- **0 pts:** No way to test hook in isolation

**Logging Example:**
```bash
echo "[$(date)] Hook triggered: $HOOK_EVENT" >> .claude/hooks/debug.log
```

**Testing:**
```bash
CLAUDE_PROJECT_DIR="$(pwd)" .claude/hooks/my-hook.sh
```

## Red Flags (Automatic Deductions)

- **-2 pts:** Script not executable
- **-2 pts:** Hook blocks Claude for >1 second (not async)
- **-1 pt:** No error handling
- **-1 pt:** Hardcoded paths instead of `$CLAUDE_PROJECT_DIR`
- **-1 pt:** No documentation of what hook does
- **-1 pt:** Wrong exit code usage
- **-1 pt:** No logging for debugging

## Excellent Hook Checklist

An 18-20 point hook has:

- ✅ Valid event type for purpose
- ✅ Complete hook configuration (type, command)
- ✅ Matcher for PreToolUse/PostToolUse when appropriate
- ✅ Script in `.claude/hooks/` directory
- ✅ Execute permissions on script (`chmod +x`)
- ✅ Proper exit codes (0 for success, non-zero to block)
- ✅ Uses `$CLAUDE_PROJECT_DIR` for paths
- ✅ Fast execution (<1 second) or runs in background
- ✅ Error handling with useful feedback
- ✅ stdout for feedback to Claude, stderr for errors
- ✅ Logging to debug file
- ✅ Can be tested manually
- ✅ Documented purpose (comment or script header)
- ✅ No hardcoded values

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| Script not executable | Run `chmod +x .claude/hooks/script.sh` |
| Blocking operation | Add `&` to run in background or make faster |
| Hardcoded paths | Replace with `$CLAUDE_PROJECT_DIR/path` |
| No error handling | Add try/catch or if/else with error messages |
| No logging | Add `echo "[$(date)] ..." >> .claude/hooks/debug.log` |
| Wrong exit code | Use `exit 0` for success, `exit 1` to block |
| No matcher | Add `"matcher": "ToolName"` to filter when appropriate |
| No documentation | Add comment in settings.json or script header |
| stdout/stderr misuse | Send feedback to stdout, errors to stderr |
| Can't test | Export env vars and run script manually |

## Hook Configuration Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use/validate-agent.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/notifications/sound.sh"
          }
        ]
      }
    ]
  }
}
```

## Script Template

```bash
#!/bin/bash
set -euo pipefail

# Hook: [Purpose of this hook]
# Event: [Event type]
# Usage: Triggered automatically on [event]

# Log execution
echo "[$(date)] Hook triggered" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/debug.log"

# Read input from stdin if needed
input=$(cat)

# Do work
if ! perform_action; then
    echo "Hook failed: reason" >&2
    exit 0  # Change to exit 1 to block operation
fi

# Output feedback to Claude (stdout)
echo "Hook completed successfully"
exit 0
```
