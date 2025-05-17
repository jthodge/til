"""Test CLI interface."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import click.testing

# Import the module and cli separately to fix CI issues
from til.cli import cli


# Get the actual module for patching
cli_module = sys.modules["til.cli"]


class TestCLI:
    """Test the CLI interface."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "TIL - Today I Learned static site generator" in result.output
        assert "Commands:" in result.output
        assert "build" in result.output
        assert "update-readme" in result.output

    def test_build_command_help(self) -> None:
        """Test build command help."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["build", "--help"])

        assert result.exit_code == 0
        assert "Build TIL database from markdown files" in result.output
        assert "--github-token" in result.output
        assert "--repo" in result.output
        assert "--db" in result.output

    def test_update_readme_command_help(self) -> None:
        """Test update-readme command help."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["update-readme", "--help"])

        assert result.exit_code == 0
        assert "Update README with latest TIL entries" in result.output
        assert "--rewrite" in result.output
        assert "--db" in result.output
        assert "--output" in result.output

    @patch.object(cli_module, "TILProcessor")
    @patch.object(cli_module, "ConfigLoader")
    def test_build_command(
        self, mock_loader_class: Mock, mock_processor_class: Mock
    ) -> None:
        """Test build command execution."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_loader_class.load_config.return_value = mock_config

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(cli, ["build"])

        assert result.exit_code == 0
        assert "Database built successfully!" in result.output

        # Verify ConfigLoader was called with defaults
        mock_loader_class.load_config.assert_called_once_with(
            config_file=None,
            github_token=None,
            github_repo="jthodge/til",
            database_name="til.db",
        )

        # Verify processor was used
        mock_processor_class.assert_called_once_with(mock_config)
        mock_processor.build_database.assert_called_once()

    @patch.object(cli_module, "TILProcessor")
    @patch.object(cli_module, "ConfigLoader")
    def test_build_command_with_options(
        self, mock_loader_class: Mock, mock_processor_class: Mock
    ) -> None:
        """Test build command with custom options."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_loader_class.load_config.return_value = mock_config

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(
            cli,
            [
                "build",
                "--github-token",
                "token123",
                "--repo",
                "user/repo",
                "--db",
                "custom.db",
            ],
        )

        assert result.exit_code == 0

        # Verify ConfigLoader was called with custom options
        mock_loader_class.load_config.assert_called_once_with(
            config_file=None,
            github_token="token123",
            github_repo="user/repo",
            database_name="custom.db",
        )

    @patch.object(cli_module, "TILProcessor")
    @patch.object(cli_module, "ConfigLoader")
    def test_build_command_verbose(
        self, mock_loader_class: Mock, mock_processor_class: Mock
    ) -> None:
        """Test build command with verbose output."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_config.database_path = Path("/tmp/til.db")
        mock_config.github_repo = "user/repo"
        mock_loader_class.load_config.return_value = mock_config

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(cli, ["--verbose", "build"])

        assert result.exit_code == 0
        assert "Building database: /tmp/til.db" in result.output
        assert "Repository: user/repo" in result.output

    @patch.object(cli_module, "TILProcessor")
    @patch.object(cli_module, "ConfigLoader")
    def test_build_command_quiet(
        self, mock_loader_class: Mock, mock_processor_class: Mock
    ) -> None:
        """Test build command with quiet output."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_loader_class.load_config.return_value = mock_config

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(cli, ["--quiet", "build"])

        assert result.exit_code == 0
        assert "Database built successfully!" not in result.output

    @patch.object(cli_module, "TILProcessor")
    @patch.object(cli_module, "ConfigLoader")
    def test_build_command_error_handling(
        self, mock_loader_class: Mock, mock_processor_class: Mock
    ) -> None:
        """Test build command error handling."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_loader_class.load_config.return_value = mock_config

        mock_processor = Mock()
        mock_processor.build_database.side_effect = Exception("Test error")
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(cli, ["build"])

        assert result.exit_code == 1
        assert "Unexpected error: Test error" in result.output

    @patch.object(cli_module, "ReadmeGenerator")
    @patch.object(cli_module, "TILDatabase")
    @patch.object(cli_module, "ConfigLoader")
    def test_update_readme_command(
        self, mock_loader_class: Mock, mock_db_class: Mock, mock_generator_class: Mock
    ) -> None:
        """Test update-readme command execution."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        mock_config = Mock()
        mock_config.database_path = Mock(exists=Mock(return_value=True))
        mock_config.root_path = Path("/tmp")
        mock_loader_class.load_config.return_value = mock_config

        mock_db = Mock()
        mock_db.count.return_value = 5
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_index.return_value = ["# Index", "content"]
        mock_generator_class.return_value = mock_generator

        result = runner.invoke(cli, ["update-readme"])

        assert result.exit_code == 0
        assert "# Index" in result.output

    @patch.object(cli_module, "ReadmeGenerator")
    @patch.object(cli_module, "TILDatabase")
    @patch.object(cli_module, "ConfigLoader")
    def test_update_readme_with_rewrite(
        self, mock_loader_class: Mock, mock_db_class: Mock, mock_generator_class: Mock
    ) -> None:
        """Test update-readme command with --rewrite flag."""
        runner = click.testing.CliRunner()

        # Set up mock instances
        readme_path = Mock(exists=Mock(return_value=True))
        mock_config = Mock()
        mock_config.database_path = Mock(exists=Mock(return_value=True))
        mock_config.root_path = Mock(__truediv__=Mock(return_value=readme_path))
        mock_loader_class.load_config.return_value = mock_config

        mock_db = Mock()
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        result = runner.invoke(cli, ["update-readme", "--rewrite"])

        assert result.exit_code == 0
        assert "README updated successfully!" in result.output
        mock_generator.update_readme.assert_called_once()

    @patch.object(cli_module, "ReadmeGenerator")
    @patch.object(cli_module, "TILDatabase")
    @patch.object(cli_module, "ConfigLoader")
    def test_update_readme_with_output(
        self, mock_loader_class: Mock, mock_db_class: Mock, mock_generator_class: Mock
    ) -> None:
        """Test update-readme command with output file."""
        runner = click.testing.CliRunner()

        with runner.isolated_filesystem():
            # Set up mock instances
            mock_config = Mock()
            mock_config.database_path = Mock(exists=Mock(return_value=True))
            mock_loader_class.load_config.return_value = mock_config

            mock_db = Mock()
            mock_db_class.return_value = mock_db

            mock_generator = Mock()
            mock_generator.generate_index.return_value = ["# Index", "content"]
            mock_generator_class.return_value = mock_generator

            result = runner.invoke(cli, ["update-readme", "--output", "output.md"])

            assert result.exit_code == 0
            assert "Index written to output.md" in result.output
            assert Path("output.md").exists()
            assert Path("output.md").read_text() == "# Index\ncontent"

    @patch.object(cli_module, "ConfigLoader")
    def test_update_readme_no_database(self, mock_loader_class: Mock) -> None:
        """Test update-readme command when database doesn't exist."""
        runner = click.testing.CliRunner()

        # Set up mock instance
        mock_config = Mock()
        mock_config.database_path = Mock(exists=Mock(return_value=False))
        mock_loader_class.load_config.return_value = mock_config

        result = runner.invoke(cli, ["update-readme"])

        assert result.exit_code == 1
        assert "Database not found" in result.output
        assert "Run 'til build' to create the database first" in result.output
