#!/usr/bin/env python
"""Remove all old TIL entries that don't use the content/ prefix."""

import logging
import pathlib
import sqlite3


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_old_entries(db_path: pathlib.Path) -> None:
    """Remove all entries that don't use the content/ prefix."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Find all entries that don't have content/ prefix and aren't special cases
        cursor.execute("""
            SELECT path, slug, topic
            FROM til
            WHERE path NOT LIKE 'content_%'
              AND path NOT LIKE '.pytest%'
              AND path NOT LIKE 'templates_%'
            ORDER BY topic, slug
        """)

        old_entries = cursor.fetchall()
        logger.info(f"Found {len(old_entries)} old entries to remove")

        # Delete all old entries
        if old_entries:
            paths_to_delete = [entry[0] for entry in old_entries]
            placeholders = ",".join(["?"] * len(paths_to_delete))
            cursor.execute(
                f"DELETE FROM til WHERE path IN ({placeholders})",  # noqa: S608
                paths_to_delete,
            )

            for path, slug, topic in old_entries:
                logger.info(f"  Removed: {topic}/{slug} ({path})")

        conn.commit()
        logger.info(f"Cleanup complete. Removed {len(old_entries)} old entries.")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: cleanup_old_entries.py <database_path>")
        sys.exit(1)

    db_path = pathlib.Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    cleanup_old_entries(db_path)
