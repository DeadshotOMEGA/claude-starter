---
name: writing-readmes
description: Write README.md files for projects and packages. Use when creating or improving README documentation.
---

# README Writing

Create README files that help users understand and use projects.

## Purpose

READMEs are the front door to a project. They should:
- Explain what the project does
- Show how to get started quickly
- Provide essential reference information
- Link to detailed documentation

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Title & Description** — Project name and 1-2 sentence summary
2. **Quick Start** — Fastest path to running the project
3. **Installation** — Prerequisites and setup steps
4. **Usage** — Basic usage examples
5. **Documentation** — Links to detailed docs
6. **Contributing** — How to contribute (or link to CONTRIBUTING.md)
7. **License** — License type

## Optional Sections

- **Features** — Key capabilities
- **Screenshots/Demo** — Visual examples
- **API Reference** — If applicable
- **FAQ** — Common questions
- **Roadmap** — Future plans
- **Acknowledgments** — Credits

## Best Practices

### Lead with Value
First paragraph should answer: "What does this do and why should I care?"

### Show, Don't Tell
Include code examples that work:
```bash
npm install my-package
```
```javascript
import { thing } from 'my-package';
thing.doSomething();
```

### Keep Quick Start Quick
3-5 commands maximum to get running.

### Use Badges Sparingly
Only include badges that provide useful information:
- Build status
- Version
- License

### Progressive Disclosure
Start simple, link to details:
- Quick start in README
- Full docs in `/docs` or external site
