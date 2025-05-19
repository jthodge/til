#!/usr/bin/env python
"""Remove duplicate TIL entries from the database.

This script migrates from the old path structure (e.g., bash/file.md)
to the new structure (e.g., content/bash/file.md) while preserving
git history data.
"""

import logging
import pathlib
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_duplicates(db_path: pathlib.Path) -> None:
    """Remove duplicate entries, preserving git history from old entries."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all entries to analyze
        cursor.execute("""
            SELECT path, slug, topic, created, created_utc, updated, updated_utc, url
            FROM til
            ORDER BY path
        """)
        
        all_entries = cursor.fetchall()
        
        # Group entries by slug and topic
        entries_by_key = {}
        for entry in all_entries:
            path, slug, topic, created, created_utc, updated, updated_utc, url = entry
            key = (slug, topic)
            
            if key not in entries_by_key:
                entries_by_key[key] = []
            
            entries_by_key[key].append({
                'path': path,
                'created': created,
                'created_utc': created_utc,
                'updated': updated,
                'updated_utc': updated_utc,
                'url': url
            })
        
        # Process duplicates
        updates = []
        deletions = []
        
        for key, entries in entries_by_key.items():
            if len(entries) > 1:
                slug, topic = key
                logger.info(f"Found duplicates for {topic}/{slug}")
                
                # Find the entry with content/ prefix (new format)
                new_entry = None
                old_entries = []
                
                for entry in entries:
                    if entry['path'].startswith('content_'):
                        new_entry = entry
                    else:
                        old_entries.append(entry)
                
                if new_entry and old_entries:
                    # Get the oldest created date from old entries
                    oldest_created = None
                    oldest_created_utc = None
                    
                    for old in old_entries:
                        if old['created'] and (not oldest_created or old['created'] < oldest_created):
                            oldest_created = old['created']
                            oldest_created_utc = old['created_utc']
                    
                    # Update the new entry with the old timestamps if they exist
                    if oldest_created:
                        updates.append((
                            oldest_created,
                            oldest_created_utc,
                            new_entry['path']
                        ))
                        logger.info(f"  Updating {new_entry['path']} with timestamp from {old_entries[0]['path']}")
                    
                    # Mark old entries for deletion
                    for old in old_entries:
                        deletions.append(old['path'])
                        logger.info(f"  Marking {old['path']} for deletion")
        
        # Apply updates
        if updates:
            logger.info(f"Applying {len(updates)} timestamp updates...")
            cursor.executemany("""
                UPDATE til 
                SET created = ?, created_utc = ?
                WHERE path = ?
            """, updates)
        
        # Apply deletions
        if deletions:
            logger.info(f"Deleting {len(deletions)} old entries...")
            cursor.executemany("DELETE FROM til WHERE path = ?", [(path,) for path in deletions])
        
        conn.commit()
        logger.info(f"Database cleanup complete. Updated {len(updates)} entries, deleted {len(deletions)} entries.")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: remove_duplicates.py <database_path>")
        sys.exit(1)
    
    db_path = pathlib.Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)
    
    remove_duplicates(db_path)