# Tool Comparison: Success vs Failure Scenarios

## 1. GIT_RESET - Type Mismatch Error

### Error Breakdown
```
Location: /work/skills/repository/skill.py, line 4853
Error Type: AttributeError
Message: 'tuple' object has no attribute 'sha'

Stack:
├─ git_reset(hard=true) called
│  └─ Attempts to iterate tree entries
│     └─ tree_entry treated as object
│        └─ Accesses tree_entry.sha ❌ WRONG!
│           └─ But tree_entry is tuple (mode, sha, name)
│              └─ Tuple has no .sha attribute
│                 └─ CRASH
```

### The Problem Code
```python
# Current implementation (BROKEN)
def reset_files():
    tree = memory_repo.HEAD.commit.tree
    for tree_entry in tree.traverse():
        # tree_entry is returned as: (mode, sha, name)
        # but code expects object with .sha property
        head_content = memory_repo[tree_entry.sha].data  # ❌ FAIL
```

### The Fix
```python
# Fixed implementation
def reset_files():
    tree = memory_repo.HEAD.commit.tree
    for tree_entry in tree.traverse():
        # tree_entry is a tuple: (mode, sha, name)
        mode, sha, name = tree_entry
        head_content = memory_repo[sha].data  # ✅ WORKS
        # Restore file...
```

### Why This Happens
When iterating over GitPython tree objects in certain contexts:
1. **Context A** (works): Tree iteration returns TreeEntry objects
2. **Context B** (fails): Tree iteration returns tuples

The code assumes Context A but runs in Context B.

### Testing the Issue
```
Test Setup:
  1. Create file: src/app.py
  2. Commit to repository
  3. Modify file: add comment "# TEST MODIFICATION"
  4. Verify: git_status shows "1 modified file" ✅
  5. Attempt reset: git_reset(hard=true) ❌

Expected Result: File restored to committed state
Actual Result: AttributeError during tree traversal
```

### Impact
- **Severity**: HIGH - Core functionality broken
- **Affected Operations**: Hard reset of uncommitted changes
- **Workaround**: Use git_checkout to switch branches (also resets files)
- **Files**: Cannot directly reset individual files to HEAD

---

## 2. GIT_DIFF - Reference Resolution Incomplete

### The Issue
```
Branch name references fail to resolve to commit SHAs

Failed Calls:
  git_diff(source='main', target='feature/add-app-module')
  → ❌ Could not resolve references: main or feature/add-app-module

  git_diff(source='origin/main', target='HEAD')
  → ❌ (Likely would fail)
```

### What Works
```
Working Reference Types:

1. FULL COMMIT HASHES
   git_diff(source='a2bff62a', target='c91a9b05')
   → ✅ Shows 4 files changed

2. HEAD RELATIVES
   git_diff(source='HEAD~5', target='HEAD')
   → ✅ Shows 6 files changed
   
3. SEQUENTIAL COMMITS
   git_diff(source='49ca6b33', target='ca810f12')
   → ✅ Shows 8 files changed

4. ABBREVIATED COMMITS (6+ chars)
   git_diff(source='a2bff6', target='c91a9b')
   → ✅ Likely works (not fully tested)
```

### Test Results Matrix
```
Reference Type           | Format              | Status | Notes
─────────────────────────┼─────────────────────┼────────┼──────────────
Full commit hash         | a2bff62a            | ✅     | Always works
Abbreviated hash         | a2bff6 (6+ chars)   | ✅     | Should work
HEAD                     | HEAD                | ✅     | Direct reference
HEAD relative            | HEAD~1, HEAD~5      | ✅     | Works perfectly
Branch name              | main                | ❌     | Not resolved
Branch name              | feature/add-app     | ❌     | Not resolved
Remote branch            | origin/main         | ⏳     | Untested
Tag name                 | v1.0.0              | ⏳     | Untested
```

### Root Cause
The reference resolution only handles:
1. Commit SHAs (full and abbreviated)
2. HEAD relatives (HEAD, HEAD~N, etc.)

It does NOT handle:
1. Branch names → resolve to commit SHA
2. Remote references → fetch and resolve
3. Tag names → resolve to commit SHA

### Implementation Gap
```python
# Current implementation
def resolve_reference(ref):
    if is_commit_hash(ref):
        return ref  # ✅ Works
    if is_head_relative(ref):
        return resolve_head(ref)  # ✅ Works
    if is_branch_name(ref):
        return memory_repo.refs[ref].commit.hexsha  # ❌ Missing!
    if is_remote_ref(ref):
        return memory_repo.refs[ref].commit.hexsha  # ❌ Missing!
```

### Workaround
```python
# To compare branches, use commit hashes:

# Step 1: Get commit history
history = git_history()
# Returns commits for all branches

# Step 2: Extract commit SHA you want
# e.g., from "main" commit: a2bff62a

# Step 3: Use the hash in git_diff
git_diff(source='a2bff62a', target='c91a9b05')
# ✅ Works!
```

