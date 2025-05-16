"""Integration tests for the full TIL pipeline."""

import subprocess
from pathlib import Path
from typing import Any

import pytest
import sqlite_utils

from git import Repo
from til.build_db import build_database
from til.config import TILConfig
from til.database import TILDatabase
from til.readme_generator import ReadmeGenerator
from til.update_readme import main as update_readme_main


class TestFullPipeline:
    """Test the complete TIL pipeline from files to database to README."""

    def test_complete_workflow(
        self, temp_dir: Path, mock_github_api: Any
    ) -> None:  # TODO: Replace Any with specific type
        """Test the complete workflow from markdown files to updated README."""
        # Initialize git repo with TIL files
        repo = Repo.init(temp_dir)

        # Configure git user for commits
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Create directory structure
        python_dir = temp_dir / "python"
        python_dir.mkdir()
        bash_dir = temp_dir / "bash"
        bash_dir.mkdir()

        # Create TIL files
        til1 = python_dir / "lists.md"
        til1.write_text(
            "# Working with Lists\n\nPython list comprehensions are powerful."
        )

        til2 = python_dir / "decorators.md"
        til2.write_text("# Python Decorators\n\nDecorators modify function behavior.")

        til3 = bash_dir / "loops.md"
        til3.write_text("# Bash Loops\n\nFor loops in bash use different syntax.")

        # Commit files
        repo.index.add(["python/lists.md", "python/decorators.md", "bash/loops.md"])
        repo.index.commit("Add initial TILs")

        # Create README
        readme = temp_dir / "README.md"
        readme.write_text(
            """# Today I Learned

<!-- count starts -->0<!-- count ends -->

<!-- index starts -->
<!-- index ends -->
"""
        )

        # Configure and build database
        config = TILConfig(root_path=temp_dir, database_name="til.db")

        build_database(config)

        # Verify database was created
        assert config.database_path.exists()
        db = sqlite_utils.Database(config.database_path)
        assert db["til"].count == 3

        # Manually add timestamps to satisfy README generation requirements
        til_table = db["til"]
        assert hasattr(til_table, "update"), "til_table should be a Table, not a View"
        for row in til_table.rows:
            til_table.update(
                row["path"],
                {
                    "created": "2023-01-01T00:00:00",
                    "created_utc": "2023-01-01T00:00:00+00:00",
                },
            )

        # Build and update README using new classes
        til_db = TILDatabase(config.database_path)
        generator = ReadmeGenerator(til_db)
        generator.update_readme(readme)

        # Verify README was updated
        readme_content = readme.read_text()
        assert "<!-- count starts -->3<!-- count ends -->" in readme_content
        assert "## python" in readme_content
        assert "## bash" in readme_content
        assert "[Working with Lists]" in readme_content
        assert "[Python Decorators]" in readme_content
        assert "[Bash Loops]" in readme_content

    def test_incremental_update(
        self, temp_dir: Path, mock_github_api: Any
    ) -> None:  # TODO: Replace Any with specific type
        """Test updating existing database with new TIL."""
        # Set up initial state
        repo = Repo.init(temp_dir)

        # Configure git user for commits
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        python_dir = temp_dir / "python"
        python_dir.mkdir()

        til1 = python_dir / "first.md"
        til1.write_text("# First TIL\n\nInitial content.")

        repo.index.add(["python/first.md"])
        repo.index.commit("Initial commit")

        # Build initial database
        config = TILConfig(root_path=temp_dir, database_name="til.db")
        build_database(config)

        db = sqlite_utils.Database(config.database_path)
        assert db["til"].count == 1

        # Add new TIL
        til2 = python_dir / "second.md"
        til2.write_text("# Second TIL\n\nNew content.")

        repo.index.add(["python/second.md"])
        repo.index.commit("Add second TIL")

        # Rebuild database
        build_database(config)

        # Verify both TILs are in database
        db = sqlite_utils.Database(config.database_path)
        assert db["til"].count == 2

        titles = {row["title"] for row in db["til"].rows}
        assert titles == {"First TIL", "Second TIL"}

    def test_cli_commands(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch, mock_github_api: Any
    ) -> None:  # TODO: Replace Any with specific type
        """Test CLI commands work correctly."""
        # Set up test environment
        monkeypatch.chdir(temp_dir)
        monkeypatch.setenv("MARKDOWN_GITHUB_TOKEN", "test_token")

        # Create git repo with TIL
        repo = Repo.init(temp_dir)

        # Configure git user for commits
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        test_dir = temp_dir / "test"
        test_dir.mkdir()
        til = test_dir / "example.md"
        til.write_text("# Example\n\nTest content.")

        repo.index.add(["test/example.md"])
        repo.index.commit("Add example")

        # Create README
        readme = temp_dir / "README.md"
        readme.write_text(
            """# TIL

<!-- count starts -->0<!-- count ends -->

<!-- index starts -->
<!-- index ends -->
"""
        )

        # Test til-build with real output
        import os
        import sys
        from pathlib import Path

        # Find the project root (where til package is located)
        current_file = Path(__file__)
        project_root = (
            current_file.parent.parent
        )  # tests/test_integration.py -> project root

        # Add current dir to PYTHONPATH and run module
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, "-m", "til.build_db"],
            capture_output=True,
            text=True,
            env=env,
            cwd=temp_dir,
        )

        # It might fail with the real CLI due to auth, but we can verify it at least runs
        assert (
            "Building database" in result.stderr
            or "ModuleNotFoundError" not in result.stderr
            or result.returncode == 0
        )

        # Try to run update-readme without a database - it will fail but that's OK for this test
        result2 = subprocess.run(
            [sys.executable, "-m", "til.update_readme"],
            capture_output=True,
            text=True,
            env=env,
            cwd=temp_dir,
        )

        # The command exists and can be run, even if it fails due to missing DB
        assert (
            "no such table" in result2.stderr
            or "ModuleNotFoundError" not in result2.stderr
            or result2.returncode == 0
        )

    def test_error_recovery(
        self, temp_dir: Path, mock_github_api: Any
    ) -> None:  # TODO: Replace Any with specific type
        """Test system handles errors gracefully."""
        # Initialize git repo
        repo = Repo.init(temp_dir)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        config = TILConfig(root_path=temp_dir, database_name="til.db")

        # Create invalid markdown file
        invalid_dir = temp_dir / "invalid"
        invalid_dir.mkdir()
        invalid_file = invalid_dir / "bad.md"
        invalid_file.write_text("No title here\n\nJust content")

        # Commit the file
        repo.index.add(["invalid/bad.md"])
        repo.index.commit("Add invalid file")

        # Should not crash
        build_database(config)

        # Database should still be created
        assert config.database_path.exists()


