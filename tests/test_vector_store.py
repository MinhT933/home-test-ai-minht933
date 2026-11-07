from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.vector_store import (
    UploadError,
    upload_articles,
    upload_single_file,
    vector_store_status,
)


def client_with_empty_store():
    client = Mock()
    client.vector_stores.retrieve.return_value = SimpleNamespace(
        file_counts=SimpleNamespace(total=0)
    )
    return client


def test_initial_upload_reports_partial_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_VECTOR_STORE_ID", "vs_existing")
    (tmp_path / "1.md").write_text("one", encoding="utf-8")
    (tmp_path / "2.md").write_text("two", encoding="utf-8")
    client = client_with_empty_store()
    client.files.create.side_effect = [SimpleNamespace(id="file-1"), RuntimeError("boom")]

    with pytest.raises(UploadError) as error:
        upload_articles(tmp_path, client)

    assert "2.md" in str(error.value)
    assert "1.md=file-1" in str(error.value)
    client.vector_stores.file_batches.create_and_poll.assert_not_called()


def test_initial_upload_refuses_nonempty_store(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_VECTOR_STORE_ID", "vs_existing")
    (tmp_path / "1.md").write_text("one", encoding="utf-8")
    client = client_with_empty_store()
    client.vector_stores.retrieve.return_value.file_counts.total = 1

    with pytest.raises(RuntimeError, match="prevent duplicates"):
        upload_articles(tmp_path, client)
    client.files.create.assert_not_called()


@pytest.mark.parametrize("remote_name", ["31.md", "31-old-title.md"])
def test_single_upload_refuses_matching_article_id(monkeypatch, tmp_path, remote_name):
    monkeypatch.setenv("OPENAI_VECTOR_STORE_ID", "vs_existing")
    path = tmp_path / "31.md"
    path.write_text("article", encoding="utf-8")
    client = Mock()
    client.vector_stores.files.list.return_value = [SimpleNamespace(file_id="file-31")]
    client.files.retrieve.return_value = SimpleNamespace(filename=remote_name)

    with pytest.raises(RuntimeError, match="duplicate upload"):
        upload_single_file(path, client)
    client.vector_stores.files.upload_and_poll.assert_not_called()


@pytest.mark.parametrize("remote_name", ["360051014713.md", "360051014713-youtube.md"])
def test_status_finds_article_id_read_only(monkeypatch, remote_name):
    monkeypatch.setenv("OPENAI_VECTOR_STORE_ID", "vs_existing")
    client = Mock()
    counts = SimpleNamespace(total=31, completed=31, failed=0)
    client.vector_stores.retrieve.return_value = SimpleNamespace(file_counts=counts)
    client.vector_stores.files.list.return_value = [SimpleNamespace(file_id="file-youtube")]
    client.files.retrieve.return_value = SimpleNamespace(filename=remote_name)

    result = vector_store_status(client=client)

    assert result["file_counts"] is counts
    assert result["article_exists"] is True
    client.files.create.assert_not_called()
    client.vector_stores.files.upload_and_poll.assert_not_called()
    client.vector_stores.file_batches.create_and_poll.assert_not_called()


def test_single_upload_reports_indexing_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_VECTOR_STORE_ID", "vs_existing")
    path = tmp_path / "31.md"
    path.write_text("article", encoding="utf-8")
    client = Mock()
    client.vector_stores.files.list.return_value = []
    client.vector_stores.files.upload_and_poll.return_value = SimpleNamespace(status="failed")

    with pytest.raises(UploadError, match="status failed"):
        upload_single_file(path, client)
