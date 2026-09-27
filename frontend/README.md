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
├── app/              App-Komposition und dauerhaftes Layout
├── features/         Benutzerfunktionen wie Home und Aufnahme
├── infrastructure/   Adapter für Browser- und spätere externe APIs
├── shared/           gemeinsam verwendete Styles und UI-Bausteine
└── test/             gemeinsame Testkonfiguration
```

Die Abhängigkeitsrichtung lautet:

```text
App/UI → Feature-Schnittstelle ← Browser-Adapter
```

Eine Feature-Komponente greift nicht direkt auf `MediaRecorder`, Whisper oder
Ollama zu. Browser- und Backenddetails werden hinter kleinen Schnittstellen
gekapselt und am App-Einstieg zusammengesetzt.

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
