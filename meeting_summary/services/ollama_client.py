"""HTTP-Client für die lokale Ollama-API."""

from collections.abc import Mapping, Sequence

import requests

from ..config import AppConfig
from ..exceptions import OllamaConnectionError, OllamaResponseError


class OllamaClient:
    def __init__(
        self,
        config: AppConfig,
        session: requests.Session | None = None,
    ) -> None:
        self._base_url = config.ollama_base_url.rstrip("/")
        self._status_timeout_seconds = config.ollama_status_timeout_seconds
        self._session = session if session is not None else requests.Session()
        self._model = config.ollama_model
        self._generation_timeout_seconds = (
            config.ollama_generation_timeout_seconds
        )

    def list_models(self) -> tuple[str, ...]:
        payload = self._request_json(
            method="GET",
            endpoint="/api/tags",
            timeout_seconds=self._status_timeout_seconds,
        )
        return self._parse_model_names(payload)

    def chat(
        self,
        messages: Sequence[Mapping[str, str]],
        response_schema: Mapping[str, object],
    ) -> str:
        json_body: dict[str, object] = {
            "model": self._model,
            "messages": [dict(message) for message in messages],
            "stream": False,
            "format": dict(response_schema),
        }
        payload = self._request_json(
            method="POST",
            endpoint="/api/chat",
            timeout_seconds=self._generation_timeout_seconds,
            json_body=json_body,
        )
        return self._parse_chat_content(payload)

    @staticmethod
    def _parse_model_names(payload: object) -> tuple[str, ...]:
        error_message = "Ollama-API lieferte eine ungültige Modellliste."

        if not isinstance(payload, dict):
            raise OllamaResponseError(error_message)

        models = payload.get("models")
        if not isinstance(models, list):
            raise OllamaResponseError(error_message)

        names: list[str] = []
        for model in models:
            if not isinstance(model, dict):
                raise OllamaResponseError(error_message)

            name = model.get("name")
            if not isinstance(name, str) or not name.strip():
                raise OllamaResponseError(error_message)
            names.append(name)

        return tuple(names)

    @staticmethod
    def _parse_chat_content(payload: object) -> str:
        error_message = "Ollama-API lieferte keine vollständige Chat-Antwort."
        if not isinstance(payload, dict):
            raise OllamaResponseError(error_message)
        if payload.get("done") is not True:
            raise OllamaResponseError(error_message)
        message = payload.get("message")
        if not isinstance(message, dict):
            raise OllamaResponseError(error_message)
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OllamaResponseError(error_message)
        return content

    def _request_json(
        self,
        method: str,
        endpoint: str,
        timeout_seconds: float,
        json_body: dict[str, object] | None = None,
    ) -> object:
        try:
            response = self._session.request(
                method=method,
                url=f"{self._base_url}{endpoint}",
                timeout=timeout_seconds,
                json=json_body,
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise OllamaConnectionError(
                f"Ollama-API unter {self._base_url} ist nicht erreichbar."
            ) from exc
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise OllamaResponseError(
                "Ollama-API lieferte einen HTTP-Fehler."
            ) from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise OllamaResponseError(
                "Ollama-API lieferte kein gültiges JSON."
            ) from exc
        return payload
