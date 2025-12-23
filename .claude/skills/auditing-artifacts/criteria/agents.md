# Agent Audit Criteria

Scoring criteria for `.claude/agents/*.md` files based on official sub-agents documentation.

## Structure (5 points)

### Frontmatter Completeness (3 points)
- **3 pts:** All required + relevant optional fields present and valid
  - Required: `name`, `description`
  - Optional: `tools`, `model`, `permissionMode`, `skills`, `color`
  - Registry metadata (if using workflow orchestrator): `tiers`, `category`, `capabilities`, `triggers`, `parallel`
- **2 pts:** Required fields present, key optional fields included
- **1 pt:** Only required fields, missing useful optionals
- **0 pts:** Missing required fields or invalid YAML

### Content Organization (1 point)
- **1 pt:** Follows recommended prompt structure (role → when invoked → focus areas → approach → output → checklist)
- **0 pts:** Disorganized or unclear structure

### Appropriate Length (1 point)
- **1 pt:** 30-100 lines (simple to standard agents)
- **0 pts:** <30 lines (too thin) or >100 lines (should split or use skills)

**Common Issues:**
- `name` doesn't match filename
- `description` missing "PROACTIVELY" for auto-delegation
- Missing `tools` when agent should have restricted access
- Missing registry metadata when using workflow orchestrator

## Clarity (4 points)

### Purpose Statement (1 point)
- **1 pt:** `description` clearly states role, domain, and when to use
- **0 pts:** Vague or unclear description

### Usage Examples (1 point)
- **1 pt:** Shows when Claude should invoke this agent
- **0 pts:** No usage guidance

### Output Format (1 point)
- **1 pt:** Clearly states what agent delivers (report, fixes, analysis, etc.)
- **0 pts:** Unclear deliverables

### Proactive Triggers (1 point)
- **1 pt:** Description includes "Use PROACTIVELY" or "MUST BE USED"
- **0 pts:** Missing proactive language

**Good Description Examples:**
- "Database migration specialist. Use PROACTIVELY for schema changes, RLS policies, and production database modifications."
- "Code review specialist. Use PROACTIVELY after writing or modifying code to ensure high development standards."

**Bad Description Examples:**
- "Helps with databases"
- "Does code review stuff"

## Technical (5 points)

### Naming Convention (2 points)
- **2 pts:** Follows domain-first, tier-suffix pattern (`[domain]-[suffix]`)
  - Tier suffixes: `-manager`, `-explorer`, `-researcher`, `-advisor`, `-planner`, `-architect`, `-builder`, `-optimizer`, `-checker`, `-reviewer`
  - Special case: `orchestrate-[scope]` for orchestrators
- **1 pt:** Name is descriptive but doesn't follow pattern
- **0 pts:** Poor naming (abbreviations, generic names like "helper")

### Tools Selection (1 point)
- **1 pt:** Appropriate tools for agent's purpose, or omitted to inherit all
- **0 pts:** Too many tools, wrong tools, or restrictive when shouldn't be

### Tier Metadata (1 point)
- **1 pt:** Registry metadata present with correct tier(s) for agent's role
- **0 pts:** Missing metadata or incorrect tier assignment

### Model Selection (1 point)
- **1 pt:** Appropriate model choice (haiku for speed, sonnet default, opus for complex, inherit for consistency)
- **0 pts:** Wrong model or missing when non-default would be better

**Naming Examples:**

**Good:**
- `codebase-explorer` (domain: codebase, tier 1: -explorer)
- `security-advisor` (domain: security, tier 2: -advisor)
- `frontend-builder` (domain: frontend, tier 4: -builder)
- `test-checker` (domain: test, tier 5: -checker)

**Bad:**
- `explorer` (missing domain)
- `db-helper` (abbreviation + wrong suffix)
- `senior-architect` (seniority prefix)
- `nextjs-expert` (non-standard suffix)

**Tool Selection Patterns:**

| Agent Type | Tools |
|------------|-------|
| Read-only research | `Read, Grep, Glob` |
| Code review | `Read, Grep, Glob, Bash` |
| Implementation | `Read, Write, Edit, Bash, Glob, Grep` |
| Web research | `WebSearch, WebFetch, Read, Write` |
| Full access | Omit field to inherit all |

## Operational (4 points)

