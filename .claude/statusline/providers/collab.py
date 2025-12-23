#!/usr/bin/env python3
"""
Collaborative mode provider - shows session progress when active.
"""

import json
from pathlib import Path
from typing import Optional


# ANSI color codes
COLORS = {
    'HIGH': '\033[31m',      # Red
    'MODERATE': '\033[33m',  # Yellow
    'LOW': '\033[32m',       # Green
    'reset': '\033[0m'
}

PHASE_ICONS = {
    'understanding': '🎯',
    'exploration': '🔍',
    'design': '✏️',
    'review': '🔄',
    'exit': '🚀',
    'completed': '✅'
}


def render(project_dir: str) -> Optional[str]:
    """
    Render collaborative mode segment if active.

    Returns:
        Formatted string or None if not in collab mode
    """
    # Check both locations for backwards compatibility
    state_paths = [
        Path(project_dir) / '.claude' / 'statusline' / 'state' / 'collab.json',
        Path(project_dir) / '.claude' / 'collaborative-state.json',
    ]

    state = None
    for state_path in state_paths:
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    state = json.load(f)
                if state.get('active', False):
                    break
                state = None
            except (json.JSONDecodeError, IOError):
                continue

    if not state or not state.get('active', False):
        return None

    # Extract session info
    project = state.get('project', 'unknown')
    phase = state.get('phase', 'starting')
    category = state.get('category', '')
    risk = state.get('risk_level', '—')

    # Calculate progress
    progress = state.get('progress', {})
    done = sum(p.get('completed', 0) for p in progress.values())
    total = sum(p.get('total', 0) for p in progress.values()) or 32

    # Format components
    phase_icon = PHASE_ICONS.get(phase, '📋')

    risk_color = COLORS.get(risk, '')
    reset = COLORS['reset']
    risk_display = f"{risk_color}{risk}{reset}" if risk_color else risk

    category_display = f":{category}" if category else ""

    return f"🤝 {project} {phase_icon} {phase}{category_display} [{done}/{total}] {risk_display}"
