# MeetingZusammenfassung – Zielbild und Roadmap

Stand: 25. September 2026. Dieses Dokument hält die besprochenen **Ziele**
fest; es behauptet keinen bereits implementierten Funktionsumfang. Die
tatsächliche Umsetzung ist jeweils am Repository zu prüfen.

## Zweck

Die Anwendung soll Meetings aufnehmen oder importieren, transkribieren und aus
dem Gespräch eine überprüfbare Zusammenfassung mit Entscheidungen, Aufgaben,
Verantwortlichen, Terminen und offenen Fragen erzeugen. Gleichzeitig soll das
Projekt als nachvollziehbarer Kompetenznachweis für Softwareentwicklung und
KI-Integration dienen.

## Festgelegte Reihenfolge

### Phase 1: Standalone für Windows

Priorität hat eine leicht installierbare Windows-Anwendung ohne separat
einzurichtenden Datenbankserver oder Container-Runtime:

- Aufnahme über ein gewähltes Mikrofon sowie Import vorhandener Audiodateien
  und Transkripte.
- Lokale Transkription und wahlweise lokale oder über API erreichbare
  KI-Modelle. Einstellungen für Provider, Modell und API-Key; Schlüssel sicher
  im Betriebssystem-Schlüsselspeicher ablegen, nicht in Klartext in der
  Datenbank oder in Logs.
- SQLite für Meetings, Rohtranskripte, überarbeitete Transkripte, Ergebnisse
  und Bearbeitungsstatus. Export zunächst als Markdown und JSON, später bei
  Bedarf als PDF.
- Verarbeitung im Hintergrund mit sichtbarem Status und verständlicher
  Fehleranzeige; die Oberfläche bleibt während längerer Audio- und
  Modellaufrufe bedienbar.
- Paketierte Windows-Auslieferung als Installer oder ausführbares
  Programmpaket. Ein *einzelnes* EXE-File ist kein zwingendes technisches
  Kriterium: lokale Modellgewichte können erheblich groß sein und separate
  Dateien oder einen optionalen Download erfordern. Offline-Betrieb setzt lokal
  verfügbare Modelle voraus; API-Betrieb benötigt Netzverbindung.
- Einstellungen, Datenablage und eine einfache Sicherungs-/Exportmöglichkeit
  für lokale Daten.

Nach stabiler Persistenz und überprüfbaren Transkriptsegmenten kann Phase 1 um
eine lokale Meeting-Suche und einen beleggestützten Chat erweitert werden. Das
ist keine Voraussetzung für den ersten vorzeigbaren Stand.

### Phase 2: Erweiterbarer Backend-Modus

Nach dem funktionierenden Standalone-Produkt folgen bei tatsächlichem Bedarf:

- REST-API mit dokumentierten Endpunkten und klaren Fehlerantworten.
- PostgreSQL als zweite Persistenz für einen Server- oder Mehrbenutzerbetrieb;
  Migrationen für beide unterstützten Datenbanken.
- Optional `pgvector` für serverseitige Vektorsuche. Die fachliche
  Retrieval-Schnittstelle bleibt dieselbe wie im SQLite-Modus.
- Dockerfile und Docker Compose für reproduzierbaren **Server- und
  Entwicklerbetrieb**. Endnutzer der Standalone-Version benötigen weder Docker
  noch PostgreSQL.
- Robuster Job-Worker, falls Prozesse getrennt laufen oder Jobs über Neustarts
  und mehrere Instanzen hinweg zuverlässig verarbeitet werden müssen.
- Optionale Integrationen: bestätigte Aufgaben als GitHub-, Jira- oder
  Notion-Einträge übertragen. Auto-Update, automatische Sprecheridentifikation
  und persistente Stimmprofile werden erst nach Grundfunktion und Tests
  priorisiert.

## Architekturprinzipien

Geschäftslogik, Oberfläche, Datenbank, Audioverarbeitung, Retrieval und
Modellaufrufe werden über schmale Schnittstellen verbunden. Das ermöglicht
einen SQLite-Standalone-Modus und später einen PostgreSQL-/API-Modus mit
demselben Anwendungskern.

```text
Desktop-Oberfläche                         später: REST-API
        \                                    /
         Anwendungskern / Processing-Service
           |           |          |          |
     Repository   Transkription   KI      Retrieval*
     SQLite       lokal           lokal   FTS + Vektor
     PostgreSQL*  API*            API*    pgvector*

* später oder optional
```

