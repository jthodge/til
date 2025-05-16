"""Markdown rendering functionality for TIL."""

import logging
import time
from typing import Optional, Union

import httpx

from .config import TILConfig
from .exceptions import APIError, RenderingError

logger = logging.getLogger(__name__)


class MarkdownRenderer:
    """Handle markdown to HTML conversion."""

    def __init__(self, config: TILConfig):
        """Initialize MarkdownRenderer with configuration.

        Args:
            config: TIL configuration containing API settings
        """
        self.config = config
        self.api_url = "https://api.github.com/markdown"

    def render(self, markdown: str) -> Optional[str]:
        """Render markdown to HTML via GitHub API.

        Args:
            markdown: Markdown content to render

        Returns:
            Rendered HTML

        Raises:
            RenderingError: If rendering fails after all retries
            APIError: If API returns an authentication error
        """
        if not markdown.strip():
            logger.warning("Empty markdown content provided")
            return None

        headers = {}
        if self.config.github_token:
            headers["authorization"] = f"Bearer {self.config.github_token}"
        else:
            logger.warning("No GitHub token configured, API rate limits may apply")

        last_error: Optional[Union[APIError, RenderingError]] = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(
                    f"Attempting to render markdown (attempt {attempt + 1}/{self.config.max_retries})"
                )
                response = httpx.post(
                    self.api_url,
                    json={"mode": "markdown", "text": markdown},
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    logger.debug("Successfully rendered markdown")
                    html = str(response.text).strip()
                    if not html:
                        logger.warning("GitHub API returned empty HTML")
                    return html
                elif response.status_code == 401:
                    raise APIError(
                        "GitHub API returned 401 Unauthorized - check your token",
                        status_code=401,
                    )
                elif response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        logger.warning(
                            f"Rate limit exceeded (attempt {attempt + 1}/{self.config.max_retries})"
                        )
                        last_error = APIError(
                            "GitHub API rate limit exceeded", status_code=403
                        )
                    else:
                        raise APIError(
                            "GitHub API returned 403 Forbidden", status_code=403
                        )
                elif response.status_code == 422:
                    raise RenderingError(f"Invalid markdown content: {response.text}")
                else:
                    logger.warning(
                        f"GitHub API returned {response.status_code}, "
                        f"attempt {attempt + 1}/{self.config.max_retries}"
                    )
                    last_error = APIError(
                        f"GitHub API returned {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )

                    if attempt < self.config.max_retries - 1:
                        wait_time = self._calculate_backoff(attempt)
                        logger.info(f"Sleeping for {wait_time} seconds before retry...")
                        time.sleep(wait_time)

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during request: {e}")
                last_error = RenderingError(f"Network error: {e}")

                if attempt < self.config.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    logger.info(f"Sleeping for {wait_time} seconds before retry...")
                    time.sleep(wait_time)
            except (APIError, RenderingError):
                # Re-raise our custom exceptions without wrapping
                raise
            except Exception as e:
                logger.error(f"Unexpected error during rendering: {e}")
                last_error = RenderingError(f"Unexpected error: {e}")

                if attempt < self.config.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    logger.info(f"Sleeping for {wait_time} seconds before retry...")
                    time.sleep(wait_time)

        # All retries exhausted
        error_msg = (
            f"Failed to render markdown after {self.config.max_retries} attempts"
        )
        if last_error:
            error_msg += f": {last_error}"
        raise RenderingError(error_msg)

    def _calculate_backoff(self, attempt: int) -> int:
        """Calculate exponential backoff time.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Number of seconds to wait
        """
        # Exponential backoff: 1, 2, 4, 8, etc. seconds
        base_delay = self.config.retry_delay
        return int(min(base_delay * (2**attempt), 60))  # Cap at 60 seconds
