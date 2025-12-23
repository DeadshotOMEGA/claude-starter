#!/usr/bin/env python3
"""
Validate CLAUDE.md and rules files for correctness.

Features:
- Parse YAML frontmatter (check for --- delimiters)
- Validate `paths` field glob patterns
- Check @import references exist
- Detect import depth (warn if >3, error if >5)
- Detect circular imports
- Report issues with line numbers

Usage: python validate.py <path-to-file-or-directory>

Output: JSON with validation results
"""

import json
import re
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import TypedDict


class ValidationIssue(TypedDict):
    file: str
    line: int | None
    message: str
    severity: str  # "error" | "warning"


class ValidationResult(TypedDict):
    valid: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]


def parse_frontmatter(content: str) -> tuple[dict[str, str | list[str]], int, int]:
    """
    Parse YAML frontmatter from content.
    Returns (frontmatter_dict, start_line, end_line).
    Raises ValueError if frontmatter is invalid.
    """
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return {}, 0, 0

    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        raise ValueError("Unclosed frontmatter: missing closing '---'")

    frontmatter: dict[str, str | list[str]] = {}
    yaml_lines = lines[1:end_index]

    for i, line in enumerate(yaml_lines):
        line_num = i + 2  # Account for first ---
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Handle arrays
        if value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            frontmatter[key] = [item.strip().strip("\"'") for item in items if item.strip()]
        elif value.startswith('"') and value.endswith('"'):
            frontmatter[key] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            frontmatter[key] = value[1:-1]
        else:
            frontmatter[key] = value

    return frontmatter, 1, end_index + 1


def validate_glob_pattern(pattern: str) -> bool:
    """Check if a glob pattern is syntactically valid."""
    # Basic validation - check for common issues
    if not pattern:
        return False

    # Check for unbalanced brackets
    bracket_count = 0
    for char in pattern:
        if char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1
        if bracket_count < 0:
            return False

    if bracket_count != 0:
        return False

    # Check for invalid sequences
    if "***" in pattern:
        return False

    return True


def find_imports(content: str) -> list[tuple[int, str]]:
    """
    Find all @import references in content.
    Returns list of (line_number, import_path).
    """
    imports: list[tuple[int, str]] = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Match @import("path") or @import('path')
        matches = re.findall(r'@import\s*\(\s*["\']([^"\']+)["\']\s*\)', line)
        for match in matches:
            imports.append((i + 1, match))

    return imports


def resolve_import_path(import_path: str, base_file: Path, project_root: Path) -> Path | None:
    """Resolve an import path relative to the base file or project root."""
    # Try relative to base file first
    relative_path = base_file.parent / import_path
    if relative_path.exists():
        return relative_path.resolve()

    # Try relative to project root
    root_path = project_root / import_path
    if root_path.exists():
        return root_path.resolve()

    # Try with .md extension
    for path in [relative_path, root_path]:
        with_md = path.with_suffix(".md")
        if with_md.exists():
            return with_md.resolve()

    return None


def check_import_depth(
    file_path: Path,
    project_root: Path,
    visited: set[Path] | None = None,
    depth: int = 0
) -> tuple[int, list[Path]]:
    """
    Recursively check import depth.
    Returns (max_depth, import_chain).
    """
    if visited is None:
        visited = set()

    resolved_path = file_path.resolve()

    if resolved_path in visited:
        # Circular import detected - return current depth
        return depth, [resolved_path]

    visited.add(resolved_path)

    if not file_path.exists():
        return depth, [resolved_path]

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return depth, [resolved_path]

    imports = find_imports(content)
    max_depth = depth
    deepest_chain = [resolved_path]

    for _, import_path in imports:
        resolved_import = resolve_import_path(import_path, file_path, project_root)
        if resolved_import:
            sub_depth, sub_chain = check_import_depth(
                resolved_import, project_root, visited.copy(), depth + 1
            )
            if sub_depth > max_depth:
                max_depth = sub_depth
                deepest_chain = [resolved_path] + sub_chain

    return max_depth, deepest_chain


def detect_circular_imports(
    file_path: Path,
    project_root: Path,
    visited: list[Path] | None = None
) -> list[Path] | None:
    """
    Detect circular imports starting from file_path.
    Returns the cycle path if found, None otherwise.
    """
    if visited is None:
        visited = []

    resolved_path = file_path.resolve()

    if resolved_path in visited:
        # Found a cycle - return the path from the cycle start
        cycle_start = visited.index(resolved_path)
        return visited[cycle_start:] + [resolved_path]

    visited.append(resolved_path)

    if not file_path.exists():
        return None

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    imports = find_imports(content)

    for _, import_path in imports:
        resolved_import = resolve_import_path(import_path, file_path, project_root)
        if resolved_import:
            cycle = detect_circular_imports(resolved_import, project_root, visited.copy())
            if cycle:
                return cycle

    return None


