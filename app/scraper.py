"""Collect Zendesk Help Center articles with bounded, rate-limit-aware retries."""

import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests

from app.markdown_converter import convert_html_to_markdown


API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
ARTICLE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles/{article_id}.json"

OUTPUT_DIR = Path("data/articles")
REQUEST_TIMEOUT = 15

# One initial request plus at most three retries.
MAX_RETRIES = 3

# HTTP 429 without Retry-After: 60, 120, 240 seconds.
RATE_LIMIT_BACKOFF_SECONDS = 60

# HTTP 5xx or network errors: 10, 20, 40 seconds.
TRANSIENT_BACKOFF_SECONDS = 10

# Maximum time allowed for a single retry delay.
MAX_RETRY_WAIT_SECONDS = 900

# Delay between successful pagination requests.
PAGE_DELAY_SECONDS = 1

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _retry_after_seconds(value: str | None) -> float | None:
    """Parse Retry-After as seconds or an HTTP date."""

    if value is None:
        return None

    try:
        seconds = float(value.strip())

        if 0 <= seconds < float("inf"):
            return seconds

    except (ValueError, OverflowError):
        pass

    try:
        retry_time = parsedate_to_datetime(value)

        if retry_time.tzinfo is None:
            retry_time = retry_time.replace(tzinfo=timezone.utc)

        return max(
            0.0,
            (retry_time - datetime.now(timezone.utc)).total_seconds(),
        )

    except (TypeError, ValueError, OverflowError, IndexError):
        return None


def _retry_delay(
    attempt: int,
    status: int | None,
    retry_after: str | None,
) -> float:
    """Respect Retry-After or use exponential backoff with jitter."""

    server_delay = _retry_after_seconds(retry_after)

    if server_delay is not None:
        # Never retry earlier than requested by the server.
        delay = max(1.0, server_delay) + random.uniform(0, 1)

    else:
        base = (
            RATE_LIMIT_BACKOFF_SECONDS
            if status == 429
            else TRANSIENT_BACKOFF_SECONDS
        )

        backoff = base * (2 ** attempt)

        delay = backoff + random.uniform(0, backoff * 0.1)

    if delay > MAX_RETRY_WAIT_SECONDS:
        raise RuntimeError(
            f"Zendesk retry requires waiting {delay:.0f}s, "
            f"exceeding the allowed {MAX_RETRY_WAIT_SECONDS}s; "
            "stopping without another request"
        )

    return delay


def _request_json(
    url: str,
    params: dict[str, int] | None = None,
) -> Any:
    """Fetch JSON with bounded retries for temporary failures."""

    for attempt in range(MAX_RETRIES + 1):

        try:
            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.HTTPError as exc:

            status = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            # Do not retry permanent errors or exhausted attempts.
            if (
                status not in RETRYABLE_STATUS_CODES
                or attempt == MAX_RETRIES
            ):
                raise

            retry_after = (
                exc.response.headers.get("Retry-After")
                if exc.response is not None
                else None
            )

            delay = _retry_delay(
                attempt=attempt,
                status=status,
                retry_after=retry_after,
            )

            source = (
                "Retry-After"
                if _retry_after_seconds(retry_after) is not None
                else "exponential backoff"
            )

            print(
                f"Zendesk HTTP {status}. "
                f"Retry {attempt + 1}/{MAX_RETRIES} "
                f"after {delay:.0f}s ({source}).",
                flush=True,
            )

            time.sleep(delay)

        except (requests.Timeout, requests.ConnectionError) as exc:

            if attempt == MAX_RETRIES:
                raise

            delay = _retry_delay(
                attempt=attempt,
                status=None,
                retry_after=None,
            )

            print(
                f"Zendesk {type(exc).__name__}. "
                f"Retry {attempt + 1}/{MAX_RETRIES} "
                f"after {delay:.0f}s.",
                flush=True,
            )

            time.sleep(delay)

    raise RuntimeError("Zendesk request exceeded retry limit")


def _valid_article(article: Any) -> bool:
    return (
        isinstance(article, dict)
        and isinstance(article.get("id"), int)
        and not isinstance(article.get("id"), bool)
        and isinstance(article.get("title"), str)
        and bool(article["title"].strip())
        and isinstance(article.get("html_url"), str)
        and bool(article["html_url"].strip())
        and isinstance(article.get("body"), str)
        and bool(article["body"].strip())
    )


def fetch_articles(max_pages: int | None = None, strict: bool = False) -> list[Path]:
    """Fetch and save all available pages."""

    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    url: str | None = API_URL

    params: dict[str, int] | None = {
        "per_page": 30
    }

    page = 0
    saved_paths: list[Path] = []

    while url and (max_pages is None or page < max_pages):

        try:
            data = _request_json(
                url,
                params=params,
            )

        except (
            requests.RequestException,
            ValueError,
            RuntimeError,
        ) as exc:

            raise RuntimeError(
                f"Failed to fetch Zendesk articles from {url}: {exc}"
            ) from exc

        if not isinstance(data, dict) or not isinstance(
            data.get("articles"), list
        ):
            raise RuntimeError(
                f"Invalid Zendesk response from {url}: "
                "missing articles list"
            )

        for article in data["articles"]:

            if _valid_article(article):

                path = save_article(article)

                saved_paths.append(path)

                print(f"Saved: {path.name}")

            elif strict:
                raise RuntimeError("Zendesk returned an invalid article; refusing partial source input")

        next_page = data.get("next_page")

        url = (
            next_page
            if isinstance(next_page, str) and next_page
            else None
        )

        params = None
        page += 1

        # Avoid sending pagination requests too quickly.
        if url and (max_pages is None or page < max_pages):
            time.sleep(PAGE_DELAY_SECONDS)

    print(f"Total saved: {len(saved_paths)}")

    return saved_paths


def fetch_article_by_id(article_id: int) -> dict[str, Any]:
    """Fetch one Zendesk article by ID."""

    if (
        not isinstance(article_id, int)
        or isinstance(article_id, bool)
        or article_id <= 0
    ):
        raise ValueError("article_id must be a positive integer")

    url = ARTICLE_URL.format(article_id=article_id)

    try:
        data = _request_json(url)

    except (
        requests.RequestException,
        ValueError,
        RuntimeError,
    ) as exc:

        raise RuntimeError(
            f"Failed to fetch Zendesk article {article_id}: {exc}"
        ) from exc

    article = (
        data.get("article")
        if isinstance(data, dict)
        else None
    )

    if not _valid_article(article):
        raise RuntimeError(
            f"Zendesk article {article_id} is missing required fields"
        )

    return article


def save_article(
    article: dict[str, Any],
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    """Convert an article to Markdown and save it locally."""

    if not _valid_article(article):
        raise ValueError(
            "Article must contain a valid id, title, html_url, and body"
        )

    article_id = article["id"]
    title = article["title"].strip()
    url = article["html_url"].strip()

    markdown = convert_html_to_markdown(
        article["body"],
        article_url=url,
        title=title,
    )

    content = f"# {title}\n\nArticle URL: {url}\n"

    if markdown:
        content += f"\n{markdown}\n"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_paths = sorted(
        output_dir.glob(f"{article_id}-*.md")
    )

    stable_path = output_dir / f"{article_id}.md"

    if stable_path.exists():
        path = stable_path

    elif existing_paths:
        path = existing_paths[0]

    else:
        path = stable_path

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path


if __name__ == "__main__":
    fetch_articles()
