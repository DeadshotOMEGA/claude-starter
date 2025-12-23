---
name: writing-feature-docs
description: Write feature documentation explaining how features work. Use when creating feature docs or explaining existing functionality.
---

# Feature Documentation Writing

Create feature documentation that explains how features work for developers.

## Purpose

Feature docs provide:
- Overview of what the feature does
- How users interact with it
- Data flow through the system
- Key implementation files
- Usage examples

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Overview** — 1-2 sentences: what it does and why it exists
2. **User Perspective** — How users interact with the feature
3. **Data Flow** — Step-by-step through the system
4. **Implementation** — Key files, database, configuration
5. **Usage Example** — Code showing common usage
6. **Testing** — How to manually test the feature
7. **Related Documentation** — Links to architecture, API docs

## Data Flow Format

```markdown
1. [User action initiates...]
2. [Server/client processes...]
3. [Database operations...]
4. [Response handling...]
5. [UI updates with...]
```

## Implementation Section

```markdown
### Key Files
- `src/[path]/[component].tsx` - [Purpose]
- `src/actions/[action].ts` - [Server action]
- `src/lib/repositories/[repo].ts` - [Data access]

### Database
- Tables: `[table_name]` - [purpose]
- RPC functions: `[function_name]()` - [what it does]

### Configuration
- Environment variables: `[VAR_NAME]`
```

## Best Practices

- Write for developers who will maintain the code
- Include real file paths
- Show concrete examples, not abstract descriptions
- Link to related docs instead of duplicating
