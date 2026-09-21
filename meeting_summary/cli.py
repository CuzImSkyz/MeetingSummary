"""Kommandozeilenschnittstelle der Anwendung."""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Erstellt aus einer Audiodatei ein Meeting-Protokoll als PDF."
    )
    parser.add_argument("audio", type=Path, help="Pfad zu einer WAV- oder MP3-Datei")
    return parser


def main() -> int:
    """Liest die Kommandozeilenargumente ein und startet später die Pipeline."""
    build_parser().parse_args()
    return 0
