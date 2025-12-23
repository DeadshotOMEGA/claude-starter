# {{ARTIFACT_TYPE}} Audit Report

**Date:** {{DATE}}
**Directory:** `{{DIRECTORY}}`
**Auditor:** {{AUDITOR}}

## Summary

- **Total Artifacts Audited:** {{TOTAL_COUNT}}
- **Average Score:** {{AVERAGE_SCORE}}/20
- **Grade Distribution:**
  - A (18-20): {{COUNT_A}} artifacts
  - B (15-17): {{COUNT_B}} artifacts
  - C (12-14): {{COUNT_C}} artifacts
  - D (9-11): {{COUNT_D}} artifacts
  - F (0-8): {{COUNT_F}} artifacts

---

## Individual Scores

{{#each artifacts}}
### {{name}}

**Score: {{score}}/20 (Grade: {{grade}})**

| Category | Score | Max | Notes |
|----------|-------|-----|-------|
| Structure | {{structure_score}} | 5 | {{structure_notes}} |
| Clarity | {{clarity_score}} | 4 | {{clarity_notes}} |
| Technical | {{technical_score}} | 5 | {{technical_notes}} |
| Operational | {{operational_score}} | 4 | {{operational_notes}} |
| Maintainability | {{maintainability_score}} | 2 | {{maintainability_notes}} |

**Strengths:**
{{#each strengths}}
- {{this}}
{{/each}}

**Issues:**
{{#each issues}}
- {{this}}
{{/each}}

**Recommendations:**
{{#each recommendations}}
- {{this}}
{{/each}}

---

{{/each}}

## Category Analysis

### Structure Issues
{{#each category_patterns.structure}}
- {{this}}
{{/each}}

### Clarity Issues
{{#each category_patterns.clarity}}
- {{this}}
{{/each}}

### Technical Issues
{{#each category_patterns.technical}}
- {{this}}
{{/each}}

### Operational Issues
{{#each category_patterns.operational}}
- {{this}}
{{/each}}

### Maintainability Issues
{{#each category_patterns.maintainability}}
- {{this}}
{{/each}}

## Organization Recommendations

{{ORGANIZATION_SUGGESTIONS}}

## Suggested Batch Fixes

{{#each batch_fixes}}
### {{title}}

**Affects:** {{count}} artifacts
**Fix:** {{fix_description}}

**Artifacts:**
{{#each artifacts}}
- `{{this}}`
{{/each}}

{{/each}}

## Next Steps

1. Review artifacts with grade D or F first (highest priority)
2. Apply batch fixes for common issues
3. Consider reorganization if suggested
4. Re-audit after fixes applied

---

**Legend:**
- ✅ Excellent (no action needed)
- ⚠️ Needs improvement (minor fixes)
- ❌ Critical issue (requires immediate attention)
