---
name: writing-skills
description: Write and manage Claude Code Skill definitions. Use when creating, editing, or understanding .claude/skills/*/SKILL.md files.
---

# Skill Writing

Package reusable expertise into discoverable capabilities that Claude activates automatically.

## Contents

- [Quick Start](#quick-start)
- [What Are Skills](#what-are-skills)
- [Skill Locations](#skill-locations)
- [SKILL.md Requirements](#skillmd-requirements)
- [Supporting Files](#supporting-files)
- [Testing & Debugging](#testing--debugging)
- [Sharing Skills](#sharing-skills)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Quick Start

### Personal Skill (available everywhere)

```bash
mkdir -p ~/.claude/skills/my-skill-name
```

### Project Skill (shared with team)

```bash
mkdir -p .claude/skills/my-skill-name
```

### Create SKILL.md

```yaml
---
name: processing-pdfs
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# Processing PDFs

## Quick Start
[Immediate usage instructions]

## Detailed Guide
[Step-by-step procedures]
```

## What Are Skills

Skills are modular capabilities that extend Claude's functionality:

- **SKILL.md** — Instructions Claude reads when the skill triggers
- **Supporting files** — Optional scripts, templates, reference docs
- **Model-invoked** — Claude autonomously decides when to use based on description
- **Progressive loading** — Only loads content when relevant

### Benefits

- Solve recurring problems once, reuse everywhere
- Share expertise across teams via git
- Compose multiple skills for complex tasks
- Reduce token overhead from repetitive prompting

## Skill Locations

### Personal Skills: `~/.claude/skills/`

Available across all projects. Use for:
- Individual workflows and preferences
- Experimental skills in development
- Personal productivity tools

### Project Skills: `.claude/skills/`

Shared with team via git. Use for:
- Team workflows and conventions
- Project-specific capabilities
- Shared utilities

Team members automatically get project skills when they pull.

### Plugin Skills

Bundled with Claude Code plugins. Automatically available when plugin installed. Recommended for distributing skills to teams.

## SKILL.md Requirements

Every skill requires a `SKILL.md` file with YAML frontmatter.

### Required Fields

| Field | Limit | Rules |
|-------|-------|-------|
| `name` | 64 chars | Lowercase letters, numbers, hyphens only. No XML tags. No reserved words ("anthropic", "claude"). |
| `description` | 1024 chars | Non-empty. No XML tags. Must include what it does AND when to use it. |

### Optional Fields

| Field | Purpose |
|-------|---------|
| `allowed-tools` | Restrict which tools Claude can use (Claude Code only) |

### Name Field

Use **action-first naming** with gerund form (verb-ing + noun):

**Pattern:** `[action]-[target]`

| Good | Why |
|------|-----|
| `processing-pdfs` | Action (processing) + target (pdfs) |
| `analyzing-spreadsheets` | Action (analyzing) + target (spreadsheets) |
| `writing-documentation` | Action (writing) + target (documentation) |
| `testing-code` | Action (testing) + target (code) |

Skills describe *what you do*, so action comes first.

> **Note:** This differs from agents, which use domain-first naming (`code-reviewer`, `database-admin`) because agents are *roles* (things), not actions.

**Avoid:**
- Reversed order: `pdf-processor`, `code-tester` (use for agents, not skills)
- Vague: `helper`, `utils`, `tools`
- Generic: `documents`, `data`, `files`
- Reserved: `anthropic-helper`, `claude-tools`

### Description Field

The description enables skill discovery. Claude uses it to decide whether to activate.

**Write in third person.** The description is injected into the system prompt.

- **Good:** "Processes Excel files and generates reports"
- **Avoid:** "I can help you process Excel files"
- **Avoid:** "You can use this to process Excel files"

**Include both what AND when:**

```yaml
# Good - specific triggers
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Bad - too vague
description: Helps with documents
```

### Allowed-Tools Field

Restrict which tools Claude can use when the skill is active:

```yaml
---
name: safe-file-reader
description: Reads files without making changes. Use when read-only file access is needed.
allowed-tools: Read, Grep, Glob
---
```

Use for:
- Read-only skills that shouldn't modify files
- Security-sensitive workflows
- Skills with limited scope

## Supporting Files

Skills can include additional files that load on-demand.

### Simple Skill (single file)

```text
commit-helper/
└── SKILL.md
```

### Multi-File Skill

```text
pdf-processing/
├── SKILL.md              # Main instructions (<500 lines)
├── FORMS.md              # Form-filling guide
├── REFERENCE.md          # API reference
└── scripts/
    ├── analyze_form.py   # Utility script
    └── validate.py       # Validation script
```

### Progressive Disclosure Pattern

Keep SKILL.md under 500 lines. Link to detailed content:

Example SKILL.md content:

    ## Quick Start

    Extract text with pdfplumber:
    ```python
    import pdfplumber
    with pdfplumber.open("file.pdf") as pdf:
        text = pdf.pages[0].extract_text()
    ```

    ## Advanced Features

    **Form filling**: See FORMS.md
    **API reference**: See REFERENCE.md

Claude loads additional files only when needed.

### Reference Depth

Keep references one level deep from SKILL.md:

- **Good:** SKILL.md → FORMS.md
- **Bad:** SKILL.md → advanced.md → details.md

Deeply nested references may be partially read.

### Multi-Domain Organization

For skills covering multiple domains:

```text
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md
```

SKILL.md acts as router linking to domain-specific docs.

## Testing & Debugging

### Test With Multiple Models

Skills behave differently across models:

- **Haiku**: May need more explicit guidance
- **Sonnet**: Balanced—clear and efficient instructions work best
- **Opus**: Avoid over-explaining; can handle more ambiguity

Test with all models you plan to use.

### Test Activation

Ask questions matching your description:

```text
Can you help me extract text from this PDF?
```

Claude should automatically activate the skill.

### Debug Activation Issues

**Skill won't activate?**

1. **Check description specificity:**
   - Too vague: `Helps with documents`
   - Specific: `Extracts text and tables from PDFs. Use when working with PDF files.`

2. **Include trigger terms** users would actually say

3. **Verify file location:**
   ```bash
   # Personal
   ls ~/.claude/skills/my-skill/SKILL.md

   # Project
   ls .claude/skills/my-skill/SKILL.md
   ```

**Multiple skills conflict?**

Use distinct trigger terms:

```yaml
# Instead of both being "data analysis"

# Skill 1
description: Analyzes sales data in Excel and CRM exports. Use for sales reports and pipeline analysis.

# Skill 2
description: Analyzes log files and system metrics. Use for performance monitoring and debugging.
```

**YAML syntax errors?**

```bash
cat SKILL.md | head -n 10
```

Verify:
- Opening `---` on line 1
- Closing `---` before content
- No tabs (use spaces)
- Correct indentation

### Run Debug Mode

```bash
claude --debug
```

Shows skill loading errors.

## Sharing Skills

### Via Git (Project Skills)

```bash
# Add to project
mkdir -p .claude/skills/team-skill
# Create SKILL.md...

# Commit
git add .claude/skills/
git commit -m "Add team skill for PDF processing"
git push
```

Team members get skills automatically on pull.

### Via Plugins (Recommended)

For broader distribution, package skills in Claude Code plugins:

1. Create plugin with skills in `skills/` directory
2. Add to marketplace
3. Team members install plugin

See Claude Code plugin documentation.

## Best Practices

### Be Concise

Claude is smart. Don't explain basics.

**Verbose** (~150 tokens):
```text
PDF files are a common format containing text and images.
To extract text, you need a library. Many libraries exist...
```

**Concise** (~50 tokens):

    Use pdfplumber for text extraction:
    ```python
    import pdfplumber
    with pdfplumber.open("file.pdf") as pdf:
        text = pdf.pages[0].extract_text()
    ```

### Use Examples Over Explanations

Provide input/output pairs:

    **Example 1:**
    Input: Added user authentication with JWT tokens
    Output:
    ```text
    feat(auth): implement JWT-based authentication

    Add login endpoint and token validation middleware
    ```

### Match Specificity to Task Fragility

**High freedom** (multiple valid approaches):

    ## Code Review Process

    1. Analyze code structure
    2. Check for potential bugs
    3. Suggest improvements

**Low freedom** (exact sequence required):

    ## Database Migration

    Run exactly this command:
    ```bash
    python scripts/migrate.py --verify --backup
    ```
    Do not modify the command.

### Provide Utility Scripts

Pre-made scripts are more reliable than generated code:

    **analyze_form.py**: Extract form fields
    ```bash
    python scripts/analyze_form.py input.pdf > fields.json
    ```

Scripts execute without loading into context—token efficient.

### Script Best Practices

**Solve, don't punt.** Handle errors in scripts rather than failing to Claude:

```python
# Good - handles error
except FileNotFoundError:
    print(f"File {path} not found, creating default")
    return ''

# Bad - punts to Claude
return open(path).read()  # Just fails
```

**No voodoo constants.** Justify magic numbers:

```python
# Good - self-documenting
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30 seconds

# Bad - unexplained
TIMEOUT = 47  # Why 47?
```

### Use Validation Loops

For quality-critical tasks:

    1. Make edits
    2. **Validate**: `python scripts/validate.py`
    3. If fails:
       - Review error
       - Fix issues
       - Validate again
    4. **Only proceed when validation passes**

### Use Consistent Terminology

Choose one term throughout:
- Always "API endpoint" (not "URL", "route", "path")
- Always "field" (not "box", "element")
- Always "extract" (not "pull", "get")

### Avoid Time-Sensitive Info

Don't include dates that will become outdated:

    # Bad
    If before August 2025, use old API...

    # Good - use "old patterns" section
    ## Current Method
    Use v2 API...

    <details>
    <summary>Legacy v1 API (deprecated)</summary>
    ...
    </details>

### Use Forward Slashes

- **Good:** `scripts/helper.py`
- **Bad:** `scripts\helper.py`

Unix paths work cross-platform.

## Examples

### Simple Skill

```yaml
---
name: generating-commit-messages
description: Generates clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.
---

# Generating Commit Messages

## Instructions

1. Run `git diff --staged` to see changes
2. Suggest commit message with:
   - Summary under 50 characters
   - Detailed description
   - Affected components

## Best Practices

- Use present tense
- Explain what and why, not how
```

### Skill with Tool Restrictions

```yaml
---
name: code-reviewer
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
allowed-tools: Read, Grep, Glob
---

# Code Reviewer

## Checklist

1. Code organization and structure
2. Error handling
3. Performance considerations
4. Security concerns
5. Test coverage
```

### Multi-File Skill

**SKILL.md:**

    ---
    name: processing-pdfs
    description: Extracts text, fills forms, merges PDFs. Use when working with PDF files, forms, or document extraction.
    ---

    # Processing PDFs

    ## Quick Start

    ```python
    import pdfplumber
    with pdfplumber.open("doc.pdf") as pdf:
        text = pdf.pages[0].extract_text()
    ```

    ## Requirements

    ```bash
    pip install pypdf pdfplumber
    ```

    ## Advanced

    - **Form filling**: See FORMS.md
    - **API reference**: See REFERENCE.md

## Creating Skills (Detailed)

For comprehensive skill creation workflow including evaluation-driven development, see CREATING.md.

**Quick creation scripts:**

```bash
# Initialize new skill
python scripts/init_skill.py my-skill-name --path .claude/skills/

# Validate skill
python scripts/quick_validate.py .claude/skills/my-skill-name

# Package for distribution
python scripts/package_skill.py .claude/skills/my-skill-name
```
