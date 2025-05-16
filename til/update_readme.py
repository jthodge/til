"""Update README with latest TIL entries."""

import logging
import pathlib
import re
import sys
from typing import Dict, List

import sqlite_utils

from .config import TILConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Regular expressions for finding index sections
INDEX_RE = re.compile(r"<!\-\- index starts \-\->.*<!\-\- index ends \-\->", re.DOTALL)
COUNT_RE = re.compile(r"<!\-\- count starts \-\->.*<!\-\- count ends \-\->", re.DOTALL)

COUNT_TEMPLATE = "<!-- count starts -->{}<!-- count ends -->"


def build_index(db: sqlite_utils.Database) -> List[str]:
    """Build index of TIL entries grouped by topic.

    Args:
        db: SQLite database containing TIL entries

    Returns:
        List of index lines to be inserted into README
    """
    by_topic: Dict[str, List[Dict]] = {}

    # Group entries by topic
    for row in db["til"].rows_where(order_by="created_utc"):
        by_topic.setdefault(row["topic"], []).append(row)

    # Build index lines
    index = ["<!-- index starts -->"]

    for topic, rows in sorted(by_topic.items()):
        index.append(f"## {topic}\n")

        for row in rows:
            date = row["created"].split("T")[0]
            index.append(f"* [{row['title']}]({row['url']}) - {date}")
        index.append("")

    # Remove trailing empty line if present
    if index[-1] == "":
        index.pop()

    index.append("<!-- index ends -->")

    return index


def update_readme_file(
    readme_path: pathlib.Path, index_lines: List[str], total_count: int
) -> None:
    """Update README file with new index and count.

    Args:
        readme_path: Path to README.md file
        index_lines: Lines containing the index to insert
        total_count: Total number of TIL entries
    """
    try:
        with readme_path.open() as f:
            readme_contents = f.read()
    except IOError as e:
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
    except IOError as e:
        logger.error(f"Failed to write README: {e}")


def main() -> None:
    """Main entry point."""
    config = TILConfig.from_environment()
    db = sqlite_utils.Database(config.database_path)

    # Build index
    index_lines = build_index(db)
    total_count = db["til"].count

    logger.info(f"Found {total_count} TIL entries")

    # Update README if --rewrite flag is present
    if "--rewrite" in sys.argv:
        readme_path = config.root_path / "README.md"
        logger.info(f"Updating {readme_path}")
        update_readme_file(readme_path, index_lines, total_count)
    else:
        # Just print the index
        print("\n".join(index_lines))


if __name__ == "__main__":
    main()
