"""Anwendungsspezifische Fehler."""


class MeetingSummaryError(Exception):
    """Basisklasse für erwartete Anwendungsfehler."""


class InfrastructureError(MeetingSummaryError):
    """Eine lokale Abhängigkeit ist nicht verfügbar oder falsch konfiguriert."""
