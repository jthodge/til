"""Tests for MarkdownRenderer class."""

import time
from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest

from til.config import TILConfig
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

    # The mock returns "<h1>Test</h1>\n<p></p>" based on the fixture logic
    assert html is not None
    assert "<h1>Test" in html


def test_render_without_token(
    mock_github_api: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test rendering without GitHub token."""
    config = TILConfig(github_token=None)
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html is not None
    assert "<h1>Test" in html


@patch("httpx.post")
def test_render_unauthorized(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of 401 unauthorized response."""
    # Mock 401 response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response

    config = TILConfig(github_token="invalid_token")
    renderer = MarkdownRenderer(config)

    html = renderer.render("# Test")

    assert html is None
    mock_post.assert_called_once()


@patch("httpx.post")
def test_render_with_retry(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test retry logic for failed requests."""
    # Mock responses: first two fail, third succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.text = "<h1>Test</h1>"

    mock_post.side_effect = [
        mock_response_fail,
        mock_response_fail,
        mock_response_success,
    ]

    config = TILConfig(github_token="test_token", max_retries=3, retry_delay=1)
    renderer = MarkdownRenderer(config)

    with patch("time.sleep") as mock_sleep:
        html = renderer.render("# Test")

    assert html == "<h1>Test</h1>"
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(1)


@patch("httpx.post")
def test_render_max_retries_exceeded(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test failure when max retries exceeded."""
    # Mock all responses to fail
    mock_response = Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    config = TILConfig(github_token="test_token", max_retries=3, retry_delay=1)
    renderer = MarkdownRenderer(config)

    with patch("time.sleep") as mock_sleep:
        html = renderer.render("# Test")

    assert html is None
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2


@patch("httpx.post")
def test_render_request_error(
    mock_post: Any,
) -> None:  # TODO: Replace Any with specific type
    """Test handling of request errors."""
    # Mock request error
    mock_post.side_effect = httpx.RequestError("Connection error")

    config = TILConfig(github_token="test_token", max_retries=2, retry_delay=1)
    renderer = MarkdownRenderer(config)

    with patch("time.sleep") as mock_sleep:
        html = renderer.render("# Test")

    assert html is None
    assert mock_post.call_count == 2
    assert mock_sleep.call_count == 1


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

    config = TILConfig(github_token="test_token", max_retries=2, retry_delay=1)
    renderer = MarkdownRenderer(config)

    with patch("time.sleep") as mock_sleep:
        html = renderer.render("# Test")

    assert html == "<h1>Test</h1>"
    assert mock_post.call_count == 2
    assert mock_sleep.call_count == 1
