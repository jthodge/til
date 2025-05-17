"""Test configuration module."""

from pathlib import Path

import pytest

from til.config import TILConfig


class TestTILConfig:
    """Test TILConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = TILConfig()

        assert config.github_repo == "jthodge/til"
        assert config.database_name == "til.db"
        assert config.max_retries == 3
        assert config.retry_delay == 60
        assert config.github_token is None
        assert config.markdown_api_url == "https://api.github.com/markdown"

    def test_config_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test configuration from environment variables."""
        # Set test environment variables
        monkeypatch.setenv("MARKDOWN_GITHUB_TOKEN", "test_token")
        monkeypatch.setenv("TIL_GITHUB_REPO", "test/repo")

        config = TILConfig.from_environment()

        assert config.github_token == "test_token"
        assert config.github_repo == "test/repo"

    def test_derived_properties(self) -> None:
        """Test derived configuration properties."""
        config = TILConfig()

        assert isinstance(config.database_path, Path)
        assert config.database_path.name == "til.db"
        assert config.github_url_base == "https://github.com/jthodge/til"

    def test_custom_config_values(self) -> None:
        """Test creating config with custom values."""
        config = TILConfig(
            github_token="custom_token",
            github_repo="custom/repo",
            database_name="custom.db",
            max_retries=5,
            retry_delay=30,
        )

        assert config.github_token == "custom_token"
        assert config.github_repo == "custom/repo"
        assert config.database_name == "custom.db"
        assert config.max_retries == 5
        assert config.retry_delay == 30
        assert config.database_path.name == "custom.db"
        assert config.github_url_base == "https://github.com/custom/repo"

    def test_root_path_is_absolute(self) -> None:
        """Test that root_path is always absolute."""
        config = TILConfig()
        assert config.root_path.is_absolute()

    def test_github_url_base_format(self) -> None:
        """Test GitHub URL base formatting."""
        config = TILConfig(github_repo="user/repo")
        assert config.github_url_base == "https://github.com/user/repo"

        # Test with different repo format
        config = TILConfig(github_repo="org/project-name")
        assert config.github_url_base == "https://github.com/org/project-name"
