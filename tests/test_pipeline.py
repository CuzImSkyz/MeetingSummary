"""Tests für die Orchestrierung der Meeting-Pipeline."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

from meeting_summary.models import (
    MeetingProtocol,
    MeetingTime,
    MeetingTimeSource,
    Transcript,
)
from meeting_summary.pipeline import (
    MeetingPipeline,
    MeetingTimeResolver,
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
    meeting_time = MeetingTime(
        value=datetime(2026, 9, 25, 18, 30, tzinfo=UTC),
        source=MeetingTimeSource.EMBEDDED_METADATA,
    )
    expected_protocol = MeetingProtocol(
        short_summary="Zusammenfassung.",
        topics=(),
        todos=(),
        meeting_time=meeting_time,
    )

    transcriber = Mock(spec=Transcriber)
    transcriber.transcribe.return_value = transcript

    meeting_time_resolver = Mock(spec=MeetingTimeResolver)
    meeting_time_resolver.resolve.return_value = meeting_time

    summarizer = Mock(spec=Summarizer)
    summarizer.summarize.return_value = protocol

    pdf_exporter = Mock(spec=PdfExporter)
    pdf_exporter.export.return_value = target_path

    pipeline = MeetingPipeline(
        transcriber=transcriber,
        meeting_time_resolver=meeting_time_resolver,
        summarizer=summarizer,
        pdf_exporter=pdf_exporter,
    )

    result = pipeline.run(audio_path, target_path)

    assert result == target_path
    transcriber.transcribe.assert_called_once_with(audio_path)
    meeting_time_resolver.resolve.assert_called_once_with(audio_path)
    summarizer.summarize.assert_called_once_with(transcript)
    pdf_exporter.export.assert_called_once_with(
        expected_protocol,
        target_path,
    )
