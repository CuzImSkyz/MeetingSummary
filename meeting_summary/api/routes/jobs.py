"""HTTP-Routen für Verarbeitungsaufträge."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.job_service import ProcessingJobService
from ..dependencies import get_job_service
from ..schemas.jobs import JobResponse


router = APIRouter(tags=["jobs"])

JobServiceDependency = Annotated[
    ProcessingJobService,
    Depends(get_job_service),
]


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
)
async def get_job_status(
    job_id: UUID,
    job_service: JobServiceDependency,
) -> JobResponse:
    job = job_service.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verarbeitungsauftrag wurde nicht gefunden.",
        )

    return JobResponse.from_job(job)
