from pathlib import Path

from app.sync import (
    MemoryStateStore,
    RemoteDocument,
    StateRecord,
    build_bootstrap_report,
    confirm_bootstrap,
    content_hash,
    synchronize,
    write_bootstrap_report,
)
from google.genai import types


class FakeGateway:
    def __init__(self, documents=(), upload_error=None):
        self.documents = list(documents)
        self.upload_error = upload_error
        self.uploads = []
        self.deletes = []

    def list_documents(self):
        return list(self.documents)

    def upload(self, path, article_id, digest, synced_at):
        self.uploads.append(path.name)
        if self.upload_error:
            raise RuntimeError(self.upload_error)
        document = RemoteDocument(
            f"documents/{article_id}-new", article_id, digest, "ACTIVE", synced_at
        )
        self.documents.append(document)
        return document

    def delete(self, document_name):
        self.deletes.append(document_name)
        self.documents = [item for item in self.documents if item.name != document_name]


def markdown(tmp_path: Path, article_id="123", body="Body", title="Title") -> Path:
    path = tmp_path / f"{article_id}-{title.lower()}.md"
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    return path


def remote(path, digest=None, name="documents/123-old"):
    return RemoteDocument(name, "123", digest or content_hash(path.read_text(encoding="utf-8")))


def test_first_time_article_is_added(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway()
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert (result.added, result.updated, result.failed) == (1, 0, 0)
    assert gateway.uploads == [path.name]


def test_unchanged_content_is_skipped(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway([remote(path)])
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.skipped == 1
    assert gateway.uploads == []


def test_modified_content_is_updated_and_old_deleted_after_upload(tmp_path):
    path = markdown(tmp_path, body="New")
    gateway = FakeGateway([remote(path, digest=content_hash("Old"))])
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.updated == 1
    assert gateway.uploads == [path.name]
    assert gateway.deletes == ["documents/123-old"]


def test_changed_title_keeps_article_identity(tmp_path):
    path = markdown(tmp_path, title="Changed title")
    gateway = FakeGateway([remote(path, name="documents/123-original-title")])
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.skipped == 1


def test_failed_upload_preserves_existing_document(tmp_path):
    path = markdown(tmp_path, body="New")
    old = remote(path, digest=content_hash("Old"))
    gateway = FakeGateway([old], upload_error="upload failed")
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.failed == 1
    assert gateway.deletes == []
    assert old in gateway.documents


def test_failed_indexing_preserves_existing_document(tmp_path):
    path = markdown(tmp_path, body="New")
    old = remote(path, digest=content_hash("Old"))
    gateway = FakeGateway([old], upload_error="Indexing failed")
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.failed == 1
    assert gateway.deletes == []


def test_partial_zendesk_input_never_deletes_absent_articles(tmp_path):
    path = markdown(tmp_path)
    other = RemoteDocument("documents/999", "999", "hash")
    gateway = FakeGateway([remote(path), other])
    synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert "documents/999" not in gateway.deletes


def test_repeated_runs_do_not_create_duplicates(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway()
    state = MemoryStateStore()
    first = synchronize([path], gateway, state, dry_run=False)
    second = synchronize([path], gateway, state, dry_run=False)
    assert first.added == 1 and second.skipped == 1
    assert gateway.uploads == [path.name]


def test_dry_run_performs_no_remote_mutations(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway()
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=True)
    assert result.added == 1
    assert gateway.uploads == [] and gateway.deletes == []


def test_interrupted_update_is_reconciled_without_reupload(tmp_path):
    path = markdown(tmp_path, body="Current")
    digest = content_hash(path.read_text(encoding="utf-8"))
    gateway = FakeGateway(
        [
            RemoteDocument("documents/123-old", "123", content_hash("Old")),
            RemoteDocument("documents/123-new", "123", digest),
        ]
    )
    state = MemoryStateStore(
        [StateRecord("123", content_hash("Old"), "documents/123-old", "earlier")]
    )
    result = synchronize([path], gateway, state, dry_run=False)
    assert result.skipped == 1
    assert gateway.uploads == []
    assert gateway.deletes == ["documents/123-old"]
    assert state.get("123").document_name == "documents/123-new"


def test_legacy_document_without_verified_hash_fails_safely(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway([RemoteDocument("documents/123-legacy", "123", None)])
    result = synchronize([path], gateway, MemoryStateStore(), dry_run=False)
    assert result.failed == 1
    assert gateway.uploads == [] and gateway.deletes == []


def test_explicitly_reconciled_legacy_document_can_be_skipped(tmp_path):
    path = markdown(tmp_path)
    digest = content_hash(path.read_text(encoding="utf-8"))
    gateway = FakeGateway([RemoteDocument("documents/123-legacy", "123", None)])
    state = MemoryStateStore(
        [StateRecord("123", digest, "documents/123-legacy", "reconciled-at")]
    )

    result = synchronize([path], gateway, state, dry_run=False)

    assert result.skipped == 1
    assert gateway.uploads == [] and gateway.deletes == []


def test_inactive_reconciled_legacy_document_is_not_skipped(tmp_path):
    path = markdown(tmp_path)
    digest = content_hash(path.read_text(encoding="utf-8"))
    gateway = FakeGateway(
        [RemoteDocument("documents/123-legacy", "123", None, "PENDING")]
    )
    state = MemoryStateStore(
        [StateRecord("123", digest, "documents/123-legacy", "reconciled-at")]
    )

    result = synchronize([path], gateway, state, dry_run=False)

    assert result.skipped == 0
    assert result.failed == 1
    assert gateway.uploads == [] and gateway.deletes == []


def test_successful_legacy_bootstrap_and_rerun_are_idempotent(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway([RemoteDocument("documents/123-legacy", "123", None)])
    report_path = tmp_path / "bootstrap.json"
    report = build_bootstrap_report([path], gateway.list_documents())
    write_bootstrap_report(report, report_path)
    state = MemoryStateStore()

    first = confirm_bootstrap(
        report_path, [path], gateway, state, True, "trusted upload log run-1"
    )
    second = confirm_bootstrap(
        report_path, [path], gateway, state, True, "trusted upload log run-1"
    )

    assert first == second == 1
    assert len(state.records) == 1
    assert state.get("123").verification_evidence == "trusted upload log run-1"
    assert gateway.uploads == [] and gateway.deletes == []


def test_bootstrap_detects_duplicate_remote_article_ids(tmp_path):
    path = markdown(tmp_path)
    report = build_bootstrap_report(
        [path],
        [
            RemoteDocument("documents/123-a", "123", None),
            RemoteDocument("documents/123-b", "123", None),
        ],
    )
    assert {issue["type"] for issue in report.issues} == {"duplicate_remote"}
    assert report.entries == []


def test_bootstrap_detects_missing_local_and_remote_articles(tmp_path):
    local = markdown(tmp_path, article_id="123")
    report = build_bootstrap_report(
        [local], [RemoteDocument("documents/999", "999", None)]
    )
    assert {issue["type"] for issue in report.issues} == {
        "missing_local",
        "missing_remote",
    }


def test_bootstrap_rejects_unverified_confirmation(tmp_path):
    path = markdown(tmp_path)
    gateway = FakeGateway([RemoteDocument("documents/123", "123", None)])
    report_path = tmp_path / "bootstrap.json"
    write_bootstrap_report(
        build_bootstrap_report([path], gateway.list_documents()), report_path
    )

    try:
        confirm_bootstrap(report_path, [path], gateway, MemoryStateStore(), False, "")
    except ValueError as exc:
        assert "explicit acknowledgement" in str(exc)
    else:
        raise AssertionError("Unverified bootstrap must be rejected")
    assert gateway.uploads == [] and gateway.deletes == []


def test_bootstrap_report_does_not_claim_hash_is_verified(tmp_path):
    path = markdown(tmp_path)
    report = build_bootstrap_report(
        [path], [RemoteDocument("documents/123", "123", None)]
    )
    assert report.entries[0].verified is False
    assert "does not verify remote content" in report.to_dict()["warning"]


def test_gemini_active_state_is_normalized_for_bootstrap(monkeypatch, tmp_path):
    from app.sync import GeminiDocumentGateway

    path = markdown(tmp_path)
    document = type(
        "Document",
        (),
        {
            "name": "fileSearchStores/store/documents/123",
            "display_name": path.name,
            "custom_metadata": [],
            "state": types.DocumentState.STATE_ACTIVE,
        },
    )()
    client = type(
        "Client",
        (),
        {
            "file_search_stores": type(
                "Stores",
                (),
                {
                    "documents": type(
                        "Documents", (), {"list": lambda self, parent: [document]}
                    )()
                },
            )()
        },
    )()

    remote = GeminiDocumentGateway(client, "fileSearchStores/store").list_documents()
    report = build_bootstrap_report([path], remote)

    assert remote[0].state == "ACTIVE"
    assert len(report.entries) == 1
    assert report.issues == []


def test_structured_counters_are_accurate(tmp_path):
    added = markdown(tmp_path, article_id="111")
    skipped = markdown(tmp_path, article_id="222")
    failed = tmp_path / "invalid.md"
    failed.write_text("bad", encoding="utf-8")
    digest = content_hash(skipped.read_text(encoding="utf-8"))
    gateway = FakeGateway([RemoteDocument("documents/222", "222", digest)])
    result = synchronize([added, skipped, failed], gateway, MemoryStateStore(), dry_run=True)
    assert (result.added, result.updated, result.skipped, result.failed) == (1, 0, 1, 1)
    assert result.total_processed == 3


def test_hash_treats_relative_and_absolute_self_anchors_as_equal():
    relative = """# Guide

Article URL: https://example.com/articles/123-guide

* [Setup](#Setup)
"""
    absolute = """# Guide

Article URL: https://example.com/articles/123-guide

* [Setup](https://example.com/articles/123-guide#Setup)
"""

    assert content_hash(relative) == content_hash(absolute)
