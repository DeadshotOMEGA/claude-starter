#!/usr/bin/env python3
"""
Match requirements text to available agents based on triggers and capabilities.

Takes requirements summary and returns matched agents with relevance scores.
Supports project-aware merging (project-specific overrides shared).
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


def load_registry(registry_path: Path = None) -> dict[str, Any]:
    """Load the agents-registry.json file."""
    if registry_path is None:
        registry_path = Path(".claude/registries/agents-registry.json")

    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}", file=sys.stderr)
        print("Run /sync-registry first to create it.", file=sys.stderr)
        sys.exit(1)

    return json.loads(registry_path.read_text(encoding="utf-8"))


def get_merged_agents(registry: dict, project: str | None = None) -> dict[str, Any]:
    """
    Get merged agent pool (shared + project-specific).
    Project agents override shared agents with same name.
    """
    agents = dict(registry["shared"].get("agents", {}))

    if project and project in registry.get("projects", {}):
        project_agents = registry["projects"][project].get("agents", {})
        agents.update(project_agents)  # Project overrides shared

    return agents




def tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words."""
    return set(re.findall(r"\b[a-z][a-z0-9-]+\b", text.lower()))


def calculate_match_score(
    requirements_tokens: set[str],
    triggers: list[str],
    capabilities: list[str],
    description: str,
) -> float:
    """
    Calculate match score between requirements and agent.

    Scoring:
    - Trigger match: 10 points each
    - Capability match: 5 points each
    - Description keyword match: 1 point each
    """
    score = 0.0

    triggers_lower = [t.lower() for t in triggers]
    capabilities_lower = [c.lower() for c in capabilities]
    description_tokens = tokenize(description)

    for token in requirements_tokens:
        # Check triggers (highest weight)
        for trigger in triggers_lower:
            if token in trigger or trigger in token:
                score += 10.0
                break

        # Check capabilities (medium weight)
        for cap in capabilities_lower:
            if token in cap or cap in token:
                score += 5.0
                break

        # Check description (low weight)
        if token in description_tokens:
            score += 1.0

    return score


def match_requirements(
    requirements: str,
    project: str | None = None,
    registry_path: Path | None = None,
    threshold: float = 5.0,
) -> dict[str, Any]:
    """
    Match requirements to agents and skills.

    Args:
        requirements: Text describing the work to be done
        project: Optional project name for project-specific agents
        registry_path: Optional path to registry.json
        threshold: Minimum score to include an agent

    Returns:
        Dict with matched agents grouped by tier
    """
    registry = load_registry(registry_path)
    agents = get_merged_agents(registry, project)

    requirements_tokens = tokenize(requirements)

    matched_agents = {}

    # Score and filter agents
    for name, agent in agents.items():
        score = calculate_match_score(
            requirements_tokens,
            agent.get("triggers", []),
            agent.get("capabilities", []),
            agent.get("description", ""),
        )

        if score >= threshold:
            matched_agents[name] = {
                **agent,
                "match_score": score,
            }

    # Group agents by tier (agents can appear in multiple tiers)
    by_tier: dict[int, list[dict]] = {}
    for name, agent in matched_agents.items():
        tiers = agent.get("tiers", [])
        if not tiers:
            tiers = [4]  # Default to implementation tier

        for tier in tiers:
            if tier not in by_tier:
                by_tier[tier] = []

            by_tier[tier].append({"name": name, "active_tier": tier, **agent})

    # Sort each tier by score (highest first)
    for tier in by_tier:
        by_tier[tier].sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "project": project,
        "requirements_summary": requirements[:500],
        "matched_agents": matched_agents,
        "by_tier": {str(k): v for k, v in sorted(by_tier.items())},
        "total_matched": len(matched_agents),
    }


def detect_project(requirements: str, registry: dict) -> str | None:
    """
    Attempt to detect project from requirements text.

    Looks for project keywords defined in registry.
    """
    requirements_lower = requirements.lower()

    for project_name, project_data in registry.get("projects", {}).items():
        keywords = project_data.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in requirements_lower:
                return project_name

    return None


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Match requirements to agents")
    parser.add_argument("requirements", nargs="?", help="Requirements text (or read from stdin)")
    parser.add_argument("-p", "--project", help="Project name for project-specific agents")
    parser.add_argument("-t", "--threshold", type=float, default=5.0, help="Minimum match score")
    parser.add_argument("--detect-project", action="store_true", help="Auto-detect project from requirements")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get requirements text
    if args.requirements:
        requirements = args.requirements
    elif not sys.stdin.isatty():
        requirements = sys.stdin.read()
    else:
        print("Error: Provide requirements as argument or via stdin", file=sys.stderr)
        sys.exit(1)

    # Auto-detect project if requested
    project = args.project
    if args.detect_project and not project:
        registry = load_registry()
        project = detect_project(requirements, registry)
        if project and not args.json:
            print(f"Detected project: {project}")

    # Run matching
    result = match_requirements(requirements, project=project, threshold=args.threshold)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nMatched {result['total_matched']} agents for project: {project or 'shared'}")
        print("=" * 60)

        for tier, agents in result["by_tier"].items():
            tier_names = {
                "0": "Git Setup",
                "1": "Explore & Research",
                "2": "Domain Expertise",
                "3": "Planning",
                "4": "Implementation",
                "5": "Validation",
            }
            print(f"\nTier {tier}: {tier_names.get(tier, 'Unknown')}")
            print("-" * 40)

            for agent in agents:
                parallel = "parallel" if agent.get("parallel", True) else "sequential"
                print(f"  {agent['name']:30} (score: {agent['match_score']:.1f}, {parallel})")


if __name__ == "__main__":
    main()
