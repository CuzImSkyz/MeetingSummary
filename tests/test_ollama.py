"""Tests für den lokalen Ollama-HTTP-Client."""

from unittest.mock import Mock

import pytest
import requests

from meeting_summary.config import AppConfig
from meeting_summary.exceptions import (
    OllamaConnectionError,
    OllamaResponseError,
)
from meeting_summary.services.ollama_client import OllamaClient


def test_list_models_returns_names_from_api_response() -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = {
        "models": [
            {"name": "llama3:8b-instruct-q4_K_M"},
            {"name": "gemma3:4b"},
        ]
    }

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(config=AppConfig(), session=session)
    result = client.list_models()

    assert result == (
        "llama3:8b-instruct-q4_K_M",
        "gemma3:4b",
    )

    session.request.assert_called_once_with(
        method="GET",
        url="http://localhost:11434/api/tags",
        timeout=5.0,
        json=None,
    )
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    "request_error",
    (
        requests.ConnectionError("Verbindung abgelehnt"),
        requests.Timeout("Zeitüberschreitung"),
    ),
)
def test_list_models_translates_connection_failures(
    request_error: requests.RequestException,
) -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = request_error

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )

    with pytest.raises(
        OllamaConnectionError,
        match="Ollama-API.*nicht erreichbar",
    ):
        client.list_models()

    session.request.assert_called_once_with(
        method="GET",
        url="http://localhost:11434/api/tags",
        timeout=5.0,
        json=None,
    )


def test_list_models_translates_http_error() -> None:
    response = Mock(spec=requests.Response)
    response.raise_for_status.side_effect = requests.HTTPError(
        "500 Server Error"
    )

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )

    with pytest.raises(
        OllamaResponseError,
        match="HTTP-Fehler",
    ):
        client.list_models()

    response.raise_for_status.assert_called_once_with()
    response.json.assert_not_called()


def test_list_models_translates_invalid_json() -> None:
    response = Mock(spec=requests.Response)
    response.json.side_effect = ValueError("Ungültiges JSON")

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )

    with pytest.raises(
        OllamaResponseError,
        match="kein gültiges JSON",
    ):
        client.list_models()


@pytest.mark.parametrize(
    "payload",
    (
        None,
        [],
        {},
        {"models": None},
        {"models": {}},
        {"models": [None]},
        {"models": [{}]},
        {"models": [{"name": ""}]},
        {"models": [{"name": "   "}]},
        {"models": [{"name": 17}]},
    ),
)
def test_list_models_rejects_invalid_response_structure(payload: object) -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = payload

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )

    with pytest.raises(
        OllamaResponseError,
        match="ungültige Modellliste",
    ):
        client.list_models()


def test_chat_returns_content_from_complete_response() -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = {
        "done": True,
        "message": {
            "role": "assistant",
            "content": '{"short_summary":"Test"}',
        },
    }

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )
    messages = (
        {"role": "system", "content": "Erzeuge strukturiertes JSON."},
        {"role": "user", "content": "Fasse das Meeting zusammen."},
    )
    response_schema = {
        "type": "object",
        "properties": {
            "short_summary": {"type": "string"},
        },
        "required": ["short_summary"],
    }

    result = client.chat(
        messages=messages,
        response_schema=response_schema,
    )

    assert result == '{"short_summary":"Test"}'
    session.request.assert_called_once_with(
        method="POST",
        url="http://localhost:11434/api/chat",
        timeout=600.0,
        json={
            "model": "llama3:8b-instruct-q4_K_M",
            "messages": [
                {"role": "system", "content": "Erzeuge strukturiertes JSON."},
                {"role": "user", "content": "Fasse das Meeting zusammen."},
            ],
            "stream": False,
            "format": response_schema,
        },
    )


def test_chat_includes_generation_options_when_provided() -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = {
        "done": True,
        "message": {"role": "assistant", "content": "{}"},
    }
    session = Mock(spec=requests.Session)
    session.request.return_value = response
    client = OllamaClient(config=AppConfig(), session=session)

    client.chat(
        messages=({"role": "user", "content": "Test"},),
        response_schema={"type": "object"},
        options={"temperature": 0},
    )

    request_body = session.request.call_args.kwargs["json"]
    assert request_body["options"] == {"temperature": 0}


@pytest.mark.parametrize(
    "payload",
    (
        None,
        {},
        {"done": False, "message": {"content": "unvollständig"}},
        {"done": True},
        {"done": True, "message": None},
        {"done": True, "message": []},
        {"done": True, "message": {}},
        {"done": True, "message": {"content": None}},
        {"done": True, "message": {"content": ""}},
        {"done": True, "message": {"content": "   "}},
    ),
)
def test_chat_rejects_incomplete_response(payload: object) -> None:
    response = Mock(spec=requests.Response)
    response.json.return_value = payload

    session = Mock(spec=requests.Session)
    session.request.return_value = response

    client = OllamaClient(
        config=AppConfig(),
        session=session,
    )

    with pytest.raises(
        OllamaResponseError,
        match="keine vollständige Chat-Antwort",
    ):
        client.chat(
            messages=({"role": "user", "content": "Test"},),
            response_schema={"type": "object"},
        )
