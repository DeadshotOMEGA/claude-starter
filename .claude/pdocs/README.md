# pdocs - Project Documentation CLI

CLI tool for managing YAML-based project documentation with validation, templates, and registry tracking.

## Installation

```bash
cd .claude/pdocs
bun install
bun run build
```

## Usage

```bash
# Run directly
./pdocs <command>

# Or via bun
bun run dev <command>
```

## Commands

### `pdocs template [type]`

Get or list document templates.

```bash
# List available templates
./pdocs template --list

# Get a specific template
./pdocs template plan

# Write template to file
./pdocs template investigation -o docs/new-investigation.md

# Fetch remote template
./pdocs template --from github:user/repo/template.md
```

### `pdocs create <type> <output-dir>`

Create a new document from template.

```bash
# Create a plan document
./pdocs create plan docs/plans/

# With custom variables
./pdocs create investigation docs/ --vars title="Auth Bug" priority=high

# Auto-generate ID
./pdocs create plan docs/ --auto-id

# Custom filename
./pdocs create feature-spec docs/ --name user-authentication
```

### `pdocs register <file>`

Register a document in the registry for tracking.

```bash
# Register with auto-detection
./pdocs register docs/plans/auth-plan.md

# Force document type
./pdocs register docs/custom.md -t plan

# Re-register existing
./pdocs register docs/plan.md --force
```

### `pdocs list [type]`

List registered documents.

```bash
# List all documents
./pdocs list

# Filter by type
./pdocs list plan

# Filter by status
./pdocs list --status valid

# Tree view grouped by type
./pdocs list --tree

# JSON output
./pdocs list --json
```

### `pdocs info`

Show project documentation overview.

```bash
./pdocs info
./pdocs info --detailed
./pdocs info --json
```

### `pdocs check [path]`

Validate documents against schemas.

```bash
# Check specific file
./pdocs check docs/plan.md

# Check all files in directory
./pdocs check docs/ --recursive

# Auto-fix issues
./pdocs check docs/plan.md --fix

# Dry-run fixes
./pdocs check docs/ --fix --dry-run

# Strict mode (fail on warnings)
./pdocs check docs/ --strict
```

### `pdocs watch [path]`

Watch for changes and validate continuously.

```bash
./pdocs watch docs/
./pdocs watch docs/ --debounce 1000
```

## Document Types

| Type | Skill | Description |
|------|-------|-------------|
| `plan` | writing-plans | Implementation plans |
| `investigation` | writing-investigations | Bug/feature investigations |
| `requirements` | writing-requirements | Requirements documents |
| `feature-spec` | writing-feature-docs | Feature specifications |
| `api-contract` | writing-api-specs | API contracts |
| `agent` | writing-subagents | Agent definitions |
| `skill` | writing-skills | Skill definitions |
| `claudemd` | writing-claudemd | CLAUDE.md files |
| `rule` | writing-rules | Rule files |
| `command` | writing-commands | Command definitions |
| `readme` | writing-readmes | README files |
| `changelog` | writing-changelogs | Changelog files |

## Registry

Documents are tracked in `registry.json`:

```json
{
  "version": "1.0",
  "documents": {
    "/path/to/doc.md": {
      "type": "plan",
      "skill": "writing-plans",
      "status": "valid",
      "registered": "2025-01-01T00:00:00Z"
    }
  },
  "stats": {
    "total": 1,
    "valid": 1,
    "invalid": 0,
    "pending": 0
  }
}
```

## Project Setup

If using this as part of a project starter:

```bash
# Install pdocs dependencies
cd .claude/pdocs && bun install

# Build (if dist/ is missing)
bun run build

# Verify it works
./pdocs info
```
