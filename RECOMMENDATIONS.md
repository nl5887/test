# Tool Recommendations and Best Practices

## Quick Reference: Which Tool to Use?

### For Resetting Changes
```
GOAL: Undo uncommitted changes

❌ DON'T USE: git_reset(hard=true)
   └─ Will crash with AttributeError

✅ DO USE: git_checkout(target='<current-branch>')
   └─ Resets virtual files to current branch state
   └─ Works reliably
   └─ Same effect as git_reset --hard

Example:
  1. Make modifications
  2. git_checkout(target='feature/add-app-module')
  3. Files reset to branch state ✅
```

### For Comparing Commits
```
GOAL: See what changed between commits

❌ DON'T USE: git_diff(source='main', target='develop')
   └─ Will fail: Could not resolve references

✅ DO USE: git_diff(source='a2bff62a', target='c91a9b05')
   └─ Use commit hashes from git_history()
   └─ Works perfectly

ALTERNATIVE: git_diff(source='HEAD~3', target='HEAD')
   └─ Also works: HEAD relatives
   └─ Great for comparing recent commits

Example Workflow:
  1. git_history(limit=10)
     → Get list of commits
  2. Find SHA you want: c91a9b05
  3. git_diff(source='a2bff62a', target='c91a9b05')
     → Shows exact changes ✅
```

### For Finding Code
```
GOAL: Search for functions or classes

❌ DON'T USE: search_code(pattern='.*Handler', search_type='classes')
   └─ Regex patterns not supported
   └─ Will find nothing

✅ DO USE: search_code(pattern='Handler', search_type='classes')
   └─ Substring matching works
   └─ Finds "ErrorHandler", "RequestHandler", etc.

✅ DO USE: search_code(pattern='validate', search_type='functions')
   └─ Partial name search
   └─ Finds "validate_input", "validate_config", etc.

Example Workflow:
  1. search_code('process', search_type='functions')
     → Find all process-related functions
  2. Substring matching works great for:
     - Naming patterns (validate_*, process_*, handle_*)
     - Class names (DataProcessor, Calculator, etc.)
     - Exact matches (fibonacci, add, etc.)
```

---

## Recommended Workflows

### Workflow 1: Feature Development on Branch
```
# Start work
1. git_checkout(target='feature/my-feature', create_if_missing=true)
   → Create and switch to feature branch ✅

# Make changes
2. apply_patch_advanced(...) or search_replace(...)
   → Modify code ✅

# Check progress
3. git_status(detailed=true)
   → See what changed ✅

# Save work
4. create_commit(message="Add feature X")
   → Save to feature branch ✅

# Push when ready
5. push_commits(branch_name='feature/my-feature')
   → Send to GitHub ✅
```

### Workflow 2: Code Review and Analysis
```
# Examine code
1. list_functions(file_path='src/*.py')
   → See all functions ✅

2. preview_code('src/app.py#ClassName')
   → View specific class ✅

3. grep_content(pattern='TODO|FIXME', context_after=2)
   → Find issues to fix ✅

# Find related code
4. find_function_calls(function_name='calculate_fibonacci')
   → See where it's used ✅

5. search_code('fibonacci', search_type='functions')
   → Find similar functions ✅
```

### Workflow 3: Refactoring with Rename
```
# Plan changes
1. search_code('old_name', search_type='functions')
   → Find all old_name functions ✅

# Preview changes
2. rename_symbol(old_name='old_name', new_name='new_name', dry_run=true)
   → See what would change (14 references) ✅

# Apply changes
3. rename_symbol(old_name='old_name', new_name='new_name')
   → Rename everywhere ✅

# Verify
4. search_code('new_name', search_type='functions')
   → Confirm rename worked ✅

# Commit
5. create_commit(message="refactor: rename old_name to new_name")
   → Save refactoring ✅
```

### Workflow 4: Comparing Changes Between Commits
```
# Get commit history
1. git_history(limit=5)
   → Shows recent commits with SHAs ✅

# Compare two commits
2. git_diff(source='a2bff62a', target='c91a9b05')
   → See what changed ✅

# Or compare relative to HEAD
3. git_diff(source='HEAD~3', target='HEAD')
   → Compare last 3 commits ✅

# Get details on specific commit
4. show_commit(commit_id='c91a9b05', show_diff=true)
   → See commit details ✅
```

### Workflow 5: Undo Changes (Without Reset)
```
# If you modified a file and want to undo

# Option A: Switch branch (resets files)
1. git_checkout(target='<current-branch>')
   → Files reset to branch state ✅

# Option B: Revert patch (undo the change)
2. search_replace(file='app.py', search='new_code', replace='old_code')
   → Manually revert ✅

# Option C: Copy from backup
3. copy_file(source_path='backups/app_v1.py', destination_path='app.py')
   → Restore from backup ✅

# AVOID: git_reset(hard=true)
❌ Will crash with AttributeError
```

---

## Known Limitations and Workarounds

| Tool | Limitation | Workaround |
|------|-----------|-----------|
| git_reset | Crashes on hard reset | Use git_checkout to reset files |
| git_diff | Can't use branch names | Use commit hashes from git_history |
| search_code | No regex patterns | Use substring search instead |

---

## Performance Notes

- **Large repositories**: list_functions() and list_classes() may take time
  - Tip: Use file_path filtering to limit scope
- **Complex patches**: apply_patch_advanced() handles multi-hunk patches efficiently
- **Grep searches**: With large codebases, results can be extensive
  - Tip: Use line_limit parameter to cap results

---

## Error Prevention Checklist

Before each operation:

- [ ] Creating commits? Make sure you're on a feature branch (not main)
- [ ] Running git_diff? Use commit hashes, not branch names
- [ ] Searching code? Remember substring, not regex
- [ ] Resetting files? Use git_checkout, not git_reset
- [ ] Renaming symbols? Run with dry_run=true first
- [ ] Removing files? Confirm with confirm=true parameter

---

## Testing Your Tools

### Test git_diff correctly
```python
# Get a recent commit hash
history = git_history(limit=1)
# Copy the commit SHA

# Use it in git_diff
git_diff(source='commit1_sha', target='commit2_sha')
# ✅ Works!
```

### Test search_code correctly
```python
# Search by partial name (substring)
search_code('validate', search_type='functions')
# ✅ Works! (finds validate_input, validate_config, etc.)

# NOT by regex
search_code('validate_.*', search_type='functions')
# ❌ Doesn't work (regex not supported)
```

### Test resetting files correctly
```python
# Make a change
search_replace('app.py', 'old', 'new')

# Reset it
git_checkout(target='<branch>')  # ✅ Works!
# NOT git_reset(hard=true)  # ❌ Crashes!
```

