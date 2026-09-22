"""Anwendungsspezifische Fehler."""


class MeetingSummaryError(Exception):
    """Basisklasse für erwartete Anwendungsfehler."""


class InfrastructureError(MeetingSummaryError):
    """Eine lokale Abhängigkeit ist nicht verfügbar oder falsch konfiguriert."""


class OllamaConnectionError(InfrastructureError):
    """Die lokale Ollama-API ist nicht erreichbar."""


class OllamaResponseError(InfrastructureError):
    """Die Ollama-API hat eine fehlerhafte Antwort geliefert."""
