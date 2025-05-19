"""Integration test for the complete migration workflow."""

import pathlib
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from til.config import TILConfig
from til.database import TILDatabase
from til.production_safe_migration import ProductionMigration
from til.readme_generator import ReadmeGenerator


def test_full_migration_workflow() -> None:
    """Test the complete migration workflow from duplicates to clean database."""

    # Create a test database with realistic data
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = pathlib.Path(tmp.name)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the til table
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

    # Insert a mix of old and new entries with various edge cases
    entries = [
        # Old entries with timestamps
        ('bash_script-template.md', 'script-template', 'bash', 'Shell Script Template',
         'Template body', '<p>Template body</p>',
         '2020-05-01T12:00:00', '2020-05-01T16:00:00',
         '2020-05-01T12:00:00', '2020-05-01T16:00:00',
         'https://github.com/jthodge/til/blob/main/bash/script-template.md'),

        # New entries without timestamps (duplicates)
        ('content_bash_script-template.md', 'script-template', 'bash', 'Shell Script Template',
         'Template body', '<p>Template body</p>',
         None, None, None, None,
         'https://github.com/jthodge/til/blob/main/content/bash/script-template.md'),

        # Entry with partial timestamp info
        ('python_deepcopy.md', 'deepcopy', 'python', 'Creating Deep Copies',
         'Deepcopy body', '<p>Deepcopy body</p>',
         '2021-03-15T09:30:00', None, None, None,
         'https://github.com/jthodge/til/blob/main/python/deepcopy.md'),

        # New entry without old counterpart
        ('content_javascript_promises.md', 'promises', 'javascript', 'Understanding Promises',
         'Promise body', '<p>Promise body</p>',
         '2024-01-01T00:00:00', '2024-01-01T00:00:00',
         '2024-01-01T00:00:00', '2024-01-01T00:00:00',
         'https://github.com/jthodge/til/blob/main/content/javascript/promises.md'),
    ]

    cursor.executemany('INSERT INTO til VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entries)
    conn.commit()
    conn.close()

    try:
        # Run the production migration
        migration = ProductionMigration(db_path)

        # Mock input to not keep backup
        with patch('builtins.input', return_value='n'):
            success = migration.run()

        assert success

        # Verify the results
        conn = sqlite3.connect(db_path)
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

        # Check that old entries with duplicates were removed
        cursor.execute("SELECT COUNT(*) FROM til WHERE path = 'bash_script-template.md'")
        old_bash_count = cursor.fetchone()[0]
        assert old_bash_count == 0

        # Check that old entries without new counterparts remain
        cursor.execute("SELECT COUNT(*) FROM til WHERE path = 'python_deepcopy.md'")
        old_python_count = cursor.fetchone()[0]
        assert old_python_count == 1

        # Check that timestamps were preserved
        cursor.execute("""
            SELECT created
            FROM til
            WHERE path = 'content_bash_script-template.md'
        """)
        result = cursor.fetchone()
        assert result[0] == '2020-05-01T12:00:00'

        # Check that new entry without old counterpart still exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM til
            WHERE path = 'content_javascript_promises.md'
        """)
        count = cursor.fetchone()[0]
        assert count == 1

        conn.close()

        # Test README generation with the migrated database
        db = TILDatabase(db_path)
        generator = ReadmeGenerator(db)

        # This should not raise any exceptions
        index_lines = generator.generate_index()

        # Verify content
        content = '\n'.join(index_lines)
        assert 'Shell Script Template' in content
        assert 'Understanding Promises' in content
        assert '2020-05-01' in content  # Old timestamp preserved
        assert '2024-01-01' in content  # New timestamp kept

        # Test updating README file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as readme:
            readme_path = pathlib.Path(readme.name)
            readme.write("""# Test README

<!-- index starts -->
<!-- index ends -->
""")

        generator.update_readme(readme_path)

        # Verify README was updated
        with open(readme_path) as f:
            updated_content = f.read()

        assert 'Shell Script Template' in updated_content
        assert 'Understanding Promises' in updated_content

        # Cleanup
        readme_path.unlink()

    finally:
        # Cleanup database
        if db_path.exists():
            db_path.unlink()


def test_migration_workflow_with_edge_cases() -> None:
    """Test migration with various edge cases."""

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

    # Edge cases
    entries = [
        # Entry with null created but valid updated
        ('old_edge1.md', 'edge1', 'testing', 'Edge Case 1', 'Body', '<p>Body</p>',
         None, None, '2022-01-01T00:00:00', '2022-01-01T00:00:00',
         'https://example.com/old_edge1.md'),

        # Special characters in path/slug
        ('content_testing_special-chars-test.md', 'special-chars-test', 'testing',
         'Special Characters: Test!', 'Body', '<p>Body</p>',
         '2023-01-01T00:00:00', '2023-01-01T00:00:00', None, None,
         'https://example.com/content_testing_special-chars-test.md'),

        # Very long title
        ('content_testing_long-title.md', 'long-title', 'testing',
         'This is a very long title that might cause issues with formatting or display in various contexts but should still be handled properly',
         'Body', '<p>Body</p>', None, None, None, None,
         'https://example.com/content_testing_long-title.md'),
    ]

    cursor.executemany('INSERT INTO til VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entries)
    conn.commit()
    conn.close()

    try:
        # Run migration
        migration = ProductionMigration(db_path)

        with patch('builtins.input', return_value='n'):
            success = migration.run()

        assert success

        # Test README generation
        db = TILDatabase(db_path)
        generator = ReadmeGenerator(db)

        # Should not raise exceptions with edge cases
        index_lines = generator.generate_index()
        content = '\n'.join(index_lines)

        # Verify all entries are included
        assert 'Special Characters: Test!' in content
        assert 'This is a very long title' in content

    finally:
        if db_path.exists():
            db_path.unlink()
