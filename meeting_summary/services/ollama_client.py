"""HTTP-Client für die lokale Ollama-API."""

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

    def list_models(self) -> tuple[str, ...]:
        try:
            response = self._session.get(
                f"{self._base_url}/api/tags",
                timeout=self._status_timeout_seconds,
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

        return self._parse_model_names(payload)

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
