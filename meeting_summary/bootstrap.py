"""Verdrahtet die konkreten Adapter zur lauffähigen Anwendung."""

from .api.runtime import ApiRuntime
from .application.job_service import ProcessingJobService
from .config import AppConfig
from .pipeline import MeetingPipeline
from .services.audio_metadata import PyAvMeetingTimeResolver
from .services.audio_upload import LocalAudioUploadStore
from .services.infrastructure import InfrastructureChecker
from .services.job_store import InMemoryProcessingJobStore
from .services.ollama_client import OllamaClient
from .services.pdf_export import ReportLabExporter
from .services.summarization import OllamaSummarizer
from .services.task_runner import ThreadPoolTaskRunner
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


def build_api_runtime(config: AppConfig) -> ApiRuntime:
    """Erzeugt die gemeinsam genutzten API-Abhängigkeiten."""

    pipeline = build_pipeline(config)
    store = InMemoryProcessingJobStore()
    audio_upload_store = LocalAudioUploadStore(
        config.api_upload_directory,
        max_bytes=config.api_max_upload_bytes,
    )
    task_runner = ThreadPoolTaskRunner()

    job_service = ProcessingJobService(
        processor=pipeline,
        store=store,
        task_runner=task_runner,
    )

    return ApiRuntime(
        job_service=job_service,
        audio_upload_store=audio_upload_store,
        result_directory=config.api_result_directory,
        task_runner=task_runner,
    )
