from google.genai import errors
from app.sync import sdk_http
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from google.genai import types

from app.checkpoint import merge_checkpoint, read_checkpoint
from app.pipeline import PartialPolicy, evaluate
from app.sync import MemoryStateStore, RemoteDocument, SyncSummary, content_hash, synchronize, upload_with_retry


def article(tmp_path, article_id="123"):
    path = tmp_path / f"{article_id}.md"
    path.write_text("# Title\n\nNew body\n", encoding="utf-8")
    return path


class Gateway:
    def __init__(self, errors_to_raise=(), documents=(), accepted_on_error=False):
        self.errors = list(errors_to_raise)
        self.documents = list(documents)
        self.accepted_on_error = accepted_on_error
        self.uploads = 0
        self.deletes = []

    def list_documents(self):
        return list(self.documents)

    def upload(self, path, article_id, digest, synced_at):
        self.uploads += 1
        document = RemoteDocument(f"documents/{article_id}-new", article_id, digest, "ACTIVE", synced_at)
        if self.errors:
            error = self.errors.pop(0)
            if self.accepted_on_error:
                self.documents.append(document)
            raise error
        self.documents.append(document)
        return document

    def delete(self, name):
        self.deletes.append(name)
        self.documents = [item for item in self.documents if item.name != name]


def terminated():
    return errors.ClientError(400, {"message": "Upload has already been terminated"})


