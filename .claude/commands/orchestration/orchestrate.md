---
description: Execute intelligent workflow orchestration with dynamic agent matching
argument-hint: [requirements or project:requirements]
allowed-tools: Read, Bash, Task, AskUserQuestion
model: opus
---

$ARGUMENTS

## Workflow Orchestration

You are the workflow orchestrator. Execute the complete orchestration flow:

### Phase 1: Parse Input

Parse `$ARGUMENTS` to extract:
- **Project**: If format is `project:requirements`, extract project name
- **Requirements**: The work to be done

If no project specified, attempt auto-detection from requirements.

### Phase 2: Load Registry

Read the registry:
```bash
cat .claude/skills/orchestrating-workflows/registry.json
```

If registry doesn't exist, inform user to run `/sync-registry` first.

### Phase 3: Match Requirements

Run matching script:
```bash
python .claude/skills/orchestrating-workflows/scripts/match_requirements.py "$REQUIREMENTS" -p "$PROJECT" --json
```

Review matched agents and their tiers.

### Phase 4: Build Sequence

Pipe match results to build sequence:
```bash
python .claude/skills/orchestrating-workflows/scripts/match_requirements.py "$REQUIREMENTS" -p "$PROJECT" --json | \
python .claude/skills/orchestrating-workflows/scripts/build_sequence.py --json
```

### Phase 5: Confirm Execution

Present the execution plan to user:

```
Workflow Execution Plan
=======================
Project: [project or shared]
Requirements: [summary]

Stages:
  T0 Git Setup: [agents]
  T1 Explore & Research: [agents]
  T2 Domain Expertise: [agents]
  T3 Planning: [agents]
  T4 Implementation: [agents]
  T5 Validation: [agents]

Total: X agents across Y stages
```

Ask: "Proceed with this execution plan?"

### Phase 6: Execute Stages

For each stage in order:

**Sequential agents first:**
For each sequential agent in the stage:
1. Spawn using Task tool
2. Wait for completion
3. Collect output for context

**Then parallel agents:**
Spawn all parallel agents simultaneously using multiple Task calls in a single message:
```
Task(subagent_type="agent-name", prompt="...")
Task(subagent_type="another-agent", prompt="...")
```

Wait for all to complete before proceeding to next stage.

### Phase 7: Context Passing

Pass relevant context between stages:
- T1 outputs → T2 and T3 agents
- T2 outputs → T3 agents
- T3 plan → T4 agents
- T4 outputs → T5 agents

### Phase 8: Report Completion

Summarize:
- Stages completed
- Agents invoked
- Key outputs/artifacts created
- Any issues encountered

## Execution Rules

1. **Never skip stages** - Execute all matched stages in order
2. **Wait between stages** - Each tier completes before the next
3. **Parallel within tiers** - Spawn parallel agents simultaneously
4. **Pass context forward** - Later stages need earlier outputs
5. **Handle blockers** - If an agent reports [BLOCKER], attempt resolution before continuing

## Error Handling

If an agent fails:
1. Log the failure
2. Attempt once to resolve (spawn appropriate helper agent)
3. If unresolved, report to user and ask how to proceed
4. Continue with remaining agents if user approves

## Skills Reference

Available skills from registry can be invoked as needed:
```
Skill(skill: "skill-name")
```

Use skills for reference and guidance during orchestration.
