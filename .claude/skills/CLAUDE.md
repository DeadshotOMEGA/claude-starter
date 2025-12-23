**Skills Directory**

Skills are reusable expertise packages invoked via the Skill tool.

**Structure**
Each skill is a directory containing:
- `SKILL.md` — Main skill definition and instructions
- Additional `.md` files for supplementary context
- Optional `scripts/`, `references/`, `assets/` directories

**Creating Skills**
- Use the `skills` skill for comprehensive guidance
- Run `python3 scripts/init_skill.py` to initialize new skills
- Focus on a specific domain or capability
- Include trigger phrases in description

**Invocation**
```
Skill(skill: "skill-name")
```

**Available Skills**
- `writing-skills` — Create and manage skills
- `managing-memory` — Audit and manage CLAUDE.md and rules
- `executing-parallel-work` — Agent coordination
- `testing-playwright` — E2E testing (includes webapp automation)
- `auditing-security` — Vulnerability analysis
- `referencing-typescript-sdk` — Agent SDK reference
- `processing-spreadsheets` — Spreadsheet creation and analysis
- `writing-commit-messages` — Writing commit messages
- `crafting-prompts` — Prompt engineering
