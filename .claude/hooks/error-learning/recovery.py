#!/usr/bin/env python3
"""
Recovery Detection Module

Detects when errors were successfully recovered from using multiple signals:
1. Success after failure - same operation type succeeds after failing
2. Self-correction language - Claude says "let me try...", "instead I'll..."
3. Task completion - overall task completes despite errors
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class RecoveryResult:
    """Result of recovery detection analysis."""
    is_recovered: bool
    method: Optional[str]  # 'success_after_failure', 'self_correction', 'task_completion'
    confidence: float  # 0.0 to 1.0
    fix_applied: Optional[str]  # What action fixed the error


def load_recovery_config() -> dict:
    """Load recovery signal configuration."""
    config_path = Path(__file__).parent / 'patterns.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
            return data.get('recovery_signals', {})
    return {}


def detect_success_after_failure(
    error_line_idx: int,
    error_type: str,
    transcript_lines: list[str]
) -> Optional[RecoveryResult]:
    """
    Detect if the same operation succeeded after failing.

    Looks for:
    - Tool success after tool failure
    - File read success after file not found
    - Command success after command failure
    """
    # Map error types to success patterns
    success_patterns = {
        'file_not_found': [
            r'File.*read successfully',
            r'successfully read',
            r'<file_contents>',
        ],
        'permission_denied': [
            r'successfully.*wrote',
            r'File created successfully',
            r'completed successfully',
        ],
        'edit_before_read': [
            r'<file_contents>',  # Read happened
            r'has been updated',  # Then edit succeeded
        ],
        'command_not_found': [
            r'Tool ran without output or errors',
            r'exit code 0',
        ],
    }

    patterns = success_patterns.get(error_type, [r'successfully', r'completed'])

    # Look in lines after the error
    search_window = transcript_lines[error_line_idx + 1:error_line_idx + 50]

    for i, line in enumerate(search_window):
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return RecoveryResult(
                    is_recovered=True,
                    method='success_after_failure',
                    confidence=0.8,
                    fix_applied=f"Operation succeeded on retry (line +{i+1})"
                )

    return None


def detect_self_correction(
    error_line_idx: int,
    transcript_lines: list[str]
) -> Optional[RecoveryResult]:
    """
    Detect if Claude used self-correction language after the error.

    Looks for phrases like:
    - "let me try..."
    - "instead I'll..."
    - "I should read first"
    """
    config = load_recovery_config()
    correction_patterns = config.get('self_correction_language', {}).get('patterns', [
        'let me try',
        'instead I\'ll',
        'let me use',
        'I\'ll try a different',
        'let me read.*first',
        'I should read',
        'I need to read',
    ])

    # Look in lines after the error (Claude's response)
    search_window = transcript_lines[error_line_idx + 1:error_line_idx + 20]

    for i, line in enumerate(search_window):
        for pattern in correction_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Extract what action was taken
                fix_applied = line.strip()[:100]  # First 100 chars
                return RecoveryResult(
                    is_recovered=True,
                    method='self_correction',
                    confidence=0.7,
                    fix_applied=fix_applied
                )

    return None


def detect_task_completion(
    error_line_idx: int,
    transcript_lines: list[str]
) -> Optional[RecoveryResult]:
    """
    Detect if the overall task completed despite the error.

    Looks for:
    - Task completion indicators
    - User satisfaction signals
    - Successful output delivery
    """
    completion_patterns = [
        r'task.*complete',
        r'successfully.*implemented',
        r'changes.*applied',
        r'done!',
        r'finished',
        r'all.*complete',
        r'created.*successfully',
        r'updated.*successfully',
    ]

    # Look towards end of transcript (task completion usually at end)
    search_window = transcript_lines[error_line_idx + 1:]

    for i, line in enumerate(search_window):
        for pattern in completion_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return RecoveryResult(
                    is_recovered=True,
                    method='task_completion',
                    confidence=0.6,
                    fix_applied="Task completed successfully despite error"
                )

    return None


def analyze_recovery(
    error_line_idx: int,
    error_type: str,
    transcript_lines: list[str]
) -> RecoveryResult:
    """
    Analyze whether an error was recovered from using all detection methods.

    Combines signals with weighted confidence:
    - Success after failure: 0.4 weight
    - Self-correction: 0.3 weight
    - Task completion: 0.3 weight
    """
    results = []

    # Try each detection method
    success_result = detect_success_after_failure(error_line_idx, error_type, transcript_lines)
    if success_result:
        results.append(success_result)

    correction_result = detect_self_correction(error_line_idx, transcript_lines)
    if correction_result:
        results.append(correction_result)

    completion_result = detect_task_completion(error_line_idx, transcript_lines)
    if completion_result:
        results.append(completion_result)

    if not results:
        return RecoveryResult(
            is_recovered=False,
            method=None,
            confidence=0.0,
            fix_applied=None
        )

    # Combine results - use highest confidence method
    best_result = max(results, key=lambda r: r.confidence)

    # Boost confidence if multiple methods agree
    if len(results) > 1:
        best_result.confidence = min(1.0, best_result.confidence + 0.1 * (len(results) - 1))

    return best_result


if __name__ == '__main__':
    # Test with sample data
    sample_lines = [
        "User: Please edit the file",
        "Error: Edit tool requires prior Read",
        "Let me read the file first",
        "File contents: ...",
        "Now I'll edit the file",
        "File has been updated successfully"
    ]

    result = analyze_recovery(1, 'edit_before_read', sample_lines)
    print(f"Recovered: {result.is_recovered}")
    print(f"Method: {result.method}")
    print(f"Confidence: {result.confidence}")
    print(f"Fix: {result.fix_applied}")
