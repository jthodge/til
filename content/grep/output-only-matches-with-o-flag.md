# grep: Output Only Matches with -o Flag

The `-o` flag displays only the matched text, _not_ entire lines.
This makes it great for extracting specific patterns.

```bash
# Extract only email addresses
grep -o "[^ ]*@[^ ]*" contacts.txt

# Output:
# john@example.com
# mary@company.org
# support@service.net
```

## Practical Examples

```bash
# Extract all URLs from HTML
grep -o 'href="[^"]*"' page.html

# Get all IP addresses
grep -o "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" access.log

# Extract version numbers
grep -o "v[0-9]\+\.[0-9]\+\.[0-9]\+" CHANGELOG.md
```

Data extraction and analysis:

```bash
# Extract all hashtags from tweets
grep -o "#[^ ]\+" tweets.txt | sort | uniq -c

# Get all function names from code
grep -o "function [a-zA-Z_]*" *.js | cut -d' ' -f2

# Extract timestamps
grep -o "[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}" system.log
```

Advanced pattern extraction:

```bash
# Extract JSON values
grep -o '"user": "[^"]*"' api.log | cut -d'"' -f4

# Get all hex color codes
grep -o "#[0-9A-Fa-f]\{6\}\b" styles.css

# Extract words ending in specific suffix
grep -o '\b[^ ]*tion\b' document.txt
```

