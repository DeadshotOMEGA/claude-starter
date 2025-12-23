# Statusline System

Universal composable status line with modular providers and hook-driven state updates.

## Structure

```
statusline/
├── statusline.py          # Main script - assembles providers
├── update.py              # CLI for manual state updates
├── state/                 # State files (gitignored)
│   ├── session.json       # Session info
│   ├── agents.json        # Running agents
│   ├── todo.json          # Todo progress
│   └── collab.json        # Collaborative mode (optional)
├── providers/             # Modular segments
│   ├── base.py            # Model, persona, branch
│   ├── collab.py          # Collaborative mode overlay
│   ├── agents.py          # Running agents indicator
│   └── todo.py            # Todo progress
└── hooks/                 # Hook scripts
    ├── agent-tracker.py   # PreToolUse/SubagentStop
    └── todo-tracker.py    # PostToolUse (TodoWrite)
```

## State Files

| File | Updated By | Shows |
|------|------------|-------|
| `agents.json` | agent-tracker hook | Running subagents |
| `todo.json` | todo-tracker hook | Todo progress |
| `collab.json` | collaborative-mode skill | Collab session |

## Adding Providers

1. Create `providers/myprovider.py` with `render(project_dir) -> Optional[str]`
2. Import in `statusline.py`
3. Call in main() and append to segments if non-None

## Manual State Updates

```bash
# Update agents
./update.py agents add explorer
./update.py agents remove explorer
./update.py agents clear

# Update todos
./update.py todo 3 5 "Building component"

# Session tracking
./update.py session start
./update.py session prompt
```
