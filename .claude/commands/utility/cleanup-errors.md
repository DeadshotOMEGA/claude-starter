# Cleanup Errors

Manually clean up the error learning log to manage storage.

## Usage

```
/cleanup-errors [options]
```

## What This Does

Removes old entries from the error learning log. Options:

- Remove entries older than N days
- Remove entries for specific error types
- Clear all entries (reset)

## Options

- `--older-than N` - Remove entries older than N days
- `--type error_type` - Remove only entries of specific type
- `--all` - Clear entire log (requires confirmation)

## Examples

```bash
# Remove entries older than 30 days
/cleanup-errors --older-than 30

# Remove all 'file_not_found' entries
/cleanup-errors --type file_not_found

# Clear entire log
/cleanup-errors --all
```

## Prompt

```
Clean up the error learning log based on user options.

Log file location: ~/.claude/logs/error-learning.jsonl

For --older-than N:
1. Read the log file
2. Filter out entries where timestamp is older than N days
3. Write remaining entries back to file
4. Report how many entries were removed

For --type error_type:
1. Read the log file
2. Filter out entries matching the error type
3. Write remaining entries back
4. Report count removed

For --all:
1. Ask user to confirm: "This will delete all error learning data. Continue?"
2. If confirmed, delete the log file
3. Report success

Always back up before major deletions:
cp ~/.claude/logs/error-learning.jsonl ~/.claude/logs/error-learning.jsonl.bak
```
