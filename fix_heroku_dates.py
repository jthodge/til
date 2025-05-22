#!/usr/bin/env python
"""Standalone script to fix creation dates on Heroku."""

import logging
import sqlite3
import subprocess
import sys
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_git_history():
    """Extract git history for all files."""
    try:
        # Get all commits in reverse chronological order (oldest first)
        result = subprocess.run(
            ["git", "rev-list", "--reverse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.strip().split('\n')
        
        file_history = {}
        
        for commit in commits:
            # Get commit date
            date_result = subprocess.run(
                ["git", "show", "--no-patch", "--format=%aI", commit],
                capture_output=True,
                text=True,
                check=True
            )
            commit_date = date_result.stdout.strip()
            
            # Get files changed in this commit
            files_result = subprocess.run(
                ["git", "show", "--name-only", "--format=", commit],
                capture_output=True,
                text=True,
                check=True
            )
            
            for file_path in files_result.stdout.strip().split('\n'):
                if file_path and file_path.endswith('.md'):
                    if file_path not in file_history:
                        # This is the first time we've seen this file (earliest commit)
                        try:
                            dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                            file_history[file_path] = {
                                'created': commit_date,
                                'created_utc': dt.astimezone(datetime.timezone.utc).isoformat(),
                                'updated': commit_date,
                                'updated_utc': dt.astimezone(datetime.timezone.utc).isoformat(),
                            }
                        except Exception as e:
                            logger.warning(f"Error parsing date {commit_date}: {e}")
                    else:
                        # Update the 'updated' time for this file
                        try:
                            dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                            file_history[file_path]['updated'] = commit_date
                            file_history[file_path]['updated_utc'] = dt.astimezone(datetime.timezone.utc).isoformat()
                        except Exception as e:
                            logger.warning(f"Error parsing date {commit_date}: {e}")
        
        logger.info(f"Found git history for {len(file_history)} files")
        return file_history
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error extracting git history: {e}")
        return {}


def fix_creation_dates(dry_run=False):
    """Fix creation dates in the database."""
    # Get git history
    logger.info("Extracting git history...")
    git_history = get_git_history()
    
    if not git_history:
        logger.error("No git history found, aborting")
        return
    
    # Connect to database
    conn = sqlite3.connect('til.db')
    cursor = conn.cursor()
    
    try:
        # Get all entries from database
        cursor.execute("""
            SELECT path, created, created_utc, updated, updated_utc
            FROM til
            ORDER BY path
        """)
        
        db_entries = cursor.fetchall()
        logger.info(f"Found {len(db_entries)} entries in database")
        
        updates = []
        files_without_history = []
        
        for db_path_slug, db_created, db_created_utc, db_updated, db_updated_utc in db_entries:
            # Convert database path slug back to file path
            git_paths_to_check = []
            
            if db_path_slug.startswith("content_"):
                # Remove "content_" prefix and replace underscores with slashes
                path_parts = db_path_slug[8:].split("_")  # Remove "content_" prefix
                if len(path_parts) >= 2:
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
                if git_path in git_history:
                    history = git_history[git_path]
                    created_time = history["created"]
                    
                    if earliest_created is None or created_time < earliest_created:
                        found_history = history
                        git_path_used = git_path
                        earliest_created = created_time
            
            if found_history:
                # Check if we need to update (only if current creation date is 2025-05-18 or 2025-05-19)
                needs_update = False
                if (
                    db_created
                    and ("2025-05-18" in db_created or "2025-05-19" in db_created)
                ) or (
                    db_created_utc
                    and (
                        "2025-05-18" in db_created_utc or "2025-05-19" in db_created_utc
                    )
                ):
                    needs_update = True
                
                if needs_update:
                    git_created = found_history["created"]
                    git_created_utc = found_history["created_utc"]
                    
                    # For updated dates, use the more recent of git history or current database value
                    try:
                        git_updated_dt = datetime.fromisoformat(
                            found_history["updated"].replace("Z", "+00:00")
                        )
                        if db_updated:
                            db_updated_dt = datetime.fromisoformat(
                                db_updated.replace("Z", "+00:00")
                            )
                            if db_updated_dt > git_updated_dt:
                                updated_updated = db_updated
                                updated_updated_utc = db_updated_utc
                            else:
                                updated_updated = found_history["updated"]
                                updated_updated_utc = found_history["updated_utc"]
                        else:
                            updated_updated = found_history["updated"]
                            updated_updated_utc = found_history["updated_utc"]
                    except Exception as e:
                        logger.warning(f"Error comparing dates for {db_path_slug}, using git times: {e}")
                        updated_updated = found_history["updated"]
                        updated_updated_utc = found_history["updated_utc"]
                    
                    updates.append((
                        git_created,
                        git_created_utc,
                        updated_updated,
                        updated_updated_utc,
                        db_path_slug,
                    ))
                    
                    logger.info(f"Will update {db_path_slug}: {db_created} -> {git_created} (from {git_path_used})")
            else:
                files_without_history.append((db_path_slug, " or ".join(git_paths_to_check)))
        
        # Apply updates
        if updates:
            if dry_run:
                logger.info(f"DRY RUN: Would apply {len(updates)} timestamp updates")
                logger.info("No changes made to database")
            else:
                logger.info(f"Applying {len(updates)} timestamp updates...")
                cursor.executemany("""
                    UPDATE til
                    SET created = ?, created_utc = ?, updated = ?, updated_utc = ?
                    WHERE path = ?
                """, updates)
                
                conn.commit()
                logger.info(f"Successfully updated {len(updates)} entries")
        else:
            logger.info("No updates needed")
        
        # Report files without git history
        if files_without_history:
            logger.warning(f"Found {len(files_without_history)} files without git history:")
            for db_path_entry, git_path in files_without_history:
                logger.warning(f"  {db_path_entry} (looked for {git_path})")
    
    except Exception as e:
        logger.error(f"Error during timestamp fix: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    fix_creation_dates(dry_run=dry_run)
    logger.info("Creation date fix completed successfully")