# Detailed Analysis: git_reset, git_diff, search_code

## Executive Summary

Three tools were identified with issues during comprehensive testing:

| Tool | Severity | Type | Root Cause | Impact |
|------|----------|------|-----------|--------|
| **git_reset** | 🔴 CRITICAL | Runtime Error | Type mismatch (tuple vs object) | Cannot reset files |
| **git_diff** | 🟡 MODERATE | Incomplete Feature | Missing reference resolution | Cannot use branch names |
| **search_code** | 🟢 MINOR | Design Limitation | No regex support | Substring only |

---

## 1. GIT_RESET - Critical Type Error

### 1.1 Error Details

**Error Message:**
```
❌ Error during git reset: 'tuple' object has no attribute 'sha'

File: /work/skills/repository/skill.py
Line: 4853
Type: AttributeError
```

**Stack Trace:**
```python
Traceback (most recent call last):
  File "/work/skills/repository/skill.py", line 4853, in _run
    head_content = memory_repo[tree_entry.sha].data
                               ^^^^^^^^^^^^^^
AttributeError: 'tuple' object has no attribute 'sha'
```

### 1.2 Root Cause Analysis

**The Problem:**
The code at line 4853 assumes `tree_entry` is an object with a `.sha` attribute:
```python
head_content = memory_repo[tree_entry.sha].data  # ← Assumes object
```

**The Reality:**
`tree_entry` is actually a tuple from tree traversal:
```python
tree_entry = (mode, sha, name)  # ← Tuple returned
# Trying to access .sha on tuple fails!
```

**Why This Happens:**
1. Code iterates over `tree.traverse()` 
2. Different GitPython versions or contexts return different types
3. Sometimes returns TreeEntry objects (has .sha attribute)
4. Sometimes returns tuples (no .sha attribute)
5. Code only handles case 1, crashes in case 2

### 1.3 Code Comparison

**BROKEN CODE:**
```python
def reset_hard():
    tree = memory_repo.HEAD.commit.tree
    
    # Iterate tree entries
    for tree_entry in tree.traverse():
        # Assumes tree_entry is object like TreeEntry
        # But actually gets tuple (mode, sha, name)
        head_content = memory_repo[tree_entry.sha].data  # ❌ CRASH
        
        # Write content back...
        virtual_file_path = tree_entry.path
```

**FIXED CODE:**
```python
def reset_hard():
    tree = memory_repo.HEAD.commit.tree
    
    # Iterate tree entries
    for item in tree.traverse():
        # Handle both cases: object or tuple
        if isinstance(item, tuple):
            mode, sha, name = item  # ✅ Unpack tuple
        else:
            sha = item.sha  # ✅ Access object
            name = item.path
        
        head_content = memory_repo[sha].data  # ✅ Works!
        
        # Write content back...
```

### 1.4 When This Fails

**Trigger Conditions:**
1. Create a file or modify existing file
2. Verify file is changed (git_status shows modifications)
3. Call git_reset(hard=true)
4. → CRASH with AttributeError

**Test Case:**
```python
# Step 1: Modify file
search_replace('src/app.py', 'import json', 'import json\n# MODIFIED')
# ✅ File modified successfully

# Step 2: Verify modification
git_status(detailed=true)
# ✅ Shows: "1 modified file"

# Step 3: Try to reset
git_reset(hard=true)
# ❌ Crash! AttributeError: 'tuple' object has no attribute 'sha'
```

### 1.5 Impact Assessment

**Severity: CRITICAL**

**Affected Operations:**
- `git_reset(hard=true)` - Cannot hard reset
- All reset scenarios with uncommitted changes
- File restoration to HEAD state

**User Experience:**
- Feature doesn't work at all (always crashes)
- No partial success or workaround within the tool
- Complete failure of git reset functionality

**Workaround:**
```python
# Instead of: git_reset(hard=true)
# Use this:
git_checkout(target='current-branch')
# Both reset files to branch state
# git_checkout works, git_reset crashes
```

---

## 2. GIT_DIFF - Incomplete Reference Resolution

### 2.1 The Issue

