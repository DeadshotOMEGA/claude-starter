# Git Conventions (Git Flow)

## Branch Naming
- `feature/*` — New features (branches from develop)
- `release/*` — Release preparation (branches from develop)
- `hotfix/*` — Emergency production fixes (branches from main)

## Protected Branches
- `main` — Production
- `develop` — Integration

## Commits
- Format: conventional commits (feat:, fix:, chore:, docs:, refactor:, test:)
- Always pull before push
- Rebase preferred over merge

## Push Authentication
- Use `GIT_ASKPASS=/snap/bin/gh git push` for authenticated pushes
- Direct `git push` is permission-denied in this environment

## Tooling
- Use `git-flow-manager` agent for branch operations
