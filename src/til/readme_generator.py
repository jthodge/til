"""README generation functionality for TIL."""

import logging
import pathlib
import re

from .database import TILDatabase


logger = logging.getLogger(__name__)

# Regular expressions for finding index sections
INDEX_RE = re.compile(r"<!\-\- index starts \-\->.*<!\-\- index ends \-\->", re.DOTALL)
COUNT_RE = re.compile(r"<!\-\- count starts \-\->.*<!\-\- count ends \-\->", re.DOTALL)

COUNT_TEMPLATE = "<!-- count starts -->{}<!-- count ends -->"


class ReadmeGenerator:
    """Generate README content from TIL database."""

    def __init__(self, database: TILDatabase):
        """Initialize ReadmeGenerator with database.

        Args:
            database: TIL database instance

        """
        self.database = database

    def generate_index(self) -> list[str]:
        """Generate index lines for README.

        Returns:
            List of index lines to be inserted into README

        """
        by_topic = self.database.get_all_by_topic()

        # Build index lines
        index = ["<!-- index starts -->"]

        for topic, rows in sorted(by_topic.items()):
            index.append(f"## {topic}\n")

            # Deduplicate entries by slug
            seen_slugs = set()
            deduplicated_rows = []

            for row in rows:
                # Only add if we haven't seen this slug yet
                if row["slug"] not in seen_slugs:
                    seen_slugs.add(row["slug"])
                    deduplicated_rows.append(row)

            # Ensure all entries have content/ prefix in the URL for consistency
            for row in deduplicated_rows:
                # Handle entries without created dates (e.g., non-TIL files)
                if row.get("created"):
                    date = row["created"].split("T")[0]
                    # Make sure URL points to content directory
                    url = row["url"]
                    if "/content/" not in url and "/blob/main/" in url:
                        url = url.replace("/blob/main/", "/blob/main/content/", 1)
                    index.append(f"* [{row['title']}]({url}) - {date}")
                else:
                    # For entries without dates, just show the title and URL
                    url = row["url"]
                    if "/content/" not in url and "/blob/main/" in url:
                        url = url.replace("/blob/main/", "/blob/main/content/", 1)
                    index.append(f"* [{row['title']}]({url})")
            index.append("")

        # Remove trailing empty line if present
        if index[-1] == "":
            index.pop()

        index.append("<!-- index ends -->")

        return index

    def update_readme(self, readme_path: pathlib.Path) -> None:
        """Update README file with new index.

        Args:
            readme_path: Path to README.md file

        """
        index_lines = self.generate_index()
        total_count = self.database.count()

        try:
            with readme_path.open() as f:
                readme_contents = f.read()
        except OSError as e:
            logger.error(f"Failed to read README: {e}")
            return

        # Replace index section
        index_txt = "\n".join(index_lines).strip()
        updated_contents = INDEX_RE.sub(index_txt, readme_contents)

        # Replace count section
        updated_contents = COUNT_RE.sub(
            COUNT_TEMPLATE.format(total_count), updated_contents
        )

        # Write updated contents
        try:
            with readme_path.open("w") as f:
                f.write(updated_contents)
            logger.info("README updated successfully")
        except OSError as e:
            logger.error(f"Failed to write README: {e}")
