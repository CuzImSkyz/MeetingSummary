# Implementierungsleitfaden

## Ziel und Arbeitsweise

Du implementierst die Anwendung schrittweise selbst. Jeder Schritt endet mit
kleinen Tests, bevor der nächste Dienst angeschlossen wird. Dadurch lassen sich
Fehler einer Schicht zuordnen, statt sie erst in der Gesamtpipeline zu suchen.

Empfohlener Arbeitsmodus mit Codex:

1. Bitte zunächst um eine Erklärung ohne Code.
2. Implementiere den kleinen Schritt selbst.
3. Bitte anschließend um ein Review deiner konkreten Änderung.
4. Lass dir Fehlerursachen erklären, aber nicht sofort die gesamte Lösung schreiben.
5. Fordere vollständigen Code nur an, wenn du nach einem eigenen Versuch feststeckst.

Beispielprompt:

> Erkläre mir die Aufgabe von `OllamaClient.list_models`, die erwarteten Ein- und
> Ausgaben sowie typische Fehlerfälle. Schreibe noch keinen Implementierungscode.

## Architektur

```text
CLI
 └─ MeetingPipeline
     ├─ WhisperTranscriber      Audio -> Transcript
     ├─ OllamaSummarizer        Transcript -> MeetingProtocol
     │   └─ OllamaClient        lokale HTTP-API
     └─ ReportLabExporter       MeetingProtocol -> PDF
```

- `models.py`: reine Datenobjekte, keine externen Bibliotheken.
- `pipeline.py`: Ablaufsteuerung über kleine Schnittstellen (`Protocol`).
- `services/`: Adapter zu Whisper, Ollama und PDF.
- `cli.py`: Argumente, Benutzertexte und Exit-Codes.
- `tests/`: Tests entlang derselben Modulgrenzen.

Die Abhängigkeiten zeigen nur nach innen: Services dürfen die Datenmodelle
kennen. Die Datenmodelle dürfen keine Services kennen.

## Entwicklungsumgebung

Einmalig im Projektverzeichnis:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Danach aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Umgebung prüfen:

```powershell
python .\scripts\doctor.py
pytest
```

Die virtuelle Umgebung ist projektlokal. Es werden keine Pakete global
installiert. Python 3.14 ist auf diesem Rechner vorhanden und wurde mit den
gewählten Paketen geprüft.

## Technische Entscheidung zum PDF-Export

WeasyPrint wurde praktisch getestet und konnte ohne Pango/GLib nicht geladen
werden. Diese nativen Bibliotheken erschweren eine portable Windows-EXE ohne
Administratorrechte. Deshalb verwendet die vorbereitete Umgebung ReportLab.

Konsequenz: Das PDF wird mit ReportLab-Flowables aufgebaut, nicht aus HTML/CSS
gerendert. Die vorhandenen Dateien unter `templates/` bleiben als gestalterische
Referenz erhalten, werden im empfohlenen Weg aber nicht ausgeführt.

## Schritt 1: Datenmodelle verstehen und absichern

Dateien:

- `meeting_summary/models.py`
- `tests/test_models.py`

Prüfe zunächst die vorhandenen Dataclasses. Entscheide bewusst:

- Ist `tuple` oder `list` für Segmente und Aufgaben geeigneter?
- Wie werden Themen strukturiert: `dict[str, list[str]]` oder eigene Dataclass?
- Darf eine Aufgabe keine zuständige Person enthalten?
- Sollen Zeitstempel Sekunden als `float` bleiben?

Akzeptanzkriterien:

- Ein `Transcript` setzt seine Segmente in richtiger Reihenfolge zu Text zusammen.
- Leere oder nur aus Leerzeichen bestehende Segmente sind definiert behandelt.
- Das Protokoll kann Kurzfassung, Themen und Aufgaben eindeutig darstellen.

Codex-Prompt für das Review:

> Prüfe ausschließlich meine Datenmodelle auf Mutabilität, klare Typen und
> spätere JSON-Konvertierbarkeit. Ändere noch keine Dateien.

## Schritt 2: Kleinen Ollama-HTTP-Client bauen

Dateien:

- `meeting_summary/services/ollama_client.py`
- `tests/test_ollama.py`

Implementiere mit `requests.Session` zwei Operationen:

1. `GET /api/tags` liefert die installierten Modellnamen.
2. `POST /api/chat` sendet Modell, Nachrichten, `stream: false` und ein
   JSON-Schema im Feld `format`.

Der Client soll nur HTTP und Antwortformate behandeln. Er darf noch keine
Meeting-Zusammenfassung kennen.

Teste ohne echtes Modell mit einem Fake oder `unittest.mock`. Prüfe mindestens:

- erfolgreiche Antwort;
- Timeout oder Verbindungsfehler;
- HTTP-Fehler;
- syntaktisch ungültiges JSON;
- fehlendes Feld `message.content`.

Danach genau einen echten Aufruf gegen `http://127.0.0.1:11434` ausführen.

## Schritt 3: Infrastrukturprüfung implementieren

Dateien:

- `meeting_summary/services/infrastructure.py`
- `meeting_summary/exceptions.py`

Die Prüfung fragt den Ollama-Client nach Modellen und vergleicht exakt mit
`AppConfig.ollama_model`. Sie installiert und startet noch nichts automatisch.
Automatische Prozesssteuerung kommt erst nach einer stabilen manuellen Version.

Akzeptanzkriterien:

- Ollama nicht erreichbar -> verständlicher eigener Fehler.
- Modell fehlt -> Fehler nennt Sollmodell und vorhandene Modelle.
- Modell vorhanden -> Rückkehr ohne Fehler.

## Schritt 4: Strukturierte Zusammenfassung implementieren

Dateien:

