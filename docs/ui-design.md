# MeetMe – UI- und Interaktionskonzept

Status: bestätigt am 26. September 2026.

Dieses Dokument hält die verbindliche gestalterische Richtung fest. Es
beschreibt Zielzustände der Oberfläche, nicht bereits implementierten
Funktionsumfang. Technische Detailentscheidungen werden separat getroffen.

## Technischer Implementierungsstand

Die erste UI-Laufzeit ist inzwischen festgelegt:

- React 19 mit TypeScript und Vite;
- CSS Modules für lokal begrenzte Komponentenstile;
- semantische Design-Tokens für Dark und Light Mode;
- Oxlint sowie der TypeScript-Compiler für statische Prüfungen;
- Vitest und Testing Library für Unit- und Komponententests.

Implementiert sind derzeit die Desktop-App-Shell, Home, der visuelle
Aufnahmebildschirm, ein laufender Aufnahmetimer und ein getesteter
`MediaRecorder`-Browseradapter. Die React-Oberfläche startet und beendet die
Mikrofonaufnahme über eine injizierte `AudioRecorder`-Schnittstelle. Der fertige
Audioblob wird vorübergehend von der App-Komposition gehalten. Die Übergabe an
den Python-Anwendungskern und die anschließende Verarbeitung fehlen noch.

Die Frontend-Struktur trennt App-Komposition, Features, gemeinsame Darstellung
und Infrastrukturadapter. Browser- oder Backenddetails dürfen nicht direkt in
Seitenkomponenten eingebaut werden.

## Produktidentität

- Produktname: **MeetMe**.
- Logo: kompakte abstrahierte Audiowellenmarke mit Wortmarke `MeetMe`.
- Wirkung: modern, dezent, elegant und technisch präzise.
- Keine typische KI-Ästhetik: keine violetten Verläufe, Glaseffekte,
  Funkel-Symbole, Chatbot-Maskottchen oder dekorativen KI-Begriffe.
- Die Oberfläche ist lokal und vertrauenswürdig formuliert. Funktionen werden
  konkret benannt, nicht als Magie dargestellt.

## Farb- und Formensystem

Ausgangswerte für den Dark Mode:

- Hintergrund: `#090a0b`;
- Fläche: `#111315`;
- erhöhte Fläche: `#181b1e`;
- Primärtext: `#f2f0ea`;
- Sekundärtext: `#92979d`;
- Trennlinien: `#292d31`;
- Signalfarbe: Ember `#f06b42`.

Der Light Mode verwendet warme, nicht reinweiße Flächen. Ember bleibt die
einzige dominante Signalfarbe. Farben kennzeichnen keinen Zustand allein;
Text, Form oder Symbol liefern immer eine zweite Bedeutungsebene.

Ecken sind moderat gerundet. Schatten und Animationen bleiben zurückhaltend.

## Navigation und Hauptzustände

Die Desktop-Navigation liegt links und enthält zunächst:

- Home;
- Meetings;
- Einstellungen am unteren Rand.

Der zentrale Ablauf lautet:

```text
Startup → Home → Aufnahme → Verarbeitung → Review/Ergebnis → Meetings
```

Der Startup-Screen zeigt kurz Logo und Produktname. Er darf den Start nicht
künstlich verzögern. Dauert die Initialisierung länger, zeigt er einen echten
Systemstatus statt einer rein dekorativen Animation.

## Home

Home priorisiert genau zwei Aktionen:

1. **Starte Meeting** – große zentrale Primäraktion, beginnt nach erteilter
   Mikrofonfreigabe direkt mit der Aufnahme.
2. **Aufgenommenes Meeting zusammenfassen** – kleinere Dropzone mit Drag-and-
   Drop und Dateiauswahl.

Weitere Funktionen dürfen diese Hierarchie nicht verwässern.

## Aufnahme

Während der Aufnahme zeigt MeetMe:

- klaren Aufnahmestatus und laufende Zeit;
- ein Echtzeit-Frequenz- oder Wellenformdiagramm;
- Pause und Beenden als eindeutige Aktionen;
- später Sprecherkreise mit neutralem Personen-Symbol.

Der aktuell sprechende Kreis wird vergrößert und zusätzlich beschriftet. Diese
Darstellung setzt eine tatsächlich verfügbare Sprecherzuordnung voraus und darf
nicht vorgeben, eine Person sicher erkannt zu haben.

## Vergangene Meetings und RAG

Der Reiter **Meetings** öffnet standardmäßig eine Liste vergangener Meetings.
Jeder Eintrag zeigt mindestens Titel, Zeitpunkt, Dauer und eine knappe
inhaltliche Einordnung.

Die RAG-Unterhaltung ist nicht dauerhaft geöffnet. Die Aktion **MeetMe fragen**
wechselt aus der Listenansicht in eine erweiterte, beleggestützte Unterhaltung.
Eine Zurück-Aktion führt wieder zur Liste.

Für RAG-Antworten gelten folgende Vertrauensregeln:

- jede Tatsachenbehauptung verweist auf mindestens eine Fundstelle;
- Fundstellen nennen Meeting, Zeitstempel und Transkriptausschnitt;
- ein Klick öffnet später Audio oder Transkript an der betreffenden Stelle;
- der Suchraum kann alle oder ausgewählte Meetings umfassen;
- ohne ausreichende Evidenz meldet MeetMe, dass keine belegbare Antwort
  vorliegt, statt Inhalte zu erfinden.

Das LLM formuliert die Antwort. Gespeicherte Transkriptsegmente bleiben die
überprüfbare Quelle.

## Einstellungen

Einstellungen öffnen als seitlicher Drawer über das Zahnrad. Vorgesehen sind:

- Dark, Light und System Mode;
- Hotwords;
- Standard-Ausgabeordner;
- später Modell- und Provider-Einstellungen.

## Responsive Strategie

Die erste Implementierung wird für Desktop- und Laptop-Monitore im Format 16:9
optimiert. Das Layout darf trotzdem keine festen Desktop-Annahmen in
Anwendungslogik oder Komponentenstruktur einbauen.

Startwerte für Layoutwechsel:

- ab `981 px`: vollständige Seitenleiste und mehrspaltige Detailansichten;
- `721–980 px`: kompakte Icon-Seitenleiste für kleine Laptops und Tablets;
- bis `720 px`: einspaltiger Inhalt und untere Navigation für Smartphones.

Komponenten verwenden flexible Breiten, `minmax`-Layouts und umbrechende
Inhalte. Essenzielle Funktionen sind nicht von Hover abhängig. Interaktive
Ziele sind für Touch ungefähr 44 × 44 Pixel groß.

## Bewegung und Barrierefreiheit

- kurze Zustandswechsel statt dauernder dekorativer Bewegung;
- Frequenzdiagramm und Sprecherwechsel dürfen kontinuierlich animieren, wenn
  sie reale Daten darstellen;
- `prefers-reduced-motion` wird unterstützt;
- Tastaturbedienung und sichtbare Fokuszustände bleiben erhalten;
- Kontraste werden vor der Implementierungsfreigabe geprüft;
- Aufnahmestatus und Fehler werden nicht nur durch Farbe kommuniziert.

## Noch nicht festgelegt

- Desktop-Verpackung und Distribution, beispielsweise über Tauri;
- Transportvertrag zwischen React-Frontend und Python-Anwendungskern;
- endgültige Schriftfamilie und Logoausarbeitung;
- genaue Tablet- und Smartphone-Navigation nach Usability-Test;
- visuelle Darstellung des Review- und Ergebnisbildschirms.

