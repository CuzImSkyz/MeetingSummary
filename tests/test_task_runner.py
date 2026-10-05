"""Tests für die Ausführung von Hintergrundaufgaben."""

from threading import Event

from meeting_summary.services.task_runner import ThreadPoolTaskRunner


def test_runner_executes_submitted_task() -> None:
    runner = ThreadPoolTaskRunner()
    task_executed = Event()

    try:
        runner.submit(task_executed.set)

        assert task_executed.wait(timeout=1.0)
    finally:
        runner.shutdown()
