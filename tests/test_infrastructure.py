"""Tests für die lokale Infrastrukturprüfung."""

from unittest.mock import Mock

import pytest

from meeting_summary.config import AppConfig
from meeting_summary.exceptions import OllamaModelNotInstalledError
from meeting_summary.services.infrastructure import InfrastructureChecker
from meeting_summary.services.ollama_client import OllamaClient


def test_check_accepts_installed_configured_model() -> None:
    config = AppConfig(
        ollama_model="llama3:8b-instruct-q4_K_M",
    )
    client = Mock(spec=OllamaClient)
    client.list_models.return_value = (
        "mistral:latest",
        "llama3:8b-instruct-q4_K_M",
    )

    result = InfrastructureChecker(
        config=config,
        client=client,
    ).check()

    assert result is None
    client.list_models.assert_called_once_with()


def test_check_reports_configured_and_available_models() -> None:
    config = AppConfig(
        ollama_model="llama3:8b-instruct-q4_K_M",
    )
    client = Mock(spec=OllamaClient)
    client.list_models.return_value = (
        "mistral:latest",
        "llama3.2:latest",
    )

    with pytest.raises(
        OllamaModelNotInstalledError,
    ) as error:
        InfrastructureChecker(
            config=config,
            client=client,
        ).check()

    message = str(error.value)
    assert config.ollama_model in message
    assert "mistral:latest" in message
    assert "llama3.2:latest" in message
    client.list_models.assert_called_once_with()


def test_check_reports_empty_model_list() -> None:
    config = AppConfig(
        ollama_model="llama3:8b-instruct-q4_K_M",
    )
    client = Mock(spec=OllamaClient)
    client.list_models.return_value = ()

    with pytest.raises(
        OllamaModelNotInstalledError,
    ) as error:
        InfrastructureChecker(
            config=config,
            client=client,
        ).check()

    assert config.ollama_model in str(error.value)
    assert "keine Modelle installiert" in str(error.value)
    client.list_models.assert_called_once_with()

