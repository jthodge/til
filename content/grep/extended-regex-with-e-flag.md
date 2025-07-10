# grep: Extended Regex with -E Flag

The `-E` flag enables extended regex, providing more powerful pattern matching without escaping special characters.

```bash
# Basic grep requires escaping
grep "a\+b" file.txt     # Matches one or more 'a' followed by 'b'

# Extended regex is cleaner
grep -E "a+b" file.txt   # Same result, no escaping needed
```

## Extended Regex Features

```bash
# Alternation (OR)
grep -E "error|warning|critical" log.txt

# Quantifiers
grep -E "ab+" file          # One or more b's
grep -E "ab?" file          # Zero or one b
grep -E "a{2,4}" file       # 2 to 4 a's

# Grouping
grep -E "(ha)+" file        # Matches "ha", "haha", "hahaha"
grep -E "^(INFO|WARN):" log # Lines starting with INFO: or WARN:
```

## Real-World Use Case

Log analysis and data extraction:

```bash
# Match multiple log levels
grep -E "^(ERROR|FATAL|CRITICAL):" app.log

# Extract semantic versions
grep -E "[0-9]+\.[0-9]+\.[0-9]+" CHANGELOG

# Find email domains
grep -E -o "@[a-zA-Z0-9]+\.(com|org|net)" emails.txt

# Match IP addresses
grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" access.log
```

Complex pattern matching:

```bash
# Phone numbers in multiple formats
grep -E "\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}" contacts.txt

# URLs with optional protocols
grep -E "(https?://)?(www\.)?[a-zA-Z0-9]+\.[a-z]+" page.html

# Time formats
grep -E "([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?" schedule.txt
```

`-E` vs basic grep:

```bash
# Basic (escaped)
grep "word\(s\)\?\|phrase\(s\)\?" file

# Extended (readable)
grep -E "word(s)?|phrase(s)?" file
```

