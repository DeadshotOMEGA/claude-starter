---
description: Validate and fix Claude hooks configuration (permissions, dependencies, line endings)
argument-hint: [hooks-path]
allowed-tools: Read, Glob, Bash(chmod:*, sed:*, bun:*, file:*, find:*)
---

Run the hooks setup validation to ensure all Claude hooks are properly configured. Check and fix these three common issues:

1. **CRLF Line Endings**: Find all hook files (*.sh, *.mjs, *.js, *.py, *.ts) outside node_modules and check if they have CRLF line endings using `file` command. Convert any CRLF files to Unix LF endings using `sed -i 's/\r$//'`.

2. **Execute Permissions**: Find all hook files (*.sh, *.mjs, *.js, *.py) outside node_modules that lack execute permission. Add execute permission with `chmod +x`.

3. **Node Dependencies**: Check if `.claude/hooks/package.json` exists and if `node_modules` is missing or incomplete. Run `bun install` in the hooks directory if needed.

Report what was found and fixed in a clear summary.
