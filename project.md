# Projekt-Dokumentation: Offline Meeting-Protokoll-Generator

> Das aktuelle Zielbild und die priorisierte Weiterentwicklung stehen in
> [`docs/roadmap.md`](docs/roadmap.md). Dieses Dokument beschreibt den
> ursprünglichen technischen Ausgangspunkt und wird schrittweise angeglichen.

## 1. Projektübersicht
Ein lokales, datenschutzkonformes Tool zur automatisierten Transkription und strukturierten Zusammenfassung von Meetings. Die Anwendung arbeitet vollständig offline auf der CPU und exportiert die Ergebnisse als formatiertes PDF-Dokument.

## 2. Technische Architektur & Stack
* **Programmiersprache:** Python
* **Speech-to-Text (STT):** `faster-whisper` (Modell: `small`, Quantisierung: `int8`, Ausführung auf CPU)
* **Large Language Model (LLM):** `Llama 3 8B` (über lokal laufendes **Ollama**)
* **PDF-Generierung:** `WeasyPrint` (HTML/CSS zu PDF)
* **Verpackung:** `PyInstaller` (zur Erstellung einer portablen `.exe` für eingeschränkte Windows-11-Work-PCs ohne Admin-Rechte)

## 3. Workflow
1. **Infrastruktur-Check:** Die Anwendung prüft beim Start, ob Ollama läuft und das erforderliche Modell (`llama3:8b-instruct-q4_K_M`) installiert ist (mit automatischer Installations- und Start-Option).
2. **Audio-Eingabe:** Der Nutzer gibt den Pfad zur lokalen Audiodatei (`.wav` oder `.mp3`) ein.
3. **Transkription:** `faster-whisper` wandelt das Audio zeitsynchron in Text um.
4. **Zusammenfassung:** Das Transkript wird per lokaler Ollama-API analysiert. Das Modell generiert:
   * Eine kurze Zusammenfassung (max. 3 Sätze)
   * Thematisch gruppierte Stichpunkte
   * Eine strukturierte To-Do-Liste mit Aufgabenzuweisungen
5. **PDF-Export:** Das Ergebnis wird über ein sauberes HTML/CSS-Layout als PDF im selben Verzeichnis gespeichert.

## 4. Dependencies (`requirements.txt`)
```text
faster-whisper>=1.0.0
requests>=2.31.0
weasyprint>=60.0
