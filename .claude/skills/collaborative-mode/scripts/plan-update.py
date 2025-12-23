#!/usr/bin/env python3
"""
Update a specific section in a collaborative-mode plan file.

Usage:
    python plan-update.py <plan_path> <section> <content>
    python plan-update.py <plan_path> <section> --file <content_file>
    echo "content" | python plan-update.py <plan_path> <section> --stdin

Sections use dot notation matching phases.json:
    overview.scope, overview.users, overview.success_criteria, etc.
    impact.affected_areas, impact.integration_points, etc.
    implementation.approach, implementation.patterns, etc.

Examples:
    python plan-update.py docs/plans/my-plan/plan.md overview.scope "Define user auth boundaries"
    python plan-update.py docs/plans/my-plan/plan.md impact.risks --file risks.md
"""

import sys
import re
import argparse
from pathlib import Path

# Map section paths to markdown headers
SECTION_MAP = {
    # Overview sections
    "overview.scope": "### Scope",
    "overview.users": "### Users",
    "overview.success_criteria": "### Success Criteria",
    "overview.constraints": "### Constraints",
    "overview.dependencies": "### Dependencies",
    "overview.current_state": "### Current State",
    "overview.prior_attempts": "### Prior Attempts",
    "overview.urgency": "### Urgency",

    # Impact sections
    "impact.affected_areas": "### Affected Areas",
    "impact.integration_points": "### Integration Points",
    "impact.risks": "### Risks",
    "impact.undocumented": "### Undocumented Behavior",
    "impact.external_services": "### External Services",

    # Implementation sections
    "implementation.approach": "### Approach",
    "implementation.patterns": "### Patterns",
    "implementation.data": "### Data & State",
    "implementation.error_handling": "### Error Handling",
    "implementation.rollout": "### Rollout",
    "implementation.ux": "### UX",
    "implementation.maintainability": "### Maintainability",
    "implementation.observability": "### Observability",
    "implementation.extensibility": "### Extensibility",

    # Requirements sections
    "requirements.performance": "### Performance",
    "requirements.security": "### Security",

    # Validation sections
    "validation.testing": "### Testing",

    # Review sections
    "review.scope_changes": "### Scope Changes",
    "review.success_validation": "### Success Validation",
    "review.constraint_changes": "### Constraint Changes",
    "review.dependency_changes": "### Dependency Changes",
    "review.risk_summary": "### Risk Summary",
    "review.feasibility": "### Feasibility",
    "review.open_questions": "### Open Questions",
}


def find_section_bounds(lines: list[str], header: str) -> tuple[int, int]:
    """Find the start and end line indices for a section."""
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if line.strip() == header:
            start_idx = i
        elif start_idx is not None and line.startswith("### "):
            # Next section of same level
            end_idx = i
            break
        elif start_idx is not None and line.startswith("---"):
            # Section divider
            end_idx = i
            break
        elif start_idx is not None and line.startswith("## ") and i > start_idx:
            # Parent section ended
            end_idx = i
            break

    if start_idx is None:
        return -1, -1

    # If no end found, go to end of file
    if end_idx is None:
        end_idx = len(lines)

    return start_idx, end_idx


def update_section(plan_path: Path, section: str, content: str) -> bool:
    """Update a section in the plan file."""
    if section not in SECTION_MAP:
        print(f"Error: Unknown section '{section}'", file=sys.stderr)
        print(f"Valid sections: {', '.join(sorted(SECTION_MAP.keys()))}", file=sys.stderr)
        return False

    header = SECTION_MAP[section]

    if not plan_path.exists():
        print(f"Error: Plan file not found: {plan_path}", file=sys.stderr)
        return False

    lines = plan_path.read_text().splitlines(keepends=True)

    # Normalize line endings
    lines = [line.rstrip('\r\n') + '\n' for line in lines]

    start_idx, end_idx = find_section_bounds([l.rstrip('\n') for l in lines], header)

    if start_idx == -1:
        print(f"Error: Section '{header}' not found in plan", file=sys.stderr)
        return False

    # Build new section content
    new_content = [f"{header}\n"]

    # Add the content (ensure proper formatting)
    content_lines = content.strip().split('\n')
    for line in content_lines:
        new_content.append(line + '\n')
    new_content.append('\n')

    # Replace the section
    new_lines = lines[:start_idx] + new_content + lines[end_idx:]

    # Write back
    plan_path.write_text(''.join(new_lines))

    print(f"Updated section: {section}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Update a section in a collaborative-mode plan file")
    parser.add_argument("plan_path", nargs="?", help="Path to the plan.md file")
    parser.add_argument("section", nargs="?", help="Section to update (e.g., overview.scope)")
    parser.add_argument("content", nargs="?", help="Content to add (or use --file/--stdin)")
    parser.add_argument("--file", "-f", help="Read content from file")
    parser.add_argument("--stdin", action="store_true", help="Read content from stdin")
    parser.add_argument("--list-sections", action="store_true", help="List all valid sections")

    args = parser.parse_args()

    if args.list_sections:
        print("Valid sections:")
        for section in sorted(SECTION_MAP.keys()):
            print(f"  {section}")
        return 0

    # Require plan_path and section for actual updates
    if not args.plan_path or not args.section:
        parser.error("plan_path and section are required (unless using --list-sections)")
        return 1

    # Get content from appropriate source
    if args.stdin:
        content = sys.stdin.read()
    elif args.file:
        content = Path(args.file).read_text()
    elif args.content:
        content = args.content
    else:
        print("Error: No content provided. Use positional arg, --file, or --stdin", file=sys.stderr)
        return 1

    plan_path = Path(args.plan_path)

    if update_section(plan_path, args.section, content):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
