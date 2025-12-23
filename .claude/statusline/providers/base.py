#!/usr/bin/env python3
"""
Base provider - always-on status segments.
Shows model name, persona, git branch.
"""

import subprocess
from typing import Optional


def get_git_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def render(input_data: dict) -> dict:
    """
    Render base status segments.

    Returns:
        dict with 'prefix' and 'suffix' segments
    """
    model = input_data.get('model', {}).get('display_name', 'Claude')
    workspace = input_data.get('workspace', {})
    current_dir = workspace.get('current_dir', '.')

    # Output style (persona)
    output_style = input_data.get('output_style', {}).get('name', '')
    style_segment = f" 👤 {output_style}" if output_style and output_style != 'default' else ""

    # Git branch
    git_branch = get_git_branch()
    branch_segment = f" 🌿 {git_branch}" if git_branch else ""

    # Directory name
    from pathlib import Path
    dir_name = Path(current_dir).name or current_dir

    return {
        'prefix': f"[{model}]{style_segment}",
        'dir': dir_name,
        'branch': branch_segment,
    }
