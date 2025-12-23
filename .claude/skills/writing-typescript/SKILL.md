---
name: writing-typescript
description: Advanced TypeScript patterns with strict typing, generics, conditional types, and type inference. Use when writing TypeScript code, creating complex types, designing type-safe APIs, or migrating from JavaScript.
---

# Writing TypeScript

Master advanced TypeScript features for type-safe, maintainable applications.

## Focus Areas

- Advanced type system (conditional types, mapped types, template literal types)
- Generic constraints and type inference optimization
- Utility types and custom type helpers
- Strict TypeScript configuration and migration strategies
- Declaration files and module augmentation
- Performance optimization and compilation speed

## Approach

1. Leverage TypeScript's type system for compile-time safety
2. Use strict configuration for maximum type safety
3. Prefer type inference over explicit typing when clear
4. Design APIs with generic constraints for flexibility
5. Optimize build performance with project references
6. Create reusable type utilities for common patterns

## Common Patterns

### Utility Types

```typescript
// Extract keys of a type
type Keys<T> = keyof T;

// Make all properties readonly
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// Pick specific properties
type Pick<T, K extends keyof T> = { [P in K]: T[P] };

// Omit specific properties
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
```

### Conditional Types

```typescript
// Type-level ternary operator
type IsString<T> = T extends string ? true : false;

// Extract union members of specific type
type Extract<T, U> = T extends U ? T : never;
```

### Generic Constraints

```typescript
// Constrain generic to object with specific properties
function getProperty<T extends Record<string, any>>(obj: T, key: keyof T) {
  return obj[key];
}

// Constrain function parameter to array elements
function process<T extends readonly any[]>(items: T): T {
  return items;
}
```

## Configuration

Use strict tsconfig:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitThis": true
  }
}
```

## Output Standards

- Strongly typed with no `any` types
- Advanced generic types with proper constraints
- Custom utility types for reusable patterns
- Type-safe API designs with proper error handling
- Performance-optimized builds
- Clear documentation of complex types
