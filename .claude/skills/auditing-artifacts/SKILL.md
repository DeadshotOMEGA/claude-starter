---
name: auditing-artifacts
description: Audit Claude Code artifacts (commands, agents, skills, hooks, CLAUDE.md, rules) using standardized 20-point scoring rubric. Use when auditing, reviewing, scoring, or evaluating any Claude Code artifact.
---

# Auditing Artifacts

Systematically audit Claude Code artifacts using a standardized 20-point scoring rubric with type-specific criteria.

## Contents

- [Quick Start](#quick-start)
- [Scoring Rubric](#scoring-rubric)
- [Auto-Detection](#auto-detection)
- [Audit Process](#audit-process)
- [Report Format](#report-format)
- [Bulk Auditing](#bulk-auditing)

## Quick Start

**Audit a single artifact:**
```
Audit .claude/commands/my-command.md
```

**Audit all commands:**
```
Audit all commands in .claude/commands/
```

**Generate report:**
```
Audit commands and save report to docs/Review/commands-audit.md
```

## Scoring Rubric

Every artifact is scored on 20 points across 5 categories:

| Category | Points | Focus |
|----------|--------|-------|
| **Structure** | 5 | Frontmatter completeness, organization, appropriate length |
| **Clarity** | 4 | Purpose statement, usage examples, edge cases, output format |
| **Technical** | 5 | Type-specific patterns (tools, tiers, triggers, arguments) |
| **Operational** | 4 | Delegation, security/permissions, error handling |
| **Maintainability** | 2 | No hardcoded values, dependencies documented |

**Total:** 20 points

### Scoring Guide

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 18-20 | A | Excellent - production-ready, exemplary |
| 15-17 | B | Good - minor improvements suggested |
| 12-14 | C | Fair - needs refinement |
| 9-11 | D | Poor - significant issues to address |
| 0-8 | F | Failing - requires major rework |

## Auto-Detection

Artifact type is auto-detected from file path:

| Path Pattern | Artifact Type | Criteria File |
|--------------|---------------|---------------|
| `.claude/commands/*.md` | Command | `criteria/commands.md` |
| `.claude/agents/*.md` | Agent | `criteria/agents.md` |
| `.claude/skills/*/SKILL.md` | Skill | `criteria/skills.md` |
| `settings.json` (hooks context) | Hook | `criteria/hooks.md` |
| `**/CLAUDE.md` | CLAUDE.md | `criteria/claudemd.md` |
| `.claude/rules/*.md` | Rule | `criteria/rules.md` |

## Audit Process

1. **Detect artifact type** from file path
2. **Load criteria file** from `criteria/` directory
3. **Read artifact** and analyze against rubric
4. **Score each category** (Structure, Clarity, Technical, Operational, Maintainability)
5. **Generate audit report** using `templates/audit-report.md`
6. **Provide recommendations** for improvements

## Report Format

Audit reports include:

```markdown
# Artifact Audit Report

## Summary
- Total Artifacts Audited: N
- Average Score: X.X/20
- Grade Distribution: A (N), B (N), C (N), D (N), F (N)

## Individual Scores

### artifact-name.md
**Score: XX/20 (Grade: X)**

| Category | Score | Max | Notes |
|----------|-------|-----|-------|
| Structure | X | 5 | ... |
| Clarity | X | 4 | ... |
| Technical | X | 5 | ... |
| Operational | X | 4 | ... |
| Maintainability | X | 2 | ... |

**Strengths:**
- [What it does well]

**Issues:**
- [What needs improvement]

**Recommendations:**
- [Specific actionable fixes]

---

## Category Recommendations

[Patterns observed across all artifacts]

## Suggested Fixes

[Offer to apply fixes automatically]
```

## Bulk Auditing

When auditing multiple artifacts:

1. **Score all artifacts** using consistent criteria
2. **Identify patterns** across the collection
3. **Categorize by score** for triage
4. **Suggest folder organization** if needed (e.g., subfolder by category)
5. **Offer batch fixes** for common issues

### Category Recommendations

After bulk audit, provide recommendations like:

- **Missing frontmatter fields:** 12 commands missing `argument-hint`
- **Description quality:** 8 agents need more specific trigger phrases
- **Tool permissions:** 5 skills should restrict tools using `allowed-tools`
- **Organization:** Consider subfolders: `commands/git/`, `commands/review/`, `commands/project/`

## Criteria Files

Each artifact type has specific criteria in `criteria/`:

- `commands.md` — Slash command requirements (frontmatter, arguments, references)
- `agents.md` — Subagent requirements (naming, tools, prompts, tiers)
- `skills.md` — Skill requirements (naming, description, progressive disclosure)
- `hooks.md` — Hook requirements (events, matchers, performance)
- `claudemd.md` — CLAUDE.md requirements (hierarchy, conciseness, separation)
- `rules.md` — Rules requirements (paths, specificity, imperative)

## When to Use

- **New artifact created:** Validate before committing
- **Bulk review:** Audit entire directory for consistency
- **Quality assessment:** Score artifacts for improvement prioritization
- **Documentation:** Generate audit reports for tracking quality
- **Refactoring:** Identify artifacts needing attention

## Output

After auditing, provide:

1. **Individual scores** with specific feedback
2. **Aggregate statistics** (average score, distribution)
3. **Actionable recommendations** for improvements
4. **Optional:** Offer to fix common issues automatically
