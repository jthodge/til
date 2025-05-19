"""TIL processor orchestrating the entire pipeline."""

import datetime
import logging
import pathlib
from typing import Any, Optional

from .config import TILConfig
from .database import TILDatabase
from .exceptions import ConfigurationError, FileProcessingError, RepositoryError
from .renderer import MarkdownRenderer
from .repository import GitRepository


logger = logging.getLogger(__name__)


class TILProcessor:
    """Orchestrate the TIL processing pipeline."""

    def __init__(self, config: TILConfig):
        """Initialize TILProcessor with configuration.

        Args:
            config: TIL configuration

        Raises:
            ConfigurationError: If configuration is invalid

        """
        if not config.root_path.exists():
            raise ConfigurationError(f"Root path does not exist: {config.root_path}")

        self.config = config

        # Initialize components
        self.repository: Optional[GitRepository]
        try:
            self.repository = GitRepository(config.root_path)
        except RepositoryError as e:
            logger.warning(f"Git repository not available: {e}")
            self.repository = None
        except Exception as e:
            logger.error(f"Unexpected error initializing git repository: {e}")
            self.repository = None

        self.renderer = MarkdownRenderer(config)
        self.database = TILDatabase(config.database_path)

    def process_file(self, filepath: pathlib.Path) -> dict[str, Any]:
        """Process a single markdown file.

        Args:
            filepath: Path to markdown file

        Returns:
            Dictionary containing record data

        Raises:
            FileProcessingError: If file cannot be processed

        """
        if not filepath.exists():
            raise FileProcessingError(f"File does not exist: {filepath}")

        if not filepath.is_file():
            raise FileProcessingError(f"Path is not a file: {filepath}")

        if filepath.suffix != ".md":
            raise FileProcessingError(f"Not a markdown file: {filepath}")

        try:
            with filepath.open(encoding="utf-8") as fp:
                first_line = fp.readline()
                if not first_line.strip():
                    raise FileProcessingError(f"Empty file: {filepath}")

                title = first_line.lstrip("#").strip()
                if not title:
                    raise FileProcessingError(f"No title found in file: {filepath}")

                body = fp.read().strip()

        except UnicodeDecodeError as e:
            raise FileProcessingError(f"Invalid encoding in file {filepath}: {e}")
        except OSError as e:
            raise FileProcessingError(f"Failed to read file {filepath}: {e}")

        try:
            path = str(filepath.relative_to(self.config.root_path))
        except ValueError as e:
            raise FileProcessingError(f"File {filepath} is not under root path: {e}")

        slug = filepath.stem

        # Extract topic from path
        path_parts = path.split("/")
        if len(path_parts) < 3 or path_parts[0] != "content":
            raise FileProcessingError(
                f"Invalid file structure, expected content/topic/file.md: {path}"
            )

        topic = path_parts[1]
        url = f"{self.config.github_url_base}/blob/main/{path}"
        path_slug = path.replace("/", "_")

        return {
            "path": path_slug,
            "slug": slug,
            "topic": topic,
            "title": title,
            "url": url,
            "body": body,
        }

    def should_update_html(self, record: dict[str, Any]) -> bool:
        """Check if HTML needs to be updated for a record.

        Args:
            record: Current record data

        Returns:
            True if HTML needs updating, False otherwise

        """
        try:
            previous_record = self.database.get_previous_record(record["path"])
            if not previous_record:
                return True

            return record["body"] != previous_record.get(
                "body"
            ) or not previous_record.get("html")
        except Exception as e:
            logger.warning(f"Error checking previous record: {e}")
            return True

    def process_all_files(self) -> None:
        """Process all markdown files in the repository."""
        logger.info(f"Processing all files from {self.config.root_path}")

        # Get git history if available
        all_times = {}
        if self.repository:
            try:
                all_times = self.repository.get_file_history()
            except Exception as e:
                logger.warning(
                    f"Failed to get git history, continuing without timestamps: {e}"
                )

        # Find all markdown files
        try:
            markdown_files = list(self.config.root_path.glob("content/*/*.md"))
        except Exception as e:
            raise FileProcessingError(f"Failed to find markdown files: {e}")

        logger.info(f"Found {len(markdown_files)} markdown files")

        processed_count = 0
        error_count = 0

        for filepath in markdown_files:
            logger.info(f"Processing {filepath}")

            try:
                record = self.process_file(filepath)
            except FileProcessingError as e:
                logger.error(f"Failed to process {filepath}: {e}")
                error_count += 1
                continue

            if not record:
                error_count += 1
                continue

            path = str(filepath.relative_to(self.config.root_path))

            # Check if HTML needs updating
            if self.should_update_html(record):
                try:
                    html = self.renderer.render(record["body"])
                    if html:
                        record["html"] = html
                    else:
                        logger.error(f"Empty HTML returned for {path}, skipping")
                        error_count += 1
                        continue
                except Exception as e:
                    logger.error(f"Failed to render HTML for {path}: {e}")
                    error_count += 1
                    continue
            else:
                # Get existing HTML from database
                previous_record = self.database.get_previous_record(record["path"])
                if previous_record and previous_record.get("html"):
                    record["html"] = previous_record["html"]
                else:
                    logger.warning(f"No existing HTML found for {path}, rendering new")
                    try:
                        html = self.renderer.render(record["body"])
                        if html:
                            record["html"] = html
                        else:
                            logger.error(f"Empty HTML returned for {path}, skipping")
                            error_count += 1
                            continue
                    except Exception as e:
                        logger.error(f"Failed to render HTML for {path}: {e}")
                        error_count += 1
                        continue

            # Add timestamps from git history
            if path in all_times:
                record.update(all_times[path])
            else:
                logger.info(f"No git history found for {path}, using current time")
                # Add current time as fallback
                now = datetime.datetime.now()
                now_utc = now.astimezone(datetime.timezone.utc)
                record.update(
                    {
                        "created": now.isoformat(),
                        "created_utc": now_utc.isoformat(),
                        "updated": now.isoformat(),
                        "updated_utc": now_utc.isoformat(),
                    }
                )

            # Update database
            try:
                self.database.upsert_record(record)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to save record for {path}: {e}")
                error_count += 1
                continue

        # Enable full-text search
        try:
            self.database.enable_search()
        except Exception as e:
            logger.error(f"Failed to enable full-text search: {e}")

        logger.info(
            f"Database build complete. Processed: {processed_count}, Errors: {error_count}"
        )

        if error_count > 0 and processed_count == 0:
            raise FileProcessingError("No files were successfully processed")

    def build_database(self) -> None:
        """Build complete database from all markdown files.

        This is the main entry point for the processor.

        Raises:
            FileProcessingError: If no files could be processed

        """
        try:
            self.process_all_files()
        except Exception as e:
            logger.error(f"Database build failed: {e}")
            raise
