"""Test configuration validation."""

import tempfile
from pathlib import Path

import pytest

from til.config import TILConfig
from til.exceptions import ConfigurationError


class TestConfigValidation:
    """Test configuration validation logic."""

    def test_valid_configuration(self) -> None:
        """Test valid configuration passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TILConfig(
                github_token="test_token",
                github_repo="owner/repo",
                database_name="test.db",
                max_retries=3,
                retry_delay=10,
                root_path=Path(tmpdir),
            )
            assert config.github_token == "test_token"
            assert config.github_repo == "owner/repo"

    def test_invalid_github_repo_format(self) -> None:
        """Test invalid GitHub repository format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="Invalid GitHub repository format"
            ):
                TILConfig(
                    github_repo="invalid_format",
                    root_path=Path(tmpdir),
                )

    def test_empty_github_repo(self) -> None:
        """Test empty GitHub repository raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="Invalid GitHub repository format"
            ):
                TILConfig(
                    github_repo="",
                    root_path=Path(tmpdir),
                )

    def test_github_repo_with_extra_slashes(self) -> None:
        """Test GitHub repository with extra slashes raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="Invalid GitHub repository format"
            ):
                TILConfig(
                    github_repo="owner/repo/extra",
                    root_path=Path(tmpdir),
                )

    def test_invalid_database_name(self) -> None:
        """Test invalid database name raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="Database name must end with '.db'"
            ):
                TILConfig(
                    database_name="invalid",
                    root_path=Path(tmpdir),
                )

    def test_empty_database_name(self) -> None:
        """Test empty database name raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="Database name cannot be empty"
            ):
                TILConfig(
                    database_name="",
                    root_path=Path(tmpdir),
                )

    def test_negative_max_retries(self) -> None:
        """Test negative max_retries raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="max_retries must be non-negative"
            ):
                TILConfig(
                    max_retries=-1,
                    root_path=Path(tmpdir),
                )

    def test_zero_retry_delay(self) -> None:
        """Test zero retry_delay raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="retry_delay must be positive"
            ):
                TILConfig(
                    retry_delay=0,
                    root_path=Path(tmpdir),
                )

    def test_negative_retry_delay(self) -> None:
        """Test negative retry_delay raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ConfigurationError, match="retry_delay must be positive"
            ):
                TILConfig(
                    retry_delay=-10,
                    root_path=Path(tmpdir),
                )

    def test_non_existent_root_path(self) -> None:
        """Test non-existent root path raises error."""
        with pytest.raises(ConfigurationError, match="Root path does not exist"):
            TILConfig(
                root_path=Path("/non/existent/path"),
            )

    def test_root_path_is_file(self) -> None:
        """Test root path that is a file raises error."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(
                ConfigurationError, match="Root path is not a directory"
            ):
                TILConfig(
                    root_path=Path(tmpfile.name),
                )

    def test_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating config from environment variables."""
        monkeypatch.setenv("MARKDOWN_GITHUB_TOKEN", "env_token")
        monkeypatch.setenv("TIL_GITHUB_REPO", "env_owner/env_repo")

        config = TILConfig.from_environment()
        assert config.github_token == "env_token"
        assert config.github_repo == "env_owner/env_repo"

    def test_from_environment_defaults(self) -> None:
        """Test creating config from environment with defaults."""
        config = TILConfig.from_environment()
        assert config.github_token is None
        assert config.github_repo == "jthodge/til"

    def test_database_path_property(self) -> None:
        """Test database_path property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TILConfig(
                database_name="custom.db",
                root_path=Path(tmpdir),
            )
            expected_path = Path(tmpdir) / "custom.db"
            assert config.database_path == expected_path

    def test_github_url_base_property(self) -> None:
        """Test github_url_base property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TILConfig(
                github_repo="owner/repo",
                root_path=Path(tmpdir),
            )
            assert config.github_url_base == "https://github.com/owner/repo"
