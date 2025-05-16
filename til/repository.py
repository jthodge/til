"""Git repository operations for TIL."""

import logging
import pathlib
from datetime import timezone
from typing import Dict, Optional

import git

from .exceptions import RepositoryError

logger = logging.getLogger(__name__)


class GitRepository:
    """Handle all git-related operations."""

    def __init__(self, path: pathlib.Path):
        """Initialize GitRepository with path to repository.

        Args:
            path: Path to git repository

        Raises:
            RepositoryError: If path is not a valid git repository
        """
        self.path = path
        if not path.exists():
            raise RepositoryError(f"Path does not exist: {path}")

        try:
            self.repo = git.Repo(path, odbt=git.GitDB)
        except git.InvalidGitRepositoryError as e:
            raise RepositoryError(f"Not a valid git repository at {path}: {e}")
        except Exception as e:
            raise RepositoryError(f"Failed to initialize git repository at {path}: {e}")

    def get_current_branch(self) -> str:
        """Get the current branch name.

        Returns:
            Current branch name or "HEAD" if detached

        Raises:
            RepositoryError: If unable to determine current branch
        """
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Detached HEAD state
            logger.info("Repository is in detached HEAD state")
            return "HEAD"
        except Exception as e:
            raise RepositoryError(f"Failed to get current branch: {e}")

    def get_file_history(self, ref: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """Extract created/changed times from git history.

        Args:
            ref: Git reference to use (default: None to use current branch)

        Returns:
            Dictionary mapping file paths to created/updated times

        Raises:
            RepositoryError: If unable to retrieve git history
        """
        created_changed_times: Dict[str, Dict[str, str]] = {}

        # Use current branch if ref not specified
        if ref is None:
            try:
                ref = self.get_current_branch()
            except RepositoryError:
                logger.warning("Could not determine current branch, using HEAD")
                ref = "HEAD"

        try:
            commits = list(self.repo.iter_commits(ref))
            if not commits:
                logger.warning(f"No commits found for ref {ref}")
                return created_changed_times

            # Process in chronological order
            commits = list(reversed(commits))
        except git.GitCommandError as e:
            if "unknown revision" in str(e):
                raise RepositoryError(f"Invalid git reference '{ref}': {e}")
            else:
                raise RepositoryError(f"Failed to get commits for ref {ref}: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error getting commits: {e}")

        processed_count = 0
        for commit in commits:
            try:
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
                processed_count += 1
            except Exception as e:
                logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                continue

        logger.info(
            f"Processed {processed_count} commits, found history for {len(created_changed_times)} files"
        )
        return created_changed_times
