# Use Verbose Mode and Named Groups for Readable Patterns

Python's `re`  module provides:
- verbose mode for multi-line regexes with comments
- named groups for accessing matches by name
- function replacements for complex substitutions.

## Verbose Mode with `(?x)`

The `(?x)` flag enables verbose regex syntax, allowing whitespace and comments:

```python
# E.g. parsing log entries
log_pattern = r"""(?x)
    ^                           # Start of line
    \[                          # Opening bracket
        (?P<timestamp>          # Capture timestamp
            \d{4}-\d{2}-\d{2}   # Date: YYYY-MM-DD
            \s+                 # Whitespace
            \d{2}:\d{2}:\d{2}  # Time: HH:MM:SS
        )
    \]                          # Closing bracket
    \s+                         # Whitespace
    (?P<level>\w+)              # Log level (INFO, ERROR, etc)
    \s+-\s+                     # Separator
    (?P<message>.+)             # Rest of the line is the message
    $                           # End of line
"""

# Compare to inscrutable one-liner:
# r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+(\w+)\s+-\s+(.+)$"
```

## Named Groups and Function Replacements

Combining named groups with replacement functions can offer useful text transformations:

```python
import re

# E.g. URL shortener with custom protocols
def expand_short_urls(text: str, url_mappings: dict[str, str]) -> str:
    """Expand shortened URLs with custom protocols and aliases."""

    url_pattern = r"""(?x)
        (?P<protocol>           # Protocol group
            https?:// |         # Standard HTTP(S)
            (?P<custom>         # Custom protocols
                gh:// |         # GitHub shorthand
                docs:// |       # Documentation links
                api://          # API endpoints
            )
        )?                      # Protocol is optional
        (?P<domain>             # Domain/alias
            [a-zA-Z0-9.-]+      # Domain characters
        )
        (?P<path>               # Path (optional)
            /[^\s]*             # Everything after domain
        )?
    """

    def url_replacer(match: re.Match[str]) -> str:
        """Replace shortened URLs with full versions."""
        protocol = match["protocol"] or ""
        custom = match["custom"]
        domain = match["domain"]
        path = match["path"] or ""

        # Handle custom protocols
        if custom == "gh://":
            return f"https://github.com/{domain}{path}"
        elif custom == "docs://":
            return f"https://docs.python.org/3/{domain}{path}"
        elif custom == "api://":
            return f"https://api.{domain}.com/v1{path}"

        # Expand domain aliases
        if domain in url_mappings:
            expanded = url_mappings[domain]
            return f"{protocol or 'https://'}{expanded}{path}"

        # Return original if no expansion needed
        return match.group(0)

    return re.sub(url_pattern, url_replacer, text)

# Usage
mappings = {
    "gh": "github.com",
    "so": "stackoverflow.com",
    "mdn": "developer.mozilla.org"
}

text = "Check gh://python/cpython/blob/main/README.rst and docs://library/re.html"
print(expand_short_urls(text, mappings))
# Output: Check https://github.com/python/cpython/blob/main/README.rst and https://docs.python.org/3/library/re.html
```

## Non-Capturing Groups with `(?:...)`

Use non-capturing groups when you need grouping but _not_ the captured value:

```python
# Parsing semantic version numbers with optional pre-release
version_pattern = r"""(?x)
    ^
    v?                          # Optional 'v' prefix
    (?P<major>\d+)              # Major version
    \.
    (?P<minor>\d+)              # Minor version
    \.
    (?P<patch>\d+)              # Patch version
    (?:                         # Non-capturing group for pre-release
        -                       # Hyphen separator
        (?P<prerelease>         # Pre-release identifier
            (?:alpha|beta|rc)   # Type (non-capturing)
            \.?                 # Optional dot
            \d+                 # Number
        )
    )?                          # Pre-release is optional
    $
"""

def parse_version(version_string: str) -> dict:
    match = re.match(version_pattern, version_string)
    if not match:
        raise ValueError(f"Invalid version: {version_string}")

    return {
        "major": int(match["major"]),
        "minor": int(match["minor"]),
        "patch": int(match["patch"]),
        "prerelease": match["prerelease"] or None
    }

# E.g.
print(parse_version("v2.1.0"))          # {'major': 2, 'minor': 1, 'patch': 0, 'prerelease': None}
print(parse_version("3.0.0-beta.2"))    # {'major': 3, 'minor': 0, 'patch': 0, 'prerelease': 'beta.2'}
```

## Accessing Named Groups

Match objects offer multiple ways to access named groups:

```python
# Using match["name"] or match.group("name")
pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
match = re.match(pattern, "2025-01-07")

# Dictionary-style access
year = match["year"]            # "2025"

# Multiple groups at once
year, month = match.group("year", "month")  # ("2025", "01")

# Get all groups as a dict
date_parts = match.groupdict()  # {'year': '2025', 'month': '01', 'day': '07'}
```

## Best Practices

1. **Use verbose mode** for any regex longer than 30 characters
2. **Name your groups** because  they're self-documenting
3. **Prefer non-capturing groups** when you don't need the match
4. **Test complex patterns** incrementally
5. **Comment intent**, not just  syntax

