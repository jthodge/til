# grep: Show Context Lines with -C Flag

The `-C` (Context) flag shows lines both before and after matche to provide complete, surrounding context.

```bash
# Show 2 lines before and after each match
grep -C 2 "exception" debug.log

# Example output:
# Processing user request...
# Validating input parameters
# exception: null pointer reference
# Stack trace follows:
# at UserService.process(line 42)
```

## Practical Examples

```bash
# Find code changes with surrounding context
grep -C 3 "FIXME" src/*.py

# Locate configuration values with nearby settings
grep -C 5 "port:" docker-compose.yml

# Search log entries with full event context
grep -C 4 "timeout" service.log
```

Analyzing API requests and responses:

```bash
# Find failed API calls with request/response
grep -C 10 "status_code: 5" api_trace.log

# Debug authentication issues
grep -C 8 "unauthorized" auth.log

# Review database transactions
grep -C 6 "ROLLBACK" postgresql.log
```

Equivalent to using both -A and -B:

```bash
# These are identical
grep -C 3 "pattern" file.txt
grep -A 3 -B 3 "pattern" file.txt

# Asymmetric context when needed
grep -B 2 -A 5 "DELETE FROM" queries.log
```

