#!/usr/bin/env python3
"""
Status Line State Updater

Hook-callable script to update statusline state files.

Usage:
  update.py agents add <agent_name>     # Add running agent
  update.py agents remove <agent_name>  # Remove agent
  update.py agents clear                # Clear all agents
  update.py todo <completed> <total> [current_task]  # Update todo state
  update.py session start               # Mark session started
  update.py session prompt              # Increment prompt count

Reads CLAUDE_PROJECT_DIR from environment.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_state_dir() -> Path:
    """Get the state directory path."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    return Path(project_dir) / '.claude' / 'statusline' / 'state'


def load_state(filename: str) -> dict:
    """Load state from JSON file."""
    state_path = get_state_dir() / filename
    if state_path.exists():
        try:
            with open(state_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_state(filename: str, state: dict):
    """Save state to JSON file."""
    state_path = get_state_dir() / filename
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def update_agents(action: str, agent_name: str = None):
    """Update agents state."""
    state = load_state('agents.json')
    running = state.get('running', [])

    if action == 'add' and agent_name:
        if agent_name not in running:
            running.append(agent_name)
    elif action == 'remove' and agent_name:
        running = [a for a in running if a != agent_name]
    elif action == 'clear':
        running = []

    state['running'] = running
    state['last_updated'] = datetime.now().isoformat()
    save_state('agents.json', state)


def update_todo(completed: int, total: int, current_task: str = None):
    """Update todo state."""
    state = {
        'completed': completed,
        'total': total,
        'in_progress': current_task,
        'last_updated': datetime.now().isoformat()
    }
    save_state('todo.json', state)


def update_session(action: str):
    """Update session state."""
    state = load_state('session.json')

    if action == 'start':
        state['started_at'] = datetime.now().isoformat()
        state['prompt_count'] = 0
    elif action == 'prompt':
        state['prompt_count'] = state.get('prompt_count', 0) + 1

    state['last_updated'] = datetime.now().isoformat()
    save_state('session.json', state)


def main():
    if len(sys.argv) < 2:
        print("Usage: update.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'agents':
        if len(sys.argv) < 3:
            print("Usage: update.py agents <add|remove|clear> [agent_name]", file=sys.stderr)
            sys.exit(1)
        action = sys.argv[2]
        agent_name = sys.argv[3] if len(sys.argv) > 3 else None
        update_agents(action, agent_name)

    elif command == 'todo':
        if len(sys.argv) < 4:
            print("Usage: update.py todo <completed> <total> [current_task]", file=sys.stderr)
            sys.exit(1)
        completed = int(sys.argv[2])
        total = int(sys.argv[3])
        current_task = sys.argv[4] if len(sys.argv) > 4 else None
        update_todo(completed, total, current_task)

    elif command == 'session':
        if len(sys.argv) < 3:
            print("Usage: update.py session <start|prompt>", file=sys.stderr)
            sys.exit(1)
        action = sys.argv[2]
        update_session(action)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
