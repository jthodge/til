"""Centralized logging configuration for TIL application."""

import json
import logging
import logging.handlers
import os
import sys
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .exceptions import ConfigurationError


class LogFormat(Enum):
    """Available log formats."""

    JSON = "json"
    TEXT = "text"


class LogLevel(Enum):
    """Available log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogConfig:
    """Configuration for logging.

    Integrates with TILConfig for centralized configuration management.
    """

    # Basic configuration
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT

    # File configuration
    log_file: Optional[Path] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    # Console configuration
    console_enabled: bool = True

    # Context configuration
    add_context: bool = True
    request_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.log_file and not self.log_file.parent.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        if self.max_bytes <= 0:
            raise ConfigurationError("max_bytes must be positive")

        if self.backup_count < 0:
            raise ConfigurationError("backup_count must be non-negative")

    @classmethod
    def from_environment(cls) -> "LogConfig":
        """Create log configuration from environment variables.

        Returns:
            LogConfig instance

        """
        level = LogLevel(os.environ.get("TIL_LOG_LEVEL", "INFO").upper())
        format = LogFormat(os.environ.get("TIL_LOG_FORMAT", "text").lower())

        log_file = None
        if log_file_env := os.environ.get("TIL_LOG_FILE"):
            log_file = Path(log_file_env)

        return cls(
            level=level,
            format=format,
            log_file=log_file,
            console_enabled=os.environ.get("TIL_LOG_CONSOLE", "true").lower() == "true",
            add_context=os.environ.get("TIL_LOG_CONTEXT", "true").lower() == "true",
        )


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, include_timestamp: bool = True):
        """Initialize JSON formatter.

        Args:
            include_timestamp: Whether to include timestamp in logs

        """
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string

        """
        log_data: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_timestamp:
            log_data["timestamp"] = self.formatTime(record, self.datefmt)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
            ):
                log_data[key] = value

        return json.dumps(log_data, default=str)


class ContextFilter(logging.Filter):
    """Add context to log records."""

    def __init__(self, request_id: Optional[str] = None):
        """Initialize context filter.

        Args:
            request_id: Request ID to add to logs

        """
        super().__init__()
        self.request_id = request_id or str(uuid.uuid4())

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record.

        Args:
            record: Log record to filter

        Returns:
            True to allow the record through

        """
        if not hasattr(record, "request_id"):
            record.request_id = self.request_id
        return True


def setup_logging(config: LogConfig) -> None:
    """Set up logging with the provided configuration.

    Args:
        config: Logging configuration

    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.level.value)

    # Clear existing handlers and filters
    root_logger.handlers = []
    root_logger.filters = []

    # Set up formatters
    if config.format == LogFormat.JSON:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Add context filter if enabled
    if config.add_context:
        context_filter = ContextFilter(config.request_id)
        root_logger.addFilter(context_filter)

    # Set up console handler
    if config.console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(config.level.value)
        root_logger.addHandler(console_handler)

    # Set up file handler
    if config.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.log_file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(config.level.value)
        root_logger.addHandler(file_handler)

    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized",
        extra={
            "log_level": config.level.value,
            "log_format": config.format.value,
            "log_file": str(config.log_file) if config.log_file else None,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    """
    return logging.getLogger(name)
