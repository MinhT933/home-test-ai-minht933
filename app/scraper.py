"""Collect Zendesk Help Center articles."""

from pathlib import Path
from typing import Any

import requests

from app.markdown_converter import convert_html_to_markdown

API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
ARTICLE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles/{article_id}.json"
OUTPUT_DIR = Path("data/articles")
REQUEST_TIMEOUT = 15


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


def fetch_articles(max_pages: int | None = None) -> list[Path]:
    """Fetch and save all available pages, optionally limited by ``max_pages``."""
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    url: str | None = API_URL
    params: dict[str, int] | None = {"per_page": 30}
    page = 0
    saved_paths: list[Path] = []
    while url and (max_pages is None or page < max_pages):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise RuntimeError(f"Failed to fetch Zendesk articles from {url}: {exc}") from exc

        if not isinstance(data, dict) or not isinstance(data.get("articles"), list):
            raise RuntimeError(f"Invalid Zendesk response from {url}: missing articles list")
        for article in data["articles"]:
            if _valid_article(article):
                path = save_article(article)
                saved_paths.append(path)
                print(f"Saved: {path.name}")

        next_page = data.get("next_page")
        url = next_page if isinstance(next_page, str) and next_page else None
        params = None
        page += 1

    print(f"Total saved: {len(saved_paths)}")
    return saved_paths


def fetch_article_by_id(article_id: int) -> dict[str, Any]:
    if not isinstance(article_id, int) or isinstance(article_id, bool) or article_id <= 0:
        raise ValueError("article_id must be a positive integer")
    url = ARTICLE_URL.format(article_id=article_id)
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f"Failed to fetch Zendesk article {article_id}: {exc}") from exc

    article = data.get("article") if isinstance(data, dict) else None
    if not _valid_article(article):
        raise RuntimeError(f"Zendesk article {article_id} is missing required fields")
    return article


def save_article(article: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> Path:
    if not _valid_article(article):
        raise ValueError("Article must contain a valid id, title, html_url, and body")
    article_id = article["id"]
    title = article["title"].strip()
    url = article["html_url"].strip()
    markdown = convert_html_to_markdown(article["body"], article_url=url, title=title)
    content = f"# {title}\n\nArticle URL: {url}\n"
    if markdown:
        content += f"\n{markdown}\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    existing_paths = sorted(output_dir.glob(f"{article_id}-*.md"))
    stable_path = output_dir / f"{article_id}.md"
    if stable_path.exists():
        path = stable_path
    elif existing_paths:
        path = existing_paths[0]
    else:
        path = stable_path
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    fetch_articles()