**What Fails:**
```python
git_diff(source='main', target='feature/add-app-module')
# ❌ Could not resolve references: main or feature/add-app-module
```

**Why It Fails:**
Branch names are not resolved to commit SHAs

### 2.2 Working vs Non-Working Cases

**WORKING CASES:**

1. **Full Commit Hashes:**
```python
git_diff(source='a2bff62a', target='c91a9b05')
# ✅ SUCCESS: Shows 4 files changed
```

2. **HEAD Relatives:**
```python
git_diff(source='HEAD~5', target='HEAD')
# ✅ SUCCESS: Shows 6 files changed

git_diff(source='HEAD', target='HEAD~1')
# ✅ SUCCESS: Works
```

3. **Sequential Commits:**
```python
git_diff(source='49ca6b33', target='ca810f12')
# ✅ SUCCESS: Shows 8 files changed
```

**NON-WORKING CASES:**

1. **Branch Names:**
```python
git_diff(source='main', target='develop')
# ❌ FAIL: Could not resolve references

git_diff(source='feature/add-app-module', target='main')
# ❌ FAIL: Could not resolve references
```

2. **Remote References:**
```python
git_diff(source='origin/main', target='origin/develop')
# ❌ LIKELY FAIL: Not tested, but pattern suggests no support
```

3. **Tag Names:**
```python
git_diff(source='v1.0.0', target='v2.0.0')
# ❌ LIKELY FAIL: Not tested, but pattern suggests no support
```

### 2.3 Resolution Implementation Gap

**Current Implementation:**
```python
def resolve_reference(ref):
    # Handle commit hashes
    if looks_like_commit_sha(ref):
        return resolve_sha(ref)  # ✅ Works
    
    # Handle HEAD relatives
    if ref.startswith('HEAD'):
        return resolve_head_relative(ref)  # ✅ Works
    
    # Everything else fails
    raise Exception(f"Could not resolve references: {ref}")
```

**What's Missing:**
```python
def resolve_reference(ref):
    # ... existing code ...
    
    # MISSING: Branch resolution
    if is_branch_name(ref):
        try:
            return memory_repo.refs[ref].commit.hexsha
        except:
            pass  # Not a local branch
    
    # MISSING: Remote reference resolution  
    if is_remote_ref(ref):
        try:
            return memory_repo.refs[f'origin/{ref}'].commit.hexsha
        except:
            pass  # Not a remote branch
    
    # MISSING: Tag resolution
    if is_tag_name(ref):
        try:
            return memory_repo.tags[ref].commit.hexsha
        except:
            pass  # Not a valid tag
```

### 2.4 Test Results Matrix

```
Reference Type              | Format              | Works?
────────────────────────────┼─────────────────────┼────────
Full commit hash            | a2bff62a            | ✅ YES
Abbreviated hash (6+ chars) | a2bff6              | ✅ YES (likely)
HEAD keyword                | HEAD                | ✅ YES
HEAD relative (n)           | HEAD~1, HEAD~5      | ✅ YES
Local branch                | main, develop       | ❌ NO
Local branch (path)         | feature/my-feature  | ❌ NO
Remote branch               | origin/main         | ⏳ UNKNOWN
Tag                         | v1.0.0              | ⏳ UNKNOWN
```

### 2.5 Workaround

**When you need to compare branches:**

```python
# Step 1: Get commit history (includes all branches)
history = git_history(limit=20)

# Step 2: Find the commit SHA for your branch
# Look through history output for desired branch commits
# Example output: "📝 a2bff62a - Initial commit"

# Step 3: Use the SHA in git_diff
git_diff(source='a2bff62a', target='c91a9b05')
# ✅ Works perfectly!
```

### 2.6 Impact Assessment

**Severity: MODERATE**

**Affected Operations:**
- Comparing branches by name (common workflow)
- User must lookup commit SHAs manually
- All branch-based comparisons fail

**User Experience:**
- Workaround exists (use commit hashes)
- Requires extra steps (get history first)
- Minor inconvenience, not critical

---

## 3. SEARCH_CODE - Pattern Matching Limitation

### 3.1 The Misunderstanding

**Parameter Name:** `pattern`
**User Expectation:** Regex pattern matching
**Actual Behavior:** Substring matching only

