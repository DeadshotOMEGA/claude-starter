#!/usr/bin/env python3
"""
Suggestion Generator Module

Generates actionable suggestions for preventing future errors.
Outputs target-specific formats:
- CLAUDE.md: Memory file additions
- .claude/rules/: Rule file content
- settings.json: Hook configurations
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from collections import Counter


@dataclass
class Suggestion:
    """A prevention suggestion."""
    error_type: str
    target: str  # 'claudemd', 'rule', 'hook'
    priority: int
    title: str
    description: str
    content: str  # Ready-to-use content
    frequency: int  # How often this error occurred


def load_patterns() -> dict:
    """Load pattern configuration."""
    config_path = Path(__file__).parent / 'patterns.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {'patterns': [], 'suggestion_targets': {}}


def generate_claudemd_suggestion(pattern: dict, frequency: int) -> Suggestion:
    """Generate a CLAUDE.md memory addition."""
    template = pattern.get('suggestion_template', 'Address this error pattern')

    content = f"""## {pattern['description']}

**Pattern**: {pattern['id']}

{template}

Example error:
```
{pattern['pattern']}
```
"""

    return Suggestion(
        error_type=pattern['id'],
        target='claudemd',
        priority=1,
        title=f"Add to CLAUDE.md: {pattern['description']}",
        description=f"Prevent '{pattern['id']}' errors ({frequency} occurrences)",
        content=content,
        frequency=frequency
    )


def generate_rule_suggestion(pattern: dict, frequency: int) -> Suggestion:
    """Generate a .claude/rules/ file content."""
    rule_name = pattern['id'].replace('_', '-')
    template = pattern.get('suggestion_template', 'Follow this pattern')

    content = f"""# {pattern['description'].title()}

## Rule

{template}

## When This Applies

This rule applies when {pattern['type']} errors occur.

## Pattern to Avoid

```
{pattern['pattern']}
```

## Best Practice

[Add specific guidance here]
"""

    return Suggestion(
        error_type=pattern['id'],
        target='rule',
        priority=2,
        title=f"Create rule: .claude/rules/{rule_name}.md",
        description=f"Prevent '{pattern['id']}' errors ({frequency} occurrences)",
        content=content,
        frequency=frequency
    )


def generate_hook_suggestion(pattern: dict, frequency: int) -> Suggestion:
    """Generate a settings.json hook configuration."""
    hook_type = 'PreToolUse'
    matcher = 'Read|Edit|Bash'  # Default

    # Customize based on error type
    if 'file' in pattern['type']:
        matcher = 'Read|Edit|Write'
    elif 'bash' in pattern['type']:
        matcher = 'Bash'
    elif 'permission' in pattern['type']:
        matcher = 'Write|Edit|Bash'

    config = {
        hook_type: [{
            'matcher': matcher,
            'hooks': [{
                'type': 'prompt',
                'prompt': f"Validate before operation to prevent {pattern['description']}. If invalid, return deny with explanation.",
                'timeout': 10
            }]
        }]
    }

    content = json.dumps(config, indent=2)

    return Suggestion(
        error_type=pattern['id'],
        target='hook',
        priority=3,
        title=f"Add hook: {pattern['description']}",
        description=f"Prevent '{pattern['id']}' errors ({frequency} occurrences)",
        content=content,
        frequency=frequency
    )


def generate_suggestions(error_counts: Counter, impact_scores: Optional[dict] = None) -> list[Suggestion]:
    """
    Generate prioritized suggestions based on error frequencies.

    Args:
        error_counts: Counter of error_type -> count
        impact_scores: Optional dict of error_type -> impact score (higher = blocked task)

    Returns:
        List of Suggestion objects, sorted by priority
    """
    config = load_patterns()
    patterns = {p['id']: p for p in config.get('patterns', [])}
    suggestions = []

    for error_type, count in error_counts.items():
        if error_type not in patterns:
            continue

        pattern = patterns[error_type]
        target = pattern.get('suggestion_target', 'claudemd')

        if target == 'claudemd':
            suggestion = generate_claudemd_suggestion(pattern, count)
        elif target == 'rule':
            suggestion = generate_rule_suggestion(pattern, count)
        elif target == 'hook':
            suggestion = generate_hook_suggestion(pattern, count)
        else:
            continue

        # Adjust priority based on impact if provided
        if impact_scores and error_type in impact_scores:
            # Lower priority number = higher priority
            # High impact errors get boosted
            impact = impact_scores[error_type]
            if impact > 0.7:
                suggestion.priority = 0  # Highest

        suggestions.append(suggestion)

    # Sort by priority (lower first), then by frequency (higher first)
    suggestions.sort(key=lambda s: (s.priority, -s.frequency))

    return suggestions


def format_suggestion_for_review(suggestion: Suggestion) -> str:
    """Format a suggestion for the review command output."""
    output = []
    output.append(f"### {suggestion.title}")
    output.append("")
    output.append(f"**Priority**: {'HIGH' if suggestion.priority <= 1 else 'MEDIUM' if suggestion.priority == 2 else 'LOW'}")
    output.append(f"**Occurrences**: {suggestion.frequency}")
    output.append("")
    output.append(suggestion.description)
    output.append("")
    output.append("**Ready-to-use content:**")
    output.append("")

    if suggestion.target == 'hook':
        output.append("```json")
    else:
        output.append("```markdown")

    output.append(suggestion.content)
    output.append("```")
    output.append("")

    return '\n'.join(output)


if __name__ == '__main__':
    # Test with sample data
    test_counts = Counter({
        'edit_before_read': 5,
        'file_not_found': 3,
        'permission_denied': 2
    })

    suggestions = generate_suggestions(test_counts)

    for s in suggestions:
        print(format_suggestion_for_review(s))
        print("---")
