"""Tests für die Ermittlung des Meetingzeitpunkts."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from meeting_summary.models import MeetingTime, MeetingTimeSource
from meeting_summary.services import audio_metadata
from meeting_summary.services.audio_metadata import (
    PyAvMeetingTimeResolver,
)


_FALLBACK_TIME = datetime(
    2026,
    9,
    25,
    20,
    0,
    tzinfo=UTC,
)


def test_resolve_uses_embedded_creation_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_metadata,
        "_read_metadata",
        lambda _: {
            "creation_time": "2026-09-24T18:30:00Z",
        },
    )

    result = PyAvMeetingTimeResolver(
        now=lambda: _FALLBACK_TIME,
    ).resolve(Path("meeting.mp3"))

    assert result == MeetingTime(
        value=datetime(
            2026,
            9,
            24,
            18,
            30,
            tzinfo=UTC,
        ),
        source=MeetingTimeSource.EMBEDDED_METADATA,
    )


def test_resolve_uses_fallback_for_date_without_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_metadata,
        "_read_metadata",
        lambda _: {"tdrc": "2026-09-24"},
    )

    result = PyAvMeetingTimeResolver(
        now=lambda: _FALLBACK_TIME,
    ).resolve(Path("meeting.mp3"))

    assert result == MeetingTime(
        value=_FALLBACK_TIME,
        source=MeetingTimeSource.PROCESSING_TIME,
    )


def test_resolve_uses_fallback_when_metadata_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_read_error(_: Path) -> dict[str, str]:
        raise OSError("Metadaten nicht lesbar")

    monkeypatch.setattr(
        audio_metadata,
        "_read_metadata",
        raise_read_error,
    )

    result = PyAvMeetingTimeResolver(
        now=lambda: _FALLBACK_TIME,
    ).resolve(Path("meeting.mp3"))

    assert result.source is MeetingTimeSource.PROCESSING_TIME
    assert result.value == _FALLBACK_TIME


def test_resolve_rejects_naive_fallback_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_metadata,
        "_read_metadata",
        lambda _: {},
    )

    resolver = PyAvMeetingTimeResolver(
        now=lambda: datetime(2026, 9, 25, 20, 0),
    )

    with pytest.raises(
        ValueError,
        match="Zeitzonen-behafteten",
    ):
        resolver.resolve(Path("meeting.mp3"))


def test_read_metadata_normalizes_keys_and_prefers_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    container = MagicMock()
    container.metadata = {
        "Creation_Time": "2026-09-24T18:30:00Z",
    }

    audio_stream = MagicMock()
    audio_stream.metadata = {
        "creation_time": "2025-01-01T10:00:00Z",
        "TDRC": "2026-09-24",
    }
    container.streams.audio = (audio_stream,)

    context_manager = MagicMock()
    context_manager.__enter__.return_value = container
    open_mock = MagicMock(return_value=context_manager)

    monkeypatch.setattr(
        audio_metadata.av,
        "open",
        open_mock,
    )

    result = audio_metadata._read_metadata(Path("meeting.mp3"))

    assert result == {
        "creation_time": "2026-09-24T18:30:00Z",
        "tdrc": "2026-09-24",
    }
    open_mock.assert_called_once_with("meeting.mp3")
    context_manager.__exit__.assert_called_once()
