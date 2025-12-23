---
description: Archive completed feature documentation
argument-hint: [feature-folder]
allowed-tools: Read, Glob, Bash(mv:*, mkdir:*, ls:*), AskUserQuestion
---

# Cleanup Documentation

Archive feature documentation from `docs/features/` to `docs/archive/`.

## Instructions

### Phase 1: Discover Feature Folders

List all folders in `docs/features/` directory:
- Check that directory exists
- If no folders found, report and exit
- Display all discovered features to user

### Phase 2: User Selection

Use `AskUserQuestion` with:
- Question: "Which features would you like to archive?"
- Header: "Features"
- Multiple select enabled
- Options: List all discovered features

### Phase 3: Archive Folders

For each selected feature:
1. Move folder:
   - FROM: `docs/features/<folder>/`
   - TO: `docs/archive/<date>/<folder>/`
2. Create archive directory if it doesn't exist

### Phase 4: Report Results

Display summary showing:
- Number of features archived
- List of archived folders
- Any errors encountered

## Error Handling

- **No features found**: "No feature folders found in docs/features/"
- **Directory doesn't exist**: Create `docs/archive/` if needed
- **Folder move error**: Report but don't fail entire command

## Expected Output Format

```
✓ Archived Features (3)
  - auth-flow
  - user-dashboard
  - notifications

Archive complete!
```
