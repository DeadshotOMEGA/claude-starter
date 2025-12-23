#!/usr/bin/env python3
"""
Audit existing memory/rules for issues.

Features:
- Scan all memory files (CLAUDE.md, CLAUDE.local.md, .claude/rules/*.md)
- Detect conflicts: contradictory rules across files
- Detect duplication: same content in multiple files
- Detect stale references: paths to files that don't exist
- Suggest coverage gaps: common patterns not documented

Usage: python audit.py [--path <project-root>]

Output: Markdown report with findings organized by severity
"""

import argparse
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple


class Finding(NamedTuple):
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    category: str
    title: str
    description: str
    files: list[str]
    suggestion: str | None = None


# Common patterns to check for coverage
COVERAGE_PATTERNS = {
    "package.json": {
        "check": lambda p: (p / "package.json").exists(),
        "docs_keywords": ["npm", "package.json", "scripts", "dependencies"],
        "suggestion": "Document npm scripts and key dependencies in CLAUDE.md",
    },
    "tsconfig.json": {
        "check": lambda p: (p / "tsconfig.json").exists(),
        "docs_keywords": ["typescript", "tsconfig", "strict", "paths"],
        "suggestion": "Document TypeScript configuration choices in CLAUDE.md",
    },
    ".env": {
        "check": lambda p: any(p.glob(".env*")),
        "docs_keywords": ["environment", ".env", "secrets", "configuration"],
        "suggestion": "Document required environment variables (without values) in CLAUDE.md",
    },
    "docker": {
        "check": lambda p: (p / "Dockerfile").exists() or (p / "docker-compose.yml").exists(),
        "docs_keywords": ["docker", "container", "compose"],
        "suggestion": "Document Docker setup and common commands in CLAUDE.md",
    },
    "database": {
        "check": lambda p: any([
            (p / "prisma").exists(),
            any(p.glob("**/migrations/**")),
            (p / "drizzle.config.ts").exists(),
        ]),
        "docs_keywords": ["database", "migration", "schema", "prisma", "drizzle"],
        "suggestion": "Document database schema and migration workflow in CLAUDE.md",
    },
    "testing": {
        "check": lambda p: any([
            (p / "jest.config.js").exists(),
            (p / "jest.config.ts").exists(),
            (p / "vitest.config.ts").exists(),
            any(p.glob("**/*.test.*")),
            any(p.glob("**/*.spec.*")),
        ]),
        "docs_keywords": ["test", "jest", "vitest", "coverage"],
        "suggestion": "Document testing strategy and commands in CLAUDE.md",
    },
    "ci_cd": {
        "check": lambda p: any([
            (p / ".github" / "workflows").exists(),
            (p / ".gitlab-ci.yml").exists(),
            (p / "Jenkinsfile").exists(),
        ]),
        "docs_keywords": ["ci", "cd", "pipeline", "github actions", "workflow"],
        "suggestion": "Document CI/CD pipeline and deployment process in CLAUDE.md",
    },
}

# Keywords that might indicate contradictory rules
CONTRADICTION_KEYWORDS = {
    "use": "avoid",
    "always": "never",
    "prefer": "avoid",
    "recommended": "discouraged",
    "required": "optional",
    "enable": "disable",
}


def parse_frontmatter(content: str) -> dict[str, str | list[str]]:
    """Parse YAML frontmatter from content."""
    if not content.startswith("---"):
        return {}

    lines = content.split("\n")
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return {}

    frontmatter: dict[str, str | list[str]] = {}
    yaml_lines = lines[1:end_index]

    for line in yaml_lines:
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            frontmatter[key] = [item.strip().strip("\"'") for item in items if item.strip()]
        elif value.startswith('"') and value.endswith('"'):
            frontmatter[key] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            frontmatter[key] = value[1:-1]
        else:
            frontmatter[key] = value

    return frontmatter


def extract_rules(content: str) -> list[str]:
    """Extract individual rules/statements from content."""
    rules: list[str] = []

    # Skip frontmatter
    if content.startswith("---"):
        match = re.search(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if match:
            content = content[match.end():]

    # Extract bullet points
    bullet_pattern = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)
    for match in bullet_pattern.finditer(content):
        rules.append(match.group(1).strip())

    # Extract numbered items
    numbered_pattern = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)
    for match in numbered_pattern.finditer(content):
        rules.append(match.group(1).strip())

    return rules


