"""Tests für den Lebenszyklus der API-Abhängigkeiten."""

from unittest.mock import Mock

from meeting_summary.application.job_service import ProcessingJobService
from meeting_summary.api.runtime import ApiRuntime
from meeting_summary.services.task_runner import ThreadPoolTaskRunner


def test_shutdown_closes_task_runner() -> None:
    job_service = Mock(spec=ProcessingJobService)
    task_runner = Mock(spec=ThreadPoolTaskRunner)
    runtime = ApiRuntime(
        job_service=job_service,
        task_runner=task_runner,
    )

    runtime.shutdown()

    task_runner.shutdown.assert_called_once_with()
