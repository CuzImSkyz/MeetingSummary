"""Prüft ausschließlich die Entwicklungsumgebung, nicht die Anwendung."""

from __future__ import annotations

import importlib.metadata
import json
import sys
import urllib.error
import urllib.request


PACKAGES = ("faster-whisper", "requests", "reportlab", "pytest", "pyinstaller")
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
EXPECTED_MODEL = "llama3:8b-instruct-q4_K_M"


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    for package in PACKAGES:
        version = importlib.metadata.version(package)
        print(f"{package}: {version}")

    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=3) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"Ollama: NICHT ERREICHBAR ({exc})")
        return 1

    models = {
        item.get("name")
        for item in payload.get("models", [])
        if isinstance(item, dict)
    }
    print("Ollama: erreichbar")
    print(
        f"Modell {EXPECTED_MODEL}: "
        + ("vorhanden" if EXPECTED_MODEL in models else "FEHLT")
    )
    return 0 if EXPECTED_MODEL in models else 1


if __name__ == "__main__":
    raise SystemExit(main())
