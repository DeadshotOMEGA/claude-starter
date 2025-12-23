---
name: applying-git-flow
description: Git Flow workflow patterns, validation rules, and automation scripts for branch management. Use when executing Git Flow operations like feature, release, or hotfix workflows.
---

# Applying Git Flow

Git Flow workflow patterns and validation rules for branch management.

## Workflow Commands

### Feature Workflow
```bash
# Start feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# Finish feature
git checkout develop
git pull origin develop
git merge --no-ff feature/new-feature
git push origin develop
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### Release Workflow
```bash
# Start release
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
# Update version in package.json
git commit -am "chore(release): bump version to 1.2.0"
git push -u origin release/v1.2.0

# Finish release
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### Hotfix Workflow
```bash
# Start hotfix
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix
git push -u origin hotfix/critical-fix

# Finish hotfix
git checkout main
git merge --no-ff hotfix/critical-fix
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin main --tags
git checkout develop
git merge --no-ff hotfix/critical-fix
git push origin develop
git branch -d hotfix/critical-fix
git push origin --delete hotfix/critical-fix
```

## Validation Rules

### Branch Name Validation
- ✅ `feature/user-authentication`
- ✅ `release/v1.2.0`
- ✅ `hotfix/security-patch`
- ❌ `my-new-feature`
- ❌ `fix-bug`
- ❌ `random-branch`

### Merge Validation
Before merging, verify:
- [ ] No uncommitted changes
- [ ] Tests passing (run `npm test` or equivalent)
- [ ] No merge conflicts
- [ ] Remote is up to date
- [ ] Correct target branch

### Release Version Validation
- Must follow semantic versioning: `vMAJOR.MINOR.PATCH`
- Examples: `v1.0.0`, `v2.1.3`, `v0.5.0-beta.1`

## Conflict Resolution

When merge conflicts occur:
1. **Identify conflicting files**: `git status`
2. **Show conflict markers**: Display files with `<<<<<<<`, `=======`, `>>>>>>>`
3. **Guide resolution**:
   - Explain what each side represents
   - Suggest resolution based on context
   - Edit files to resolve conflicts
4. **Verify resolution**: `git diff --check`
5. **Complete merge**: `git add` resolved files, then `git commit`

## Status Reporting

Provide clear status updates:
```
🌿 Git Flow Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Branch: feature/user-profile
Branch Type: Feature
Base Branch: develop
Remote Tracking: origin/feature/user-profile

Changes:
  ● 3 modified
  ✚ 5 added
  ✖ 1 deleted

Sync Status:
  ↑ 2 commits ahead
  ↓ 1 commit behind

Ready to merge: ⚠️  Pull from origin first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Error Handling

Handle common errors gracefully:

### Direct push to protected branches
```
❌ Cannot push directly to main/develop
💡 Create a feature branch instead:
   git checkout -b feature/your-feature-name
```

### Merge conflicts
```
⚠️  Merge conflicts detected in:
   - src/components/User.js
   - src/utils/auth.js

🔧 Resolve conflicts and run:
   git add <resolved-files>
   git commit
```

### Invalid branch name
```
❌ Invalid branch name: "my-feature"
✅ Use Git Flow naming:
   - feature/my-feature
   - release/v1.2.0
   - hotfix/bug-fix
```

## Advanced Features

### Changelog Generation
When creating releases, generate CHANGELOG.md from commits:
1. Group commits by type (feat, fix, etc.)
2. Format with links to commits
3. Include breaking changes section
4. Add release date and version

### Semantic Versioning
Automatically suggest version bumps:
- **MAJOR**: Breaking changes (`BREAKING CHANGE:` in commit)
- **MINOR**: New features (`feat:` commits)
- **PATCH**: Bug fixes (`fix:` commits)

### Branch Cleanup
Periodically suggest cleanup:
```
🧹 Branch Cleanup Suggestions:
Merged branches that can be deleted:
  - feature/old-feature (merged 30 days ago)
  - feature/completed-task (merged 15 days ago)

Run: git branch -d feature/old-feature
```

## Integration with CI/CD

When finishing branches, remind about:
- **Automated tests** will run on PR
- **Deployment pipelines** will trigger on merge to main
- **Staging environment** updates on develop merge
