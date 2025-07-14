# grep: Recursive Search with -r Flag

The `-r` flag searches through directories recursively.

```bash
# Search all files under current directory
grep -r "API_KEY" .

# Search specific directory tree
grep -r "error" /var/log/
```

## Practical Examples

```bash
# Find all TODO comments in project
grep -r "TODO" src/

# Search for function usage
grep -r "getUserData()" app/

# Find hardcoded values
grep -r "localhost:3000" --include="*.js" .
```



Security audits and code reviews:

```bash
# Find potential security issues
grep -r "eval(" --include="*.php" .

# Locate sensitive data
grep -r -i "password\|secret\|key" config/

# Find deprecated APIs
grep -r "@deprecated" --include="*.java" src/
```

Control what to search:

```bash
# Include only specific files
grep -r "import" --include="*.py" .

# Exclude directories
grep -r "TODO" --exclude-dir=node_modules .

# Multiple exclusions
grep -r "console.log" \
  --exclude-dir={.git,dist,build} \
  --include="*.js" .
```

Performance tips:

```bash
# Follow symlinks
grep -R "pattern" .  # Capital R

# Limit depth (GNU grep)
grep -r --max-depth=2 "config" .

# Binary file handling
grep -r -I "text" .  # Skip binary files
```

