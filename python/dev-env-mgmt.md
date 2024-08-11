# Python Development Environment Management (macOS)

Notes re: using `pyenv` and `pyenv-virtualenv` to manage Python development environments.

`pyenv`
Used to install and manage Python versions.
Allows us to upgrade default Python version without breaking projects that rely on the default.

`pyenv-virtualenv`
Used to create and manage virtual environments — most commonly for isolating project-level dependencies.

## Installation
```bash
brew update && brew install pyenv pyenv-virtualenv
```

## Shell Configuration
```bash
# pyenv
## Assign variable to pyenv location
export PYENV_ROOT="${HOME}/.pyenv"
## Pyenv config
if command -y pyenv > /dev/null; then
    eval "$(pyenv init --path)";
    eval "$(pyenv init -)";
    pyenv virtualenvwrapper_lazy;
fi
```

## Version Management

### Installation
```bash
# Install latest Python 3.11 version
pyenv install 3.11:latest

# Confirm installed version
pyenv latest 3.11

# Install latest 3.12 version
pyenv install 3.12:latest

# Confirm installed version
pyenv latest 3.12

# Set each version globally
pyenv global 3.11.$PATCH 3.12.$PATCH
```

### Upgrading
```bash
# Upgrade to latest version of Python 3.11 and 3.12
pyenv install --skip-existing 3.11:latest 3.12:latest
```

### Navigation
```bash
# List all versions available for installation
pyenv install --list

# List all versions installed
pyenv versions
```

TEST