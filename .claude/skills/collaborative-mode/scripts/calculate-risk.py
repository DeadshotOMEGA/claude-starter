#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate risk level based on discovered files and signals.

Usage:
    python calculate-risk.py --files "file1.ts,file2.ts,file3.ts"
    python calculate-risk.py --files "file1.ts" --signals "schema_changes,security_changes"
    echo '{"files": [...], "signals": [...]}' | python calculate-risk.py --json

Output:
    JSON with risk assessment:
    {
        "risk_level": "HIGH",
        "file_count": 12,
        "signals_detected": ["file_count", "schema_changes"],
        "reasoning": "..."
    }
"""

import argparse
import json
import os
import sys
from pathlib import Path


# Risk signals from config (embedded for standalone execution)
HIGH_SIGNALS = {
    "file_count": {"condition": "10+ files", "check": lambda ctx: ctx.get("file_count", 0) >= 10},
    "core_utilities": {"condition": "modifies shared/core utilities"},
    "schema_changes": {"condition": "database migrations or schema modifications"},
    "breaking_api": {"condition": "non-backwards-compatible API changes"},
    "security_changes": {"condition": "auth, authorization, or sensitive data"},
    "major_refactor": {"condition": "restructures existing patterns"},
    "data_migration": {"condition": "migrating existing production data"},
    "external_service_changes": {"condition": "third-party service integration changes"},
}

MODERATE_SIGNALS = {
    "medium_file_count": {"condition": "5-9 files", "check": lambda ctx: 5 <= ctx.get("file_count", 0) <= 9},
    "multi_module": {"condition": "touches multiple modules"},
    "new_feature_integration": {"condition": "new feature integrating with existing code"},
    "state_management": {"condition": "modifies global/shared state"},
    "test_updates": {"condition": "updating multiple test files"},
    "config_changes": {"condition": "env vars, config files, feature flags"},
    "performance_sensitive": {"condition": "performance-critical code paths"},
}

# File patterns that indicate risk
RISKY_PATH_PATTERNS = {
    "HIGH": [
        "migrations/",
        "schema",
        "auth",
        "security",
        "core/",
        "shared/",
        "lib/",
        "utils/",
    ],
    "MODERATE": [
        "config",
        "state",
        "store",
        "context",
        ".env",
        "test",
        "spec",
    ]
}


def analyze_files(files: list[str]) -> dict:
    """Analyze file list for risk signals."""
    file_count = len(files)
    signals_detected = []

    # Check file count thresholds
    if file_count >= 10:
        signals_detected.append(("HIGH", "file_count", f"{file_count} files affected"))
    elif file_count >= 5:
        signals_detected.append(("MODERATE", "medium_file_count", f"{file_count} files affected"))

    # Check file paths for risky patterns
    for file_path in files:
        path_lower = file_path.lower()

        for pattern in RISKY_PATH_PATTERNS["HIGH"]:
            if pattern in path_lower:
                signal_id = f"path_{pattern.replace('/', '')}"
                signals_detected.append(("HIGH", signal_id, f"Touches {pattern}: {file_path}"))
                break

        for pattern in RISKY_PATH_PATTERNS["MODERATE"]:
            if pattern in path_lower:
                signal_id = f"path_{pattern.replace('/', '')}"
                signals_detected.append(("MODERATE", signal_id, f"Touches {pattern}: {file_path}"))
                break

    return {
        "file_count": file_count,
        "signals": signals_detected
    }


def analyze_explicit_signals(signals: list[str]) -> list[tuple]:
    """Analyze explicitly provided signals."""
    detected = []

    for signal in signals:
        signal_lower = signal.lower().strip()

        if signal_lower in HIGH_SIGNALS:
            detected.append(("HIGH", signal_lower, HIGH_SIGNALS[signal_lower]["condition"]))
        elif signal_lower in MODERATE_SIGNALS:
            detected.append(("MODERATE", signal_lower, MODERATE_SIGNALS[signal_lower]["condition"]))

    return detected


def calculate_risk(files: list[str], explicit_signals: list[str] = None) -> dict:
    """
    Calculate overall risk level.

    Rules:
    - Any HIGH signal = HIGH risk
    - 3+ MODERATE signals = HIGH risk
    - Any MODERATE signal = MODERATE risk
    - Otherwise = LOW risk
    """
    all_signals = []

    # Analyze files
    file_analysis = analyze_files(files)
    all_signals.extend(file_analysis["signals"])

    # Add explicit signals
    if explicit_signals:
        all_signals.extend(analyze_explicit_signals(explicit_signals))

    # Deduplicate signals
    seen = set()
    unique_signals = []
    for signal in all_signals:
        key = (signal[0], signal[1])
        if key not in seen:
            seen.add(key)
            unique_signals.append(signal)

    # Count by level
    high_count = sum(1 for s in unique_signals if s[0] == "HIGH")
    moderate_count = sum(1 for s in unique_signals if s[0] == "MODERATE")

    # Determine risk level
    if high_count > 0:
        risk_level = "HIGH"
        reasoning = f"{high_count} high-risk signal(s) detected"
    elif moderate_count >= 3:
        risk_level = "HIGH"
        reasoning = f"{moderate_count} moderate signals (3+ triggers HIGH)"
    elif moderate_count > 0:
        risk_level = "MODERATE"
        reasoning = f"{moderate_count} moderate-risk signal(s) detected"
    else:
        risk_level = "LOW"
        reasoning = "No significant risk signals detected"

    return {
        "risk_level": risk_level,
        "file_count": file_analysis["file_count"],
        "high_signals": high_count,
        "moderate_signals": moderate_count,
        "signals_detected": [
            {"level": s[0], "id": s[1], "reason": s[2]}
            for s in unique_signals
        ],
        "reasoning": reasoning
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate risk level for collaborative mode")
    parser.add_argument("--files", type=str, help="Comma-separated list of files")
    parser.add_argument("--signals", type=str, help="Comma-separated list of explicit signals")
    parser.add_argument("--json", action="store_true", help="Read JSON input from stdin")

    args = parser.parse_args()

    files = []
    explicit_signals = []

    if args.json:
        # Read JSON from stdin
        try:
            data = json.load(sys.stdin)
            files = data.get("files", [])
            explicit_signals = data.get("signals", [])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.exit(1)
    else:
        if args.files:
            files = [f.strip() for f in args.files.split(",") if f.strip()]
        if args.signals:
            explicit_signals = [s.strip() for s in args.signals.split(",") if s.strip()]

    result = calculate_risk(files, explicit_signals)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
