# Creating Skills

Detailed workflow for creating effective skills that extend Claude's capabilities.

## Contents

- [About Skills](#about-skills)
- [Skill Creation Process](#skill-creation-process)
- [Evaluation-Driven Development](#evaluation-driven-development)
- [Iterative Development with Claude](#iterative-development-with-claude)
- [Validation](#validation)
- [Quality Checklist](#quality-checklist)

## About Skills

Skills are modular, self-contained packages that provide specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains—they transform Claude from a general-purpose agent into a specialized expert.

### What Skills Provide

1. **Specialized workflows** — Multi-step procedures for specific domains
2. **Tool integrations** — Instructions for working with specific file formats or APIs
3. **Domain expertise** — Company-specific knowledge, schemas, business logic
4. **Bundled resources** — Scripts, references, and assets for complex tasks

### Anatomy of a Skill

```text
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: lowercase-with-hyphens
│   │   └── description: what + when to use
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation
    └── assets/           - Templates, images
```

### Bundled Resources

#### Scripts (`scripts/`)

Executable code for tasks requiring deterministic reliability.

- **When to include**: Same code rewritten repeatedly OR deterministic reliability needed
- **Benefits**: Token efficient, deterministic, executed without loading into context
- **Example**: `scripts/rotate_pdf.py` for PDF rotation

#### References (`references/`)

Documentation loaded into context as needed.

- **When to include**: Information Claude should reference while working
- **Examples**: Database schemas, API docs, company policies
- **Best practice**: If >10k words, include grep patterns in SKILL.md

#### Assets (`assets/`)

Files used in output, not loaded into context.

- **When to include**: Files for final output
- **Examples**: Templates, images, boilerplate code, fonts

### Progressive Disclosure

Skills use three-level loading:

| Level | When Loaded | Token Cost |
|-------|-------------|------------|
| Metadata (name + description) | Always | ~100 tokens |
| SKILL.md body | When triggered | <5k tokens |
| Bundled resources | As needed | Unlimited |

## Skill Creation Process

### Step 1: Understand with Concrete Examples

Skip only when usage patterns are already clear.

Ask questions to understand the skill:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

**Conclude when**: Clear sense of functionality the skill should support.

### Step 2: Plan Reusable Contents

Analyze each example by:
1. Considering how to execute from scratch
2. Identifying what scripts, references, and assets would help

**Examples:**

| Skill | Example Query | Analysis | Resource |
|-------|--------------|----------|----------|
| `pdf-editor` | "Rotate this PDF" | Same code rewritten each time | `scripts/rotate_pdf.py` |
| `webapp-builder` | "Build me a todo app" | Same boilerplate each time | `assets/hello-world/` |
| `big-query` | "How many users logged in?" | Re-discovering schemas each time | `references/schema.md` |

### Step 3: Initialize the Skill

Skip if iterating on existing skill.

**Always run the init script:**

```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:
- Creates skill directory at specified path
- Generates SKILL.md template with proper frontmatter
- Creates example `scripts/`, `references/`, `assets/` directories
- Adds example files to customize or delete

### Step 4: Edit the Skill

Remember: the skill is for another Claude instance to use. Focus on non-obvious procedural knowledge.

#### Start with Reusable Contents

Implement `scripts/`, `references/`, `assets/` identified in Step 2.

**Note**: May require user input (e.g., brand assets, documentation).

Delete example files/directories not needed.

#### Update SKILL.md

**Writing Style**: Use **imperative/infinitive form** (verb-first instructions), not second person.
- **Good:** "To accomplish X, do Y"
- **Bad:** "You should do X"

Answer these questions:
1. What is the purpose of the skill?
2. When should the skill be used?
3. How should Claude use the skill? (Reference all bundled contents)

### Step 5: Package the Skill

Package into distributable zip:

```bash
python scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory:
```bash
python scripts/package_skill.py <path/to/skill-folder> ./dist
```

The script:
1. **Validates** automatically:
   - YAML frontmatter format and required fields
   - Naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Packages** if validation passes:
   - Creates zip file named after skill
   - Maintains proper directory structure

Fix validation errors and re-run if needed.

### Step 6: Iterate

After testing, users may request improvements.

**Iteration workflow:**
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify SKILL.md or resource updates needed
4. Implement changes and test again

## Evaluation-Driven Development

**Create evaluations BEFORE writing extensive documentation.** This ensures your skill solves real problems rather than documenting imagined ones.

### The Process

1. **Identify gaps**: Run Claude on representative tasks without a skill. Document specific failures or missing context.

2. **Create evaluations**: Build at least three scenarios that test these gaps.

3. **Establish baseline**: Measure Claude's performance without the skill.

4. **Write minimal instructions**: Create just enough content to address the gaps and pass evaluations.

5. **Iterate**: Execute evaluations, compare against baseline, and refine.

### Evaluation Structure

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using appropriate library",
    "Extracts text content from all pages without missing any",
    "Saves extracted text to output.txt in readable format"
  ]
}
```

### Why This Works

- Solves actual problems, not anticipated ones
- Prevents over-documentation
- Provides objective success criteria
- Enables measurable improvement

## Iterative Development with Claude

The most effective skill development involves Claude itself. Work with one instance ("Claude A") to create a skill used by other instances ("Claude B").

### Creating a New Skill

1. **Complete a task without a skill**: Work through a problem with Claude A using normal prompting. Notice what information you repeatedly provide.

2. **Identify the reusable pattern**: After completing the task, identify what context you provided that would be useful for similar future tasks.

   *Example*: If you worked through BigQuery analysis, you might have provided table names, field definitions, filtering rules, and common query patterns.

3. **Ask Claude A to create a skill**: "Create a skill that captures this pattern we just used. Include the schemas, naming conventions, and the rule about filtering test accounts."

4. **Review for conciseness**: Check that Claude A hasn't added unnecessary explanations. Ask: "Remove the explanation about what win rate means—Claude already knows that."

5. **Improve information architecture**: Ask Claude A to organize content effectively. "Organize this so the table schema is in a separate reference file."

6. **Test on similar tasks**: Use the skill with Claude B (fresh instance with skill loaded) on related use cases. Observe whether Claude B finds the right information and applies rules correctly.

7. **Iterate based on observation**: If Claude B struggles, return to Claude A with specifics: "When Claude used this skill, it forgot to filter by date for Q4. Should we add a section about date filtering patterns?"

### Iterating on Existing Skills

1. **Use the skill in real workflows**: Give Claude B actual tasks, not test scenarios.

2. **Observe behavior**: Note where it struggles, succeeds, or makes unexpected choices.

   *Example*: "When I asked Claude B for a regional sales report, it wrote the query but forgot to filter out test accounts."

3. **Return to Claude A for improvements**: Share the current SKILL.md and describe what you observed. "The skill mentions filtering, but maybe it's not prominent enough?"

4. **Review suggestions**: Claude A might suggest reorganizing to make rules more prominent, using stronger language ("MUST filter" instead of "always filter"), or restructuring workflows.

5. **Apply and test**: Update the skill with refinements, test again with Claude B on similar requests.

6. **Repeat**: Continue the observe-refine-test cycle as you encounter new scenarios.

### Why This Works

- Claude A understands agent needs
- You provide domain expertise
- Claude B reveals gaps through real usage
- Iterative refinement improves skills based on observed behavior, not assumptions

## Validation

Quick validation without packaging:

```bash
python scripts/quick_validate.py <path/to/skill-folder>
```

Checks:
- YAML frontmatter syntax
- Required fields present
- Description quality
- File structure

## Quality Checklist

### Metadata

- [ ] `name` uses lowercase letters, numbers, and hyphens only
- [ ] `name` follows gerund naming (e.g., `processing-pdfs`)
- [ ] `name` does not contain reserved words ("anthropic", "claude")
- [ ] `name` is 64 characters or less
- [ ] `description` is written in third person
- [ ] `description` includes WHAT it does
- [ ] `description` includes WHEN to use it
- [ ] `description` is 1024 characters or less
- [ ] Trigger terms are specific, not vague

### Content

- [ ] Uses imperative/infinitive form ("To accomplish X, do Y")
- [ ] Assumes Claude's intelligence (no explaining basics)
- [ ] Examples provided where helpful
- [ ] SKILL.md under 500 lines
- [ ] Table of contents if over 100 lines
- [ ] Consistent terminology throughout

### Resources

- [ ] Scripts are tested and deterministic
- [ ] Scripts handle errors (don't punt to Claude)
- [ ] No voodoo constants (all magic numbers justified)
- [ ] References are appropriately sized
- [ ] Assets are properly organized
- [ ] No duplicated information between files
- [ ] Required packages listed in SKILL.md

### Structure

- [ ] Progressive disclosure pattern used
- [ ] Reference depth is one level max (SKILL.md → file.md)
- [ ] Forward slashes in all paths
- [ ] Multi-domain skills organized by domain
- [ ] Long reference files have table of contents

### Testing

- [ ] At least three evaluations created
- [ ] Tested with Haiku model
- [ ] Tested with Sonnet model
- [ ] Tested with Opus model
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)

### Distribution

- [ ] Validation passes (`quick_validate.py`)
- [ ] Packaging succeeds (`package_skill.py`)
- [ ] Skill activates when expected triggers are used
- [ ] No conflicts with other skills
