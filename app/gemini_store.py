"""One-time upload of missing Markdown articles to an existing Gemini store."""

import argparse
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types

ARTICLES_DIR = Path("data/articles")
ARTICLE_ID_PATTERN = re.compile(r"^(\d+)")


@dataclass
class UploadSummary:
    total: int
    added: int = 0
    skipped: int = 0
    failed: list[tuple[str, str]] = field(default_factory=list)
    initial_remote_count: int = 0

    @property
    def final_remote_count(self) -> int:
        return self.initial_remote_count + self.added


def create_client() -> genai.Client:
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Missing GEMINI_API_KEY")
    return genai.Client(
        vertexai=False,
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(
            api_version="v1beta",
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def configured_store_name() -> str:
    load_dotenv()
    name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME", "").strip()
    if not name.startswith("fileSearchStores/"):
        raise RuntimeError("GEMINI_FILE_SEARCH_STORE_NAME must be a full resource name")
    return name


def article_id(value: str | None) -> str | None:
    match = ARTICLE_ID_PATTERN.match(Path(value or "").name)
    return match.group(1) if match else None


def document_article_id(document: Any) -> str | None:
    for metadata in getattr(document, "custom_metadata", None) or []:
        if getattr(metadata, "key", None) == "article_id":
            value = getattr(metadata, "string_value", None)
            if value and value.isdigit():
                return value
    return article_id(getattr(document, "display_name", None)) or article_id(
        getattr(document, "name", None)
    )


def list_documents(client: Any, store_name: str) -> list[Any]:
    return list(client.file_search_stores.documents.list(parent=store_name))


def print_store_documents(client: Any, store_name: str) -> None:
    store = client.file_search_stores.get(name=store_name)
    documents = list_documents(client, store_name)

    print(f"Store ID: {store_name}")
    print(f"Active document count: {store.active_documents_count}")
    print(f"Total documents returned: {len(documents)}")
    for number, document in enumerate(documents, start=1):
        print(f"{number}. {document.display_name or document.name}")


def upload_missing_articles(
    client: Any,
    store_name: str,
    directory: Path = ARTICLES_DIR,
    poll_interval: float = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> UploadSummary:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Article directory does not exist: {directory}")
    files = sorted(directory.glob("*.md"))
    if not files:
        raise ValueError(f"No Markdown files found in {directory}")

    documents = list_documents(client, store_name)
    existing_ids = {
        stable_id
        for document in documents
        if (stable_id := document_article_id(document)) is not None
    }
    summary = UploadSummary(total=len(files), initial_remote_count=len(documents))

    for path in files:
        stable_id = article_id(path.name)
        if stable_id is None:
            summary.failed.append((path.name, "Filename does not start with an article ID"))
            continue
        if stable_id in existing_ids:
            summary.skipped += 1
            print(f"Skipped existing article {stable_id}: {path.name}")
            continue

        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(path),
                file_search_store_name=store_name,
                config={
                    "display_name": path.name,
                    "custom_metadata": [
                        types.CustomMetadata(key="article_id", string_value=stable_id)
                    ],
                },
            )
            while not operation.done:
                sleep(poll_interval)
                operation = client.operations.get(operation)
            if operation.error:
                raise RuntimeError(f"Indexing failed: {operation.error}")
        except Exception as exc:
            summary.failed.append((path.name, str(exc)))
            print(f"Failed article {stable_id}: {exc}")
            continue

        existing_ids.add(stable_id)
        summary.added += 1
        print(f"Indexed article {stable_id}: {path.name}")

    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["upload-missing", "list"])
    parser.add_argument("--directory", type=Path, default=ARTICLES_DIR)
    args = parser.parse_args(argv)

    store_name = configured_store_name()
    client = create_client()
    if args.command == "list":
        print_store_documents(client, store_name)
        return

    summary = upload_missing_articles(client, store_name, args.directory)
    print(f"Total local Markdown files: {summary.total}")
    print(f"Added: {summary.added}")
    print(f"Skipped: {summary.skipped}")
    print(f"Failed: {len(summary.failed)}")
    print(f"Final indexed document count: {summary.final_remote_count}")
    for filename, error in summary.failed:
        print(f"Failure: {filename}: {error}")


if __name__ == "__main__":
    main()
