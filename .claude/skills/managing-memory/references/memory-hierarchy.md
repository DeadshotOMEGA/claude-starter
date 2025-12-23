# Claude Code Memory Hierarchy

Complete reference for the layered memory system that provides persistent instructions to Claude Code.

---

## Memory Types Overview

| Type | Location | Purpose | Shared With |
|------|----------|---------|-------------|
| Enterprise policy | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux) | Organization-wide instructions | All org users |
| Project memory | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared project instructions | Team via git |
| Project rules | `./.claude/rules/*.md` | Modular, topic-specific rules | Team via git |
| User memory | `~/.claude/CLAUDE.md` | Personal preferences | Just you (all projects) |
| Project local | `./CLAUDE.local.md` | Personal project-specific | Just you (gitignored) |

---

## Loading Order and Precedence

Memory files load in a specific order, with later sources overriding earlier ones:

1. **Enterprise policy** (lowest priority)
2. **User memory** (`~/.claude/CLAUDE.md`)
3. **Project memory** (`./CLAUDE.md` or `./.claude/CLAUDE.md`)
4. **Project rules** (`./.claude/rules/*.md`)
5. **Project local** (`./CLAUDE.local.md`) (highest priority)

### Conflict Resolution

When instructions conflict between layers:
- More specific instructions override general ones
- Later-loaded files take precedence
- Local overrides always win for the current user

---

## Recursive Lookup Behavior

Claude Code performs **upward directory traversal** when loading memory:

1. Start from current working directory
2. Look for `CLAUDE.md` in current directory
3. Move to parent directory
4. Repeat until reaching filesystem root

### Example Traversal

Working directory: `/home/user/projects/myapp/src/components`

Files checked (in order):
```
/home/user/projects/myapp/src/components/CLAUDE.md
/home/user/projects/myapp/src/CLAUDE.md
/home/user/projects/myapp/CLAUDE.md
/home/user/projects/CLAUDE.md
/home/user/CLAUDE.md
/home/CLAUDE.md
/CLAUDE.md
```

All found files are loaded and merged according to precedence rules.

---

## Subtree Discovery

When Claude accesses files in subdirectories, **nested CLAUDE.md files are automatically discovered and loaded**.

### Behavior

- Memory files in subdirectories load when Claude reads/writes files in those directories
- This allows directory-specific instructions without polluting root memory
- Useful for monorepos with different conventions per package

### Example

```
project/
├── CLAUDE.md              # Project-wide rules
├── packages/
│   ├── frontend/
│   │   └── CLAUDE.md      # Frontend-specific rules (loaded when accessing frontend/)
│   └── backend/
│       └── CLAUDE.md      # Backend-specific rules (loaded when accessing backend/)
```

---

## Quick Memory Addition

The `#` shortcut provides rapid memory updates without opening files.

### Syntax

```
# <instruction to remember>
```

### Behavior

1. Claude presents the instruction
2. Prompts for memory location choice:
   - **Project memory** (`CLAUDE.md`)
   - **User memory** (`~/.claude/CLAUDE.md`)
   - **Project local** (`CLAUDE.local.md`)
3. Appends instruction to chosen file

### Examples

```
# Always use bun instead of npm
# Prefer composition over inheritance
# Run tests before committing
```

---

## The /memory Command

Edit memory files interactively using the `/memory` slash command.

### Usage

```
/memory
```

### Features

- Opens memory file in default editor
- Supports all memory file types
- Validates syntax on save
- Reloads memory after editing

### Common Operations

| Action | Command |
|--------|---------|
| View current memory | `/memory` |
| Add new instruction | `# <instruction>` shortcut |
| Edit project memory | `/memory` then select project |
| Clear memory | Delete content from file |

---

## File Format

All memory files use **Markdown** format with optional structure.

### Recommended Structure

```markdown
# Project Name (optional header)

**Section Header**
- Instruction 1
- Instruction 2

**Another Section**
- More instructions

**Commands**
- `bun test` - Run tests
- `bun build` - Build project
```

### Formatting Guidelines

- Use bullet points for lists of instructions
- Group related instructions under headings
- Keep instructions concise and actionable
- Use code blocks for commands and examples

---

## Common Patterns

### User Memory (`~/.claude/CLAUDE.md`)

Personal preferences applied to all projects:

```markdown
**Preferences**
- Use vim keybindings in examples
- Prefer functional programming patterns
- Always explain reasoning before code

**Communication**
- Be concise
- Skip pleasantries
```

### Project Memory (`./CLAUDE.md`)

Team-shared project conventions:

```markdown
**Code Style**
- Use 2-space indentation
- Prefer const over let
- Use TypeScript strict mode

**Testing**
- Write tests before fixing bugs
- Use descriptive test names

**Commands**
- `bun test` - Run tests
- `bun run dev` - Start dev server
```

### Project Local (`./CLAUDE.local.md`)

Personal project overrides (gitignored):

```markdown
**Local Settings**
- API_KEY is stored in .env.local
- Use port 3001 for dev server (3000 is taken)

**Secrets**
- Test database: postgres://localhost:5432/test_db
```

---

## Related

- [Rules Syntax](./rules-syntax.md) - Path-scoped rule files
- [Best Practices](./best-practices.md) - Writing effective memory and rules
