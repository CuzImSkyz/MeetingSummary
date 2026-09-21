# Projektregeln für die Zusammenarbeit

## Ziel

Dieses Projekt dient nicht nur der Fertigstellung der Anwendung, sondern auch
dem technischen Verständnis des Entwicklers. Änderungen müssen deshalb
nachvollziehbar, modular und überprüfbar bleiben.

## Modern und stabil arbeiten

- Vor technischen Entscheidungen aktuelle stabile Versionen und offizielle
  Primärdokumentation prüfen, wenn sich APIs, Kompatibilität oder Best Practices
  geändert haben könnten.
- Stabile, gepflegte Verfahren bevorzugen. Preview-, Beta- oder experimentelle
  Funktionen nur nach ausdrücklicher Abwägung einsetzen.
- Keine Bibliothek allein wegen einer höheren Versionsnummer aktualisieren.
  Nutzen, Breaking Changes, Plattformkompatibilität und Verpackbarkeit prüfen.
- Veraltete APIs und abgekündigte Muster vermeiden. Relevante Änderungen zur
  bisherigen Lösung ausdrücklich benennen.
- Abhängigkeiten reproduzierbar versionieren und Änderungen daran begründen.

## Erklären und gemeinsam entwickeln

- Vor nichttrivialen Änderungen kurz erklären:
  - welches Problem gelöst wird;
  - welche Schicht oder Schnittstelle betroffen ist;
  - welche Alternativen existieren;
  - warum die gewählte Lösung angemessen ist.
- Nach Änderungen knapp erklären, was sich fachlich und architektonisch geändert
  hat und wie es geprüft wurde.
- Theorie mit dem konkreten Projekt verbinden, nicht abstrakt referieren.
- Wenn der Nutzer selbst implementieren möchte, zuerst Anforderungen,
  Schnittstellen, Datenfluss und Fehlerfälle erklären. Nicht ungefragt die
  vollständige Lösung vorwegnehmen.
- Reviews präzise durchführen: Fehlerursache, Auswirkung und Verbesserung
  getrennt darstellen.
- Unsicherheit kennzeichnen und bei zeitabhängigen technischen Aussagen aktuelle
  offizielle Quellen prüfen.

## Architektur und Modularität

- Module nach klarer Verantwortung trennen.
- Domänenmodelle unabhängig von HTTP-, Whisper-, PDF- und CLI-Details halten.
- Externe Systeme über kleine Adapter kapseln.
- Die Pipeline koordiniert nur; sie implementiert keine Adapterdetails.
- Abhängigkeiten sollen zur Domäne zeigen, nicht von der Domäne zu externen
  Diensten.
- Kleine, typisierte Schnittstellen und Dependency Injection bevorzugen, wenn
  dadurch Tests und Austauschbarkeit tatsächlich verbessert werden.
- Keine zusätzliche Abstraktionsschicht ohne konkreten Nutzen einführen.
- Fehler an Schichtgrenzen in verständliche projektspezifische Fehler übersetzen.
- Tests entlang der Modulgrenzen strukturieren. Externe Modelle und Dienste in
  Unit-Tests durch Fakes oder Mocks ersetzen.

## Git-Arbeitsweise

- Vor Änderungen `git status` und relevante Diffs prüfen.
- Vorhandene Änderungen des Nutzers nicht überschreiben oder ungefragt
  umformatieren.
- Änderungen klein und thematisch zusammenhängend halten.
- Tests vor einem Commit ausführen und das Ergebnis nennen.
- Für abgeschlossene Arbeitsschritte atomare Commits mit klarer, sachlicher
  Commit-Message vorbereiten.
- Keine gemischten Commits aus Refactoring, Feature und unabhängigen
  Formatänderungen erzeugen.
- Keine History umschreiben, keine Force-Pushes, kein `reset --hard` und kein
  Entfernen fremder Änderungen.
- Niemals ohne ausdrückliche Freigabe pushen, rebasen, Tags veröffentlichen oder
  Remote-Branches verändern.
- Wenn ein Commit nicht ausdrücklich beauftragt ist, Änderungen commit-fertig
  hinterlassen und einen passenden Commit-Vorschlag nennen.

## Qualitätsmaßstab

- Korrektheit und Verständlichkeit gehen vor Geschwindigkeit.
- Öffentliche Funktionen und nicht offensichtliche Entscheidungen dokumentieren.
- Keine unnötigen Kommentare, die lediglich den Code wiederholen.
- Fehlerfälle und Plattformgrenzen früh testen.
- Erst Unit-Tests, dann Integrations- und End-to-End-Tests.
- Packaging erst beginnen, wenn die Anwendung aus der Entwicklungsumgebung
  zuverlässig funktioniert.
