#!/usr/bin/env python
"""Database backup and recovery management for TIL."""

import hashlib
import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Represents a database backup with metadata."""

    def __init__(
        self,
        path: Path,
        checksum: str,
        timestamp: datetime,
        metadata: Optional[dict] = None,
    ):
        """Initialize database backup.

        Args:
            path: Path to backup file
            checksum: SHA256 checksum of backup
            timestamp: When backup was created
            metadata: Optional metadata dictionary

        """
        self.path = path
        self.checksum = checksum
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """Return string representation of backup."""
        return f"Backup({self.path.name}, {self.timestamp.isoformat()}, {self.checksum[:8]}...)"


class BackupManager:
    """Manage database backups and recovery operations."""

    def __init__(self, backup_dir: Path):
        """Initialize backup manager.

        Args:
            backup_dir: Directory to store backups

        """
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_checksum(self, db_path: Path) -> str:
        """Calculate SHA256 checksum of database file."""
        sha256_hash = hashlib.sha256()
        with open(db_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _get_backup_filename(self, timestamp: datetime, checksum: str) -> str:
        """Generate backup filename with timestamp and checksum."""
        return f"til_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}_{checksum[:8]}.db"

    def create_backup(
        self, db_path: Path, description: Optional[str] = None
    ) -> DatabaseBackup:
        """Create a backup of the database.

        Args:
            db_path: Path to database to backup
            description: Optional description for the backup

        Returns:
            DatabaseBackup object representing the created backup

        """
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

        # Calculate checksum
        checksum = self._calculate_checksum(db_path)
        timestamp = datetime.now()

        # Create backup filename
        backup_filename = self._get_backup_filename(timestamp, checksum)
        backup_path = self.backup_dir / backup_filename

        # Copy database file
        shutil.copy2(db_path, backup_path)

        # Verify backup
        backup_checksum = self._calculate_checksum(backup_path)
        if backup_checksum != checksum:
            backup_path.unlink()  # Remove failed backup
            raise RuntimeError("Backup verification failed - checksums don't match")

        # Create metadata
        metadata = {
            "original_path": str(db_path),
            "description": description,
            "file_size": backup_path.stat().st_size,
        }

        backup = DatabaseBackup(backup_path, checksum, timestamp, metadata)
        logger.info(f"Created backup: {backup}")

        return backup

    def list_backups(self) -> list[DatabaseBackup]:
        """List all available backups, sorted by timestamp (newest first)."""
        backups = []

        for backup_file in self.backup_dir.glob("til_backup_*.db"):
            try:
                # Parse timestamp from filename
                parts = backup_file.stem.split("_")
                if len(parts) >= 4:
                    date_str = parts[2]
                    time_str = parts[3]
                    timestamp = datetime.strptime(
                        f"{date_str}_{time_str}", "%Y%m%d_%H%M%S"
                    )

                    # Calculate current checksum
                    checksum = self._calculate_checksum(backup_file)

                    backup = DatabaseBackup(backup_file, checksum, timestamp)
                    backups.append(backup)
            except Exception as e:
                logger.warning(f"Failed to parse backup file {backup_file}: {e}")

        return sorted(backups, key=lambda b: b.timestamp, reverse=True)

    def restore_backup(
        self, backup: DatabaseBackup, target_path: Path, verify: bool = True
    ) -> None:
        """Restore a backup to the target path.

        Args:
            backup: DatabaseBackup to restore
            target_path: Path where to restore the database
            verify: Whether to verify the restored database

        """
        if not backup.path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup.path}")

        # Create backup of current database if it exists
        if target_path.exists():
            current_backup = self.create_backup(target_path, "Pre-restore backup")
            logger.info(f"Created pre-restore backup: {current_backup}")

        # Restore the backup
        shutil.copy2(backup.path, target_path)

        if verify:
            # Verify restored database
            restored_checksum = self._calculate_checksum(target_path)
            if restored_checksum != backup.checksum:
                raise RuntimeError(
                    "Restore verification failed - checksums don't match"
                )

            # Quick database integrity check
            try:
                conn = sqlite3.connect(target_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()

                if result != "ok":
                    raise RuntimeError(f"Database integrity check failed: {result}")

            except Exception as e:
                raise RuntimeError(f"Database verification failed: {e}")

        logger.info(f"Restored backup {backup} to {target_path}")

    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Remove old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep

        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            logger.info(f"Only {len(backups)} backups found, nothing to clean up")
            return

        to_remove = backups[keep_count:]

        for backup in to_remove:
            try:
                backup.path.unlink()
                logger.info(f"Removed old backup: {backup}")
            except Exception as e:
                logger.warning(f"Failed to remove backup {backup}: {e}")

        logger.info(f"Cleaned up {len(to_remove)} old backups")

    def find_backup_by_checksum(self, checksum: str) -> Optional[DatabaseBackup]:
        """Find a backup by its checksum.

        Args:
            checksum: Full or partial checksum to search for

        Returns:
            DatabaseBackup if found, None otherwise

        """
        backups = self.list_backups()

        for backup in backups:
            if backup.checksum.startswith(checksum):
                return backup

        return None


def main() -> None:
    """CLI entry point for backup management."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="TIL Database Backup Manager")
    parser.add_argument("command", choices=["create", "list", "restore", "cleanup"])
    parser.add_argument("--db", default="til.db", help="Database file path")
    parser.add_argument("--backup-dir", default="backups", help="Backup directory")
    parser.add_argument("--description", help="Backup description")
    parser.add_argument("--checksum", help="Backup checksum for restore")
    parser.add_argument(
        "--keep", type=int, default=10, help="Number of backups to keep during cleanup"
    )

    args = parser.parse_args()

    backup_manager = BackupManager(Path(args.backup_dir))

    if args.command == "create":
        db_path = Path(args.db)
        backup = backup_manager.create_backup(db_path, args.description)
        print(f"Created backup: {backup}")

    elif args.command == "list":
        backups = backup_manager.list_backups()
        if not backups:
            print("No backups found")
        else:
            print(f"Found {len(backups)} backups:")
            for backup in backups:
                print(f"  {backup}")

    elif args.command == "restore":
        if not args.checksum:
            print("--checksum required for restore command")
            sys.exit(1)

        found_backup = backup_manager.find_backup_by_checksum(args.checksum)
        if found_backup is None:
            print(f"No backup found with checksum: {args.checksum}")
            sys.exit(1)

        target_path = Path(args.db)
        backup_manager.restore_backup(found_backup, target_path)
        print(f"Restored backup {found_backup} to {target_path}")

    elif args.command == "cleanup":
        backup_manager.cleanup_old_backups(args.keep)
        print(f"Cleanup completed, keeping {args.keep} most recent backups")


if __name__ == "__main__":
    main()
