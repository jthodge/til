"""Configuration for TIL application."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TILConfig:
    """Configuration for TIL application."""

    # GitHub configuration
    github_token: Optional[str] = None
    github_repo: str = "jthodge/til"
    markdown_api_url: str = "https://api.github.com/markdown"

    # Database configuration
    database_name: str = "til.db"

    # Retry configuration
    max_retries: int = 3
    retry_delay: int = 60

    # Paths
    root_path: Path = Path(__file__).parent.parent.resolve()

    @classmethod
    def from_environment(cls) -> "TILConfig":
        """Create configuration from environment variables."""
        return cls(
            github_token=os.environ.get("MARKDOWN_GITHUB_TOKEN"),
            github_repo=os.environ.get("TIL_GITHUB_REPO", "jthodge/til"),
        )

    @property
    def database_path(self) -> Path:
        """Get full path to database file."""
        return self.root_path / self.database_name

    @property
    def github_url_base(self) -> str:
        """Get base URL for GitHub repository."""
        return f"https://github.com/{self.github_repo}"
