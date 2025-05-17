"""Tests for logging configuration."""

import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from til.exceptions import ConfigurationError
from til.logging_config import (
    ContextFilter,
    get_logger,
    JSONFormatter,
    LogConfig,
    LogFormat,
    LogLevel,
    setup_logging,
)


class TestLogLevel:
    """Test LogLevel enum."""

    def test_log_levels(self):
        """Test all log levels are defined."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"


class TestLogFormat:
    """Test LogFormat enum."""

    def test_log_formats(self):
        """Test all log formats are defined."""
        assert LogFormat.JSON.value == "json"
        assert LogFormat.TEXT.value == "text"


class TestLogConfig:
    """Test LogConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LogConfig()
        assert config.level == LogLevel.INFO
        assert config.format == LogFormat.TEXT
        assert config.log_file is None
        assert config.max_bytes == 10 * 1024 * 1024
        assert config.backup_count == 5
        assert config.console_enabled is True
        assert config.add_context is True
        assert config.request_id is None

    def test_custom_config(self):
        """Test custom configuration values."""
        log_file = Path("/tmp/test.log")
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            log_file=log_file,
            max_bytes=1024,
            backup_count=3,
            console_enabled=False,
            add_context=False,
            request_id="test-123",
        )
        assert config.level == LogLevel.DEBUG
        assert config.format == LogFormat.JSON
        assert config.log_file == log_file
        assert config.max_bytes == 1024
        assert config.backup_count == 3
        assert config.console_enabled is False
        assert config.add_context is False
        assert config.request_id == "test-123"

    def test_validation_max_bytes(self):
        """Test max_bytes validation."""
        with pytest.raises(ConfigurationError, match="max_bytes must be positive"):
            LogConfig(max_bytes=0)

        with pytest.raises(ConfigurationError, match="max_bytes must be positive"):
            LogConfig(max_bytes=-1)

    def test_validation_backup_count(self):
        """Test backup_count validation."""
        with pytest.raises(
            ConfigurationError, match="backup_count must be non-negative"
        ):
            LogConfig(backup_count=-1)

    def test_log_file_directory_creation(self):
        """Test log file directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "logs" / "test.log"
            config = LogConfig(log_file=log_file)
            assert log_file.parent.exists()

    def test_from_environment(self):
        """Test creating config from environment variables."""
        env_vars = {
            "TIL_LOG_LEVEL": "DEBUG",
            "TIL_LOG_FORMAT": "json",
            "TIL_LOG_FILE": "/tmp/test.log",
            "TIL_LOG_CONSOLE": "false",
            "TIL_LOG_CONTEXT": "false",
        }

        with patch.dict(os.environ, env_vars):
            config = LogConfig.from_environment()
            assert config.level == LogLevel.DEBUG
            assert config.format == LogFormat.JSON
            assert config.log_file == Path("/tmp/test.log")
            assert config.console_enabled is False
            assert config.add_context is False

    def test_from_environment_defaults(self):
        """Test creating config from environment with defaults."""
        with patch.dict(os.environ, clear=True):
            config = LogConfig.from_environment()
            assert config.level == LogLevel.INFO
            assert config.format == LogFormat.TEXT
            assert config.log_file is None
            assert config.console_enabled is True
            assert config.add_context is True


class TestJSONFormatter:
    """Test JSONFormatter class."""

    def test_format_basic(self):
        """Test basic JSON formatting."""
        formatter = JSONFormatter(include_timestamp=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" not in data

    def test_format_with_timestamp(self):
        """Test JSON formatting with timestamp."""
        formatter = JSONFormatter(include_timestamp=True)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert "timestamp" in data

    def test_format_with_exception(self):
        """Test JSON formatting with exception."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert "exception" in data
        assert "ValueError: Test error" in data["exception"]

    def test_format_with_extra_fields(self):
        """Test JSON formatting with extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.request_id = "req-123"
        record.user_id = "user-456"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["request_id"] == "req-123"
        assert data["user_id"] == "user-456"


class TestContextFilter:
    """Test ContextFilter class."""

    def test_filter_adds_request_id(self):
        """Test filter adds request_id to record."""
        filter = ContextFilter(request_id="test-123")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = filter.filter(record)
        assert result is True
        assert record.request_id == "test-123"

    def test_filter_generates_request_id(self):
        """Test filter generates request_id if not provided."""
        filter = ContextFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = filter.filter(record)
        assert result is True
        assert hasattr(record, "request_id")
        assert len(record.request_id) > 0

    def test_filter_preserves_existing_request_id(self):
        """Test filter preserves existing request_id."""
        filter = ContextFilter(request_id="new-123")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.request_id = "existing-456"

        result = filter.filter(record)
        assert result is True
        assert record.request_id == "existing-456"


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_basic(self):
        """Test basic logging setup."""
        config = LogConfig()
        setup_logging(config)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 1

        # Check console handler
        console_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break

        assert console_handler is not None

    def test_setup_with_file(self):
        """Test logging setup with file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            config = LogConfig(log_file=log_file)
            setup_logging(config)

            root_logger = logging.getLogger()

            # Check file handler
            file_handler = None
            for handler in root_logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                    break

            assert file_handler is not None
            assert file_handler.baseFilename == str(log_file)

    def test_setup_json_format(self):
        """Test logging setup with JSON format."""
        config = LogConfig(format=LogFormat.JSON)
        setup_logging(config)

        root_logger = logging.getLogger()

        # Check formatter
        for handler in root_logger.handlers:
            assert isinstance(handler.formatter, JSONFormatter)

    def test_setup_without_console(self):
        """Test logging setup without console handler."""
        config = LogConfig(console_enabled=False)
        setup_logging(config)

        root_logger = logging.getLogger()

        # Check no console handler
        console_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break

        assert console_handler is None

    def test_setup_with_context(self):
        """Test logging setup with context filter."""
        config = LogConfig(add_context=True, request_id="test-123")
        setup_logging(config)

        root_logger = logging.getLogger()

        # Check filter
        assert len(root_logger.filters) >= 1
        context_filter = root_logger.filters[0]
        assert isinstance(context_filter, ContextFilter)
        assert context_filter.request_id == "test-123"


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_inherits_configuration(self):
        """Test logger inherits root configuration."""
        config = LogConfig(level=LogLevel.DEBUG)
        setup_logging(config)

        logger = get_logger("test.module")
        assert logger.level == logging.NOTSET  # Inherits from root
        assert logger.getEffectiveLevel() == logging.DEBUG


if __name__ == "__main__":
    pytest.main([__file__])
