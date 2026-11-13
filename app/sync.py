"""Safe delta synchronization between Markdown articles and Gemini File Search."""

import hashlib
import json
import os
import re
import tempfile
import time
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

from google.genai import types
from google.genai import errors as genai_errors

try:
    import httpx2 as sdk_http
except ImportError:  # Older google-genai releases use httpx.
    import httpx as sdk_http

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
        metadata = _metadata(document)
        if metadata.get("article_id") != article_id or metadata.get("content_hash") != digest:
            raise RuntimeError("Indexed document metadata does not match upload")
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
    failures: list[dict[str, Any]] = field(default_factory=list)
    articles: list[dict[str, Any]] = field(default_factory=list)


MAX_UPLOAD_RETRIES = 3
RETRYABLE_UPLOAD_CODES = {429, 500, 502, 503, 504}


class UploadFailure(RuntimeError):
    def __init__(self, error: Exception, attempts: int, unsafe: bool = False):
        self.error = error
        self.attempts = attempts
        self.unsafe = unsafe
        super().__init__(safe_error(error))


def safe_error(error: Exception) -> str:
    """Keep actionable error information without logging SDK response bodies."""
    if isinstance(error, genai_errors.APIError):
        message = "Upload has already been terminated" if "Upload has already been terminated" in str(error.message) else ""
        return f"{type(error).__name__} HTTP {error.code}" + (f": {message}" if message else "")
    if str(error) in {"remote upload outcome is ambiguous", "remote upload outcome is not ACTIVE"}:
        return str(error)
    return type(error).__name__


def retryable_upload_error(error: Exception) -> bool:
    if isinstance(error, genai_errors.APIError):
        return error.code in RETRYABLE_UPLOAD_CODES
    return isinstance(error, (TimeoutError, ConnectionError,
                              sdk_http.TimeoutException, sdk_http.NetworkError))


def terminated_upload(error: Exception) -> bool:
    return (isinstance(error, genai_errors.APIError)
            and error.code == 400
            and "Upload has already been terminated" in str(error.message))


def _matching_after_error(
    gateway: DocumentGateway, stable_id: str, digest: str
) -> RemoteDocument | None:
    """Fail closed when the remote outcome could be ambiguous."""
    documents = [doc for doc in gateway.list_documents() if doc.article_id == stable_id]
    matching = [doc for doc in documents if doc.content_hash == digest and doc.state == "ACTIVE"]
    if len(matching) > 1 or any(doc.content_hash is None for doc in documents):
        raise RuntimeError("remote upload outcome is ambiguous")
    if any(doc.content_hash == digest and doc.state != "ACTIVE" for doc in documents):
        raise RuntimeError("remote upload outcome is not ACTIVE")
    return matching[0] if matching else None


def upload_with_retry(
    gateway: DocumentGateway, path: Path, stable_id: str, digest: str,
    synced_at: str, sleep=None,
) -> tuple[RemoteDocument, int]:
    sleep = sleep or time.sleep
    for retry_count in range(MAX_UPLOAD_RETRIES + 1):
        try:
            return gateway.upload(path, stable_id, digest, synced_at), retry_count
        except Exception as error:
            try:
                recovered = _matching_after_error(gateway, stable_id, digest)
            except Exception as verification_error:
                raise UploadFailure(verification_error, retry_count + 1, unsafe=True) from error
            if recovered:
                return recovered, retry_count
            if not retryable_upload_error(error) or retry_count == MAX_UPLOAD_RETRIES:
                raise UploadFailure(error, retry_count + 1,
                                    unsafe=terminated_upload(error)) from error
            delay = min(2 ** retry_count, 8) + random.uniform(0, 0.5)
            _log("upload_retry", article_id=stable_id, retry_count=retry_count + 1,
                 error_type=type(error).__name__, delay_seconds=round(delay, 2))
            sleep(delay)
            try:
                recovered = _matching_after_error(gateway, stable_id, digest)
            except Exception as verification_error:
                raise UploadFailure(verification_error, retry_count + 1, unsafe=True) from error
            if recovered:
                return recovered, retry_count + 1
    raise AssertionError("upload retry loop exhausted")


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


