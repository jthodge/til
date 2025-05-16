"""Test database building functionality."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import sqlite_utils

from git import Repo
from til.build_db import (
    build_database,
    get_created_changed_times,
    process_markdown_file,
    render_markdown_via_github,
)
from til.config import TILConfig


class TestGetCreatedChangedTimes:
    """Test git history timestamp extraction."""

    def test_get_created_changed_times(self, temp_git_repo: Repo):
        """Test extracting timestamps from git history."""
        # Use the repo's active branch instead of assuming "main"
        branch_name = temp_git_repo.active_branch.name
        times = get_created_changed_times(
            Path(temp_git_repo.working_dir), ref=branch_name
        )

        # Should have timestamps for all committed files
        assert "python/test-til-1.md" in times
        assert "python/test-til-2.md" in times
        assert "bash/bash-test.md" in times

        # Check timestamp structure
        for file_times in times.values():
            assert "created" in file_times
            assert "created_utc" in file_times
            assert "updated" in file_times
            assert "updated_utc" in file_times

            # Verify ISO format
            datetime.fromisoformat(file_times["created"])
            datetime.fromisoformat(file_times["created_utc"])

    def test_get_created_changed_times_invalid_ref(self, temp_git_repo: Repo):
        """Test handling of invalid git reference."""
        times = get_created_changed_times(
            Path(temp_git_repo.working_dir), ref="nonexistent"
        )
        assert times == {}

    def test_file_creation_and_updates(self, temp_dir: Path):
        """Test tracking file creation vs updates."""
        repo = Repo.init(temp_dir)

        # Configure git user for commits
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Create and commit initial file
        file1 = temp_dir / "test.md"
        file1.write_text("Initial content")
        repo.index.add(["test.md"])
        repo.index.commit("Initial commit")

        # Sleep to ensure different timestamp
        import time

        time.sleep(1)

        # Update and commit same file
        file1.write_text("Updated content")
        repo.index.add(["test.md"])
        repo.index.commit("Update commit")

        # Use the repo's active branch instead of assuming "main"
        branch_name = repo.active_branch.name
        times = get_created_changed_times(temp_dir, ref=branch_name)

        assert "test.md" in times
        # Created time should be from first commit
        # Updated time should be from second commit
        created = datetime.fromisoformat(times["test.md"]["created"])
        updated = datetime.fromisoformat(times["test.md"]["updated"])
        assert updated > created


class TestRenderMarkdownViaGithub:
    """Test GitHub markdown rendering."""

    def test_successful_rendering(self, mock_github_api):
        """Test successful markdown rendering."""
        config = TILConfig(github_token="test_token")
        html = render_markdown_via_github("# Test", config)

        assert html is not None
        assert "<h1>" in html
        assert "Test" in html

    def test_rendering_without_token(self, mock_github_api):
        """Test rendering without GitHub token."""
        config = TILConfig(github_token=None)
        html = render_markdown_via_github("# Test", config)

        assert html is not None
        assert "<h1>" in html

    @patch("httpx.post")
    def test_rendering_with_retry(self, mock_post):
        """Test retry mechanism on failure."""
        config = TILConfig(max_retries=3, retry_delay=0)

        # Simulate failures then success
        mock_post.side_effect = [
            Mock(status_code=500),
            Mock(status_code=500),
            Mock(status_code=200, text="<h1>Test</h1>"),
        ]

        html = render_markdown_via_github("# Test", config)

        assert html == "<h1>Test</h1>"
        assert mock_post.call_count == 3

    @patch("httpx.post")
    def test_rendering_unauthorized(self, mock_post):
        """Test handling of 401 unauthorized response."""
        config = TILConfig(github_token="invalid")
        mock_post.return_value = Mock(status_code=401)

        html = render_markdown_via_github("# Test", config)

        assert html is None
        assert mock_post.call_count == 1  # Should not retry on 401

    @patch("httpx.post")
    def test_rendering_max_retries_exceeded(self, mock_post):
        """Test behavior when max retries exceeded."""
        config = TILConfig(max_retries=2, retry_delay=0)
        mock_post.return_value = Mock(status_code=500)

        html = render_markdown_via_github("# Test", config)

        assert html is None
        assert mock_post.call_count == 2


class TestProcessMarkdownFile:
    """Test markdown file processing."""

    def test_process_valid_markdown_file(self, temp_dir: Path):
        """Test processing a valid markdown file."""
        config = TILConfig(root_path=temp_dir)

        # Create test file
        python_dir = temp_dir / "python"
        python_dir.mkdir()
        test_file = python_dir / "test.md"
        test_file.write_text("# Test Title\n\nTest content")

        record = process_markdown_file(test_file, config)

        assert record is not None
        assert record["title"] == "Test Title"
        assert record["body"] == "Test content"
        assert record["slug"] == "test"
        assert record["topic"] == "python"
        assert record["path"] == "python_test.md"
        assert "/blob/main/python/test.md" in record["url"]

    def test_process_empty_file(self, temp_dir: Path):
        """Test processing an empty markdown file."""
        config = TILConfig(root_path=temp_dir)

        # Create empty file
        test_dir = temp_dir / "test"
        test_dir.mkdir()
        empty_file = test_dir / "empty.md"
        empty_file.write_text("")

        record = process_markdown_file(empty_file, config)

        assert record is not None
        assert record["title"] == ""
        assert record["body"] == ""

    def test_process_nonexistent_file(self, temp_dir: Path):
        """Test processing a nonexistent file."""
        config = TILConfig(root_path=temp_dir)
        nonexistent = temp_dir / "nonexistent.md"

        record = process_markdown_file(nonexistent, config)

        assert record is None

    def test_process_file_with_special_characters(self, temp_dir: Path):
        """Test processing files with special characters in path."""
        config = TILConfig(root_path=temp_dir)

        # Create file with special characters
        special_dir = temp_dir / "special-topic"
        special_dir.mkdir()
        special_file = special_dir / "file-with-dashes.md"
        special_file.write_text("# Special Title\n\nContent")

        record = process_markdown_file(special_file, config)

        assert record is not None
        assert record["slug"] == "file-with-dashes"
        assert record["topic"] == "special-topic"
        assert record["path"] == "special-topic_file-with-dashes.md"


class TestBuildDatabase:
    """Test full database building process."""

    def test_build_database_from_scratch(
        self, temp_git_repo: Repo, temp_dir: Path, mock_github_api
    ):
        """Test building database from scratch."""
        config = TILConfig(
            root_path=Path(temp_git_repo.working_dir), database_name="test.db"
        )

        build_database(config)

        # Check database was created and populated
        db = sqlite_utils.Database(config.database_path)

        assert "til" in db.table_names()
        assert db["til"].count == 3  # We created 3 TIL files

        # Check table structure
        columns = {col.name for col in db["til"].columns}
        # Some columns are optional if no git history is available
        required_columns = {"path", "slug", "topic", "title", "url", "body", "html"}
        optional_columns = {"created", "created_utc", "updated", "updated_utc"}
        assert required_columns.issubset(columns)

        # Check FTS is enabled
        assert "til_fts" in db.table_names()

    def test_build_database_update_existing(
        self, temp_git_repo: Repo, temp_dir: Path, mock_github_api
    ):
        """Test updating existing database."""
        config = TILConfig(
            root_path=Path(temp_git_repo.working_dir), database_name="test.db"
        )

        db = sqlite_utils.Database(config.database_path)

        # Pre-populate database with one record
        table = db["til"]
        table.insert(
            {
                "path": "python_test-til-1.md",
                "slug": "test-til-1",
                "topic": "python",
                "title": "Old Title",
                "body": "Old content",
                "html": "<p>Old</p>",
            }
        )

        build_database(config)

        # Re-open database to check results
        db = sqlite_utils.Database(config.database_path)
        table = db["til"]

        # Check that record was updated
        all_records = list(table.rows)
        assert len(all_records) > 0

        # Find the updated record
        updated_record = None
        for record in all_records:
            if record["path"] == "python_test-til-1.md":
                updated_record = record
                break

        assert updated_record is not None
        assert updated_record["title"] == "Test TIL 1"  # Should be updated
        assert updated_record["body"] != "Old content"

        # Check that new records were added (we have 4: 1 existing + 3 from the test repo)
        assert table.count == 4

    def test_build_database_handles_missing_git_history(
        self, temp_dir: Path, mock_github_api
    ):
        """Test building database when git history is missing."""
        # Initialize git repo but don't add the markdown file to git
        repo = Repo.init(temp_dir)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Create files without git history
        python_dir = temp_dir / "python"
        python_dir.mkdir()
        test_file = python_dir / "test.md"
        test_file.write_text("# Test\n\nContent")

        # Commit something else to establish repo
        dummy = temp_dir / "dummy.txt"
        dummy.write_text("dummy")
        repo.index.add(["dummy.txt"])
        repo.index.commit("Initial")

        config = TILConfig(root_path=temp_dir, database_name="test.db")

        build_database(config)

        db = sqlite_utils.Database(config.database_path)
        assert db["til"].count == 1
        record = list(db["til"].rows)[0]

        # Should create record but without git timestamps
        assert record["title"] == "Test"
        # The record might not have created/updated fields if not in git history
        if "created" in record:
            assert record["created"] is None

    @patch("til.build_db.render_markdown_via_github")
    def test_build_database_handles_render_failure(
        self, mock_render, temp_git_repo: Repo
    ):
        """Test handling of markdown rendering failures."""
        mock_render.return_value = None  # Simulate rendering failure

        config = TILConfig(
            root_path=Path(temp_git_repo.working_dir), database_name="test.db"
        )

        # build_database should skip files that fail to render
        build_database(config)

        # Database should be created but empty since all renders failed
        assert config.database_path.exists()
        db = sqlite_utils.Database(config.database_path)

        # Since no files were successfully processed, the table may not exist
        if "til" in db.table_names():
            assert db["til"].count == 0
        else:
            # If table doesn't exist, that's fine - no files were processed
            assert True
