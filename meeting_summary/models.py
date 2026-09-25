"""Datenmodelle für Transkription und Protokoll."""

from dataclasses import dataclass


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


@dataclass(frozen=True, slots=True)
class MeetingProtocol:
    short_summary: str
    topics: tuple[TopicSection, ...]
    todos: tuple[TodoItem, ...] = ()
    mentioned_people: tuple[str, ...] = ()
