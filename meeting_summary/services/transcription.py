"""CPU-basierte Transkription mit faster-whisper."""

from pathlib import Path

from faster_whisper import WhisperModel

from ..config import AppConfig
from ..exceptions import TranscriptionError
from ..models import Transcript, TranscriptSegment


class WhisperTranscriber:
    def __init__(
        self,
        config: AppConfig,
        model: WhisperModel | None = None,
    ) -> None:
        self._language = config.whisper_language
        self._hotwords = (
            ", ".join(
                word.strip()
                for word in config.whisper_hotwords
                if word.strip()
            )
            or None
        )

        if model is not None:
            self._model = model
            return

        try:
            self._model = WhisperModel(
                config.whisper_model,
                device="cpu",
                compute_type=config.whisper_compute_type,
            )
        except Exception as exc:
            raise TranscriptionError(
                "Whisper-Modell konnte nicht geladen werden."
            ) from exc

    def transcribe(self, audio_path: Path) -> Transcript:
        if not audio_path.is_file():
            raise TranscriptionError(
                f"Audiodatei wurde nicht gefunden: {audio_path}"
            )
        try:
            segments, info = self._model.transcribe(
                str(audio_path),
                beam_size=5,
                vad_filter=True,
                language=self._language,
                hotwords=self._hotwords,
            )
            raw_segments = tuple(segments)
        except Exception as exc:
            raise TranscriptionError(
                f"Transkription ist fehlgeschlagen: {audio_path}"
            ) from exc

        if not raw_segments or not any(
            segment.text.strip() for segment in raw_segments
        ):
            raise TranscriptionError(
                f"In der Audiodatei wurde keine Sprache erkannt: {audio_path}"
            )

        transcript_segments = tuple(
            TranscriptSegment(
                start_seconds=segment.start,
                end_seconds=segment.end,
                text=segment.text,
            )
            for segment in raw_segments
        )

        return Transcript(
            segments=transcript_segments,
            language=info.language,
        )
