#!/usr/bin/env python3
"""
Agent Tracker Hook

Tracks subagent start/stop for statusline display.
Use with PreToolUse (Task matcher) and SubagentStop hooks.

Reads hook input from stdin and updates agents.json state.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_state_path() -> Path:
    """Get the agents state file path."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    return Path(project_dir) / '.claude' / 'statusline' / 'state' / 'agents.json'


def load_state() -> dict:
    """Load current agents state."""
    state_path = get_state_path()
    if state_path.exists():
        try:
            with open(state_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {'running': [], 'last_updated': None}


def save_state(state: dict):
    """Save agents state."""
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    # Read hook input
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            input_data = json.loads(stdin_data)
        else:
            input_data = {}
    except json.JSONDecodeError:
        input_data = {}

    # Determine hook type from environment or input
    hook_event = os.environ.get('CLAUDE_HOOK_EVENT', '')

    state = load_state()
    running = state.get('running', [])

    if 'tool_input' in input_data:
        # PreToolUse - agent starting
        tool_input = input_data.get('tool_input', {})
        agent_type = tool_input.get('subagent_type', 'agent')
        description = tool_input.get('description', '')[:15]

        agent_id = f"{agent_type}"
        if description:
            agent_id = f"{agent_type}:{description}"

        if agent_id not in running:
            running.append(agent_id)

    elif hook_event == 'SubagentStop' or 'subagent' in str(input_data).lower():
        # SubagentStop - agent finished
        # Try to identify which agent stopped
        agent_id = input_data.get('agent_id', '')

        if agent_id and agent_id in running:
            running.remove(agent_id)
        elif running:
            # Remove the oldest agent if we can't identify which stopped
            running.pop(0)

    state['running'] = running
    state['last_updated'] = datetime.now().isoformat()
    save_state(state)

    # Always succeed - don't block Claude
    sys.exit(0)


if __name__ == '__main__':
    main()
