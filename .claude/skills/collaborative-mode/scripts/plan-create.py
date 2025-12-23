#!/usr/bin/env python3
"""
Create a new collaborative-mode plan file from template.

Usage:
    python plan-create.py <output_dir> --project <name> --slug <slug> --goal <goal>
    python plan-create.py docs/plans/myapp-auth --project myapp --slug auth --goal "Add user authentication"

Creates:
    <output_dir>/plan.md

Output (JSON):
    {"success": true, "path": "docs/plans/myapp-auth/plan.md"}
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import uuid


def get_template_path() -> Path:
    """Get path to plan-init.md template."""
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "templates" / "plan-init.md"
    return template_path


def create_plan(
    output_dir: Path,
    project: str,
    slug: str,
    goal: str,
    feature_name: str | None = None,
) -> dict:
    """Create a new plan file from template."""
    template_path = get_template_path()

    if not template_path.exists():
        return {
            "success": False,
            "error": f"Template not found: {template_path}",
        }

    # Read template
    template = template_path.read_text()

    # Generate metadata
    timestamp = datetime.now().isoformat()
    session_id = str(uuid.uuid4())[:8]

    # Default feature name from slug
    if not feature_name:
        feature_name = slug.replace("-", " ").title()

    # Substitute variables
    plan_content = template.replace("{{feature_name}}", feature_name)
    plan_content = plan_content.replace("{{project}}", project)
    plan_content = plan_content.replace("{{initial_goal}}", goal)
    plan_content = plan_content.replace("{{timestamp}}", timestamp)
    plan_content = plan_content.replace("{{session_id}}", session_id)

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write plan file
    plan_path = output_dir / "plan.md"
    plan_path.write_text(plan_content)

    return {
        "success": True,
        "path": str(plan_path),
        "session_id": session_id,
        "project": project,
        "slug": slug,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create a new collaborative-mode plan file"
    )
    parser.add_argument("output_dir", help="Directory to create plan.md in")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--slug", "-s", required=True, help="Feature slug")
    parser.add_argument("--goal", "-g", required=True, help="Initial goal/description")
    parser.add_argument("--name", "-n", help="Feature name (defaults to slug titlecased)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = create_plan(
        output_dir=Path(args.output_dir),
        project=args.project,
        slug=args.slug,
        goal=args.goal,
        feature_name=args.name,
    )

    if args.json:
        print(json.dumps(result))
    else:
        if result["success"]:
            print(f"Created: {result['path']}")
            print(f"Session: {result['session_id']}")
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
