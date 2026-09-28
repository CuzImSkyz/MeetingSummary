"""Tests für den flüchtigen Job-Speicher."""

from dataclasses import replace
from uuid import uuid4

from meeting_summary.application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)
from meeting_summary.pipeline import ProcessingStage
from meeting_summary.services.job_store import (
    InMemoryProcessingJobStore,
)


def test_store_saves_and_returns_job() -> None:
    store = InMemoryProcessingJobStore()
    job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.QUEUED,
    )

    store.save(job)

    assert store.get(job.job_id) == job


def test_store_returns_none_for_unknown_job() -> None:
    store = InMemoryProcessingJobStore()
    assert store.get(uuid4()) is None


def test_store_replaces_existing_job_state() -> None:
    store = InMemoryProcessingJobStore()
    queued_job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.QUEUED,
    )
    running_job = replace(
        queued_job,
        status=ProcessingJobStatus.RUNNING,
        stage=ProcessingStage.TRANSCRIBING,
    )

    store.save(queued_job)
    store.save(running_job)

    assert store.get(queued_job.job_id) == running_job

