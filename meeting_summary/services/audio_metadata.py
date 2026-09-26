"""Ermittelt den Meetingzeitpunkt aus Audiometadaten."""

import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import av

from ..models import MeetingTime, MeetingTimeSource


_METADATA_KEYS = (
    "creation_time",
    "date",
    "tdrc",
)
_ISO_DATETIME_PREFIX = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}"
)


class PyAvMeetingTimeResolver:
    """Liest einen Meetingzeitpunkt oder verwendet die Verarbeitungszeit."""

    def __init__(
        self,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._now = now if now is not None else _local_now

    def resolve(self, audio_path: Path) -> MeetingTime:
        """Ermittelt den Zeitpunkt und kennzeichnet dessen Herkunft."""

        try:
            metadata = _read_metadata(audio_path)
        except (av.FFmpegError, OSError):
            return self._fallback_time()

        for key in _METADATA_KEYS:
            raw_value = metadata.get(key)
            if raw_value is None:
                continue

            parsed_value = _parse_metadata_datetime(raw_value)
            if parsed_value is not None:
                return MeetingTime(
                    value=parsed_value,
                    source=MeetingTimeSource.EMBEDDED_METADATA,
                )

        return self._fallback_time()

    def _fallback_time(self) -> MeetingTime:
        return MeetingTime(
            value=self._now(),
            source=MeetingTimeSource.PROCESSING_TIME,
        )


def _read_metadata(audio_path: Path) -> dict[str, str]:
    with av.open(str(audio_path)) as container:
        metadata = {
            key.casefold(): value
            for key, value in container.metadata.items()
            if isinstance(value, str)
        }

        for stream in container.streams.audio:
            for key, value in stream.metadata.items():
                if isinstance(value, str):
                    metadata.setdefault(key.casefold(), value)

    return metadata


def _parse_metadata_datetime(raw_value: str) -> datetime | None:
    normalized_value = raw_value.strip()

    if not _ISO_DATETIME_PREFIX.match(normalized_value):
        return None

    if normalized_value.endswith(("Z", "z")):
        normalized_value = f"{normalized_value[:-1]}+00:00"

    try:
        parsed_value = datetime.fromisoformat(normalized_value)
    except ValueError:
        return None

    if parsed_value.tzinfo is None or parsed_value.utcoffset() is None:
        return parsed_value.astimezone()

    return parsed_value


def _local_now() -> datetime:
    return datetime.now().astimezone()
