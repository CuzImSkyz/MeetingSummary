# Offline Meeting-Protokoll-Generator

Lokale Python-Anwendung zur Transkription, strukturierten Zusammenfassung und
PDF-Ausgabe von Meetingaufnahmen.

Das zukünftige Zielbild steht getrennt in
[`docs/roadmap.md`](docs/roadmap.md). Dieses Dokument beschreibt ausschließlich
den aktuell implementierten Stand.

## Aktueller Funktionsumfang

Die Anwendung kann:

- lokale WAV- und MP3-Dateien mit `faster-whisper` transkribieren;
- wiederholbare `--hotword`-Optionen für Namen und Fachbegriffe verwenden;
- vor der Verarbeitung Ollama und das konfigurierte Modell prüfen;
- Datum und Uhrzeit aus eingebetteten Audiometadaten übernehmen;
- ohne verwertbare Zeitmetadaten die aktuelle Verarbeitungszeit verwenden;
- Transkripte über ein lokal laufendes Ollama-Modell zusammenfassen;
- Kurzfassung, Themen, genannte Personen und To-dos strukturiert extrahieren;
- ein formatiertes PDF mit To-do-Checkboxen über ReportLab erzeugen;
- erwartete Fehler mit verständlicher Meldung und Exit-Code `1` ausgeben.

## Architektur

```text
CLI
 └─ build_pipeline (Composition Root)
     └─ MeetingPipeline
         ├─ PyAvMeetingTimeResolver  Audio -> MeetingTime
         ├─ WhisperTranscriber       Audio -> Transcript
         ├─ OllamaSummarizer         Transcript -> MeetingProtocol
         │   └─ OllamaClient         lokale Ollama-HTTP-API
         └─ ReportLabExporter        MeetingProtocol -> PDF
```

Die Pipeline koordiniert den Ablauf. Konkrete Bibliotheks- und Transportdetails
liegen in den Adaptern unter `meeting_summary/services/`.

Die Domänenmodelle in `meeting_summary/models.py` kennen weder Whisper, PyAV,
Ollama noch ReportLab. Die Adapter werden ausschließlich im Composition Root
`meeting_summary/bootstrap.py` zusammengesetzt.

## Technischer Stack

- Python 3.14
- `faster-whisper` mit dem Modell `small`
- CPU-Ausführung mit `int8`-Quantisierung
- PyAV zum Lesen eingebetteter Audiometadaten
- Ollama mit `llama3:8b-instruct-q4_K_M`
- ReportLab für die PDF-Erzeugung
- pytest für automatisierte Tests
- PyInstaller als vorgesehenes Verpackungswerkzeug

Die reproduzierbar festgelegten Versionen stehen in `requirements.txt` und
`requirements-dev.txt`.

## Voraussetzungen

- Windows mit installiertem Python 3.14
- installiertes und laufendes Ollama
- lokal verfügbares Ollama-Modell:

```powershell
ollama pull llama3:8b-instruct-q4_K_M
```

Für den späteren Offline-Betrieb müssen Ollama-Modell und Whisper-Modell bereits
lokal vorhanden sein. Der erste Modelldownload kann eine Internetverbindung
benötigen.

## Entwicklungsumgebung einrichten

Im Projektverzeichnis:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Danach die virtuelle Umgebung aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Umgebung und lokale Ollama-Installation prüfen:

```powershell
python .\scripts\doctor.py
```

## Anwendung starten

Ohne Hotwords:

```powershell
python -m meeting_summary ".\local-data\meeting.mp3"
```

Mit mehreren Hotwords:

```powershell
python -m meeting_summary `
  --hotword Anna `
  --hotword "Release Notes" `
  ".\local-data\meeting.mp3"
```

Das PDF wird mit demselben Basisnamen neben der Audiodatei erzeugt:

```text
meeting.mp3 -> meeting.pdf
```

Hotwords sind Hinweise für Whisper. Sie garantieren keine korrekte Erkennung und
dürfen nicht zur nachträglichen Erfindung von Namen verwendet werden.

## Tests ausführen

Gesamte Testsuite:

```powershell
python -m pytest
```

Einzelnes Testmodul:

```powershell
python -m pytest tests\test_cli.py -v
```

Unit-Tests ersetzen Whisper, Ollama und Dateigrenzen durch Mocks oder Fakes.
Reale Modellaufrufe erfolgen nur als bewusste Integrationstests.

## Aktuelle Einschränkungen

Noch nicht implementiert sind insbesondere:

- grafische Desktop-Oberfläche;
- automatische Installation oder Prozesssteuerung von Ollama;
- Datenbank und persistente Meetingverwaltung;
- Sprecherdiarisierung und bestätigte Namenszuordnung;
- RAG-Suche über vergangene Meetings;
- Hintergrundverarbeitung mit Fortschrittsanzeige und Abbruch;
- fertig geprüfte PyInstaller-Auslieferung.

Diese Punkte sind Zielbild, nicht aktueller Funktionsumfang. Ihre geplante
Reihenfolge und Architektur stehen in [`docs/roadmap.md`](docs/roadmap.md).
