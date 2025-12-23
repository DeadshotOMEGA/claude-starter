#!/usr/bin/env python3
"""
Todo provider - shows todo list progress.
"""

import json
from pathlib import Path
from typing import Optional


def render(project_dir: str) -> Optional[str]:
    """
    Render todo progress segment.

    Returns:
        Formatted string or None if no todos
    """
    state_path = Path(project_dir) / '.claude' / 'statusline' / 'state' / 'todo.json'

    if not state_path.exists():
        return None

    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    total = state.get('total', 0)
    if total == 0:
        return None

    completed = state.get('completed', 0)
    in_progress = state.get('in_progress')

    # Show progress bar or fraction
    segment = f"📋 {completed}/{total}"

    if in_progress:
        # Truncate long task names
        task = in_progress[:20] + "..." if len(in_progress) > 23 else in_progress
        segment += f" ({task})"

    return segment
