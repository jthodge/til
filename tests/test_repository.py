"""Tests for GitRepository class."""

import pathlib
from datetime import timezone
from pathlib import Path

import pytest

import git
from git import Repo
from til.exceptions import RepositoryError
from til.repository import GitRepository


def test_git_repository_initialization(temp_git_repo: Repo) -> None:
    """Test GitRepository initialization with valid repo."""
    repo_path = temp_git_repo.working_dir
    git_repo = GitRepository(pathlib.Path(repo_path))

    assert git_repo.path == pathlib.Path(repo_path)
    assert isinstance(git_repo.repo, git.Repo)


def test_git_repository_initialization_invalid_path(temp_dir: Path) -> None:
    """Test GitRepository initialization with non-git directory."""
    with pytest.raises(RepositoryError, match="Not a valid git repository"):
        GitRepository(temp_dir)


def test_git_repository_initialization_nonexistent_path() -> None:
    """Test GitRepository initialization with nonexistent path."""
    with pytest.raises(RepositoryError, match="Path does not exist"):
        GitRepository(Path("/nonexistent/path"))


def test_get_current_branch(temp_git_repo: Repo) -> None:
    """Test getting current branch name."""
    repo_path = temp_git_repo.working_dir
    git_repo = GitRepository(pathlib.Path(repo_path))

    # The temp_git_repo fixture creates a branch, so we check for that
    branch_name = git_repo.get_current_branch()
    assert branch_name == temp_git_repo.active_branch.name


def test_get_current_branch_detached_head(temp_git_repo: Repo) -> None:
    """Test getting branch name when in detached HEAD state."""
    repo_path = temp_git_repo.working_dir

    # Checkout a commit (detached HEAD)
    temp_git_repo.head.set_reference(temp_git_repo.head.commit)

    git_repo = GitRepository(pathlib.Path(repo_path))
    branch_name = git_repo.get_current_branch()
    assert branch_name == "HEAD"


def test_get_file_history(temp_git_repo: Repo) -> None:
    """Test extracting file history from git."""
    repo_path = temp_git_repo.working_dir
    git_repo = GitRepository(pathlib.Path(repo_path))

    history = git_repo.get_file_history()

    # Check that we have history for our test files
    assert "python/test-til-1.md" in history
    assert "python/test-til-2.md" in history
    assert "bash/bash-test.md" in history

    # Check structure of history entries
    for filepath, times in history.items():
        assert "created" in times
        assert "created_utc" in times
        assert "updated" in times
        assert "updated_utc" in times

        # Verify UTC times end with timezone offset
        assert times["created_utc"].endswith("+00:00")
        assert times["updated_utc"].endswith("+00:00")


def test_get_file_history_with_ref(temp_git_repo: Repo) -> None:
    """Test extracting file history with specific ref."""
    repo_path = temp_git_repo.working_dir
    git_repo = GitRepository(pathlib.Path(repo_path))

    # Use explicit branch name
    branch_name = temp_git_repo.active_branch.name
    history = git_repo.get_file_history(ref=branch_name)

    assert "python/test-til-1.md" in history
    assert "python/test-til-2.md" in history


def test_get_file_history_invalid_ref(temp_git_repo: Repo) -> None:
    """Test extracting file history with invalid ref."""
    repo_path = temp_git_repo.working_dir
    git_repo = GitRepository(pathlib.Path(repo_path))

    # Should raise RepositoryError for invalid ref
    with pytest.raises(RepositoryError, match="bad revision"):
        git_repo.get_file_history(ref="nonexistent-branch")


def test_get_file_history_multiple_commits(temp_git_repo: Repo, temp_dir: Path) -> None:
    """Test file history with multiple commits to same file."""
    repo_path = temp_git_repo.working_dir

    # Create additional commits for the same file
    test_file = temp_dir / "python" / "test-til-1.md"
    test_file.write_text("# Updated Content\nNew content")
    # Use relative path for git add
    relative_path = "python/test-til-1.md"
    temp_git_repo.index.add([relative_path])
    second_commit = temp_git_repo.index.commit("Update test1.md")

    git_repo = GitRepository(pathlib.Path(repo_path))
    history = git_repo.get_file_history()

    # Check that updated times are from the second commit
    file_history = history["python/test-til-1.md"]
    updated_time = file_history["updated"]

    # The updated time should match the second commit
    assert updated_time == second_commit.committed_datetime.isoformat()
