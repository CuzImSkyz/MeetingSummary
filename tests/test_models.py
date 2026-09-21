"""Basistests für die Datenmodelle."""

from meeting_summary.models import Transcript, TranscriptSegment


def test_transcript_combines_segment_text() -> None:
    transcript = Transcript(
        segments=(
            TranscriptSegment(0.0, 1.0, "Erster Satz."),
            TranscriptSegment(1.0, 2.0, "Zweiter Satz."),
        )
    )

    assert transcript.text == "Erster Satz. Zweiter Satz."
