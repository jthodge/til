# grep: List Matching Files with -l Flag

The `-l` flag shows only filenames containing matches, _not_ the matching lines themselves.

```bash
# Find which files contain "TODO"
grep -l "TODO" *.py

# Output:
# main.py
# utils.py
# tests.py
```

## Practical Examples

```bash
# Find files with specific imports
grep -l "import pandas" *.ipynb

# Locate configuration files with database settings
grep -l "DATABASE_URL" config/*

# Find which tests use a specific fixture
grep -l "@pytest.fixture" tests/*.py
```

Project analysis and refactoring:

```bash
# Find all files using deprecated function
grep -l "oldFunction" src/**/*.js

# Identify files needing updates
grep -l "version: 1.0" */package.json

# Find files with security issues
grep -l "password.*=.*['\"]" --include="*.py" -r .
```

Combine with other commands:

```bash
# Edit all files containing pattern
vim $(grep -l "FIXME" *.go)

# Count files with matches
grep -l "error" *.log | wc -l

# Copy files containing pattern
grep -l "CONFIDENTIAL" *.doc | xargs -I {} cp {} secure/
```

Inverse with `-L`:

```bash
# Files NOT containing copyright notice
grep -L "Copyright" *.java

# Find missing imports
grep -L "strict mode" *.js
```

