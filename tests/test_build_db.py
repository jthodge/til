"""Test database building functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

from til.build_db import build_database
from til.config import TILConfig


class TestBuildDatabase:
    """Test the build_database function."""

    def _create_mock_log_config(self) -> Mock:
        """Create a properly configured mock log config."""
        from til.logging_config import LogFormat

        mock_log_config = Mock()
        mock_log_config.level = Mock()
        mock_log_config.level.value = "INFO"
        mock_log_config.format = LogFormat.TEXT
        mock_log_config.add_context = False
        mock_log_config.console_enabled = True
        mock_log_config.log_file = None
        mock_log_config.request_id = None
        return mock_log_config

    def test_build_database(self, temp_dir: Path) -> None:
        """Test that build_database creates a TILProcessor and calls build_database."""
        config = TILConfig(root_path=temp_dir)

        with patch("til.build_db.TILProcessor") as mock_processor:
            build_database(config)

            # Verify TILProcessor was instantiated with config
            mock_processor.assert_called_once_with(config)

            # Verify build_database was called on the processor
            mock_processor.return_value.build_database.assert_called_once()

    def test_main(self) -> None:
        """Test the main entry point."""
        with (
            patch("til.build_db.TILConfig") as mock_config,
            patch("til.build_db.build_database") as mock_build,
        ):
            mock_config.from_environment.return_value = Mock(
                log_config=self._create_mock_log_config()
            )

            # Import main and call it
            from til.build_db import main

            main()

            # Verify config was created from environment
            mock_config.from_environment.assert_called_once()

            # Verify build_database was called with the config
            mock_build.assert_called_once_with(
                mock_config.from_environment.return_value
            )
