"""Tests für die strukturierte Meeting-Zusammenfassung."""

from unittest.mock import Mock

import pytest

from meeting_summary.exceptions import SummarizationError
from meeting_summary.models import (
    MeetingProtocol,
    TodoItem,
    TopicSection,
    Transcript,
    TranscriptSegment,
)
from meeting_summary.services.ollama_client import OllamaClient
from meeting_summary.services.summarization import OllamaSummarizer


def test_summarize_maps_json_response_to_protocol() -> None:
    client = Mock(spec=OllamaClient)
    client.chat.return_value = """
    {
        "short_summary": "Das Team plant den nächsten Release.",
        "topics": [
            {
                "title": "Release",
                "bullet_points": [
                    "Der Release ist für Freitag geplant."
                ]
            }
        ],
        "todos": [
            {
                "task": "Release Notes erstellen",
                "assignee": "Anna"
            }
        ]
    }
    """

    transcript = Transcript(
        segments=(
            TranscriptSegment(
                0.0,
                5.0,
                "Der Release ist Freitag. Anna erstellt die Release Notes.",
            ),
        )
    )

    result = OllamaSummarizer(client).summarize(transcript)

    assert result == MeetingProtocol(
        short_summary="Das Team plant den nächsten Release.",
        topics=(
            TopicSection(
                title="Release",
                bullet_points=("Der Release ist für Freitag geplant.",),
            ),
        ),
        todos=(
            TodoItem(
                task="Release Notes erstellen",
                assignee="Anna",
            ),
        ),
    )


def test_summarize_sends_transcript_and_complete_schema() -> None:
    client = Mock(spec=OllamaClient)
    client.chat.return_value = """
    {
        "short_summary": "Kurze Zusammenfassung.",
        "topics": [],
        "todos": []
    }
    """
    transcript = Transcript(
        segments=(TranscriptSegment(0.0, 1.0, "Besprochener Inhalt."),)
    )

    OllamaSummarizer(client).summarize(transcript)

    client.chat.assert_called_once()
    call_arguments = client.chat.call_args.kwargs
    messages = call_arguments["messages"]
    schema = call_arguments["response_schema"]
    system_prompt = " ".join(messages[0]["content"].split())

    assert call_arguments["options"] == {"temperature": 0}
    assert messages[1] == {
        "role": "user",
        "content": "Besprochener Inhalt.",
    }
    assert "ausschließlich aus dem bereitgestellten Transkript" in system_prompt
    assert schema["required"] == ["short_summary", "topics", "todos"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["topics"]["type"] == "array"
    assert schema["properties"]["todos"]["type"] == "array"


def test_summarize_accepts_todo_without_assignee() -> None:
    client = Mock(spec=OllamaClient)
    client.chat.return_value = """
    {
        "short_summary": "Eine Aufgabe wurde vereinbart.",
        "topics": [],
        "todos": [
            {
                "task": "Protokoll versenden",
                "assignee": null
            }
        ]
    }
    """
    transcript = Transcript(
        segments=(TranscriptSegment(0.0, 1.0, "Protokoll versenden."),)
    )

    result = OllamaSummarizer(client).summarize(transcript)

    assert result.todos == (
        TodoItem(task="Protokoll versenden", assignee=None),
    )


@pytest.mark.parametrize(
    "response",
    [
        "kein JSON",
        "[]",
        '{"short_summary": null, "topics": [], "todos": []}',
        '{"short_summary": "Text", "topics": {}, "todos": []}',
        '{"short_summary": "Text", "topics": [], "todos": {}}',
        '{"short_summary": "Text", "topics": [null], "todos": []}',
        '{"short_summary": "Text", "topics": [{}], "todos": []}',
        (
            '{"short_summary": "Text", "topics": '
            '[{"title": "Thema", "bullet_points": {}}], "todos": []}'
        ),
        (
            '{"short_summary": "Text", "topics": '
            '[{"title": "Thema", "bullet_points": [1]}], "todos": []}'
        ),
        '{"short_summary": "Text", "topics": [], "todos": [null]}',
        '{"short_summary": "Text", "topics": [], "todos": [{}]}',
        (
            '{"short_summary": "Text", "topics": [], "todos": '
            '[{"task": "Aufgabe"}]}'
        ),
        (
            '{"short_summary": "Text", "topics": [], "todos": '
            '[{"task": "Aufgabe", "assignee": 42}]}'
        ),
    ],
)
def test_summarize_rejects_invalid_protocol_response(response: str) -> None:
    client = Mock(spec=OllamaClient)
    client.chat.return_value = response
    transcript = Transcript(
        segments=(TranscriptSegment(0.0, 1.0, "Inhalt."),)
    )

    with pytest.raises(
        SummarizationError,
        match="ungültiges Meeting-Protokoll",
    ):
        OllamaSummarizer(client).summarize(transcript)
