"""Übersetzt Pipeline-Fortschritt in gespeicherte Jobzustände."""

from uuid import UUID

from ..pipeline import ProcessingStage
from .processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
    ProcessingJobStore,
)


class JobProgressReporter:
    """Speichert den Fortschritt eines einzelnen Jobs."""

    def __init__(
        self,
        job_id: UUID,
        store: ProcessingJobStore,
    ) -> None:
        self._job_id = job_id
        self._store = store

    def report(self, stage: ProcessingStage) -> None:
        if stage is ProcessingStage.COMPLETED:
            return

        current_job = self._store.get(self._job_id)

        if current_job is None:
            raise LookupError(
                f"Verarbeitungsauftrag nicht gefunden: {self._job_id}"
            )

        if current_job.status not in {
            ProcessingJobStatus.QUEUED,
            ProcessingJobStatus.RUNNING,
        }:
            raise RuntimeError(
                "Nur wartende oder laufende Jobs dürfen fortgesetzt werden."
            )

        self._store.save(
            ProcessingJob(
                job_id=self._job_id,
                status=ProcessingJobStatus.RUNNING,
                stage=stage,
            )
        )