#!/usr/bin/env python3
"""
Agents provider - shows running subagents.
"""

import json
from pathlib import Path
from typing import Optional


def render(project_dir: str) -> Optional[str]:
    """
    Render running agents segment.

    Returns:
        Formatted string or None if no agents running
    """
    state_path = Path(project_dir) / '.claude' / 'statusline' / 'state' / 'agents.json'

    if not state_path.exists():
        return None

    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    running = state.get('running', [])
    if not running:
        return None

    first_agent = running[0]
    segment = f"⚡{first_agent}"

    if len(running) > 1:
        segment += f"+{len(running) - 1}"

    return segment