### Delegation Clarity (1 point)
- **1 pt:** Clear when/how agent delegates to other agents or uses skills
- **0 pts:** Unclear delegation strategy

### Permission Awareness (1 point)
- **1 pt:** Appropriate `permissionMode` if agent needs special permissions
- **0 pts:** Missing permission mode when needed (e.g., auto-accepting edits)

### Error Handling (1 point)
- **1 pt:** Instructions on handling failures or blockers
- **0 pts:** No error handling guidance

### "When Invoked" Section (1 point)
- **1 pt:** Has clear "When invoked" section with 1-3 immediate first steps
- **0 pts:** Missing "when invoked" or unclear first actions

**Permission Modes:**

| Mode | Use Case |
|------|----------|
| `default` | Ask for permission normally |
| `acceptEdits` | Auto-accept file edits |
| `bypassPermissions` | Skip permission prompts |
| `plan` | Plan mode (research only) |
| `ignore` | No permission handling |

## Maintainability (2 points)

### No Hardcoded Values (1 point)
- **1 pt:** No hardcoded paths, file names, or magic values
- **0 pts:** Contains hardcoded values

### Dependencies Documented (1 point)
- **1 pt:** Skills, external tools, or special requirements documented
- **0 pts:** Uses tools/skills without mentioning them

**Skills Field:**
If agent always needs certain skills, list them:
```yaml
skills: writing-commit-messages, applying-git-flow
```

## Red Flags (Automatic Deductions)

- **-2 pts:** Name doesn't match filename
- **-2 pts:** No registry metadata when workflow orchestrator is in use
- **-1 pt:** Description missing "PROACTIVELY"
- **-1 pt:** >100 lines without clear justification
- **-1 pt:** Contains XML tags in description
- **-1 pt:** Uses abbreviations in name (`db-`, `fe-`, etc.)

## Excellent Agent Checklist

An 18-20 point agent has:

- ✅ Follows naming convention: `[domain]-[tier-suffix]`
- ✅ Complete frontmatter with required fields
- ✅ Description includes "Use PROACTIVELY" + specific trigger scenarios
- ✅ Appropriate tier-based `color` field
- ✅ Registry metadata (tiers, category, capabilities, triggers, parallel)
- ✅ Restricted `tools` list (only what's needed) or omitted for full access
- ✅ Appropriate `model` choice for task complexity
- ✅ Clear "When invoked" section with first 1-3 actions
- ✅ Organized prompt structure
- ✅ Focus areas clearly stated
- ✅ Step-by-step approach documented
- ✅ Output/deliverables specified
- ✅ Quality checklist for self-validation
- ✅ Error handling instructions
- ✅ 30-100 lines (appropriate length)
- ✅ No hardcoded values
- ✅ Skills/dependencies documented if used

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| Name violates pattern | Rename to `[domain]-[tier-suffix]` |
| Missing PROACTIVELY | Add "Use PROACTIVELY" to description |
| Missing registry metadata | Add HTML comment block with tiers, category, capabilities, triggers |
| Wrong tier suffix | Use tier-appropriate suffix (-manager, -explorer, -advisor, -planner, -builder, -checker) |
| No color field | Add tier-based color (0:gray, 1:cyan, 2:magenta, 3:yellow, 4:green, 5:blue) |
| Too many tools | Restrict to only necessary tools |
| No "when invoked" section | Add section with 1-3 first actions |
| Missing output spec | Add section describing deliverables |
| >100 lines | Split into multiple agents or delegate to skills |
| Hardcoded paths | Use arguments or dynamic detection |
| Uses abbreviations | Spell out full words (database not db) |
| Missing error handling | Add instructions for failure scenarios |

## Registry Metadata Format

```html
<!-- workflow-orchestrator-registry
tiers: [2, 5]
category: expertise
capabilities: [code-review, security, quality]
triggers: [review, security, audit, code-reviewer]
parallel: true
-->
```

**Tier to Suffix Mapping:**

| Tier | Suffix(es) |
|------|------------|
| 0 | `-manager` |
| 1 | `-explorer`, `-researcher` |
| 2 | `-advisor` |
| 3 | `-planner`, `-architect` |
| 4 | `-builder`, `-optimizer` |
| 5 | `-checker`, `-reviewer` |

**Multi-tier agents:** Use primary tier's suffix, list all tiers in metadata.
