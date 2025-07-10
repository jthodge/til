# grep: Match Whole Words with -w Flag

The `-w` flag matches only complete words, preventing partial matches within larger words.

```bash
# Match "log" but not "login" or "catalog"
grep -w "log" files.txt

# Without -w would match: login, logout, catalog, blog
# With -w only matches: log (as a complete word)
```

## Practical Examples

```bash
# Find exact variable names in code
grep -w "id" *.py  # Won't match 'identity' or 'sidebar'

# Search for specific commands
history | grep -w "rm"  # Won't match 'chmod' or 'armv7'

# Find exact error codes
grep -w "404" server.log  # Won't match '4041' or '1404'
```

Code refactoring and precise searches:

```bash
# Find function calls, not definitions
grep -w "print" script.py  # Matches print() not printed

# Search for exact table names in SQL
grep -w "users" database.sql  # Not 'users_backup' or 'old_users'

# Find specific port numbers
grep -w "8080" config/  # Not '18080' or '80801'
```

Word boundaries in action:

```bash
# Find standalone numbers
grep -w "[0-9]\+" data.txt

# Match exact status codes
grep -w -E "200|404|500" access.log

# Case-insensitive whole word
grep -i -w "error" logs/  # ERROR but not ERRORS
```

