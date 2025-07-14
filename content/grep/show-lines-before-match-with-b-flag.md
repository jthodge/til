# grep: Show Lines Before Match with -B Flag

The `-B` (Before) flag displays lines preceding a match.

```bash
# Show 3 lines before each match
grep -B 3 "failed" deployment.log

# Example output:
# Starting deployment process...
# Checking dependencies...
# Memory allocation: 2GB
# failed: insufficient resources
```

## Practical Examples

```bash
# Find errors and see what preceded them
grep -B 5 "ERROR" application.log

# Check git commits before a specific change
git log --oneline | grep -B 4 "hotfix"

# Find test failures with setup context
grep -B 10 "AssertionError" pytest.log
```

Troubleshooting build failures:

```bash
# See compilation steps before error
grep -B 15 "compilation terminated" build.log

# Find database queries before timeout
grep -B 7 "Lock wait timeout exceeded" mysql.log

# Review request headers before 404 errors
grep -B 6 "404 Not Found" nginx.log
```

Combine with line numbers for precise location:

```bash
# Show line numbers with context
grep -n -B 3 "panic:" server.log

# Multiple patterns with before context
grep -B 2 -e "WARN" -e "ERROR" app.log
```

