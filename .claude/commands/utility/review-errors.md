# Review Errors

Analyze the error learning log and get actionable improvement suggestions.

## Usage

```
/review-errors [options]
```

## What This Does

Reviews errors that occurred and were successfully recovered from during Claude Code sessions. Shows:

1. **Summary statistics** - Total errors, recovery rate, affected sessions
2. **ASCII trend graphs** - Visual patterns over the last 7 days
3. **Impact-prioritized suggestions** - Errors that blocked tasks get top priority
4. **Ready-to-use configurations** - Copy-paste content for CLAUDE.md, rules, and hooks

## Options

- `--since YYYY-MM-DD` - Only show errors since specified date
- `--type error_type` - Filter by specific error type (e.g., `edit_before_read`)
- `--days N` - Number of days for trend analysis (default: 7)
- `--show-context` - Include full error context examples
- `--include-unrecovered` - Include errors that weren't recovered from
- `--json` - Output as JSON for programmatic use

## Examples

```bash
# Basic review
/review-errors

# Review last 3 days with context
/review-errors --days 3 --show-context

# Focus on specific error type
/review-errors --type edit_before_read

# Export as JSON
/review-errors --json > errors.json
```

## Suggestion Targets

Suggestions are categorized by where to apply them:

| Target | Location | When to Use |
|--------|----------|-------------|
| `claudemd` | CLAUDE.md | General guidance and patterns |
| `rule` | .claude/rules/*.md | Path-specific conventions |
| `hook` | settings.json | Automated validation |

## Prompt

```
Run the error learning review script to analyze logged errors and generate improvement suggestions.

Execute: python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/error-learning/review.py" $ARGUMENTS

Present the output to the user. If they want to apply a suggestion, help them:
1. For CLAUDE.md suggestions: Edit the appropriate CLAUDE.md file
2. For rule suggestions: Create the rule file in .claude/rules/
3. For hook suggestions: Update settings.json with the hook configuration
```
