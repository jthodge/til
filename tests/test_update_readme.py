"""Test README update functionality."""

from pathlib import Path

import pytest
import sqlite_utils

from til.config import TILConfig
from til.update_readme import build_index, update_readme_file


class TestBuildIndex:
    """Test index building from database."""
    
    def test_build_index_empty_database(self, temp_db: sqlite_utils.Database):
        """Test building index from empty database."""
        # Create empty til table with all required columns
        temp_db["til"].create({
            "path": str,
            "topic": str, 
            "title": str,
            "url": str,
            "created": str,
            "created_utc": str
        })
        
        index = build_index(temp_db)
        
        assert index[0] == "<!-- index starts -->"
        assert index[-1] == "<!-- index ends -->"
        assert len(index) == 2  # Just the markers
    
    def test_build_index_with_entries(self, temp_db: sqlite_utils.Database):
        """Test building index with multiple entries."""
        # Create til table with sample data
        temp_db["til"].insert_all([
            {
                "path": "python_test1.md",
                "topic": "python",
                "title": "Python Test 1",
                "url": "https://github.com/user/repo/blob/main/python/test1.md",
                "created": "2023-01-01T10:00:00",
                "created_utc": "2023-01-01T10:00:00+00:00"
            },
            {
                "path": "python_test2.md",
                "topic": "python",
                "title": "Python Test 2",
                "url": "https://github.com/user/repo/blob/main/python/test2.md",
                "created": "2023-01-02T10:00:00",
                "created_utc": "2023-01-02T10:00:00+00:00"
            },
            {
                "path": "bash_test.md",
                "topic": "bash",
                "title": "Bash Test",
                "url": "https://github.com/user/repo/blob/main/bash/test.md",
                "created": "2023-01-03T10:00:00",
                "created_utc": "2023-01-03T10:00:00+00:00"
            }
        ])
        
        index = build_index(temp_db)
        
        # Check structure
        assert "<!-- index starts -->" in index
        assert "<!-- index ends -->" in index
        
        # Join the index to check for the headers (they include newlines)
        index_text = " ".join(index)
        assert "## python" in index_text
        assert "## bash" in index_text
        
        # Check entries
        assert "* [Python Test 1]" in " ".join(index)
        assert "* [Python Test 2]" in " ".join(index)
        assert "* [Bash Test]" in " ".join(index)
        
        # Check dates are included
        assert "2023-01-01" in " ".join(index)
        assert "2023-01-02" in " ".join(index)
        assert "2023-01-03" in " ".join(index)
    
    def test_build_index_sorted_by_topic(self, temp_db: sqlite_utils.Database):
        """Test that index is sorted by topic name."""
        # Create entries in reverse alphabetical order
        temp_db["til"].insert_all([
            {
                "path": "zsh_test.md",
                "topic": "zsh",
                "title": "ZSH Test",
                "url": "https://example.com",
                "created": "2023-01-01T00:00:00",
                "created_utc": "2023-01-01T00:00:00+00:00"
            },
            {
                "path": "ansible_test.md",
                "topic": "ansible",
                "title": "Ansible Test",
                "url": "https://example.com",
                "created": "2023-01-01T00:00:00",
                "created_utc": "2023-01-01T00:00:00+00:00"
            }
        ])
        
        index = build_index(temp_db)
        index_text = "\n".join(index)
        
        # Ansible should come before zsh
        ansible_pos = index_text.find("## ansible")
        zsh_pos = index_text.find("## zsh")
        assert ansible_pos < zsh_pos
    
    def test_build_index_entries_sorted_by_date(self, temp_db: sqlite_utils.Database):
        """Test that entries within a topic are sorted by creation date."""
        # Create entries out of chronological order
        temp_db["til"].insert_all([
            {
                "path": "python_new.md",
                "topic": "python",
                "title": "Newer Entry",
                "url": "https://example.com",
                "created": "2023-01-10T00:00:00",
                "created_utc": "2023-01-10T00:00:00+00:00"
            },
            {
                "path": "python_old.md",
                "topic": "python",
                "title": "Older Entry",
                "url": "https://example.com",
                "created": "2023-01-01T00:00:00",
                "created_utc": "2023-01-01T00:00:00+00:00"
            }
        ])
        
        index = build_index(temp_db)
        index_text = "\n".join(index)
        
        # Older entry should come first
        older_pos = index_text.find("Older Entry")
        newer_pos = index_text.find("Newer Entry")
        assert older_pos < newer_pos


class TestUpdateReadmeFile:
    """Test README file updates."""
    
    @pytest.fixture
    def sample_readme(self, temp_dir: Path) -> Path:
        """Create a sample README file."""
        readme_path = temp_dir / "README.md"
        readme_content = """# TIL

My Today I Learned repository.

<!-- count starts -->0<!-- count ends -->

<!-- index starts -->
## Old Topic

* [Old Entry](https://example.com) - 2020-01-01
<!-- index ends -->

## Footer
Some footer content.
"""
        readme_path.write_text(readme_content)
        return readme_path
    
    def test_update_readme_file(self, sample_readme: Path):
        """Test updating README with new index and count."""
        new_index = [
            "<!-- index starts -->",
            "## python",
            "",
            "* [Test Entry](https://example.com) - 2023-01-01",
            "<!-- index ends -->"
        ]
        
        update_readme_file(sample_readme, new_index, 42)
        
        content = sample_readme.read_text()
        
        # Check count was updated
        assert "<!-- count starts -->42<!-- count ends -->" in content
        
        # Check index was replaced
        assert "## python" in content
        assert "Test Entry" in content
        assert "## Old Topic" not in content
        assert "Old Entry" not in content
        
        # Check footer is preserved
        assert "## Footer" in content
        assert "Some footer content." in content
    
    def test_update_readme_missing_markers(self, temp_dir: Path):
        """Test updating README with missing markers."""
        readme_path = temp_dir / "README.md"
        readme_path.write_text("# TIL\n\nNo markers here.")
        
        new_index = ["<!-- index starts -->", "## Test", "<!-- index ends -->"]
        
        # Should not crash, but content won't be updated
        update_readme_file(readme_path, new_index, 5)
        
        content = readme_path.read_text()
        assert "No markers here." in content
    
    def test_update_readme_nonexistent_file(self, temp_dir: Path):
        """Test handling of nonexistent README file."""
        nonexistent = temp_dir / "nonexistent.md"
        new_index = ["<!-- index starts -->", "<!-- index ends -->"]
        
        # Should not crash
        update_readme_file(nonexistent, new_index, 0)
        
        assert not nonexistent.exists()
    
    def test_update_readme_preserves_content_outside_markers(self, sample_readme: Path):
        """Test that content outside markers is preserved."""
        # Add content before and after index
        original = sample_readme.read_text()
        new_content = original.replace(
            "<!-- index starts -->",
            "Some content before\n<!-- index starts -->"
        ).replace(
            "<!-- index ends -->",
            "<!-- index ends -->\nSome content after"
        )
        sample_readme.write_text(new_content)
        
        new_index = [
            "<!-- index starts -->",
            "## New Index",
            "<!-- index ends -->"
        ]
        
        update_readme_file(sample_readme, new_index, 1)
        
        content = sample_readme.read_text()
        assert "Some content before" in content
        assert "Some content after" in content
        assert "## New Index" in content