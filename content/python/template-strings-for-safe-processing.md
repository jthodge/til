# Template Strings for Safe Processing

Python 3.14.x introduces template strings (t-strings).
T-strings are an f-strings generalization that returns processable `Template` objects (vs. immediate strings).
Returning `Template`s allows for safer and more flexible string handling.

## Basic Syntax

```python
from string.templatelib import Template

# f-string: immediate evaluation
name = "World"
greeting = f"Hello {name}!"  # Returns string

# t-string: deferred processing
template = t"Hello {name}!"  # Returns Template object
```

## Why t-strings Matter

Unlike f-strings, templates must be explicitly processed.
In addition to being more idiomatically pythonic...explicit processing can also
prevent dangerous misuse:

```python
# DANGEROUS: f-string with user input
user_input = "<script>alert('xss')</script>"
html = f"<div>{user_input}</div>"  # Immediate string with XSS

# SAFE: t-string requires processing
template = t"<div>{user_input}</div>"  # Template object
# Must call html_escape(template) or similar
```

## Template Structure

Templates provide access to raw components:

```python
name = "Alice"
age = 30
template = t"Hello {name}, you are {age} years old"

# Access components
print(template.strings)  # ("Hello ", ", you are ", " years old")
print(template.values)   # ("Alice", 30)

# Detailed interpolation info
interp = template.interpolations[0]
print(interp.expression)  # "name"
print(interp.value)       # "Alice"
```

## Processing Templates

```python
# E.g. simple escaper
def escape_html(template: Template) -> str:
    """Safely escape HTML in template values."""
    result = []
    for item in template:
        if isinstance(item, str):
            result.append(item)  # Raw strings pass through
        else:
            # Escape interpolated values
            escaped = str(item.value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            result.append(escaped)
    return ''.join(result)

# E.g. SQL query builder
def build_query(template: Template) -> tuple[str, list]:
    """Convert template to parameterized query."""
    sql_parts = []
    params = []

    for item in template:
        if isinstance(item, str):
            sql_parts.append(item)
        else:
            sql_parts.append('?')  # Parameterized placeholder
            params.append(item.value)

    return ''.join(sql_parts), params

# Usage
user_id = 123
email = "user@example.com"
template = t"SELECT * FROM users WHERE id = {user_id} AND email = {email}"
query, params = build_query(template)
# Result: ("SELECT * FROM users WHERE id = ? AND email = ?", [123, "user@example.com"])
```

## Advanced Processing

```python
# Log formatting with structured data
def format_log(template: Template) -> str:
    """Format template with enhanced logging info."""
    import datetime
    result = []

    for item in template:
        if isinstance(item, str):
            result.append(item)
        else:
            value = item.value
            # Add type information for debugging
            if hasattr(value, '__dict__'):
                formatted = f"{value} (type: {type(value).__name__})"
            else:
                formatted = str(value)
            result.append(formatted)

    timestamp = datetime.datetime.now().isoformat()
    return f"[{timestamp}] {''.join(result)}"

# Configuration file generator
def generate_config(template: Template) -> str:
    """Generate config file with validation."""
    result = []

    for item in template:
        if isinstance(item, str):
            result.append(item)
        else:
            value = item.value
            # Validate config values
            if isinstance(value, str) and ' ' in value:
                value = f'"{value}"'  # Quote strings with spaces
            elif isinstance(value, bool):
                value = str(value).lower()  # boolean formatting
            result.append(str(value))

    return ''.join(result)
```

## Direct Template Construction

```python
from string.templatelib import Template, Interpolation

# Programmatic template creation
template = Template(
    "User: ",
    Interpolation(value="john_doe", expression="username"),
    " has ",
    Interpolation(value=42, expression="post_count"),
    " posts"
)

# Equivalent to: t"User: {username} has {post_count} posts"
```

## Safety Benefits

```python
# Template cannot accidentally become string
template = t"Hello {name}!"
# str(template)  # Would not return useful value

# Must be processed explicitly
def secure_render(template: Template) -> str:
    # Custom processing ensures safety
    pass

# Forces deliberate handling
safe_output = secure_render(template)
```


