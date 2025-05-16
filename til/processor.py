"""TIL processor orchestrating the entire pipeline."""

import logging
import pathlib
from typing import Any, Dict, Optional

from .config import TILConfig
from .database import TILDatabase
from .renderer import MarkdownRenderer
from .repository import GitRepository

logger = logging.getLogger(__name__)


class TILProcessor:
    """Orchestrate the TIL processing pipeline."""

    def __init__(self, config: TILConfig):
        """Initialize TILProcessor with configuration.

        Args:
            config: TIL configuration
        """
        self.config = config

        # Initialize components
        self.repository: Optional[GitRepository]
        try:
            self.repository = GitRepository(config.root_path)
        except Exception as e:
            logger.error(f"Failed to initialize git repository: {e}")
            self.repository = None

        self.renderer = MarkdownRenderer(config)
        self.database = TILDatabase(config.database_path)

    def process_file(self, filepath: pathlib.Path) -> Optional[Dict[str, Any]]:
        """Process a single markdown file.

        Args:
            filepath: Path to markdown file

        Returns:
            Dictionary containing record data or None if processing failed
        """
        try:
            with filepath.open() as fp:
                title = fp.readline().lstrip("#").strip()
                body = fp.read().strip()
        except IOError as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            return None

        path = str(filepath.relative_to(self.config.root_path))
        slug = filepath.stem
        url = f"{self.config.github_url_base}/blob/main/{path}"
        path_slug = path.replace("/", "_")
        topic = path.split("/")[0]

        record = {
            "path": path_slug,
            "slug": slug,
            "topic": topic,
            "title": title,
            "url": url,
            "body": body,
        }

        return record

    def should_update_html(self, record: Dict[str, Any]) -> bool:
        """Check if HTML needs to be updated for a record.

        Args:
            record: Current record data

        Returns:
            True if HTML needs updating, False otherwise
        """
        previous_record = self.database.get_previous_record(record["path"])
        if not previous_record:
            return True

        return record["body"] != previous_record.get("body") or not previous_record.get(
            "html"
        )

    def process_all_files(self) -> None:
        """Process all markdown files in the repository."""
        logger.info(f"Processing all files from {self.config.root_path}")

        # Get git history if available
        all_times = {}
        if self.repository:
            try:
                all_times = self.repository.get_file_history()
            except Exception as e:
                logger.error(f"Failed to get git history: {e}")

        # Find all markdown files
        markdown_files = list(self.config.root_path.glob("*/*.md"))
        logger.info(f"Found {len(markdown_files)} markdown files")

        for filepath in markdown_files:
            logger.info(f"Processing {filepath}")

            record = self.process_file(filepath)
            if not record:
                continue

            path = str(filepath.relative_to(self.config.root_path))

            # Check if HTML needs updating
            if self.should_update_html(record):
                html = self.renderer.render(record["body"])
                if html:
                    record["html"] = html
                else:
                    logger.error(f"Failed to render HTML for {path}")
                    continue
            else:
                # Get existing HTML from database
                previous_record = self.database.get_previous_record(record["path"])
                if previous_record:
                    record["html"] = previous_record["html"]

            # Add timestamps from git history
            if path in all_times:
                record.update(all_times[path])
            else:
                logger.warning(f"No git history found for {path}")

            # Update database
            self.database.upsert_record(record)

        # Enable full-text search
        self.database.enable_search()
        logger.info("Database build complete")

    def build_database(self) -> None:
        """Build complete database from all markdown files.

        This is the main entry point for the processor.
        """
        self.process_all_files()
