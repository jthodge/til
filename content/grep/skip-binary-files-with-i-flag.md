# grep: Skip Binary Files with -I Flag

The `-I` (uppercase i) flag treats binary files as if they contain no matches.
This can improve performance by speeding up searches in heterogeneous  codebases.

```bash
# Search text files only, skip binaries
grep -r -I "SearchTerm" .

# Without -I: searches PDFs, images, executables (slow)
# With -I: skips non-text files (fast)
```

## Practical Examples

```bash
# Search source code, ignore compiled files
grep -r -I "className" build/

# Find text in mixed-content directories
grep -I "user_id" uploads/

# Search logs alongside binary data
grep -r -I "ERROR" /var/app/
```

Efficient codebase searching:

```bash
# Search Git repository (with binary assets)
grep -r -I "TODO" --exclude-dir=.git .

# Find strings in web project
grep -r -I "localhost" \
  --exclude-dir={node_modules,dist,.next} \
  public/

# Search mixed media folders
grep -r -I "copyright" assets/
```

Identify binary vs text files:

```bash
# List binary files in directory
find . -type f -exec grep -IL . {} \; 2>/dev/null

# Count text files containing pattern
grep -r -I -l "pattern" . | wc -l

# Process only text files
grep -r -I -l . | xargs wc -l
```

Performance comparison:

```bash
# Slow: searches inside PDFs, images, etc.
time grep -r "text" large_directory/

# Fast: skips binary files
time grep -r -I "text" large_directory/
```

