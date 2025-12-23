#!/usr/bin/env python3
"""
Validate Claude Code subagent definition files.

Usage:
    python validate-agent.py path/to/agent.md
    python validate-agent.py .claude/agents/  # Validate all in directory
"""

import sys
import re
import os
from pathlib import Path

# Valid tool names (common ones - not exhaustive)
VALID_TOOLS = {
    'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep',
    'WebSearch', 'WebFetch', 'Task', 'TodoWrite', 'TodoRead',
    'NotebookEdit', 'AskUserQuestion', 'Skill',
    'mcp__*'  # MCP tools pattern
}

VALID_MODELS = {'sonnet', 'opus', 'haiku', 'inherit'}

VALID_PERMISSION_MODES = {'default', 'acceptEdits', 'bypassPermissions', 'plan', 'ignore'}

VALID_CATEGORIES = {'explore', 'expertise', 'implementation', 'git', 'planning', 'research', 'validation'}

# Naming convention: [domain]-[tier-suffix]
VALID_SUFFIXES = {
    0: {'manager'},
    1: {'explorer', 'researcher'},
    2: {'advisor'},
    3: {'planner', 'architect'},
    4: {'builder', 'optimizer'},
    5: {'checker', 'reviewer'},
}

ORCHESTRATOR_PATTERN = re.compile(r'^orchestrate-[a-z]+(-[a-z]+)*$')

# Common abbreviations to reject (ui-/ux- are standard, not abbreviations)
INVALID_PREFIXES = {'db-', 'fe-', 'be-'}
SENIORITY_PREFIXES = {'senior-', 'junior-', 'lead-', 'principal-', 'staff-'}


def validate_naming_convention(name: str, tiers: list[int]) -> list[str]:
    """Validate agent name follows naming convention."""
    issues = []

    # Check orchestrator pattern (valid cross-tier pattern)
    if ORCHESTRATOR_PATTERN.match(name):
        return []

    # Check for abbreviations
    for prefix in INVALID_PREFIXES:
        if name.startswith(prefix):
            full_word = {'db-': 'database-', 'fe-': 'frontend-', 'be-': 'backend-'}.get(prefix, prefix)
            issues.append(f"Avoid abbreviation '{prefix}' in name (use '{full_word}')")

    # Check for seniority prefixes
    for prefix in SENIORITY_PREFIXES:
        if name.startswith(prefix):
            issues.append(f"Avoid seniority prefix '{prefix}' in name")

    # Check for required suffix based on primary tier
    if tiers:
        primary_tier = tiers[0]
        valid_suffixes = VALID_SUFFIXES.get(primary_tier, set())
        if valid_suffixes:
            has_valid_suffix = any(name.endswith(f'-{s}') for s in valid_suffixes)
            if not has_valid_suffix:
                suffix_list = ', '.join(f'-{s}' for s in sorted(valid_suffixes))
                issues.append(f"Name should end with tier {primary_tier} suffix: {suffix_list}")

    # Check for single-word names (missing domain)
    if '-' not in name:
        issues.append(f"Name '{name}' should follow pattern [domain]-[suffix]")

    return issues


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, parts[2]


def parse_registry_metadata(body: str) -> dict:
    """Extract workflow-orchestrator-registry metadata from HTML comment."""
    pattern = r'<!--\s*workflow-orchestrator-registry\s*(.*?)-->'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return {}

    metadata = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    return metadata


def validate_agent(filepath: Path) -> list[str]:
    """Validate an agent file and return list of issues."""
    issues = []

    if not filepath.exists():
        return [f"File not found: {filepath}"]

    content = filepath.read_text()
    frontmatter, body = parse_frontmatter(content)

    # Check required fields
    if 'name' not in frontmatter:
        issues.append("Missing required field: name")
    if 'description' not in frontmatter:
        issues.append("Missing required field: description")

    # Check name matches filename
    if 'name' in frontmatter:
        expected_name = filepath.stem
        if frontmatter['name'] != expected_name:
            issues.append(f"Name mismatch: frontmatter says '{frontmatter['name']}' but filename is '{expected_name}'")

    # Check for proactive trigger in description
    if 'description' in frontmatter:
        desc = frontmatter['description'].upper()
        if 'PROACTIVELY' not in desc and 'PROACTIVE' not in desc:
            issues.append("Description missing 'PROACTIVELY' trigger phrase (recommended for auto-delegation)")

    # Validate model if present
    if 'model' in frontmatter:
        if frontmatter['model'] not in VALID_MODELS:
            issues.append(f"Invalid model: '{frontmatter['model']}'. Valid: {', '.join(VALID_MODELS)}")

    # Validate permissionMode if present
    if 'permissionMode' in frontmatter:
        if frontmatter['permissionMode'] not in VALID_PERMISSION_MODES:
            issues.append(f"Invalid permissionMode: '{frontmatter['permissionMode']}'. Valid: {', '.join(VALID_PERMISSION_MODES)}")

    # Check registry metadata (project-specific extension, not required by Claude Code)
    registry = parse_registry_metadata(body)
    tiers = []
    if not registry:
        issues.append("[optional] Missing workflow-orchestrator-registry metadata (project-specific for workflow orchestrator)")
    else:
        if 'category' in registry:
            cat = registry['category']
            if cat not in VALID_CATEGORIES:
                issues.append(f"Invalid registry category: '{cat}'. Valid: {', '.join(VALID_CATEGORIES)}")
        # Parse tiers for naming validation
        if 'tiers' in registry:
            tiers_str = registry['tiers'].strip('[]')
            tiers = [int(t.strip()) for t in tiers_str.split(',') if t.strip().isdigit()]

    # Validate naming convention
    if 'name' in frontmatter:
        naming_issues = validate_naming_convention(frontmatter['name'], tiers)
        issues.extend(naming_issues)

    # Check prompt has content
    prompt_content = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL).strip()
    if len(prompt_content) < 50:
        issues.append("Agent prompt seems too short (< 50 chars after removing comments)")

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-agent.py <agent.md or directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_dir():
        files = list(target.glob('*.md'))
    else:
        files = [target]

    total_issues = 0

    for filepath in files:
        issues = validate_agent(filepath)
        if issues:
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
        else:
            print(f"{filepath}: OK")

    if total_issues > 0:
        print(f"\nTotal issues: {total_issues}")
        sys.exit(1)
    else:
        print("\nAll agents validated successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
