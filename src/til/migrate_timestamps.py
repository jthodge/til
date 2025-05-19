#!/usr/bin/env python
"""Migrate timestamps from old entries to new entries in the TIL database.

This script ensures that entries in the new structure (content/) preserve
the original creation dates from the old structure.
"""

import logging
import pathlib
import sqlite3


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_timestamps(db_path: pathlib.Path) -> None:
    """Migrate timestamps from old entries to new entries."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create a mapping of slugs to old timestamps
        cursor.execute("""
            SELECT slug, topic, MIN(created) as oldest_created, MIN(created_utc) as oldest_created_utc
            FROM til
            WHERE path NOT LIKE 'content_%'
              AND created IS NOT NULL
            GROUP BY slug, topic
        """)

        old_timestamps: dict[tuple[str, str], tuple[str, str]] = {}
        for slug, topic, created, created_utc in cursor.fetchall():
            old_timestamps[(slug, topic)] = (created, created_utc)
            logger.info(f"Found old timestamp for {topic}/{slug}: {created}")

        # Update new entries with old timestamps
        updates = []
        cursor.execute("""
            SELECT path, slug, topic, created
            FROM til
            WHERE path LIKE 'content_%'
        """)

        for path, slug, topic, current_created in cursor.fetchall():
            key = (slug, topic)
            if key in old_timestamps:
                old_created, old_created_utc = old_timestamps[key]
                # Only update if the old timestamp is earlier
                if not current_created or old_created < current_created:
                    updates.append((old_created, old_created_utc, path))
                    logger.info(
                        f"  Will update {path}: {current_created} -> {old_created}"
                    )

        # Apply updates
        if updates:
            logger.info(f"Applying {len(updates)} timestamp updates...")
            cursor.executemany(
                """
                UPDATE til
                SET created = ?, created_utc = ?
                WHERE path = ?
            """,
                updates,
            )

            conn.commit()
            logger.info(f"Successfully migrated {len(updates)} timestamps")
        else:
            logger.info("No timestamp updates needed")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: migrate_timestamps.py <database_path>")
        sys.exit(1)

    db_path = pathlib.Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    migrate_timestamps(db_path)
