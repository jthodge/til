"""Configuration for TIL application."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .exceptions import ConfigurationError


@dataclass
class TILConfig:
    """Configuration for TIL application with validation."""

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
    root_path: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.resolve()
    )

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_github_repo()
        self._validate_database_name()
        self._validate_retries()
        self._validate_paths()

    def _validate_github_repo(self) -> None:
        """Validate GitHub repository format."""
        if not self.github_repo or "/" not in self.github_repo:
            raise ConfigurationError(
                f"Invalid GitHub repository format: '{self.github_repo}'. "
                "Expected format: 'owner/repo'"
            )
        parts = self.github_repo.split("/")
        if len(parts) != 2 or not all(parts):
            raise ConfigurationError(
                f"Invalid GitHub repository format: '{self.github_repo}'. "
                "Expected format: 'owner/repo'"
            )

    def _validate_database_name(self) -> None:
        """Validate database name."""
        if not self.database_name:
            raise ConfigurationError("Database name cannot be empty")
        if not self.database_name.endswith(".db"):
            raise ConfigurationError(
                f"Database name must end with '.db': '{self.database_name}'"
            )

    def _validate_retries(self) -> None:
        """Validate retry configuration."""
        if self.max_retries < 0:
            raise ConfigurationError(
                f"max_retries must be non-negative: {self.max_retries}"
            )
        if self.retry_delay <= 0:
            raise ConfigurationError(
                f"retry_delay must be positive: {self.retry_delay}"
            )

    def _validate_paths(self) -> None:
        """Validate paths configuration."""
        if not self.root_path.exists():
            raise ConfigurationError(f"Root path does not exist: {self.root_path}")
        if not self.root_path.is_dir():
            raise ConfigurationError(f"Root path is not a directory: {self.root_path}")

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
