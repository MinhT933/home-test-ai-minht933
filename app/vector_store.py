"""Explicit commands for uploading documents to the configured vector store."""

import argparse
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

ARTICLES_DIR = Path("data/articles")
DEFAULT_STATUS_ARTICLE_ID = 360051014713


class UploadError(RuntimeError):
    """An upload failed, possibly after creating recoverable OpenAI files."""


def _configuration() -> str:
    load_dotenv()
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID", "").strip()
    if not vector_store_id:
        raise ValueError("Missing OPENAI_VECTOR_STORE_ID")
    return vector_store_id


def _validate_markdown_file(path: Path) -> Path:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Markdown file does not exist: {path}")
    if path.suffix.lower() != ".md":
        raise ValueError(f"Expected a Markdown file: {path}")
    return path


def _article_id(filename: str) -> int | None:
    match = re.match(r"^(\d+)(?:-|\.md$)", Path(filename).name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _remote_filenames(client: Any, vector_store_id: str) -> set[str]:
    names: set[str] = set()
    page = client.vector_stores.files.list(vector_store_id=vector_store_id, limit=100)
    while True:
        for item in page:
            file_id = getattr(item, "file_id", None) or getattr(item, "id", None)
            if file_id:
                filename = getattr(client.files.retrieve(file_id), "filename", None)
                if filename:
                    names.add(Path(filename).name)
        has_next_page = getattr(page, "has_next_page", None)
        if not callable(has_next_page) or not has_next_page():
            break
        page = page.get_next_page()
    return names


def vector_store_status(
    article_id: int = DEFAULT_STATUS_ARTICLE_ID, client: Any | None = None
) -> dict[str, Any]:
    """Read vector store counts and check whether an article ID is indexed."""
    if not isinstance(article_id, int) or isinstance(article_id, bool) or article_id <= 0:
        raise ValueError("article_id must be a positive integer")
    vector_store_id = _configuration()
    client = client or OpenAI()
    store = client.vector_stores.retrieve(vector_store_id)
    filenames = _remote_filenames(client, vector_store_id)
    return {
        "vector_store_id": vector_store_id,
        "file_counts": getattr(store, "file_counts", None),
        "article_id": article_id,
        "article_exists": article_id in {
            remote_id for name in filenames if (remote_id := _article_id(name)) is not None
        },
        "filenames": sorted(filenames),
    }


def upload_articles(directory: Path = ARTICLES_DIR, client: Any | None = None) -> Any:
    """Perform a guarded initial upload to an empty configured vector store."""
    vector_store_id = _configuration()
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Article directory does not exist: {directory}")
    files = sorted(directory.glob("*.md"))
    if not files:
        raise ValueError(f"No Markdown files found in {directory}")

    client = client or OpenAI()
    store = client.vector_stores.retrieve(vector_store_id)
    if getattr(getattr(store, "file_counts", None), "total", 0) > 0:
        raise RuntimeError(
            "Vector Store already has files; initial upload was refused to prevent duplicates"
        )

    uploaded: list[tuple[Path, str]] = []
    try:
        for path in files:
            with path.open("rb") as file:
                result = client.files.create(file=file, purpose="assistants")
            uploaded.append((path, result.id))
    except Exception as exc:
        recovery = ", ".join(f"{item.name}={file_id}" for item, file_id in uploaded)
        raise UploadError(
            f"Upload failed at {path.name}. Created files for recovery: {recovery or 'none'}"
        ) from exc

    file_ids = [file_id for _, file_id in uploaded]
    try:
        batch = client.vector_stores.file_batches.create_and_poll(
            vector_store_id=vector_store_id, file_ids=file_ids
        )
    except Exception as exc:
        raise UploadError(f"Indexing request failed; uploaded OpenAI file IDs: {file_ids}") from exc
    if getattr(batch, "status", None) != "completed":
        raise UploadError(
            f"Indexing ended with status {getattr(batch, 'status', 'unknown')}; "
            f"uploaded OpenAI file IDs: {file_ids}; counts: {getattr(batch, 'file_counts', None)}"
        )
    return batch


def upload_single_file(path: Path, client: Any | None = None) -> Any:
    """Upload one new Markdown file, refusing an existing remote article ID."""
    vector_store_id = _configuration()
    path = _validate_markdown_file(path)
    client = client or OpenAI()
    local_article_id = _article_id(path.name)
    remote_filenames = _remote_filenames(client, vector_store_id)
    remote_article_ids = {
        remote_id
        for name in remote_filenames
        if (remote_id := _article_id(name)) is not None
    }
    if local_article_id is not None and local_article_id in remote_article_ids:
        raise RuntimeError(
            f"Refusing duplicate upload: article {local_article_id} is already indexed"
        )
    if local_article_id is None and path.name in remote_filenames:
        raise RuntimeError(f"Refusing duplicate upload: {path.name} is already indexed")
    try:
        with path.open("rb") as file:
            result = client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store_id, file=file
            )
    except Exception as exc:
        raise UploadError(f"Failed to upload or index {path}") from exc
    if getattr(result, "status", None) != "completed":
        raise UploadError(
            f"Indexing {path.name} ended with status {getattr(result, 'status', 'unknown')}"
        )
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    initial = subparsers.add_parser("initial-upload")
    initial.add_argument("directory", nargs="?", type=Path, default=ARTICLES_DIR)
    single = subparsers.add_parser("upload-file")
    single.add_argument("path", type=Path)
    status = subparsers.add_parser("status")
    status.add_argument("article_id", nargs="?", type=int, default=DEFAULT_STATUS_ARTICLE_ID)
    args = parser.parse_args(argv)
    if args.command == "status":
        result = vector_store_status(args.article_id)
        counts = result["file_counts"]
        print(f"Vector Store file counts: {counts}")
        print(f"Article {args.article_id} indexed: {result['article_exists']}")
        return
    result = (
        upload_articles(args.directory)
        if args.command == "initial-upload"
        else upload_single_file(args.path)
    )
    print(f"Upload completed: {getattr(result, 'status', 'completed')}")


if __name__ == "__main__":
    main()
