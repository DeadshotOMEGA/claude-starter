---
name: writing-subagents
description: Write and review Claude Code subagent definitions following official best practices. Use when creating, editing, or auditing .claude/agents/*.md files.
---

# Subagent Writing

Write and validate Claude Code subagent definitions per official specification.

## Contents

- [Frontmatter Specification](#frontmatter-specification)
- [Naming Convention](#naming-convention)
- [Registry Metadata](#registry-metadata)
- [Description Best Practices](#description-best-practices)
- [Tools Selection](#tools-selection)
- [Model Selection](#model-selection)
- [Prompt Structure](#prompt-structure)
- [Built-in Subagents](#built-in-subagents)
- [Plugin Agents](#plugin-agents)
- [CLI Configuration](#cli-configuration)
- [Resumable Subagents](#resumable-subagents)
- [Advanced Usage](#advanced-usage)
- [Template](#template)
- [Validation](#validation)
- [Common Issues](#common-issues)

## Frontmatter Specification

**Required Fields:**

| Field | Format | Notes |
|-------|--------|-------|
| `name` | lowercase-with-hyphens | Must match filename (without .md) |
| `description` | Natural language | Include "PROACTIVELY" for auto-delegation |

### Name Field

Agent names must follow the **Naming Convention** pattern defined below. Names use domain-first structure with tier-appropriate suffixes.

> **Note:** This differs from skills, which use action-first naming (`processing-pdfs`, `writing-documentation`) because skills describe *actions*, not roles.

## Naming Convention

**Required Pattern:** `[domain]-[tier-suffix]`

All agent names must follow the domain-first, tier-suffix pattern:

| Tier | Stage | Allowed Suffixes | Examples |
|------|-------|------------------|----------|
| 0 | Git Setup | `-manager` | `git-manager` |
| 1 | Explore | `-explorer`, `-researcher` | `codebase-explorer`, `web-researcher` |
| 2 | Expertise | `-advisor` | `database-advisor`, `security-advisor` |
| 3 | Planning | `-planner`, `-architect` | `task-planner`, `schema-architect` |
| 4 | Implementation | `-builder`, `-optimizer` | `frontend-builder`, `react-optimizer` |
| 5 | Validation | `-checker`, `-reviewer` | `test-checker`, `code-reviewer` |
| — | Cross-tier | `orchestrate-[scope]` | `orchestrate-workflow` |

### Naming Rules

1. **Domain-first**: The subject/domain comes before the action suffix
2. **Tier-suffix**: Suffix indicates the agent's primary tier
3. **Multi-tier agents**: Use suffix of the primary/most-common tier
4. **Orchestrators**: Follow special pattern `orchestrate-[scope]`
5. **No abbreviations**: Use full words (`database-` not `db-`)
6. **No seniority prefixes**: Avoid `senior-`, `junior-`, `lead-`

### Naming Examples

**Good:**
- `codebase-explorer` (tier 1, explores codebase)
- `security-advisor` (tier 2, advises on security)
- `frontend-builder` (tier 4, builds frontend)

**Bad:**
- `explorer` (missing domain)
- `senior-architect` (seniority prefix)
- `db-modifier` (abbreviation)
- `nextjs-architecture-expert` (non-standard suffix)

**Optional Fields:**

| Field | Values | Default |
|-------|--------|---------|
| `tools` | Comma-separated tool names | Inherits all from parent |
| `model` | `sonnet`, `opus`, `haiku`, `inherit` | `sonnet` |
| `permissionMode` | `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore` | `default` |
| `skills` | Comma-separated skill names | None |
| `color` | Color name for UI display | None |

### Color Field

The `color` field controls visual display in Claude Code's UI. Use tier-based colors for consistency:

| Tier | Stage | Color |
|------|-------|-------|
| 0 | Git Setup | `gray` |
| 1 | Explore & Research | `cyan` |
| 2 | Domain Expertise | `magenta` |
| 3 | Planning | `yellow` |
| 4 | Implementation | `green` |
| 5 | Validation | `blue` |

**Multi-tier agents**: Use the color of the primary/most common tier.

**Valid colors**: `gray`, `cyan`, `magenta`, `yellow`, `green`, `blue`, `orange`, `red`

**File Locations:**

| Type | Location | Scope | Priority |
|------|----------|-------|----------|
| Project | `.claude/agents/` | Current project only | Highest |
| CLI | `--agents` flag | Current session | Middle |
| User | `~/.claude/agents/` | All projects | Lowest |

When names conflict, higher priority agents take precedence.

## Registry Metadata

> **Note:** This is a project-specific extension for workflow-orchestrator integration, not part of official Claude Code.

Add an HTML comment block AFTER the closing `---`:

```html
<!-- workflow-orchestrator-registry
tiers: [2, 4]
category: expertise
capabilities: [keywords, for, matching]
triggers: [activation, words]
parallel: true
-->
```

**Registry Fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `tiers` | array | Numbers [0-5] for workflow orchestration phases |
| `category` | string | One of: explore, expertise, implementation, git, planning, research |
| `capabilities` | array | Keywords for requirement matching |
| `triggers` | array | Words that activate this agent |
| `parallel` | boolean | Can run alongside other agents (default: true) |

**Tier Definitions:**

| Tier | Name | Purpose |
|------|------|---------|
| 0 | Git Setup | Branch creation, git flow |
| 1 | Explore & Research | Investigation, research |
| 2 | Domain Expertise | Specialist consultation |
| 3 | Planning | Implementation planning |
| 4 | Implementation | Code changes |
| 5 | Validation | Testing, review |

## Description Best Practices

The description is critical for automatic delegation. Claude uses it to decide when to invoke your agent.

**Good:**
```
Database migration specialist. Use PROACTIVELY for schema changes, RLS policies, and production database modifications.
```

**Bad:**
```
Helps with database stuff.
```

**Include:**
- Specific role/domain expertise
- "Use PROACTIVELY" for automatic delegation
- Concrete trigger scenarios (what tasks should invoke this agent)

## Tools Selection

Only grant tools necessary for the agent's purpose. Fewer tools = more focused agent + better security.

**Common Patterns:**

| Use Case | Tools |
|----------|-------|
| Read-only research | `Read, Grep, Glob` |
| Code review | `Read, Grep, Glob, Bash` |
| Implementation | `Read, Write, Edit, Bash, Glob, Grep` |
| Web research | `WebSearch, WebFetch, Read, Write` |
| Full access | Omit `tools` field to inherit all |

**MCP Tools:** Subagents can access MCP tools from configured MCP servers. When the `tools` field is omitted, subagents inherit all MCP tools available to the main thread.

## Model Selection

| Model | When to Use |
|-------|-------------|
| `sonnet` | Default. Balanced performance for most tasks. |
| `opus` | Complex reasoning, architecture decisions, nuanced analysis. |
| `haiku` | Fast, simple tasks, high-volume operations. |
| `inherit` | Match parent conversation's model for consistency. |

## Prompt Structure

Organize the agent prompt with these sections:

1. **Role statement** — Clear identity and expertise (1-2 sentences)
2. **When invoked** — First actions to take (1-3 numbered steps)
3. **Focus areas** — Domain expertise bullets
4. **Approach** — Step-by-step process
5. **Output** — Deliverables and formats
6. **Quality checklist** — Self-validation before completing

**Length Guidelines:**
- 30-50 lines: Simple, focused agents
- 50-100 lines: Standard agents with detailed process
- 100+ lines: Consider splitting into multiple agents or using Skills

## Built-in Subagents

Claude Code includes three built-in subagents. Understand these to avoid duplicating functionality:

### General-purpose
- **Model:** Sonnet
- **Tools:** All tools
- **Purpose:** Complex multi-step tasks requiring both exploration and modification
- **When used:** Tasks with multiple dependent steps, complex reasoning needed

### Plan
- **Model:** Sonnet
- **Tools:** Read, Glob, Grep, Bash (read-only)
- **Purpose:** Research during plan mode
- **When used:** Automatically in plan mode when Claude needs codebase context

### Explore
- **Model:** Haiku (fast)
- **Tools:** Glob, Grep, Read, Bash (read-only)
- **Purpose:** Fast codebase searching and analysis
- **When used:** Searching/understanding code without making changes
- **Thoroughness levels:** Quick, Medium, Very thorough

## Plugin Agents

Plugins can provide custom subagents that integrate with Claude Code:

- Plugin agents live in the plugin's `agents/` directory
- Appear in `/agents` alongside custom agents
- Can be invoked explicitly or automatically
- Priority: Project > CLI > Plugin > User

## CLI Configuration

Define subagents dynamically without creating files:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

**Use cases:**
- Quick testing of configurations
- Session-specific subagents
- Automation scripts
- Sharing definitions in documentation

## Resumable Subagents

Subagents can be resumed to continue previous conversations:

**How it works:**
- Each execution gets a unique `agentId`
- Conversation stored in `agent-{agentId}.jsonl`
- Resume with the `resume` parameter to continue with full context

**Example workflow:**
```
> Use code-analyzer to review the auth module
[Agent completes, returns agentId: "abc123"]

> Resume agent abc123 and now analyze authorization logic
[Agent continues with previous context]
```

**Use cases:**
- Long-running research across sessions
- Iterative refinement without losing context
- Multi-step workflows with maintained state

**Programmatic usage:**
```typescript
{
  "description": "Continue analysis",
  "prompt": "Now examine error handling patterns",
  "subagent_type": "code-analyzer",
  "resume": "abc123"
}
```

## Advanced Usage

### Chaining Subagents

For complex workflows, chain multiple subagents:

```
> First use code-analyzer to find performance issues, then use optimizer to fix them
```

### Dynamic Selection

Claude intelligently selects subagents based on context. Make `description` fields specific and action-oriented for best matching.

## Template

Use `template.md` in this Skill directory for new agents:

```bash
cat .claude/skills/writing-subagents/template.md
```

## Validation

Before committing a new or modified agent:

```bash
python .claude/skills/writing-subagents/scripts/validate-agent.py .claude/agents/agent-name.md
```

**Checks performed:**
- Required fields present (`name`, `description`)
- Name matches filename
- Description includes proactive trigger phrase
- Tools are valid tool names
- Model is valid alias
- permissionMode is valid value

## Common Issues

| Issue | Solution |
|-------|----------|
| Agent not triggering automatically | Add "Use PROACTIVELY" to description |
| Name doesn't match filename | Ensure `name:` field matches `filename.md` |
| Too many tools granted | Remove unused tools for focus |
| Prompt too complex | Split into multiple agents or use Skills |
| Duplicating built-in functionality | Check if General-purpose, Plan, or Explore already handles your use case |

## References

- [Official Subagents Documentation](references/official-spec.md)
- [Template](template.md)
