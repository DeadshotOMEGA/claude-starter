# Skills Directory Audit Report

**Date:** 2024-12-05
**Audited by:** Claude (Opus 4.5)

## Executive Summary

**Total Skills Reviewed:** 17 skills
**Recommendation:** Keep 15, revise 2, consider consolidation of 2

| Rating | Skills |
|--------|--------|
| ✅ Excellent | skill-creator, skills-guide, playwright-testing, typescript-sdk-reference, xlsx, git-commit-helper |
| 🟢 Good | bug-fixing-protocol, investigating, planning, security-auditing, parallel-execution, prompting-effectively |
| 🟡 Needs Revision | code-reviewing, testing-protocol, documenting-code, requirements-gathering |
| 🔴 Consider Deletion/Merge | llm-documentation, webapp-testing |

---

## Individual Skill Reviews

### 1. **skill-creator** ✅ Excellent

**Purpose:** Guide for creating effective skills
**Lines:** ~210 | **Has Scripts:** ✅ (init_skill.py, package_skill.py, quick_validate.py)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Clear "what + when" pattern |
| Naming | ⚠️ | Uses noun form, should be "Creating Skills" |
| Writing Style | ✅ | Proper imperative form throughout |
| Conciseness | ✅ | Well-structured, no fluff |
| Bundled Resources | ✅ | Excellent utility scripts |
| Progressive Disclosure | ✅ | Main file + scripts pattern |

**Verdict:** KEEP - Essential meta-skill for maintaining the skills system.

---

### 2. **skills-guide** ✅ Excellent

**Purpose:** Comprehensive guide to understanding and using skills
**Lines:** ~422

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Excellent specificity |
| Naming | ⚠️ | "Skills Guide" vs gerund "Managing Skills" |
| Writing Style | ✅ | Clean, direct instructions |
| Conciseness | 🟡 | Slightly long but justified - reference doc |
| Examples | ✅ | Excellent code examples throughout |
| Structure | ✅ | Great TOC, progressive disclosure |

**Verdict:** KEEP - Valuable reference documentation.

**Potential Consolidation:** Could merge with skill-creator to create a single "skills" skill with main guide + creator workflow.

---

### 3. **bug-fixing-protocol** 🟢 Good

**Purpose:** Systematic debugging workflow
**Lines:** ~148

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Clear triggers ("broken", "errors", "unexpected behavior") |
| Naming | ✅ | "Fixing Bugs Systematically" is good gerund form |
| Writing Style | ✅ | Imperative throughout |
| Conciseness | ✅ | Well-structured steps |
| Practical Value | 🟡 | References non-existent paths (`docs/feature-spec/F-##-*.md`) |

**Issues:**
- References `./agent-responses/await {agent_id}` which may not exist
- Assumes specific project structure that may not apply universally

**Verdict:** KEEP with minor revision - Remove project-specific assumptions or make them conditional.

---

### 4. **code-reviewing** 🟡 Needs Revision

**Purpose:** Systematic code review
**Lines:** ~198

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good triggers |
| Naming | ✅ | "Reviewing Code" - proper gerund |
| Writing Style | ✅ | Good imperative form |
| Practical Value | 🟡 | Heavy doc references that won't exist |

**Issues:**
- Assumes `docs/feature-spec/`, `docs/user-stories/`, `docs/api-contracts.yaml` exist
- Scoring system (X/100) adds unnecessary overhead
- Too template-heavy for general use

**Recommendation:** Simplify to focus on code review principles rather than project-specific workflows.

---

### 5. **documenting-code** 🟡 Needs Revision

**Purpose:** Documentation maintenance
**Lines:** ~113

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Clear triggers |
| Naming | ✅ | Proper gerund form |
| Practical Value | ❌ | Entirely dependent on init-project template |

**Critical Issues:**
- References `/file-templates/init-project/CLAUDE.md` that doesn't exist
- Assumes YAML-based docs (`feature-specs/F-##-slug.yaml`)
- Validation commands (`/manage-project/...`) don't exist
- Bash utilities (`./check-project.sh`) don't exist

**Verdict:** DELETE or MAJOR REWRITE - Too coupled to non-existent infrastructure. If there's no init-project template, this skill is useless.

---

### 6. **git-commit-helper** ✅ Excellent

**Purpose:** Generate commit messages from diffs
**Lines:** ~204

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Simple, clear |
| Naming | ⚠️ | Noun form - should be "Writing Commit Messages" |
| Writing Style | ✅ | Great examples |
| Conciseness | ✅ | Appropriate depth |
| Examples | ✅ | Excellent input/output examples |
| Self-Contained | ✅ | No external dependencies |

**Verdict:** KEEP - Practical, self-contained, well-structured.

---

### 7. **investigating** 🟢 Good

**Purpose:** Code exploration and flow tracing
**Lines:** ~213

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Excellent trigger coverage |
| Naming | ✅ | "Investigating Code Patterns" - proper gerund |
| Structure | ✅ | Great templates (flow, location, perf, architecture) |
| Writing Style | ✅ | Clear imperative instructions |
| Practical Value | 🟡 | Some doc references may not exist |

