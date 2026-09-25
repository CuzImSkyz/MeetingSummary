"""Anwendungsspezifische Fehler."""


class MeetingSummaryError(Exception):
    """Basisklasse für erwartete Anwendungsfehler."""


class InfrastructureError(MeetingSummaryError):
    """Eine lokale Abhängigkeit ist nicht verfügbar oder falsch konfiguriert."""


class OllamaConnectionError(InfrastructureError):
    """Die lokale Ollama-API ist nicht erreichbar."""


class OllamaResponseError(InfrastructureError):
    """Die Ollama-API hat eine fehlerhafte Antwort geliefert."""


class SummarizationError(MeetingSummaryError):
    """Die Modellantwort konnte nicht in ein Protokoll umgewandelt werden."""


class TranscriptionError(MeetingSummaryError):
    """Die Audiodatei konnte nicht transkribiert werden."""


class PdfExportError(MeetingSummaryError):
    """Das Meeting-Protokoll konnte nicht als PDF gespeichert werden."""
