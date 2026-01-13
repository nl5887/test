# Detailed Tool Analysis: git_reset, git_diff, and search_code

## 1. GIT_RESET - Detailed Analysis

### Purpose
Reset all changed files to match the current HEAD commit (equivalent to `git reset --hard HEAD`).
Discards all uncommitted changes permanently.

### Expected Behavior
```
Input:  File modified but not committed
        git_reset(hard=true)
Output: File restored to HEAD state
        Uncommitted changes discarded
```

### Error Encountered
```
❌ Error during git reset: 'tuple' object has no attribute 'sha'
Traceback (most recent call last):
  File "/work/skills/repository/skill.py", line 4853, in _run
    head_content = memory_repo[tree_entry.sha].data
                               ^^^^^^^^^^^^^^
AttributeError: 'tuple' object has no attribute 'sha'
```

### Root Cause Analysis
The error occurs at line 4853 in the repository skill code. The issue is:

1. **Type Mismatch**: `tree_entry` is a tuple, not an object with `.sha` attribute
2. **GitPython API Issue**: The tree iteration returns tuples `(mode, sha, name)` 
   instead of tree entry objects in this context
3. **Expected vs Actual**:
   - Expected: `tree_entry` is a GitPython TreeEntry object with `.sha` attribute
   - Actual: `tree_entry` is a tuple `(mode, sha, name)`

### Code Issue
```python
# WRONG - Assumes tree_entry is object
head_content = memory_repo[tree_entry.sha].data

# CORRECT - tree_entry is tuple (mode, sha, name)
mode, sha, name = tree_entry
head_content = memory_repo[sha].data
```

### Current Status
- **Not Working**: Hard reset with uncommitted changes
- **Why**: Type handling error in tree traversal
- **Impact**: Cannot reset modified files to HEAD state
- **Workaround**: Use git_checkout to switch branches (resets files)

### Test Case That Fails
```python
# Step 1: Modify a file
search_replace("src/app.py", "import json", "import json\n# MODIFIED")
# Result: ✅ File modified

# Step 2: Check status
git_status()
# Result: ✅ Shows "1 modified file"

# Step 3: Reset changes
git_reset(hard=true)
# Result: ❌ AttributeError: 'tuple' object has no attribute 'sha'
```

---

## 2. GIT_DIFF - Detailed Analysis

### Purpose
Show differences between two branches, commits, or references.
Displays what changed to transform source into target.

### Expected Behavior
```
git_diff(source='commit1', target='commit2')
→ Shows all files changed between commits
```

### Issue Found
**Branch name references fail, but commit hashes work perfectly**

### Failed Attempt
```
git_diff(source='main', target='feature/add-app-module')

Result:
❌ Could not resolve references: main or feature/add-app-module
```

### Successful Attempts
```
# Test 1: Using commit hashes
git_diff(source='a2bff62a', target='c91a9b05')
Result: ✅ SUCCESS
📊 Git Diff Summary (a2bff62a → c91a9b05):
   Files changed: 4
   [+] backups/app_v1.py
   [+] src/app.py
   [+] src/config.py
   [+] src/utils.py

# Test 2: HEAD references
git_diff(source='HEAD~3', target='HEAD')
Result: ✅ SUCCESS
📊 Git Diff Summary (HEAD~3 → HEAD):
   Files changed: 6
   [-] app.py
   [+] backups/app_v1.py
   [+] src/app.py
   [+] src/config.py
   [+] src/utils.py
   [-] utils.py

# Test 3: Sequential commits
git_diff(source='49ca6b33', target='ca810f12')
Result: ✅ SUCCESS
📊 Git Diff Summary (49ca6b33 → ca810f12):
   Files changed: 8
   ...
```

### Root Cause Analysis

1. **Reference Resolution Issue**: Branch names not properly resolved to commit SHAs
2. **What Works**:
   - Commit hashes (full SHA-1): `a2bff62a`, `c91a9b05`
   - HEAD references: `HEAD`, `HEAD~1`, `HEAD~3`
   - Relative refs: `HEAD~N` syntax