def _failed(summary: SyncSummary, stable_id: str | None, error: str,
            error_type: str, attempts: int = 0, file: str | None = None,
            critical: bool = False) -> None:
    entry = {"article_id": stable_id or "", "error": error,
             "error_type": error_type, "attempts": attempts,
             "retry_count": max(0, attempts - 1), "critical": critical}
    if file:
        entry["file"] = file
    summary.failed += 1
    summary.failures.append(entry)
    summary.articles.append({"article_id": stable_id or "", "status": "FAILED"})
    _log("failed", **entry)


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
            _failed(summary, stable_id, reason, "InvalidArticleId", file=path.name,
                    critical=True)
            continue
        seen.add(stable_id)
        digest = content_hash(path.read_text(encoding="utf-8"))
        documents = remote_by_id.get(stable_id, [])
        record = state_store.get(stable_id)

        matching = [doc for doc in documents if doc.content_hash == digest and doc.state == "ACTIVE"]
        ambiguous = [doc for doc in documents if doc.content_hash is None]
        if matching:
            if len(matching) != 1:
                _failed(summary, stable_id, "multiple verified documents require reconciliation", "DuplicateRemote")
                continue
            stale = [doc for doc in documents if doc.name != matching[0].name]
            if stale and (ambiguous or any(doc.content_hash is None for doc in stale)):
                reason = "ambiguous legacy duplicate requires explicit reconciliation"
                _failed(summary, stable_id, reason, "AmbiguousRemote")
                continue
            if not dry_run:
                try:
                    state_store.put(
                        StateRecord(stable_id, digest, matching[0].name, matching[0].last_successful_sync or datetime.now(timezone.utc).isoformat())
                    )
                except Exception as exc:
                    raise RuntimeError("checkpoint write failed") from exc
                try:
                    for document in stale:
                        gateway.delete(document.name)
                except Exception as exc:
                    _failed(summary, stable_id, safe_error(exc), type(exc).__name__)
                    continue
            summary.skipped += 1
            summary.articles.append({"article_id": stable_id, "status": "SKIPPED"})
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
            summary.articles.append({"article_id": stable_id, "status": "SKIPPED"})
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
            _failed(summary, stable_id, reason, "AmbiguousRemote")
            continue

        old_document = None
        if documents:
            if len(documents) != 1:
                reason = "multiple remote documents with no current hash match"
                _failed(summary, stable_id, reason, "DuplicateRemote")
                continue
            old_document = documents[0]
        action = "updated" if old_document else "added"
        if dry_run:
            setattr(summary, action, getattr(summary, action) + 1)
            summary.articles.append({"article_id": stable_id, "status": "SUCCESS", "dry_run": True})
            _log(action, article_id=stable_id, content_hash=digest, dry_run=True)
            continue

        synced_at = datetime.now(timezone.utc).isoformat()
        attempts = 0
        try:
            new_document, retry_count = upload_with_retry(gateway, path, stable_id, digest, synced_at)
            attempts = retry_count + 1
        except Exception as exc:
            if isinstance(exc, UploadFailure):
                _failed(summary, stable_id, str(exc), type(exc.error).__name__, exc.attempts,
                        critical=exc.unsafe)
            else:
                _failed(summary, stable_id, safe_error(exc), type(exc).__name__, attempts)
            continue
        try:
            state_store.put(StateRecord(stable_id, digest, new_document.name, synced_at))
        except Exception as exc:
            raise RuntimeError("checkpoint write failed") from exc
        if old_document:
            try:
                gateway.delete(old_document.name)
            except Exception as exc:
                _failed(summary, stable_id, safe_error(exc), type(exc).__name__, attempts)
                continue
        setattr(summary, action, getattr(summary, action) + 1)
        summary.articles.append({"article_id": stable_id, "status": "SUCCESS"})
        _log(action, article_id=stable_id, content_hash=digest, document_name=new_document.name)

    _log("summary", **asdict(summary))
    return summary
