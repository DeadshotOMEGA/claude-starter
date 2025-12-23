---
name: writing-changelogs
description: Write changelogs and release notes following Keep a Changelog format. Use when creating CHANGELOG.md, release notes, or version documentation.
---

# Writing Changelogs

Create changelogs that clearly communicate changes to users.

## Purpose

Changelogs provide:
- Clear record of changes per version
- Migration guidance for breaking changes
- User-facing impact summaries
- Release documentation

## Format: Keep a Changelog

Follow [keepachangelog.com](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Deprecated
- Feature being phased out

### Removed
- Deleted feature

### Fixed
- Bug fix description

### Security
- Security fix description

## [1.0.0] - 2024-01-15

### Added
- Initial release features
```

## Change Categories

| Category | Use For |
|----------|---------|
| Added | New features |
| Changed | Changes in existing functionality |
| Deprecated | Soon-to-be removed features |
| Removed | Removed features |
| Fixed | Bug fixes |
| Security | Vulnerability fixes |

## Best Practices

### Lead with Breaking Changes
Put breaking changes first with migration instructions:
```markdown
### Changed
- **BREAKING**: `oldMethod()` renamed to `newMethod()`
  - Migration: Replace all calls to `oldMethod` with `newMethod`
```

### Be User-Focused
Write for users, not developers:
- **Bad**: "Refactored UserService class"
- **Good**: "Improved login speed by 50%"

### Link to Issues/PRs
```markdown
- Fixed login timeout issue ([#123](link))
```

### Include Dates
Use ISO format: `## [1.2.0] - 2024-01-15`

### Keep Unreleased Section
Always maintain an `[Unreleased]` section for ongoing changes.

## Generating from Git

Use conventional commits to automate:
```bash
git log --oneline v1.0.0..HEAD
```

Commit prefixes:
- `feat:` → Added
- `fix:` → Fixed
- `docs:` → (usually skip)
- `refactor:` → Changed
- `BREAKING CHANGE:` → Changed (breaking)
