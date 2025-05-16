"""Git repository operations for TIL."""

import logging
import pathlib
from datetime import timezone
from typing import Dict, Optional

import git

logger = logging.getLogger(__name__)


class GitRepository:
    """Handle all git-related operations."""

    def __init__(self, path: pathlib.Path):
        """Initialize GitRepository with path to repository.

        Args:
            path: Path to git repository
        """
        self.path = path
        try:
            self.repo = git.Repo(path, odbt=git.GitDB)
        except git.InvalidGitRepositoryError as e:
            logger.error(f"Invalid git repository at {path}: {e}")
            raise

    def get_current_branch(self) -> str:
        """Get the current branch name.

        Returns:
            Current branch name or "HEAD" if detached
        """
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Detached HEAD state
            return "HEAD"

    def get_file_history(self, ref: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """Extract created/changed times from git history.

        Args:
            ref: Git reference to use (default: None to use current branch)

        Returns:
            Dictionary mapping file paths to created/updated times
        """
        created_changed_times: Dict[str, Dict[str, str]] = {}

        # Use current branch if ref not specified
        if ref is None:
            ref = self.get_current_branch()

        try:
            commits = reversed(list(self.repo.iter_commits(ref)))
        except git.GitCommandError as e:
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
