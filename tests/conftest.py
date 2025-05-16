"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Generator, Dict, Optional

import pytest
import sqlite_utils

from git import Repo


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_git_repo(temp_dir: Path) -> Generator[Repo, None, None]:
    """Create a temporary git repository with sample TIL files."""
    repo = Repo.init(temp_dir)

    # Create sample TIL files
    python_dir = temp_dir / "python"
    python_dir.mkdir()

    til1 = python_dir / "test-til-1.md"
    til1.write_text("# Test TIL 1\n\nThis is a test TIL about Python.")

    til2 = python_dir / "test-til-2.md"
    til2.write_text("# Test TIL 2\n\nAnother test TIL with **bold** text.")

    # Configure git user for commits
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Create initial commit
    repo.index.add(["python/test-til-1.md", "python/test-til-2.md"])
    commit = repo.index.commit("Initial commit")

    # Ensure we have a branch reference
    if not repo.active_branch.name:
        repo.create_head("main", commit)

    # Create another TIL in a different topic
    bash_dir = temp_dir / "bash"
    bash_dir.mkdir()

    til3 = bash_dir / "bash-test.md"
    til3.write_text("# Bash Test\n\nA test TIL about bash scripting.")

    repo.index.add(["bash/bash-test.md"])
    repo.index.commit("Add bash TIL")

    # Create a main branch if the default is different (e.g., master)
    if repo.active_branch.name != "main":
        repo.create_head("main", force=True)
        repo.head.set_reference(repo.heads.main)
        repo.head.reset(index=True, working_tree=True)

    yield repo


@pytest.fixture
def temp_db(temp_dir: Path) -> sqlite_utils.Database:
    """Create a temporary SQLite database."""
    db_path = temp_dir / "test.db"
    return sqlite_utils.Database(db_path)


@pytest.fixture
def sample_til_record() -> Dict[str, str]:
    """Sample TIL record for testing."""
    return {
        "path": "python_test-til.md",
        "slug": "test-til",
        "topic": "python",
        "title": "Test TIL",
        "url": "https://github.com/jthodge/til/blob/main/python/test-til.md",
        "body": "# Test TIL\n\nThis is a test.",
        "html": "<h1>Test TIL</h1>\n<p>This is a test.</p>",
        "created": "2023-01-01T00:00:00",
        "created_utc": "2023-01-01T00:00:00+00:00",
        "updated": "2023-01-02T00:00:00",
        "updated_utc": "2023-01-02T00:00:00+00:00",
    }


@pytest.fixture
def mock_github_api(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock GitHub API responses."""
    import httpx

    class MockResponse:
        def __init__(self, text: str, status_code: int = 200) -> None:
            self.text = text
            self.status_code = status_code

    def mock_post(
        url: str,
        *,
        json: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> MockResponse:
        if url == "https://api.github.com/markdown" and json is not None:
            # Simple markdown to HTML conversion
            text = json["text"]
            html = text.replace("# ", "<h1>").replace("\n", "</h1>\n<p>", 1) + "</p>"
            html = html.replace("**", "<strong>").replace("**", "</strong>")
            return MockResponse(html)
        return MockResponse("", 404)

    monkeypatch.setattr(httpx, "post", mock_post)
