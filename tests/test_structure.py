"""Test basic package structure."""

import sys
from pathlib import Path


def test_til_package_imports() -> None:
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


def test_cli_entry_points_exist() -> None:
    """Test that CLI entry points are properly configured."""
    root = Path(__file__).parent.parent

    # Check that pyproject.toml exists and contains the entry points
    pyproject_path = root / "pyproject.toml"
    assert pyproject_path.exists()

    with open(pyproject_path) as f:
        content = f.read()
        assert "[project.scripts]" in content
        assert 'til = "til.cli:cli"' in content

    # Verify the module and function exist
    sys.path.insert(0, str(root))
    from til.cli import cli

    # Check it's callable
    assert callable(cli)
