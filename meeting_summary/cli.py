"""Kommandozeilenschnittstelle der Anwendung."""

import argparse
import sys
from pathlib import Path

from .bootstrap import build_pipeline
from .config import AppConfig
from .exceptions import MeetingSummaryError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Erstellt aus einer Audiodatei ein Meeting-Protokoll als PDF."
    )
    parser.add_argument(
        "--hotword",
        action="append",
        default=[],
        metavar="BEGRIFF",
        help=(
            "Bevorzugter Name oder Fachbegriff für Whisper; "
            "mehrere hotwords möglich."
        ),
    )
    parser.add_argument(
        "audio",
        type=Path,
        help="Pfad zu einer WAV- oder MP3-Datei",
    )
    return parser


def main() -> int:
    """Verarbeitet eine Audiodatei und meldet das Ergebnis an die Shell."""

    arguments = build_parser().parse_args()
    target_path = arguments.audio.with_suffix(".pdf")
    config = AppConfig(
        whisper_hotwords=tuple(arguments.hotword),
    )

    try:
        result_path = build_pipeline(config).run(
            arguments.audio,
            target_path,
        )
    except MeetingSummaryError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1

    print(f"PDF erstellt: {result_path}")
    return 0
