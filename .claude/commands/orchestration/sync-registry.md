---
description: Sync agent and skill registries for workflow orchestrator
argument-hint: [--force]
allowed-tools: Bash(python3:*, cat:*)
model: haiku
---

Sync the workflow orchestrator registries by scanning all agents and skills.

## Execution

Run both discovery scripts:

```bash
python3 .claude/skills/orchestrating-workflows/scripts/discover_agents.py && \
python3 .claude/skills/orchestrating-workflows/scripts/discover_skills.py
```

## What It Does

### Agents Registry
1. **Scans shared agents**: `.claude/agents/*.md`
2. **Scans project-specific**: `[project]/.claude/agents/`
3. **Uses mtime checking**: Only re-parses files that changed since last sync
4. **Infers metadata**: Tier, category, capabilities from descriptions when not explicit
5. **Writes registry**: `.claude/registries/agents-registry.json`

### Skills Registry
1. **Scans skills**: `.claude/skills/*/SKILL.md`
2. **Merges config**: Combines discovered skills with `.claude/registries/skills-config.json`
3. **Writes registry**: `.claude/registries/skills-registry.json`

## When to Run

- After adding new agents or skills
- After modifying agent/skill descriptions or metadata
- After updating skills-config.json
- After adding a new project with its own `.claude/` folder
- When agents aren't matching as expected (to refresh inference)

## Output

Report what changed:
- Agents: Unchanged, added, modified, removed
- Skills: Discovered, configured, missing config

## Verification

After running, you can verify the registries:

```bash
# Check agents registry
cat .claude/registries/agents-registry.json | python3 -m json.tool | head -50

# Check skills registry
cat .claude/registries/skills-registry.json | python3 -m json.tool | head -50

# Test agent matching
python3 .claude/skills/orchestrating-workflows/scripts/match_requirements.py "test query"
```
