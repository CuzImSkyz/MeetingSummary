"""Tests für den Lebenszyklus der API-Abhängigkeiten."""

from pathlib import Path
from unittest.mock import Mock

from meeting_summary.application.job_service import ProcessingJobService
from meeting_summary.api.runtime import ApiRuntime
from meeting_summary.services.audio_upload import LocalAudioUploadStore
from meeting_summary.services.task_runner import ThreadPoolTaskRunner


def test_shutdown_closes_task_runner() -> None:
    job_service = Mock(spec=ProcessingJobService)
    task_runner = Mock(spec=ThreadPoolTaskRunner)
    audio_upload_store = Mock(spec=LocalAudioUploadStore)

    runtime = ApiRuntime(
        job_service=job_service,
        audio_upload_store=audio_upload_store,
        result_directory=Path("results"),
        task_runner=task_runner,
    )

    runtime.shutdown()

    task_runner.shutdown.assert_called_once_with()
