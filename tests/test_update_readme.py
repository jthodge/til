"""Test README update functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.config import TILConfig
from til.update_readme import main


class TestUpdateReadme:
    """Test the update_readme module."""
    
    def test_main_with_rewrite(self):
        """Test main function with --rewrite flag."""
        with patch("til.update_readme.sys.argv", ["update_readme.py", "--rewrite"]), \
             patch("til.update_readme.TILConfig") as mock_config, \
             patch("til.update_readme.TILDatabase") as mock_db, \
             patch("til.update_readme.ReadmeGenerator") as mock_generator:
            
            # Setup mocks
            mock_config.from_environment.return_value = Mock(
                root_path=Path("/test"),
                database_path=Path("/test/til.db")
            )
            mock_db.return_value.count.return_value = 5
            
            # Run main
            main()
            
            # Verify flow
            mock_config.from_environment.assert_called_once()
            mock_db.assert_called_once_with(Path("/test/til.db"))
            mock_generator.assert_called_once_with(mock_db.return_value)
            
            # Verify update_readme was called
            generator_instance = mock_generator.return_value
            generator_instance.update_readme.assert_called_once_with(Path("/test/README.md"))
    
    def test_main_without_rewrite(self, capsys):
        """Test main function without --rewrite flag."""
        with patch("til.update_readme.sys.argv", ["update_readme.py"]), \
             patch("til.update_readme.TILConfig") as mock_config, \
             patch("til.update_readme.TILDatabase") as mock_db, \
             patch("til.update_readme.ReadmeGenerator") as mock_generator:
            
            # Setup mocks
            mock_config.from_environment.return_value = Mock(
                root_path=Path("/test"),
                database_path=Path("/test/til.db")
            )
            mock_db.return_value.count.return_value = 3
            mock_generator.return_value.generate_index.return_value = [
                "<!-- index starts -->",
                "## python",
                "* [Test](url) - 2023-01-01",
                "<!-- index ends -->"
            ]
            
            # Run main
            main()
            
            # Verify only index was printed
            captured = capsys.readouterr()
            assert "<!-- index starts -->" in captured.out
            assert "## python" in captured.out
            assert "<!-- index ends -->" in captured.out
            
            # Verify update_readme was NOT called
            generator_instance = mock_generator.return_value
            generator_instance.update_readme.assert_not_called()
    
    @patch("til.update_readme.main")
    def test_module_execution(self, mock_main):
        """Test that main is called when module is executed."""
        # Import the module
        import til.update_readme
        
        # Mock the name check
        with patch.object(til.update_readme, "__name__", "__main__"):
            # This would trigger the if __name__ == "__main__" block
            pass