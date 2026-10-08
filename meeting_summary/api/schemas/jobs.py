"""API-Modelle für Verarbeitungsaufträge."""

from typing import Self
from uuid import UUID

from pydantic import BaseModel

from ...application.processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
)
from ...pipeline import ProcessingStage


class JobResponse(BaseModel):
    """Öffentlicher Zustand eines Verarbeitungsauftrags."""

    job_id: UUID
    status: ProcessingJobStatus
    stage: ProcessingStage | None
    error_message: str | None
    result_available: bool

    @classmethod
    def from_job(cls, job: ProcessingJob) -> Self:
        return cls(
            job_id=job.job_id,
            status=job.status,
            stage=job.stage,
            error_message=job.error_message,
            result_available=job.result_path is not None,
        )