def test_transient_retry_is_bounded_and_recovers(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([TimeoutError(), TimeoutError(), TimeoutError()])
    document, retries = upload_with_retry(gateway, path, "123", content_hash(path.read_text()), "now", sleep=lambda _: None)
    assert document.state == "ACTIVE"
    assert (gateway.uploads, retries) == (4, 3)


def test_sdk_transport_timeout_is_retryable(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([sdk_http.ReadTimeout("timed out")])
    _, retries = upload_with_retry(gateway, path, "123", content_hash(path.read_text()), "now", sleep=lambda _: None)
    assert (gateway.uploads, retries) == (2, 1)


def test_http_503_retries_but_other_400_does_not(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([errors.ServerError(503, {"message": "unavailable"})])
    _, retries = upload_with_retry(gateway, path, "123", content_hash(path.read_text()), "now", sleep=lambda _: None)
    assert (gateway.uploads, retries) == (2, 1)
    permanent = Gateway([errors.ClientError(400, {"message": "bad input"})])
    result = synchronize([path], permanent, MemoryStateStore(), dry_run=False)
    assert (permanent.uploads, result.failed, result.failures[0]["critical"]) == (1, 1, False)


def test_permanent_400_is_not_retried(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([terminated()])
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.failed == 1
    assert result.failures[0]["retry_count"] == 0
    assert result.failures[0]["critical"] is True
    assert gateway.uploads == 1


def test_terminated_but_remote_active_is_reused_without_duplicate(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([terminated()], accepted_on_error=True)
    state = MemoryStateStore()
    first = synchronize([path], gateway, state, dry_run=False)
    second = synchronize([path], gateway, state, dry_run=False)
    assert (first.added, first.failed, second.skipped) == (1, 0, 1)
    assert gateway.uploads == 1
    assert len(gateway.documents) == 1


def test_ambiguous_remote_preserves_old_document_and_checkpoint(tmp_path):
    path = article(tmp_path)
    old = RemoteDocument("documents/123-old", "123", "old-hash")
    gateway = Gateway([terminated()], [old], accepted_on_error=True)
    original_list = gateway.list_documents
    def duplicate_list():
        docs = original_list()
        if gateway.uploads:
            docs.append(RemoteDocument("documents/123-duplicate", "123", content_hash(path.read_text())))
        return docs
    gateway.list_documents = duplicate_list
    state = MemoryStateStore()
    result = synchronize([path], gateway, state, dry_run=False)
    assert result.failed == 1
    assert gateway.deletes == []
    assert state.get("123") is None


def test_remote_read_failure_stops_retry_and_is_critical(tmp_path):
    path = article(tmp_path)
    gateway = Gateway([TimeoutError()])
    def unreadable():
        raise ConnectionError("remote unavailable")
    gateway.list_documents = unreadable
    try:
        upload_with_retry(gateway, path, "123", content_hash(path.read_text()), "now", sleep=lambda _: None)
    except Exception as exc:
        assert exc.unsafe is True
        assert exc.attempts == 1
    else:
        raise AssertionError("unverifiable upload must fail")
    assert gateway.uploads == 1


def test_other_article_continues_and_only_success_is_checkpointed(tmp_path):
    first, second = article(tmp_path, "123"), article(tmp_path, "456")
    gateway = Gateway([terminated()])
    state = MemoryStateStore()
    result = synchronize([first, second], gateway, state, dry_run=False)
    assert (result.failed, result.added) == (1, 1)
    assert state.get("123") is None
    assert state.get("456") is not None
    assert [entry["status"] for entry in result.articles] == ["FAILED", "SUCCESS"]


def test_partial_requires_persisted_checkpoint_and_enabled_policy():
    summary = SyncSummary(failed=1, total_processed=200, failures=[{"article_id": "123", "error": "HTTP 400"}])
    assert evaluate(summary, PartialPolicy(enabled=True), False)[0]["status"] == "FAILED"
    assert evaluate(summary, PartialPolicy(), True)[0]["status"] == "FAILED"
    assert evaluate(summary, PartialPolicy(enabled=True), True)[0]["status"] == "PARTIAL_SUCCESS"
    assert evaluate(summary, PartialPolicy(enabled=True), True, {"123": 1})[0]["status"] == "FAILED"
    summary.failures[0]["critical"] = True
    assert evaluate(summary, PartialPolicy(enabled=True), True)[0]["status"] == "FAILED"


def test_retry_exhaustion_keeps_old_and_does_not_checkpoint(tmp_path):
    path = article(tmp_path)
    old = RemoteDocument("documents/123-old", "123", "old-hash")
    gateway = Gateway([TimeoutError()] * 4, [old])
    state = MemoryStateStore()
    # Avoid real backoff in this integration test by patching the module's sleep.
    from unittest.mock import patch
    with patch("app.sync.time.sleep"):
        result = synchronize([path], gateway, state, dry_run=False)
    assert (gateway.uploads, result.failed, result.failures[0]["retry_count"]) == (4, 1, 3)
    assert gateway.deletes == []
    assert state.get("123") is None


def test_checkpoint_merge_preserves_unrelated_newer_records_and_rejects_conflict():
    base = {"123": {"article_id": "123", "content_hash": "old", "document_name": "old", "last_successful_sync": "old"}}
    local = {"123": {"article_id": "123", "content_hash": "new", "document_name": "new", "last_successful_sync": "new"}}
    latest = {**base, "456": {"article_id": "456", "content_hash": "other", "document_name": "other", "last_successful_sync": "other"}}
    assert merge_checkpoint(base, local, latest) == {**local, "456": latest["456"]}
    conflicting = {"123": {**base["123"], "document_name": "concurrent"}}
    try:
        merge_checkpoint(base, local, conflicting)
    except ValueError as exc:
        assert "conflict" in str(exc)
    else:
        raise AssertionError("stale checkpoint must be rejected")


def test_corrupt_checkpoint_is_not_replaced_with_empty_state(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{broken", encoding="utf-8")
    try:
        read_checkpoint(path)
    except ValueError:
        pass
    else:
        raise AssertionError("corrupt checkpoint must fail")


def test_gateway_rejects_active_document_with_wrong_metadata(tmp_path):
    from app.sync import GeminiDocumentGateway
    path = article(tmp_path)
    client = Mock()
    client.file_search_stores.upload_to_file_search_store.return_value = SimpleNamespace(
        done=True, error=None, response=SimpleNamespace(document_name="documents/new"))
    client.file_search_stores.documents.get.return_value = SimpleNamespace(
        state=types.DocumentState.STATE_ACTIVE,
        custom_metadata=[types.CustomMetadata(key="article_id", string_value="123"),
                         types.CustomMetadata(key="content_hash", string_value="wrong")])
    try:
        GeminiDocumentGateway(client, "fileSearchStores/test").upload(path, "123", "correct", "now")
    except RuntimeError as exc:
        assert "metadata" in str(exc)
    else:
        raise AssertionError("wrong remote metadata must not be verified")


def test_finalizer_requires_history_and_persisted_checkpoint(tmp_path):
    worker = tmp_path / "worker.json"
    worker.write_text(json.dumps(asdict(SyncSummary(total_processed=200, failed=1,
        failures=[{"article_id": "123", "error_type": "ClientError", "retry_count": 0}]))))
    output = tmp_path / "final.json"
    script = Path(__file__).resolve().parents[1] / "tools/finalize_sync_report.py"
    env = {**os.environ, "ALLOW_PARTIAL_SUCCESS": "true"}
    args = [sys.executable, str(script), "--worker-report", str(worker), "--output", str(output)]
    missing = subprocess.run(args, env=env, capture_output=True, text=True)
    assert missing.returncode != 0
    history = tmp_path / "history.json"
    history.write_text("{}")
    prepared = subprocess.run(args + ["--prior-streaks", str(history), "--prepare-history"],
                              env=env, capture_output=True, text=True)
    assert prepared.returncode == 0
    assert json.loads(output.read_text()) == {"123": 1}
    unpersisted = subprocess.run(args + ["--prior-streaks", str(history)], env=env,
                                 capture_output=True, text=True)
    assert unpersisted.returncode == 1
    assert json.loads(output.read_text())["status"] == "FAILED"
    persisted = subprocess.run(args + ["--prior-streaks", str(history), "--checkpoint-persisted"],
                               env=env, capture_output=True, text=True)
    assert persisted.returncode == 0
    assert json.loads(output.read_text())["status"] == "PARTIAL_SUCCESS"
