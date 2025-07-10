# grep: Invert Match with -v Flag

The `-v` flag inverts the match to show all lines that do _NOT_ contain the pattern.

```bash
# Show all lines except those containing "debug"
grep -v "debug" application.log

# Remove comment lines from config
grep -v "^#" nginx.conf

# Filter out empty lines
grep -v "^$" document.txt
```

## Practical Examples

```bash
# Show all files except README files
ls -la | grep -v README

# Find non-successful HTTP status codes
grep -v "200 OK" access.log

# Remove verbose logging
tail -f app.log | grep -v "TRACE\|DEBUG"
```

Filtering test results and system processes:

```bash
# Show only failed tests
pytest --tb=short | grep -v "PASSED"

# Find inactive users
grep -v "active" user_status.csv

# Show processes excluding system ones
ps aux | grep -v "^root"

# Filter out successful builds
grep -v "BUILD SUCCESSFUL" ci_logs.txt
```

Powerful combinations:

```bash
# Remove comments and empty lines
grep -v "^#" config.ini | grep -v "^$"

# Exclude multiple patterns
grep -v -e "INFO" -e "DEBUG" system.log

# Case-insensitive exclusion
grep -i -v "success" results.txt
```

