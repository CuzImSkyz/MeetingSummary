"""Prüfung der lokal benötigten Infrastruktur."""

from ..config import AppConfig


class InfrastructureChecker:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def check(self) -> None:
        """Prüft künftig Ollama-Dienst und Modellverfügbarkeit."""
        raise NotImplementedError
