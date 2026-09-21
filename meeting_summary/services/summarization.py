"""Strukturierte Zusammenfassung über die lokale Ollama-API."""

from ..config import AppConfig
from ..models import MeetingProtocol, Transcript


class OllamaSummarizer:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def summarize(self, transcript: Transcript) -> MeetingProtocol:
        """Erzeugt künftig Kurzfassung, Themen und Aufgaben."""
        raise NotImplementedError
