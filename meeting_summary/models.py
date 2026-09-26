"""Datenmodelle für Transkription und Protokoll."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(frozen=True, slots=True)
class Transcript:
    segments: tuple[TranscriptSegment, ...]
    language: str | None = None

    @property
    def text(self) -> str:
        parts = (segment.text.strip() for segment in self.segments) # clean out empty segments
        return " ".join(part for part in parts if part)


@dataclass(frozen=True, slots=True)
class TopicSection:
    title: str
    bullet_points: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TodoItem:
    task: str
    assignee: str | None = None


class MeetingTimeSource(StrEnum):
    """Kennzeichnet die Herkunft des Meetingzeitpunkts."""

    EMBEDDED_METADATA = "embedded_metadata"
    PROCESSING_TIME = "processing_time"


@dataclass(frozen=True, slots=True)
class MeetingTime:
    """Zeitpunkt eines Meetings einschließlich seiner Herkunft."""

    value: datetime
    source: MeetingTimeSource

    def __post_init__(self) -> None:
        if self.value.tzinfo is None or self.value.utcoffset() is None:
            raise ValueError(
                "MeetingTime benötigt einen Zeitzonen-behafteten Zeitpunkt."
            )


@dataclass(frozen=True, slots=True)
class MeetingProtocol:
    short_summary: str
    topics: tuple[TopicSection, ...]
    todos: tuple[TodoItem, ...] = ()
    mentioned_people: tuple[str, ...] = ()
    meeting_time: MeetingTime | None = None