def validate_file(file_path: Path, project_root: Path) -> ValidationResult:
    """Validate a single CLAUDE.md or rules file."""
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if not file_path.exists():
        errors.append({
            "file": str(file_path),
            "line": None,
            "message": "File does not exist",
            "severity": "error"
        })
        return {"valid": False, "errors": errors, "warnings": warnings}

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append({
            "file": str(file_path),
            "line": None,
            "message": f"Failed to read file: {e}",
            "severity": "error"
        })
        return {"valid": False, "errors": errors, "warnings": warnings}

    str_path = str(file_path)

    # Parse frontmatter
    try:
        frontmatter, fm_start, fm_end = parse_frontmatter(content)
    except ValueError as e:
        errors.append({
            "file": str_path,
            "line": 1,
            "message": str(e),
            "severity": "error"
        })
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Validate paths field glob patterns
    paths = frontmatter.get("paths")
    if paths:
        if isinstance(paths, str):
            paths = [paths]

        for pattern in paths:
            if not validate_glob_pattern(pattern):
                errors.append({
                    "file": str_path,
                    "line": fm_start,
                    "message": f"Invalid glob pattern in paths: '{pattern}'",
                    "severity": "error"
                })

    # Check @import references
    imports = find_imports(content)
    for line_num, import_path in imports:
        resolved = resolve_import_path(import_path, file_path, project_root)
        if not resolved:
            errors.append({
                "file": str_path,
                "line": line_num,
                "message": f"Import reference not found: '{import_path}'",
                "severity": "error"
            })

    # Check import depth
    max_depth, chain = check_import_depth(file_path, project_root)
    if max_depth > 5:
        errors.append({
            "file": str_path,
            "line": None,
            "message": f"Import depth ({max_depth}) exceeds maximum of 5. Chain: {' -> '.join(p.name for p in chain)}",
            "severity": "error"
        })
    elif max_depth > 3:
        warnings.append({
            "file": str_path,
            "line": None,
            "message": f"Import depth ({max_depth}) exceeds recommended maximum of 3. Chain: {' -> '.join(p.name for p in chain)}",
            "severity": "warning"
        })

    # Detect circular imports
    cycle = detect_circular_imports(file_path, project_root)
    if cycle:
        cycle_str = " -> ".join(p.name for p in cycle)
        errors.append({
            "file": str_path,
            "line": None,
            "message": f"Circular import detected: {cycle_str}",
            "severity": "error"
        })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_directory(dir_path: Path) -> ValidationResult:
    """Validate all memory/rules files in a directory."""
    all_errors: list[ValidationIssue] = []
    all_warnings: list[ValidationIssue] = []

    # Find project root (directory containing .claude or the directory itself)
    project_root = dir_path
    if (dir_path / ".claude").exists():
        project_root = dir_path
    elif dir_path.name == ".claude":
        project_root = dir_path.parent
    else:
        # Walk up to find project root
        for parent in dir_path.parents:
            if (parent / ".claude").exists():
                project_root = parent
                break

    # Find all relevant files
    patterns = ["CLAUDE.md", "CLAUDE.local.md"]
    files_to_check: list[Path] = []

    # Check for CLAUDE.md files
    for pattern in patterns:
        files_to_check.extend(dir_path.rglob(pattern))

    # Check for rules directory
    rules_dir = dir_path / ".claude" / "rules" if (dir_path / ".claude").exists() else dir_path / "rules"
    if rules_dir.exists():
        files_to_check.extend(rules_dir.rglob("*.md"))

    # Also check if dir_path itself is a .claude directory
    if dir_path.name == ".claude":
        rules_in_claude = dir_path / "rules"
        if rules_in_claude.exists():
            files_to_check.extend(rules_in_claude.rglob("*.md"))

    # Validate each file
    for file_path in files_to_check:
        result = validate_file(file_path, project_root)
        all_errors.extend(result["errors"])
        all_warnings.extend(result["warnings"])

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings
    }


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python validate.py <path-to-file-or-directory>", file=sys.stderr)
        sys.exit(1)

    target_path = Path(sys.argv[1]).resolve()

    if target_path.is_file():
        # Find project root
        project_root = target_path.parent
        for parent in target_path.parents:
            if (parent / ".claude").exists():
                project_root = parent
                break
        result = validate_file(target_path, project_root)
    elif target_path.is_dir():
        result = validate_directory(target_path)
    else:
        result: ValidationResult = {
            "valid": False,
            "errors": [{
                "file": str(target_path),
                "line": None,
                "message": "Path does not exist",
                "severity": "error"
            }],
            "warnings": []
        }

    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
