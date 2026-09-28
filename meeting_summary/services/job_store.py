"""In-Memory-Speicher für Verarbeitungsaufträge."""

from threading import Lock
from uuid import UUID

from ..application.processing_jobs import ProcessingJob


class InMemoryProcessingJobStore:
    """Thread-sicherer flüchtiger Job-Speicher."""

    def __init__(self) -> None:
        self._jobs: dict[UUID, ProcessingJob] = {}
        self._lock = Lock()

    def save(self, job: ProcessingJob) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: UUID) -> ProcessingJob | None:
        with self._lock:
            return self._jobs.get(job_id)
