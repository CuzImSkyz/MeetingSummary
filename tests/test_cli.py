"""Tests für die Kommandozeilenschnittstelle."""

import sys
from pathlib import Path
from unittest.mock import ANY, Mock

import pytest

from meeting_summary import cli
from meeting_summary.config import AppConfig
from meeting_summary.exceptions import (
    OllamaModelNotInstalledError,
    TranscriptionError,
)
from meeting_summary.pipeline import MeetingPipeline, ProcessingStage


@pytest.mark.parametrize(
    ("stage", "expected_message"),
    [
        (
            ProcessingStage.READING_METADATA,
            "Audiometadaten werden gelesen ...",
        ),
        (
            ProcessingStage.TRANSCRIBING,
            "Audio wird transkribiert ...",
        ),
        (
            ProcessingStage.SUMMARIZING,
            "Protokoll wird zusammengefasst ...",
        ),
        (
            ProcessingStage.EXPORTING,
            "PDF wird erstellt ...",
        ),
        (
            ProcessingStage.COMPLETED,
            "Verarbeitung abgeschlossen.",
        ),
    ],
)
def test_console_progress_reporter_prints_message(
    stage: ProcessingStage,
    expected_message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reporter = cli.ConsoleProgressReporter()

    reporter.report(stage)

    assert capsys.readouterr().out.strip() == expected_message


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
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "meeting_summary",
            "--hotword",
            "Anna",
            "--hotword",
            "Release Notes",
            str(audio_path),
        ],
    )

    exit_code = cli.main()

    assert exit_code == 0
    build_pipeline.assert_called_once_with(
        AppConfig(
            whisper_hotwords=(
                "Anna",
                "Release Notes",
            )
        ),
        progress_reporter=ANY,
    )
    progress_reporter = build_pipeline.call_args.kwargs[
        "progress_reporter"
    ]
    assert isinstance(
        progress_reporter,
        cli.ConsoleProgressReporter,
    )
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

    build_pipeline = Mock(return_value=pipeline)
    monkeypatch.setattr(
        cli,
        "build_pipeline",
        build_pipeline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["meeting_summary", str(audio_path)],
    )

    exit_code = cli.main()
    captured = capsys.readouterr()

    build_pipeline.assert_called_once_with(
        AppConfig(),
        progress_reporter=ANY,
    )
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() == (
        f"Fehler: Audiodatei wurde nicht gefunden: {audio_path}"
    )


def test_main_reports_infrastructure_error_during_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audio_path = tmp_path / "meeting.mp3"
    error_message = (
        "Ollama-Modell 'required-model' ist nicht installiert."
    )
    build_pipeline = Mock(
        side_effect=OllamaModelNotInstalledError(
            error_message
        )
    )

    monkeypatch.setattr(
        cli,
        "build_pipeline",
        build_pipeline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["meeting_summary", str(audio_path)],
    )

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    build_pipeline.assert_called_once_with(
        AppConfig(),
        progress_reporter=ANY,
    )
    assert captured.out == ""
    assert captured.err.strip() == f"Fehler: {error_message}"


def test_main_uses_explicit_output_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audio_path = tmp_path / "meeting.mp3"
    requested_output_path = (
        tmp_path / "exports" / "custom-name.txt"
    )
    exported_output_path = requested_output_path.with_suffix(
        ".pdf"
    )

    pipeline = Mock(spec=MeetingPipeline)
    pipeline.run.return_value = exported_output_path
    build_pipeline = Mock(return_value=pipeline)

    monkeypatch.setattr(
        cli,
        "build_pipeline",
        build_pipeline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "meeting_summary",
            "--output",
            str(requested_output_path),
            str(audio_path),
        ],
    )

    exit_code = cli.main()

    assert exit_code == 0
    build_pipeline.assert_called_once_with(
        AppConfig(),
        progress_reporter=ANY,
    )
    pipeline.run.assert_called_once_with(
        audio_path,
        requested_output_path,
    )
    assert capsys.readouterr().out.strip() == (
        f"PDF erstellt: {exported_output_path}"
    )
