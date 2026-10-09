from pathlib import Path

from fastapi import Request

from ..application.job_service import ProcessingJobService
from ..services.audio_upload import LocalAudioUploadStore
from .runtime import ApiRuntime


def get_job_service(request: Request) -> ProcessingJobService:
    """Liefert den Job-Service der laufenden API-Instanz."""

    runtime: ApiRuntime = request.app.state.runtime
    return runtime.job_service


def get_audio_upload_store(
    request: Request,
) -> LocalAudioUploadStore:
    """Liefert den Upload-Speicher der laufenden API-Instanz."""

    runtime: ApiRuntime = request.app.state.runtime
    return runtime.audio_upload_store


def get_result_directory(
    request: Request,
) -> Path:
    """Liefert das konfigurierte Ergebnisverzeichnis."""

    runtime: ApiRuntime = request.app.state.runtime
    return runtime.result_directory
