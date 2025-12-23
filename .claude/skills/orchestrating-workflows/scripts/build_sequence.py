#!/usr/bin/env python3
"""
Build execution sequence from matched agents.

Takes matched agents and builds a tier-ordered execution plan
with parallel groupings where possible.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# Tier metadata
TIER_DEFINITIONS = {
    0: {
        "name": "Git Setup",
        "description": "Branch creation and git flow setup",
        "wait": True,
        "parallel_within": False,
    },
    1: {
        "name": "Explore & Research",
        "description": "Codebase exploration and external research",
        "wait": True,
        "parallel_within": True,
    },
    2: {
        "name": "Domain Expertise",
        "description": "Consult domain experts for guidance",
        "wait": True,
        "parallel_within": True,
    },
    3: {
        "name": "Planning",
        "description": "Create implementation plans from gathered context",
        "wait": True,
        "parallel_within": False,
    },
    4: {
        "name": "Implementation",
        "description": "Execute implementation tasks",
        "wait": True,
        "parallel_within": True,  # Parallel per plan task dependencies
    },
    5: {
        "name": "Validation",
        "description": "Testing, review, and verification",
        "wait": True,
        "parallel_within": True,
    },
}


# Tier prerequisite requirements for pdocs validation
TIER_DOC_REQUIREMENTS = {
    3: {
        "required": ["investigation"],
        "message": "Planning requires investigation. Run Tier 1 first.",
    },
    4: {
        "required": ["plan"],
        "message": "Implementation requires valid plan. Run Tier 3 first.",
    },
}


def validate_tier_prerequisites(
    tier: int,
    feature_path: str,
) -> tuple[bool, str]:
    """
    Validate that required documents exist for a tier using pdocs.

    Args:
        tier: The tier number to validate prerequisites for
        feature_path: Path to the feature directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if tier not in TIER_DOC_REQUIREMENTS:
        return True, ""

    requirements = TIER_DOC_REQUIREMENTS[tier]

    for doc_type in requirements["required"]:
        try:
            result = subprocess.run(
                [
                    "bunx",
                    ".claude/pdocs",
                    "check",
                    feature_path,
                    "--type",
                    doc_type,
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False, requirements["message"]

            status = json.loads(result.stdout)

            if not status.get("valid"):
                return False, requirements["message"]

        except subprocess.TimeoutExpired:
            return False, f"Timeout validating {doc_type} document"
        except json.JSONDecodeError:
            return False, f"Invalid response from pdocs for {doc_type}"
        except FileNotFoundError:
            # pdocs not available - skip validation
            return True, ""

    return True, ""


def build_sequence(
    matched_result: dict[str, Any],
    include_skills: bool = True,
    skip_validation: bool = False,
    feature_path: str | None = None,
) -> dict[str, Any]:
    """
    Build execution sequence from match results.

    Args:
        matched_result: Output from match_requirements.py
        include_skills: Whether to include matched skills
        skip_validation: Whether to skip tier prerequisite validation
        feature_path: Path to feature directory for validation

    Returns:
        Execution plan with ordered stages
    """
    by_tier = matched_result.get("by_tier", {})
    matched_skills = matched_result.get("matched_skills", {}) if include_skills else {}

    stages = []
    total_agents = 0
    validation_results: dict[int, dict[str, Any]] = {}

    # Determine feature path for validation
    effective_feature_path = feature_path or matched_result.get("project", ".")

    # Build stages in tier order
    for tier_num in sorted(int(t) for t in by_tier.keys()):
        tier_key = str(tier_num)
        agents = by_tier[tier_key]

        if not agents:
            continue

        tier_def = TIER_DEFINITIONS.get(tier_num, {
            "name": f"Tier {tier_num}",
            "description": "Unknown tier",
            "wait": True,
            "parallel_within": True,
        })

        # Validate tier prerequisites
        if skip_validation:
            validation_results[tier_num] = {
                "valid": True,
                "skipped": True,
                "message": "",
            }
        else:
            is_valid, error_message = validate_tier_prerequisites(
                tier_num,
                effective_feature_path,
            )
            validation_results[tier_num] = {
                "valid": is_valid,
                "skipped": False,
                "message": error_message,
            }

        # Separate parallel and sequential agents
        parallel_agents = [a for a in agents if a.get("parallel", True)]
        sequential_agents = [a for a in agents if not a.get("parallel", True)]

        tier_validation = validation_results[tier_num]
        stage = {
            "tier": tier_num,
            "name": tier_def["name"],
            "description": tier_def["description"],
            "wait_for_completion": tier_def["wait"],
            "validation": {
                "valid": tier_validation["valid"],
                "skipped": tier_validation["skipped"],
                "message": tier_validation["message"],
            },
            "parallel_agents": [
                {
                    "name": a["name"],
                    "path": a["path"],
                    "category": a.get("category", "general"),
                    "tiers": a.get("tiers", []),  # All tiers this agent belongs to
                    "match_score": a.get("match_score", 0),
                }
                for a in parallel_agents
            ],
            "sequential_agents": [
                {
                    "name": a["name"],
                    "path": a["path"],
                    "category": a.get("category", "general"),
                    "tiers": a.get("tiers", []),  # All tiers this agent belongs to
                    "match_score": a.get("match_score", 0),
                }
                for a in sequential_agents
            ],
        }

        stages.append(stage)
        total_agents += len(agents)

    # Add skills as references (not executed, but available)
    skill_references = [
        {
            "name": name,
            "path": skill["path"],
            "category": skill.get("category", "utility"),
        }
        for name, skill in matched_skills.items()
    ]

    # Compute overall validation status
    all_valid = all(
        validation_results.get(s["tier"], {}).get("valid", True)
        for s in stages
    )
    validation_errors = [
        {"tier": tier, "message": result["message"]}
        for tier, result in validation_results.items()
        if not result["valid"]
    ]

    return {
        "project": matched_result.get("project"),
        "requirements_summary": matched_result.get("requirements_summary", ""),
        "total_agents": total_agents,
        "total_stages": len(stages),
        "validation": {
            "all_valid": all_valid,
            "skip_validation": skip_validation,
            "errors": validation_errors,
        },
        "stages": stages,
        "available_skills": skill_references,
        "execution_notes": generate_execution_notes(stages),
    }


def generate_execution_notes(stages: list[dict]) -> list[str]:
    """Generate human-readable execution notes."""
    notes = []

    for stage in stages:
        tier = stage["tier"]
        parallel_count = len(stage["parallel_agents"])
        sequential_count = len(stage["sequential_agents"])

        if parallel_count > 0 and sequential_count > 0:
            notes.append(
                f"Tier {tier} ({stage['name']}): "
                f"Run {sequential_count} sequential agent(s) first, "
                f"then {parallel_count} in parallel"
            )
        elif parallel_count > 1:
            notes.append(
                f"Tier {tier} ({stage['name']}): "
                f"Run {parallel_count} agents in parallel"
            )
        elif parallel_count == 1:
            notes.append(
                f"Tier {tier} ({stage['name']}): "
                f"Run {stage['parallel_agents'][0]['name']}"
            )
        elif sequential_count > 0:
            notes.append(
                f"Tier {tier} ({stage['name']}): "
                f"Run {sequential_count} agent(s) sequentially"
            )

    return notes


def generate_task_prompt(
    sequence: dict[str, Any],
    requirements: str,
) -> str:
    """
    Generate a prompt for the workflow-orchestrator agent
    to execute this sequence.
    """
    project = sequence.get("project", "shared")
    stages = sequence.get("stages", [])

    prompt_parts = [
        "## Workflow Execution Plan",
        "",
        f"**Project**: {project}",
        f"**Total Agents**: {sequence['total_agents']}",
        f"**Stages**: {sequence['total_stages']}",
        "",
        "### Requirements",
        requirements[:1000],
        "",
        "### Execution Sequence",
        "",
    ]

    for stage in stages:
        prompt_parts.append(f"#### Stage {stage['tier']}: {stage['name']}")
        prompt_parts.append(f"*{stage['description']}*")
        prompt_parts.append("")

        if stage["sequential_agents"]:
            prompt_parts.append("**Sequential (run in order):**")
            for agent in stage["sequential_agents"]:
                prompt_parts.append(f"1. `{agent['name']}` - {agent['category']}")
            prompt_parts.append("")

        if stage["parallel_agents"]:
            prompt_parts.append("**Parallel (run simultaneously):**")
            for agent in stage["parallel_agents"]:
                prompt_parts.append(f"- `{agent['name']}` - {agent['category']}")
            prompt_parts.append("")

    if sequence.get("available_skills"):
        prompt_parts.append("### Available Skills")
        for skill in sequence["available_skills"]:
            prompt_parts.append(f"- `{skill['name']}` ({skill['category']})")
        prompt_parts.append("")

    prompt_parts.append("### Execution Instructions")
    prompt_parts.append("")
    prompt_parts.append("1. Execute each stage in order (Tier 0 → Tier 5)")
    prompt_parts.append("2. Within each stage, run sequential agents first")
    prompt_parts.append("3. Then spawn parallel agents simultaneously using multiple Task calls")
    prompt_parts.append("4. Wait for all agents in a stage to complete before proceeding")
    prompt_parts.append("5. Pass relevant outputs from earlier stages to later ones")
    prompt_parts.append("6. Use available skills as needed for reference")

    return "\n".join(prompt_parts)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build execution sequence from matched agents")
    parser.add_argument("match_file", nargs="?", help="JSON file from match_requirements.py (or stdin)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--prompt", action="store_true", help="Output as orchestrator prompt")
    parser.add_argument("-r", "--requirements", help="Original requirements (for prompt generation)")
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip tier prerequisite validation (bypass pdocs checks)",
    )
    parser.add_argument(
        "--feature-path",
        help="Path to feature directory for validation (defaults to project from match results)",
    )

    args = parser.parse_args()

    # Load match results
    if args.match_file:
        match_result = json.loads(Path(args.match_file).read_text())
    elif not sys.stdin.isatty():
        match_result = json.loads(sys.stdin.read())
    else:
        print("Error: Provide match results file or via stdin", file=sys.stderr)
        sys.exit(1)

    # Build sequence with validation options
    sequence = build_sequence(
        match_result,
        skip_validation=args.skip_validation,
        feature_path=args.feature_path,
    )

    if args.prompt:
        requirements = args.requirements or match_result.get("requirements_summary", "")
        print(generate_task_prompt(sequence, requirements))
    elif args.json:
        print(json.dumps(sequence, indent=2))
    else:
        print(f"Execution Plan for: {sequence.get('project', 'shared')}")
        print("=" * 60)
        print(f"Total agents: {sequence['total_agents']}")
        print(f"Stages: {sequence['total_stages']}")

        # Show validation status
        validation = sequence.get("validation", {})
        if validation.get("skip_validation"):
            print("Validation: SKIPPED")
        elif validation.get("all_valid"):
            print("Validation: PASSED")
        else:
            print("Validation: FAILED")
            for error in validation.get("errors", []):
                print(f"  - Tier {error['tier']}: {error['message']}")

        print()

        for note in sequence.get("execution_notes", []):
            print(f"  {note}")

        print()
        print("Stages:")
        for stage in sequence["stages"]:
            all_agents = stage["parallel_agents"] + stage["sequential_agents"]
            agent_names = [a["name"] for a in all_agents]
            stage_validation = stage.get("validation", {})
            validation_indicator = ""
            if stage_validation.get("skipped"):
                validation_indicator = " [SKIPPED]"
            elif not stage_validation.get("valid"):
                validation_indicator = " [BLOCKED]"
            print(f"  {stage['tier']}. {stage['name']}: {', '.join(agent_names)}{validation_indicator}")

        if sequence.get("available_skills"):
            print()
            print("Available skills:")
            for skill in sequence["available_skills"]:
                print(f"  - {skill['name']}")


if __name__ == "__main__":
    main()
