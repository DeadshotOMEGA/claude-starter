---
paths: "**/*.test.{ts,tsx,js,jsx}, **/*.spec.{ts,tsx,js,jsx}"
---

# Testing Conventions

## Test Structure
- [Describe test file organization, e.g., "Co-locate tests with source files" or "Place in __tests__ directories"]
- [Describe test naming: describe blocks for modules/components, it blocks for specific behaviors]

## Test Types
- Unit tests: [when to use, what to mock—e.g., "For pure functions and utilities, mock external dependencies"]
- Integration tests: [when to use, setup requirements—e.g., "For API routes, use test database"]
- E2E tests: [when to use, tooling—e.g., "For critical user flows, use Playwright"]

## Commands
- `[test command]` — Run all tests
- `[test command] --watch` — Watch mode
- `[test command] [path]` — Run specific tests

## Best Practices
- [Write tests first when fixing bugs to capture the failure]
- [Prefer descriptive test names that explain expected behavior]
- [Additional conventions, e.g., "Avoid testing implementation details"]
