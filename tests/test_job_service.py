"""Tests für die Job-Orchestrierung."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from meeting_summary.application.job_service import (
    MeetingProcessor,
    ProcessingJobService,
)
from meeting_summary.application.processing_jobs import (
    ProcessingJobStatus,
)
from meeting_summary.pipeline import (
    ProcessingStage,
    ProgressReporter,
)
from meeting_summary.services.job_store import (
    InMemoryProcessingJobStore,
)


class ControlledTaskRunner:
    """Speichert Aufgaben, bis der Test sie explizit ausführt."""

    def __init__(self) -> None:
        self.tasks: list[Callable[[], None]] = []

    def submit(self, task: Callable[[], None]) -> None:
        self.tasks.append(task)

    def run_next(self) -> None:
        if not self.tasks:
            raise AssertionError("Keine Hintergrundaufgabe vorhanden.")

        task = self.tasks.pop(0)
        task()


def test_submit_queues_job_before_processing() -> None:
    audio_path = Path("meeting.webm")
    target_path = Path("meeting.pdf")
    store = InMemoryProcessingJobStore()
    task_runner = ControlledTaskRunner()
    processor = Mock(spec=MeetingProcessor)

    def run_pipeline(
        received_audio_path: Path,
        received_target_path: Path,
        *,
        progress_reporter: ProgressReporter,
    ) -> Path:
        assert received_audio_path == audio_path
        assert received_target_path == target_path

        progress_reporter.report(ProcessingStage.TRANSCRIBING)
        return target_path

    processor.run.side_effect = run_pipeline

    service = ProcessingJobService(
        processor=processor,
        store=store,
        task_runner=task_runner,
    )

    queued_job = service.submit(audio_path, target_path)

    assert queued_job.status is ProcessingJobStatus.QUEUED
    assert store.get(queued_job.job_id) == queued_job
    processor.run.assert_not_called()
    assert len(task_runner.tasks) == 1

    task_runner.run_next()

    completed_job = service.get(queued_job.job_id)

    assert completed_job is not None
    assert task_runner.tasks == []
    assert completed_job.status is ProcessingJobStatus.COMPLETED
    assert completed_job.stage is ProcessingStage.COMPLETED
    assert completed_job.result_path == target_path


def test_processing_failure_preserves_last_stage() -> None:
    audio_path = Path("meeting.webm")
    target_path = Path("meeting.pdf")
    store = InMemoryProcessingJobStore()
    task_runner = ControlledTaskRunner()
    processor = Mock(spec=MeetingProcessor)

    def fail_pipeline(
        received_audio_path: Path,
        received_target_path: Path,
        *,
        progress_reporter: ProgressReporter,
    ) -> Path:
        assert received_audio_path == audio_path
        assert received_target_path == target_path

        progress_reporter.report(
            ProcessingStage.SUMMARIZING
        )
        raise RuntimeError("Ollama ist nicht erreichbar.")

    processor.run.side_effect = fail_pipeline

    service = ProcessingJobService(
        processor=processor,
        store=store,
        task_runner=task_runner,
    )

    queued_job = service.submit(audio_path, target_path)
    task_runner.run_next()

    failed_job = service.get(queued_job.job_id)

    assert failed_job is not None
    assert failed_job.status is ProcessingJobStatus.FAILED
    assert failed_job.stage is ProcessingStage.SUMMARIZING
    assert failed_job.result_path is None
    assert failed_job.error_message == (
        "Ollama ist nicht erreichbar."
    )


def test_submit_uses_provided_job_id() -> None:
    job_id = uuid4()
    store = InMemoryProcessingJobStore()
    task_runner = ControlledTaskRunner()
    processor = Mock(spec=MeetingProcessor)
    service = ProcessingJobService(
        processor=processor,
        store=store,
        task_runner=task_runner,
    )

    queued_job = service.submit(
        Path("meeting.webm"),
        Path("meeting.pdf"),
        job_id=job_id,
    )

    assert queued_job.job_id == job_id
    assert store.get(job_id) == queued_job
