# Skill Audit Criteria

Scoring criteria for `.claude/skills/*/SKILL.md` files based on official skills documentation.

## Structure (5 points)

### Frontmatter Completeness (3 points)
- **3 pts:** Required fields + relevant optional fields present and valid
  - Required: `name` (action-first pattern), `description`
  - Optional: `allowed-tools`
- **2 pts:** Required fields present
- **1 pt:** Required fields with formatting issues
- **0 pts:** Missing required fields or invalid YAML

### Content Organization (1 point)
- **1 pt:** Clear sections (Quick Start, detailed guide, references)
- **0 pts:** Disorganized or unclear structure

### Appropriate Length (1 point)
- **1 pt:** SKILL.md <500 lines, uses progressive disclosure for details
- **0 pts:** SKILL.md >500 lines or doesn't use progressive disclosure

**Common Issues:**
- Name uses domain-first instead of action-first (e.g., `pdf-processor` instead of `processing-pdfs`)
- Description too vague or missing trigger terms
- Missing `allowed-tools` when skill should be read-only
- No progressive disclosure (everything in SKILL.md instead of separate reference files)

## Clarity (4 points)

### Purpose Statement (1 point)
- **1 pt:** Description clearly states what AND when to use
- **0 pts:** Vague description

### Usage Examples (1 point)
- **1 pt:** Concrete examples with input/output
- **0 pts:** No examples or only explanations

### Edge Cases (1 point)
- **1 pt:** Documents limitations, edge cases, or error scenarios
- **0 pts:** No edge case documentation

### Progressive Disclosure (1 point)
- **1 pt:** Links to detailed files (REFERENCE.md, FORMS.md, etc.) for advanced content
- **0 pts:** Everything crammed into SKILL.md

**Good Description Examples:**
- "Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
- "Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format."

**Bad Description Examples:**
- "Helps with documents"
- "Data analysis tool"

## Technical (5 points)

### Naming Convention (2 points)
- **2 pts:** Action-first pattern: `[verb-ing]-[target]` (e.g., `processing-pdfs`, `analyzing-spreadsheets`)
- **1 pt:** Descriptive but doesn't follow pattern
- **0 pts:** Poor naming (abbreviations, vague, domain-first like agents)

### Tool Restrictions (1 point)
- **1 pt:** Uses `allowed-tools` when skill has limited scope (e.g., read-only)
- **0 pts:** Should restrict tools but doesn't

### Reference Depth (1 point)
- **1 pt:** References one level deep from SKILL.md (not deeply nested)
- **0 pts:** References multiple levels deep (hard to follow)

### Trigger Terms (1 point)
- **1 pt:** Description includes specific keywords users would say
- **0 pts:** Generic description without triggers

**Naming Examples:**

**Good:**
- `processing-pdfs` (action: processing, target: pdfs)
- `analyzing-spreadsheets` (action: analyzing, target: spreadsheets)
- `writing-documentation` (action: writing, target: documentation)
- `testing-code` (action: testing, target: code)

**Bad:**
- `pdf-processor` (domain-first, use for agents not skills)
- `docs` (missing action)
- `helper-utils` (vague)
- `spreadsheet-analysis-tool` (verbose, domain-first)

**Progressive Disclosure Pattern:**

```
skill/
├── SKILL.md (<500 lines, links to details)
├── REFERENCE.md (API reference)
├── FORMS.md (specialized topic)
└── scripts/
    └── helper.py
```

SKILL.md should link: "For form filling, see FORMS.md"

## Operational (4 points)

### Script Utilities (2 points)
- **2 pts:** Provides pre-made scripts for error-prone operations
- **1 pt:** Has scripts but they punt errors to Claude
- **0 pts:** No scripts when they would help reliability

### Validation Loops (1 point)
- **1 pt:** Quality-critical tasks include validation steps
- **0 pts:** No validation guidance

### Dependencies (1 point)
- **1 pt:** Required packages/tools listed in description or requirements section
- **0 pts:** Uses dependencies without mentioning them

**Script Best Practices:**

**Good - handles errors:**
```python
try:
    return open(path).read()
except FileNotFoundError:
    print(f"File {path} not found, creating default")
    return ""
```

**Bad - punts to Claude:**
```python
return open(path).read()  # Just fails
```

## Maintainability (2 points)

### No Hardcoded Values (1 point)
- **1 pt:** No magic numbers or unexplained constants; uses clear variable names
- **0 pts:** Has voodoo constants or hardcoded values

### Consistent Terminology (1 point)
- **1 pt:** Uses same terms throughout (e.g., always "API endpoint", not mixing with "URL", "route", "path")
- **0 pts:** Inconsistent terminology

**Naming in Scripts:**

**Good:**
```python
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30 seconds
```

**Bad:**
```python
TIMEOUT = 47  # Why 47?
```

## Red Flags (Automatic Deductions)

- **-2 pts:** Uses domain-first naming (agent pattern) instead of action-first
- **-2 pts:** SKILL.md >500 lines without clear need
- **-1 pt:** Description missing trigger terms
- **-1 pt:** No examples, only explanations
- **-1 pt:** Contains XML tags in description or name
- **-1 pt:** Reserved words in name ("anthropic", "claude")
- **-1 pt:** Deeply nested references (>1 level)

## Excellent Skill Checklist

An 18-20 point skill has:

- ✅ Action-first naming: `[verb-ing]-[target]`
- ✅ Complete frontmatter (name, description)
- ✅ Description includes what + when + trigger terms
- ✅ `allowed-tools` if skill has limited scope
- ✅ SKILL.md < 500 lines
- ✅ Progressive disclosure (links to REFERENCE.md, etc.)
- ✅ Quick Start section with immediate usage
- ✅ Concrete examples with input/output
- ✅ Utility scripts for error-prone operations
- ✅ Validation loops for quality-critical tasks
- ✅ Dependencies documented
- ✅ No hardcoded values or magic numbers
- ✅ Consistent terminology throughout
- ✅ References one level deep (not nested)
- ✅ Concise (avoids explaining what Claude knows)

## Common Improvement Suggestions

| Issue | Fix |
|-------|-----|
| Domain-first name | Rename to `[verb-ing]-[target]` (e.g., `pdf-processor` → `processing-pdfs`) |
| SKILL.md too long | Move details to REFERENCE.md, FORMS.md, etc. |
| No trigger terms | Add keywords users would say ("use when working with PDF files") |
| Missing allowed-tools | Add `allowed-tools: Read, Grep, Glob` for read-only |
| No examples | Add Quick Start with concrete input/output |
| No scripts | Create utility scripts for complex operations |
| Scripts punt errors | Add try/except with fallback behavior |
| Magic numbers | Add explanatory comments for constants |
| Inconsistent terms | Pick one term and use throughout ("API endpoint" not mixed with "URL") |
| Nested references | Flatten to one level (SKILL.md → detailed files, not deeper) |
| Too verbose | Remove explanations of basics Claude knows |
| No validation | Add validation steps for quality-critical operations |

## Supporting File Structure

```
skill-name/
├── SKILL.md                # Main entry point (<500 lines)
├── REFERENCE.md            # Detailed API reference
├── ADVANCED.md             # Advanced usage patterns
├── scripts/
│   ├── validate.py         # Validation utility
│   └── process.sh          # Processing script
└── templates/
    └── template.txt        # Template file
```

**Reference from SKILL.md:**
```markdown
## Quick Start
[Basic usage here]

## Advanced
For detailed API reference, see REFERENCE.md
For advanced patterns, see ADVANCED.md
```
