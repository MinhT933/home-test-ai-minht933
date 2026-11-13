"""Validate and merge checkpoint snapshots before a compare-and-swap branch push."""

import json
from pathlib import Path


def read_checkpoint(path: Path) -> dict[str, dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_checkpoint(data)


def validate_checkpoint(data: object) -> dict[str, dict]:
    if not isinstance(data, dict):
        raise ValueError("checkpoint must be an object")
    for article_id, record in data.items():
        if (not isinstance(article_id, str) or not article_id.isdigit()
                or not isinstance(record, dict)
                or record.get("article_id") != article_id
                or not all(isinstance(record.get(key), str) and record[key]
                           for key in ("content_hash", "document_name", "last_successful_sync"))):
            raise ValueError("checkpoint contains an invalid record")
    return data


def merge_checkpoint(base: dict[str, dict], local: dict[str, dict],
                     latest: dict[str, dict]) -> dict[str, dict]:
    """Apply only local changes, rejecting keys changed remotely since base."""
    if set(base) - set(local):
        raise ValueError("local checkpoint removed records")
    if set(base) - set(latest):
        raise ValueError("latest checkpoint removed records")
    merged = dict(latest)
    for key, record in local.items():
        if base.get(key) == record:
            continue
        if latest.get(key) != base.get(key) and latest.get(key) != record:
            raise ValueError(f"checkpoint conflict for article {key}")
        merged[key] = record
    return merged
