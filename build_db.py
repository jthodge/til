import git
import httpx
import os
import pathlib
import sqlite_utils
import time

from datetime import timezone
from datasette.utils import tilde_encode
from sqlite_utils.db import NotFoundError

root = pathlib.Path(__file__).parent.resolve()


def created_changed_times(repo_path, ref="main"):
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref)))
    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times


def build_database(repo_path):
    all_times = created_changed_times(repo_path)
    db = sqlite_utils.Database(repo_path / "til.db")
    table = db.table("til", pk="path")

    for filepath in root.glob("*/*.md"):
        fp = filepath.open()
        title = fp.readline().lstrip("#").strip()
        body = fp.read().strip()
        path = str(filepath.relative_to(root))
        slug = filepath.stem
        url = "https://github.com/jthodge/til/blob/main/{}".format(path)
        path_slug = tilde_encode(path.replace("/", "_"))
        topic = path.split("/")[0]

        try:
            row = table.get(path_slug)
            previous_body = row["body"]
            previous_html = row["html"]
        except (NotFoundError, KeyError):
            previous_body = None
            previous_html = None

        record = {
            "path": path_slug,
            "slug": slug,
            "topic": topic,
            "title": title,
            "url": url,
            "body": body,
        }

        if (body != previous_body) or not previous_html:
            retries = 0
            response = None

            while retries < 3:
                headers = {}
                if os.environ.get("GITHUB_TOKEN"):
                    headers = {
                        "authorization": "Bearer {}".format(os.environ["GITHUB_TOKEN"])
                    }

                response = httpx.post(
                    "https://api.github.com/markdown",
                    json={
                        "mode": "markdown",
                        "text": body,
                    },
                    headers=headers,
                )

                if response.status_code == 200:
                    record["html"] = response.text
                    print("Rendered HTML for {}".format(path))
                    break
                elif response.status_code == 401:
                    assert False, "401 Unauthorized returned from GitHub API when rendering markdown"
                else:
                    print(response.status_code, response.headers)
                    print("  sleeping 60s")
                    time.sleep(60)
                    retries += 1
            else:
                assert False, "Could not render {} - last response was {}".format(
                    path, response.headers
                )

        record.update(all_times[path])
        with db.conn:
            table.upsert(record, alter=True)

    table.enable_fts(
        ["title", "body"], tokenize="porter", create_triggers=True, replace=True
    )


if __name__ == "__main__":
    build_database(root)

