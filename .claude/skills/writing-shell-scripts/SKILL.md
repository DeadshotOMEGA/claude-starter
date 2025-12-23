---
name: writing-shell-scripts
description: Robust shell scripts with POSIX compliance, error handling, and automation patterns. Use when writing bash/zsh scripts, deployment automation, or system administration tasks.
---

# Writing Shell Scripts

## Focus Areas

- **POSIX compliance** — Cross-platform compatibility across bash, zsh, sh
- **Error handling** — Defensive programming with proper exit codes and validation
- **Process management** — Job control, signal handling, subprocess management
- **Text processing** — Efficient pipelines and file operations
- **System integration** — Logging, monitoring, and environment management

## Essential Patterns

### Strict Mode
Always use `set -euo pipefail` for robust error handling:
```bash
#!/bin/bash
set -euo pipefail
```

### Variable Quoting
Quote all variables to prevent word splitting:
```bash
# Good
echo "$var"
grep "$pattern" "$file"

# Bad (can break with spaces)
echo $var
grep $pattern $file
```

### Input Validation
Validate arguments early and often:
```bash
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <required-arg>" >&2
  exit 1
fi

if [[ ! -f "$file" ]]; then
  echo "Error: File not found: $file" >&2
  exit 1
fi
```

### Error Handling
Use trap for cleanup and error handling:
```bash
trap 'echo "Error on line $LINENO" >&2' ERR
trap 'rm -f "$temp_file"' EXIT
```

### Function Pattern
Well-structured functions with documentation:
```bash
# Check if a file is readable
# Args: $1 = file path
# Returns: 0 if readable, 1 otherwise
is_readable() {
  [[ -r "$1" ]]
}
```

## Code Examples

### Deployment Script Template
```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

cleanup() {
  log "Cleaning up..."
  # Cleanup logic here
}

trap cleanup EXIT
trap 'log "Error on line $LINENO"; exit 1' ERR

main() {
  log "Starting deployment..."
  # Main logic here
}

main "$@"
```

### Process Management
```bash
# Run command with timeout
timeout 30 long_running_command

# Run in background and wait
background_job &
local pid=$!
wait "$pid" || log "Job failed with code $?"

# Process substitution
diff <(command1) <(command2)
```

### Text Processing
```bash
# Read file line by line
while IFS= read -r line; do
  process "$line"
done < "$file"

# Safe globbing
shopt -s nullglob
for file in *.txt; do
  process "$file"
done
```

## Output Expectations

- Shell scripts with comprehensive error handling
- POSIX-compliant code for maximum portability
- Input validation and argument sanitization
- Clear error messages to stderr
- Usage documentation and help messages
- Modular, reusable functions
- Exit codes indicating success/failure

## Key Principles

1. **Fail fast** — Exit on errors, don't continue silently
2. **Quote everything** — Prevent word splitting vulnerabilities
3. **Check inputs** — Validate files exist, arguments provided
4. **Log clearly** — Use stderr for errors, document what script does
5. **Clean up** — Use traps to ensure temporary files are removed
6. **Be portable** — Avoid bash-isms when POSIX compliance matters
