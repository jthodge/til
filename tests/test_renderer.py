"""Tests for MarkdownRenderer class."""

import time
from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest

from til.config import TILConfig
from til.exceptions import APIError, RenderingError
from til.renderer import MarkdownRenderer


def test_markdown_renderer_initialization() -> None:
    """Test MarkdownRenderer initialization."""
    config = TILConfig(github_token="test_token")
    renderer = MarkdownRenderer(config)

    assert renderer.config == config
    assert renderer.api_url == "https://api.github.com/markdown"


def test_render_successful(
    mock_github_api: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test successful markdown rendering."""
    config = TILConfig(github_token="test_token")
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html == "<h1>Test</p>"


def test_render_empty_markdown() -> None:
    """Test rendering empty markdown."""
    config = TILConfig()
    renderer = MarkdownRenderer(config)

    html = renderer.render("")

    assert html is None


def test_render_no_token_warning(
    caplog: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test warning when no token is configured."""
    config = TILConfig()
    renderer = MarkdownRenderer(config)

    with patch("httpx.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<h1>Test</h1>"
        mock_post.return_value = mock_response

        renderer.render("# Test")

    assert "No GitHub token configured" in caplog.text


@patch("httpx.post")
def test_render_unauthorized(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of 401 unauthorized response."""
    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    config = TILConfig(github_token="invalid_token", max_retries=1)
    renderer = MarkdownRenderer(config)

    with pytest.raises(APIError, match="401 Unauthorized"):
        renderer.render("# Test")

    mock_post.assert_called_once()


@patch("httpx.post")
def test_render_with_retry(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test retry logic for failed requests."""
    # Mock responses: first two fail, third succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500
    mock_response_fail.text = "Server error"

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.text = "<h1>Test</h1>"

    mock_post.side_effect = [
        mock_response_fail,
        mock_response_fail,
        mock_response_success,
    ]

    config = TILConfig(github_token="test_token", max_retries=3, retry_delay=0)
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html == "<h1>Test</h1>"
    assert mock_post.call_count == 3


@patch("httpx.post")
def test_render_max_retries_exceeded(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test failure when max retries exceeded."""
    # Mock all responses to fail
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Server error"
    mock_post.return_value = mock_response

    config = TILConfig(github_token="test_token", max_retries=3, retry_delay=0)
    renderer = MarkdownRenderer(config)

    with pytest.raises(
        RenderingError, match="Failed to render markdown after 3 attempts"
    ):
        renderer.render("# Test")

    assert mock_post.call_count == 3


@patch("httpx.post")
def test_render_request_error(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of request errors."""
    # Mock request error
    mock_post.side_effect = httpx.RequestError("Connection error")

    config = TILConfig(github_token="test_token", max_retries=2, retry_delay=0)
    renderer = MarkdownRenderer(config)

    with pytest.raises(RenderingError, match="Network error"):
        renderer.render("# Test")

    assert mock_post.call_count == 2


@patch("httpx.post")
def test_render_request_error_then_success(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test recovery from request error."""
    # First call raises error, second succeeds
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<h1>Test</h1>"

    mock_post.side_effect = [
        httpx.RequestError("Connection error"),
        mock_response,
    ]

    config = TILConfig(github_token="test_token", max_retries=2, retry_delay=0)
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html == "<h1>Test</h1>"
    assert mock_post.call_count == 2


@patch("httpx.post")
def test_render_rate_limit(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of rate limit response."""
    # Mock 403 rate limit response
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "API rate limit exceeded"
    mock_post.return_value = mock_response

    config = TILConfig(github_token="test_token", max_retries=2, retry_delay=0)
    renderer = MarkdownRenderer(config)

    with pytest.raises(RenderingError, match="rate limit"):
        renderer.render("# Test")

    assert mock_post.call_count == 2


@patch("httpx.post")
def test_render_422_invalid_content(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of 422 invalid content response."""
    # Mock 422 response
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.text = "Invalid markdown"
    mock_post.return_value = mock_response

    config = TILConfig(github_token="test_token", max_retries=1)
    renderer = MarkdownRenderer(config)

    with pytest.raises(RenderingError, match="Invalid markdown content"):
        renderer.render("# Test")

    mock_post.assert_called_once()


@patch("httpx.post")
def test_render_empty_html_warning(
    mock_post: Any,
    caplog: Any,
) -> None:  # TODO: Replace Any with specific types
    """Test warning when GitHub returns empty HTML."""
    # Mock empty response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ""
    mock_post.return_value = mock_response

    config = TILConfig(github_token="test_token")
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html == ""
    assert "GitHub API returned empty HTML" in caplog.text
