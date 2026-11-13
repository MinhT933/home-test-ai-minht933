"""Exercise sync-state persistence against a local bare Git repository only."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.persist_sync_state import persist


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def record(article_id: str, digest: str) -> dict:
    return {"article_id": article_id, "content_hash": digest,
            "document_name": f"documents/{article_id}-{digest}",
            "last_successful_sync": digest}


@unittest.skipUnless(shutil.which("git"), "local git executable required")
class PersistStateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.remote = root / "remote.git"
        self.repo = root / "repo"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True,
                       capture_output=True)
        subprocess.run(["git", "init", "-b", "sync-state", str(self.repo)],
                       check=True, capture_output=True)
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "config", "user.name", "Local Test")
        git(self.repo, "config", "user.email", "local@example.invalid")
        self.base_data = {"123": record("123", "old")}
        (self.repo / "sync-state.json").write_text(json.dumps(self.base_data))
        git(self.repo, "add", "sync-state.json")
        git(self.repo, "commit", "-m", "base")
        git(self.repo, "push", "origin", "sync-state")
        self.base = root / "base.json"
        self.local = root / "local.json"
        self.prior = root / "prior.json"
        self.next = root / "next.json"
        self.base.write_text(json.dumps(self.base_data))
        self.local.write_text(json.dumps({**self.base_data, "456": record("456", "new")}))
        self.prior.write_text("{}")
        self.next.write_text('{"8899727608083": 1}')

    def test_partial_result_persists_verified_article_and_failure_history(self):
        persisted = persist(self.repo, self.base, self.local, self.prior, self.next)
        remote = git(self.repo, "ls-remote", "origin", "refs/heads/sync-state").split()[0]
        self.assertEqual(persisted, remote)
        checkpoint = json.loads(git(self.repo, "show", f"{persisted}:sync-state.json"))
        history = json.loads(git(self.repo, "show", f"{persisted}:failure-streaks.json"))
        self.assertEqual(set(checkpoint), {"123", "456"})
        self.assertEqual(history, {"8899727608083": 1})

    def test_changed_remote_article_fails_without_overwriting(self):
        latest = {"123": record("123", "concurrent")}
        (self.repo / "sync-state.json").write_text(json.dumps(latest))
        git(self.repo, "add", "sync-state.json")
        git(self.repo, "commit", "-m", "concurrent")
        git(self.repo, "push", "origin", "sync-state")
        before = git(self.repo, "ls-remote", "origin", "refs/heads/sync-state")
        self.local.write_text(json.dumps({"123": record("123", "mine")}))
        with self.assertRaisesRegex(ValueError, "conflict"):
            persist(self.repo, self.base, self.local, self.prior, self.next)
        self.assertEqual(before, git(self.repo, "ls-remote", "origin", "refs/heads/sync-state"))

    def test_unrelated_remote_article_is_preserved(self):
        latest = {**self.base_data, "999": record("999", "other")}
        (self.repo / "sync-state.json").write_text(json.dumps(latest))
        git(self.repo, "add", "sync-state.json")
        git(self.repo, "commit", "-m", "another article")
        git(self.repo, "push", "origin", "sync-state")
        persisted = persist(self.repo, self.base, self.local, self.prior, self.next)
        checkpoint = json.loads(git(self.repo, "show", f"{persisted}:sync-state.json"))
        self.assertEqual(set(checkpoint), {"123", "456", "999"})

    def test_changed_failure_history_is_not_overwritten(self):
        (self.repo / "failure-streaks.json").write_text('{"8899727608083": 4}')
        git(self.repo, "add", "failure-streaks.json")
        git(self.repo, "commit", "-m", "concurrent history")
        git(self.repo, "push", "origin", "sync-state")
        with self.assertRaisesRegex(ValueError, "history changed"):
            persist(self.repo, self.base, self.local, self.prior, self.next)

    def test_corrupt_checkpoint_fails_before_remote_write(self):
        before = git(self.repo, "ls-remote", "origin", "refs/heads/sync-state")
        self.local.write_text("{broken")
        with self.assertRaises(ValueError):
            persist(self.repo, self.base, self.local, self.prior, self.next)
        self.assertEqual(before, git(self.repo, "ls-remote", "origin", "refs/heads/sync-state"))
