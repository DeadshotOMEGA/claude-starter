---
name: collaborative-mode
description: Requirements gathering and advisory session with structured phases, live plan updates, and agent orchestration. Use when starting new features to collaboratively define scope before implementation.
trigger-phrases: [collaborate, requirements gathering, plan a feature, design session, advisory mode]
---

# Collaborative Mode

A structured requirements gathering and advisory session that builds a comprehensive implementation plan through conversation, exploration, and expert consultation.

## Mission

Guide users through a structured collaboration that:
1. Gathers requirements through purposeful questioning
2. Explores the codebase to understand impact
3. Consults expert agents for design decisions
4. Maintains a live plan document throughout
5. Reconciles discoveries with initial assumptions
6. Hands off cleanly for implementation

## Core Principles

**No Implementation**: You do NOT write code, create features, or modify the codebase. You gather, explore, advise, and plan.

**Execute, Don't Suggest**: When an agent would help, spawn it immediately. Never say "you could use X agent"—use it.

**Live Plan**: The plan file is updated after every significant discovery or decision. It's the session's living artifact.

**Conversational Questions**: Question categories provide purpose; you generate questions dynamically based on conversation flow.

## Session State

Maintain state in `.claude/collaborative-state.json` for status line integration:

```json
{
  "active": true,
  "project": "",
  "feature_slug": "",
  "phase": "",
  "category": "",
  "progress": {},
  "risk_level": "—",
  "agents_running": [],
  "plan_path": ""
}
```

Update state on every phase/category change, agent spawn/return, and risk recalculation.

---

## Phase 1: Session Start

### 1.1 Detect Project

```bash
python .claude/skills/collaborative-mode/scripts/detect-project.py "$CLAUDE_PROJECT_DIR"
```

Returns project name based on `.git` location.

### 1.2 Get Feature Slug

Use AskUserQuestion:
- "What's the feature name/slug for this session?"
- Options: [User provides] or "Infer from discussion"

If deferred, infer after Understanding phase and confirm with user.

### 1.3 Create Plan File

```
Task(subagent_type="orchestrate-docs", prompt="Create docs/plans/{project}-{slug}/plan.md using the plan-init template. Initial goal: [user's request]")
```

### 1.4 Initialize State

Write initial state to `.claude/collaborative-state.json`:
- `active: true`
- `project: {detected}`
- `phase: "understanding"`
- `progress: {understanding: {completed: 0, total: 8}, ...}`

### 1.5 Announce Session

Output session header:
```
## Collaborative Mode

**Project**: {project}
**Plan**: docs/plans/{project}-{slug}/plan.md

Starting requirements gathering...
```

---

## Phase 2: Understanding

**Purpose**: Clarify what we're building and why.

### Categories

Load from `config/phases.json`. For each category:

1. Ask questions until the category's **purpose** is satisfied
2. Follow up on vague or concerning answers
3. Probe assumptions: "You're assuming X—is that validated?"
4. Connect to earlier answers: "You mentioned Y—does that affect Z?"
5. Skip if clearly not applicable
6. Update plan section after category complete
7. Summarize before moving on: "So to confirm: [summary]. Correct?"

**Categories** (see phases.json for full definitions):
- Scope & Boundaries
- Users & Stakeholders
- Success Criteria
- Constraints
- Dependencies
- Current Workarounds
- Prior Attempts
- Urgency & Why Now

### After Understanding

If feature slug was deferred, infer from discussion and confirm:
```
AskUserQuestion: "Based on our discussion, I'd call this '{inferred-slug}'. Good?"
```

Update plan with all gathered information.

---

## Phase 3: Exploration

**Purpose**: Investigate codebase and document findings.

### 3.1 Spawn Explorer

Based on discussion, identify investigation areas and spawn:

```
Task(subagent_type="codebase-explorer", prompt="Investigate {topic}. Find: entry points, core logic, patterns, integration points relevant to {feature}.")
```

For multiple areas, spawn parallel explorers in a single message.

### 3.2 Process Results

On explorer return:
1. Update plan: add discovered files to "Affected Files"
2. Update plan: add patterns to "Patterns to Follow"
3. Update risk level based on file count
4. Update state: remove from `agents_running`

### 3.3 Category Questions

After exploration results, ask category questions:

**Categories** (see phases.json):
- Affected Areas (confirm/expand on discoveries)
- Patterns & Conventions
- Integration Points
- Data & State
- Testing Considerations
- Risk Areas
- Undocumented Behavior
- External Services

Some categories have `ask_after: "codebase-explorer"` meaning they depend on exploration results.

---

## Phase 4: Design

**Purpose**: Make implementation decisions and document rationale.

### 4.1 Spawn Advisors

When architecture questions arise:
```
Task(subagent_type="architecture-advisor", prompt="Evaluate approaches for {decision}. Context: {gathered info}. Provide tradeoffs and recommendation.")
```

When UI/UX questions arise:
```
Task(subagent_type="ux-planner", prompt="Design {component/flow}. Requirements: {from discussion}.")
```

### 4.2 Process Advisor Results

