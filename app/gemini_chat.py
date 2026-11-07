"""Minimal OptiBot chatbot backed by an existing Gemini File Search Store."""

import argparse
import os
import re
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash-lite"
API_VERSION = "v1beta"
QUESTION = "How do I add a YouTube video?"
EXPECTED_ARTICLE_URL = (
    "https://support.optisigns.com/hc/en-us/articles/360051014713"
)
SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""


@dataclass(frozen=True)
class ChatResult:
    answer: str
    grounding_metadata: dict[str, Any] | None
    cited_files: list[str]
    source_urls: list[str]
    grounding_store_names: list[str]
    bullet_count: int

    @property
    def contains_expected_url(self) -> bool:
        return EXPECTED_ARTICLE_URL in self.answer or EXPECTED_ARTICLE_URL in self.source_urls

    @property
    def respects_bullet_limit(self) -> bool:
        return self.bullet_count <= 5

    @property
    def retrieval_citations_returned(self) -> bool:
        chunks = (self.grounding_metadata or {}).get("grounding_chunks") or []
        return bool(chunks)


def _grounding_metadata(response: Any) -> Any | None:
    candidates = getattr(response, "candidates", None) or []
    return getattr(candidates[0], "grounding_metadata", None) if candidates else None


def _extract_citations(
    metadata: Any | None,
) -> tuple[list[str], list[str], list[str]]:
    files: set[str] = set()
    urls: set[str] = set()
    stores: set[str] = set()
    for chunk in getattr(metadata, "grounding_chunks", None) or []:
        context = getattr(chunk, "retrieved_context", None)
        if context is None:
            continue
        if getattr(context, "title", None):
            files.add(context.title)
        if (getattr(context, "uri", None) or "").startswith(("http://", "https://")):
            urls.add(context.uri)
        if getattr(context, "file_search_store", None):
            stores.add(context.file_search_store)
        text = getattr(context, "text", None) or ""
        urls.update(
            re.findall(r"Article URL:\s*(https?://[^\s)\]>]+)", text, flags=re.IGNORECASE)
        )
    return sorted(files), sorted(urls), sorted(stores)


def _bullet_count(answer: str) -> int:
    return sum(
        bool(re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line))
        for line in answer.splitlines()
    )


def ask_optibot(client: Any, store_name: str) -> ChatResult:
    """Ask the fixed take-home question using one existing File Search Store."""
    if not store_name.strip():
        raise ValueError("GEMINI_FILE_SEARCH_STORE_NAME is missing")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=QUESTION,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ],
            ),
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini File Search request failed: {exc}") from exc

    answer = getattr(response, "text", None) or ""
    metadata = _grounding_metadata(response)
    files, urls, stores = _extract_citations(metadata)
    metadata_dict = metadata.model_dump(mode="json") if metadata is not None else None
    return ChatResult(
        answer, metadata_dict, files, urls, stores, _bullet_count(answer)
    )


def create_client() -> genai.Client:
    """Create a Gemini Developer API client on the File Search API version."""
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is missing")
    return genai.Client(
        vertexai=False,
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(
            api_version=API_VERSION,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def format_demo(result: ChatResult, store_name: str) -> str:
    """Format a concise, screenshot-friendly demonstration."""
    cited_urls = "\n".join(f"  - {url}" for url in result.source_urls) or "  (none returned)"
    cited_files = "\n".join(f"  - {name}" for name in result.cited_files) or "  (none returned)"
    grounded_stores = (
        "\n".join(f"  - {name}" for name in result.grounding_store_names)
        or "  (none returned)"
    )
    return "\n".join(
        [
            "=" * 72,
            "OptiBot Mini-Clone - Gemini File Search Demo",
            "=" * 72,
            f"Model: {MODEL}",
            f"File Search Store: {store_name}",
            f"User: {QUESTION}",
            "-" * 72,
            "OptiBot:",
            result.answer,
            "-" * 72,
            "Grounding evidence",
            "Citations returned: "
            + ("YES" if result.retrieval_citations_returned else "NO"),
            "Cited article URLs:",
            cited_urls,
            "Grounding source files:",
            cited_files,
            "Grounding stores:",
            grounded_stores,
            f"Expected YouTube article cited: {result.contains_expected_url}",
            f"Bullet points: {result.bullet_count}",
            f"Maximum 5 bullets respected: {result.respects_bullet_limit}",
            "=" * 72,
        ]
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo"])
    parser.parse_args(argv)
    load_dotenv()
    store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME")
    if not store_name:
        raise RuntimeError("GEMINI_FILE_SEARCH_STORE_NAME is missing")

    result = ask_optibot(create_client(), store_name)
    print(format_demo(result, store_name))


if __name__ == "__main__":
    main()
