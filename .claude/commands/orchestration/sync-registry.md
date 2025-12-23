---
description: Sync agent/skill registry for workflow orchestrator
argument-hint: [--force]
allowed-tools: Bash(python3:*, cat:*)
model: haiku
---

Sync the workflow orchestrator registry by scanning all agents and skills.

## Execution

Run the discovery script:

```bash
python3 .claude/skills/orchestrating-workflows/scripts/discover_agents.py
```

## What It Does

1. **Scans shared agents**: `.claude/agents/*.md`
2. **Scans shared skills**: `.claude/skills/*/SKILL.md`
3. **Scans project-specific**: `[project]/.claude/agents/`, `[project]/.claude/skills/`
4. **Uses mtime checking**: Only re-parses files that changed since last sync
5. **Infers metadata**: Tier, category, capabilities from descriptions when not explicit
6. **Writes registry**: `.claude/skills/orchestrating-workflows/registry.json`

## When to Run

- After adding new agents or skills
- After modifying agent/skill descriptions or metadata
- After adding a new project with its own `.claude/` folder
- When agents aren't matching as expected (to refresh inference)

## Output

Report what changed:
- Unchanged (skipped due to same mtime)
- Added (new files)
- Modified (existing files with newer mtime)
- Removed (files that no longer exist)

## Verification

After running, you can verify the registry:

```bash
# Check registry contents
cat .claude/skills/orchestrating-workflows/registry.json | python3 -m json.tool | head -50

# Test matching
python3 .claude/skills/orchestrating-workflows/scripts/match_requirements.py "test query"
```
