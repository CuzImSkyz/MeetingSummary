"""Tests für die Übersetzung von Pipeline-Fortschritt."""

from uuid import uuid4

import pytest

from meeting_summary.application.job_progress import (
    JobProgressReporter,
)
from meeting_summary.application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)
from meeting_summary.pipeline import ProcessingStage
from meeting_summary.services.job_store import (
    InMemoryProcessingJobStore,
)


def test_reporter_stores_running_stage() -> None:
    store = InMemoryProcessingJobStore()
    job_id = uuid4()
    store.save(
        ProcessingJob(
            job_id=job_id,
            status=ProcessingJobStatus.QUEUED,
        )
    )
    reporter = JobProgressReporter(job_id, store)
    reporter.report(ProcessingStage.TRANSCRIBING)

    assert store.get(job_id) == ProcessingJob(
        job_id=job_id,
        status=ProcessingJobStatus.RUNNING,
        stage=ProcessingStage.TRANSCRIBING,
    )


def test_reporter_ignores_completed_stage() -> None:
    store = InMemoryProcessingJobStore()
    running_job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.RUNNING,
        stage=ProcessingStage.EXPORTING,
    )
    store.save(running_job)
    reporter = JobProgressReporter(running_job.job_id, store)

    reporter.report(ProcessingStage.COMPLETED)

    assert store.get(running_job.job_id) == running_job


def test_reporter_rejects_unknown_job() -> None:
    store = InMemoryProcessingJobStore()
    unknown_job_id = uuid4()
    reporter = JobProgressReporter(unknown_job_id, store)

    with pytest.raises(
        LookupError,
        match=str(unknown_job_id),
    ):
        reporter.report(ProcessingStage.TRANSCRIBING)


def test_reporter_rejects_terminal_job() -> None:
    store = InMemoryProcessingJobStore()
    failed_job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.FAILED,
        stage=ProcessingStage.TRANSCRIBING,
        error_message="Whisper ist fehlgeschlagen.",
    )
    store.save(failed_job)
    reporter = JobProgressReporter(failed_job.job_id, store)

    with pytest.raises(
        RuntimeError,
        match="wartende oder laufende",
    ):
        reporter.report(ProcessingStage.TRANSCRIBING)
