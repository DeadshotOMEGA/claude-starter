#!/bin/bash
# Forced Skill Evaluation Hook
# Forces Claude to evaluate available skills before implementation

REGISTRY_PATH=".claude/registries/skills-registry.json"

# Check if registry exists
if [ ! -f "$REGISTRY_PATH" ]; then
    cat << 'EOF'
<user-prompt-submit-hook>
## SKILL EVALUATION UNAVAILABLE

Skills registry not found. Run `/sync-registry` to generate it.
</user-prompt-submit-hook>
EOF
    exit 0
fi

# Parse skills registry and format for Claude
SKILLS=$(python3 -c "
import json
import sys

with open('$REGISTRY_PATH', 'r') as f:
    registry = json.load(f)

skills = registry.get('skills', {})

# Sort by priority (lower = higher priority)
sorted_skills = sorted(skills.items(), key=lambda x: x[1].get('priority', 999))

print('Available Skills (sorted by priority):')
print()

for name, skill in sorted_skills:
    domain = skill.get('domain', 'reference')
    when = skill.get('when', '')
    why = skill.get('why', '')
    priority = skill.get('priority', 2)

    print(f'**{name}** (domain: {domain}, priority: {priority})')
    print(f'  WHEN: {when}')
    print(f'  WHY NOT: {why}')
    print()
" 2>/dev/null)

# Output the hook message
cat << EOF
<user-prompt-submit-hook>
## MANDATORY SKILL EVALUATION PROTOCOL

Before responding to this prompt, you MUST complete all three steps:

### Step 1 - EVALUATE

$SKILLS

For EACH skill above, explicitly state:
- Skill name: YES or NO
- Brief reason (one sentence)

### Step 2 - ACTIVATE
For every skill marked YES:
- Use the Skill() tool NOW before any other action
- Do NOT proceed until all relevant skills are activated

### Step 3 - IMPLEMENT
Only AFTER skill activation may you proceed with implementation.

CRITICAL: Skipping steps is NOT permitted. This evaluation ensures optimal tool usage.
</user-prompt-submit-hook>
EOF
