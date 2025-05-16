"""Build TIL database from markdown files."""

import logging
import pathlib
import time
from datetime import timezone
from typing import Dict, Optional, Any, cast

import git
import httpx
import sqlite_utils
from sqlite_utils.db import NotFoundError, Table

from .config import TILConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_created_changed_times(
    repo_path: pathlib.Path, ref: str = "main"
) -> Dict[str, Dict[str, str]]:
    """Extract created and updated times from git history.

    Args:
        repo_path: Path to git repository
        ref: Git reference to use (default: main)

    Returns:
        Dictionary mapping file paths to created/updated times
    """
    created_changed_times: Dict[str, Dict[str, str]] = {}
    repo = git.Repo(repo_path, odbt=git.GitDB)  # type: ignore[attr-defined]

    try:
        commits = reversed(list(repo.iter_commits(ref)))
    except git.GitCommandError as e:  # type: ignore[attr-defined]
        logger.error(f"Failed to get commits for ref {ref}: {e}")
        return created_changed_times

    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())

        for filepath in affected_files:
            # Ensure filepath is a string for dict key
            filepath_str = str(filepath)
            if filepath_str not in created_changed_times:
                created_changed_times[filepath_str] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath_str].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )

    return created_changed_times


def render_markdown_via_github(body: str, config: TILConfig) -> Optional[str]:
    """Render markdown to HTML using GitHub API.

    Args:
        body: Markdown content to render
        github_token: Optional GitHub API token
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Rendered HTML or None if failed
    """
    headers = {}
    if config.github_token:
        headers["authorization"] = f"Bearer {config.github_token}"

    for attempt in range(config.max_retries):
        try:
            response = httpx.post(
                "https://api.github.com/markdown",
                json={"mode": "markdown", "text": body},
                headers=headers,
                timeout=30.0,
            )

            if response.status_code == 200:
                logger.info("Successfully rendered markdown")
                return str(response.text)
            elif response.status_code == 401:
                logger.error("GitHub API returned 401 Unauthorized")
                return None
            else:
                logger.warning(
                    f"GitHub API returned {response.status_code}, "
                    f"attempt {attempt + 1}/{config.max_retries}"
                )

                if attempt < config.max_retries - 1:
                    logger.info(
                        f"Sleeping for {config.retry_delay} seconds before retry..."
                    )
                    time.sleep(config.retry_delay)

        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay)

    return None


def process_markdown_file(
    filepath: pathlib.Path, config: TILConfig
) -> Optional[Dict[str, Any]]:
    """Process a single markdown file into a database record.

    Args:
        filepath: Path to markdown file
        root: Root directory of the project
        github_token: Optional GitHub API token

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

    path = str(filepath.relative_to(config.root_path))
    slug = filepath.stem
    url = f"{config.github_url_base}/blob/main/{path}"
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


def build_database(config: TILConfig) -> None:
    """Build SQLite database from markdown files in repository.

    Args:
        config: TIL configuration
    """
    logger.info(f"Building database from {config.root_path}")

    all_times = get_created_changed_times(config.root_path)
    db = sqlite_utils.Database(config.database_path)
    table = db.table("til", pk="path")

    markdown_files = list(config.root_path.glob("*/*.md"))
    logger.info(f"Found {len(markdown_files)} markdown files")

    for filepath in markdown_files:
        logger.info(f"Processing {filepath}")

        record = process_markdown_file(filepath, config)
        if not record:
            continue

        path = str(filepath.relative_to(config.root_path))

        # Check if HTML needs to be updated
        try:
            row = table.get(record["path"])
            previous_body = row["body"]
            previous_html = row.get("html")
        except (NotFoundError, KeyError):
            previous_body = None
            previous_html = None

        if record["body"] != previous_body or not previous_html:
            html = render_markdown_via_github(record["body"], config)
            if html:
                record["html"] = html
            else:
                logger.error(f"Failed to render HTML for {path}")
                continue

        # Add timestamps from git history
        if path in all_times:
            record.update(all_times[path])
        else:
            logger.warning(f"No git history found for {path}")

        # Update database
        with db.conn:
            table.upsert(record, alter=True)

    # Enable full-text search
    logger.info("Enabling full-text search...")
    table.enable_fts(
        ["title", "body"], tokenize="porter", create_triggers=True, replace=True
    )

    logger.info("Database build complete")


def main() -> None:
    """Main entry point."""
    config = TILConfig.from_environment()
    build_database(config)


if __name__ == "__main__":
    main()
