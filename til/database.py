"""Database operations for TIL."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import sqlite_utils
from sqlite_utils.db import NotFoundError, Table

from .exceptions import DatabaseError

logger = logging.getLogger(__name__)


class TILDatabase:
    """Handle all database operations."""

    def __init__(self, db_path: Path):
        """Initialize TILDatabase with database path.

        Args:
            db_path: Path to SQLite database file

        Raises:
            DatabaseError: If database cannot be initialized
        """
        self.db_path = db_path

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.db = sqlite_utils.Database(db_path)
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database at {db_path}: {e}")

    def get_table(self) -> Table:
        """Get the til table, ensuring it's a Table instance.

        Returns:
            Table instance for the til table

        Raises:
            DatabaseError: If table cannot be accessed
        """
        try:
            table = self.db.table("til", pk="path")
            # Ensure it's a Table instance for type safety
            if not isinstance(table, Table):
                raise DatabaseError(f"Expected Table instance, got {type(table)}")
            return table
        except Exception as e:
            raise DatabaseError(f"Failed to get til table: {e}")

    def upsert_record(self, record: Dict[str, Any]) -> None:
        """Insert or update a TIL record.

        Args:
            record: Dictionary containing record data

        Raises:
            DatabaseError: If record cannot be saved
        """
        if not record:
            raise DatabaseError("Cannot save empty record")

        required_fields = ["path", "slug", "topic", "title", "body"]
        missing_fields = [field for field in required_fields if field not in record]
        if missing_fields:
            raise DatabaseError(f"Record missing required fields: {missing_fields}")

        try:
            table = self.get_table()
            with self.db.conn:
                table.upsert(record, alter=True)
                logger.debug(f"Saved record: {record['path']}")
        except Exception as e:
            raise DatabaseError(f"Failed to save record {record.get('path', '?')}: {e}")

    def get_previous_record(self, path: str) -> Optional[Dict[str, Any]]:
        """Get previous version of a record.

        Args:
            path: Path identifier for the record

        Returns:
            Previous record data or None if not found

        Raises:
            DatabaseError: If there's an error retrieving the record
        """
        if not path:
            raise DatabaseError("Path cannot be empty")

        try:
            table = self.get_table()
            return dict(table.get(path))
        except NotFoundError:
            logger.debug(f"No previous record found for {path}")
            return None
        except KeyError:
            # Table doesn't exist yet
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get previous record for {path}: {e}")

    def enable_search(self) -> None:
        """Enable full-text search on title and body fields.

        Raises:
            DatabaseError: If search cannot be enabled
        """
        try:
            table = self.get_table()

            # Only enable if the table has records
            if "til" in self.db.table_names() and table.count > 0:
                logger.info("Enabling full-text search...")
                table.enable_fts(
                    ["title", "body"],
                    tokenize="porter",
                    create_triggers=True,
                    replace=True,
                )
                logger.info("Full-text search enabled successfully")
            else:
                logger.info("No records in database, skipping FTS setup")
        except Exception as e:
            # FTS might already be enabled, which is fine
            if "already exists" in str(e):
                logger.info("Full-text search already enabled")
            else:
                raise DatabaseError(f"Failed to enable full-text search: {e}")

    def get_all_by_topic(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all entries grouped by topic.

        Returns:
            Dictionary mapping topics to lists of records

        Raises:
            DatabaseError: If records cannot be retrieved
        """
        by_topic: Dict[str, List[Dict[str, Any]]] = {}

        try:
            if "til" not in self.db.table_names():
                logger.info("No til table exists yet")
                return by_topic

            for row in self.db["til"].rows_where(order_by="created_utc"):
                topic = row.get("topic", "unknown")
                by_topic.setdefault(topic, []).append(dict(row))

            logger.info(
                f"Retrieved {sum(len(records) for records in by_topic.values())} records across {len(by_topic)} topics"
            )
            return by_topic
        except Exception as e:
            raise DatabaseError(f"Failed to fetch records by topic: {e}")

    def count(self) -> int:
        """Get total number of records.

        Returns:
            Number of records in the database
        """
        try:
            if "til" not in self.db.table_names():
                return 0
            return self.db["til"].count
        except Exception as e:
            logger.warning(f"Failed to count records: {e}")
            return 0

    def close(self) -> None:
        """Close the database connection."""
        try:
            self.db.close()
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
