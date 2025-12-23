#!/usr/bin/env python3
"""
Discover and catalog all skills for the skill evaluation hook.

Features:
- Scans .claude/skills/ for SKILL.md files
- Merges discovered skills with manual config from skills-config.json
- Outputs skills-registry.json optimized for hook evaluation
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_frontmatter(file_path: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return {}

    # Match YAML frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        # No frontmatter - try to extract info from content
        frontmatter = {"_no_frontmatter": True}

        # Extract name from first heading
        heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if heading_match:
            frontmatter["name"] = heading_match.group(1).strip()

        # Extract description from first non-heading paragraph
        para_match = re.search(r"^(?!#)([A-Z][^\n]{20,})", content, re.MULTILINE)
        if para_match:
            frontmatter["description"] = para_match.group(1).strip()[:200]

        return frontmatter

    frontmatter = {}
    yaml_content = match.group(1)

    # Simple YAML parsing for common fields
    for line in yaml_content.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            # Handle arrays (simple single-line format)
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            # Handle quoted strings
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            frontmatter[key] = value

    return frontmatter


def discover_skills(base_path: Path) -> dict[str, dict[str, Any]]:
    """Scan for all SKILL.md files and extract basic info."""
    discovered = {}
    skills_dir = base_path / ".claude/skills"

    if not skills_dir.exists():
        return discovered

    for skill_file in skills_dir.glob("*/SKILL.md"):
        # Skip orchestrating-workflows itself
        if "orchestrating-workflows" in str(skill_file):
            continue

        name = skill_file.parent.name
        frontmatter = parse_frontmatter(skill_file)

        if not frontmatter:
            continue

        description = frontmatter.get("description", "")

        discovered[name] = {
            "what": description[:200] if description else "",
            "path": f"@.claude/skills/{name}/SKILL.md",
            "mtime": os.path.getmtime(skill_file),
        }

    return discovered


def load_skills_config(base_path: Path) -> dict[str, dict[str, Any]]:
    """Load manual skill metadata from skills-config.json."""
    config_path = base_path / ".claude/registries/skills-config.json"

    if not config_path.exists():
        print(f"Warning: {config_path} not found", file=sys.stderr)
        return {}

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return config.get("skills", {})
    except Exception as e:
        print(f"Error loading skills config: {e}", file=sys.stderr)
        return {}


def merge_skills(discovered: dict[str, dict], config: dict[str, dict]) -> dict[str, dict]:
    """Merge discovered skills with manual config."""
    merged = {}

    for skill_name, skill_data in discovered.items():
        # Start with discovered data
        merged_skill = {
            "what": skill_data["what"],
            "path": skill_data["path"],
        }

        # Merge with config if exists
        if skill_name in config:
            cfg = config[skill_name]
            merged_skill["domain"] = cfg.get("domain", "reference")
            merged_skill["when"] = cfg.get("when", "")
            merged_skill["priority"] = cfg.get("priority", 2)
            merged_skill["why"] = cfg.get("why", "")
        else:
            # Default values for skills not in config
            merged_skill["domain"] = "reference"
            merged_skill["when"] = ""
            merged_skill["priority"] = 2
            merged_skill["why"] = ""

        merged[skill_name] = merged_skill

    return merged


def sync_skills_registry(base_path: Path = Path(".")) -> dict[str, int]:
    """Main sync function. Returns counts of changes."""
    stats = {"discovered": 0, "configured": 0, "missing_config": 0}

    # Discover all skills
    discovered = discover_skills(base_path)
    stats["discovered"] = len(discovered)

    # Load manual config
    config = load_skills_config(base_path)
    stats["configured"] = len(config)

    # Merge
    merged = merge_skills(discovered, config)

    # Check for skills without config
    missing = set(discovered.keys()) - set(config.keys())
    stats["missing_config"] = len(missing)

    if missing:
        print(f"Warning: {len(missing)} skills missing from config:", file=sys.stderr)
        for skill in sorted(missing):
            print(f"  - {skill}", file=sys.stderr)

    # Build registry
    registry = {
        "version": "1.0",
        "last_synced": datetime.now().isoformat(),
        "skills": merged,
    }

    # Write registry
    registry_path = base_path / ".claude/registries/skills-registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return stats


def main():
    """CLI entry point."""
    base_path = Path(".")

    print("Syncing skills registry...")
    print(f"Base path: {base_path.absolute()}")
    print()

    stats = sync_skills_registry(base_path)

    print("Skills registry sync complete:")
    print(f"  {stats['discovered']:3d} skills discovered")
    print(f"  {stats['configured']:3d} skills configured")
    print(f"  {stats['missing_config']:3d} missing config")
    print()
    print("Registry: .claude/registries/skills-registry.json")


if __name__ == "__main__":
    main()