Beispielhafte Domänenobjekte: `Meeting`, `TranscriptSegment`, `Correction`,
`Summary`, `Decision`, `ActionItem`, `ProcessingJob`, später `SpeakerTurn` und
`RetrievalChunk`. Ein Aufgabenpunkt enthält soweit im Gespräch genannt
Beschreibung, Verantwortliche, Termin und Status. Unbekannte Werte bleiben
unbekannt und werden nicht erfunden.

Die Auswahl von Transkriptions-, Zusammenfassungs- und Embedding-Modell soll
unabhängig voneinander möglich sein. Provider-Schnittstellen erlauben
deterministische Testimplementierungen. Timeouts, begrenzte Wiederholungen,
Abbruch, nachvollziehbare Fehler und optional erfasste Laufzeit oder
Tokenkosten gehören zu den jeweiligen Aufrufen.

Für einfache spätere Erweiterbarkeit gelten bereits während der Grundfunktion
folgende Regeln:

- Domänenmodelle enthalten keine SQLite-, PostgreSQL-, HTTP-, PyAV-, Whisper-
  oder Vektordatenbanktypen.
- Externe Systeme werden durch kleine Adapter hinter typisierten Schnittstellen
  gekapselt.
- Die Pipeline koordiniert Schritte, implementiert aber weder
  Transkriptions- noch Retrieval- oder Persistenzdetails.
- Rohdaten und daraus abgeleitete Daten bleiben getrennt. Embeddings und
  Suchindizes sind jederzeit neu erzeugbare Ableitungen, nicht die fachliche
  Quelle.
- Mit Einführung der Persistenz erhalten Meetings, Transkriptsegmente,
  Korrekturen und Ergebnisse stabile IDs.
- Jedes gespeicherte Transkriptsegment behält Start- und Endzeit, Quellenart
  sowie die Beziehung zur Rohfassung. Dadurch können spätere Suchtreffer auf
  eine überprüfbare Audio- oder Textstelle verweisen.
- Modellname, Modellversion und relevante Parameter werden bei abgeleiteten
  Ergebnissen gespeichert. So bleiben Re-Indexierung und Vergleiche
  reproduzierbar.
- Abstraktionen für RAG, Sprechererkennung oder PostgreSQL werden erst
  implementiert, wenn der zugehörige vertikale Anwendungsfall gebaut wird.

## Verarbeitung und Status

```text
Audio/Import → Rohtranskript → geprüfte Korrektur → Zusammenfassung
                                                  ├─ Entscheidungen
                                                  ├─ Aufgaben
                                                  └─ offene Fragen
```

Als Zustände sind `QUEUED`, `TRANSCRIBING`, `CORRECTING`, `SUMMARIZING`,
`COMPLETED` und `FAILED` denkbar. Die genaue Zustandsmaschine wird bei der
Implementierung festgelegt. Für die Desktop-Version reicht zunächst ein
Hintergrundprozess oder Worker innerhalb der Anwendung; ein verteilter
Jobdienst ist dafür nicht nötig. Ein späteres `POST /meetings` kann einen Job
annehmen und einen Status-Endpunkt bereitstellen.

Die aktuelle CLI verwendet davon getrennte, nicht persistierte
`ProcessingStage`-Ereignisse. Sie informieren die Oberfläche über den laufenden
Pipeline-Schritt, bilden aber noch keine Job-State-Machine ab.

## Korrektur von Transkriptionsfehlern

Das **Rohtranskript bleibt unverändert** und wird neben einer bearbeiteten
Fassung gespeichert. Die Korrektur ist ein eigener, einsehbarer
Verarbeitungsschritt vor der Zusammenfassung:

- Offensichtliche Erkennungsfehler und Fachbegriffe nur korrigieren, wenn der
  Gesprächskontext die Änderung hinreichend belegt, etwa „Docket Compose“ →
  „Docker Compose“.
- Keine Aussagen, Personen, Zahlen, Termine, Entscheidungen oder Aufgaben aus
  Plausibilität ergänzen.
- Mehrdeutige Passagen als unklar kennzeichnen und gegebenenfalls zur Prüfung
  im Audio anbieten.
- Ursprünglichen Ausschnitt, Vorschlag und betroffene Stelle nachvollziehbar
  speichern; Korrekturen sollen in der UI prüfbar sein.
