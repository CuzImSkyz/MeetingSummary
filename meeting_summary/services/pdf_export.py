"""PDF-Ausgabe mit ReportLab."""

from pathlib import Path

from ..models import MeetingProtocol


class ReportLabExporter:
    def export(self, protocol: MeetingProtocol, target_path: Path) -> Path:
        """Erzeugt künftig ein formatiertes PDF-Dokument."""
        raise NotImplementedError
