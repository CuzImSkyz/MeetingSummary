"""Tests für die Orchestrierung der Meeting-Pipeline."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, call

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
    ProcessingStage,
    ProgressReporter,
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

    progress_reporter = Mock(spec=ProgressReporter)
    call_order = Mock()
    call_order.attach_mock(
        progress_reporter,
        "progress",
    )
    call_order.attach_mock(
        meeting_time_resolver,
        "meeting_time",
    )
    call_order.attach_mock(
        transcriber,
        "transcriber",
    )
    call_order.attach_mock(
        summarizer,
        "summarizer",
    )
    call_order.attach_mock(
        pdf_exporter,
        "pdf_exporter",
    )

    pipeline = MeetingPipeline(
        transcriber=transcriber,
        meeting_time_resolver=meeting_time_resolver,
        summarizer=summarizer,
        pdf_exporter=pdf_exporter,
    )

    result = pipeline.run(
        audio_path,
        target_path,
        progress_reporter=progress_reporter,
    )

    assert result == target_path
    assert call_order.mock_calls == [
        call.progress.report(
            ProcessingStage.READING_METADATA
        ),
        call.meeting_time.resolve(audio_path),
        call.progress.report(
            ProcessingStage.TRANSCRIBING
        ),
        call.transcriber.transcribe(audio_path),
        call.progress.report(
            ProcessingStage.SUMMARIZING
        ),
        call.summarizer.summarize(transcript),
        call.progress.report(
            ProcessingStage.EXPORTING
        ),
        call.pdf_exporter.export(
            expected_protocol,
            target_path,
        ),
        call.progress.report(
            ProcessingStage.COMPLETED
        ),
    ]