- Optional projektspezifisches Vokabular wie Namen, Akronyme und Fachbegriffe
  bereits bei der Transkription verwenden, sofern der jeweilige Anbieter dies
  unterstützt.
- Für wichtige Beschlüsse und Aufgaben nach Möglichkeit eine Fundstelle im
  Transkript hinterlegen. Nutzende bestätigen Korrekturen und Aufgaben vor
  externem Export.

Mögliche strukturierte Ausgabe:

```json
{
  "corrected_transcript": "Wir verwenden Docker Compose.",
  "corrections": [
    {
      "original": "Docket Compose",
      "proposed": "Docker Compose",
      "segment_id": "s42",
      "needs_review": true
    }
  ],
  "uncertain_segments": []
}
```

Eine vom Sprachmodell ausgegebene Zahl wie `confidence: 0.97` ist **keine
kalibrierte Wahrscheinlichkeit** für die Korrektheit. Solche Werte erst nach
Messung und Kalibrierung als Prozentanzeige verwenden. Kontext kann eine
Hypothese liefern; bei strittigen Stellen ist der Abgleich mit der
Audioaufnahme nötig.

## Spätere Sprechertrennung und Namenszuordnung

Sprecherdiarisierung und Sprecheridentifikation sind getrennte Aufgaben:

- Diarisierung ordnet Zeitbereiche zunächst anonymen Sprecherkennungen wie
  `speaker_01` zu.
- Namen werden nur aufgrund expliziter Selbstvorstellung, bestätigter
  Nutzereingabe oder optionaler Sprecherverifikation zugeordnet.
- Eine Ansprache wie „Anna, was meinst du?“ darf höchstens einen prüfpflichtigen
  Namensvorschlag erzeugen, keine bestätigte Identität.
- Stimmhöhe allein ist kein belastbares Identifikationsmerkmal. Eine spätere
  Verifikation verwendet Sprecher-Embeddings und einen evaluierten
  Schwellenwert.
- Persistente Stimmprofile sind optional. Sie benötigen ausdrückliche
  Zustimmung, sichere lokale Speicherung und eine Löschmöglichkeit.

Mögliche spätere Domänenobjekte sind `SpeakerTurn`, `SpeakerIdentity` und
`IdentitySuggestion`. Die Grundpipeline bleibt davon unabhängig und arbeitet
weiterhin gegen eine optionale `SpeakerDiarizer`-Schnittstelle.

## Spätere Meeting-Suche und RAG

Nach stabiler SQLite-Persistenz kann ein Chatfenster Fragen über vergangene
Meetings beantworten. Das System verwendet RAG nur für Fragen, bei denen
unstrukturierte Gesprächsinhalte benötigt werden:

```text
Frage
  ├─ SQL: Aufgaben, Verantwortliche, Status und Termine
  ├─ FTS5: exakte Begriffe, Namen, Zitate und Zeitpunkte
  └─ Hybrid-Retrieval: semantische Fragen über Gesprächsinhalte
          ↓
  relevante Segmente + unmittelbarer Gesprächskontext
          ↓
  LLM-Antwort mit Meeting-, Segment- und Zeitquellen
```

### Indexierung

- Retrieval-Einheiten werden aus zusammengehörigen, zeitgestempelten
  Transkriptsegmenten gebildet; Sätze und Sprecherwechsel werden nicht
  willkürlich zerschnitten.
- Jeder Retrieval-Chunk verweist auf die ursprünglichen Segment-IDs sowie auf
  Start- und Endzeit. Ein Treffer bleibt dadurch bis zur Audioaufnahme
  nachvollziehbar.
- Für die Suche wird bevorzugt die bestätigte Korrekturfassung verwendet. Die
  unveränderte Rohfassung bleibt zur Prüfung erreichbar.
- SQLite FTS5 übernimmt exakte Volltextsuche und BM25-Ranking.
- Ein austauschbarer `EmbeddingProvider` erzeugt lokale Embeddings für
  semantische Suche. Modell und Version werden mitgespeichert.
- In kleinen lokalen Datenbeständen reicht zunächst eine exakte
  Ähnlichkeitssuche. Eine spezielle Vektor-Erweiterung wird erst nach einer
  Messung des Bedarfs eingeführt.

### Retrieval und Antwortgenerierung

