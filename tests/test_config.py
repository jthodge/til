"""Test configuration module."""

import os
from pathlib import Path

from til.config import TILConfig


def test_default_config():
    """Test default configuration values."""
    config = TILConfig()

    assert config.github_repo == "jthodge/til"
    assert config.database_name == "til.db"
    assert config.max_retries == 3
    assert config.retry_delay == 60
    assert config.github_token is None


def test_config_from_environment():
    """Test configuration from environment variables."""
    # Set test environment variables
    os.environ["MARKDOWN_GITHUB_TOKEN"] = "test_token"
    os.environ["TIL_GITHUB_REPO"] = "test/repo"

    config = TILConfig.from_environment()

    assert config.github_token == "test_token"
    assert config.github_repo == "test/repo"

    # Clean up environment
    del os.environ["MARKDOWN_GITHUB_TOKEN"]
    del os.environ["TIL_GITHUB_REPO"]


def test_derived_properties():
    """Test derived configuration properties."""
    config = TILConfig()

    assert isinstance(config.database_path, Path)
    assert config.database_path.name == "til.db"
    assert config.github_url_base == "https://github.com/jthodge/til"
