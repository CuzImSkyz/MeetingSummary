"""Verdrahtet die konkreten Adapter zur lauffähigen Anwendung."""

from .config import AppConfig
from .pipeline import MeetingPipeline
from .services.audio_metadata import PyAvMeetingTimeResolver
from .services.infrastructure import InfrastructureChecker
from .services.ollama_client import OllamaClient
from .services.pdf_export import ReportLabExporter
from .services.summarization import OllamaSummarizer
from .services.transcription import WhisperTranscriber


def build_pipeline(
    config: AppConfig,
) -> MeetingPipeline:
    """Erzeugt die Anwendung mit den konfigurierten Adaptern."""

    ollama_client = OllamaClient(config)
    infrastructure_checker = InfrastructureChecker(
        config=config,
        client=ollama_client,
    )
    infrastructure_checker.check()

    return MeetingPipeline(
        transcriber=WhisperTranscriber(config),
        meeting_time_resolver=PyAvMeetingTimeResolver(),
        summarizer=OllamaSummarizer(ollama_client),
        pdf_exporter=ReportLabExporter(),
    )
