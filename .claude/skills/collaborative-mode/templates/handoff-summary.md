## Ready for Implementation

**Project**: {{project}}
**Feature**: {{feature_slug}}
**Branch**: {{branch_name}}
**Risk Level**: {{risk_level}}

---

### Plan Location

`{{plan_path}}`

---

### Requirements Summary

{{requirements_summary}}

---

### Key Decisions

{{key_decisions}}

---

### Affected Files

{{affected_files}}

---

### Task Breakdown

See `{{plan_path}}` for full task breakdown with dependencies.

**Quick overview:**
{{task_overview}}

---

### Suggested First Steps

1. Review the full plan at `{{plan_path}}`
2. {{first_step}}
3. {{second_step}}
4. {{third_step}}

---

### Open Questions

{{open_questions}}

---

### Available Agents for Implementation

| Agent | Use For |
|-------|---------|
| `programmer` | Complex multi-file implementation |
| `junior-engineer` | Focused single-file tasks |
| `frontend-builder` | UI component work |
| `test-checker` | Test implementation |
| `code-reviewer` | Post-implementation review |

---

### To Orchestrate Later

If you want to orchestrate implementation later:

```
Task(subagent_type="orchestrate-workflow", prompt="Execute plan at {{plan_path}}")
```

---

*Collaborative session ended. Plan is ready for implementation.*
