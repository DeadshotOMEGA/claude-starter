---
description: Enter collaborative mode - structured requirements gathering with live plan updates
argument-hint: [feature description]
allowed-tools: Read, Grep, Glob, Bash, AskUserQuestion, Write, Task, TodoWrite
model: sonnet
---

# Collaborative Mode

$ARGUMENTS

Load and execute the collaborative-mode skill:

1. Read `.claude/skills/collaborative-mode/SKILL.md` for behavior rules
2. Read `.claude/skills/collaborative-mode/config/phases.json` for phase definitions
3. Follow the skill instructions exactly

## Quick Reference

**Phases**: Session Start → Understanding → Exploration → Design → Review → Exit

**Your role**: Gather requirements, explore codebase, consult experts, build plan. NO implementation.

**Key behaviors**:
- Execute agents when needed (don't just suggest them)
- Update plan after every discovery/decision
- Ask follow-up questions based on answers
- All exit steps are mandatory

## Begin

Start by running the Session Start phase from SKILL.md.