3. **What Doesn't Work**:
   - Branch names: `main`, `feature/add-app-module`
   - Remote refs: `origin/main` (not tested)
   - Tag names (not tested)

### Current Status
- **Partially Working**: Commit hashes and HEAD references work
- **Limited**: Branch name resolution not implemented
- **Impact**: Must use commit SHAs instead of branch names
- **Workaround**: Use commit hashes from git_history output

### Test Cases
```python
# ✅ WORKS - Using commit hash
git_diff(source='a2bff62a', target='c91a9b05')

# ✅ WORKS - Using HEAD relatives  
git_diff(source='HEAD~5', target='HEAD~1')

# ❌ FAILS - Using branch names
git_diff(source='main', target='feature/add-app-module')

# ❌ LIKELY FAILS - Using remote refs
git_diff(source='origin/main', target='HEAD')
```

---

## 3. SEARCH_CODE - Detailed Analysis

### Purpose
Search for functions and classes by pattern in the repository.
Supports pattern matching and exact name searches.

### Expected Behavior
```
search_code(pattern='Calculator', search_type='classes')
→ Finds class Calculator

search_code(pattern='.*Handler', search_type='classes')
→ Finds all classes matching regex pattern
```

### Actual Behavior
**Only exact name matching works. Regex patterns don't match.**

### Successful Searches (Exact Names)
```
# ✅ Exact class name
search_code(pattern='Calculator', search_type='classes')
Result: Found 2 matches (Calculator in 2 files)

# ✅ Exact function name
search_code(pattern='add', search_type='functions')
Result: Found 2 matches (add method in 2 files)

# ✅ Partial name match (substring)
search_code(pattern='validate', search_type='functions')
Result: Found 3 matches
  - validate_input
  - validate_input
  - validate_config

# ✅ Partial match works
search_code(pattern='process', search_type='functions')
Result: Found 3 matches
  - process_data
  - process_data
  - process
```

### Failed Searches (Regex/Pattern Matching)
```
# ❌ Regex pattern - No matches
search_code(pattern='Handler', search_type='classes')
Result: ❌ No matches found
Notes: ErrorHandler was deleted, but pattern didn't work anyway

# ❌ Regex pattern
search_code(pattern='Error', search_type='both')
Result: ❌ No matches found
Notes: No classes/functions with "Error" in name currently exist

# ✅ Would work if existed
search_code(pattern='.*Handler', search_type='classes')
Result: ❌ Not tested (no Handler classes exist)
```

### Root Cause Analysis

1. **Search Type**: Pattern matching uses substring search, not regex
2. **Limitations**:
   - Does NOT support regex patterns (e.g., `.*Handler`)
   - Does NOT support case-insensitive matching
   - DOES support substring matching (e.g., `Handler` finds `ErrorHandler`)
   - DOES support exact name matching

3. **How It Works**:
   - Pattern is checked against function/class names
   - Simple substring inclusion test (not regex)
   - Returns all matches containing the pattern

### Current Status
- **Working**: Exact names and substring matching
- **Limited**: No regex pattern support
- **Misleading**: Parameter name `pattern` suggests regex support
- **Impact**: Can find by partial names but not complex patterns

### Test Results Summary
```
Substring Search (Works):
  "validate"     → find validate_input, validate_config ✅
  "process"      → find process_data, process ✅
  "add"          → find add methods ✅
  "calculate"    → find calculate_fibonacci ✅

Regex Patterns (Don't work):
  ".*Handler"    → No match ❌
  "Error.*"      → No match ❌
  "[A-Z].*"      → No match ❌
```

---

## Summary Table

| Tool | Status | Issues | Workaround |
|------|--------|--------|-----------|
| git_reset | ❌ Broken | Type error: tuple vs object | Use git_checkout instead |
| git_diff | ⚠️ Partial | Branch refs fail, hashes work | Use commit SHAs not branch names |
| search_code | ⚠️ Limited | No regex, only substring | Use partial names for search |

