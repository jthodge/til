# grep: Show Lines After Match with -A Flag

The `-A` (After) flag displays lines following a match

```bash
# Show 3 lines after each match
grep -A 3 "error" logfile.txt

# Example output:
# error: connection refused
# timestamp: 2025-01-07 14:23:45
# severity: high
# action: retry attempted
```

## Practical Examples

```bash
# Find function definitions and see their body
grep -A 5 "^def " script.py

# Locate config section headers and show settings
grep -A 10 "^\[database\]" config.ini

# Find TODO comments with context
grep -A 2 "TODO:" src/*.js
```

Debugging application crashes by finding stack traces:

```bash
# Find exception and show full stack trace
grep -A 20 "Exception:" app.log

# Search for failed tests and see error details
grep -A 15 "FAILED" test_results.txt

# Find HTTP 500 errors with request details
grep -A 8 "HTTP/1.1 500" access.log
```

Combine with other flags for more power:

```bash
# Case-insensitive search with context
grep -i -A 4 "warning" system.log

# Show filename and line numbers
grep -n -A 3 "CRITICAL" *.log
```

