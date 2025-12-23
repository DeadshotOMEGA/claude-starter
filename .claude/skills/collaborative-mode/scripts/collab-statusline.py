#!/usr/bin/env python3
"""
Collaborative Mode Status Line

Displays session progress when in collaborative mode.
Falls back to default status line otherwise.

Usage: Configure in .claude/settings.json:
  {
    "statusLine": {
      "type": "command",
      "command": "$CLAUDE_PROJECT_DIR/.claude/skills/collaborative-mode/scripts/collab-statusline.py"
    }
  }
"""

import json
import sys
import subprocess
from pathlib import Path


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


def main():
    # Read JSON input from Claude Code
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    # Extract base info
    model = input_data.get('model', {}).get('display_name', 'Claude')
    workspace = input_data.get('workspace', {})
    current_dir = workspace.get('current_dir', '.')
    project_dir = workspace.get('project_dir', '.')

    # Get output style (persona)
    output_style = input_data.get('output_style', {}).get('name', '')
    style_display = f" 👤 {output_style}" if output_style and output_style != 'default' else ""

    # Look for collaborative state file
    state_file = Path(project_dir) / '.claude' / 'collaborative-state.json'

    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)

            if state.get('active', False):
                # Extract collaborative session info
                project = state.get('project', 'unknown')
                phase = state.get('phase', 'starting')
                category = state.get('category', '')
                risk = state.get('risk_level', '—')
                agents_running = state.get('agents_running', [])

                # Calculate progress
                progress = state.get('progress', {})
                done = sum(p.get('completed', 0) for p in progress.values())
                total = sum(p.get('total', 0) for p in progress.values()) or 32

                # Phase icons (using actual Unicode)
                phase_icons = {
                    'understanding': '🎯',
                    'exploration': '🔍',
                    'design': '✏️',
                    'review': '🔄',
                    'exit': '🚀',
                    'completed': '✅'
                }
                phase_icon = phase_icons.get(phase, '📋')

                # Risk with ANSI colors
                risk_colors = {
                    'HIGH': '\033[31m',      # Red
                    'MODERATE': '\033[33m',  # Yellow
                    'LOW': '\033[32m'        # Green
                }
                reset = '\033[0m'
                risk_color = risk_colors.get(risk, '')
                risk_display = f"{risk_color}{risk}{reset}" if risk_color else risk

                # Agent indicator
                agent_indicator = ""
                if agents_running:
                    first_agent = agents_running[0]
                    agent_indicator = f" ⚡{first_agent}"
                    if len(agents_running) > 1:
                        agent_indicator += f"+{len(agents_running) - 1}"

                # Category display
                category_display = f":{category}" if category else ""

                # Output collaborative status line
                print(f"[{model}]{style_display} 🤝 {project} {phase_icon} {phase}{category_display} [{done}/{total}] {risk_display}{agent_indicator}")
                return

        except (json.JSONDecodeError, IOError):
            pass

    # Default status line (not in collaborative mode)
    git_branch = get_git_branch()
    branch_display = f" | 🌿 {git_branch}" if git_branch else ""

    dir_name = Path(current_dir).name or current_dir
    print(f"[{model}]{style_display} 📁 {dir_name}{branch_display}")


if __name__ == '__main__':
    main()
