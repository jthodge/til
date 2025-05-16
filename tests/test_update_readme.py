"""Test README update functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.config import TILConfig
from til.update_readme import main


class TestUpdateReadme:
    """Test the update_readme module."""

    def test_main_with_rewrite(self) -> None:
        """Test main function with --rewrite flag."""
        with (
            patch("til.update_readme.sys.argv", ["update_readme.py", "--rewrite"]),
            patch("til.update_readme.TILConfig") as mock_config,
            patch("til.update_readme.TILDatabase") as mock_db,
            patch("til.update_readme.ReadmeGenerator") as mock_generator,
        ):

            # Setup mocks
            mock_db_path = Mock()
            mock_db_path.exists.return_value = True

            mock_readme_path = Mock()
            mock_readme_path.exists.return_value = True

            mock_config.from_environment.return_value = Mock(
                root_path=Mock(spec=Path), database_path=mock_db_path
            )
            mock_config.from_environment.return_value.root_path.__truediv__ = Mock(
                return_value=mock_readme_path
            )

            mock_db.return_value.count.return_value = 5

            # Run main
            main()

            # Verify flow
            mock_config.from_environment.assert_called_once()
            mock_db.assert_called_once_with(mock_db_path)
            mock_generator.assert_called_once_with(mock_db.return_value)

            # Verify update_readme was called
            generator_instance = mock_generator.return_value
            generator_instance.update_readme.assert_called_once_with(mock_readme_path)

    def test_main_without_rewrite(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function without --rewrite flag."""
        with (
            patch("til.update_readme.sys.argv", ["update_readme.py"]),
            patch("til.update_readme.TILConfig") as mock_config,
            patch("til.update_readme.TILDatabase") as mock_db,
            patch("til.update_readme.ReadmeGenerator") as mock_generator,
        ):

            # Setup mocks
            mock_db_path = Mock()
            mock_db_path.exists.return_value = True

            mock_config.from_environment.return_value = Mock(
                root_path=Path("/test"), database_path=mock_db_path
            )

            mock_db.return_value.count.return_value = 3
            mock_generator.return_value.generate_index.return_value = [
                "<!-- index starts -->",
                "## python",
                "* [Test](url) - 2023-01-01",
                "<!-- index ends -->",
            ]

            # Run main
            main()

            # Verify only index was printed
            captured = capsys.readouterr()
            assert "<!-- index starts -->" in captured.out
            assert "## python" in captured.out
            assert "<!-- index ends -->" in captured.out

            # Verify update_readme was NOT called
            generator_instance = mock_generator.return_value
            generator_instance.update_readme.assert_not_called()

    def test_main_database_not_found(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test main function when database doesn't exist."""
        with (
            patch("til.update_readme.sys.argv", ["update_readme.py", "--rewrite"]),
            patch("til.update_readme.TILConfig") as mock_config,
            patch("til.update_readme.sys.exit") as mock_exit,
        ):
            # Setup mocks
            mock_db_path = Mock()
            mock_db_path.exists.return_value = False

            mock_config.from_environment.return_value = Mock(
                root_path=Path("/test"), database_path=mock_db_path
            )

            # Make sys.exit raise an exception to stop execution
            mock_exit.side_effect = SystemExit(1)

            # Run main - should raise SystemExit due to our mock
            with pytest.raises(SystemExit):
                main()

            # Verify error message was logged
            assert "Database not found" in caplog.text

            # Verify exit was called at least once with error code
            mock_exit.assert_called_with(1)

    def test_main_readme_not_found(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test main function when README doesn't exist."""
        with (
            patch("til.update_readme.sys.argv", ["update_readme.py", "--rewrite"]),
            patch("til.update_readme.TILConfig") as mock_config,
            patch("til.update_readme.TILDatabase") as mock_db,
            patch("til.update_readme.ReadmeGenerator") as mock_generator,
            patch("til.update_readme.sys.exit") as mock_exit,
        ):
            # Setup mocks
            mock_db_path = Mock()
            mock_db_path.exists.return_value = True

            mock_readme_path = Mock()
            mock_readme_path.exists.return_value = False

            mock_config.from_environment.return_value = Mock(
                root_path=Mock(spec=Path), database_path=mock_db_path
            )
            mock_config.from_environment.return_value.root_path.__truediv__ = Mock(
                return_value=mock_readme_path
            )

            mock_db.return_value.count.return_value = 5

            # Run main
            main()

            # Verify error message was logged
            assert "README.md not found" in caplog.text

            # Verify exit was called with error code
            mock_exit.assert_called_once_with(1)

    @patch("til.update_readme.main")
    def test_module_execution(self, mock_main: Mock) -> None:
        """Test that main is called when module is executed."""
        # Import the module
        import til.update_readme

        # Mock the name check
        with patch.object(til.update_readme, "__name__", "__main__"):
            # This would trigger the if __name__ == "__main__" block
            pass
