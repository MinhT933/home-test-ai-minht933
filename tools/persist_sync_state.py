"""Persist verified worker state on sync-state without overwriting concurrent work."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.checkpoint import merge_checkpoint, read_checkpoint, validate_checkpoint


BRANCH = "sync-state"


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed")
    return result.stdout.strip()


def remote_json(repo: Path, commit: str, path: str, *, missing_ok: bool = False) -> object:
    present = git(repo, "ls-tree", "--name-only", commit, "--", path)
    if not present:
        if missing_ok:
            return {}
        raise ValueError(f"remote {path} is missing")
    return json.loads(git(repo, "show", f"{commit}:{path}"))


def history(data: object) -> dict[str, int]:
    if (not isinstance(data, dict)
            or any(not isinstance(key, str) or not key.isdigit()
                   or type(value) is not int or value < 0
                   for key, value in data.items())):
        raise ValueError("failure history is invalid")
    return data


def persist(repo: Path, base: Path, local: Path, prior_history: Path,
            next_history: Path) -> str:
    base_records = read_checkpoint(base)
    local_records = read_checkpoint(local)
    prior = history(json.loads(prior_history.read_text(encoding="utf-8")))
    next_state = history(json.loads(next_history.read_text(encoding="utf-8")))

    git(repo, "fetch", "--no-tags", "origin",
        f"refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    latest_commit = git(repo, "rev-parse", f"refs/remotes/origin/{BRANCH}")
    latest_records = validate_checkpoint(remote_json(repo, latest_commit, "sync-state.json"))
    latest_history = history(remote_json(repo, latest_commit, "failure-streaks.json",
                                         missing_ok=True))
    if latest_history != prior:
        raise ValueError("failure history changed since worker started")
    merged = merge_checkpoint(base_records, local_records, latest_records)

    with tempfile.TemporaryDirectory(prefix="sync-state-") as directory:
        worktree = Path(directory) / "checkout"
        git(repo, "worktree", "add", "--detach", str(worktree), latest_commit)
        try:
            (worktree / "sync-state.json").write_text(
                json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            (worktree / "failure-streaks.json").write_text(
                json.dumps(next_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            git(worktree, "add", "sync-state.json", "failure-streaks.json")
            # diff --quiet reports changes through its exit code, not stdout.
            diff_code = subprocess.run(["git", "-C", str(worktree), "diff", "--cached", "--quiet"],
                                       check=False).returncode
            if diff_code not in (0, 1):
                raise RuntimeError("could not compare staged checkpoint changes")
            changed = diff_code == 1
            if changed:
                git(worktree, "-c", "user.name=github-actions[bot]",
                    "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                    "commit", "-m", "Persist verified sync state")
                git(worktree, "push", "origin", f"HEAD:refs/heads/{BRANCH}")
            expected = git(worktree, "rev-parse", "HEAD")
        finally:
            git(repo, "worktree", "remove", "--force", str(worktree))

    git(repo, "fetch", "--no-tags", "origin",
        f"refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    actual = git(repo, "rev-parse", f"refs/remotes/origin/{BRANCH}")
    if actual != expected:
        raise RuntimeError("remote sync-state moved after persistence")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--prior-history", type=Path, required=True)
    parser.add_argument("--next-history", type=Path, required=True)
    args = parser.parse_args()
    commit = persist(args.repo, args.base, args.local, args.prior_history,
                     args.next_history)
    print(f"Verified sync-state commit {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
