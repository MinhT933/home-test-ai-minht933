"""Check the runner/container file boundary, including atomic replacement."""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/daily-sync.yml"


def test_workflow_restores_runner_access_before_host_reads_and_artifact_upload():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    grant = 'sudo chgrp -R "$(id -g)" .sync-state'
    chmod = 'sudo chmod -R g+rX .sync-state'
    assert workflow.count(grant) == workflow.count(chmod) == 2
    first = workflow.index(grant)
    second = workflow.index(grant, first + 1)
    assert first < workflow.index(chmod, first) < second
    assert second < workflow.index(chmod, second)
    assert workflow.index("--prepare-history") < first < workflow.index("python3 tools/persist_sync_state.py")
    assert workflow.index("echo 'persisted=true'") > workflow.index("python3 tools/persist_sync_state.py")
    assert workflow.index('echo "final_exit=$final_exit"') < second < workflow.index("uses: actions/upload-artifact@v4")


def test_atomic_replace_requires_new_file_access_grant(tmp_path):
    image = os.getenv("SYNC_PERMISSIONS_TEST_IMAGE")
    if not image or not shutil.which("docker") or os.geteuid() == 0:
        pytest.skip("set SYNC_PERMISSIONS_TEST_IMAGE and run as a non-root Docker user")
    if subprocess.run(["docker", "image", "inspect", image], capture_output=True).returncode:
        pytest.skip("local Docker test image is unavailable")

    state = tmp_path / "sync-state.json"
    state.write_text("{}\n", encoding="utf-8")
    prior_history = tmp_path / "failure-streaks.json"
    prior_history.write_text("{}\n", encoding="utf-8")
    tmp_path.chmod(0o2770)  # Setgid gives new files the runner's group.
    group = os.getgid()
    assert state.stat().st_uid == os.getuid()
    assert stat.S_IMODE(state.stat().st_mode) & stat.S_IRUSR
    print(f"before replace: {state.stat().st_uid}:{state.stat().st_gid} "
          f"{stat.S_IMODE(state.stat().st_mode):03o}")

    def container(code):
        subprocess.run([
            "docker", "run", "--rm", "--user", f"10001:{group}",
            "--volume", f"{tmp_path}:/state", "--entrypoint", "python", image,
            "-c", code,
        ], check=True, capture_output=True, text=True)

    container("""
import os, tempfile
from pathlib import Path
directory = Path('/state')
fd, temporary = tempfile.mkstemp(dir=directory, prefix='sync-', suffix='.json')
with os.fdopen(fd, 'w') as handle:
    handle.write('{"updated": true}\\n')
os.replace(temporary, directory / 'sync-state.json')
with tempfile.NamedTemporaryFile('w', dir=directory, delete=False) as handle:
    handle.write('{"status": "FAILED"}\\n')
    temporary = handle.name
os.replace(temporary, directory / 'final-report.json')
with tempfile.NamedTemporaryFile('w', dir=directory, delete=False) as handle:
    handle.write('{"123": 1}\\n')
    temporary = handle.name
os.replace(temporary, directory / 'next-failure-streaks.json')
""")

    report = tmp_path / "final-report.json"
    next_history = tmp_path / "next-failure-streaks.json"
    for path in (state, report, next_history):
        print(f"after replace {path.name}: {path.stat().st_uid}:{path.stat().st_gid} "
              f"{stat.S_IMODE(path.stat().st_mode):03o}")
        assert (path.stat().st_uid, path.stat().st_gid) == (10001, group)
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        with pytest.raises(PermissionError):
            path.read_text(encoding="utf-8")

    # This is the same group-read permission the workflow grants with sudo
    # after each Docker write. The container owner applies it in this local test.
    container("import os; [os.chmod('/state/' + name, 0o640) for name in "
              "('sync-state.json', 'final-report.json', 'next-failure-streaks.json')]")
    print(f"after grant: {stat.S_IMODE(state.stat().st_mode):03o}, "
          f"{stat.S_IMODE(report.stat().st_mode):03o}")
    assert '"updated": true' in state.read_text(encoding="utf-8")
    assert '"status": "FAILED"' in report.read_text(encoding="utf-8")
    assert prior_history.read_text(encoding="utf-8").strip() == "{}"
    assert '"123": 1' in next_history.read_text(encoding="utf-8")