def extract_file_references(content: str) -> list[str]:
    """Extract file/path references from content."""
    references: list[str] = []

    # Common false positive patterns to skip
    skip_patterns = {
        "e.g", "i.e", "etc.", "vs.", "a.k.a",  # Abbreviations
        "1.0", "2.0", "3.0", "0.1", "0.0",  # Version numbers
    }

    # Common documentation-only files that might not exist yet
    doc_only_files = {
        "CLAUDE.local.md",  # May be gitignored/not created
        "example.ts", "example.js", "example.py",  # Example references
        "my-file.ts", "your-file.js",  # Placeholder names
    }

    # Match file paths with extensions (require at least 2 char extension)
    path_pattern = re.compile(r'`([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]{2,})`')
    for match in path_pattern.finditer(content):
        path = match.group(1)
        # Filter out URLs and common non-file patterns
        if path.startswith("http") or path.startswith("www"):
            continue
        if path in skip_patterns:
            continue
        if Path(path).name in doc_only_files:
            continue
        # Skip if looks like a version (x.y.z pattern)
        if re.match(r'^\d+\.\d+(\.\d+)?$', path):
            continue
        references.append(path)

    # Match directory references (explicit ./ prefix)
    dir_pattern = re.compile(r'`(\./[a-zA-Z0-9_\-./]+)`')
    for match in dir_pattern.finditer(content):
        references.append(match.group(1))

    return list(set(references))


def content_hash(text: str) -> str:
    """Generate a hash for content comparison."""
    # Normalize whitespace for comparison
    normalized = " ".join(text.split())
    return hashlib.md5(normalized.encode()).hexdigest()[:8]


def find_memory_files(project_root: Path) -> list[Path]:
    """Find all memory/rules files in the project."""
    files: list[Path] = []

    # Root CLAUDE.md
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists():
        files.append(claude_md)

    # Root CLAUDE.local.md
    claude_local = project_root / "CLAUDE.local.md"
    if claude_local.exists():
        files.append(claude_local)

    # .claude directory
    claude_dir = project_root / ".claude"
    if claude_dir.exists():
        # CLAUDE.md in .claude
        if (claude_dir / "CLAUDE.md").exists():
            files.append(claude_dir / "CLAUDE.md")

        # Rules directory
        rules_dir = claude_dir / "rules"
        if rules_dir.exists():
            files.extend(rules_dir.rglob("*.md"))

    return files


def detect_conflicts(files_content: dict[Path, str]) -> list[Finding]:
    """Detect contradictory rules across files."""
    findings: list[Finding] = []

    # Skip conflict detection if only one file (can't have conflicts)
    if len(files_content) < 2:
        return findings

    # Extract rules from each file
    file_rules: dict[Path, list[str]] = {}
    for file_path, content in files_content.items():
        file_rules[file_path] = extract_rules(content)

    # Check for contradictions across different files only
    for positive, negative in CONTRADICTION_KEYWORDS.items():
        positive_files: dict[str, list[tuple[Path, str]]] = defaultdict(list)
        negative_files: dict[str, list[tuple[Path, str]]] = defaultdict(list)

        for file_path, rules in file_rules.items():
            for rule in rules:
                rule_lower = rule.lower()
                # Extract the subject being discussed
                words = rule_lower.split()

                if positive in words:
                    # Find the subject (word after the keyword)
                    idx = words.index(positive)
                    if idx + 1 < len(words):
                        subject = words[idx + 1]
                        # Skip common false positives (short words, punctuation)
                        if len(subject) < 3 or not subject.isalnum():
                            continue
                        positive_files[subject].append((file_path, rule))

                if negative in words:
                    idx = words.index(negative)
                    if idx + 1 < len(words):
                        subject = words[idx + 1]
                        if len(subject) < 3 or not subject.isalnum():
                            continue
                        negative_files[subject].append((file_path, rule))

        # Find conflicts - only flag if rules are in DIFFERENT files
        for subject in set(positive_files.keys()) & set(negative_files.keys()):
            pos_entries = positive_files[subject]
            neg_entries = negative_files[subject]

            pos_file_set = set(p for p, _ in pos_entries)
            neg_file_set = set(p for p, _ in neg_entries)

            # Only flag if the contradiction spans multiple files
            if pos_file_set != neg_file_set and pos_file_set and neg_file_set:
                all_files = list(set(str(p) for p in pos_file_set | neg_file_set))
                findings.append(Finding(
                    severity="high",
                    category="conflict",
                    title=f"Potential conflict for '{subject}'",
                    description=f"Found '{positive}' in some files and '{negative}' in others for '{subject}'",
                    files=all_files,
                    suggestion="Review and consolidate these rules to ensure consistency",
                ))

    return findings


def detect_duplication(files_content: dict[Path, str]) -> list[Finding]:
    """Detect duplicate content across files."""
    findings: list[Finding] = []

    # Extract content blocks and their hashes
    block_locations: dict[str, list[tuple[Path, str]]] = defaultdict(list)

    for file_path, content in files_content.items():
        rules = extract_rules(content)
        for rule in rules:
            if len(rule) > 20:  # Only check substantial rules
                h = content_hash(rule)
                block_locations[h].append((file_path, rule))

    # Find duplicates
    for hash_val, locations in block_locations.items():
        if len(locations) > 1:
            files = list(set(str(loc[0]) for loc in locations))
            sample_content = locations[0][1][:100]

            findings.append(Finding(
                severity="medium",
                category="duplication",
                title="Duplicate content detected",
                description=f"Same or very similar content found in multiple files: '{sample_content}...'",
                files=files,
                suggestion="Consider moving shared content to a common file and using @import",
            ))

    return findings


