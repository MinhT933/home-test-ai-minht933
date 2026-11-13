from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import main as worker_main


ROOT = Path(__file__).resolve().parents[1]


def test_container_is_non_root_one_shot_worker():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.13-slim" in dockerfile
    assert "PYTHONUNBUFFERED=1" in dockerfile
    assert "USER worker" in dockerfile
    assert 'ENTRYPOINT ["python", "main.py"]' in dockerfile
    assert 'CMD ["--sync", "--state-file", "/state/sync-state.json"]' in dockerfile
    assert "COPY . ." not in dockerfile


def test_dockerignore_excludes_credentials_state_and_artifacts():
    ignored = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    for value in [".env", ".venv/", ".git/", ".pytest_cache/", ".sync-state/", "screenshots/"]:
        assert value in ignored


def test_missing_checkpoint_fails_closed_before_api_client(monkeypatch, tmp_path):
    create_client = Mock()
    monkeypatch.setattr(worker_main, "create_client", create_client)

    result = worker_main.main(
        ["--sync", "--state-file", str(tmp_path / "missing.json")]
    )

    assert result == 2
    create_client.assert_not_called()


def test_corrupt_checkpoint_fails_before_gemini_client(monkeypatch, tmp_path):
    state = tmp_path / "corrupt.json"
    state.write_text("{broken", encoding="utf-8")
    create_client = Mock()
    monkeypatch.setattr(worker_main, "create_client", create_client)

    assert worker_main.main(["--sync", "--state-file", str(state)]) == 2
    create_client.assert_not_called()


def test_successful_sync_returns_zero(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text("{}\n", encoding="utf-8")
    fetch = Mock(return_value=[Path("123.md")])
    monkeypatch.setattr(worker_main, "fetch_articles", fetch)
    monkeypatch.setattr(worker_main, "create_client", lambda: object())
    monkeypatch.setattr(worker_main, "configured_store_name", lambda: "fileSearchStores/test")
    monkeypatch.setattr(worker_main, "GeminiDocumentGateway", lambda *_: object())
    sync = Mock(return_value=SimpleNamespace(failed=0))
    monkeypatch.setattr(worker_main, "synchronize", sync)

    assert worker_main.main(["--sync", "--state-file", str(state)]) == 0
    fetch.assert_called_once_with(max_pages=None, strict=True)
    assert sync.call_args.kwargs["dry_run"] is False


def test_failed_sync_returns_nonzero(monkeypatch, tmp_path):
    state = tmp_path / "state.json"
    state.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        worker_main, "fetch_articles", Mock(return_value=[Path("123.md")])
    )
    monkeypatch.setattr(worker_main, "create_client", lambda: object())
    monkeypatch.setattr(worker_main, "configured_store_name", lambda: "fileSearchStores/test")
    monkeypatch.setattr(worker_main, "GeminiDocumentGateway", lambda *_: object())
    monkeypatch.setattr(
        worker_main, "synchronize", Mock(return_value=SimpleNamespace(failed=1))
    )

    assert worker_main.main(["--sync", "--state-file", str(state)]) == 1


def test_workflow_schedule_secrets_artifact_and_state_branch():
    workflow = (ROOT / ".github/workflows/daily-sync.yml").read_text(encoding="utf-8")
    # The documented 09:17 Vietnam schedule is 02:17 UTC.
    assert 'cron: "17 2 * * *"' in workflow
    assert "workflow_dispatch:" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "secrets.GEMINI_API_KEY" in workflow
    assert "secrets.GEMINI_FILE_SEARCH_STORE_NAME" in workflow
    assert "origin/sync-state:sync-state.json" in workflow
    assert "test -s .sync-state/sync-state.json" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "if: always()" in workflow
    assert "worker_exit=${PIPESTATUS[0]}" in workflow
    assert "--max-pages" not in workflow
    assert "optibot-sync:${{ github.sha }}" in workflow
    assert "tools/persist_sync_state.py" in workflow
    assert "--prepare-history" in workflow
    assert "--checkpoint-persisted" in workflow
    assert "ALLOW_PARTIAL_SUCCESS: ${{ vars.ALLOW_PARTIAL_SUCCESS || 'false' }}" in workflow
    assert "include-hidden-files: true" in workflow
    assert "git push --force" not in workflow