### 3.2 What Works (Substring Matching)

```python
# All of these work - substring matching

search_code('validate', search_type='functions')
# Finds: validate_input, validate_config, validate_something

search_code('process', search_type='functions')
# Finds: process_data, process, data_process_handler

search_code('Handler', search_type='classes')
# Finds: ErrorHandler, RequestHandler, ResponseHandler

search_code('Calculator', search_type='classes')
# Finds: Calculator, MultiCalculator, AdvancedCalculator
```

### 3.3 What Doesn't Work (Regex Patterns)

```python
# None of these work - regex not supported

search_code('.*Handler', search_type='classes')
# Expected: All classes ending in Handler
# Actual: No matches (literal pattern ".*Handler" not found)

search_code('^calculate', search_type='functions')
# Expected: Functions starting with 'calculate'
# Actual: No matches (literal pattern "^calculate" not found)

search_code('[A-Z].*', search_type='functions')
# Expected: Classes/functions starting with capital letter
# Actual: No matches (regex brackets not supported)

search_code('Error|Exception', search_type='both')
# Expected: Things with Error OR Exception
# Actual: No matches (pipe character interpreted literally)
```

### 3.4 Implementation Detail

**Current Search Algorithm:**
```python
def search_code(pattern, search_type='both'):
    results = []
    
    if search_type in ['functions', 'both']:
        for func in all_functions:
            if pattern in func.name:  # ← Simple substring check!
                results.append(func)
    
    if search_type in ['classes', 'both']:
        for cls in all_classes:
            if pattern in cls.name:  # ← Simple substring check!
                results.append(cls)
    
    return results
```

**What Users Might Expect:**
```python
import re  # (not used currently)

def search_code(pattern, search_type='both', use_regex=False):
    results = []
    
    if use_regex:
        regex = re.compile(pattern)
        matcher = lambda name: regex.search(name) is not None
    else:
        matcher = lambda name: pattern in name
    
    # ... apply matcher ...
    
    return results
```

### 3.5 Case Sensitivity

Search is case-sensitive:
```python
search_code('calculator', search_type='classes')
# ❌ No results (doesn't match "Calculator")

search_code('Calculator', search_type='classes')
# ✅ Finds Calculator class

search_code('CALCULATOR', search_type='classes')
# ❌ No results (doesn't match case)
```

### 3.6 Impact Assessment

**Severity: LOW**

**Why It's Low Severity:**
- Substring matching actually works well for most use cases
- Developers usually name functions with patterns (validate_*, process_*, etc.)
- Partial name search is intuitive and useful
- Regex would be nice but not critical

**Issue:**
- Parameter name "pattern" suggests regex capability
- Misleading documentation or API design
- Users attempting regex patterns get silent failure (no matches)

**Workaround:**
```python
# Instead of: search_code('.*validate.*', search_type='functions')
# Use this:  search_code('validate', search_type='functions')
# Both find validation functions, second is simpler!
```

---

## Comparison Summary

```
╔══════════════╦═════════════╦═════════════════════╦═══════════════════╗
║ Tool         ║ Severity    ║ Root Cause          ║ Workaround        ║
╠══════════════╬═════════════╬═════════════════════╬═══════════════════╣
║ git_reset    ║ 🔴 CRITICAL ║ Type error          ║ Use git_checkout  ║
║ git_diff     ║ 🟡 MODERATE ║ Missing resolution  ║ Use commit hashes ║
║ search_code  ║ 🟢 MINOR    ║ Design limitation   ║ Use partial names ║
╚══════════════╩═════════════╩═════════════════════╩═══════════════════╝
```

---

## Recommendations for Users

### For git_reset Users
✅ **DO:** Use `git_checkout(target='branch')` to reset files
❌ **DON'T:** Use `git_reset(hard=true)` - will crash

### For git_diff Users
✅ **DO:** Use commit SHAs from `git_history()` output
❌ **DON'T:** Use branch names like 'main' or 'develop'

### For search_code Users
✅ **DO:** Use substring search for naming patterns
❌ **DON'T:** Try regex patterns - they don't work

