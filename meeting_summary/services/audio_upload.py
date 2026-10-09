"""Lokale Speicherung hochgeladener Audiodateien."""

from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from ..exceptions import (
    AudioUploadTooLargeError,
    EmptyAudioUploadError,
    UnsupportedAudioFormatError,
)


SUPPORTED_AUDIO_SUFFIXES = frozenset(
    {
        ".flac",
        ".m4a",
        ".mp3",
        ".ogg",
        ".wav",
        ".webm",
    }
)


class LocalAudioUploadStore:
    """Speichert Audiodaten begrenzt und unter serverseitigen Dateinamen."""

    def __init__(
        self,
        directory: Path,
        *,
        max_bytes: int,
        chunk_size: int = 1024 * 1024,
    ) -> None:
        if max_bytes <= 0:
            raise ValueError("max_bytes muss größer als null sein.")
        if chunk_size <= 0:
            raise ValueError("chunk_size muss größer als null sein.")

        self._directory = directory
        self._max_bytes = max_bytes
        self._chunk_size = chunk_size

    def save(
        self,
        source: BinaryIO,
        job_id: UUID,
        suffix: str,
    ) -> Path:
        normalized_suffix = suffix.lower()

        if normalized_suffix not in SUPPORTED_AUDIO_SUFFIXES:
            raise UnsupportedAudioFormatError(
                f"Nicht unterstütztes Audioformat: {suffix}"
            )

        self._directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        target_path = self._directory / f"{job_id}{normalized_suffix}"
        written_bytes = 0
        target_created = False

        try:
            with target_path.open("xb") as target:
                target_created = True
                while True:
                    chunk = source.read(self._chunk_size)
                    if not chunk:
                        break

                    written_bytes += len(chunk)
                    if written_bytes > self._max_bytes:
                        raise AudioUploadTooLargeError(
                            "Die hochgeladene Audiodatei überschreitet "
                            "das Größenlimit."
                        )

                    target.write(chunk)

            if written_bytes == 0:
                raise EmptyAudioUploadError(
                    "Die hochgeladene Audiodatei ist leer."
                )
        except Exception:
            if target_created:
                target_path.unlink(missing_ok=True)
            raise

        return target_path
