#!/usr/bin/env python
"""Fix creation dates in TIL database by re-extracting from git history.

This script addresses the issue where all TIL entries have creation dates
of 2025-05-18 due to database rebuild. It re-extracts the correct creation
dates from git history and updates the database.
"""

import logging
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any, Optional

from .config import TILConfig
from .repository import GitRepository


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_creation_dates(
    db_path: pathlib.Path,
    repo_path: Optional[pathlib.Path] = None,
    dry_run: bool = False,
) -> None:
    """Fix creation dates by re-extracting from git history.

    Args:
        db_path: Path to SQLite database
        repo_path: Path to git repository (defaults to current directory)
        dry_run: If True, show what changes would be made without applying them
    """
    if repo_path is None:
        repo_path = pathlib.Path.cwd()

    # Initialize git repository
    try:
        repository = GitRepository(repo_path)
    except Exception as e:
        logger.error(f"Failed to initialize git repository: {e}")
        raise

    # Extract all file history from git
    logger.info("Extracting file history from git...")
    try:
        all_times = repository.get_file_history()
    except Exception as e:
        logger.error(f"Failed to extract git history: {e}")
        raise

    logger.info(f"Found git history for {len(all_times)} files")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all current entries from database
        cursor.execute("""
            SELECT path, created, created_utc, updated, updated_utc
            FROM til
            ORDER BY path
        """)

        db_entries = cursor.fetchall()
        logger.info(f"Found {len(db_entries)} entries in database")

        updates = []
        files_without_history = []

        for (
            db_path_slug,
            db_created,
            db_created_utc,
            db_updated,
            db_updated_utc,
        ) in db_entries:
            # Convert database path slug back to file path
            # Database stores as "content_topic_filename.md"
            # We need to check git history for both new and old paths
            git_paths_to_check = []

            if db_path_slug.startswith("content_"):
                # Remove "content_" prefix and replace underscores with slashes
                path_parts = db_path_slug[8:].split("_")  # Remove "content_" prefix
                if len(path_parts) >= 2:
                    # Reconstruct as content/topic/filename.md
                    topic = path_parts[0]
                    filename_parts = path_parts[1:]
                    filename = "_".join(filename_parts)
                    if not filename.endswith(".md"):
                        filename += ".md"

                    # Check both new path and old path (without content/ prefix)
                    new_path = f"content/{topic}/{filename}"
                    old_path = f"{topic}/{filename}"
                    git_paths_to_check = [new_path, old_path]
                else:
                    logger.warning(f"Unexpected path format: {db_path_slug}")
                    continue
            else:
                # Fallback for any other format
                git_path = db_path_slug.replace("_", "/")
                if not git_path.endswith(".md"):
                    git_path += ".md"
                git_paths_to_check = [git_path]

            # Look up git history - try both paths and find the earliest creation date
            found_history = None
            git_path_used = None
            earliest_created = None

            for git_path in git_paths_to_check:
                if git_path in all_times:
                    history = all_times[git_path]
                    created_time = history["created"]

                    if earliest_created is None or created_time < earliest_created:
                        found_history = history
                        git_path_used = git_path
                        earliest_created = created_time

            if found_history:
                git_history = found_history
                git_created = git_history["created"]
                git_created_utc = git_history["created_utc"]

                # Check if we need to update (only if current creation date is 2025-05-18 or 2025-05-19)
                needs_update = False
                if db_created and (
                    "2025-05-18" in db_created or "2025-05-19" in db_created
                ):
                    needs_update = True
                elif db_created_utc and (
                    "2025-05-18" in db_created_utc or "2025-05-19" in db_created_utc
                ):
                    needs_update = True

                if needs_update:
                    # Use git history for created dates, keep existing updated dates if they're newer
                    updated_created = git_created
                    updated_created_utc = git_created_utc

                    # For updated dates, use the more recent of git history or current database value
                    try:
                        git_updated_dt = datetime.fromisoformat(
                            git_history["updated"].replace("Z", "+00:00")
                        )
                        if db_updated:
                            db_updated_dt = datetime.fromisoformat(
                                db_updated.replace("Z", "+00:00")
                            )
                            if db_updated_dt > git_updated_dt:
                                # Keep database updated time if it's newer
                                updated_updated = db_updated
                                updated_updated_utc = db_updated_utc
                            else:
                                # Use git updated time
                                updated_updated = git_history["updated"]
                                updated_updated_utc = git_history["updated_utc"]
                        else:
                            # Use git updated time
                            updated_updated = git_history["updated"]
                            updated_updated_utc = git_history["updated_utc"]
                    except Exception as e:
                        logger.warning(
                            f"Error comparing dates for {db_path_slug}, using git times: {e}"
                        )
                        updated_updated = git_history["updated"]
                        updated_updated_utc = git_history["updated_utc"]

                    updates.append(
                        (
                            updated_created,
                            updated_created_utc,
                            updated_updated,
                            updated_updated_utc,
                            db_path_slug,
                        )
                    )

                    logger.info(
                        f"Will update {db_path_slug}: {db_created} -> {updated_created} (from {git_path_used})"
                    )
            else:
                files_without_history.append(
                    (db_path_slug, " or ".join(git_paths_to_check))
                )

        # Apply updates
        if updates:
            if dry_run:
                logger.info(f"DRY RUN: Would apply {len(updates)} timestamp updates")
                logger.info("No changes made to database")
            else:
                logger.info(f"Applying {len(updates)} timestamp updates...")
                cursor.executemany(
                    """
                    UPDATE til 
                    SET created = ?, created_utc = ?, updated = ?, updated_utc = ?
                    WHERE path = ?
                """,
                    updates,
                )

                conn.commit()
                logger.info(f"Successfully updated {len(updates)} entries")
        else:
            logger.info("No updates needed")

        # Report files without git history
        if files_without_history:
            logger.warning(
                f"Found {len(files_without_history)} files without git history:"
            )
            for db_path, git_path in files_without_history:
                logger.warning(f"  {db_path} (looked for {git_path})")

    except Exception as e:
        logger.error(f"Error during timestamp fix: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: fix_creation_dates.py <database_path> [repository_path]")
        sys.exit(1)

    db_path = pathlib.Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    repo_path = None
    if len(sys.argv) > 2:
        repo_path = pathlib.Path(sys.argv[2])
        if not repo_path.exists():
            print(f"Repository path not found: {repo_path}")
            sys.exit(1)

    try:
        fix_creation_dates(db_path, repo_path)
        logger.info("Creation date fix completed successfully")
    except Exception as e:
        logger.error(f"Failed to fix creation dates: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
