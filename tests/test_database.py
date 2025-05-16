"""Tests for TILDatabase class."""

import sqlite3
from pathlib import Path

import pytest
import sqlite_utils

from til.database import TILDatabase


def test_til_database_initialization(temp_dir: Path) -> None:
    """Test TILDatabase initialization."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    assert til_db.db_path == db_path
    assert isinstance(til_db.db, sqlite_utils.Database)
    assert db_path.exists()


def test_get_table(temp_dir: Path) -> None:
    """Test getting the til table."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Use the upsert_record method which sets the primary key correctly
    til_db.upsert_record({"path": "test.md", "title": "Test"})

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
    record = {
        "path": "test.md",
        "title": "Test",
        "body": "Content",
        "topic": "testing",
    }
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
    record = {
        "path": "test.md",
        "title": "Test",
        "body": "Content",
        "html": "<p>Content</p>",
    }
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
    til_db.upsert_record(
        {
            "path": "test1.md",
            "title": "Test 1",
            "body": "Content 1",
            "topic": "testing",
        }
    )
    til_db.upsert_record(
        {
            "path": "test2.md",
            "title": "Test 2",
            "body": "Content 2",
            "topic": "testing",
        }
    )

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
    til_db.upsert_record(
        {
            "path": "python/test1.md",
            "title": "Python Test 1",
            "topic": "python",
            "created_utc": "2023-01-01T00:00:00+00:00",
        }
    )
    til_db.upsert_record(
        {
            "path": "python/test2.md",
            "title": "Python Test 2",
            "topic": "python",
            "created_utc": "2023-01-02T00:00:00+00:00",
        }
    )
    til_db.upsert_record(
        {
            "path": "javascript/test1.md",
            "title": "JS Test",
            "topic": "javascript",
            "created_utc": "2023-01-03T00:00:00+00:00",
        }
    )

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
    til_db.upsert_record({"path": "test1.md", "title": "Test 1"})
    assert til_db.count() == 1

    til_db.upsert_record({"path": "test2.md", "title": "Test 2"})
    assert til_db.count() == 2


def test_table_exists(temp_dir: Path) -> None:
    """Test checking if table exists."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Initially no table
    assert not til_db.table_exists()

    # Create table
    til_db.upsert_record({"path": "test.md", "title": "Test"})
    assert til_db.table_exists()


def test_close(temp_dir: Path) -> None:
    """Test closing database connection."""
    db_path = temp_dir / "test.db"
    til_db = TILDatabase(db_path)

    # Add a record
    til_db.upsert_record({"path": "test.md", "title": "Test"})

    # Close connection
    til_db.close()

    # Verify database file still exists
    assert db_path.exists()

    # Try to use the database after closing (should fail)
    with pytest.raises(sqlite3.ProgrammingError):
        til_db.db["til"].count
