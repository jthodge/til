"""Test configuration loader."""

import tempfile
from pathlib import Path

import pytest

from til.config_loader import ConfigLoader
from til.exceptions import ConfigurationError


class TestConfigLoader:
    """Test configuration file loading."""

    def test_load_yaml_config(self) -> None:
        """Test loading configuration from YAML file."""
        # Skip test if PyYAML is not installed
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not available")

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.yaml"
            config_file.write_text(
                """
github-repo: test/repo
database-name: test.db
max-retries: 5
retry-delay: 30
"""
            )

            config = ConfigLoader.load_config(
                config_file=config_file,
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "test/repo"
            assert config.database_name == "test.db"
            assert config.max_retries == 5
            assert config.retry_delay == 30

    def test_load_toml_config(self) -> None:
        """Test loading configuration from TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.toml"
            config_file.write_text(
                """
[til]
github-repo = "test/repo"
database-name = "test.db"
max-retries = 5
retry-delay = 30
"""
            )

            config = ConfigLoader.load_config(
                config_file=config_file,
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "test/repo"
            assert config.database_name == "test.db"
            assert config.max_retries == 5
            assert config.retry_delay == 30

    def test_cli_overrides_file(self) -> None:
        """Test CLI arguments override file configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.yaml"
            config_file.write_text(
                """
github-repo: file/repo
database-name: file.db
"""
            )

            config = ConfigLoader.load_config(
                config_file=config_file,
                github_repo="cli/repo",
                database_name="cli.db",
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "cli/repo"
            assert config.database_name == "cli.db"

    def test_env_overrides_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variables override file configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.yaml"
            config_file.write_text(
                """
github-repo: file/repo
database-name: file.db
"""
            )

            monkeypatch.setenv("TIL_GITHUB_REPO", "env/repo")
            monkeypatch.setenv("TIL_DATABASE_NAME", "env.db")

            config = ConfigLoader.load_config(
                config_file=config_file,
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "env/repo"
            assert config.database_name == "env.db"

    def test_cli_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CLI arguments override environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("TIL_GITHUB_REPO", "env/repo")
            monkeypatch.setenv("TIL_DATABASE_NAME", "env.db")

            config = ConfigLoader.load_config(
                github_repo="cli/repo",
                database_name="cli.db",
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "cli/repo"
            assert config.database_name == "cli.db"

    def test_invalid_config_file(self) -> None:
        """Test error on invalid configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "nonexistent.yaml"

            with pytest.raises(
                ConfigurationError, match="Configuration file not found"
            ):
                ConfigLoader.load_config(config_file=config_file)

    def test_unsupported_format(self) -> None:
        """Test error on unsupported configuration file format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.json"
            config_file.write_text("{}")

            with pytest.raises(
                ConfigurationError, match="Unsupported configuration file format"
            ):
                ConfigLoader.load_config(config_file=config_file)

    def test_default_file_discovery(self) -> None:
        """Test automatic discovery of configuration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                # Create a config file
                config_file = Path(tmpdir) / "til.yaml"
                config_file.write_text(
                    """
github-repo: discovered/repo
database-name: discovered.db
"""
                )

                # Load without specifying file
                config = ConfigLoader.load_config(root_path=Path(tmpdir))

                assert config.github_repo == "discovered/repo"
                assert config.database_name == "discovered.db"

            finally:
                os.chdir(old_cwd)

    def test_path_normalization(self) -> None:
        """Test path string normalization to Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.yaml"
            config_file.write_text(
                f"""
github-repo: test/repo
database-name: test.db
root-path: {tmpdir}
"""
            )

            config = ConfigLoader.load_config(config_file=config_file)

            assert isinstance(config.root_path, Path)
            assert config.root_path == Path(tmpdir)

    def test_kebab_to_snake_case(self) -> None:
        """Test kebab-case keys are converted to snake_case."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "til.yaml"
            config_file.write_text(
                """
github-repo: test/repo
github-token: test-token
database-name: test.db
max-retries: 3
retry-delay: 60
"""
            )

            config = ConfigLoader.load_config(
                config_file=config_file,
                root_path=Path(tmpdir),
            )

            assert config.github_repo == "test/repo"
            assert config.github_token == "test-token"
            assert config.database_name == "test.db"
            assert config.max_retries == 3
            assert config.retry_delay == 60
