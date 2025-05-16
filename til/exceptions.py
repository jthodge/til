"""Custom exceptions for TIL processing."""

from typing import Optional


class TILError(Exception):
    """Base exception for all TIL-related errors."""

    pass


class RepositoryError(TILError):
    """Errors related to git repository operations."""

    pass


class ConfigurationError(TILError):
    """Errors related to configuration."""

    pass


class FileProcessingError(TILError):
    """Errors that occur while processing markdown files."""

    pass


class RenderingError(TILError):
    """Errors that occur during markdown rendering."""

    pass


class DatabaseError(TILError):
    """Errors related to database operations."""

    pass


class APIError(TILError):
    """Errors related to external API calls."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
