---
description: Review code changes and provide structured feedback
argument-hint: [scope or file]
allowed-tools: Read, Grep, Glob, Bash(git diff:*, git log:*, git show:*)
---

Review the code changes and provide feedback. Follow this workflow:

## Review Scope
$ARGUMENTS

## Process

1. **Identify changes**: Use `git diff` to see what changed (or diff against main branch)
2. **Read affected files**: Understand the full context of modified code
3. **Analyze for issues**:
   - Logic errors or bugs
   - Security vulnerabilities
   - Performance concerns
   - Code style violations
   - Missing error handling
   - Type safety issues (no `any` types)
4. **Check test coverage**: Verify tests exist for new/changed functionality
5. **Provide structured feedback**:
   - 🔴 **Critical**: Must fix before merge
   - 🟡 **Suggestion**: Recommended improvements
   - 🟢 **Nitpick**: Minor style preferences

## Output Format

Provide a concise review with:
- Summary of changes (1-2 sentences)
- List of findings by severity
- Overall recommendation: Approve / Request Changes / Needs Discussion
