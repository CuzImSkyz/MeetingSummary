"""Orchestriert Transkription, Zusammenfassung und PDF-Export."""

from dataclasses import replace
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from .models import MeetingProtocol, MeetingTime, Transcript


class ProcessingStage(StrEnum):
    """Semantische Stufen der Meetingverarbeitung."""

    READING_METADATA = "reading_metadata"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    EXPORTING = "exporting"
    COMPLETED = "completed"


class ProgressReporter(Protocol):
    """Empfängt Fortschrittsereignisse ohne Darstellungslogik."""

    def report(self, stage: ProcessingStage) -> None: ...


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> Transcript: ...


class MeetingTimeResolver(Protocol):
    def resolve(self, audio_path: Path) -> MeetingTime: ...


class Summarizer(Protocol):
    def summarize(self, transcript: Transcript) -> MeetingProtocol: ...


class PdfExporter(Protocol):
    def export(self, protocol: MeetingProtocol, target_path: Path) -> Path: ...


class MeetingPipeline:
    def __init__(
        self,
        transcriber: Transcriber,
        meeting_time_resolver: MeetingTimeResolver,
        summarizer: Summarizer,
        pdf_exporter: PdfExporter,
        progress_reporter: ProgressReporter,
    ) -> None:
        self._transcriber = transcriber
        self._meeting_time_resolver = meeting_time_resolver
        self._summarizer = summarizer
        self._pdf_exporter = pdf_exporter
        self._progress_reporter = progress_reporter

    def run(self, audio_path: Path, target_path: Path) -> Path:
        self._progress_reporter.report(ProcessingStage.READING_METADATA)
        meeting_time = self._meeting_time_resolver.resolve(audio_path)
        self._progress_reporter.report(ProcessingStage.TRANSCRIBING)
        transcript = self._transcriber.transcribe(audio_path)
        self._progress_reporter.report(ProcessingStage.SUMMARIZING)
        protocol = self._summarizer.summarize(transcript)
        self._progress_reporter.report(ProcessingStage.EXPORTING)
        protocol_with_time = replace(
            protocol,
            meeting_time=meeting_time,
        )
        result_path = self._pdf_exporter.export(
            protocol_with_time,
            target_path,
        )
        self._progress_reporter.report(ProcessingStage.COMPLETED)
        return result_path
