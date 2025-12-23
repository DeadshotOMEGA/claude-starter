---
paths: "**/*.py, **/*.sh, **/*.mjs"
---

# Line Endings

## Rule

**Always use LF (Unix) line endings for executable scripts.**

CRLF (Windows) line endings break shebang interpretation:
- `#!/usr/bin/env python3\r` looks for interpreter `python3\r` (doesn't exist)
- Scripts fail silently or with cryptic "not found" errors

## Environment Detection

| Environment | Default Line Endings | Risk Level |
|-------------|---------------------|------------|
| WSL2 | Mixed (editor-dependent) | ⚠️ High |
| Windows | CRLF | ⚠️ High |
| macOS/Linux | LF | ✅ Low |

## Prevention

This project uses `.gitattributes` to enforce LF:

```
*.py text eol=lf
*.sh text eol=lf
*.mjs text eol=lf
```

## When Creating Scripts

1. **Check file encoding** after creation:
   ```bash
   file path/to/script.py
   ```
   Should show `text executable` NOT `with CRLF line terminators`

2. **Fix if needed**:
   ```bash
   sed -i 's/\r$//' path/to/script.py
   ```

## Symptoms of CRLF Issues

- Hook scripts don't execute but exit silently
- Python/bash scripts fail with `/usr/bin/env: 'python3\r': No such file or directory`
- Scripts work when run with `python3 script.py` but not `./script.py`