- `meeting_summary/services/summarization.py`
- `tests/test_ollama.py`

Definiere zuerst ein JSON-Schema für:

- `short_summary`: nichtleerer Text, maximal drei Sätze als Promptregel;
- `topics`: Liste aus Überschrift und nichtleeren Stichpunkten;
- `todos`: Aufgabe und optionale zuständige Person.

Wichtige Erkenntnis aus dem realen Test: Ein formal korrektes Schema garantiert
noch keine semantisch vollständigen To-dos. Der Prompt braucht eine explizite
Regel und ein kurzes Beispiel für Formulierungen wie „Anna erstellt den Bericht
bis Freitag“.

Validiere die Modellantwort trotzdem nochmals in Python. Ungültige oder leere
Pflichtfelder dürfen nicht bis zum PDF gelangen.

Akzeptanztest mit echtem Modell:

```text
Anna erstellt den Entwurf bis Freitag.
Ben prüft den Entwurf am Montag.
```

Erwartet werden zwei Aufgaben mit korrekter Zuordnung.

## Schritt 5: Transkription implementieren

Dateien:

- `meeting_summary/services/transcription.py`
- `tests/test_transcription.py`

Baue `WhisperModel` mit:

- Modell `small`;
- `device="cpu"`;
- `compute_type="int8"`;
- optional `vad_filter=True`;
- Beam-Size zunächst 5.

Beachte: `model.transcribe()` liefert einen Generator. Die eigentliche
Transkription erfolgt erst beim Iterieren. Überführe jedes Segment in
`TranscriptSegment` und speichere die erkannte Sprache.

Dateivalidierung vor dem Modellaufruf:

- Datei existiert;
- Dateiendung `.wav` oder `.mp3`;
- leeres Ergebnis wird als fachlicher Fehler behandelt.

Teste zuerst mit einem Fake-Modell. Nutze erst danach eine kurze reale Audiodatei.
Das Whisper-Modell wird beim ersten realen Laden heruntergeladen. Für die spätere
Offline-EXE muss der Modellordner separat vorbereitet oder mit ausgeliefert werden.

## Schritt 6: PDF mit ReportLab implementieren

Dateien:

- `meeting_summary/services/pdf_export.py`
- `tests/test_pdf_export.py`

Verwende `reportlab.platypus`:

- `SimpleDocTemplate` für A4 und Ränder;
- `Paragraph` für Überschriften und Kurzfassung;
- `ListFlowable` für Themenpunkte;
- `Table` für Aufgabe und Zuständigkeit;
- eigene `ParagraphStyle`-Objekte für ein einheitliches Layout.

Akzeptanzkriterien:

- Ausgabepfad endet auf `.pdf`;
- Zielverzeichnis existiert;
- Sonderzeichen und Umlaute funktionieren;
- leere To-do-Liste wird sinnvoll dargestellt;
- Rückgabewert ist der tatsächlich erzeugte Pfad.

Erzeuge im Test eine temporäre PDF-Datei und prüfe mindestens PDF-Header und
Dateigröße. Eine spätere visuelle Prüfung bleibt zusätzlich erforderlich.

## Schritt 7: Pipeline prüfen

Datei:

- `meeting_summary/pipeline.py`

Die vorhandene Pipeline soll nur koordinieren:

```text
audio_path -> transcribe -> summarize -> export -> pdf_path
```

Keine HTTP-, Whisper- oder PDF-Details gehören hier hinein. Schreibe einen Test
mit drei Fakes und prüfe Aufrufreihenfolge sowie weitergereichte Werte.

## Schritt 8: CLI fertigstellen

Dateien:

- `meeting_summary/cli.py`
- `tests/test_cli.py`

Ergänze:

- optionalen Ausgabepfad `--output`;
- `--check` für die Infrastrukturprüfung;
- Standardausgabe `<audio_stem>_protokoll.pdf` neben der Audiodatei;
- klare Fortschrittsmeldungen;
- Exit-Code 0 bei Erfolg, 1 bei erwarteten Fehlern;
- keine vollständigen Tracebacks für normale Benutzerfehler.

Teste die CLI mit gemockter Pipeline. Ein CLI-Test darf weder ein Modell laden
noch Ollama aufrufen.

## Schritt 9: Echter End-to-End-Test

Reihenfolge:

1. `python scripts/doctor.py`
2. `pytest`
3. kurze WAV-Datei, etwa 20 bis 60 Sekunden;
4. Transkript manuell auf grobe Fehler prüfen;
5. Zusammenfassung gegen Transkript prüfen;
6. PDF visuell öffnen und Seitenumbrüche kontrollieren.

Miss getrennt:

- Ladezeit des Whisper-Modells;
- Transkriptionszeit;
- Ollama-Ladezeit;
- Generierungszeit;
- PDF-Zeit.

## Schritt 10: Verpackung erst am Schluss

PyInstaller erst einsetzen, wenn der Python-Aufruf zuverlässig funktioniert.
Zuerst `--onedir`, nicht `--onefile`: Fehler bei Modellen und Binärbibliotheken
sind dort leichter zu untersuchen. Danach können Modellpfad, ReportLab-Ressourcen
und CTranslate2-Binärdateien explizit geprüft werden.

Vor der Zielrechner-Verteilung testen:

- Rechner ohne Python;
- kein Internetzugang;
- Ollama läuft bzw. läuft nicht;
- Modell vorhanden bzw. fehlt;
- Pfade mit Leerzeichen und Umlauten;
- längere Audiodatei;
- Schreibrechte im Audioverzeichnis.

## Nächster konkreter Schritt

Beginne mit Schritt 1. Ändere nur `models.py` und `test_models.py`. Führe dann aus:

```powershell
pytest tests/test_models.py -v
```

Danach ist der Ollama-Client der erste externe Adapter.
