---
name: writing-library-references
description: Create compressed LLM-optimized reference docs for external libraries. Use when documenting third-party libraries or creating quick reference guides.
---

# Writing Library References

Create compressed, LLM-optimized reference documentation for external libraries.

## Purpose

Library references provide:
- Quick lookup for API details
- Non-obvious behaviors and gotchas
- Configuration shapes
- Version-specific information

## Key Principle

**Only include what an LLM wouldn't know.**

Claude knows general programming. Include:
- Exact function signatures with parameter types
- Non-obvious constraints ("max 100 items")
- Configuration object shapes
- Library-specific gotchas
- Version-specific changes

## Output Structure

```markdown
# [Library Name] LLM Reference

## Version
[X.X.X] - [Date fetched]

## Critical Signatures

[Complex function signatures with non-obvious parameters]

## Configuration Shapes

[Required config objects with all fields]

## Non-Obvious Behaviors

[Things that would surprise even an expert]

## Common Gotchas

[Mistakes that are easy to make]
```

## What to Include vs Exclude

### Include (LLM needs this)
```typescript
createClient({
  url: string, // Required format: "https://*.supabase.co"
  auth: {
    persistSession: boolean, // Default: true
    detectSessionInUrl: boolean, // Default: true, breaks SSR
  },
});
```

### Exclude (LLM already knows)
```typescript
// useState manages state in React components
const [count, setCount] = useState(0);
```

## Decision Heuristic

Ask: "Would Claude make a mistake without this information?"
- If no → exclude
- If yes → include with minimal context

## Best Practices

### Be Concise
One line per behavior. No tutorials.

### Include Constraints
```
maxItems: 100  // API rejects larger arrays
timeout: number  // milliseconds, not seconds
```

### Note Breaking Changes
```
v2.0: `oldMethod()` removed, use `newMethod()`
```

### Date Your Reference
Libraries change. Include version and fetch date.

## File Location

Save to: `docs/external/[library]-llm-ref.md`

## Fetching Documentation

1. Use WebFetch for official docs
2. Use WebSearch for latest patterns
3. Check GitHub for recent issues/changes
