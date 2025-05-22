#!/usr/bin/env python
"""Database validation and integrity checks for TIL."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional


logger = logging.getLogger(__name__)


class ValidationResult(NamedTuple):
    """Result of a database validation check."""

    is_valid: bool
    message: str
    details: Optional[dict] = None


class DatabaseValidator:
    """Validate TIL database integrity and consistency."""

    def __init__(self, db_path: Path):
        """Initialize validator with database path.

        Args:
            db_path: Path to SQLite database file

        """
        self.db_path = db_path

    def validate_schema(self) -> ValidationResult:
        """Validate database has expected schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if til table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='til'
            """)

            if not cursor.fetchone():
                return ValidationResult(False, "Missing required 'til' table")

            # Check required columns
            cursor.execute("PRAGMA table_info(til)")
            columns = {row[1] for row in cursor.fetchall()}

            required_columns = {
                "path",
                "topic",
                "slug",
                "title",
                "body",
                "html",
                "created",
                "created_utc",
                "updated",
                "updated_utc",
            }

            missing_columns = required_columns - columns
            if missing_columns:
                return ValidationResult(
                    False, f"Missing required columns: {missing_columns}"
                )

            conn.close()
            return ValidationResult(True, "Schema validation passed")

        except Exception as e:
            return ValidationResult(False, f"Schema validation failed: {e}")

    def validate_creation_dates(self) -> ValidationResult:
        """Validate creation dates are reasonable (not all the same recent date)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all creation dates
            cursor.execute("""
                SELECT created, COUNT(*) as count
                FROM til
                WHERE created IS NOT NULL
                GROUP BY DATE(created)
                ORDER BY count DESC
                LIMIT 5
            """)

            date_counts = cursor.fetchall()

            if not date_counts:
                return ValidationResult(False, "No creation dates found in database")

            # Check if >80% of entries have the same creation date
            total_entries = sum(count for _, count in date_counts)
            most_common_date, most_common_count = date_counts[0]

            if most_common_count / total_entries > 0.8:
                # Check if this date is recent (potential bug indicator)
                try:
                    parsed_date = datetime.fromisoformat(
                        most_common_date.replace("Z", "+00:00")
                    )
                    days_ago = (datetime.now(parsed_date.tzinfo) - parsed_date).days

                    if days_ago < 30:  # Created within last 30 days
                        return ValidationResult(
                            False,
                            f"Suspicious: {most_common_count}/{total_entries} entries "
                            f"have same recent creation date: {most_common_date}",
                            {
                                "suspicious_date": most_common_date,
                                "count": most_common_count,
                            },
                        )
                except Exception:
                    pass  # Date parsing failed, continue with other checks

            # Get date range
            cursor.execute("""
                SELECT MIN(created) as earliest, MAX(created) as latest
                FROM til
                WHERE created IS NOT NULL
            """)

            earliest, latest = cursor.fetchone()
            conn.close()

            return ValidationResult(
                True,
                f"Creation dates look healthy: {earliest} to {latest}",
                {"date_range": (earliest, latest), "unique_dates": len(date_counts)},
            )

        except Exception as e:
            return ValidationResult(False, f"Creation date validation failed: {e}")

    def validate_content_integrity(self) -> ValidationResult:
        """Validate content fields are populated and consistent."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check for entries with missing required content
            cursor.execute("""
                SELECT COUNT(*) FROM til
                WHERE title IS NULL OR title = ''
                OR body IS NULL OR body = ''
                OR html IS NULL OR html = ''
            """)

            missing_content = cursor.fetchone()[0]

            if missing_content > 0:
                return ValidationResult(
                    False, f"{missing_content} entries missing required content fields"
                )

            # Check for reasonable content lengths
            cursor.execute("""
                SELECT COUNT(*) FROM til
                WHERE LENGTH(body) < 10 OR LENGTH(html) < 20
            """)

            short_content = cursor.fetchone()[0]

            if short_content > 0:
                return ValidationResult(
                    False, f"{short_content} entries have suspiciously short content"
                )

            conn.close()
            return ValidationResult(True, "Content integrity validation passed")

        except Exception as e:
            return ValidationResult(False, f"Content validation failed: {e}")

    def validate_full_text_search(self) -> ValidationResult:
        """Validate FTS table exists and is populated."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if FTS table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='til_fts'
            """)

            if not cursor.fetchone():
                return ValidationResult(
                    False, "Missing full-text search table 'til_fts'"
                )

            # Check FTS table has entries
            cursor.execute("SELECT COUNT(*) FROM til_fts")
            fts_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM til")
            til_count = cursor.fetchone()[0]

            if fts_count != til_count:
                return ValidationResult(
                    False,
                    f"FTS table count ({fts_count}) doesn't match til table count ({til_count})",
                )

            conn.close()
            return ValidationResult(True, "Full-text search validation passed")

        except Exception as e:
            return ValidationResult(False, f"FTS validation failed: {e}")

    def run_all_validations(self) -> list[ValidationResult]:
        """Run all validation checks."""
        validations = [
            ("Schema", self.validate_schema),
            ("Creation Dates", self.validate_creation_dates),
            ("Content Integrity", self.validate_content_integrity),
            ("Full-Text Search", self.validate_full_text_search),
        ]

        results = []
        for name, validator in validations:
            logger.info(f"Running {name} validation...")
            result = validator()
            results.append(result)

            if result.is_valid:
                logger.info(f"✅ {name}: {result.message}")
            else:
                logger.error(f"❌ {name}: {result.message}")

        return results

    def is_database_healthy(self) -> bool:
        """Check if database passes all critical validations."""
        results = self.run_all_validations()
        return all(result.is_valid for result in results)


def main() -> None:
    """CLI entry point for database validation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: database_validator.py <database_path>")
        sys.exit(1)

    db_path = Path(sys.argv[1])
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    validator = DatabaseValidator(db_path)

    print(f"Validating database: {db_path}")
    print("=" * 50)

    results = validator.run_all_validations()

    failed_checks = [r for r in results if not r.is_valid]

    if failed_checks:
        print(f"\n❌ Database validation failed ({len(failed_checks)} issues)")
        sys.exit(1)
    else:
        print(f"\n✅ Database validation passed (all {len(results)} checks)")
        sys.exit(0)


if __name__ == "__main__":
    main()
