"""Zentrale Anwendungskonfiguration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    whisper_model: str = "small"
    whisper_compute_type: str = "int8"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b-instruct-q4_K_M"
    request_timeout_seconds: int = 300
