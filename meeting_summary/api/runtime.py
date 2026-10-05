"""Lebenszyklus der API-Anwendung."""

from dataclasses import dataclass

from ..application.job_service import ProcessingJobService
from ..services.task_runner import ThreadPoolTaskRunner


@dataclass(frozen=True, slots=True)
class ApiRuntime:
    """Hält gemeinsam erzeugte API-Abhängigkeiten."""

    job_service: ProcessingJobService
    task_runner: ThreadPoolTaskRunner

    def shutdown(self) -> None:
        self.task_runner.shutdown()
