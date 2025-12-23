#!/usr/bin/env python3
"""
Todo Tracker Hook

Tracks TodoWrite tool usage for statusline display.
Use with PostToolUse (TodoWrite matcher) hook.

Reads hook input from stdin and updates todo.json state.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_state_path() -> Path:
    """Get the todo state file path."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    return Path(project_dir) / '.claude' / 'statusline' / 'state' / 'todo.json'


def save_state(state: dict):
    """Save todo state."""
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

    # Extract todo data from tool input
    tool_input = input_data.get('tool_input', {})
    todos = tool_input.get('todos', [])

    if not todos:
        # No todos, might be from tool_result
        tool_result = input_data.get('tool_result', {})
        if isinstance(tool_result, dict):
            todos = tool_result.get('todos', [])

    if not todos:
        sys.exit(0)

    # Calculate stats
    total = len(todos)
    completed = sum(1 for t in todos if t.get('status') == 'completed')

    # Find current in-progress task
    in_progress = None
    for t in todos:
        if t.get('status') == 'in_progress':
            in_progress = t.get('activeForm') or t.get('content', '')[:30]
            break

    state = {
        'completed': completed,
        'total': total,
        'in_progress': in_progress,
        'last_updated': datetime.now().isoformat()
    }
    save_state(state)

    # Always succeed
    sys.exit(0)


if __name__ == '__main__':
    main()
