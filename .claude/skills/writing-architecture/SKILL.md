---
name: writing-architecture
description: Write architecture documentation explaining system design. Use when creating architecture.md or system design documents.
---

# Architecture Documentation Writing

Create architecture documentation that explains system design decisions.

## Purpose

Architecture docs capture:
- High-level system overview
- Technology choices and rationale
- Layer responsibilities
- Data flow patterns
- Design decisions

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Overview** — High-level purpose and philosophy
2. **Tech Stack** — Technologies with versions
3. **Architecture Diagram** — Visual representation
4. **Core Layers** — Presentation, business logic, data access
5. **Data Flow Patterns** — Read and write operations
6. **Security Architecture** — Auth, authorization, data isolation
7. **Performance Considerations** — Caching, optimization
8. **Key Design Decisions** — Decisions with rationale

## Layer Documentation Format

```markdown
### Presentation Layer
- Location: `src/app/`, `src/components/`
- Pattern: [Server/Client Components]
- Key decisions: [Why this approach]

### Business Logic Layer
- Services: `src/lib/services/`
- Actions: `src/actions/`
- Key patterns: [Service pattern decisions]

### Data Access Layer
- Repositories: `src/lib/repositories/`
- Security: [RLS policies, access patterns]
```

## Design Decision Format

```markdown
### [Decision Name]
**Context**: [Why this decision was needed]
**Decision**: [What was decided]
**Consequences**: [Trade-offs and implications]
```

## Best Practices

- Focus on "why" not just "what"
- Include diagrams for complex flows
- Document trade-offs explicitly
- Link to detailed docs for each area
- Keep updated as architecture evolves
