"""Thread-basierte Ausführung von Hintergrundaufgaben."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor


class ThreadPoolTaskRunner:
    """Führt Aufgaben in einem begrenzten Thread-Pool aus."""

    def __init__(self, *, max_workers: int = 1) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="meetme-job",
        )

    def submit(self, task: Callable[[], None]) -> None:
        self._executor.submit(task)

    def shutdown(self, *, wait: bool = True) -> None:
        self._executor.shutdown(
            wait=wait,
            cancel_futures=False,
        )
