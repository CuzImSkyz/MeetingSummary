"""Orchestriert Transkription, Zusammenfassung und PDF-Export."""

from dataclasses import replace
from pathlib import Path
from typing import Protocol

from .models import MeetingProtocol, MeetingTime, Transcript


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
    ) -> None:
        self._transcriber = transcriber
        self._meeting_time_resolver = meeting_time_resolver
        self._summarizer = summarizer
        self._pdf_exporter = pdf_exporter

    def run(self, audio_path: Path, target_path: Path) -> Path:
        meeting_time = self._meeting_time_resolver.resolve(audio_path)
        transcript = self._transcriber.transcribe(audio_path)
        protocol = self._summarizer.summarize(transcript)
        protocol_with_time = replace(
            protocol,
            meeting_time=meeting_time,
        )
        return self._pdf_exporter.export(
            protocol_with_time,
            target_path,
        )
