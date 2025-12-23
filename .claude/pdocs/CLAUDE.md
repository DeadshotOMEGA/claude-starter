# pdocs/

## Purpose

CLI tool for managing YAML-based project documentation with templates, validation, and registry tracking.

## When to Use

Use pdocs when:
- Creating new documentation files (plans, investigations, requirements)
- Validating existing documents against schemas
- Tracking documentation status across the project

```bash
# Create from template
./pdocs create plan docs/plans/ --auto-id

# Validate documents
./pdocs check docs/ --recursive

# List tracked documents
./pdocs list --tree
```

## Key Patterns

- Run from `.claude/pdocs/` directory or use full path
- Documents are auto-registered in `registry.json` on creation
- Each doc type maps to a writing-* skill for validation rules
- Use `--auto-id` for sequential IDs (P-001, INV-001, etc.)

## Critical Guidelines

- ⚠️ Build before first use: `bun install && bun run build`
- ⚠️ Don't edit `registry.json` manually — use CLI commands
- 📝 Run `./pdocs check` after significant document changes

## File Structure

- `src/` — TypeScript source code
- `dist/` — Built JavaScript (run `bun run build`)
- `registry.json` — Tracks all registered documents
- `pdocs` — Shell wrapper script

## Document Types

| Type | Skill | Use For |
|------|-------|---------|
| `plan` | writing-plans | Implementation plans |
| `investigation` | writing-investigations | Bug/feature investigations |
| `requirements` | writing-requirements | Feature requirements |

See `src/types.ts` for full list.

## Notes

Requires `bun` for building. See @README.md for full command reference.
