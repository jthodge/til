"""Test database building functionality."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import sqlite_utils
from git import Repo

from til.build_db import build_database
from til.config import TILConfig


class TestBuildDatabase:
    """Test the build_database function."""

    def test_build_database(self, temp_dir: Path):
        """Test that build_database creates a TILProcessor and calls build_database."""
        config = TILConfig(root_path=temp_dir)
        
        with patch("til.build_db.TILProcessor") as mock_processor:
            build_database(config)
            
            # Verify TILProcessor was instantiated with config
            mock_processor.assert_called_once_with(config)
            
            # Verify build_database was called on the processor
            mock_processor.return_value.build_database.assert_called_once()
    
    def test_main(self):
        """Test the main entry point."""
        with patch("til.build_db.TILConfig") as mock_config, \
             patch("til.build_db.build_database") as mock_build:
            
            mock_config.from_environment.return_value = Mock()
            
            # Import main and call it
            from til.build_db import main
            main()
            
            # Verify config was created from environment
            mock_config.from_environment.assert_called_once()
            
            # Verify build_database was called with the config
            mock_build.assert_called_once_with(mock_config.from_environment.return_value)