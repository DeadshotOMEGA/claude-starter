---
name: writing-setup-guides
description: Write development setup guides for projects. Use when creating setup.md or getting-started documentation.
---

# Setup Guide Writing

Create setup documentation that gets developers running quickly.

## Purpose

Setup guides help developers:
- Install prerequisites
- Configure their environment
- Run the project locally
- Troubleshoot common issues

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Prerequisites** — Required tools and versions
2. **Quick Start** — Minimal steps to run
3. **Environment Configuration** — Required and optional variables
4. **Database Setup** — Local and cloud options
5. **Running the Application** — Dev, build, test commands
6. **Common Commands** — Lint, format, typecheck
7. **Project Structure** — Directory overview
8. **Troubleshooting** — Common issues and solutions

## Environment Variables Format

```markdown
### Required Variables
```env
DATABASE_URL=[connection-string]
AUTH_SECRET=[secret-key]
```

### Optional Variables
```env
DEBUG=[true/false]
ENABLE_FEATURE=[true/false]
```
```

## Troubleshooting Format

```markdown
#### Issue: [Database connection fails]
**Solution**: [How to fix]

#### Issue: [Build errors]
**Solution**: [How to fix]
```

## Best Practices

- Test the setup steps on a fresh machine
- Include exact version numbers
- Provide both local and cloud database options
- List all required environment variables
- Include copy-paste ready commands
