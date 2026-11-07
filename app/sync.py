"""Safe delta synchronization between Markdown articles and Gemini File Search."""

import hashlib
import json
import os
import re
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

from google.genai import types

from app.gemini_store import article_id


def normalized_markdown(content: str) -> str:
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = "\n".join(line.rstrip() for line in lines).strip() + "\n"
    article_url = re.search(
        r"^Article URL:\s*(\S+)\s*$", normalized, flags=re.MULTILINE
    )
    if article_url:
        # A same-document absolute anchor and ``#anchor`` are semantically equal.
        normalized = normalized.replace(f"]({article_url.group(1)}#", "](#")
    return normalized


def content_hash(content: str) -> str:
    return hashlib.sha256(normalized_markdown(content).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class StateRecord:
    article_id: str
    content_hash: str
    document_name: str
    last_successful_sync: str
    verification_evidence: str | None = None


class StateStore(Protocol):
    """Replaceable checkpoint store; production should use durable cloud storage."""

    def get(self, article_id: str) -> StateRecord | None: ...

    def put(self, record: StateRecord) -> None: ...


class JsonManifestStateStore:
    """Atomic development adapter; not the production source of truth."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _records(self) -> dict[str, StateRecord]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {key: StateRecord(**value) for key, value in data.items()}

    def get(self, article_id: str) -> StateRecord | None:
        return self._records().get(article_id)

    def put(self, record: StateRecord) -> None:
        records = self._records()
        records[record.article_id] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {key: asdict(value) for key, value in records.items()}
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, prefix="sync-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(payload, output, indent=2, sort_keys=True)
                output.write("\n")
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


class MemoryStateStore:
    def __init__(self, records: Iterable[StateRecord] = ()):
        self.records = {record.article_id: record for record in records}

    def get(self, article_id: str) -> StateRecord | None:
        return self.records.get(article_id)

    def put(self, record: StateRecord) -> None:
        self.records[record.article_id] = record


@dataclass(frozen=True)
class RemoteDocument:
    name: str
    article_id: str | None
    content_hash: str | None
    state: str = "ACTIVE"
    last_successful_sync: str | None = None


class DocumentGateway(Protocol):
    def list_documents(self) -> list[RemoteDocument]: ...

    def upload(self, path: Path, article_id: str, digest: str, synced_at: str) -> RemoteDocument: ...

    def delete(self, document_name: str) -> None: ...


def _metadata(document: Any) -> dict[str, str]:
    return {
        item.key: item.string_value
        for item in (getattr(document, "custom_metadata", None) or [])
        if getattr(item, "key", None) and getattr(item, "string_value", None)
    }


def _document_state(document: Any) -> str:
    state = str(getattr(document, "state", "")).split(".")[-1]
    return state.removeprefix("STATE_")


class GeminiDocumentGateway:
    def __init__(self, client: Any, store_name: str, poll_interval: float = 3):
        self.client = client
        self.store_name = store_name
        self.poll_interval = poll_interval

    def list_documents(self) -> list[RemoteDocument]:
        result = []
        for document in self.client.file_search_stores.documents.list(parent=self.store_name):
            metadata = _metadata(document)
            stable_id = metadata.get("article_id") or article_id(document.display_name) or article_id(document.name)
            result.append(
                RemoteDocument(
                    name=document.name,
                    article_id=stable_id,
                    content_hash=metadata.get("content_hash"),
                    state=_document_state(document),
                    last_successful_sync=metadata.get("last_successful_sync"),
                )
            )
        return result

    def upload(self, path: Path, article_id: str, digest: str, synced_at: str) -> RemoteDocument:
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=str(path),
            file_search_store_name=self.store_name,
            config={
                "display_name": path.name,
                "custom_metadata": [
                    types.CustomMetadata(key="article_id", string_value=article_id),
                    types.CustomMetadata(key="content_hash", string_value=digest),
                    types.CustomMetadata(key="last_successful_sync", string_value=synced_at),
                ],
            },
        )
        while not operation.done:
            time.sleep(self.poll_interval)
            operation = self.client.operations.get(operation)
        if operation.error:
            raise RuntimeError(f"Indexing failed: {operation.error}")
        name = getattr(operation.response, "document_name", None)
        if not name:
            raise RuntimeError("Indexing completed without a document resource name")
        document = self.client.file_search_stores.documents.get(name=name)
        state = _document_state(document)
        if state != "ACTIVE":
            raise RuntimeError(f"Indexed document is not ACTIVE: {state or 'unknown'}")
        return RemoteDocument(name, article_id, digest, state, synced_at)

    def delete(self, document_name: str) -> None:
        self.client.file_search_stores.documents.delete(name=document_name, config={"force": True})


@dataclass
class SyncSummary:
    added: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    total_processed: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class BootstrapEntry:
    article_id: str
    local_path: str
    local_content_hash: str
    remote_document_name: str
    remote_state: str
    verified: bool = False


@dataclass
class BootstrapReport:
    generated_at: str
    entries: list[BootstrapEntry] = field(default_factory=list)
    issues: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "warning": (
                "Article-ID matching does not verify remote content. Confirm only from "
                "trusted upload records or separately verified content."
            ),
            "entries": [asdict(entry) for entry in self.entries],
            "issues": self.issues,
        }


def build_bootstrap_report(
    paths: Iterable[Path], documents: Iterable[RemoteDocument]
) -> BootstrapReport:
    local_by_id: dict[str, list[Path]] = {}
    report = BootstrapReport(datetime.now(timezone.utc).isoformat())
    for path in paths:
        stable_id = article_id(path.name)
        if stable_id is None:
            report.issues.append({"type": "ambiguous_local", "value": path.name})
        else:
            local_by_id.setdefault(stable_id, []).append(path)

    remote_by_id: dict[str, list[RemoteDocument]] = {}
    for document in documents:
        if document.article_id is None:
            report.issues.append(
                {"type": "ambiguous_remote", "value": document.name}
            )
        else:
            remote_by_id.setdefault(document.article_id, []).append(document)

    for stable_id in sorted(set(local_by_id) | set(remote_by_id)):
        local = local_by_id.get(stable_id, [])
        remote = remote_by_id.get(stable_id, [])
        if len(local) > 1:
            report.issues.append({"type": "duplicate_local", "article_id": stable_id})
            continue
        if len(remote) > 1:
            report.issues.append({"type": "duplicate_remote", "article_id": stable_id})
            continue
        if not local:
            report.issues.append({"type": "missing_local", "article_id": stable_id})
            continue
        if not remote:
            report.issues.append({"type": "missing_remote", "article_id": stable_id})
            continue
        if remote[0].state != "ACTIVE":
            report.issues.append(
                {
                    "type": "inactive_remote",
                    "article_id": stable_id,
                    "state": remote[0].state,
                }
            )
            continue
        report.entries.append(
            BootstrapEntry(
                article_id=stable_id,
                local_path=str(local[0]),
                local_content_hash=content_hash(local[0].read_text(encoding="utf-8")),
                remote_document_name=remote[0].name,
                remote_state=remote[0].state,
            )
        )
    return report


def write_bootstrap_report(report: BootstrapReport, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def confirm_bootstrap(
    report_path: Path,
    paths: Iterable[Path],
    gateway: DocumentGateway,
    state_store: StateStore,
    acknowledged: bool,
    verification_evidence: str,
) -> int:
    if not acknowledged or not verification_evidence.strip():
        raise ValueError(
            "Bootstrap confirmation requires explicit acknowledgement and verification evidence"
        )
    saved = json.loads(Path(report_path).read_text(encoding="utf-8"))
    current = build_bootstrap_report(paths, gateway.list_documents())
    if current.issues:
        raise RuntimeError(f"Bootstrap has unresolved issues: {current.issues}")
    saved_entries = saved.get("entries", [])
    current_entries = [asdict(entry) for entry in current.entries]
    if saved.get("issues") or saved_entries != current_entries:
        raise RuntimeError("Bootstrap report is stale or was modified; generate it again")

    confirmed_at = datetime.now(timezone.utc).isoformat()
    for entry in current.entries:
        state_store.put(
            StateRecord(
                article_id=entry.article_id,
                content_hash=entry.local_content_hash,
                document_name=entry.remote_document_name,
                last_successful_sync=confirmed_at,
                verification_evidence=verification_evidence.strip(),
            )
        )
    return len(current.entries)


def _log(event: str, **values: Any) -> None:
    print(json.dumps({"event": event, **values}, sort_keys=True))


def synchronize(
    paths: Iterable[Path],
    gateway: DocumentGateway,
    state_store: StateStore,
    dry_run: bool,
) -> SyncSummary:
    remote_by_id: dict[str, list[RemoteDocument]] = {}
    for document in gateway.list_documents():
        if document.article_id is not None:
            remote_by_id.setdefault(document.article_id, []).append(document)

    summary = SyncSummary()
    seen: set[str] = set()
    for path in paths:
        summary.total_processed += 1
        stable_id = article_id(path.name)
        if stable_id is None or stable_id in seen:
            reason = "invalid or duplicate local article ID"
            summary.failed += 1
            summary.failures.append({"file": path.name, "error": reason})
            _log("failed", file=path.name, error=reason)
            continue
        seen.add(stable_id)
        digest = content_hash(path.read_text(encoding="utf-8"))
        documents = remote_by_id.get(stable_id, [])
        record = state_store.get(stable_id)

        matching = [doc for doc in documents if doc.content_hash == digest and doc.state == "ACTIVE"]
        ambiguous = [doc for doc in documents if doc.content_hash is None]
        if matching:
            stale = [doc for doc in documents if doc.name != matching[0].name]
            if stale and (ambiguous or any(doc.content_hash is None for doc in stale)):
                reason = "ambiguous legacy duplicate requires explicit reconciliation"
                summary.failed += 1
                summary.failures.append({"article_id": stable_id, "error": reason})
                _log("failed", article_id=stable_id, error=reason)
                continue
            if not dry_run:
                try:
                    for document in stale:
                        gateway.delete(document.name)
                    state_store.put(
                        StateRecord(stable_id, digest, matching[0].name, matching[0].last_successful_sync or datetime.now(timezone.utc).isoformat())
                    )
                except Exception as exc:
                    summary.failed += 1
                    summary.failures.append({"article_id": stable_id, "error": str(exc)})
                    _log("failed", article_id=stable_id, error=str(exc))
                    continue
            summary.skipped += 1
            _log("skipped", article_id=stable_id, content_hash=digest)
            continue

        reconciled_legacy = (
            record
            and record.content_hash == digest
            and record.document_name
            in {doc.name for doc in ambiguous if doc.state == "ACTIVE"}
        )
        if reconciled_legacy:
            summary.skipped += 1
            _log(
                "skipped",
                article_id=stable_id,
                content_hash=digest,
                source="reconciled_legacy_state",
            )
            continue

        if ambiguous and not (
            record
            and record.document_name
            in {doc.name for doc in ambiguous if doc.state == "ACTIVE"}
        ):
            reason = "legacy document has no verified content hash; bootstrap reconciliation required"
            summary.failed += 1
            summary.failures.append({"article_id": stable_id, "error": reason})
            _log("failed", article_id=stable_id, error=reason)
            continue

        old_document = None
        if documents:
            if len(documents) != 1:
                reason = "multiple remote documents with no current hash match"
                summary.failed += 1
                summary.failures.append({"article_id": stable_id, "error": reason})
                _log("failed", article_id=stable_id, error=reason)
                continue
            old_document = documents[0]
        action = "updated" if old_document else "added"
        if dry_run:
            setattr(summary, action, getattr(summary, action) + 1)
            _log(action, article_id=stable_id, content_hash=digest, dry_run=True)
            continue

        synced_at = datetime.now(timezone.utc).isoformat()
        try:
            new_document = gateway.upload(path, stable_id, digest, synced_at)
            if old_document:
                gateway.delete(old_document.name)
            state_store.put(StateRecord(stable_id, digest, new_document.name, synced_at))
        except Exception as exc:
            summary.failed += 1
            summary.failures.append({"article_id": stable_id, "error": str(exc)})
            _log("failed", article_id=stable_id, error=str(exc))
            continue
        setattr(summary, action, getattr(summary, action) + 1)
        _log(action, article_id=stable_id, content_hash=digest, document_name=new_document.name)

    _log("summary", **asdict(summary))
    return summary
