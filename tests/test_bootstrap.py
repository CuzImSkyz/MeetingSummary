"""Tests für die Verdrahtung der Anwendungsadapter."""

from unittest.mock import Mock

import pytest

from meeting_summary import bootstrap
from meeting_summary.config import AppConfig


def test_build_pipeline_checks_infrastructure_before_whisper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AppConfig(
        whisper_hotwords=(
            "Anna",
            "Release Notes",
        )
    )
    events: list[str] = []

    transcriber = Mock(name="transcriber")
    infrastructure_checker = Mock(name="infrastructure_checker")
    meeting_time_resolver = Mock(name="meeting_time_resolver")
    ollama_client = Mock(name="ollama_client")
    summarizer = Mock(name="summarizer")
    pdf_exporter = Mock(name="pdf_exporter")
    pipeline = Mock(name="pipeline")

    def create_transcriber(_: AppConfig) -> Mock:
        events.append("transcriber")
        return transcriber

    def check_infrastructure() -> None:
        events.append("check")

    transcriber_factory = Mock(side_effect=create_transcriber)
    infrastructure_checker.check.side_effect = check_infrastructure
    infrastructure_checker_factory = Mock(
        return_value=infrastructure_checker
    )
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
        "InfrastructureChecker",
        infrastructure_checker_factory,
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
    ollama_client_factory.assert_called_once_with(config)
    infrastructure_checker_factory.assert_called_once_with(
        config=config,
        client=ollama_client,
    )
    infrastructure_checker.check.assert_called_once_with()
    transcriber_factory.assert_called_once_with(config)
    meeting_time_resolver_factory.assert_called_once_with()
    summarizer_factory.assert_called_once_with(ollama_client)
    pdf_exporter_factory.assert_called_once_with()
    pipeline_factory.assert_called_once_with(
        transcriber=transcriber,
        meeting_time_resolver=meeting_time_resolver,
        summarizer=summarizer,
        pdf_exporter=pdf_exporter,
    )
    assert events == [
        "check",
        "transcriber",
    ]
