"""Tests für den ReportLab-PDF-Export."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from meeting_summary.exceptions import PdfExportError
from meeting_summary.models import MeetingProtocol, TodoItem, TopicSection
from meeting_summary.services import pdf_export as pdf_export_module
from meeting_summary.services.pdf_export import ReportLabExporter


def test_export_creates_valid_pdf_file(tmp_path: Path) -> None:
    protocol = MeetingProtocol(
        short_summary="Budget < 500 Euro & Termin bestätigt.",
        topics=(),
    )
    target_path = tmp_path / "protokoll.txt"

    result_path = ReportLabExporter().export(protocol, target_path)

    assert result_path == tmp_path / "protokoll.pdf"
    assert result_path.is_file()
    assert result_path.read_bytes().startswith(b"%PDF-")


def test_export_supports_topics_and_todos(tmp_path: Path) -> None:
    protocol = MeetingProtocol(
        short_summary="Der Release wurde besprochen",
        topics=(
            TopicSection(
                title="Release & Betrieb",
                bullet_points=(
                    "Version < 2.0 vorbereiten",
                    "Abnahme durchführen",
                ),
            ),
        ),
        todos=(
            TodoItem(
                task="Release Notes <finalisieren>",
                assignee="Anna & Bob",
            ),
            TodoItem(task="Termin planen"),
        ),
    )

    result_path = ReportLabExporter().export(
        protocol,
        tmp_path / "vollstaendiges-protokoll.pdf",
    )

    assert result_path.is_file()
    assert result_path.read_bytes().startswith(b"%PDF-")


def test_export_translates_reportlab_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = Mock()
    document.build.side_effect = OSError("Datenträger voll")

    monkeypatch.setattr(
        pdf_export_module,
        "SimpleDocTemplate",
        Mock(return_value=document),
    )

    protocol = MeetingProtocol(
        short_summary="Testzusammenfassung",
        topics=(),
    )

    with pytest.raises(
        PdfExportError,
        match="PDF konnte nicht erstellt werden",
    ) as error:
        ReportLabExporter().export(
            protocol,
            tmp_path / "protokoll.pdf",
        )

    assert isinstance(error.value.__cause__, OSError)
