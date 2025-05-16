"""Tests for TILProcessor class."""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.config import TILConfig
from til.processor import TILProcessor


def test_til_processor_initialization() -> None:
    """Test TILProcessor initialization."""
    config = TILConfig(root_path=Path("/test"))

    with (
        patch("til.processor.GitRepository") as mock_git,
        patch("til.processor.MarkdownRenderer") as mock_renderer,
        patch("til.processor.TILDatabase") as mock_db,
    ):

        processor = TILProcessor(config)

        assert processor.config == config
        mock_git.assert_called_once_with(config.root_path)
        mock_renderer.assert_called_once_with(config)
        mock_db.assert_called_once_with(config.database_path)


def test_til_processor_initialization_git_failure() -> None:
    """Test TILProcessor initialization when git fails."""
    config = TILConfig(root_path=Path("/test"))

    with (
        patch("til.processor.GitRepository", side_effect=Exception("Git error")),
        patch("til.processor.MarkdownRenderer") as mock_renderer,
        patch("til.processor.TILDatabase") as mock_db,
    ):

        processor = TILProcessor(config)

        assert processor.repository is None
        assert processor.renderer is not None
        assert processor.database is not None


def test_process_file(temp_dir: Path) -> None:
    """Test processing a single markdown file."""
    config = TILConfig(root_path=temp_dir)

    # Create test file
    topic_dir = temp_dir / "python"
    topic_dir.mkdir()
    test_file = topic_dir / "test.md"
    test_file.write_text("# Test Title\n\nTest content")

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
    ):

        processor = TILProcessor(config)
        record = processor.process_file(test_file)

    assert record is not None
    assert record["path"] == "python_test.md"
    assert record["slug"] == "test"
    assert record["topic"] == "python"
    assert record["title"] == "Test Title"
    assert record["body"] == "Test content"
    assert record["url"] == "https://github.com/jthodge/til/blob/main/python/test.md"


def test_process_file_io_error(temp_dir: Path) -> None:
    """Test processing a file that doesn't exist."""
    config = TILConfig(root_path=temp_dir)

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
    ):

        processor = TILProcessor(config)
        record = processor.process_file(temp_dir / "nonexistent.md")

    assert record is None


def test_should_update_html_no_previous() -> None:
    """Test HTML update check with no previous record."""
    config = TILConfig()

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase") as mock_db,
    ):

        mock_db.return_value.get_previous_record.return_value = None

        processor = TILProcessor(config)
        record = {"path": "test.md", "body": "content"}

        assert processor.should_update_html(record) is True


def test_should_update_html_different_body() -> None:
    """Test HTML update check with different body."""
    config = TILConfig()

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase") as mock_db,
    ):

        previous = {"body": "old content", "html": "<p>old</p>"}
        mock_db.return_value.get_previous_record.return_value = previous

        processor = TILProcessor(config)
        record = {"path": "test.md", "body": "new content"}

        assert processor.should_update_html(record) is True


def test_should_update_html_no_html() -> None:
    """Test HTML update check with missing HTML."""
    config = TILConfig()

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase") as mock_db,
    ):

        previous = {"body": "content"}
        mock_db.return_value.get_previous_record.return_value = previous

        processor = TILProcessor(config)
        record = {"path": "test.md", "body": "content"}

        assert processor.should_update_html(record) is True


def test_should_update_html_no_update_needed() -> None:
    """Test HTML update check when no update needed."""
    config = TILConfig()

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase") as mock_db,
    ):

        previous = {"body": "content", "html": "<p>content</p>"}
        mock_db.return_value.get_previous_record.return_value = previous

        processor = TILProcessor(config)
        record = {"path": "test.md", "body": "content"}

        assert processor.should_update_html(record) is False


def test_process_all_files(temp_dir: Path) -> None:
    """Test processing all files."""
    config = TILConfig(root_path=temp_dir)

    # Create test files
    python_dir = temp_dir / "python"
    python_dir.mkdir()
    (python_dir / "test1.md").write_text("# Test 1\n\nContent 1")
    (python_dir / "test2.md").write_text("# Test 2\n\nContent 2")

    with (
        patch("til.processor.GitRepository") as mock_git,
        patch("til.processor.MarkdownRenderer") as mock_renderer,
        patch("til.processor.TILDatabase") as mock_db,
    ):

        # Setup mocks
        mock_git.return_value.get_file_history.return_value = {
            "python/test1.md": {"created": "2023-01-01"},
            "python/test2.md": {"created": "2023-01-02"},
        }
        mock_renderer.return_value.render.return_value = "<p>HTML</p>"
        mock_db.return_value.get_previous_record.return_value = None

        processor = TILProcessor(config)
        processor.process_all_files()

        # Verify calls
        assert mock_git.return_value.get_file_history.call_count == 1
        assert mock_renderer.return_value.render.call_count == 2
        assert mock_db.return_value.upsert_record.call_count == 2
        assert mock_db.return_value.enable_search.call_count == 1


def test_process_all_files_with_errors(temp_dir: Path) -> None:
    """Test processing all files with various errors."""
    config = TILConfig(root_path=temp_dir)

    # Create test files
    python_dir = temp_dir / "python"
    python_dir.mkdir()
    (python_dir / "good.md").write_text("# Good\n\nContent")
    (python_dir / "bad.md").write_text("")  # Empty file

    with (
        patch("til.processor.GitRepository") as mock_git,
        patch("til.processor.MarkdownRenderer") as mock_renderer,
        patch("til.processor.TILDatabase") as mock_db,
    ):

        # Setup mocks
        mock_git.return_value.get_file_history.return_value = {}
        mock_renderer.return_value.render.side_effect = [
            "<p>HTML</p>",  # First file succeeds
            None,  # Second file fails to render
        ]
        mock_db.return_value.get_previous_record.return_value = None

        processor = TILProcessor(config)
        processor.process_all_files()

        # Only the good file should be processed
        assert mock_db.return_value.upsert_record.call_count == 1


def test_build_database() -> None:
    """Test build_database method."""
    config = TILConfig()

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
    ):

        processor = TILProcessor(config)

        # Mock process_all_files
        with patch.object(processor, "process_all_files") as mock_process:
            processor.build_database()
            mock_process.assert_called_once()
