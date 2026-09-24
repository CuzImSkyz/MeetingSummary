"""Tests für den faster-whisper-Adapter."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from meeting_summary.config import AppConfig
from meeting_summary.exceptions import TranscriptionError
from meeting_summary.models import Transcript, TranscriptSegment
from meeting_summary.services.transcription import WhisperTranscriber


def test_transcribe_maps_whisper_segments_to_transcript(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "meeting.mp3"
    audio_path.touch()
    whisper_segments = iter(
        (
            SimpleNamespace(
                start=0.0,
                end=1.25,
                text="Erster Satz.",
            ),
            SimpleNamespace(
                start=1.25,
                end=2.5,
                text="Zweiter Satz.",
            ),
        )
    )
    transcription_info = SimpleNamespace(language="de")

    model = Mock(spec=["transcribe"])
    model.transcribe.return_value = (
        whisper_segments,
        transcription_info,
    )

    transcriber = WhisperTranscriber(
        config=AppConfig(
            whisper_hotwords=("Anna", "Release Notes"),
        ),
        model=model,
    )

    result = transcriber.transcribe(audio_path)

    assert result == Transcript(
        segments=(
            TranscriptSegment(
                start_seconds=0.0,
                end_seconds=1.25,
                text="Erster Satz.",
            ),
            TranscriptSegment(
                start_seconds=1.25,
                end_seconds=2.5,
                text="Zweiter Satz.",
            ),
        ),
        language="de",
    )
    model.transcribe.assert_called_once_with(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
        language="de",
        hotwords="Anna, Release Notes",
    )


def test_transcribe_rejects_empty_transcript(tmp_path: Path) -> None:
    audio_path = tmp_path / "silent.mp3"
    audio_path.touch()

    model = Mock(spec=["transcribe"])
    model.transcribe.return_value = (
        iter(()),
        SimpleNamespace(language="de"),
    )
    transcriber = WhisperTranscriber(
        config=AppConfig(),
        model=model,
    )

    with pytest.raises(
        TranscriptionError,
        match="keine Sprache erkannt",
    ):
        transcriber.transcribe(audio_path)


@patch("meeting_summary.services.transcription.WhisperModel")
def test_init_loads_configured_cpu_model(model_class: Mock) -> None:
    model_class.return_value = Mock(spec=["transcribe"])

    WhisperTranscriber(config=AppConfig())
    model_class.assert_called_once_with(
        "small",
        device="cpu",
        compute_type="int8",
    )


@patch("meeting_summary.services.transcription.WhisperModel")
def test_transcribe_uses_default_options_with_loaded_model(
    model_class: Mock,
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "meeting.mp3"
    audio_path.touch()
    model = Mock(spec=["transcribe"])
    model.transcribe.return_value = (
        iter((SimpleNamespace(start=0.0, end=1.0, text="Test."),)),
        SimpleNamespace(language="de"),
    )
    model_class.return_value = model

    transcriber = WhisperTranscriber(config=AppConfig())
    transcriber.transcribe(audio_path)

    model.transcribe.assert_called_once_with(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
        language="de",
        hotwords=None,
    )


def test_transcribe_rejects_missing_audio_file(tmp_path: Path) -> None:
    missing_audio_path = tmp_path / "missing.mp3"
    model = Mock(spec=["transcribe"])
    transcriber = WhisperTranscriber(
        config=AppConfig(),
        model=model,
    )

    with pytest.raises(
        TranscriptionError,
        match="Audiodatei.*nicht gefunden",
    ):
        transcriber.transcribe(missing_audio_path)

    model.transcribe.assert_not_called()


def test_transcribe_translates_model_error(tmp_path: Path) -> None:
    audio_path = tmp_path / "broken.mp3"
    audio_path.touch()

    model = Mock(spec=["transcribe"])
    model.transcribe.side_effect = RuntimeError("Dekodierung fehlgeschlagen")
    transcriber = WhisperTranscriber(AppConfig(), model=model)

    with pytest.raises(
        TranscriptionError,
        match="Transkription ist fehlgeschlagen",
    ):
        transcriber.transcribe(audio_path)


def test_transcribe_translates_segment_iteration_error(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "broken.mp3"
    audio_path.touch()

    def failing_segments():
        raise RuntimeError("Inferenz fehlgeschlagen")
        yield

    model = Mock(spec=["transcribe"])
    model.transcribe.return_value = (
        failing_segments(),
        SimpleNamespace(language="de"),
    )
    transcriber = WhisperTranscriber(AppConfig(), model=model)

    with pytest.raises(
        TranscriptionError,
        match="Transkription ist fehlgeschlagen",
    ):
        transcriber.transcribe(audio_path)


@patch("meeting_summary.services.transcription.WhisperModel")
def test_init_translates_model_loading_error(model_class: Mock) -> None:
    model_class.side_effect = RuntimeError("Modell beschädigt")

    with pytest.raises(
        TranscriptionError,
        match="Whisper-Modell konnte nicht geladen werden",
    ):
        WhisperTranscriber(config=AppConfig())
