---
name: writing-plans
description: Write implementation plans with task breakdowns and dependencies. Use when creating plan.md files or implementation strategies.
---

# Plan Writing

Create implementation plans that break down work into executable tasks.

## Purpose

Plans provide:
- Clear task breakdown with dependencies
- Agent assignments for delegation
- Parallelization opportunities
- Exit criteria for validation

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Summary** — Goal, type (Feature/Refactor/Fix), scope (Small/Medium/Large)
2. **Relevant Context** — Links to requirements, investigations, specs
3. **Current System Overview** — Brief description of affected areas
4. **Implementation Plan** — Task breakdown with details
5. **Parallelization** — Batches of independent tasks
6. **Testing Strategy** — How to validate the work
7. **Impact Analysis** — Affected files, breaking changes

## Task Breakdown Format

```markdown
| ID | Description | Agent | Deps | Files | Exit Criteria |
|----|-------------|-------|------|-------|---------------|
| T1 | [What & why] | [agent] | — | [paths] | [criteria] |
| T2 | [What & why] | [agent] | T1 | [paths] | [criteria] |
```

## Agent Assignment

| Task Type | Suggested Agent |
|-----------|-----------------|
| Research/exploration | Explore, research-specialist |
| Architecture decisions | senior-architect |
| Standard implementation | programmer, junior-engineer |
| Complex implementation | programmer |
| Testing | test-engineer |
| Review | code-reviewer |

## Best Practices

- Order tasks by dependencies
- Group independent tasks for parallel execution
- Include concrete exit criteria (not just "done")
- Reference investigation.md for file details
