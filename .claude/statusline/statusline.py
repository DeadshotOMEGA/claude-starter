#!/usr/bin/env python3
"""
Universal Status Line

Composable status line that assembles segments from modular providers.
Each provider checks its own state file and contributes a segment.

Usage: Configure in .claude/settings.json:
  {
    "statusLine": {
      "type": "command",
      "command": "$CLAUDE_PROJECT_DIR/.claude/statusline/statusline.py"
    }
  }
"""

import json
import sys
from pathlib import Path

# Import providers
from providers import base, collab, agents, todo


def main():
    # Read JSON input from Claude Code
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    workspace = input_data.get('workspace', {})
    project_dir = workspace.get('project_dir', '.')

    # Get base segments (always present)
    base_segments = base.render(input_data)
    prefix = base_segments['prefix']

    # Collect optional segments
    segments = []

    # Collaborative mode takes precedence if active
    collab_segment = collab.render(project_dir)
    if collab_segment:
        segments.append(collab_segment)
    else:
        # Default: show directory and branch
        segments.append(f"📁 {base_segments['dir']}")
        if base_segments['branch']:
            segments.append(f"|{base_segments['branch']}")

    # Always show agents if running
    agents_segment = agents.render(project_dir)
    if agents_segment:
        segments.append(agents_segment)

    # Show todo progress if any
    todo_segment = todo.render(project_dir)
    if todo_segment:
        segments.append(todo_segment)

    # Assemble final status line
    print(f"{prefix} {' '.join(segments)}")


if __name__ == '__main__':
    main()
