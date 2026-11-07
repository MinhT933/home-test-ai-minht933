from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.genai import types

from app.gemini_chat import (
    API_VERSION,
    EXPECTED_ARTICLE_URL,
    MODEL,
    QUESTION,
    SYSTEM_PROMPT,
    ask_optibot,
    create_client,
    format_demo,
    main,
)


def response_with_grounding():
    metadata = types.GroundingMetadata(
        grounding_chunks=[
            types.GroundingChunk(
                retrieved_context=types.GroundingChunkRetrievedContext(
                    title="360051014713-how-to-use-youtube-with-optisigns.md",
                    uri="fileSearchStores/store/documents/youtube",
                    text=f"Instructions\nArticle URL: {EXPECTED_ARTICLE_URL}\n",
                )
            )
        ]
    )
    return SimpleNamespace(
        text=f"- Add the YouTube app.\n\nArticle URL: {EXPECTED_ARTICLE_URL}",
        candidates=[SimpleNamespace(grounding_metadata=metadata)],
    )


def test_uses_exact_prompt_store_and_question():
    client = Mock()
    client.models.generate_content.return_value = response_with_grounding()

    result = ask_optibot(client, "fileSearchStores/existing")

    call = client.models.generate_content.call_args
    assert call.kwargs["model"] == "gemini-3.5-flash-lite" == MODEL
    assert call.kwargs["contents"] == QUESTION
    assert call.kwargs["config"].system_instruction == SYSTEM_PROMPT
    file_search = call.kwargs["config"].tools[0].file_search
    assert file_search.file_search_store_names == ["fileSearchStores/existing"]
    assert result.answer.startswith("- Add")


def test_extracts_grounding_citations_and_article_url():
    client = Mock()
    client.models.generate_content.return_value = response_with_grounding()

    result = ask_optibot(client, "fileSearchStores/existing")

    assert result.cited_files == [
        "360051014713-how-to-use-youtube-with-optisigns.md"
    ]
    assert EXPECTED_ARTICLE_URL in result.source_urls
    assert result.contains_expected_url is True
    assert result.bullet_count == 1
    assert result.respects_bullet_limit is True
    assert result.grounding_metadata is not None
    assert result.retrieval_citations_returned is True


def test_reports_api_error():
    client = Mock()
    client.models.generate_content.side_effect = ValueError("quota exceeded")

    with pytest.raises(RuntimeError, match="Gemini File Search request failed: quota exceeded"):
        ask_optibot(client, "fileSearchStores/existing")


def test_client_uses_configured_key_and_v1beta(monkeypatch):
    constructor = Mock(return_value=Mock())
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.gemini_chat.genai.Client", constructor)

    create_client()

    call = constructor.call_args
    assert call.kwargs["vertexai"] is False
    assert call.kwargs["api_key"] == "test-key"
    assert call.kwargs["http_options"].api_version == API_VERSION == "v1beta"
    assert call.kwargs["http_options"].retry_options.attempts == 1


def test_demo_output_formats_real_extracted_citations():
    client = Mock()
    client.models.generate_content.return_value = response_with_grounding()
    result = ask_optibot(client, "fileSearchStores/existing")

    output = format_demo(result, "fileSearchStores/existing")

    assert "Model: gemini-3.5-flash-lite" in output
    assert f"User: {QUESTION}" in output
    assert "Citations returned: YES" in output
    assert EXPECTED_ARTICLE_URL in output
    assert "360051014713-how-to-use-youtube-with-optisigns.md" in output
    assert "Maximum 5 bullets respected: True" in output


def test_demo_cli_prints_formatted_result(monkeypatch, capsys):
    client = Mock()
    client.models.generate_content.return_value = response_with_grounding()
    monkeypatch.setenv("GEMINI_FILE_SEARCH_STORE_NAME", "fileSearchStores/existing")
    monkeypatch.setattr("app.gemini_chat.create_client", lambda: client)

    main(["demo"])

    output = capsys.readouterr().out
    assert "OptiBot Mini-Clone" in output
    assert "File Search Store: fileSearchStores/existing" in output
    assert "OptiBot:\n- Add the YouTube app." in output
