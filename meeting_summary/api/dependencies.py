"""Abhängigkeiten für API-Routen."""

from fastapi import Request

from ..application.job_service import ProcessingJobService
from .runtime import ApiRuntime


def get_job_service(request: Request) -> ProcessingJobService:
    """Liefert den Job-Service der laufenden API-Instanz."""

    runtime: ApiRuntime = request.app.state.runtime
    return runtime.job_service
