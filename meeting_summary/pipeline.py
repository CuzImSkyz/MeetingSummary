"""Orchestriert Transkription, Zusammenfassung und PDF-Export."""

from pathlib import Path
from typing import Protocol

from .models import MeetingProtocol, Transcript


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> Transcript: ...


class Summarizer(Protocol):
    def summarize(self, transcript: Transcript) -> MeetingProtocol: ...


class PdfExporter(Protocol):
    def export(self, protocol: MeetingProtocol, target_path: Path) -> Path: ...


class MeetingPipeline:
    def __init__(
        self,
        transcriber: Transcriber,
        summarizer: Summarizer,
        pdf_exporter: PdfExporter,
    ) -> None:
        self._transcriber = transcriber
        self._summarizer = summarizer
        self._pdf_exporter = pdf_exporter

    def run(self, audio_path: Path, target_path: Path) -> Path:
        transcript = self._transcriber.transcribe(audio_path)
        protocol = self._summarizer.summarize(transcript)
        return self._pdf_exporter.export(protocol, target_path)