def detect_stale_references(files_content: dict[Path, str], project_root: Path) -> list[Finding]:
    """Detect references to files that don't exist."""
    findings: list[Finding] = []

    for file_path, content in files_content.items():
        references = extract_file_references(content)

        for ref in references:
            # Skip common false positives
            if ref.startswith("http") or "@" in ref:
                continue

            # Try to resolve the reference
            ref_path = project_root / ref
            relative_ref = file_path.parent / ref

            if not ref_path.exists() and not relative_ref.exists():
                # Check if it's a glob pattern
                if "*" in ref:
                    continue

                # Check if any file matches partially
                ref_name = Path(ref).name
                if not list(project_root.rglob(ref_name)):
                    findings.append(Finding(
                        severity="low",
                        category="stale_reference",
                        title=f"Stale file reference: {ref}",
                        description=f"Referenced file '{ref}' does not exist",
                        files=[str(file_path)],
                        suggestion="Update or remove this reference",
                    ))

    return findings


def detect_coverage_gaps(files_content: dict[Path, str], project_root: Path) -> list[Finding]:
    """Detect common patterns not documented."""
    findings: list[Finding] = []

    # Combine all content for keyword search
    all_content = " ".join(files_content.values()).lower()

    for pattern_name, pattern_info in COVERAGE_PATTERNS.items():
        # Check if pattern exists in project
        if pattern_info["check"](project_root):
            # Check if documented
            keywords = pattern_info["docs_keywords"]
            documented = any(kw in all_content for kw in keywords)

            if not documented:
                findings.append(Finding(
                    severity="info",
                    category="coverage_gap",
                    title=f"Undocumented: {pattern_name}",
                    description=f"Project has {pattern_name} but no documentation about it was found",
                    files=[],
                    suggestion=pattern_info["suggestion"],
                ))

    return findings


def generate_report(findings: list[Finding], project_root: Path) -> str:
    """Generate markdown report from findings."""
    lines = [
        "# Memory Audit Report",
        "",
        f"**Project:** {project_root.name}",
        f"**Path:** {project_root}",
        "",
    ]

    # Summary
    severity_counts = defaultdict(int)
    for finding in findings:
        severity_counts[finding.severity] += 1

    lines.extend([
        "## Summary",
        "",
        f"- Critical: {severity_counts.get('critical', 0)}",
        f"- High: {severity_counts.get('high', 0)}",
        f"- Medium: {severity_counts.get('medium', 0)}",
        f"- Low: {severity_counts.get('low', 0)}",
        f"- Info: {severity_counts.get('info', 0)}",
        "",
    ])

    if not findings:
        lines.append("No issues found. Your memory configuration looks good!")
        return "\n".join(lines)

    # Group by severity
    severity_order = ["critical", "high", "medium", "low", "info"]

    for severity in severity_order:
        severity_findings = [f for f in findings if f.severity == severity]
        if not severity_findings:
            continue

        lines.extend([
            f"## {severity.title()} Issues",
            "",
        ])

        for i, finding in enumerate(severity_findings, 1):
            lines.extend([
                f"### {i}. {finding.title}",
                "",
                f"**Category:** {finding.category}",
                "",
                finding.description,
                "",
            ])

            if finding.files:
                lines.append("**Files:**")
                for f in finding.files:
                    lines.append(f"- `{f}`")
                lines.append("")

            if finding.suggestion:
                lines.append(f"**Suggestion:** {finding.suggestion}")
                lines.append("")

    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit memory/rules files for issues"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Project root path (default: current directory)",
    )
    args = parser.parse_args()

    project_root = Path(args.path).resolve()

    if not project_root.exists():
        print(f"Error: Path does not exist: {project_root}", file=sys.stderr)
        return 1

    # Find all memory files
    memory_files = find_memory_files(project_root)

    if not memory_files:
        print(f"No memory files found in {project_root}", file=sys.stderr)
        print("\nExpected files:")
        print("  - CLAUDE.md")
        print("  - CLAUDE.local.md")
        print("  - .claude/CLAUDE.md")
        print("  - .claude/rules/*.md")
        return 0

    # Read all files
    files_content: dict[Path, str] = {}
    for file_path in memory_files:
        try:
            files_content[file_path] = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    # Run all audits
    findings: list[Finding] = []
    findings.extend(detect_conflicts(files_content))
    findings.extend(detect_duplication(files_content))
    findings.extend(detect_stale_references(files_content, project_root))
    findings.extend(detect_coverage_gaps(files_content, project_root))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: severity_order.get(f.severity, 5))

    # Generate and print report
    report = generate_report(findings, project_root)
    print(report)

    # Return non-zero if critical or high issues found
    has_serious = any(f.severity in ("critical", "high") for f in findings)
    return 1 if has_serious else 0


if __name__ == "__main__":
    sys.exit(main())
