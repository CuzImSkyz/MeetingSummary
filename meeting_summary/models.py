"""Datenmodelle für Transkription und Protokoll."""

from dataclasses import dataclass, field


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
        return " ".join(segment.text.strip() for segment in self.segments).strip()


@dataclass(frozen=True, slots=True)
class TodoItem:
    task: str
    assignee: str | None = None


@dataclass(frozen=True, slots=True)
class MeetingProtocol:
    short_summary: str
    topics: dict[str, list[str]] = field(default_factory=dict)
    todos: tuple[TodoItem, ...] = ()
