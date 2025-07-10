# Reinstall Python Versions with uv

The `--reinstall` flag is powerful but potentially destructive.
For production systems, prefer installing new versions alongside existing ones and explicitly managing which version each project uses.
`uv python install --reinstall`  upgrades an existing Python version to the latest patch release.
But. It can break virtual envs and tools that depend on specific versions.

## Upgrading Python Versions

To upgrade an existing Python installation:

```bash
# Upgrade to latest 3.13.x
uv python install --reinstall 3.13

# Verify the upgrade
uv run --python 3.13 python -c 'import sys; print(sys.version)'
# 3.13.1 (main, Jan 7 2025, 15:32:19) [Clang 16.0.0]
```

## Safer Approach: Install Alongside

Instead of reinstalling, add new versions alongside existing ones:

```bash
# Install specific patch version
uv python install 3.13.1

# List all installed Python versions
uv python list

# You'll see both versions available:
# cpython-3.13.0-macos-aarch64    /Users/you/.local/share/uv/python/cpython-3.13.0
# cpython-3.13.1-macos-aarch64    /Users/you/.local/share/uv/python/cpython-3.13.1
```

## Managing Multiple Versions

```bash
# project-specific Python version
cd my-project
uv python pin 3.13.1
# Creates .python-version file

# testing across versions
# Run tests with different Python versions
for version in 3.11 3.12 3.13; do
    echo "Testing with Python $version"
    uv run --python $version pytest tests/
done

# Create venvs with specific versions
uv venv --python 3.12.7 venv-stable
uv venv --python 3.13.1 venv-latest
```

## Reinstall Use Cases

When reinstalling makes sense:

```bash
# Fix corrupted Python installation
uv python install --reinstall 3.12

# Force reinstall after system changes
uv python install --reinstall --force 3.13

# Reinstall with different compilation options (if supported)
UV_PYTHON_COMPILE_ARGS="--enable-optimizations" uv python install --reinstall 3.13
```

## Virtual Env Recovery

After reinstalling, rebuild affected envs:

```bash
# Save current dependencies
uv pip freeze > requirements.txt

# Remove old venv
rm -rf .venv

# Create new venv with updated Python
uv venv --python 3.13

# Restore dependencies
uv pip install -r requirements.txt
```

## Tool Management

Global tools may break after reinstall:

```bash
# List installed tools
uv tool list

# Reinstall a tool after Python upgrade
uv tool install --force ruff

# Or reinstall all tools
uv tool list | grep -v "^$" | while read tool _; do
    uv tool install --force "$tool"
done
```

## Version Pinning Strategies

```bash
# Pin to major.minor (gets latest patch)
uv python pin 3.13

# Pin to exact version
uv python pin 3.13.1

# Use in CI/CD pipelines
# .github/workflows/test.yml
- name: Install Python
  run: |
    uv python install 3.13.1
    uv venv --python 3.13.1
```

## Checking Available Versions

```bash
# List installed versions
uv python list

# Show available versions (not built-in to uv yet)
# Check the uv Python versions documentation

# Remove old versions
uv python uninstall 3.13.0
```
