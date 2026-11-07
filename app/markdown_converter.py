"""Convert collected HTML content to Markdown."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import markdownify as md


def convert_html_to_markdown(
    html: str, article_url: str | None = None, title: str | None = None
) -> str:
    """Convert article HTML while preserving useful article content."""
    soup = BeautifulSoup(html or "", "html.parser")
    for element in soup.select("script, style, nav"):
        element.decompose()

    if article_url:
        for element in soup.select("a[href], img[src]"):
            attribute = "href" if element.name == "a" else "src"
            element[attribute] = urljoin(article_url, element[attribute])

    first_heading = soup.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    if (
        title
        and first_heading
        and first_heading.name == "h1"
        and " ".join(first_heading.get_text(" ", strip=True).split()).casefold()
        == " ".join(title.split()).casefold()
    ):
        first_heading.decompose()

    return md(str(soup), heading_style="ATX").strip()
