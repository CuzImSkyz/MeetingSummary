"""Basistests für die Datenmodelle."""

from meeting_summary.models import (
    Transcript, 
    TranscriptSegment, 
    TodoItem, 
    MeetingProtocol, 
    TopicSection
)


def test_transcript_combines_segment_text() -> None:
    transcript = Transcript(
        segments=(
            TranscriptSegment(0.0, 1.0, "Erster Satz."),
            TranscriptSegment(1.0, 2.0, "            "),
            TranscriptSegment(2.0, 3.0, "Zweiter Satz."),
        )
    )

    assert transcript.text == "Erster Satz. Zweiter Satz."

def test_todo_item_assignee() -> None:
    todo = TodoItem("Bericht erstellen")
    assert todo.assignee is None

def test_protocol_contains_topic() -> None:
    topic = TopicSection(
        title="Bericht",
        bullet_points=("Entwurf erstellen",),
    )
    protocol = MeetingProtocol(
        short_summary="Test",
        topics=(topic,),
    )
    assert topic in protocol.topics