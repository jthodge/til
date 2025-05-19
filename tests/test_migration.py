"""Test migration scripts for deduplication."""

import pathlib
import sqlite3
import tempfile
from collections.abc import Generator
from typing import Optional, Union
from unittest.mock import patch

import pytest

from til.cleanup_old_entries import cleanup_old_entries
from til.database import TILDatabase
from til.migrate_timestamps import migrate_timestamps
from til.production_safe_migration import ProductionMigration
from til.readme_generator import ReadmeGenerator
from til.remove_duplicates import remove_duplicates


@pytest.fixture
def test_db_with_duplicates() -> Generator[pathlib.Path, None, None]:
    """Create a test database with duplicate entries."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = pathlib.Path(tmp.name)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE til (
            path TEXT PRIMARY KEY,
            slug TEXT,
            topic TEXT,
            title TEXT,
            body TEXT,
            html TEXT,
            created TEXT,
            created_utc TEXT,
            updated TEXT,
            updated_utc TEXT,
            url TEXT
        )
    ''')

    # Insert old-style entries
    old_entries = [
        ('bash_test-entry.md', 'test-entry', 'bash', 'Test Entry', 'Body', '<p>Body</p>',
         '2020-01-01T00:00:00', '2020-01-01T00:00:00', '2020-01-01T00:00:00', '2020-01-01T00:00:00',
         'https://github.com/jthodge/til/blob/main/bash/test-entry.md'),
        ('python_another-test.md', 'another-test', 'python', 'Another Test', 'Body 2', '<p>Body 2</p>',
         '2021-01-01T00:00:00', '2021-01-01T00:00:00', '2021-01-01T00:00:00', '2021-01-01T00:00:00',
         'https://github.com/jthodge/til/blob/main/python/another-test.md'),
    ]

    # Insert new-style entries (duplicates)
    new_entries: list[tuple[str, str, str, str, str, str, Optional[str], Optional[str], Optional[str], Optional[str], str]] = [
        ('content_bash_test-entry.md', 'test-entry', 'bash', 'Test Entry', 'Body', '<p>Body</p>',
         None, None, None, None,
         'https://github.com/jthodge/til/blob/main/content/bash/test-entry.md'),
        ('content_python_another-test.md', 'another-test', 'python', 'Another Test', 'Body 2', '<p>Body 2</p>',
         None, None, None, None,
         'https://github.com/jthodge/til/blob/main/content/python/another-test.md'),
    ]

    all_entries: list[tuple[str, str, str, str, str, str, Optional[str], Optional[str], Optional[str], Optional[str], str]] = []
    all_entries.extend(old_entries)  # type: ignore[arg-type]
    all_entries.extend(new_entries)
    cursor.executemany('INSERT INTO til VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', all_entries)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_readme_generator_handles_null_timestamps(test_db_with_duplicates: pathlib.Path) -> None:
    """Test that README generator handles entries with null timestamps."""
    db = TILDatabase(test_db_with_duplicates)
    generator = ReadmeGenerator(db)

    # This should not raise an exception even with null timestamps
    index_lines = generator.generate_index()

    # Check that we have content
    assert len(index_lines) > 0

    # Check that entries without dates are still included
    content = '\n'.join(index_lines)
    assert 'Test Entry' in content
    assert 'Another Test' in content


def test_migrate_timestamps(test_db_with_duplicates: pathlib.Path) -> None:
    """Test timestamp migration."""
    migrate_timestamps(test_db_with_duplicates)

    # Check that timestamps were migrated
    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()

    cursor.execute("SELECT created FROM til WHERE path = 'content_bash_test-entry.md'")
    result = cursor.fetchone()
    assert result[0] == '2020-01-01T00:00:00'

    conn.close()


def test_cleanup_old_entries(test_db_with_duplicates: pathlib.Path) -> None:
    """Test cleanup of old entries."""
    cleanup_old_entries(test_db_with_duplicates)

    # Check that old entries were removed
    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM til WHERE path NOT LIKE 'content_%'")
    count = cursor.fetchone()[0]
    assert count == 0

    conn.close()


def test_remove_duplicates(test_db_with_duplicates: pathlib.Path) -> None:
    """Test duplicate removal with timestamp preservation."""
    remove_duplicates(test_db_with_duplicates)

    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()

    # Check no duplicates remain
    cursor.execute("""
        SELECT slug, topic, COUNT(*) as count
        FROM til
        GROUP BY slug, topic
        HAVING count > 1
    """)
    duplicates = cursor.fetchall()
    assert len(duplicates) == 0

    # Check timestamps were preserved
    cursor.execute("SELECT created FROM til WHERE path = 'content_bash_test-entry.md'")
    result = cursor.fetchone()
    assert result[0] == '2020-01-01T00:00:00'

    conn.close()


def test_production_migration(test_db_with_duplicates: pathlib.Path) -> None:
    """Test production-safe migration."""
    migration = ProductionMigration(test_db_with_duplicates)

    # Mock input to not keep backup
    with patch('builtins.input', return_value='n'):
        success = migration.run()

    assert success

    # Verify no duplicates
    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT slug, topic, COUNT(*) as count
        FROM til
        GROUP BY slug, topic
        HAVING count > 1
    """)
    duplicates = cursor.fetchall()
    assert len(duplicates) == 0

    conn.close()


def test_production_migration_rollback(test_db_with_duplicates: pathlib.Path) -> None:
    """Test production migration rollback on failure."""

    class FailingMigration(ProductionMigration):
        def validate_migration(self) -> bool:
            # Force validation to fail
            return False

    # Get original count
    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM til")
    original_count = cursor.fetchone()[0]
    conn.close()

    migration = FailingMigration(test_db_with_duplicates)
    success = migration.run()

    assert not success

    # Verify database was rolled back
    conn = sqlite3.connect(test_db_with_duplicates)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM til")
    count = cursor.fetchone()[0]
    assert count == original_count
    conn.close()