- Lexikalische und semantische Kandidaten werden getrennt ermittelt und zu
  einer hybriden Rangliste zusammengeführt.
- Metadatenfilter schränken nach Meeting, Zeitraum, Projekt oder bestätigter
  Person ein.
- Bei Bedarf ergänzt das System direkte Nachbarsegmente, damit Aussagen nicht
  aus ihrem Gesprächskontext gerissen werden.
- Optional bewertet ein Reranker nur die besten Kandidaten neu; er ersetzt
  nicht die erste Suche.
- Das LLM erhält ausschließlich die ausgewählten Belege und darf nur
  bereitgestellte Meeting-, Segment- und Zeitangaben zitieren.
- Ausgegebene Quellen-IDs werden nach der Modellantwort gegen die tatsächlich
  bereitgestellten Belege validiert.
- Ohne ausreichenden Beleg antwortet das System ausdrücklich, dass keine
  belegbare Stelle gefunden wurde.
- Quellen in der Oberfläche sind anklickbar und öffnen Transkript und Audio an
  der betreffenden Stelle.

Mögliche spätere Schnittstellen sind `LexicalRetriever`, `SemanticRetriever`,
`EmbeddingProvider`, `Reranker` und `AnswerGenerator`. Sie werden erst mit dem
jeweiligen vertikalen Suchablauf implementiert.

### Evaluation

Ein anonymisierter Fragensatz enthält erwartete Meeting- und Segment-IDs. Damit
werden mindestens folgende Eigenschaften gemessen:

- `Recall@k` und optional `MRR` für die Retrieval-Qualität,
- Quellenkorrektheit und Abdeckung der Antwort,
- Verhalten bei unbeantwortbaren Fragen,
- Antwortlatenz und Speicherbedarf auf CPU,
- Vergleich von Volltext-, Vektor- und Hybridsuche.

Ein Chatfenster ohne belegbare Quellen oder Retrieval-Evaluation gilt nicht als
abgeschlossene RAG-Funktion.

## Kompetenznachweis im Repository

Priorität hat ein benutzbarer vertikaler Ablauf von Aufnahme oder Import bis
überprüfbarem Export. Engineering-Merkmale werden daran gezeigt:

1. Klare Modulgrenzen und dokumentierte Entwurfsentscheidungen, insbesondere
   SQLite für Standalone und spätere Erweiterung auf PostgreSQL.
2. Strukturierte, validierte Modellausgaben und verlässliche Fehlerbehandlung
   an Datei-, Audio- und API-Grenzen.
3. Aussagekräftige Unit- und Integrationstests mit ersetzten Modellaufrufen;
   zusätzliche Tests für Fehlerzustände und Datenpersistenz.
4. Automatische Qualitätsprüfung in CI, beispielsweise Linting, Typprüfung,
   Tests und später Paketbau. Kein erfundener Coverage-Wert im README.
5. Reproduzierbare Anleitung zum Starten, Testen und Bauen; Beispielmeeting mit
   anonymisierten oder eigens erzeugten Daten, Architekturdiagramm und kurze
   Demonstration.
6. Für eine spätere RAG-Demo: nachvollziehbare Quellen, Retrieval-Metriken und
   ein Vergleich von lexikalischer, semantischer und hybrider Suche.
7. Später eine nachvollziehbare Server-Demo mit REST-API, Migrationen,
   PostgreSQL und Docker Compose.

## Definition für einen ersten vorzeigbaren Stand

Eine Testperson kann die Anwendung auf Windows starten, ein kurzes Meeting
aufnehmen oder importieren, lokal transkribieren, einen Provider für die
Zusammenfassung wählen, den Bearbeitungsstatus sehen, Rohtext und Korrektur
vergleichen, Aufgaben und Entscheidungen prüfen und das Ergebnis exportieren.
Die Tests und eine dokumentierte Build-Anleitung laufen auf einem frischen
Checkout. Online-Provider und lokale Modelle sind mit ihren jeweiligen
Voraussetzungen klar beschrieben.

Sprecheridentifikation und RAG-Chat sind bewusste Erweiterungen nach diesem
ersten vertikalen Stand. Ihre späteren Anforderungen beeinflussen stabile IDs,
Zeitstempel, Quellenbeziehungen und Modulschnittstellen bereits heute, führen
aber nicht zu vorzeitig implementierter Infrastruktur.
