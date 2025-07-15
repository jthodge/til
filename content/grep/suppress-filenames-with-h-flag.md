# grep: Suppress Filenames with -h Flag

The `-h` flag hides filename prefixes when searching multiple files, showing only the matched lines.

```bash
# Search multiple files without filename prefix
grep -h "error" *.log

# Instead of:
# app.log:error: connection timeout
# system.log:error: disk full

# You get:
# error: connection timeout
# error: disk full
```

## Practical Examples

```bash
# Combine log files into unified view
grep -h "^2025-01" *.log | sort

# Extract all function definitions
grep -h "^def " *.py

# Collect all TODO comments
grep -h "TODO:" src/**/*.js
```

Creating consolidated reports:

```bash
# Merge all error messages for analysis
grep -h "ERROR" logs/*.log > all_errors.txt

# Extract all email addresses
grep -h -o "[a-zA-Z0-9._%+-]\+@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}" *.txt

# Combine configuration values
grep -h "^export" ~/.bashrc ~/.zshrc ~/.profile
```

Useful with pipes and redirection:

```bash
# Count unique error types
grep -h "error:" *.log | sort | uniq -c

# Find most common IP addresses
grep -h -o "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" access.* | sort | uniq -c | sort -nr

# Create unified TODO list
grep -h -i "todo\|fixme" **/*.py | nl
```

