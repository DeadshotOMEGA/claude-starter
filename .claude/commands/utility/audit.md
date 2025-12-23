---
description: Audit Claude Code artifacts using 20-point scoring rubric
argument-hint: [path-or-type]
allowed-tools: Read, Grep, Glob, Write
---

Audit Claude Code artifacts using the auditing-artifacts skill with standardized 20-point scoring rubric.

**Usage:**

```
/audit .claude/commands/my-command.md
/audit .claude/agents/
/audit commands
/audit all
```

## Arguments

- **File path:** Audit specific artifact (e.g., `.claude/commands/review.md`)
- **Directory:** Audit all artifacts in directory (e.g., `.claude/commands/`)
- **Type:** Audit by type: `commands`, `agents`, `skills`, `hooks`, `rules`, `claudemd`
- **`all`:** Audit all artifact types

## Process

1. **Auto-detect artifact type** from path or use specified type
2. **Load appropriate criteria** from auditing-artifacts skill
3. **Score artifacts** using 20-point rubric:
   - Structure (5 pts)
   - Clarity (4 pts)
   - Technical (5 pts)
   - Operational (4 pts)
   - Maintainability (2 pts)
4. **Generate audit report** with individual scores and recommendations

## Output

- Individual artifact scores with detailed feedback
- Aggregate statistics (average, grade distribution)
- Category-specific recommendations
- Suggested batch fixes for common issues
- Optional: Organization recommendations (subfolder structure)

## Report Location

Ask where to save the report:
- Default: `docs/Review/{type}-audit.md`
- Custom path if user specifies

## After Audit

Offer to:
1. Apply suggested fixes automatically
2. Create issues for failing artifacts
3. Generate improvement plan

---

**Input:** $ARGUMENTS

Invoke the `auditing-artifacts` skill to perform the audit as specified above.
