"""Tests für die lokale Speicherung von Audio-Uploads."""

from io import BytesIO
from uuid import uuid4

import pytest

from meeting_summary.exceptions import (
    AudioUploadTooLargeError,
    EmptyAudioUploadError,
    UnsupportedAudioFormatError,
)
from meeting_summary.services.audio_upload import LocalAudioUploadStore


def test_save_writes_all_chunks_under_server_filename(
    tmp_path,
) -> None:
    job_id = uuid4()
    payload = b"abcdefg"
    store = LocalAudioUploadStore(
        tmp_path,
        max_bytes=len(payload),
        chunk_size=3,
    )

    result_path = store.save(
        BytesIO(payload),
        job_id,
        ".WEBM",
    )

    assert result_path == tmp_path / f"{job_id}.webm"
    assert result_path.read_bytes() == payload


def test_save_removes_partial_file_when_limit_is_exceeded(
    tmp_path,
) -> None:
    job_id = uuid4()
    store = LocalAudioUploadStore(
        tmp_path,
        max_bytes=4,
        chunk_size=3,
    )

    with pytest.raises(AudioUploadTooLargeError):
        store.save(
            BytesIO(b"abcdef"),
            job_id,
            ".webm",
        )

    assert not (tmp_path / f"{job_id}.webm").exists()


def test_save_removes_empty_file(
    tmp_path,
) -> None:
    job_id = uuid4()
    store = LocalAudioUploadStore(
        tmp_path,
        max_bytes=10,
    )

    with pytest.raises(EmptyAudioUploadError):
        store.save(
            BytesIO(b""),
            job_id,
            ".webm",
        )

    assert not (tmp_path / f"{job_id}.webm").exists()


def test_save_rejects_unsupported_suffix(
    tmp_path,
) -> None:
    store = LocalAudioUploadStore(
        tmp_path,
        max_bytes=10,
    )

    with pytest.raises(UnsupportedAudioFormatError):
        store.save(
            BytesIO(b"content"),
            uuid4(),
            ".exe",
        )


def test_save_does_not_delete_existing_file(
    tmp_path,
) -> None:
    job_id = uuid4()
    existing_path = tmp_path / f"{job_id}.webm"
    existing_path.write_bytes(b"existing")
    store = LocalAudioUploadStore(
        tmp_path,
        max_bytes=10,
    )

    with pytest.raises(FileExistsError):
        store.save(
            BytesIO(b"replacement"),
            job_id,
            ".webm",
        )

    assert existing_path.read_bytes() == b"existing"
