# Code Style

<!--
  Note: This rule has no `paths` frontmatter because code style applies globally.
  Consider path-scoping if you have different styles for frontend vs backend.
-->

## Formatting
- [Indentation: spaces/tabs, count—e.g., "2 spaces"]
- [Line length—e.g., "100 characters max"]
- [Trailing commas, semicolons—e.g., "ES5 trailing commas, no semicolons"]

## Naming
- [Variables: camelCase]
- [Types/Interfaces: PascalCase]
- [Constants: UPPER_SNAKE_CASE or camelCase for non-primitives]
- [Files: kebab-case or camelCase]

## TypeScript
- [any usage: never/when allowed—e.g., "Never use any, look up actual types"]
- [Type inference vs explicit—e.g., "Let TS infer when obvious, annotate function returns"]
- [Interface vs Type—e.g., "Use interface for objects, type for unions/primitives"]

## Imports
- [Order: external, internal, relative—e.g., "External packages first, then @/ aliases, then relative"]
- [Absolute vs relative paths—e.g., "Use @/ alias for src/ imports"]
