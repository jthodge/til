"""Tests for TILProcessor class."""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.config import TILConfig
from til.exceptions import ConfigurationError, FileProcessingError, RepositoryError
from til.processor import TILProcessor


def test_til_processor_initialization(temp_dir: Path) -> None:
    """Test TILProcessor initialization."""
    config = TILConfig(root_path=temp_dir)

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


def test_til_processor_initialization_git_failure(temp_dir: Path) -> None:
    """Test TILProcessor initialization when git fails."""
    config = TILConfig(root_path=temp_dir)

    with (
        patch("til.processor.GitRepository", side_effect=RepositoryError("Git error")),
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


def test_process_file_not_exists(temp_dir: Path) -> None:
    """Test processing a file that doesn't exist."""
    config = TILConfig(root_path=temp_dir)

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
    ):

        processor = TILProcessor(config)
        nonexistent_file = temp_dir / "python" / "nonexistent.md"

        with pytest.raises(FileProcessingError, match="File does not exist"):
            processor.process_file(nonexistent_file)


def test_process_file_empty(temp_dir: Path) -> None:
    """Test processing an empty file."""
    config = TILConfig(root_path=temp_dir)

    # Create empty test file
    topic_dir = temp_dir / "python"
    topic_dir.mkdir()
    test_file = topic_dir / "empty.md"
    test_file.write_text("")

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
    ):
        processor = TILProcessor(config)

        with pytest.raises(FileProcessingError, match="Empty file"):
            processor.process_file(test_file)


def test_should_update_html_no_previous(temp_dir: Path) -> None:
    """Test HTML update check with no previous record."""
    config = TILConfig(root_path=temp_dir)

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase") as mock_db,
    ):

        mock_db.return_value.get_previous_record.return_value = None

        processor = TILProcessor(config)
        record = {"path": "test.md", "body": "content"}

        assert processor.should_update_html(record) is True


def test_should_update_html_different_body(temp_dir: Path) -> None:
    """Test HTML update check with different body."""
    config = TILConfig(root_path=temp_dir)

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


def test_should_update_html_no_html(temp_dir: Path) -> None:
    """Test HTML update check with missing HTML."""
    config = TILConfig(root_path=temp_dir)

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


def test_should_update_html_same_content(temp_dir: Path) -> None:
    """Test HTML update check with same content."""
    config = TILConfig(root_path=temp_dir)

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
    """Test processing all markdown files."""
    config = TILConfig(root_path=temp_dir)

    # Create test files
    python_dir = temp_dir / "python"
    python_dir.mkdir()
    (python_dir / "test1.md").write_text("# Test 1\n\nContent 1")
    (python_dir / "test2.md").write_text("# Test 2\n\nContent 2")

    js_dir = temp_dir / "javascript"
    js_dir.mkdir()
    (js_dir / "test.md").write_text("# JS Test\n\nJS Content")

    # Mock dependencies
    mock_renderer = Mock()
    mock_renderer.render.return_value = "<p>HTML</p>"

    mock_db = Mock()
    mock_db.get_previous_record.return_value = None

    with (
        patch("til.processor.GitRepository") as mock_git,
        patch("til.processor.MarkdownRenderer", return_value=mock_renderer),
        patch("til.processor.TILDatabase", return_value=mock_db),
        patch("til.processor.logger") as mock_logger,
    ):
        mock_git.return_value.get_file_history.return_value = {}

        processor = TILProcessor(config)
        processor.process_all_files()

        # Verify all files were processed
        assert mock_db.upsert_record.call_count == 3
        assert mock_db.enable_search.called

        # Check logging
        mock_logger.info.assert_any_call("Found 3 markdown files")


def test_process_all_files_with_errors(temp_dir: Path) -> None:
    """Test processing files with some failures."""
    config = TILConfig(root_path=temp_dir)

    # Create test files - one good, one bad (empty)
    python_dir = temp_dir / "python"
    python_dir.mkdir()
    (python_dir / "good.md").write_text("# Good\n\nContent")
    (python_dir / "bad.md").write_text("")  # Empty file

    # Mock dependencies
    mock_renderer = Mock()
    mock_renderer.render.return_value = "<p>HTML</p>"

    mock_db = Mock()
    mock_db.get_previous_record.return_value = None

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer", return_value=mock_renderer),
        patch("til.processor.TILDatabase", return_value=mock_db),
        patch("til.processor.logger") as mock_logger,
    ):
        processor = TILProcessor(config)
        processor.process_all_files()

        # Only the good file should be processed
        assert mock_db.upsert_record.call_count == 1


def test_build_database(temp_dir: Path) -> None:
    """Test the main build database method."""
    config = TILConfig(root_path=temp_dir)

    with (
        patch("til.processor.GitRepository"),
        patch("til.processor.MarkdownRenderer"),
        patch("til.processor.TILDatabase"),
        patch.object(TILProcessor, "process_all_files") as mock_process,
    ):
        processor = TILProcessor(config)
        processor.build_database()

        mock_process.assert_called_once()
