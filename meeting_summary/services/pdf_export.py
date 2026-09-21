"""PDF-Ausgabe mit WeasyPrint."""

from pathlib import Path

from ..models import MeetingProtocol


class WeasyPrintExporter:
    def export(self, protocol: MeetingProtocol, target_path: Path) -> Path:
        """Rendert künftig das HTML-Template als PDF."""
        raise NotImplementedError
