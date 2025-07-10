# grep: Ignore Case with -i Flag

The `-i` flag enables case-insensitivity.

```bash
# Match "error" in any case combination
grep -i "error" logfile.txt

# Matches all of these:
# ERROR: Database connection failed
# Error: Invalid user input
# error: file not found
# ErRoR: weird but still matches
```

## Practical Examples

```bash
# Find all log levels regardless of case
grep -i "warn\|error\|fatal" app.log

# Search for names in any case format
grep -i "john smith" contacts.csv

# Find SQL keywords in mixed-case queries
grep -i "select.*from" queries.log
```

Searching user-generated content:

```bash
# Find product mentions in reviews
grep -i "macbook" customer_feedback.txt

# Search code for function calls
grep -i "getUser" --include="*.js" -r .

# Find environment variables
grep -i "api_key" .env*
```

Combine with other flags:

```bash
# Case-insensitive whole word match
grep -i -w "java" resume.txt

# Recursive case-insensitive search
grep -r -i "password" config/

# Count case-insensitive matches
grep -i -c "failed" test_results.log
```

