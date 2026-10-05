"""Orchestriert Meetingverarbeitung als Hintergrundauftrag."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid4

from ..pipeline import (
    ProcessingStage,
    ProgressReporter,
)
from .job_progress import JobProgressReporter
from .processing_jobs import (
    ProcessingJob,
    ProcessingJobStatus,
    ProcessingJobStore,
)


class MeetingProcessor(Protocol):
    """Führt die eigentliche Meeting-Pipeline aus."""

    def run(
        self,
        audio_path: Path,
        target_path: Path,
        *,
        progress_reporter: ProgressReporter,
    ) -> Path: ...


class BackgroundTaskRunner(Protocol):
    """Führt eine Funktion außerhalb des aufrufenden Requests aus."""

    def submit(self, task: Callable[[], None]) -> None: ...


class ProcessingJobService:
    """Verwaltet und verarbeitet Meetingaufträge."""

    def __init__(
        self,
        processor: MeetingProcessor,
        store: ProcessingJobStore,
        task_runner: BackgroundTaskRunner,
    ) -> None:
        self._processor = processor
        self._store = store
        self._task_runner = task_runner

    def submit(
        self,
        audio_path: Path,
        target_path: Path,
    ) -> ProcessingJob:
        job = ProcessingJob(
            job_id=uuid4(),
            status=ProcessingJobStatus.QUEUED,
        )
        self._store.save(job)

        self._task_runner.submit(
            lambda: self._execute(
                job.job_id,
                audio_path,
                target_path,
            )
        )
        return job

    def get(self, job_id: UUID) -> ProcessingJob | None:
        return self._store.get(job_id)

    def _execute(
        self,
        job_id: UUID,
        audio_path: Path,
        target_path: Path,
    ) -> None:
        progress_reporter = JobProgressReporter(
            job_id,
            self._store,
        )

        try:
            result_path = self._processor.run(
                audio_path,
                target_path,
                progress_reporter=progress_reporter,
            )
        except Exception as error:
            current_job = self._store.get(job_id)
            failed_stage = (
                current_job.stage
                if current_job is not None
                else None
            )
            error_message = (
                str(error).strip()
                or "Unbekannter Fehler bei der Meetingverarbeitung."
            )

            self._store.save(
                ProcessingJob(
                    job_id=job_id,
                    status=ProcessingJobStatus.FAILED,
                    stage=failed_stage,
                    error_message=error_message,
                )
            )
            return

        self._store.save(
            ProcessingJob(
                job_id=job_id,
                status=ProcessingJobStatus.COMPLETED,
                stage=ProcessingStage.COMPLETED,
                result_path=result_path,
            )
        )