**Minor Issue:** References `docs/product-requirements.md` etc. that may not exist universally.

**Verdict:** KEEP - Very useful for codebase exploration. Make doc references conditional.

---

### 8. **llm-documentation** 🔴 Consider Deletion/Merge

**Purpose:** Writing documentation optimized for LLMs
**Lines:** ~94

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good |
| Conciseness | ✅ | Very lean |
| Practical Value | 🟡 | Overlaps with skills-guide |
| Uniqueness | ❌ | Content exists elsewhere |

**Issues:**
- Core principles (assume competence, match specificity) already in skills-guide
- Anti-patterns section is valuable but short
- Not enough unique value to justify standalone skill

**Verdict:** MERGE into skills-guide as "Writing for LLMs" section, then DELETE.

---

### 9. **parallel-execution** 🟢 Good

**Purpose:** Coordinate concurrent agent work
**Lines:** ~123

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Clear triggers |
| Naming | ✅ | "Executing Work in Parallel" - proper gerund |
| Writing Style | ✅ | Imperative throughout |
| Structure | ✅ | Good decision framework |
| Practical Value | ✅ | Unique, valuable guidance |

**Verdict:** KEEP - Essential for agent orchestration patterns.

---

### 10. **planning** 🟢 Good

**Purpose:** Implementation planning before coding
**Lines:** ~300

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good triggers |
| Naming | ✅ | "Planning Implementation" - proper gerund |
| Structure | ✅ | Comprehensive checklist approach |
| Practical Value | 🟡 | References templates that may not exist |

**Issues:**
- References `~/.claude/file-templates/plan.*.template.md` that may not exist
- Heavy project doc assumptions (`docs/product-requirements.md`, etc.)
- At 300 lines, could benefit from trimming

**Verdict:** KEEP with revision - Remove template dependencies or make them optional.

---

### 11. **playwright-testing** ✅ Excellent

**Purpose:** E2E testing with Playwright
**Lines:** ~161

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Excellent - includes specific triggers |
| Naming | ✅ | "Playwright Testing" - clear |
| Examples | ✅ | Great code examples |
| Conciseness | ✅ | Just right |
| Self-Contained | ✅ | No external dependencies |
| Proactive Trigger | ✅ | "Run tests without asking when..." |

**Verdict:** KEEP - Model skill with excellent trigger phrases and practical examples.

---

### 12. **prompting-effectively** 🟢 Good

**Purpose:** Write better prompts for Claude
**Lines:** ~223

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good triggers |
| Naming | ✅ | "Writing Effective Prompts" - proper gerund |
| Examples | ✅ | Excellent before/after examples |
| Structure | ✅ | Clear checklist approach |
| Practical Value | ✅ | Valuable for meta-prompting |

**Verdict:** KEEP - Useful for prompt engineering guidance.

---

### 13. **requirements-gathering** 🟡 Needs Revision

**Purpose:** Clarify requirements before implementation
**Lines:** ~233

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good |
| Naming | ✅ | "Gathering Requirements" - proper gerund |
| Structure | 🟡 | Very heavyweight workflow |
| Practical Value | 🟡 | Assumes heavy documentation infrastructure |

**Issues:**
- References `~/.claude/file-templates/requirements.template.md` that doesn't exist
- Heavy assumption of project docs structure
- 8-step workflow may be overkill for most requests

**Verdict:** KEEP with simplification - Make the workflow lighter and template-independent.

---

### 14. **security-auditing** 🟢 Good

**Purpose:** Security vulnerability analysis
**Lines:** ~297

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Excellent - mentions OWASP, PCI-DSS, GDPR |
| Naming | ✅ | "Auditing Security" - proper gerund |
| Structure | ✅ | Excellent checklist approach |
| Examples | ✅ | Great vulnerability examples with fixes |
| Practical Value | ✅ | Self-contained, actionable |

**Minor Issue:** At 297 lines, could be split with references file for OWASP details.

**Verdict:** KEEP - High-quality, practical security guidance.

---

### 15. **testing-protocol** 🟡 Needs Revision

**Purpose:** Write automated tests
**Lines:** ~306

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good |
| Naming | ✅ | "Testing Code" - proper gerund |
| Examples | ✅ | Good code examples |
| Practical Value | 🟡 | Assumes specific project structure |

**Issues:**
- References `docs/user-stories/US-###-*.md` that won't exist
- References `code-finder` agents that don't exist
- At 306 lines, could use trimming
- Duplicates some content with playwright-testing

**Verdict:** KEEP with revision - Remove project-specific assumptions, trim length.

---

### 16. **typescript-sdk-reference** ✅ Excellent

