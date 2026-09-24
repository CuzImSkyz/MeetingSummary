"""Zentrale Anwendungskonfiguration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    whisper_model: str = "small"
    whisper_compute_type: str = "int8"
    whisper_language: str | None = "de"
    whisper_hotwords: tuple[str, ...] = ()
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b-instruct-q4_K_M"
    ollama_status_timeout_seconds: float = 5.0
    ollama_generation_timeout_seconds: float = 600.0