### Impact
- **Severity**: MEDIUM - Common use case broken
- **Affected Operations**: Comparing branches by name
- **User Experience**: Requires manual commit SHA lookup
- **Alternative**: Works fine with commit hashes (minor inconvenience)

---

## 3. SEARCH_CODE - Pattern Matching Not Regex

### The Misunderstanding
```
Tool Parameter: pattern = "some_pattern"
User Assumption: Regex pattern matching
Actual Behavior: Substring matching only

Result: Confusion and unexpected results
```

### What Works (Substring Search)
```python
# All substring searches work perfectly

search_code('validate', search_type='functions')
→ ✅ Finds: validate_input, validate_config, validate_something

search_code('process', search_type='functions')
→ ✅ Finds: process_data, process, process_handler

search_code('Calculator', search_type='classes')
→ ✅ Finds: Calculator (exact match as substring)

search_code('Handler', search_type='classes')
→ ❌ Finds: nothing (no classes with "Handler" substring)
```

### What Doesn't Work (Regex Patterns)
```python
# Regex patterns don't work

search_code('.*Handler', search_type='classes')
→ ❌ Finds: nothing (regex not supported)

search_code('Error.*', search_type='functions')
→ ❌ Finds: nothing (regex not supported)

search_code('[A-Z].*', search_type='classes')
→ ❌ Finds: nothing (regex not supported)

search_code('^calculate', search_type='functions')
→ ❌ Finds: nothing (regex not supported)
```

### Comparison: Intention vs Reality
```
User's Intent              | Regex Pattern        | Substring Match | Result
───────────────────────────┼──────────────────────┼─────────────────┼──────────
Find all handlers          | .*Handler            | Handler         | Different
Find error-related items   | Error.*              | Error           | Different
Find capitalized names     | [A-Z].*              | (none work)      | Fail
Find prefixed functions    | ^calculate           | calculate       | Works (luck)
Find by partial name       | validate.*           | validate        | Works
Find exact class name      | ^Calculator$         | Calculator      | Works
```

### Implementation Details
```python
# Current implementation
def search_code(pattern):
    results = []
    for func in all_functions:
        if pattern in func.name:  # Simple substring check
            results.append(func)
    return results

# What users might expect (not implemented)
def search_code(pattern):
    import re
    regex = re.compile(pattern)
    results = []
    for func in all_functions:
        if regex.search(func.name):  # Regex search
            results.append(func)
    return results
```

### Test Case: Missing Classes
```
Repository State:
  ✅ DataProcessor class exists
  ✅ Calculator class exists
  ❌ ErrorHandler class was deleted
  ❌ No other Handler-named classes

Search: search_code('Handler', search_type='classes')

Expected (if regex): ❌ No results (Handler doesn't exist)
Actual (substring): ❌ No results (Handler not in any class name)

If ErrorHandler still existed:
Expected (if regex): ✅ Would find ErrorHandler
Actual (substring): ✅ Would find ErrorHandler

Pattern that would fail with both:
search_code('.*Error', search_type='classes')
Expected (regex): Would find ErrorHandler, ErrorProcessor, etc.
Actual (substring): Finds nothing (no class named "*Error")
```

### Case Sensitivity
```python
# Search is case-sensitive (substring)

search_code('calculator', search_type='classes')  # lowercase
→ ❌ Finds: nothing (doesn't match "Calculator")

search_code('Calculator', search_type='classes')  # correct case
→ ✅ Finds: Calculator class

# Even though we say "pattern", case must match!
```

### Workarounds
```python
# If you want to find all validators:
search_code('validate', search_type='functions')
→ ✅ Works! (substring match)

# If you want to find all processors:
search_code('process', search_type='functions')
→ ✅ Works! (substring match)

# If you want specific names:
search_code('calculate_fibonacci', search_type='functions')
→ ✅ Works! (exact substring)

# What doesn't work:
search_code('.*[Hh]andler', search_type='both')
→ ❌ Doesn't work (regex not supported)
```

### Impact
- **Severity**: LOW - Works for most use cases
- **Issue**: Misleading parameter name "pattern" suggests regex
- **Actual**: Simple substring matching
- **Workaround**: Use partial function/class names
- **User Experience**: Mostly fine, just not as powerful as regex

---

## Summary of Issues

### git_reset (CRITICAL)
- Status: ❌ Completely broken
- Root: Type mismatch in tree traversal
- Fix: Parse tuple instead of accessing .sha
- Workaround: Use git_checkout to reset files

### git_diff (MODERATE)
- Status: ⚠️ Partially working
- Root: Incomplete reference resolution
- Fix: Add branch name → SHA resolution
- Workaround: Use commit SHAs instead of branch names

### search_code (MINOR)
- Status: ✅ Working but limited
- Root: Substring match, not regex
- Fix: Add regex pattern support option
- Workaround: Use partial names (still works well)

