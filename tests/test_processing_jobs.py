"""Tests für den Lebenszyklus von Verarbeitungsaufträgen."""

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest

from meeting_summary.application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)
from meeting_summary.pipeline import ProcessingStage


def test_job_transitions_without_mutating_previous_state() -> None:
    queued_job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.QUEUED,
    )

    running_job = replace(
        queued_job,
        status=ProcessingJobStatus.RUNNING,
        stage=ProcessingStage.READING_METADATA,
    )

    assert queued_job.status is ProcessingJobStatus.QUEUED
    assert queued_job.stage is None
    assert running_job.status is ProcessingJobStatus.RUNNING
    assert running_job.stage is ProcessingStage.READING_METADATA


def test_completed_job_requires_result_path() -> None:
    with pytest.raises(
        ValueError,
        match="abgeschlossener Job benötigt",
    ):
        ProcessingJob(
            job_id=uuid4(),
            status=ProcessingJobStatus.COMPLETED,
            stage=ProcessingStage.COMPLETED,
        )


def test_completed_job_accepts_result_path() -> None:
    result_path = Path("meeting.pdf")

    job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.COMPLETED,
        stage=ProcessingStage.COMPLETED,
        result_path=result_path,
    )

    assert job.result_path == result_path


def test_failed_job_requires_error_message() -> None:
    with pytest.raises(
        ValueError,
        match="fehlgeschlagener Job benötigt",
    ):
        ProcessingJob(
            job_id=uuid4(),
            status=ProcessingJobStatus.FAILED,
            stage=ProcessingStage.TRANSCRIBING,
            error_message="   ",
        )
