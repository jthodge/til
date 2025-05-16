"""Tests for ReadmeGenerator class."""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from til.database import TILDatabase
from til.readme_generator import ReadmeGenerator


def test_readme_generator_initialization():
    """Test ReadmeGenerator initialization."""
    mock_db = Mock(spec=TILDatabase)
    generator = ReadmeGenerator(mock_db)
    
    assert generator.database == mock_db


def test_generate_index_empty():
    """Test generating index for empty database."""
    mock_db = Mock(spec=TILDatabase)
    mock_db.get_all_by_topic.return_value = {}
    
    generator = ReadmeGenerator(mock_db)
    index = generator.generate_index()
    
    assert index[0] == "<!-- index starts -->"
    assert index[-1] == "<!-- index ends -->"
    assert len(index) == 2  # Just the markers


def test_generate_index_with_entries():
    """Test generating index with multiple entries."""
    mock_db = Mock(spec=TILDatabase)
    mock_db.get_all_by_topic.return_value = {
        "python": [
            {
                "title": "Python Test 1",
                "url": "https://github.com/test/python/test1.md",
                "created": "2023-01-01T00:00:00",
            },
            {
                "title": "Python Test 2",
                "url": "https://github.com/test/python/test2.md",
                "created": "2023-01-02T00:00:00",
            },
        ],
        "bash": [
            {
                "title": "Bash Test",
                "url": "https://github.com/test/bash/test.md",
                "created": "2023-01-03T00:00:00",
            },
        ],
    }
    
    generator = ReadmeGenerator(mock_db)
    index = generator.generate_index()
    
    # Check structure
    assert "<!-- index starts -->" in index
    assert "<!-- index ends -->" in index
    
    # Join the index to check for the headers
    index_text = " ".join(index)
    assert "## bash" in index_text
    assert "## python" in index_text
    
    # Check entries
    assert "* [Python Test 1]" in " ".join(index)
    assert "* [Python Test 2]" in " ".join(index)
    assert "* [Bash Test]" in " ".join(index)
    
    # Check dates are included
    assert "2023-01-01" in " ".join(index)
    assert "2023-01-02" in " ".join(index)
    assert "2023-01-03" in " ".join(index)


def test_generate_index_sorted_by_topic():
    """Test that index is sorted by topic name."""
    mock_db = Mock(spec=TILDatabase)
    mock_db.get_all_by_topic.return_value = {
        "zsh": [{"title": "ZSH Test", "url": "url", "created": "2023-01-01T00:00:00"}],
        "ansible": [{"title": "Ansible Test", "url": "url", "created": "2023-01-01T00:00:00"}],
    }
    
    generator = ReadmeGenerator(mock_db)
    index = generator.generate_index()
    
    # Topics should be sorted alphabetically
    topics = [line.strip() for line in index if line.startswith("##")]
    assert topics == ["## ansible", "## zsh"]


def test_update_readme(temp_dir):
    """Test updating README file."""
    mock_db = Mock(spec=TILDatabase)
    mock_db.get_all_by_topic.return_value = {
        "python": [
            {
                "title": "Test",
                "url": "https://github.com/test/python/test.md",
                "created": "2023-01-01T00:00:00",
            }
        ]
    }
    mock_db.count.return_value = 1
    
    # Create test README
    readme_path = temp_dir / "README.md"
    readme_path.write_text("""# TIL

This is my collection of TILs.

<!-- count starts -->0<!-- count ends -->

## Index

<!-- index starts -->
Old content
<!-- index ends -->

## Footer

Thank you!
""")
    
    generator = ReadmeGenerator(mock_db)
    generator.update_readme(readme_path)
    
    # Read updated README
    updated_content = readme_path.read_text()
    
    # Check count was updated
    assert "<!-- count starts -->1<!-- count ends -->" in updated_content
    
    # Check index was updated
    assert "## python" in updated_content
    assert "* [Test]" in updated_content
    assert "2023-01-01" in updated_content
    
    # Check other content preserved
    assert "# TIL" in updated_content
    assert "## Footer" in updated_content
    assert "Thank you!" in updated_content


def test_update_readme_io_error(temp_dir):
    """Test handling of I/O errors."""
    mock_db = Mock(spec=TILDatabase)
    # Need to mock get_all_by_topic since it gets called
    mock_db.get_all_by_topic.return_value = {}
    
    # Non-existent file
    readme_path = temp_dir / "nonexistent.md"
    
    with patch("til.readme_generator.logger") as mock_logger:
        generator = ReadmeGenerator(mock_db)
        generator.update_readme(readme_path)
        
        # Should log error for failed read
        mock_logger.error.assert_called()


def test_update_readme_missing_markers(temp_dir):
    """Test handling README without proper markers."""
    mock_db = Mock(spec=TILDatabase)
    mock_db.get_all_by_topic.return_value = {}
    mock_db.count.return_value = 0
    
    # Create README without markers
    readme_path = temp_dir / "README.md"
    readme_path.write_text("# TIL\n\nSimple content without markers.")
    
    generator = ReadmeGenerator(mock_db)
    generator.update_readme(readme_path)
    
    # Content should remain unchanged if markers not found
    content = readme_path.read_text()
    assert content == "# TIL\n\nSimple content without markers."