"""Prüfung der lokal benötigten Infrastruktur."""

from ..config import AppConfig
from ..exceptions import OllamaModelNotInstalledError
from .ollama_client import OllamaClient


class InfrastructureChecker:
    def __init__(
        self,
        config: AppConfig,
        client: OllamaClient,
    ) -> None:
        self._config = config
        self._client = client

    def check(self) -> None:
        """Prüft, ob das konfigurierte Ollama-Modell installiert ist."""

        available_models = self._client.list_models()
        expected_model = self._config.ollama_model

        if expected_model in available_models:
            return

        if available_models:
            available_description = ", ".join(
                sorted(available_models)
            )
        else:
            available_description = "keine Modelle installiert"

        raise OllamaModelNotInstalledError(
            f"Ollama-Modell '{expected_model}' ist nicht installiert. "
            f"Verfügbare Modelle: {available_description}."
        )
