#!/usr/bin/env python3
"""
Discover and catalog all agents and skills for the workflow orchestrator.

Features:
- Scans shared .claude/ and project-specific [project]/.claude/ directories
- Uses file modification times for incremental sync
- Infers tier/capabilities from descriptions when not explicitly provided
- Outputs unified registry.json
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Tier inference patterns - maps keywords to tiers
# Use word stems so "researcher" matches "research", etc.
TIER_PATTERNS = {
    0: [r"\bgit\b(?!hub)", r"\bbranch", r"\brelease", r"\bversion"],  # Git operations
    1: [r"\bexplor", r"\bsearch", r"\bresearch", r"\binvestigat", r"\bdiscover", r"\bfind\b"],  # Research
    2: [r"\bexpert", r"\barchitect", r"\bdesign", r"\badvis", r"\bspecialist", r"\badmin", r"\bauditor"],  # Expertise
    3: [r"\bplan", r"\bdecompos", r"\bbreakdown", r"\bstrateg"],  # Planning
    4: [r"\bimplement", r"\bengineer(?!ing)", r"\bdevelop", r"\bprogramm", r"\bbuild\b", r"\bcreat", r"\bmodif"],  # Implementation
    5: [r"\btest", r"\breview", r"\bvalid", r"\bverif", r"\bcheck\b"],  # Validation
}

# Category inference patterns
CATEGORY_PATTERNS = {
    "git": ["git", "branch", "commit", "release", "version", "merge"],
    "explore": ["explore", "search", "find", "discover", "trace"],
    "research": ["research", "investigate", "study", "analyze"],
    "expertise": ["expert", "architect", "designer", "specialist", "advisor", "admin"],
    "planning": ["plan", "decompos", "breakdown", "strategy", "coordinate"],
    "implementation": ["implement", "engineer", "develop", "programm", "build", "code"],
    "validation": ["test", "review", "valid", "verif", "check", "audit", "quality"],
    "documentation": ["document", "write", "technical writer", "docs"],
    "utility": ["utility", "helper", "tool"],
}


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
        # Look for first heading as name, first paragraph as description
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


def infer_tiers(description: str, name: str) -> list[int]:
    """Infer all matching tiers from description and name."""
    text = f"{name} {description}".lower()
    matched_tiers = []

    for tier, patterns in TIER_PATTERNS.items():
        for pattern in patterns:
            # Patterns are already regex patterns with word boundaries
            if re.search(pattern, text):
                matched_tiers.append(tier)
                break  # Only match once per tier

    return sorted(matched_tiers) if matched_tiers else []


def infer_category(description: str, name: str) -> str:
    """Infer category from description and name."""
    text = f"{name} {description}".lower()

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                return category

    return "general"


def infer_capabilities(description: str) -> list[str]:
    """Extract capabilities from description."""
    capabilities = []
    desc_lower = description.lower()

    # Common capability keywords
    capability_keywords = [
        "coordination", "delegation", "monitoring", "validation",
        "implementation", "review", "testing", "documentation",
        "search", "discovery", "analysis", "design", "optimization",
        "debugging", "security", "performance", "database", "api",
        "frontend", "backend", "deployment", "migration",
    ]

    for keyword in capability_keywords:
        if keyword in desc_lower:
            capabilities.append(keyword)

    return capabilities[:5]  # Limit to 5 most relevant


def infer_triggers(description: str, name: str, capabilities: list[str]) -> list[str]:
    """Infer trigger keywords from description, name, and capabilities."""
    triggers = []

    # Add name-based triggers
    name_parts = name.replace("-", " ").replace("_", " ").split()
    triggers.extend([p for p in name_parts if len(p) > 2])

    # Add capability-based triggers
    triggers.extend(capabilities[:3])

    # Extract key phrases from description
    desc_lower = description.lower()
    trigger_phrases = [
        "complex task", "multi-file", "refactor", "security",
        "database", "api", "frontend", "backend", "test",
        "performance", "deployment", "documentation",
    ]

    for phrase in trigger_phrases:
        if phrase in desc_lower:
            triggers.append(phrase.replace(" ", "-"))

    return list(set(triggers))[:6]  # Unique, limit to 6


def extract_keywords(description: str, name: str) -> list[str]:
    """Extract project detection keywords."""
    keywords = []
    text = f"{name} {description}".lower()

    # Add name parts
    name_parts = name.replace("-", " ").replace("_", " ").split()
    keywords.extend([p for p in name_parts if len(p) > 2])

    # Common product/framework names to detect
    frameworks = ["heroui", "nextui", "react", "vue", "angular", "tailwind", "prisma"]
    for fw in frameworks:
        if fw in text:
            keywords.append(fw)

    return list(set(keywords))


def process_agent_file(file_path: Path, relative_path: str) -> dict[str, Any] | None:
    """Process a single agent file and return its metadata."""
    frontmatter = parse_frontmatter(file_path)
    if not frontmatter:
        return None

    # Use filename as fallback name
    name = frontmatter.get("name", file_path.stem)
    # Clean up name if it came from heading (e.g., "HeroUI Guardian Agent" -> "heroui-guardian")
    if frontmatter.get("_no_frontmatter") and "name" in frontmatter:
        # Keep the descriptive name for display
        pass
    description = frontmatter.get("description", "")

    # Get or infer tiers (supports both 'tier' and 'tiers' in frontmatter)
    tiers = frontmatter.get("tiers")
    if tiers is not None:
        # Handle array format from frontmatter
        if isinstance(tiers, list):
            tiers = [int(t) for t in tiers]
        elif isinstance(tiers, str):
            tiers = [int(t.strip()) for t in tiers.strip("[]").split(",")]
    else:
        # Check for single tier
        tier = frontmatter.get("tier")
        if tier is not None:
            tiers = [int(tier)]
        else:
            tiers = infer_tiers(description, name)

    # Get or infer category
    category = frontmatter.get("category")
    if not category:
        category = infer_category(description, name)

    # Get or infer capabilities
    capabilities = frontmatter.get("capabilities")
    if not capabilities:
        capabilities = infer_capabilities(description)
    elif isinstance(capabilities, str):
        capabilities = [c.strip() for c in capabilities.split(",")]

    # Get or infer triggers
    triggers = frontmatter.get("triggers")
    if not triggers:
        triggers = infer_triggers(description, name, capabilities)
    elif isinstance(triggers, str):
        triggers = [t.strip() for t in triggers.split(",")]

    # Determine if can run in parallel (default True for most)
    parallel = frontmatter.get("parallel", "true")
    if isinstance(parallel, str):
        parallel = parallel.lower() in ("true", "yes", "1")

    return {
        "tiers": tiers,
        "category": category,
        "capabilities": capabilities,
        "triggers": triggers,
        "parallel": parallel,
        "path": relative_path,
        "mtime": os.path.getmtime(file_path),
        "description": description[:200] if description else "",
    }


def process_skill_file(file_path: Path, relative_path: str) -> dict[str, Any] | None:
    """Process a single skill file and return its metadata."""
    frontmatter = parse_frontmatter(file_path)
    if not frontmatter:
        return None

    name = frontmatter.get("name", file_path.parent.name)
    description = frontmatter.get("description", "")

    # Skills can have tiers too (supports both 'tier' and 'tiers')
    tiers = frontmatter.get("tiers")
    if tiers is not None:
        if isinstance(tiers, list):
            tiers = [int(t) for t in tiers]
        elif isinstance(tiers, str):
            tiers = [int(t.strip()) for t in tiers.strip("[]").split(",")]
    else:
        tier = frontmatter.get("tier")
        if tier is not None:
            tiers = [int(tier)]
        else:
            tiers = []  # Skills default to no tier (utility)

    category = frontmatter.get("category", "utility")

    capabilities = frontmatter.get("capabilities")
    if not capabilities:
        capabilities = infer_capabilities(description)
    elif isinstance(capabilities, str):
        capabilities = [c.strip() for c in capabilities.split(",")]

    triggers = frontmatter.get("triggers")
    if not triggers:
        triggers = infer_triggers(description, name, capabilities)
    elif isinstance(triggers, str):
        triggers = [t.strip() for t in triggers.split(",")]

    return {
        "tiers": tiers,
        "category": category,
        "capabilities": capabilities,
        "triggers": triggers,
        "path": relative_path,
        "mtime": os.path.getmtime(file_path),
        "description": description[:200] if description else "",
    }


def load_existing_registry(registry_path: Path) -> dict[str, Any]:
    """Load existing registry if it exists."""
    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "version": "1.0",
        "last_synced": None,
        "shared": {"base_path": ".claude", "agents": {}, "skills": {}},
        "projects": {},
    }


def find_projects(base_path: Path) -> list[tuple[str, Path]]:
    """Find all project directories with .claude folders."""
    projects = []

    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            claude_dir = item / ".claude"
            if claude_dir.exists() and claude_dir.is_dir():
                projects.append((item.name, claude_dir))

    return projects


def sync_registry(base_path: Path = Path(".")) -> dict[str, int]:
    """Main sync function. Returns counts of changes."""
    stats = {"unchanged": 0, "added": 0, "modified": 0, "removed": 0}

    registry_path = base_path / ".claude/skills/orchestrating-workflows/registry.json"
    registry = load_existing_registry(registry_path)

    # Helper to check if file needs update
    def needs_update(existing: dict | None, file_path: Path) -> bool:
        if existing is None:
            return True
        stored_mtime = existing.get("mtime", 0)
        return os.path.getmtime(file_path) > stored_mtime

    # Process shared agents
    shared_agents_dir = base_path / ".claude/agents"
    new_shared_agents = {}
    existing_shared_agents = registry["shared"].get("agents", {})

    if shared_agents_dir.exists():
        for agent_file in shared_agents_dir.glob("*.md"):
            name = agent_file.stem
            relative_path = str(agent_file.relative_to(base_path))
            existing = existing_shared_agents.get(name)

            if needs_update(existing, agent_file):
                metadata = process_agent_file(agent_file, relative_path)
                if metadata:
                    new_shared_agents[name] = metadata
                    stats["added" if existing is None else "modified"] += 1
            else:
                new_shared_agents[name] = existing
                stats["unchanged"] += 1

    # Count removed shared agents
    for name in existing_shared_agents:
        if name not in new_shared_agents:
            stats["removed"] += 1

    registry["shared"]["agents"] = new_shared_agents

    # Process shared skills
    shared_skills_dir = base_path / ".claude/skills"
    new_shared_skills = {}
    existing_shared_skills = registry["shared"].get("skills", {})

    if shared_skills_dir.exists():
        for skill_file in shared_skills_dir.glob("*/SKILL.md"):
            # Skip orchestrating-workflows itself
            if "orchestrating-workflows" in str(skill_file):
                continue

            name = skill_file.parent.name
            relative_path = str(skill_file.relative_to(base_path))
            existing = existing_shared_skills.get(name)

            if needs_update(existing, skill_file):
                metadata = process_skill_file(skill_file, relative_path)
                if metadata:
                    new_shared_skills[name] = metadata
                    stats["added" if existing is None else "modified"] += 1
            else:
                new_shared_skills[name] = existing
                stats["unchanged"] += 1

    # Count removed shared skills
    for name in existing_shared_skills:
        if name not in new_shared_skills:
            stats["removed"] += 1

    registry["shared"]["skills"] = new_shared_skills

    # Process project-specific agents and skills
    projects = find_projects(base_path)

    for project_name, claude_dir in projects:
        if project_name not in registry["projects"]:
            registry["projects"][project_name] = {
                "base_path": str(claude_dir.relative_to(base_path)),
                "keywords": [],
                "agents": {},
                "skills": {},
                "commands": {},
            }

        project_data = registry["projects"][project_name]
        existing_project_agents = project_data.get("agents", {})
        existing_project_skills = project_data.get("skills", {})

        # Project agents
        new_project_agents = {}
        agents_dir = claude_dir / "agents"

        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                name = agent_file.stem
                relative_path = str(agent_file.relative_to(base_path))
                existing = existing_project_agents.get(name)

                if needs_update(existing, agent_file):
                    metadata = process_agent_file(agent_file, relative_path)
                    if metadata:
                        new_project_agents[name] = metadata
                        # Extract keywords for project detection
                        keywords = extract_keywords(metadata.get("description", ""), name)
                        project_data["keywords"] = list(set(project_data.get("keywords", []) + keywords))
                        stats["added" if existing is None else "modified"] += 1
                else:
                    new_project_agents[name] = existing
                    stats["unchanged"] += 1

        project_data["agents"] = new_project_agents

        # Project skills
        new_project_skills = {}
        skills_dir = claude_dir / "skills"

        if skills_dir.exists():
            # Handle both SKILL.md in subdirs and direct .md files
            for skill_file in list(skills_dir.glob("*/SKILL.md")) + list(skills_dir.glob("*.md")):
                if skill_file.name == "SKILL.md":
                    name = skill_file.parent.name
                else:
                    name = skill_file.stem

                relative_path = str(skill_file.relative_to(base_path))
                existing = existing_project_skills.get(name)

                if needs_update(existing, skill_file):
                    metadata = process_skill_file(skill_file, relative_path)
                    if metadata:
                        new_project_skills[name] = metadata
                        stats["added" if existing is None else "modified"] += 1
                else:
                    new_project_skills[name] = existing
                    stats["unchanged"] += 1

        project_data["skills"] = new_project_skills

        # Project commands (just track paths, no metadata needed)
        commands_dir = claude_dir / "commands"
        if commands_dir.exists():
            project_data["commands"] = {
                cmd.stem: {
                    "path": str(cmd.relative_to(base_path)),
                    "mtime": os.path.getmtime(cmd),
                }
                for cmd in commands_dir.glob("*.md")
            }

    # Update timestamp and save
    registry["last_synced"] = datetime.now().isoformat()

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return stats


def main():
    """CLI entry point."""
    base_path = Path(".")

    print("Syncing workflow orchestrator registry...")
    print(f"Base path: {base_path.absolute()}")
    print()

    stats = sync_registry(base_path)

    print("Registry sync complete:")
    print(f"  {stats['unchanged']:3d} unchanged (skipped)")
    print(f"  + {stats['added']:3d} added")
    print(f"  ~ {stats['modified']:3d} modified")
    print(f"  - {stats['removed']:3d} removed")
    print()
    print("Registry: .claude/skills/orchestrating-workflows/registry.json")


if __name__ == "__main__":
    main()
