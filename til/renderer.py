"""Markdown rendering functionality for TIL."""

import logging
import time
from typing import Optional

import httpx

from .config import TILConfig

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
            Rendered HTML or None if failed
        """
        headers = {}
        if self.config.github_token:
            headers["authorization"] = f"Bearer {self.config.github_token}"

        for attempt in range(self.config.max_retries):
            try:
                response = httpx.post(
                    self.api_url,
                    json={"mode": "markdown", "text": markdown},
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    logger.info("Successfully rendered markdown")
                    return str(response.text)
                elif response.status_code == 401:
                    logger.error("GitHub API returned 401 Unauthorized")
                    return None
                else:
                    logger.warning(
                        f"GitHub API returned {response.status_code}, "
                        f"attempt {attempt + 1}/{self.config.max_retries}"
                    )

                    if attempt < self.config.max_retries - 1:
                        logger.info(
                            f"Sleeping for {self.config.retry_delay} seconds before retry..."
                        )
                        time.sleep(self.config.retry_delay)

            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)

        return None
