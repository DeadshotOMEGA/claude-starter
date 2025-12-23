---
description: Execute TDD workflow (Red-Green-Refactor) for feature or fix
argument-hint: <feature-description>
allowed-tools: Read, Write, Edit, Bash(bun test:*, git add:*, git commit:*)
---

Execute test-driven development workflow for the given feature or fix.

## Target
$ARGUMENTS

## TDD Workflow

### Phase 1: Red (Write Failing Test)
1. Understand the requirement/bug from the target description
2. Write a test that captures the expected behavior
3. Run the test to confirm it fails for the right reason
4. Commit the failing test: `git add -A && git commit -m "test: add failing test for [feature]"`

### Phase 2: Green (Make It Pass)
1. Write the minimum code needed to pass the test
2. Run tests to verify they pass
3. If tests fail, iterate on implementation
4. Commit passing implementation: `git add -A && git commit -m "feat: implement [feature]"`

### Phase 3: Refactor (Clean Up)
1. Review implementation for code quality
2. Refactor while keeping tests green
3. Run full test suite to ensure no regressions
4. Commit refactoring if any: `git add -A && git commit -m "refactor: clean up [feature] implementation"`

## Guidelines
- Tests should be descriptive: `it('should return error when input is invalid')`
- One assertion per test when possible
- Test edge cases and error conditions
- Use existing test patterns from the codebase
