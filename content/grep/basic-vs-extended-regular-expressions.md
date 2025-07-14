# Basic vs extended regular expressions in `grep`

`grep` uses basic regular expressions (BRE) by default, not  extended regular
expressions (ERE) you might expect from Perl or Python-flavored regex.
This causes common regex patterns to fail unexpectedly.

## The problem

A regex that works in Python or Perl might not work in grep:

```bash
# This fails with default grep
echo 123 | grep "[0-9]{3}"
# No output

# This works
echo 123 | grep "[0-9]\{3\}"
# Output: 123
```

## Basic vs Extended Regular Expressions

### Quantifiers

**Basic (BRE)**
```bash
# Repetition quantifiers need escaping
echo 123 | grep "[0-9]\{3\}"           # Match exactly 3 digits
echo 123.45 | grep "[0-9]\{3,5\}"      # Match 3 to 5 digits
echo test | grep "t\{1,\}"             # Match 1 or more t's
```

**Extended (ERE)**
```bash
# Quantifiers work without escaping
echo 123 | grep -E "[0-9]{3}"          # Match exactly 3 digits
echo 123.45 | grep -E "[0-9]{3,5}"     # Match 3 to 5 digits
echo test | grep -E "t{1,}"            # Match 1 or more t's
```

### Grouping and alternation

**Basic (BRE):**
```bash
# Parentheses and pipe need escaping
echo "cat" | grep "\(cat\|dog\)"       # Match cat or dog
echo "abc" | grep "\(ab\)\{2\}"         # Match "ab" twice
```

**Extended (ERE):**
```bash
# Natural syntax for grouping
echo "cat" | grep -E "(cat|dog)"       # Match cat or dog
echo "abab" | grep -E "(ab){2}"        # Match "ab" twice
```

## Enabling extended regex support

### Using -E flag

The `-E` flag enables extended regular expressions:

```bash
# ICD code pattern example
echo "123.4" | grep -E "[0-9]{3}\.?[0-9]{0,2}"

# Multiple options
echo "123.45" | grep -E "[0-9]{3,5}\.?[0-9]{0,2}"

# With sed
echo "123.4" | sed -E -n "/[0-9]{3}\.?[0-9]{0,2}/p"
```

### Using egrep

`egrep` is equivalent to `grep -E`:

```bash
# These are identical
echo "test123" | egrep "[a-z]+[0-9]{3}"
echo "test123" | grep -E "[a-z]+[0-9]{3}"
```

## Real-world examples

### Finding phone numbers

```bash
# BRE version
grep "\([0-9]\{3\}\) \?[0-9]\{3\}-[0-9]\{4\}" contacts.txt

# ERE version (cleaner)
grep -E "\([0-9]{3}\) ?[0-9]{3}-[0-9]{4}" contacts.txt
```

### Validating email patterns

```bash
# Basic version (cumbersome)
grep "[a-zA-Z0-9]\+@[a-zA-Z0-9]\+\.[a-zA-Z]\{2,\}" emails.txt

# Extended version (readable)
grep -E "[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}" emails.txt
```

### Log file analysis

```bash
# Find error patterns with timestamps
grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.*(ERROR|FATAL)" app.log

# Extract IP addresses
grep -E "[0-9]{1,3}(\.[0-9]{1,3}){3}" access.log
```

## Tool-specific behavior

### awk uses ERE by default

```bash
# awk naturally uses extended regex
echo "123.4" | awk "/[0-9]{3}\.?[0-9]{0,2}/"
```

### Different grep implementations

```bash
# GNU grep supports Perl-compatible regex
echo "test123" | grep -P "\d{3}"

# But this may not work on all systems
echo "test123" | grep -E "[0-9]{3}"  # More portable
```

## Common gotchas

### Dot metacharacter

```bash
# Literal dot needs escaping in all regex flavors
echo "192.168.1.1" | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
```

### Character classes

```bash
# These work in both BRE and ERE
grep "[0-9]" file.txt      # Digit
grep "[a-zA-Z]" file.txt   # Letter
grep "[[:alpha:]]" file.txt # POSIX character class
```

### Anchors

```bash
# Anchors work the same in BRE and ERE
grep -E "^[0-9]{3}" file.txt    # Start of line
grep -E "[0-9]{3}$" file.txt    # End of line
grep -E "\b[0-9]{3}\b" file.txt # Word boundaries
```

## Migration

When converting patterns from programming languages to grep:

1. **Add `-E` flag** for extended regex support
2. **Replace `\d` with `[0-9]`** for digit matching
3. **Use POSIX character classes** like `[[:digit:]]` for portability
4. **Test across different grep implementations**

```bash
# Portable pattern for finding numbers
grep -E "[0-9]+" file.txt

# Instead of Perl/Python style
grep -P "\d+" file.txt  # May not work everywhere
```

