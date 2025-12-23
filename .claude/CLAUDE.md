Project-specific Claude Code configuration. See `.claude/rules/` for modular rules.

## Project Starter Setup

**See `.claude/rules/project-setup.md` for complete checklist.**

Quick validation after cloning:
```bash
# 1. Fix execute permissions
find .claude -name "*.py" -exec chmod +x {} \;

# 2. Check line endings (WSL2/Windows)
find .claude -name "*.py" -exec file {} \; | grep CRLF

# 3. Install dependencies
bun install

# 4. Set up python command (WSL2/Linux)
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```

⚠️ **Platform notes:**
- **WSL2/Linux**: `python` command missing by default. Use `update-alternatives` above.
- **WSL2/Windows**: CRLF line endings break scripts silently. Keep `.gitattributes`.
- **macOS**: Use `sed -i ''` instead of `sed -i` for in-place edits.
- **All**: Run `gh auth setup-git` for git push authentication.

## Common Commands

- `bun test` — Run test suite
- `bun run build` — Build project
- `bun run dev` — Start dev server
- `bun run lint` — Run linter
- `bun typecheck` — TypeScript type checking
- `gh pr create` — Create pull request
- `gh issue list` — List GitHub issues

## Local Overrides

Use `CLAUDE.local.md` (gitignored) for secrets and personal project settings.
