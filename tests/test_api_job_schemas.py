"""Tests für die öffentlichen Job-Antwortmodelle."""

from pathlib import Path
from uuid import uuid4

from meeting_summary.api.schemas.jobs import JobResponse
from meeting_summary.application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)
from meeting_summary.pipeline import ProcessingStage


def test_job_response_hides_internal_result_path() -> None:
    job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.COMPLETED,
        stage=ProcessingStage.COMPLETED,
        result_path=Path("private/results/meeting.pdf"),
    )

    response = JobResponse.from_job(job)
    payload = response.model_dump(mode="json")

    assert payload == {
        "job_id": str(job.job_id),
        "status": "completed",
        "stage": "completed",
        "error_message": None,
        "result_available": True,
    }
    assert "result_path" not in payload


def test_job_response_supports_queued_job_without_stage() -> None:
    job = ProcessingJob(
        job_id=uuid4(),
        status=ProcessingJobStatus.QUEUED,
    )

    response = JobResponse.from_job(job)

    assert response.stage is None
    assert response.result_available is False
