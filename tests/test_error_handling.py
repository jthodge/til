"""Tests for error handling and custom exceptions."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.config import TILConfig
from til.database import TILDatabase
from til.exceptions import (
    APIError,
    ConfigurationError,
    DatabaseError,
    FileProcessingError,
    RenderingError,
    RepositoryError,
    TILError,
)
from til.processor import TILProcessor
from til.renderer import MarkdownRenderer
from til.repository import GitRepository


def test_repository_error_invalid_path() -> None:
    """Test RepositoryError when path doesn't exist."""
    with pytest.raises(RepositoryError, match="Path does not exist"):
        GitRepository(Path("/nonexistent/path"))


def test_repository_error_not_git_repo(temp_dir: Path) -> None:
    """Test RepositoryError when path is not a git repository."""
    with pytest.raises(RepositoryError, match="Not a valid git repository"):
        GitRepository(temp_dir)


def test_processor_configuration_error() -> None:
    """Test ConfigurationError when root path doesn't exist."""
    with pytest.raises(ConfigurationError, match="Root path does not exist"):
        TILConfig(root_path=Path("/nonexistent/path"))


def test_file_processing_error_empty_file(temp_dir: Path) -> None:
    """Test FileProcessingError for empty file."""
    config = TILConfig(root_path=temp_dir)

    # Create empty markdown file
    content_dir = temp_dir / "content"
    content_dir.mkdir()
    test_dir = content_dir / "test"
    test_dir.mkdir()
    test_file = test_dir / "empty.md"
    test_file.write_text("")

    with patch("til.processor.GitRepository"):
        processor = TILProcessor(config)

        with pytest.raises(FileProcessingError, match="Empty file"):
            processor.process_file(test_file)


def test_file_processing_error_no_title(temp_dir: Path) -> None:
    """Test FileProcessingError for file without title."""
    config = TILConfig(root_path=temp_dir)

    # Create markdown file with no title (but not empty)
    content_dir = temp_dir / "content"
    content_dir.mkdir()
    test_dir = content_dir / "test"
    test_dir.mkdir()
    test_file = test_dir / "no_title.md"
    test_file.write_text("###\n\nSome content but no title")

    with patch("til.processor.GitRepository"):
        processor = TILProcessor(config)

        with pytest.raises(FileProcessingError, match="No title found"):
            processor.process_file(test_file)


def test_file_processing_error_invalid_structure(temp_dir: Path) -> None:
    """Test FileProcessingError for invalid file structure."""
    config = TILConfig(root_path=temp_dir)

    # Create markdown file at content level (not in topic directory)
    content_dir = temp_dir / "content"
    content_dir.mkdir()
    test_file = content_dir / "invalid.md"
    test_file.write_text("# Title\n\nContent")

    with patch("til.processor.GitRepository"):
        processor = TILProcessor(config)

        with pytest.raises(FileProcessingError, match="Invalid file structure"):
            processor.process_file(test_file)


def test_rendering_error_api_failure() -> None:
    """Test RenderingError when GitHub API fails."""
    config = TILConfig(github_token="test_token", max_retries=1, retry_delay=1)
    renderer = MarkdownRenderer(config)

    with patch("httpx.post", side_effect=Exception("Network error")):
        with pytest.raises(RenderingError, match="Failed to render markdown"):
            renderer.render("# Test")


def test_api_error_unauthorized() -> None:
    """Test APIError for unauthorized access."""
    config = TILConfig(github_token="invalid_token", max_retries=1)
    renderer = MarkdownRenderer(config)

    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(APIError, match="401 Unauthorized"):
            renderer.render("# Test")


def test_api_error_rate_limit() -> None:
    """Test APIError for rate limiting."""
    config = TILConfig(max_retries=1, retry_delay=1)
    renderer = MarkdownRenderer(config)

    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "API rate limit exceeded"

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RenderingError, match="rate limit"):
            renderer.render("# Test")


def test_database_error_empty_record() -> None:
    """Test DatabaseError for empty record."""
    db = TILDatabase(Path(":memory:"))

    with pytest.raises(DatabaseError, match="Cannot save empty record"):
        db.upsert_record({})


def test_database_error_missing_fields() -> None:
    """Test DatabaseError for record with missing fields."""
    db = TILDatabase(Path(":memory:"))

    with pytest.raises(DatabaseError, match="missing required fields"):
        db.upsert_record({"path": "test", "title": "Test"})


def test_database_error_invalid_path() -> None:
    """Test DatabaseError when accessing record with empty path."""
    db = TILDatabase(Path(":memory:"))

    with pytest.raises(DatabaseError, match="Path cannot be empty"):
        db.get_previous_record("")


def test_processor_graceful_git_failure(temp_dir: Path) -> None:
    """Test that processor continues without git when repository fails."""
    config = TILConfig(root_path=temp_dir)

    # Create a topic directory with a markdown file
    content_dir = temp_dir / "content"
    content_dir.mkdir()
    topic_dir = content_dir / "test"
    topic_dir.mkdir()
    test_file = topic_dir / "test.md"
    test_file.write_text("# Test\n\nContent")

    with patch("til.processor.GitRepository", side_effect=RepositoryError("Git error")):
        processor = TILProcessor(config)

        # Should still be able to process files without git
        record = processor.process_file(test_file)
        assert record is not None
        assert record["title"] == "Test"
        assert "created" not in record  # No git history


def test_processor_continues_on_file_errors(temp_dir: Path) -> None:
    """Test that processor continues processing other files when one fails."""
    config = TILConfig(root_path=temp_dir)

    # Create topic directory
    content_dir = temp_dir / "content"
    content_dir.mkdir()
    topic_dir = content_dir / "test"
    topic_dir.mkdir()

    # Create good file
    good_file = topic_dir / "good.md"
    good_file.write_text("# Good\n\nContent")

    # Create bad file (empty)
    bad_file = topic_dir / "bad.md"
    bad_file.write_text("")

    with (
        patch("til.processor.GitRepository"),
        patch("til.renderer.MarkdownRenderer.render", return_value="<html>"),
        patch.object(TILDatabase, "upsert_record") as mock_upsert,
        patch.object(TILDatabase, "enable_search"),
    ):
        processor = TILProcessor(config)
        processor.process_all_files()

        # Should have processed the good file despite the bad one
        mock_upsert.assert_called_once()
        # Check that the call was for the good file
        call_args = mock_upsert.call_args[0][0]
        assert call_args["title"] == "Good"


def test_error_hierarchy() -> None:
    """Test that all custom exceptions inherit from TILError."""
    assert issubclass(ConfigurationError, TILError)
    assert issubclass(RepositoryError, TILError)
    assert issubclass(FileProcessingError, TILError)
    assert issubclass(RenderingError, TILError)
    assert issubclass(DatabaseError, TILError)
    assert issubclass(APIError, TILError)


def test_api_error_status_code() -> None:
    """Test APIError with status code."""
    error = APIError("Test error", status_code=404)
    assert error.status_code == 404
    assert str(error) == "Test error"
