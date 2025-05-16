"""Tests for TILDatabase class."""

import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest
import sqlite_utils

from til.database import TILDatabase
from til.exceptions import DatabaseError


def test_til_database_initialization(temp_dir: Path) -> None:
    """Test TILDatabase initialization."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    assert til_db.db_path == db_path
    assert isinstance(til_db.db, sqlite_utils.Database)
    assert db_path.exists()


# Helper function to create a complete record
def create_test_record(path: str = "test.md") -> Dict[str, Any]:
    """Create a complete test record with all required fields."""
    return {
        "path": path,
        "slug": "test",
        "topic": "testing",
        "title": "Test",
        "body": "Content",
        "url": "http://example.com",
        "html": "<p>Content</p>",
    }


def test_get_table(temp_dir: Path) -> None:
    """Test getting the til table."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Use the upsert_record method which sets the primary key correctly
    til_db.upsert_record(create_test_record())

    table = til_db.get_table()
    assert isinstance(table, sqlite_utils.db.Table)
    assert table.name == "til"
    # The table should have path as primary key
    assert table.pks == ["path"]


def test_upsert_record(temp_dir: Path) -> None:
    """Test inserting and updating records."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Insert new record
    record = create_test_record()
    til_db.upsert_record(record)

    # Verify insertion
    rows = list(til_db.db["til"].rows)
    assert len(rows) == 1
    assert rows[0]["title"] == "Test"

    # Update existing record
    record["title"] = "Updated Test"
    til_db.upsert_record(record)

    # Verify update
    rows = list(til_db.db["til"].rows)
    assert len(rows) == 1
    assert rows[0]["title"] == "Updated Test"


def test_get_previous_record(temp_dir: Path) -> None:
    """Test retrieving previous record."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # No previous record
    prev = til_db.get_previous_record("test.md")
    assert prev is None

    # Insert a record
    record = create_test_record()
    til_db.upsert_record(record)

    # Get previous record
    prev = til_db.get_previous_record("test.md")
    assert prev is not None
    assert prev["title"] == "Test"
    assert prev["html"] == "<p>Content</p>"


def test_enable_search(temp_dir: Path) -> None:
    """Test enabling full-text search."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Enable search on empty database (should skip)
    til_db.enable_search()
    assert "til_fts" not in til_db.db.table_names()

    # Add some records
    record1 = create_test_record("test1.md")
    record1["title"] = "Test 1"
    record1["body"] = "Content 1"
    til_db.upsert_record(record1)

    record2 = create_test_record("test2.md")
    record2["title"] = "Test 2"
    record2["body"] = "Content 2"
    til_db.upsert_record(record2)

    # Enable search
    til_db.enable_search()
    assert "til_fts" in til_db.db.table_names()

    # Verify FTS works
    til_table = til_db.db["til"]
    if hasattr(til_table, "search"):
        results = list(til_table.search("Content"))
    assert len(results) == 2


def test_get_all_by_topic(temp_dir: Path) -> None:
    """Test getting records grouped by topic."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Empty database
    by_topic = til_db.get_all_by_topic()
    assert by_topic == {}

    # Add records in different topics
    record1 = create_test_record("python/test1.md")
    record1.update(
        {
            "title": "Python Test 1",
            "slug": "test1",
            "topic": "python",
            "created_utc": "2023-01-01T00:00:00+00:00",
        }
    )
    til_db.upsert_record(record1)

    record2 = create_test_record("python/test2.md")
    record2.update(
        {
            "title": "Python Test 2",
            "slug": "test2",
            "topic": "python",
            "created_utc": "2023-01-02T00:00:00+00:00",
        }
    )
    til_db.upsert_record(record2)

    record3 = create_test_record("javascript/test1.md")
    record3.update(
        {
            "title": "JS Test",
            "slug": "test1",
            "topic": "javascript",
            "created_utc": "2023-01-03T00:00:00+00:00",
        }
    )
    til_db.upsert_record(record3)

    by_topic = til_db.get_all_by_topic()

    assert len(by_topic) == 2
    assert "python" in by_topic
    assert "javascript" in by_topic
    assert len(by_topic["python"]) == 2
    assert len(by_topic["javascript"]) == 1
    assert by_topic["python"][0]["title"] == "Python Test 1"


def test_count(temp_dir: Path) -> None:
    """Test counting records."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Empty database
    assert til_db.count() == 0

    # Add records
    til_db.upsert_record(create_test_record("test1.md"))
    assert til_db.count() == 1

    til_db.upsert_record(create_test_record("test2.md"))
    assert til_db.count() == 2


def test_error_handling(temp_dir: Path) -> None:
    """Test error handling scenarios."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Test empty record
    with pytest.raises(DatabaseError, match="Cannot save empty record"):
        til_db.upsert_record({})

    # Test missing required fields
    with pytest.raises(DatabaseError, match="missing required fields"):
        til_db.upsert_record({"path": "test", "title": "Test"})

    # Test empty path
    with pytest.raises(DatabaseError, match="Path cannot be empty"):
        til_db.get_previous_record("")


def test_close(temp_dir: Path) -> None:
    """Test closing database connection."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Add a record
    til_db.upsert_record(create_test_record())

    # Close connection
    til_db.close()

    # Verify database file still exists
    assert db_path.exists()
