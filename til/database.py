"""Database operations for TIL."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import sqlite_utils
from sqlite_utils.db import NotFoundError, Table

logger = logging.getLogger(__name__)


class TILDatabase:
    """Handle all database operations."""

    def __init__(self, db_path: Path):
        """Initialize TILDatabase with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db = sqlite_utils.Database(db_path)
        
    def get_table(self) -> Table:
        """Get the til table, ensuring it's a Table instance.
        
        Returns:
            Table instance for the til table
        """
        table = self.db.table("til", pk="path")
        # Ensure it's a Table instance for type safety
        assert isinstance(table, Table), "Expected Table instance"
        return table
        
    def upsert_record(self, record: Dict[str, Any]) -> None:
        """Insert or update a TIL record.
        
        Args:
            record: Dictionary containing record data
        """
        table = self.get_table()
        with self.db.conn:
            table.upsert(record, alter=True)
    
    def get_previous_record(self, path: str) -> Optional[Dict[str, Any]]:
        """Get previous version of a record.
        
        Args:
            path: Path identifier for the record
            
        Returns:
            Previous record data or None if not found
        """
        try:
            table = self.get_table()
            return dict(table.get(path))
        except (NotFoundError, KeyError):
            return None
    
    def enable_search(self) -> None:
        """Enable full-text search on title and body fields."""
        table = self.get_table()
        
        # Only enable if the table has records
        if "til" in self.db.table_names() and table.count > 0:
            logger.info("Enabling full-text search...")
            table.enable_fts(
                ["title", "body"], tokenize="porter", create_triggers=True, replace=True
            )
        else:
            logger.warning("No records in database, skipping FTS setup")
    
    def get_all_by_topic(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all entries grouped by topic.
        
        Returns:
            Dictionary mapping topics to lists of records
        """
        by_topic: Dict[str, List[Dict[str, Any]]] = {}
        
        try:
            for row in self.db["til"].rows_where(order_by="created_utc"):
                topic = row["topic"]
                by_topic.setdefault(topic, []).append(dict(row))
        except Exception as e:
            logger.error(f"Error fetching records by topic: {e}")
            
        return by_topic
    
    def count(self) -> int:
        """Get total number of records.
        
        Returns:
            Number of records in the database
        """
        try:
            return self.db["til"].count
        except Exception:
            return 0
    
    def table_exists(self) -> bool:
        """Check if the til table exists.
        
        Returns:
            True if table exists, False otherwise
        """
        return "til" in self.db.table_names()
    
    def close(self) -> None:
        """Close the database connection."""
        self.db.close()