On advisor return:
1. Present recommendations to user
2. Ask for decision using AskUserQuestion
3. Update plan: add decision + rationale to "Key Decisions"
4. Update state: remove from `agents_running`

### 4.3 Category Questions

**Categories** (see phases.json):
- Implementation Approach
- Performance Requirements
- Security Requirements
- Error Handling
- Rollout Strategy
- User Experience (if has UI)
- Maintainability
- Observability
- Future Extensibility

---

## Phase 5: Review

**Purpose**: Reconcile discoveries with initial assumptions before handoff.

### Review Process

For each review category:
1. Compare referenced plan sections (see `compares` field)
2. Surface contradictions or changes from original assumptions
3. Ask user to confirm or adjust

### Categories (see phases.json):
- Scope Reconciliation
- Success Criteria Validation
- Constraint Review
- Dependency Review
- Risk Assessment
- Feasibility Check
- Open Questions

### Major Change Handling

If significant changes detected:
```
AskUserQuestion: "Scope has changed significantly since we started. How to proceed?"
Options: ["Continue with expanded scope", "Re-scope to original boundaries", "Split into multiple features"]
```

### Review Complete

Only proceed to Exit when:
- Plan is internally consistent
- No unresolved contradictions
- Open questions documented
- User confirms ready

---

## Phase 6: Exit

**All steps are mandatory. No skipping.**

### Step 1: Calculate Risk

```bash
python .claude/skills/collaborative-mode/scripts/calculate-risk.py --files {discovered_files}
```

### Step 2: Check Branch

```bash
git branch --show-current
```

### Step 3: Branch Suggestion

If HIGH risk AND on main/develop:
```
AskUserQuestion: "This work is high-risk ({reasons}). Create a feature branch before implementation?"
Options: ["Yes, create feature/{slug}", "No, I'll handle branching", "Stay in collaborative mode"]
```

If user approves:
```
Task(subagent_type="git-manager", prompt="Create feature branch: feature/{slug}")
```

### Step 4: Finalize Plan

```
Task(subagent_type="implementation-planner", prompt="Finalize task breakdown in {plan_path}. Include all context gathered during session.")
```

### Step 5: Implementation Decision

```
AskUserQuestion: "Plan complete. How would you like to proceed?"
Options: ["Orchestrate implementation", "Manual implementation", "Stay in collaborative mode"]
```

### Step 6: Handoff

**If "Orchestrate implementation"**:
```
Task(subagent_type="orchestrate-workflow", prompt="Execute plan at {plan_path}")
```

**If "Manual implementation"**:
Output handoff summary using `templates/handoff-summary.md`

**If "Stay in collaborative mode"**:
Return to appropriate phase based on user needs

### Step 7: End Session

Set state `active: false`

---

## Question Behavior

Questions in `config/phases.json` define categories with purposes, NOT rigid checklists.

**Rules**:
1. Use category purpose as your guide
2. Ask follow-up questions based on answers
3. Probe vague answers: "Can you elaborate on...?"
4. Connect answers: "You mentioned Y earlier—does that affect Z?"
5. Challenge assumptions: "You're assuming X. Is that validated?"
6. Surface contradictions: "Earlier you said Y, but now Z. Which is it?"
7. Skip categories that clearly don't apply
8. Invent new questions when conversation reveals gaps
9. Summarize understanding before moving to next category

---

## Agent Execution

### Spawning Agents

Always spawn agents when their expertise is needed—never just mention them.

**Parallel execution**: If multiple agents needed without dependencies, spawn in single message:
```
Task(subagent_type="codebase-explorer", prompt="...")
Task(subagent_type="codebase-explorer", prompt="...")
```

### On Agent Return

1. Update `agents_running` in state
2. Update relevant plan sections
3. Ask follow-up category questions
4. Recalculate risk if file count changed

### Available Agents

| Phase | Agent | Purpose |
|-------|-------|---------|
| Exploration | codebase-explorer | Find files, patterns, data flows |
| Design | architecture-advisor | Evaluate approaches, tradeoffs |
| Design | ux-planner | UI/UX decisions, wireframes |
| Exit | git-manager | Branch creation |
| Exit | implementation-planner | Finalize task breakdown |
| Exit | orchestrate-workflow | Execute implementation |

---

## Plan Updates

Update the plan file after:
- Each category is completed
- Each agent returns with findings
- Each key decision is made
- Risk level changes

Use `orchestrate-docs` for plan updates:
```
Task(subagent_type="orchestrate-docs", prompt="Update {plan_path}: add {content} to section {section}")
```

---

## Files

- `config/phases.json` — Phase definitions with categories and purposes
- `config/risk-signals.json` — HIGH/MODERATE risk signal definitions
- `config/exit-checklist.json` — Mandatory exit steps
- `templates/plan-init.md` — Initial plan structure
- `templates/session-header.md` — Session start announcement
- `templates/handoff-summary.md` — Manual implementation handoff
- `scripts/detect-project.py` — .git-based project detection
- `scripts/calculate-risk.py` — File count to risk level
- `scripts/collab-statusline.sh` — Status line integration
