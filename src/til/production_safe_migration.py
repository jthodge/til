#!/usr/bin/env python
"""Production-safe migration script for TIL database deduplication.

This script:
1. Backs up the database before making changes
2. Preserves timestamps from old entries
3. Removes duplicates
4. Validates the result
5. Can be rolled back if needed
"""

import logging
import os
import pathlib
import shutil
import sqlite3
import sys
from typing import Any, Union


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionMigration:
    """Handles safe database migration with backup and rollback capabilities."""

    def __init__(self, db_path: Union[pathlib.Path, str]):
        """Initialize the migration with the database path."""
        self.db_path = pathlib.Path(db_path)
        self.backup_path = self.db_path.with_suffix(".backup")

    def create_backup(self) -> None:
        """Create a backup of the database."""
        logger.info(f"Creating backup at {self.backup_path}")
        shutil.copy2(self.db_path, self.backup_path)
        logger.info("Backup created successfully")

    def validate_backup(self) -> bool:
        """Validate the backup was created correctly."""
        if not self.backup_path.exists():
            logger.error("Backup file does not exist")
            return False

        if self.backup_path.stat().st_size != self.db_path.stat().st_size:
            logger.error("Backup file size doesn't match original")
            return False

        logger.info("Backup validated successfully")
        return True

    def analyze_duplicates(self) -> dict[tuple[str, str], list[dict]]:
        """Analyze the database for duplicates."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT path, slug, topic, created, created_utc, updated, updated_utc, url
                FROM til
                ORDER BY topic, slug, path
            """)

            # Group by slug and topic
            entries_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in cursor.fetchall():
                path, slug, topic, created, created_utc, updated, updated_utc, url = row
                key = (slug, topic)

                if key not in entries_by_key:
                    entries_by_key[key] = []

                entries_by_key[key].append(
                    {
                        "path": path,
                        "created": created,
                        "created_utc": created_utc,
                        "updated": updated,
                        "updated_utc": updated_utc,
                        "url": url,
                    }
                )

            # Find duplicates
            duplicates = {k: v for k, v in entries_by_key.items() if len(v) > 1}

            logger.info(f"Found {len(duplicates)} sets of duplicate entries")
            return duplicates

        finally:
            conn.close()

    def migrate_timestamps_and_remove_duplicates(
        self, duplicates: dict[tuple[str, str], list[dict]]
    ) -> tuple[int, int]:
        """Migrate timestamps from old entries to new ones and remove duplicates."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp_updates = []
        deletions = []

        try:
            for key, entries in duplicates.items():
                slug, topic = key

                # Separate old and new entries
                new_entry = None
                old_entries = []

                for entry in entries:
                    if entry["path"].startswith("content_"):
                        new_entry = entry
                    else:
                        old_entries.append(entry)

                if new_entry and old_entries:
                    # Find the oldest timestamp
                    oldest_created = None
                    oldest_created_utc = None

                    for old in old_entries:
                        if old["created"] and (
                            not oldest_created or old["created"] < oldest_created
                        ):
                            oldest_created = old["created"]
                            oldest_created_utc = old["created_utc"]

                    # Update new entry with old timestamp
                    if oldest_created:
                        timestamp_updates.append(
                            (oldest_created, oldest_created_utc, new_entry["path"])
                        )
                        logger.info(
                            f"Migrating timestamp for {topic}/{slug}: {oldest_created}"
                        )

                    # Mark old entries for deletion
                    for old in old_entries:
                        deletions.append(old["path"])

            # Apply updates
            if timestamp_updates:
                logger.info(f"Applying {len(timestamp_updates)} timestamp updates...")
                cursor.executemany(
                    """
                    UPDATE til
                    SET created = ?, created_utc = ?
                    WHERE path = ?
                """,
                    timestamp_updates,
                )

            # Apply deletions
            if deletions:
                logger.info(f"Deleting {len(deletions)} old entries...")
                placeholders = ",".join(["?"] * len(deletions))
                cursor.execute(
                    f"DELETE FROM til WHERE path IN ({placeholders})",  # noqa: S608
                    deletions,
                )

            conn.commit()
            logger.info("Migration completed successfully")
            return len(timestamp_updates), len(deletions)

        except Exception as e:
            logger.error(f"Error during migration: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def validate_migration(self) -> bool:
        """Validate the migration was successful."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check for remaining duplicates
            cursor.execute("""
                SELECT slug, topic, COUNT(*) as count
                FROM til
                GROUP BY slug, topic
                HAVING count > 1
            """)

            duplicates = cursor.fetchall()
            if duplicates:
                logger.error(f"Still have {len(duplicates)} duplicate entries")
                return False

            # Check that content entries have timestamps
            cursor.execute("""
                SELECT COUNT(*)
                FROM til
                WHERE path LIKE 'content_%'
                  AND created IS NULL
            """)

            missing_timestamps = cursor.fetchone()[0]
            if missing_timestamps > 0:
                logger.warning(
                    f"{missing_timestamps} content entries missing timestamps"
                )

            logger.info("Migration validation passed")
            return True

        finally:
            conn.close()

    def rollback(self) -> None:
        """Rollback to the backup."""
        logger.info("Rolling back to backup...")
        shutil.copy2(self.backup_path, self.db_path)
        logger.info("Rollback completed")

    def cleanup_backup(self) -> None:
        """Remove the backup file."""
        if self.backup_path.exists():
            self.backup_path.unlink()
            logger.info("Backup file removed")

    def run(self) -> bool:
        """Run the complete migration process."""
        try:
            # Step 1: Create backup
            self.create_backup()
            if not self.validate_backup():
                raise RuntimeError("Backup validation failed")

            # Step 2: Analyze duplicates
            duplicates = self.analyze_duplicates()
            if not duplicates:
                logger.info("No duplicates found, nothing to do")
                self.cleanup_backup()
                return True

            # Step 3: Migrate and deduplicate
            updates, deletions = self.migrate_timestamps_and_remove_duplicates(
                duplicates
            )
            logger.info(
                f"Migration complete: {updates} timestamps migrated, {deletions} entries deleted"
            )

            # Step 4: Validate
            if not self.validate_migration():
                logger.error("Migration validation failed, rolling back")
                self.rollback()
                return False

            logger.info("Migration successful!")
            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if self.backup_path.exists():
                self.rollback()
            return False


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: production_safe_migration.py <database_path>")
        sys.exit(1)

    db_path = pathlib.Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    migration = ProductionMigration(db_path)
    success = migration.run()

    if not success:
        sys.exit(1)

    # Optionally keep backup for safety
    if not os.environ.get("CI"):
        if input("Keep backup file? (y/n): ").lower() == "n":
            migration.cleanup_backup()
    else:
        print("CI environment detected - keeping backup file for safety")


if __name__ == "__main__":
    main()
