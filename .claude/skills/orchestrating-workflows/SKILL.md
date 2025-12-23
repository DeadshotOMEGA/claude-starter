---
name: orchestrating-workflows
description: Intelligent workflow coordination using dynamic agent registry. Matches requirements to agents, sequences execution by tier, handles project-specific agents. Use when orchestrating complex multi-phase work.
---

# Orchestrating Workflows

Coordinate complex workflows by dynamically matching requirements to available agents and executing them in the proper sequence.

## Quick Start

```bash
# Sync registries (run when agents/skills change)
python .claude/skills/orchestrating-workflows/scripts/discover_agents.py
python .claude/skills/orchestrating-workflows/scripts/discover_skills.py

# Match requirements to agents
python .claude/skills/orchestrating-workflows/scripts/match_requirements.py "implement user authentication" -p sentinel

# Build execution sequence
python .claude/skills/orchestrating-workflows/scripts/match_requirements.py "..." --json | \
python .claude/skills/orchestrating-workflows/scripts/build_sequence.py
```

## Tier System

Agents are organized into execution tiers. Each tier completes before the next begins.

| Tier | Name | Purpose | Parallel? |
|------|------|---------|-----------|
| 0 | Git Setup | Branch creation, git flow | No |
| 1 | Explore & Research | Codebase investigation, external research | Yes |
| 2 | Domain Expertise | Consult specialists for guidance | Yes |
| 3 | Planning | Create implementation plans | No |
| 4 | Implementation | Execute code changes | Yes* |
| 5 | Validation | Testing, review, verification | Yes |

*Tier 4 parallelism respects task dependencies from the plan.

## Registry Structure

Two separate registries:

### Agents Registry (`.claude/registries/agents-registry.json`)

```json
{
  "shared": {
    "agents": { ... }
  },
  "projects": {
    "project-name": {
      "keywords": ["detection", "keywords"],
      "agents": { ... }
    }
  }
}
```

Project agents **override** shared agents with the same name.

### Skills Registry (`.claude/registries/skills-registry.json`)

```json
{
  "skills": {
    "skill-name": {
      "domain": "writing|testing|devops|security|research|orchestration|reference",
      "what": "Description",
      "when": "Activation conditions",
      "why": "Exclusion criteria",
      "priority": 1,
      "path": "@.claude/skills/skill-name/SKILL.md"
    }
  }
}
```

Skills metadata is curated in `.claude/registries/skills-config.json`.

## Agent Metadata

Each agent in the registry has:

```json
{
  "tiers": [2, 5],  // Can belong to multiple tiers
  "category": "git|explore|research|expertise|planning|implementation|validation",
  "capabilities": ["what", "it", "can", "do"],
  "triggers": ["keywords", "that", "match", "requirements"],
  "parallel": true,
  "path": ".claude/agents/agent-name.md",
  "mtime": 1234567890.0
}
```

**Multi-tier agents**: Agents can belong to multiple tiers. For example, `code-reviewer` might be in tiers `[2, 5]` to provide architecture guidance (tier 2) AND validation review (tier 5). The agent appears in each tier's stage during execution.

## Scripts Reference

### discover_agents.py

Scans and catalogs all agents.

```bash
python scripts/discover_agents.py
```

Features:
- Scans `.claude/agents/` (shared) and `*/claude/agents/` (projects)
- Uses file mtime for incremental sync (only re-parses changed files)
- Infers tier/capabilities from descriptions when not explicit
- Outputs `agents-registry.json`

### discover_skills.py

Scans and catalogs all skills.

```bash
python scripts/discover_skills.py
```

Features:
- Scans `.claude/skills/*/SKILL.md`
- Merges discovered skills with `.claude/registries/skills-config.json`
- Outputs `skills-registry.json` optimized for hook evaluation

### match_requirements.py

Matches requirements text to agents.

```bash
# Basic usage
python scripts/match_requirements.py "implement new feature"

# With project context
python scripts/match_requirements.py "add heroui components" -p sentinel

# Auto-detect project from requirements
python scripts/match_requirements.py "add heroui button" --detect-project

# JSON output for piping
python scripts/match_requirements.py "..." --json
```

Scoring:
- Trigger match: 10 points
- Capability match: 5 points
- Description keyword: 1 point
- Default threshold: 5.0

### build_sequence.py

Builds execution plan from matched agents.

