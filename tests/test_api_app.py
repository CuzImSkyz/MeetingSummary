"""Tests für den FastAPI-Anwendungslebenszyklus."""

from unittest.mock import Mock

from fastapi.testclient import TestClient

from meeting_summary.api.app import create_app
from meeting_summary.api.runtime import ApiRuntime
from meeting_summary.config import AppConfig


def test_app_creates_and_closes_runtime() -> None:
    config = AppConfig()
    runtime = Mock(spec=ApiRuntime)
    runtime_factory = Mock(return_value=runtime)
    app = create_app(
        config=config,
        runtime_factory=runtime_factory,
    )

    with TestClient(app):
        assert app.state.runtime is runtime

    runtime_factory.assert_called_once_with(config)
    runtime.shutdown.assert_called_once_with()
