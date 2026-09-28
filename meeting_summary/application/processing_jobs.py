"""Anwendungsmodelle für asynchrone Meetingverarbeitung."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import UUID

from ..pipeline import ProcessingStage


class ProcessingJobStatus(StrEnum):
    """Lebenszyklus eines Verarbeitungsauftrags."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProcessingJob:
    """Aktueller Zustand eines Verarbeitungsauftrags."""

    job_id: UUID
    status: ProcessingJobStatus
    stage: ProcessingStage | None = None
    result_path: Path | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if (
            self.status is ProcessingJobStatus.QUEUED
            and (
                self.stage is not None
                or self.result_path is not None
                or self.error_message is not None
            )
        ):
            raise ValueError(
                "Ein wartender Job darf noch keine Verarbeitungsdaten besitzen."
            )

        if self.status is ProcessingJobStatus.RUNNING:
            if self.stage is None:
                raise ValueError(
                    "Ein laufender Job benötigt eine Verarbeitungsstufe."
                )
            if self.stage is ProcessingStage.COMPLETED:
                raise ValueError(
                    "Ein laufender Job darf nicht bereits abgeschlossen sein."
                )
            if self.result_path is not None or self.error_message is not None:
                raise ValueError(
                    "Ein laufender Job darf weder Ergebnis noch Fehler besitzen."
                )

        if self.status is ProcessingJobStatus.COMPLETED:
            if (
                self.stage is not ProcessingStage.COMPLETED
                or self.result_path is None
                or self.error_message is not None
            ):
                raise ValueError(
                    "Ein abgeschlossener Job benötigt Stufe und Ergebnis."
                )

        if self.status is ProcessingJobStatus.FAILED:
            if (
                self.result_path is not None
                or self.stage is ProcessingStage.COMPLETED
                or self.error_message is None
                or not self.error_message.strip()
            ):
                raise ValueError(
                    "Ein fehlgeschlagener Job benötigt eine Fehlermeldung "
                    "und darf kein Ergebnis besitzen."
                )


class ProcessingJobStore(Protocol):
    """Speichert und liefert aktuelle Jobzustände."""

    def save(self, job: ProcessingJob) -> None: ...

    def get(self, job_id: UUID) -> ProcessingJob | None: ...
