from unittest.mock import Mock

from fastapi.testclient import TestClient

from meeting_summary.api.app import create_app
from meeting_summary.api.runtime import ApiRuntime


def test_health_returns_ok() -> None:
    runtime = Mock(spec=ApiRuntime)

    with TestClient(
        create_app(
            runtime_factory=Mock(return_value=runtime),
        )
    ) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