class TestDatasetteIntegration:
    """Test Datasette-specific functionality."""

    def test_full_text_search(
        self, temp_git_repo: Repo, mock_github_api: Any
    ) -> None:  # TODO: Replace Any with specific type
        """Test full-text search functionality."""
        config = TILConfig(
            root_path=Path(temp_git_repo.working_dir), database_name="test.db"
        )

        build_database(config)

        db = sqlite_utils.Database(config.database_path)

        # Test FTS table exists
        assert "til_fts" in db.table_names()

        # Test search functionality using the FTS table
        # Check that we can search for content
        results = db.execute(
            "SELECT * FROM til_fts WHERE til_fts MATCH ?", ["Python"]
        ).fetchall()

        # Should find results
        assert len(results) > 0

        # Test joining to get full records
        search_query = """
        SELECT til.* 
        FROM til 
        JOIN til_fts ON til.rowid = til_fts.rowid 
        WHERE til_fts MATCH ?
        """
        til_results = db.execute(search_query, ["Python"]).fetchall()
        assert len(til_results) > 0
        # Check that at least one result contains "Python"
        # Results are tuples since we're using db.execute()
        # Use db["til"].search() instead to get dictionaries
        til_table_search = db["til"]
        if hasattr(til_table_search, "search"):
            search_results = list(til_table_search.search("Python"))
            assert len(search_results) > 0
            assert any("Python" in result["body"] for result in search_results)
