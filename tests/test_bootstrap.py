"""Tests für die Verdrahtung der Anwendungsadapter."""

from unittest.mock import Mock

import pytest

from meeting_summary import bootstrap
from meeting_summary.config import AppConfig


def test_build_pipeline_wires_configured_adapters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AppConfig(
        whisper_hotwords=(
            "Anna",
            "Release Notes",
        )
    )

    transcriber = Mock(name="transcriber")
    meeting_time_resolver = Mock(name="meeting_time_resolver")
    ollama_client = Mock(name="ollama_client")
    summarizer = Mock(name="summarizer")
    pdf_exporter = Mock(name="pdf_exporter")
    pipeline = Mock(name="pipeline")

    transcriber_factory = Mock(return_value=transcriber)
    meeting_time_resolver_factory = Mock(
        return_value=meeting_time_resolver
    )
    ollama_client_factory = Mock(return_value=ollama_client)
    summarizer_factory = Mock(return_value=summarizer)
    pdf_exporter_factory = Mock(return_value=pdf_exporter)
    pipeline_factory = Mock(return_value=pipeline)

    monkeypatch.setattr(
        bootstrap,
        "WhisperTranscriber",
        transcriber_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "PyAvMeetingTimeResolver",
        meeting_time_resolver_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "OllamaClient",
        ollama_client_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "OllamaSummarizer",
        summarizer_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "ReportLabExporter",
        pdf_exporter_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "MeetingPipeline",
        pipeline_factory,
    )

    result = bootstrap.build_pipeline(config)

    assert result is pipeline
    transcriber_factory.assert_called_once_with(config)
    meeting_time_resolver_factory.assert_called_once_with()
    ollama_client_factory.assert_called_once_with(config)
    summarizer_factory.assert_called_once_with(ollama_client)
    pdf_exporter_factory.assert_called_once_with()
    pipeline_factory.assert_called_once_with(
        transcriber=transcriber,
        meeting_time_resolver=meeting_time_resolver,
        summarizer=summarizer,
        pdf_exporter=pdf_exporter,
    )
