"""Tests für die Kommandozeilenschnittstelle."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from meeting_summary import cli
from meeting_summary.exceptions import TranscriptionError
from meeting_summary.pipeline import MeetingPipeline


def test_main_runs_pipeline_and_prints_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audio_path = tmp_path / "meeting.mp3"
    output_path = tmp_path / "meeting.pdf"

    pipeline = Mock(spec=MeetingPipeline)
    pipeline.run.return_value = output_path
    build_pipeline = Mock(return_value=pipeline)

    monkeypatch.setattr(
        cli,
        "build_pipeline",
        build_pipeline,
        raising=False,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["meeting_summary", str(audio_path)],
    )

    exit_code = cli.main()

    assert exit_code == 0
    build_pipeline.assert_called_once_with()
    pipeline.run.assert_called_once_with(
        audio_path,
        output_path,
    )
    assert capsys.readouterr().out.strip() == (
        f"PDF erstellt: {output_path}"
    )


def test_main_reports_expected_application_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audio_path = tmp_path / "meeting.mp3"

    pipeline = Mock(spec=MeetingPipeline)
    pipeline.run.side_effect = TranscriptionError(
        f"Audiodatei wurde nicht gefunden: {audio_path}"
    )

    monkeypatch.setattr(
        cli,
        "build_pipeline",
        Mock(return_value=pipeline),
        raising=False,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["meeting_summary", str(audio_path)],
    )

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() == (
        f"Fehler: Audiodatei wurde nicht gefunden: {audio_path}"
    )
