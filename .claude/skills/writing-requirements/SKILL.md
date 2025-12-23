---
name: writing-requirements
description: Write requirements documents with functional and technical specs. Use when creating requirements.md files or gathering feature specifications.
---

# Requirements Writing

Create requirements documents that fully specify what needs to be built.

## Purpose

Requirements docs capture:
- User needs and business value
- Functional behavior specifications
- Technical constraints and requirements
- Edge cases and error handling
- Success criteria

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Overview** — Purpose, user benefit, problem solved
2. **Edge Cases** — Empty state, error state, loading state, performance
3. **Functional Requirements** — User interactions, data requirements, API/UI specs
4. **Technical Requirements** — Performance, security, integration points
5. **Implementation Notes** — Patterns to follow, technology choices
6. **Out of Scope** — Explicitly excluded items
7. **Success Criteria** — Measurable outcomes
8. **Relevant Files** — All file paths that will be touched

## Writing Effective Requirements

### Be Specific
**Bad:** "Fast page load"
**Good:** "Page load < 2 seconds on 3G connection"

### Include Edge Cases
- What happens with no data?
- What happens on error?
- What happens with 10,000 items?

### Define Acceptance Criteria
Use Given/When/Then format:
```
Given [precondition]
When [action]
Then [expected result]
```

## Best Practices

- Gather requirements through questions, don't assume
- Include non-functional requirements (performance, security)
- List all files that will be affected
- Define what's explicitly out of scope
