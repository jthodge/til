"""Configuration file loader for TIL application."""

import os
from pathlib import Path
from typing import Any, Optional

from .config import TILConfig
from .exceptions import ConfigurationError
from .logging_config import LogConfig, LogFormat, LogLevel


class ConfigLoader:
    """Loads configuration from files and environment."""

    DEFAULT_CONFIG_FILES = [
        "til.yaml",
        "til.yml",
        ".til.yaml",
        ".til.yml",
        "til.toml",
        ".til.toml",
    ]

    @classmethod
    def load_config(
        cls,
        config_file: Optional[Path] = None,
        github_token: Optional[str] = None,
        github_repo: Optional[str] = None,
        database_name: Optional[str] = None,
        root_path: Optional[Path] = None,
    ) -> TILConfig:
        """Load configuration from file, environment, and CLI arguments.

        Priority order (highest to lowest):
        1. CLI arguments
        2. Environment variables
        3. Configuration file
        4. Defaults

        Args:
            config_file: Path to configuration file
            github_token: GitHub API token
            github_repo: GitHub repository (owner/repo)
            database_name: Database file name
            root_path: Root directory path

        Returns:
            Validated TILConfig instance

        Raises:
            ConfigurationError: If configuration is invalid

        """
        # Start with defaults
        config_dict: dict[str, Any] = {}

        # Load from configuration file if exists
        if config_file:
            config_dict.update(cls._load_config_file(config_file))
        else:
            # Try to find a config file
            for filename in cls.DEFAULT_CONFIG_FILES:
                path = Path(filename)
                if path.exists() and path.is_file():
                    config_dict.update(cls._load_config_file(path))
                    break

        # Override with environment variables
        env_config = cls._load_from_environment()
        config_dict.update(env_config)

        # Override with CLI arguments
        if github_token is not None:
            config_dict["github_token"] = github_token
        if github_repo is not None:
            config_dict["github_repo"] = github_repo
        if database_name is not None:
            config_dict["database_name"] = database_name
        if root_path is not None:
            config_dict["root_path"] = root_path

        # Extract logging configuration
        log_config = cls._load_log_config(config_dict)
        if log_config:
            config_dict["log_config"] = log_config
        else:
            # Use environment-based config if no file config
            config_dict["log_config"] = LogConfig.from_environment()

        # Set default root_path if not provided
        if "root_path" not in config_dict or config_dict["root_path"] is None:
            config_dict["root_path"] = Path.cwd()

        # Create and validate config
        return TILConfig(**config_dict)

    @classmethod
    def _load_config_file(cls, file_path: Path) -> dict[str, Any]:
        """Load configuration from YAML or TOML file.

        Args:
            file_path: Path to configuration file

        Returns:
            Dictionary of configuration values

        Raises:
            ConfigurationError: If file cannot be loaded

        """
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            return cls._load_yaml(file_path)
        if suffix == ".toml":
            return cls._load_toml(file_path)
        raise ConfigurationError(
            f"Unsupported configuration file format: {suffix}. "
            "Supported formats: .yaml, .yml, .toml"
        )

    @classmethod
    def _load_yaml(cls, file_path: Path) -> dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ConfigurationError(
                "PyYAML is required to read YAML configuration files. "
                "Install it with: uv add pyyaml"
            )

        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigurationError(
                        f"Invalid YAML configuration: expected dictionary, got {type(data).__name__}"
                    )
                return cls._normalize_config(data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to read configuration file: {e}")

    @classmethod
    def _load_toml(cls, file_path: Path) -> dict[str, Any]:
        """Load configuration from TOML file."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[import-not-found]
            except ImportError:
                raise ConfigurationError(
                    "TOML support requires Python 3.11+ or tomli package. "
                    "Install tomli with: uv add tomli"
                )

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
                # Look for a [til] section or use root
                config_data = data.get("til", data)
                return cls._normalize_config(config_data)
        except Exception as e:
            raise ConfigurationError(f"Failed to read TOML configuration: {e}")

    @classmethod
    def _load_log_config(cls, data: dict[str, Any]) -> Optional[LogConfig]:
        """Extract and parse logging configuration from config data.

        Args:
            data: Configuration dictionary

        Returns:
            LogConfig instance or None if no logging config found
        """
        log_data = data.get("logging", {})
        if not log_data:
            return None

        # Parse log level
        level = LogLevel.INFO
        if "level" in log_data:
            try:
                level = LogLevel(log_data["level"].upper())
            except (ValueError, AttributeError):
                pass

        # Parse log format
        format = LogFormat.TEXT
        if "format" in log_data:
            try:
                format = LogFormat(log_data["format"].lower())
            except (ValueError, AttributeError):
                pass

        # Parse log file
        log_file = None
        if "file" in log_data and log_data["file"]:
            log_file = Path(log_data["file"])

        return LogConfig(
            level=level,
            format=format,
            log_file=log_file,
            max_bytes=log_data.get("max_bytes", 10 * 1024 * 1024),
            backup_count=log_data.get("backup_count", 5),
            console_enabled=log_data.get("console_enabled", True),
            add_context=log_data.get("add_context", True),
        )

    @classmethod
    def _normalize_config(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize configuration keys and values.

        Converts keys from snake_case and kebab-case to snake_case.
        Converts path strings to Path objects.

        Args:
            data: Raw configuration dictionary

        Returns:
            Normalized configuration dictionary

        """
        normalized: dict[str, Any] = {}

        for key, value in data.items():
            # Normalize key (kebab-case to snake_case)
            normalized_key = key.replace("-", "_")

            # Convert path strings to Path objects
            if normalized_key == "root_path" and isinstance(value, str):
                normalized[normalized_key] = Path(value)
            else:
                normalized[normalized_key] = value

        return normalized

    @classmethod
    def _load_from_environment(cls) -> dict[str, Any]:
        """Load configuration from environment variables.

        Returns:
            Dictionary of configuration values from environment

        """
        config: dict[str, Any] = {}

        # GitHub token
        if token := os.environ.get("MARKDOWN_GITHUB_TOKEN"):
            config["github_token"] = token

        # GitHub repository
        if repo := os.environ.get("TIL_GITHUB_REPO"):
            config["github_repo"] = repo

        # Database name
        if db_name := os.environ.get("TIL_DATABASE_NAME"):
            config["database_name"] = db_name

        # Root path
        if root := os.environ.get("TIL_ROOT_PATH"):
            config["root_path"] = Path(root)

        return config