**Purpose:** TypeScript Agent SDK documentation
**Lines:** ~270 main + supporting files

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Clear |
| Naming | ⚠️ | Noun form, but acceptable for reference doc |
| Structure | ✅ | Excellent progressive disclosure (SKILL.md + 3 reference files) |
| Examples | ✅ | Great code examples |
| Bundled Resources | ✅ | MESSAGE_TYPES.md, TYPES.md, TOOLS.md |
| allowed-tools | ✅ | Properly restricts to Read, Write, Edit, Task |

**Verdict:** KEEP - Model reference skill with perfect progressive disclosure pattern.

---

### 17. **webapp-testing** 🔴 Consider Deletion/Merge

**Purpose:** Local webapp testing with Playwright
**Lines:** ~96 main + scripts + examples

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Good |
| Naming | ⚠️ | Noun form |
| Scripts | ✅ | Has with_server.py helper |
| Overlap | ❌ | Heavy overlap with playwright-testing |

**Issues:**
- 80% overlap with playwright-testing
- Main unique value is `with_server.py` for server lifecycle
- Could be merged into playwright-testing with server section

**Verdict:** MERGE into playwright-testing, then DELETE.

---

### 18. **xlsx** ✅ Excellent

**Purpose:** Spreadsheet creation and analysis
**Lines:** ~289 + recalc.py script

| Criterion | Score | Notes |
|-----------|-------|-------|
| Description Quality | ✅ | Excellent - lists all 5 use cases |
| Naming | ⚠️ | Single word, but acceptable for format name |
| Domain Knowledge | ✅ | Excellent financial modeling standards |
| Scripts | ✅ | recalc.py for formula recalculation |
| Examples | ✅ | Good pandas + openpyxl examples |
| Self-Contained | ✅ | Dependencies clearly stated (LibreOffice) |

**Verdict:** KEEP - Exceptional domain-specific skill with valuable financial conventions.

---

## Consolidation Recommendations

### 1. Merge webapp-testing → playwright-testing
- Add "Server Lifecycle Management" section
- Include `with_server.py` reference
- Delete webapp-testing after merge

### 2. Merge llm-documentation → skills-guide
- Add "Writing Documentation for LLMs" section
- Include anti-patterns checklist
- Delete llm-documentation after merge

### 3. Consider: skill-creator + skills-guide → skills
- Single "skills" directory with:
  - SKILL.md (main guide)
  - CREATING.md (creation workflow)
  - scripts/ (existing scripts)

---

## Issues to Fix Across Multiple Skills

### 1. **Non-existent Project Infrastructure**
These skills reference documentation that doesn't exist:
- `docs/feature-spec/F-##-*.md`
- `docs/user-stories/US-###-*.md`
- `docs/api-contracts.yaml`
- `docs/product-requirements.md`
- `~/.claude/file-templates/*.md`

**Affected:** bug-fixing-protocol, code-reviewing, documenting-code, investigating, planning, requirements-gathering, testing-protocol

**Fix:** Either:
1. Create the referenced infrastructure (init-project template)
2. Make all doc references conditional with "if available" language
3. Remove project-specific assumptions entirely

### 2. **Non-existent Agents/Commands**
- `./agent-responses/await {agent_id}` - referenced but doesn't exist
- `code-finder` agent - referenced but not in agent list
- `/manage-project/*` commands - referenced but don't exist

### 3. **Naming Convention**
Several skills don't follow gerund naming:
- skill-creator → "Creating Skills"
- skills-guide → "Managing Skills"
- git-commit-helper → "Writing Commit Messages"
- typescript-sdk-reference → (acceptable for reference doc)
- xlsx → (acceptable for format name)
- webapp-testing → "Testing Web Applications"

---

## Final Action Items

| Priority | Action | Skills Affected |
|----------|--------|-----------------|
| 🔴 High | Delete documenting-code (no value without infrastructure) | 1 |
| 🔴 High | Merge webapp-testing → playwright-testing | 2 |
| 🟡 Medium | Merge llm-documentation → skills-guide | 2 |
| 🟡 Medium | Remove non-existent doc references OR create init-project template | 7 |
| 🟢 Low | Update skill names to gerund form | 5 |
| 🟢 Low | Consider skills-guide + skill-creator consolidation | 2 |

---

## Post-Consolidation Status

**Consolidations Completed:**
- ✅ webapp-testing → playwright-testing
- ✅ llm-documentation → skills-guide → skills
- ✅ skill-creator + skills-guide → skills

**Final Skills Count:** 7 skills (down from 17)

**Deleted as redundant with agents:**
- ✅ investigating (redundant with `Explore` agent)
- ✅ planning (redundant with `Plan` agent)
- ✅ requirements-gathering (redundant with `product-designer` agent)

**Deleted as redundant with commands:**
- ✅ bug-fixing-protocol (redundant with `/debug` command - merged best parts)

**Deleted (non-existent doc references, limited unique value):**
- ✅ code-reviewing (use `advisor` agent instead)
- ✅ testing-protocol (use `playwright-tester` agent instead)

**Remaining Action Items:**
- ✅ Updated skill names to gerund form (git-commit-helper → "Writing Commit Messages")
