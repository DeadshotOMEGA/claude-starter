#!/usr/bin/env python3
"""
Trend Analysis Module

Generates ASCII graphs and statistics showing error patterns over time.
Helps identify whether fixes are working and which patterns are growing/shrinking.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Optional


def load_error_log() -> list[dict]:
    """Load all error entries from the log file."""
    log_file = Path.home() / '.claude' / 'logs' / 'error-learning.jsonl'

    if not log_file.exists():
        return []

    errors = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    errors.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return errors


def bucket_errors_by_day(errors: list[dict], days: int = 7) -> dict[str, Counter]:
    """
    Group errors by day for the last N days.

    Returns:
        dict mapping date string -> Counter of error types
    """
    cutoff = datetime.now() - timedelta(days=days)
    buckets = defaultdict(Counter)

    for error in errors:
        try:
            ts = datetime.fromisoformat(error['timestamp'])
            if ts >= cutoff:
                date_str = ts.strftime('%Y-%m-%d')
                buckets[date_str][error['error_type']] += 1
        except (KeyError, ValueError):
            continue

    return dict(buckets)


def calculate_trend(
    daily_buckets: dict[str, Counter],
    error_type: str,
    days: int = 7
) -> dict:
    """
    Calculate trend for a specific error type.

    Returns:
        dict with 'direction', 'change_pct', 'values'
    """
    # Get values for each day
    today = datetime.now()
    values = []

    for i in range(days - 1, -1, -1):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        count = daily_buckets.get(date_str, Counter()).get(error_type, 0)
        values.append(count)

    # Calculate trend direction
    first_half = sum(values[:len(values)//2]) or 1
    second_half = sum(values[len(values)//2:])

    if second_half > first_half:
        direction = 'increasing'
        change_pct = ((second_half - first_half) / first_half) * 100
    elif second_half < first_half:
        direction = 'decreasing'
        change_pct = ((first_half - second_half) / first_half) * 100
    else:
        direction = 'stable'
        change_pct = 0

    return {
        'direction': direction,
        'change_pct': round(change_pct, 1),
        'values': values
    }


def generate_ascii_bar(value: int, max_value: int, width: int = 20) -> str:
    """Generate an ASCII bar for a value."""
    if max_value == 0:
        return ''

    filled = int((value / max_value) * width)
    bar = '#' * filled + '-' * (width - filled)
    return f"[{bar}]"


def generate_sparkline(values: list[int]) -> str:
    """Generate a sparkline-style ASCII trend indicator."""
    if not values:
        return ''

    # Use simple block chars for sparkline
    blocks = [' ', '_', '.', '-', '=', '#']

    max_val = max(values) or 1
    min_val = min(values)
    range_val = max_val - min_val or 1

    sparkline = ''
    for v in values:
        idx = int((v - min_val) / range_val * (len(blocks) - 1))
        sparkline += blocks[idx]

    return sparkline


def generate_trend_graph(
    daily_buckets: dict[str, Counter],
    error_types: list[str],
    days: int = 7
) -> str:
    """
    Generate a multi-line ASCII trend graph.

    Example output:
    Error Trends (last 7 days)
    =============================

    edit_before_read   [##########----------] 5 total, decreasing (-40%)
                       _-.=##=-.

    file_not_found     [####----------------] 2 total, stable
                       __..--__
    """
    output = []
    output.append("Error Trends (last 7 days)")
    output.append("=" * 30)
    output.append("")

    today = datetime.now()

    for error_type in error_types:
        trend = calculate_trend(daily_buckets, error_type, days)
        total = sum(trend['values'])

        # Direction indicator
        if trend['direction'] == 'increasing':
            direction_str = f"increasing (+{trend['change_pct']}%)"
        elif trend['direction'] == 'decreasing':
            direction_str = f"decreasing (-{trend['change_pct']}%)"
        else:
            direction_str = "stable"

        # Bar graph
        max_total = max(sum(calculate_trend(daily_buckets, et, days)['values'])
                        for et in error_types) or 1
        bar = generate_ascii_bar(total, max_total)

        # Sparkline
        sparkline = generate_sparkline(trend['values'])

        # Format output
        label = error_type.ljust(20)
        output.append(f"{label} {bar} {total} total, {direction_str}")
        output.append(f"{'':20} {sparkline}")
        output.append("")

    return '\n'.join(output)


def generate_summary_stats(errors: list[dict]) -> dict:
    """Generate summary statistics."""
    if not errors:
        return {
            'total': 0,
            'recovered': 0,
            'recovery_rate': 0,
            'most_common': [],
            'sessions': 0
        }

    total = len(errors)
    recovered = sum(1 for e in errors if e.get('is_recovered', False))
    recovery_rate = (recovered / total * 100) if total > 0 else 0

    type_counts = Counter(e['error_type'] for e in errors)
    sessions = len(set(e.get('session_id', 'unknown') for e in errors))

    return {
        'total': total,
        'recovered': recovered,
        'recovery_rate': round(recovery_rate, 1),
        'most_common': type_counts.most_common(5),
        'sessions': sessions
    }


def format_stats_report(stats: dict, trend_graph: str) -> str:
    """Format a complete statistics report."""
    output = []

    output.append("# Error Learning Report")
    output.append("")
    output.append("## Summary Statistics")
    output.append("")
    output.append(f"- **Total errors logged**: {stats['total']}")
    output.append(f"- **Recovered errors**: {stats['recovered']} ({stats['recovery_rate']}%)")
    output.append(f"- **Sessions affected**: {stats['sessions']}")
    output.append("")

    if stats['most_common']:
        output.append("## Most Common Errors")
        output.append("")
        for error_type, count in stats['most_common']:
            output.append(f"- **{error_type}**: {count} occurrences")
        output.append("")

    output.append(trend_graph)

    return '\n'.join(output)


if __name__ == '__main__':
    # Test with sample data
    sample_errors = [
        {'error_type': 'edit_before_read', 'timestamp': datetime.now().isoformat(), 'is_recovered': True},
        {'error_type': 'edit_before_read', 'timestamp': (datetime.now() - timedelta(days=1)).isoformat(), 'is_recovered': True},
        {'error_type': 'file_not_found', 'timestamp': datetime.now().isoformat(), 'is_recovered': False},
    ]

    # Mock data for testing
    buckets = bucket_errors_by_day(sample_errors)
    error_types = ['edit_before_read', 'file_not_found']

    print(generate_trend_graph(buckets, error_types))
