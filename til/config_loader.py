"""Configuration file loader for TIL application."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from .config import TILConfig
from .exceptions import ConfigurationError


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
        config_dict: Dict[str, Any] = {}

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

        # Set default root_path if not provided
        if "root_path" not in config_dict or config_dict["root_path"] is None:
            config_dict["root_path"] = Path.cwd()

        # Create and validate config
        return TILConfig(**config_dict)

    @classmethod
    def _load_config_file(cls, file_path: Path) -> Dict[str, Any]:
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
        elif suffix == ".toml":
            return cls._load_toml(file_path)
        else:
            raise ConfigurationError(
                f"Unsupported configuration file format: {suffix}. "
                "Supported formats: .yaml, .yml, .toml"
            )

    @classmethod
    def _load_yaml(cls, file_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ConfigurationError(
                "PyYAML is required to read YAML configuration files. "
                "Install it with: pip install pyyaml"
            )

        try:
            with open(file_path, "r") as f:
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
    def _load_toml(cls, file_path: Path) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                raise ConfigurationError(
                    "TOML support requires Python 3.11+ or tomli package. "
                    "Install tomli with: pip install tomli"
                )

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
                # Look for a [til] section or use root
                if "til" in data:
                    config_data = data["til"]
                else:
                    config_data = data
                return cls._normalize_config(config_data)
        except Exception as e:
            raise ConfigurationError(f"Failed to read TOML configuration: {e}")

    @classmethod
    def _normalize_config(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize configuration keys and values.

        Converts keys from snake_case and kebab-case to snake_case.
        Converts path strings to Path objects.

        Args:
            data: Raw configuration dictionary

        Returns:
            Normalized configuration dictionary
        """
        normalized: Dict[str, Any] = {}

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
    def _load_from_environment(cls) -> Dict[str, Any]:
        """Load configuration from environment variables.

        Returns:
            Dictionary of configuration values from environment
        """
        config: Dict[str, Any] = {}

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
