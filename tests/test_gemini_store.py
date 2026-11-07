from types import SimpleNamespace
from unittest.mock import Mock

from app.gemini_store import upload_missing_articles


def test_skips_existing_article_ids_from_old_and_new_names(tmp_path):
    for name in ["123.md", "456-new-title.md", "789.md"]:
        (tmp_path / name).write_text("article", encoding="utf-8")
    client = Mock()
    client.file_search_stores.documents.list.return_value = [
        SimpleNamespace(display_name="123-old-title.md", custom_metadata=None),
        SimpleNamespace(
            display_name="unrelated-name.md",
            custom_metadata=[SimpleNamespace(key="article_id", string_value="456")],
        ),
    ]
    client.file_search_stores.upload_to_file_search_store.return_value = SimpleNamespace(
        done=True, error=None
    )

    result = upload_missing_articles(client, "fileSearchStores/existing", tmp_path)

    assert result.total == 3
    assert result.skipped == 2
    assert result.added == 1
    assert result.failed == []
    upload = client.file_search_stores.upload_to_file_search_store
    assert upload.call_count == 1
    assert upload.call_args.kwargs["file"].endswith("789.md")


def test_reports_upload_and_indexing_errors_without_retrying(tmp_path):
    for name in ["123.md", "456.md"]:
        (tmp_path / name).write_text("article", encoding="utf-8")
    client = Mock()
    client.file_search_stores.documents.list.return_value = []
    client.file_search_stores.upload_to_file_search_store.side_effect = [
        RuntimeError("upload rejected"),
        SimpleNamespace(done=True, error="indexing rejected"),
    ]

    result = upload_missing_articles(client, "fileSearchStores/existing", tmp_path)

    assert result.added == 0
    assert result.skipped == 0
    assert [name for name, _ in result.failed] == ["123.md", "456.md"]
    assert "upload rejected" in result.failed[0][1]
    assert "indexing rejected" in result.failed[1][1]
    assert client.file_search_stores.upload_to_file_search_store.call_count == 2
    client.operations.get.assert_not_called()
