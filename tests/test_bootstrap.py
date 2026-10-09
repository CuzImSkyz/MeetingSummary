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


def test_build_api_runtime_wires_shared_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = AppConfig()
    pipeline = Mock(name="pipeline")
    store = Mock(name="store")
    audio_upload_store = Mock(name="audio_upload_store")
    task_runner = Mock(name="task_runner")
    job_service = Mock(name="job_service")

    build_pipeline = Mock(return_value=pipeline)
    store_factory = Mock(return_value=store)
    audio_upload_store_factory = Mock(
        return_value=audio_upload_store
    )
    task_runner_factory = Mock(return_value=task_runner)
    job_service_factory = Mock(return_value=job_service)

    monkeypatch.setattr(
        bootstrap,
        "build_pipeline",
        build_pipeline,
    )
    monkeypatch.setattr(
        bootstrap,
        "InMemoryProcessingJobStore",
        store_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "LocalAudioUploadStore",
        audio_upload_store_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "ThreadPoolTaskRunner",
        task_runner_factory,
    )
    monkeypatch.setattr(
        bootstrap,
        "ProcessingJobService",
        job_service_factory,
    )

    runtime = bootstrap.build_api_runtime(config)

    build_pipeline.assert_called_once_with(config)
    store_factory.assert_called_once_with()
    audio_upload_store_factory.assert_called_once_with(
        config.api_upload_directory,
        max_bytes=config.api_max_upload_bytes,
    )
    task_runner_factory.assert_called_once_with()
    job_service_factory.assert_called_once_with(
        processor=pipeline,
        store=store,
        task_runner=task_runner,
    )
    assert runtime.job_service is job_service
    assert runtime.audio_upload_store is audio_upload_store
    assert runtime.task_runner is task_runner
    assert runtime.result_directory == config.api_result_directory
