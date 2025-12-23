---
name: writing-technical-docs
description: Write technical documentation including user guides, tutorials, and how-to guides. Use when creating documentation for end users or developers.
---

# Writing Technical Documentation

Create user guides, tutorials, and how-to documentation.

## Purpose

Technical docs help users:
- Understand concepts
- Complete specific tasks
- Troubleshoot issues
- Learn the system

## Documentation Types (Diátaxis Framework)

| Type | Purpose | Structure |
|------|---------|-----------|
| **Tutorial** | Learning-oriented | Step-by-step lessons |
| **How-To** | Task-oriented | Steps to achieve goal |
| **Reference** | Information-oriented | Accurate, complete details |
| **Explanation** | Understanding-oriented | Background and context |

## Tutorial Structure

```markdown
# Tutorial: [What You'll Build]

## Overview
What you'll learn and build.

## Prerequisites
- Required knowledge
- Required tools

## Step 1: [First Step]
Explanation and code.

## Step 2: [Second Step]
Explanation and code.

## What's Next
Links to advanced topics.
```

## How-To Guide Structure

```markdown
# How to [Accomplish Task]

## Prerequisites
What you need before starting.

## Steps

1. **[First action]**
   ```bash
   command
   ```

2. **[Second action]**
   Explanation if needed.

## Verification
How to confirm success.

## Troubleshooting
Common issues and solutions.
```

## Best Practices

### Write for Your Audience
- Know their skill level
- Define jargon on first use
- Don't assume context

### Show, Don't Tell
Include working examples:
```javascript
// This works - copy and paste
const result = doThing();
```

### Use Progressive Disclosure
Start simple, add complexity:
1. Basic usage
2. Common options
3. Advanced configuration

### Test Your Docs
Follow your own instructions on a fresh setup.

### Keep Updated
Docs rot fast. Review regularly.

## Formatting Guidelines

- Use headings for scanability
- Keep paragraphs short (3-4 sentences)
- Use bullet points for lists
- Include code blocks with syntax highlighting
- Add screenshots for UI documentation
