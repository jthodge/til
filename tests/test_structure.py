"""Test basic package structure."""

import sys
from pathlib import Path


def test_til_package_imports():
    """Test that the til package can be imported."""
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Test basic imports
    import til

    assert til.__version__ == "0.1.0"

    # Test config module imports
    from til.config import TILConfig

    config = TILConfig()
    assert config.database_name == "til.db"


def test_wrapper_scripts_exist():
    """Test that wrapper scripts exist."""
    root = Path(__file__).parent.parent

    assert (root / "build_db.py").exists()
    assert (root / "update_readme.py").exists()

    # Check they're executable scripts
    with open(root / "build_db.py") as f:
        content = f.read()
        assert "#!/usr/bin/env python3" in content
        assert "from til.build_db import main" in content
