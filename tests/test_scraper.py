from unittest.mock import Mock

import pytest

from app import scraper


def article(article_id, title="Title"):
    return {
        "id": article_id,
        "title": title,
        "html_url": f"https://example.com/articles/{article_id}",
        "body": "<p>Body</p>",
    }


def response(payload):
    result = Mock()
    result.json.return_value = payload
    return result


def test_stable_identity_reuses_legacy_title_file_without_deleting_it(tmp_path):
    legacy = tmp_path / "42-old-title.md"
    legacy.write_text("old", encoding="utf-8")
    first = scraper.save_article(article(42, "First title"), tmp_path)
    second = scraper.save_article(article(42, "Changed title"), tmp_path)

    assert first == second == legacy
    assert legacy.exists()
    assert not (tmp_path / "42.md").exists()
    assert "# Changed title" in second.read_text(encoding="utf-8")
    assert "Article URL: https://example.com/articles/42" in second.read_text(encoding="utf-8")


def test_stable_identity_reuses_new_filename_when_present(tmp_path):
    current = tmp_path / "42.md"
    current.write_text("old", encoding="utf-8")

    assert scraper.save_article(article(42), tmp_path) == current
    assert list(tmp_path.glob("42*.md")) == [current]


def test_fetch_articles_follows_pagination(monkeypatch, tmp_path):
    responses = [
        response({"articles": [article(1)], "next_page": "https://example.com/page2"}),
        response({"articles": [article(2)], "next_page": None}),
    ]
    get = Mock(side_effect=responses)
    real_save_article = scraper.save_article
    monkeypatch.setattr(scraper.requests, "get", get)
    monkeypatch.setattr(
        scraper, "save_article", lambda item: real_save_article(item, tmp_path)
    )

    paths = scraper.fetch_articles()

    assert [path.name for path in paths] == ["1.md", "2.md"]
    assert get.call_count == 2
    assert get.call_args_list[0].kwargs["params"] == {"per_page": 30}
    assert get.call_args_list[1].kwargs["params"] is None


@pytest.mark.parametrize(
    "bad_article",
    [{}, {"id": "1", "title": "T", "html_url": "url", "body": "body"}, article(1) | {"body": None}],
)
def test_save_article_rejects_invalid_data(tmp_path, bad_article):
    with pytest.raises(ValueError, match="valid id"):
        scraper.save_article(bad_article, tmp_path)


def test_fetch_articles_skips_invalid_entries(monkeypatch, tmp_path):
    real_save_article = scraper.save_article
    monkeypatch.setattr(
        scraper.requests,
        "get",
        Mock(return_value=response({"articles": [{}, article(3)], "next_page": None})),
    )
    monkeypatch.setattr(
        scraper, "save_article", lambda item: real_save_article(item, tmp_path)
    )
    assert [path.name for path in scraper.fetch_articles()] == ["3.md"]


def test_strict_fetch_rejects_invalid_source_before_sync(monkeypatch):
    monkeypatch.setattr(
        scraper.requests,
        "get",
        Mock(return_value=response({"articles": [{}, article(3)], "next_page": None})),
    )
    with pytest.raises(RuntimeError, match="invalid article"):
        scraper.fetch_articles(strict=True)
