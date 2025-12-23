#!/usr/bin/env python3
"""
Migrate monolithic CLAUDE.md to modular rules.

Features:
- Parse CLAUDE.md and identify logical sections
- Suggest which sections should become separate rule files
- Analyze content to suggest `paths:` frontmatter where appropriate
- Generate migration plan (what files to create, what content goes where)
- Optionally execute migration with --execute flag

Usage:
- python migrate.py <path-to-claude-md> (plan only)
- python migrate.py <path-to-claude-md> --execute (apply changes)

Output: Migration plan in markdown format
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Section:
    """Represents a section of the CLAUDE.md file."""
    title: str
    level: int
    content: str
    line_start: int
    line_end: int
    subsections: list["Section"] = field(default_factory=list)


@dataclass
class MigrationTarget:
    """Represents a file to create during migration."""
    filename: str
    title: str
    description: str
    content: str
    frontmatter: dict[str, str | list[str]]
    source_sections: list[str]
    reason: str


# Keywords that suggest which paths a rule file should apply to
PATH_KEYWORDS = {
    "typescript": ["*.ts", "*.tsx"],
    "javascript": ["*.js", "*.jsx"],
    "react": ["*.tsx", "*.jsx", "components/**/*"],
    "api": ["**/api/**/*", "**/routes/**/*"],
    "database": ["**/prisma/**/*", "**/db/**/*", "**/migrations/**/*"],
    "test": ["**/*.test.*", "**/*.spec.*", "**/tests/**/*"],
    "style": ["*.css", "*.scss", "*.less", "tailwind.config.*"],
    "config": ["*.config.*", ".env*", "package.json", "tsconfig.json"],
    "component": ["**/components/**/*"],
    "hook": ["**/hooks/**/*"],
    "util": ["**/utils/**/*", "**/lib/**/*"],
    "service": ["**/services/**/*"],
}

# Categories for organizing rules
SECTION_CATEGORIES = {
    "git": ["git", "commit", "branch", "merge", "version", "release"],
    "code-style": ["style", "format", "lint", "naming", "convention"],
    "testing": ["test", "spec", "jest", "vitest", "coverage", "mock"],
    "architecture": ["architecture", "pattern", "structure", "design"],
    "security": ["security", "auth", "secret", "credential", "permission"],
    "performance": ["performance", "optimize", "cache", "lazy"],
    "documentation": ["doc", "comment", "readme", "jsdoc"],
    "dependencies": ["dependency", "package", "npm", "yarn", "bun", "install"],
    "deployment": ["deploy", "ci", "cd", "pipeline", "build"],
    "database": ["database", "schema", "migration", "query", "prisma"],
    "api": ["api", "endpoint", "rest", "graphql", "route"],
    "frontend": ["component", "react", "ui", "style", "css"],
}


def parse_sections(content: str) -> list[Section]:
    """Parse markdown content into sections based on headers."""
    lines = content.split("\n")
    sections: list[Section] = []
    current_section: Section | None = None
    content_buffer: list[str] = []
    content_start = 0

    # Skip frontmatter if present
    start_line = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_line = i + 1
                break

    for i, line in enumerate(lines[start_line:], start=start_line):
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line)

        if header_match:
            # Save previous section
            if current_section:
                current_section.content = "\n".join(content_buffer).strip()
                current_section.line_end = i - 1
                sections.append(current_section)

            # Start new section
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            current_section = Section(
                title=title,
                level=level,
                content="",
                line_start=i + 1,
                line_end=i + 1,
            )
            content_buffer = []
            content_start = i + 1
        else:
            content_buffer.append(line)

    # Don't forget the last section
    if current_section:
        current_section.content = "\n".join(content_buffer).strip()
        current_section.line_end = len(lines)
        sections.append(current_section)

    return sections


def categorize_section(section: Section) -> str | None:
    """Determine the category of a section based on its content."""
    text = f"{section.title} {section.content}".lower()

    for category, keywords in SECTION_CATEGORIES.items():
        matches = sum(1 for kw in keywords if kw in text)
        if matches >= 2:
            return category

    return None


def suggest_paths(section: Section) -> list[str]:
    """Suggest glob patterns for paths frontmatter based on section content."""
    text = f"{section.title} {section.content}".lower()
    paths: list[str] = []

    for keyword, patterns in PATH_KEYWORDS.items():
        if keyword in text:
            paths.extend(patterns)

    return list(set(paths))


def should_extract(section: Section, all_sections: list[Section]) -> bool:
    """Determine if a section should be extracted to a separate file."""
    # Extract if:
    # 1. It's a top-level section (level 1 or 2)
    # 2. It has substantial content (more than 100 characters)
    # 3. It has a clear category

    if section.level > 2:
        return False

    if len(section.content) < 100:
        return False

    category = categorize_section(section)
    if category:
        return True

    # Also extract if it has multiple bullet points
    bullet_count = section.content.count("\n- ") + section.content.count("\n* ")
    if bullet_count >= 3:
        return True

    return False


def generate_filename(title: str, category: str | None) -> str:
    """Generate a suitable filename for a rule file."""
    # Clean the title
    clean = re.sub(r"[^\w\s-]", "", title.lower())
    clean = re.sub(r"\s+", "-", clean.strip())
    clean = re.sub(r"-+", "-", clean)

    # Truncate if too long
    if len(clean) > 30:
        clean = clean[:30].rsplit("-", 1)[0]

    return f"{clean}.md"


def generate_frontmatter(
    title: str,
    description: str,
    paths: list[str] | None = None,
) -> str:
    """Generate YAML frontmatter for a rule file."""
    lines = ["---"]

    # Description (required for rules)
    lines.append(f"description: {description}")

    # Paths if applicable
    if paths:
        if len(paths) == 1:
            lines.append(f"paths: [{paths[0]}]")
        else:
            lines.append(f"paths: [{', '.join(paths[:5])}]")  # Limit to 5

    lines.append("---")
    return "\n".join(lines)


def analyze_claude_md(file_path: Path) -> list[MigrationTarget]:
    """Analyze CLAUDE.md and generate migration targets."""
    content = file_path.read_text(encoding="utf-8")
    sections = parse_sections(content)

    targets: list[MigrationTarget] = []
    remaining_content: list[str] = []

    for section in sections:
        if should_extract(section, sections):
            category = categorize_section(section)
            paths = suggest_paths(section)

            filename = generate_filename(section.title, category)

            # Generate description from first sentence or bullet
            first_line = section.content.split("\n")[0] if section.content else ""
            description = first_line[:100] if first_line else f"Rules for {section.title}"

            # Build content with frontmatter
            frontmatter: dict[str, str | list[str]] = {
                "description": description,
            }
            if paths:
                frontmatter["paths"] = paths

            target = MigrationTarget(
                filename=filename,
                title=section.title,
                description=description,
                content=section.content,
                frontmatter=frontmatter,
                source_sections=[section.title],
                reason=f"Category: {category}" if category else "Substantial standalone section",
            )
            targets.append(target)
        else:
            # Keep in main CLAUDE.md
            if section.content:
                header = "#" * section.level
                remaining_content.append(f"{header} {section.title}")
                remaining_content.append(section.content)
                remaining_content.append("")

    return targets


def generate_migration_plan(
    source_file: Path,
    targets: list[MigrationTarget],
) -> str:
    """Generate a markdown migration plan."""
    lines = [
        "# Migration Plan",
        "",
        f"**Source:** `{source_file}`",
        f"**Target Directory:** `.claude/rules/`",
        "",
        "## Summary",
        "",
        f"- **Sections to extract:** {len(targets)}",
        f"- **New rule files to create:** {len(targets)}",
        "",
        "## Files to Create",
        "",
    ]

    for i, target in enumerate(targets, 1):
        lines.extend([
            f"### {i}. `{target.filename}`",
            "",
            f"**Source Section:** {target.title}",
            f"**Reason:** {target.reason}",
            "",
        ])

        if target.frontmatter.get("paths"):
            paths = target.frontmatter["paths"]
            if isinstance(paths, list):
                paths_str = ", ".join(f"`{p}`" for p in paths)
            else:
                paths_str = f"`{paths}`"
            lines.append(f"**Suggested Paths:** {paths_str}")
            lines.append("")

        lines.extend([
            "**Frontmatter:**",
            "```yaml",
        ])

        fm = generate_frontmatter(
            target.title,
            target.frontmatter.get("description", ""),  # type: ignore
            target.frontmatter.get("paths"),  # type: ignore
        )
        lines.append(fm)
        lines.extend([
            "```",
            "",
            "**Content Preview:**",
            "```markdown",
            target.content[:500] + ("..." if len(target.content) > 500 else ""),
            "```",
            "",
        ])

    lines.extend([
        "## Remaining in CLAUDE.md",
        "",
        "After migration, the main CLAUDE.md should contain:",
        "- Project overview and quick reference",
        "- Links/imports to rule files",
        "- Configuration that doesn't fit a specific category",
        "",
        "## Execution",
        "",
        "To apply this migration, run:",
        "```bash",
        f"python migrate.py {source_file} --execute",
        "```",
        "",
        "This will:",
        "1. Create `.claude/rules/` directory if needed",
        "2. Create all rule files with frontmatter",
        "3. Update the original CLAUDE.md with @import references",
        "",
    ])

    return "\n".join(lines)


def execute_migration(
    source_file: Path,
    targets: list[MigrationTarget],
) -> None:
    """Execute the migration plan."""
    project_root = source_file.parent
    if source_file.name == "CLAUDE.md" and (project_root / ".claude").exists():
        rules_dir = project_root / ".claude" / "rules"
    else:
        rules_dir = project_root / ".claude" / "rules"

    # Create rules directory
    rules_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {rules_dir}")

    # Create rule files
    created_files: list[str] = []
    for target in targets:
        file_path = rules_dir / target.filename

        # Generate full content
        frontmatter = generate_frontmatter(
            target.title,
            target.frontmatter.get("description", ""),  # type: ignore
            target.frontmatter.get("paths"),  # type: ignore
        )

        full_content = f"{frontmatter}\n\n# {target.title}\n\n{target.content}\n"

        file_path.write_text(full_content, encoding="utf-8")
        created_files.append(str(file_path))
        print(f"Created: {file_path}")

    # Update source CLAUDE.md with imports
    original_content = source_file.read_text(encoding="utf-8")

    # Find where to add imports (after frontmatter if present)
    if original_content.startswith("---"):
        match = re.search(r"^---\s*\n.*?\n---\s*\n", original_content, re.DOTALL)
        if match:
            insert_pos = match.end()
        else:
            insert_pos = 0
    else:
        insert_pos = 0

    # Build import section
    import_lines = [
        "",
        "<!-- Modular rules - auto-generated by migrate.py -->",
    ]
    for target in targets:
        import_lines.append(f"@import('.claude/rules/{target.filename}')")
    import_lines.extend([
        "<!-- End modular rules -->",
        "",
    ])

    # Note: In a production version, we would also remove the migrated sections
    # For safety, we just add imports and let the user clean up manually
    new_content = (
        original_content[:insert_pos] +
        "\n".join(import_lines) +
        original_content[insert_pos:]
    )

    source_file.write_text(new_content, encoding="utf-8")
    print(f"Updated: {source_file}")

    print()
    print("Migration complete!")
    print()
    print("Next steps:")
    print("1. Review the created rule files")
    print("2. Manually remove migrated sections from CLAUDE.md")
    print("3. Adjust paths frontmatter as needed")
    print("4. Run validate.py to verify the migration")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate monolithic CLAUDE.md to modular rules"
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to CLAUDE.md file to migrate",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the migration (default: plan only)",
    )
    args = parser.parse_args()

    source_file = Path(args.file).resolve()

    if not source_file.exists():
        print(f"Error: File does not exist: {source_file}", file=sys.stderr)
        return 1

    if not source_file.name.endswith(".md"):
        print(f"Error: Expected a markdown file: {source_file}", file=sys.stderr)
        return 1

    # Analyze the file
    targets = analyze_claude_md(source_file)

    if not targets:
        print("No sections identified for extraction.")
        print("The file may already be modular or too small to split.")
        return 0

    if args.execute:
        print("Executing migration...")
        print()
        execute_migration(source_file, targets)
    else:
        # Generate and print plan
        plan = generate_migration_plan(source_file, targets)
        print(plan)

    return 0


if __name__ == "__main__":
    sys.exit(main())
