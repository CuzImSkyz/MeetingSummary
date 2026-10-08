"""Tests für die Jobstatus-API."""

from unittest.mock import Mock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from meeting_summary.api.app import create_app
from meeting_summary.api.runtime import ApiRuntime
from meeting_summary.application.job_service import ProcessingJobService
from meeting_summary.application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)


def create_test_app(
    job_service: ProcessingJobService,
) -> FastAPI:
    runtime = Mock(spec=ApiRuntime)
    runtime.job_service = job_service

    return create_app(
        runtime_factory=Mock(return_value=runtime),
    )


def test_get_job_returns_public_status() -> None:
    job_id = uuid4()
    job = ProcessingJob(
        job_id=job_id,
        status=ProcessingJobStatus.QUEUED,
    )
    job_service = Mock(spec=ProcessingJobService)
    job_service.get.return_value = job

    with TestClient(create_test_app(job_service)) as client:
        response = client.get(f"/api/jobs/{job_id}")

        assert response.status_code == 200
        assert response.json() == {
            "job_id": str(job_id),
            "status": "queued",
            "stage": None,
            "error_message": None,
            "result_available": False,
        }
    job_service.get.assert_called_once_with(job_id)


def test_get_unknown_job_returns_not_found() -> None:
    job_id = uuid4()
    job_service = Mock(spec=ProcessingJobService)
    job_service.get.return_value = None

    with TestClient(create_test_app(job_service)) as client:
        response = client.get(f"/api/jobs/{job_id}")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Verarbeitungsauftrag wurde nicht gefunden."
        }

    job_service.get.assert_called_once_with(job_id)


def test_get_job_rejects_invalid_uuid() -> None:
    job_service = Mock(spec=ProcessingJobService)

    with TestClient(create_test_app(job_service)) as client:
        response = client.get("/api/jobs/not-a-uuid")

    assert response.status_code == 422
    job_service.get.assert_not_called()
