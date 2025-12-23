#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detect project name by walking up from a directory to find .git

Usage:
    python detect-project.py /path/to/start/dir
    python detect-project.py  # uses current directory

Output:
    JSON with project info:
    {
        "project_name": "my-project",
        "project_root": "/path/to/my-project",
        "git_found": true
    }
"""

import json
import os
import sys
from pathlib import Path


def find_git_root(start_path: str) -> tuple[Path | None, bool]:
    """
    Walk up from start_path looking for a .git directory.
    Returns (project_root, git_found)
    """
    current = Path(start_path).resolve()

    # Walk up the directory tree
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return current, True
        current = current.parent

    # Check root as well
    git_dir = current / ".git"
    if git_dir.exists() and git_dir.is_dir():
        return current, True

    return None, False


def detect_project(start_path: str) -> dict:
    """
    Detect project name from directory structure.

    Strategy:
    1. Walk up to find .git directory
    2. The directory containing .git is the project root
    3. The basename of that directory is the project name
    4. If no .git found, fall back to basename of start_path
    """
    start = Path(start_path).resolve()

    project_root, git_found = find_git_root(start_path)

    if git_found and project_root:
        return {
            "project_name": project_root.name,
            "project_root": str(project_root),
            "git_found": True
        }
    else:
        # Fallback: use the start directory name
        return {
            "project_name": start.name,
            "project_root": str(start),
            "git_found": False
        }


def main():
    # Get start path from argument or use current directory
    if len(sys.argv) > 1:
        start_path = sys.argv[1]
    else:
        start_path = os.getcwd()

    # Expand environment variables
    start_path = os.path.expandvars(start_path)
    start_path = os.path.expanduser(start_path)

    if not os.path.exists(start_path):
        print(json.dumps({
            "error": f"Path does not exist: {start_path}",
            "project_name": None,
            "project_root": None,
            "git_found": False
        }))
        sys.exit(1)

    result = detect_project(start_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