```bash
# From file
python scripts/build_sequence.py match_results.json

# From pipe
python scripts/match_requirements.py "..." --json | python scripts/build_sequence.py

# Generate orchestrator prompt
python scripts/build_sequence.py match.json --prompt -r "original requirements"
```

## Orchestration Flow

```
/collaborate or /orchestrate
         │
         ▼
┌─────────────────────────────────┐
│ 1. Load agents-registry.json    │
│ 2. Detect/confirm project       │
│ 3. Match requirements → agents  │
│ 4. Build execution sequence     │
│ 5. Clear stale StatusLine state │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Execute by tier:                │
│                                 │
│ T0: git-flow-manager            │
│     ↓ wait                      │
│ T1: explorer, research-* (||)  │  ← update.py agents add/remove
│     ↓ wait                      │
│ T2: database-admin, security-* │  ← update.py agents add/remove
│     ↓ wait                      │
│ T3: implementation-planner      │  ← update.py agents add/remove
│     ↓ wait                      │
│ T4: programmer, junior-* (||)  │  ← update.py agents add/remove
│     ↓ wait                      │
│ T5: test-engineer, reviewer    │  ← update.py agents add/remove
│     ↓                           │
│ Clear all agents                │
└─────────────────────────────────┘
```

## Adding Agent Metadata

To ensure proper tier assignment, add frontmatter to agents:

```yaml
---
name: my-agent
description: Does specific things
tiers: [2, 5]     # Multiple tiers (or use tier: 2 for single)
category: expertise
capabilities: [specific, things, it, does]
triggers: [keywords, that, activate, it]
parallel: true
---
```

If not specified, the sync script infers tiers from description (may match multiple tiers).

## Project Detection

Projects are detected by:
1. Explicit argument: `/collaborate sentinel`
2. Keywords in requirements matching `projects[name].keywords`
3. File paths mentioned: `sentinel/src/...` → sentinel

## Merge Behavior

When project is active:
1. Start with all shared agents
2. Overlay project-specific agents
3. Same name = project version wins

Example:
- Shared: `programmer`, `debugger`
- Sentinel: `heroui-guardian`, `debugger` (custom)
- Result: `programmer` (shared), `heroui-guardian` (sentinel), `debugger` (sentinel's version)

## Integration Points

### From /collaborate

On exit with high-risk work:
1. Summarize requirements from session
2. Run match_requirements.py with project context
3. Build sequence
4. Spawn orchestrate-workflow agent with sequence

### From /orchestrate

Direct invocation:
1. Accept requirements + optional project
2. Run matching and sequencing
3. Execute immediately

### StatusLine Updates

During execution, the orchestrator updates StatusLine state:
- Agents tracked in `.claude/statusline/state/agents.json`
- Use `python .claude/statusline/update.py agents add/remove <name>`
- Status displays as `🔧 agent1, agent2` in terminal

## Best Practices

1. **Run /sync-registry** after adding/modifying agents
2. **Add explicit metadata** to agents for accurate matching
3. **Use project context** when working on specific codebases
4. **Check match scores** - low scores may indicate missing triggers
5. **Review execution plan** before large orchestrations

## StatusLine Integration

The orchestrator integrates with the StatusLine system for real-time workflow visibility.

### Agent Tracking

Update agents state when spawning/completing agents:

```bash
# When spawning agent
python .claude/statusline/update.py agents add "explorer"

# When agent completes
python .claude/statusline/update.py agents remove "explorer"

# Clear at workflow end
python .claude/statusline/update.py agents clear
```

### State File

Running agents tracked in `.claude/statusline/state/agents.json`:

```json
{
  "running": ["explorer", "programmer"],
  "last_updated": "2025-01-15T10:30:00"
}
```

### Display Format

The agents provider renders as: `🔧 explorer, programmer`

### Workflow Lifecycle

1. **Start**: Clear any stale agents with `agents clear`
2. **Per Tier**: Add agents when spawning, remove when complete
3. **End**: Clear all agents

## Troubleshooting

**Agent not matching?**
- Check triggers in agents-registry.json
- Add explicit triggers to agent frontmatter
- Lower threshold: `--threshold 3.0`

**Wrong tier?**
- Add explicit `tier: N` to agent frontmatter
- Run /sync-registry to update

**Project not detected?**
- Add keywords to project in agents-registry
- Use explicit `-p project` flag

**Hook not showing skills?**
- Check that skills-registry.json exists
- Verify skills-config.json has metadata for all skills
- Run /sync-registry to regenerate
