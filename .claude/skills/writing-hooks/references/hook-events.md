# Hook Events Reference

Detailed documentation for each hook event type.

## SessionStart

**When:** Claude Code session begins

**Use cases:**
- Load additional context files
- Set up environment variables
- Initialize state

**Payload:** Session metadata via stdin

## SessionEnd

**When:** Claude Code session ends

**Use cases:**
- Save session state
- Clean up temporary files
- Log session summary

**Payload:** Session metadata including duration, message count

## UserPromptSubmit

**When:** User submits a message, before Claude processes it

**Use cases:**
- Add automatic context
- Transform or filter input
- Skill activation prompts

**Payload:** User message content

**Output:** Additional context to inject (prefix to user message)

## PreToolUse

**When:** Before Claude executes a tool

**Use cases:**
- Validate tool parameters
- Block dangerous operations
- Log tool usage

**Payload:** Tool name and parameters as JSON

**Exit codes:**
- `0` with stdout — Proceed, include stdout as context
- `0` without stdout — Proceed silently
- Non-zero — Block the tool call

## PostToolUse

**When:** After a tool executes successfully

**Use cases:**
- Log tool results
- Trigger notifications
- Post-process outputs

**Payload:** Tool name, parameters, and result as JSON

## SubagentStop

**When:** A subagent completes its work

**Use cases:**
- Notification of completion
- Result processing
- Cleanup

**Payload:** Agent ID, result summary

## Stop

**When:** Claude stops responding (task complete or interrupted)

**Use cases:**
- Sound notifications
- Desktop alerts
- Logging

**Payload:** Stop reason, message count

## Notification

**When:** Claude sends a notification

**Use cases:**
- Sound alerts
- External integrations
- Desktop notifications

**Payload:** Notification content
