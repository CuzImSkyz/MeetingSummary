# MeetMe Frontend

Das Frontend bildet die Präsentationsschicht von MeetMe. Es enthält keine
Whisper-, Ollama-, PDF- oder Datenbanklogik. Die Verbindung zum Python-Kern wird
später über eine definierte API hergestellt.

## Entwicklungsumgebung

Voraussetzungen:

- Node.js 24;
- npm 11 oder eine zum Lockfile kompatible neuere Version.

Installation und Start:

```powershell
npm install
npm run dev
```

Die lokale Python-API wird aus dem Projektwurzelverzeichnis separat gestartet:

```powershell
python -m uvicorn meeting_summary.api.app:app --host 127.0.0.1 --port 8765
```

Während der Frontend-Entwicklung leitet Vite Anfragen an `/api` an diese lokale
API weiter. React-Komponenten enthalten deshalb weder Host noch Port. Der
Vite-Proxy gehört nur zur Entwicklungsumgebung; für ein späteres Desktop- oder
Server-Paket wird das Routing separat konfiguriert.

Qualitätsprüfungen:

```powershell
npm test
npm run lint
npm run build
```

`package-lock.json` hält die tatsächlich aufgelösten Abhängigkeiten fest und
muss zusammen mit Änderungen an `package.json` versioniert werden.

## Architektur

```text
src/
├── app/                    App-Komposition und dauerhaftes Layout
├── features/               Benutzerfunktionen und ihre Schnittstellen
│   ├── recording/          Aufnahmeablauf und AudioRecorder-Port
│   └── system/             Zustandsprüfung und HealthClient-Port
├── infrastructure/         technische Adapter
│   ├── audio/              Browser-MediaRecorder-Adapter
│   └── http/               Fetch-Adapter für die lokale Python-API
├── shared/                 gemeinsame Styles und UI-Bausteine
└── test/                   gemeinsame Testkonfiguration
```

Die Abhängigkeitsrichtung lautet:

```text
App/UI → Feature-Schnittstelle ← Browser-Adapter
```

Eine Feature-Komponente greift nicht direkt auf `MediaRecorder`, Whisper oder
Ollama zu. Browser- und Backenddetails werden hinter kleinen Schnittstellen
gekapselt und am App-Einstieg zusammengesetzt.

Der `FetchHealthClient` validiert auch erfolgreiche JSON-Antworten zur Laufzeit.
TypeScript-Typen allein schützen nicht vor fehlerhaften Daten, da sie beim
Kompilieren entfernt werden.

## Styling

- CSS Modules begrenzen Klassennamen auf die jeweilige Komponente.
- Semantische Design-Tokens in `src/shared/styles/tokens.css` definieren Farben,
  Abstände, Radien und Bewegungsdauer.
- Komponenten verwenden Bedeutungen wie `--color-surface`, nicht feste
  Farbwerte. Dadurch bleiben Dark Mode, Light Mode und Branding austauschbar.
- `prefers-reduced-motion` wird bei Animationen berücksichtigt.

## Tests

Vitest führt Logiktests standardmäßig in Node aus. React-Komponententests, die
ein DOM benötigen, erhalten am Dateianfang:

```ts
// @vitest-environment jsdom
```

Browser-APIs wie `MediaRecorder` werden in Unit-Tests durch kleine Fakes ersetzt.
Echte Mikrofon- und Backendzugriffe gehören in getrennte Integrations- oder
End-to-End-Tests.
