#!/usr/bin/env python3
"""
Error Learning Review Script

Analyzes the error log and generates an actionable report with:
- Summary statistics
- ASCII trend graphs
- Prioritized suggestions (impact-first)
- Ready-to-use configurations for CLAUDE.md, rules, and hooks
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# Import local modules
import sys
sys.path.insert(0, str(Path(__file__).parent))
from suggestions import generate_suggestions, format_suggestion_for_review
from trends import (
    load_error_log,
    bucket_errors_by_day,
    generate_trend_graph,
    generate_summary_stats,
    format_stats_report
)


def filter_errors(
    errors: list[dict],
    since_date: datetime = None,
    error_type: str = None,
    recovered_only: bool = True
) -> list[dict]:
    """Filter errors by various criteria."""
    filtered = errors

    if since_date:
        filtered = [
            e for e in filtered
            if datetime.fromisoformat(e['timestamp']) >= since_date
        ]

    if error_type:
        filtered = [
            e for e in filtered
            if e['error_type'] == error_type
        ]

    if recovered_only:
        filtered = [
            e for e in filtered
            if e.get('is_recovered', False)
        ]

    return filtered


def calculate_impact_scores(errors: list[dict]) -> dict[str, float]:
    """Calculate average impact score per error type."""
    scores = {}
    counts = Counter()

    for error in errors:
        error_type = error['error_type']
        impact = error.get('impact_score', 0.5)
        scores[error_type] = scores.get(error_type, 0) + impact
        counts[error_type] += 1

    # Average
    for error_type in scores:
        scores[error_type] /= counts[error_type]

    return scores


def generate_full_report(
    errors: list[dict],
    days: int = 7,
    show_context: bool = False
) -> str:
    """Generate the complete review report."""
    output = []

    # Summary stats
    stats = generate_summary_stats(errors)

    # Trend graph
    error_types = [et for et, _ in stats['most_common']]
    daily_buckets = bucket_errors_by_day(errors, days)
    trend_graph = generate_trend_graph(daily_buckets, error_types, days)

    # Header
    output.append(format_stats_report(stats, trend_graph))
    output.append("")

    # Suggestions
    error_counts = Counter(e['error_type'] for e in errors)
    impact_scores = calculate_impact_scores(errors)
    suggestions = generate_suggestions(error_counts, impact_scores)

    if suggestions:
        output.append("## Recommended Actions (Impact-Prioritized)")
        output.append("")
        output.append("The following suggestions are ordered by impact - errors that blocked tasks come first.")
        output.append("")

        for i, suggestion in enumerate(suggestions[:10], 1):  # Top 10
            output.append(f"---")
            output.append("")
            output.append(format_suggestion_for_review(suggestion))

    # Context examples if requested
    if show_context and errors:
        output.append("---")
        output.append("")
        output.append("## Recent Error Examples")
        output.append("")

        # Group by type, show most recent for each
        seen_types = set()
        for error in reversed(errors):  # Most recent first
            if error['error_type'] not in seen_types:
                seen_types.add(error['error_type'])
                output.append(f"### {error['error_type']}")
                output.append("")
                output.append(f"**Message**: {error['message']}")
                output.append(f"**Recovery**: {error.get('recovery_method', 'unknown')}")
                output.append(f"**Fix applied**: {error.get('fix_applied', 'unknown')}")
                output.append("")
                if error.get('context'):
                    output.append("```")
                    output.append(error['context'][:300])
                    output.append("```")
                    output.append("")

            if len(seen_types) >= 5:  # Limit examples
                break

    return '\n'.join(output)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Review error learning log and get improvement suggestions'
    )
    parser.add_argument(
        '--since',
        type=str,
        help='Only show errors since date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--type',
        type=str,
        help='Filter by specific error type'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days for trend analysis (default: 7)'
    )
    parser.add_argument(
        '--show-context',
        action='store_true',
        help='Show full error context examples'
    )
    parser.add_argument(
        '--include-unrecovered',
        action='store_true',
        help='Include unrecovered errors (default: recovered only)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    # Load errors
    errors = load_error_log()

    if not errors:
        print("No errors logged yet.")
        print("")
        print("The error learning hook tracks recovered errors as they occur.")
        print("Once you have some logged errors, run this command again to see suggestions.")
        return

    # Filter
    since_date = None
    if args.since:
        since_date = datetime.fromisoformat(args.since)

    filtered = filter_errors(
        errors,
        since_date=since_date,
        error_type=args.type,
        recovered_only=not args.include_unrecovered
    )

    if not filtered:
        print("No errors match the specified filters.")
        return

    # Generate report
    if args.json:
        stats = generate_summary_stats(filtered)
        error_counts = Counter(e['error_type'] for e in filtered)
        impact_scores = calculate_impact_scores(filtered)
        suggestions = generate_suggestions(error_counts, impact_scores)

        output = {
            'stats': stats,
            'suggestions': [
                {
                    'error_type': s.error_type,
                    'target': s.target,
                    'priority': s.priority,
                    'title': s.title,
                    'description': s.description,
                    'frequency': s.frequency
                }
                for s in suggestions
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        report = generate_full_report(
            filtered,
            days=args.days,
            show_context=args.show_context
        )
        print(report)


if __name__ == '__main__':
    main()
