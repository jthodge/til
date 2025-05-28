# Python's Triple-Quoted Strings Preserve Indentation

Triple-quoted strings in Python capture indentation as part of the string content, creating unexpected differences when code moves between indentation levels. This behavior catches many developers off guard when refactoring code into functions or classes.

```python
# At module level
poem = """\
Roses are red
Violets are blue
Python is great
And so are you"""

# Inside a function
def get_poem():
    poem = """\
    Roses are red
    Violets are blue
    Python is great
    And so are you"""
    return poem

# These strings are different!
module_poem = poem
function_poem = get_poem()
print(module_poem == function_poem)  # False
print(repr(function_poem[0:4]))     # '    ' (4 spaces)
```

The backslash after the opening quotes prevents a leading newline, but the indentation required by Python's syntax becomes part of the string data.

## Solution 1: Using `textwrap.dedent()`

The standard library provides `textwrap.dedent()` specifically for this problem:

```python
import textwrap

def create_config():
    config = """\
    [database]
    host = localhost
    port = 5432

    [cache]
    enabled = true
    ttl = 3600
    """
    return textwrap.dedent(config)

# Result has no leading spaces
print(create_config())
# [database]
# host = localhost
# port = 5432

# [cache]
# enabled = true
# ttl = 3600
```

## Solution 2: Regular Expressions with Multiline Flag

Regular expressions offer more control over which whitespace to remove:

```python
import re

def generate_script():
    script = """\
    #!/bin/bash
    echo "Starting deployment"

    if [ -d "/app" ]; then
        cd /app
        git pull
    fi
    """
    # Remove leading whitespace from each line
    return re.sub("^\s+", "", script, flags=re.MULTILINE)

# Alternative using re.M shorthand
def generate_dockerfile():
    dockerfile = """\
    FROM python:3.11
    WORKDIR /app

    COPY requirements.txt .
    RUN pip install -r requirements.txt

    COPY . .
    CMD ["python", "app.py"]
    """
    return re.sub("^\s+", "", dockerfile, flags=re.M)
```

Note that the flags parameter must be specified by name - using positional arguments will misinterpret the flag as a substitution count.

## Solution 3: Inline Regular Expression Modifiers

Embedding the multiline modifier directly in the regex pattern makes the behavior more portable across languages:

```python
import re

def create_yaml_config():
    yaml = """\
    server:
      host: 0.0.0.0
      port: 8080

    database:
      connection_pool:
        min_size: 5
        max_size: 20
    """
    # (?m) modifier makes ^ match line starts
    return re.sub("(?m)^\s+", "", yaml)

# Works with any indentation level
class ConfigGenerator:
    def generate(self):
        template = """\
        # Auto-generated configuration
        version: 1.0

        features:
          - authentication
          - caching
          - monitoring
        """
        return re.sub("(?m)^\s+", "", template)
```

The `(?m)` modifier at the start of the pattern enables multiline mode for the rest of the regex, making `^` match the beginning of each line rather than just the string start. This approach works identically in Python, Perl, and many other regex implementations.

## Preserving Selective Indentation

Sometimes you want to remove only the common leading whitespace while preserving relative indentation:

```python
import textwrap

def generate_python_code():
    code = """\
    def calculate_total(items):
        total = 0
        for item in items:
            if item.active:
                total += item.price
        return total
    """
    # Preserves the internal indentation structure
    return textwrap.dedent(code)

print(generate_python_code())
# def calculate_total(items):
#     total = 0
#     for item in items:
#         if item.active:
#             total += item.price
#     return total
```

Each solution has its place: `textwrap.dedent()` for simplicity, regex with flags for more control, and inline modifiers for portability across regex engines.
