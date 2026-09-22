"""Tests für die Orchestrierung der Meeting-Pipeline."""

from pathlib import Path
from unittest.mock import Mock

from meeting_summary.models import MeetingProtocol, Transcript
from meeting_summary.pipeline import (
    MeetingPipeline,
    PdfExporter,
    Summarizer,
    Transcriber,
)


def test_run_passes_results_through_all_pipeline_steps() -> None:
    audio_path = Path("meeting.wav")
    target_path = Path("meeting.pdf")
    transcript = Transcript(segments=())
    protocol = MeetingProtocol(
        short_summary="Zusammenfassung.",
        topics=(),
        todos=(),
    )

    transcriber = Mock(spec=Transcriber)
    transcriber.transcribe.return_value = transcript

    summarizer = Mock(spec=Summarizer)
    summarizer.summarize.return_value = protocol

    pdf_exporter = Mock(spec=PdfExporter)
    pdf_exporter.export.return_value = target_path

    pipeline = MeetingPipeline(
        transcriber=transcriber,
        summarizer=summarizer,
        pdf_exporter=pdf_exporter,
    )

    result = pipeline.run(audio_path, target_path)

    assert result == target_path
    transcriber.transcribe.assert_called_once_with(audio_path)
    summarizer.summarize.assert_called_once_with(transcript)
    pdf_exporter.export.assert_called_once_with(protocol, target_path)
