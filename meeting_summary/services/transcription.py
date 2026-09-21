"""CPU-basierte Transkription mit faster-whisper."""

from pathlib import Path

from ..config import AppConfig
from ..models import Transcript


class WhisperTranscriber:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def transcribe(self, audio_path: Path) -> Transcript:
        """Transkribiert künftig WAV- und MP3-Dateien mit Zeitstempeln."""
        raise NotImplementedError
