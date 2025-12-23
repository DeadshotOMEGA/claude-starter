#!/usr/bin/env python3
"""
Error Learning Hook (UserPromptSubmit)

Monitors the transcript for errors that occurred and were recovered from.
Only logs errors where Claude successfully found a fix - these are learning opportunities.
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Import local modules
sys.path.insert(0, str(Path(__file__).parent))
from recovery import analyze_recovery


def load_patterns() -> list[dict]:
    """Load error patterns from config."""
    config_path = Path(__file__).parent / 'patterns.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
            return data.get('patterns', [])
    return []


def load_transcript(transcript_path: str) -> str:
    """Load transcript file content."""
    if not Path(transcript_path).exists():
        return ""

    with open(transcript_path, 'r', encoding='utf-8') as f:
        return f.read()


def find_last_user_prompt_index(lines: list[str]) -> int:
    """Find the index of the last user prompt in transcript."""
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].lower()
        if '<|user|>' in line or 'human:' in line or 'user:' in line:
            return i
    return 0


def scan_for_errors(transcript: str, patterns: list[dict]) -> list[dict]:
    """
    Scan transcript for error patterns since last user prompt.

    Returns list of detected errors with:
    - type: error pattern ID
    - line_idx: line number in transcript
    - message: the error message
    - context: surrounding lines
    """
    lines = transcript.split('\n')
    last_user_idx = find_last_user_prompt_index(lines)

    # Only scan from second-to-last user prompt to last user prompt
    # (errors that happened in the previous turn)
    prev_user_idx = 0
    user_count = 0
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].lower()
        if '<|user|>' in line or 'human:' in line or 'user:' in line:
            user_count += 1
            if user_count == 2:
                prev_user_idx = i
                break

    search_window = lines[prev_user_idx:last_user_idx]
    errors = []

    for i, line in enumerate(search_window):
        for pattern in patterns:
            if re.search(pattern['pattern'], line, re.IGNORECASE):
                # Get context (3 lines before and after)
                start = max(0, i - 3)
                end = min(len(search_window), i + 4)
                context = '\n'.join(search_window[start:end])

                errors.append({
                    'type': pattern['id'],
                    'severity': pattern.get('severity', 'medium'),
                    'line_idx': prev_user_idx + i,
                    'message': line.strip()[:200],  # Truncate long lines
                    'context': context[:500],  # Limit context size
                    'suggestion_target': pattern.get('suggestion_target', 'claudemd'),
                    'suggestion_template': pattern.get('suggestion_template', '')
                })
                break  # One pattern per line

    return errors


def filter_recovered_errors(
    errors: list[dict],
    transcript_lines: list[str]
) -> list[dict]:
    """Filter to only errors that were recovered from."""
    recovered = []

    for error in errors:
        result = analyze_recovery(
            error['line_idx'],
            error['type'],
            transcript_lines
        )

        if result.is_recovered:
            error['is_recovered'] = True
            error['recovery_method'] = result.method
            error['recovery_confidence'] = result.confidence
            error['fix_applied'] = result.fix_applied
            recovered.append(error)

    return recovered


def calculate_impact_score(error: dict) -> float:
    """
    Calculate impact score (0-1) for prioritization.

    Higher scores = more impactful errors (blocked tasks)
    """
    score = 0.5  # Base score

    # Severity adjustments
    if error.get('severity') == 'high':
        score += 0.2
    elif error.get('severity') == 'low':
        score -= 0.1

    # Recovery confidence (lower confidence = higher impact, harder to fix)
    confidence = error.get('recovery_confidence', 0.5)
    score += (1 - confidence) * 0.2

    return min(1.0, max(0.0, score))


def log_errors(errors: list[dict], session_id: str) -> None:
    """Append errors to the learning log."""
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / 'error-learning.jsonl'

    with open(log_file, 'a', encoding='utf-8') as f:
        for error in errors:
            entry = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'error_type': error['type'],
                'severity': error.get('severity', 'medium'),
                'message': error['message'],
                'context': error.get('context', ''),
                'is_recovered': error.get('is_recovered', False),
                'recovery_method': error.get('recovery_method'),
                'recovery_confidence': error.get('recovery_confidence'),
                'fix_applied': error.get('fix_applied'),
                'impact_score': calculate_impact_score(error),
                'suggestion_target': error.get('suggestion_target'),
                'suggestion_template': error.get('suggestion_template')
            }
            f.write(json.dumps(entry) + '\n')


def main():
    """Main hook execution."""
    try:
        # Read hook input from stdin
        stdin_content = sys.stdin.read()
        if not stdin_content.strip():
            sys.exit(0)  # No input, exit silently

        input_data = json.loads(stdin_content)

        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path')

        if not transcript_path:
            sys.exit(0)

        # Load transcript
        transcript = load_transcript(transcript_path)
        if not transcript:
            sys.exit(0)

        # Load patterns
        patterns = load_patterns()
        if not patterns:
            sys.exit(0)

        # Scan for errors
        errors = scan_for_errors(transcript, patterns)

        if not errors:
            sys.exit(0)

        # Filter to only recovered errors
        transcript_lines = transcript.split('\n')
        recovered_errors = filter_recovered_errors(errors, transcript_lines)

        if recovered_errors:
            # Log for learning
            log_errors(recovered_errors, session_id)

            # Notify user if verbose mode
            if os.environ.get('CLAUDE_ERROR_LEARNING_VERBOSE') == '1':
                output = {
                    'systemMessage': f'Logged {len(recovered_errors)} recovered error(s) for learning. Run /review-errors to see suggestions.'
                }
                print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Always notify on hook failure (user requested this)
        output = {
            'systemMessage': f'Error learning hook failed: {str(e)[:100]}'
        }
        print(json.dumps(output))
        sys.exit(0)  # Don't block prompt


if __name__ == '__main__':
    main()
