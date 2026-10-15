# Bike Weather – Phase 4 Beta-Validierung

Datum: 2026-10-15  
Workspace: `/root/.openclaw/workspace/fahrradwetter`  
Kandidat: `0.1.0-beta.1`

## Freigabegate

**Nein – Bike Weather v0.1.0-beta.1 ist noch nicht installationsbereit für
einen produktiven Praxistest.**

Die lokale Core-/Contract-Prüfung ist vollständig grün. Das Gate bleibt aber
offen, weil keine vollständige Home-Assistant-Laufzeit mit Config-Entry-
Lifecycle, echter Registry/Reload-Prüfung, Hassfest/HACS-Validator und
reproduzierbarer Browser-Testsuite gegen eine isolierte HA-Instanz verfügbar
war. Offline-Tests ersetzen diese fehlenden Laufzeitprüfungen ausdrücklich
nicht.

## Isolierte Testumgebung

| Bestandteil | Ergebnis | Nachweis/Grund |
|---|---|---|
| Python | PASS | 3.13.5 in `.venv-phase4` |
| pytest | PASS | 9.1.1, lokal installiert |
| Ruff | PASS | 0.17.0, neuer Core/`bike_weather`/Tests-Bereich |
| mypy | PASS | 2.4.0, `bike_weather_core`, ohne fehlende HA-Imports |
| Node.js | PASS | v24.21.0 |
| Playwright CLI | PASS | 1.64.1 verfügbar; Chromium vorhanden |
| Home Assistant | BLOCKED | Resolver scheitert bei HA 2026.2.3 an Bluetooth-Abhängigkeiten |
| pytest-homeassistant-custom-component | BLOCKED | Installation zieht denselben nicht abgeschlossenen HA-Resolverpfad |
| Hassfest | NOT RUN | kein lokales Tool/Container |
| HACS-Validator | NOT RUN | kein lokales Tool/Container |
| Gitleaks | NOT RUN | Binary nicht vorhanden |
| Docker/Podman | NOT RUN | nicht vorhanden |

Die HA-Installationsversuche liefen ausschließlich in `.venv-phase4`; es
wurde kein Systempaket und keine produktive Umgebung verändert.

## Bootstrap-/Prozessprüfung

Die abschließende Lesekontrolle am 2026-10-15 ergab keinen laufenden
Python-, pip-, curl-, Bootstrap-, `ensurepip`- oder uv-Prozess. Es war daher
kein Prozess zu beenden; OpenClaw-, Gateway- und Systemprozesse wurden nicht
angerührt. Für die zuvor beendeten Installationsversuche liegt kein
persistentes Prozesslog vor. Der letzte bekannte Fehler ist im Abschnitt
„Isolierte Testumgebung“ dokumentiert: der Home-Assistant-Resolver blieb bei
Bluetooth-Abhängigkeiten hängen und wurde kontrolliert abgebrochen. Es wurde
danach kein weiterer Versuch über diesen Installationsweg gestartet.

Die lokale `.venv-phase4` ist für Offline-Prüfungen verwendbar und enthält
Python 3.13.5, pip 26.2.1, pytest, Ruff und mypy. `uv` ist nicht installiert;
eine vollständige HA-Testumgebung steht weiterhin nicht zur Verfügung.

## Tatsächlich ausgeführte Tests

| Prüfung | Ergebnis | Details |
|---|---|---|
| Python pytest | PASS | `PYTHONPATH=. .venv-phase4/bin/pytest -q`: 19 Tests, einschließlich Phase-4-Cutover-Simulation; ohne den lokalen Importpfad ist das Quellworkspace nicht installiert und die Collection schlägt erwartungsgemäß fehl |
| Python unittest | PASS | 17 bestehende Phase-2/3-Tests |
| Ruff | PASS | Core, neue Integration und Tests |
| mypy | PASS | Core mit `--ignore-missing-imports` |
| Python compileall | PASS | Core, beide Integrationspfade, Tests |
| JSON | PASS | Manifest, HACS, strings und Übersetzungen |
| JavaScript Syntax | PASS | `node --check` für die Karte |
| Git-Diff-Check | PASS | keine Whitespace-Fehler |
| Manuelle Secret-/Private-Reference-Suche | PASS | keine produktiven Schlüssel/privaten URLs im neuen Kandidaten |
| Gitleaks | NOT RUN | lokales Binary fehlt |
| Hassfest | BLOCKED | HA-/Validatorumgebung fehlt |
| HACS-Validierung | BLOCKED | Validatorumgebung fehlt |

## Lovelace-/Browserstatus

Der vorhandene Chromium-Smoke-Test wurde in der unterbrochenen Phase-4-
Ausführung mit dem lokalen Bundle durchgeführt und meldete PASS für:

- idempotente Kartenregistrierung;
- Editor-/`config-changed`-Pfad;
- Score- und Forecast-Darstellung;
- Desktop-/Mobile-Overflow-Prüfung.

Zusätzlich sind `node --check` und die Playwright/Chromium-Verfügbarkeit
erneut bestätigt. Nicht als vollständig geschlossen gelten damit weiterhin:
HA-Resource-Registration in einer echten HA-Instanz, Cache-Verhalten nach
Versionswechsel, Light-/Dark-Mode gegen HA-Themes, Browser-Konsole in einer
isolierten HA-Instanz und echte Config-Entry-Auswahl über HA-WebSocket.

## Backend-Abdeckung

Offline abgedeckt sind Normalisierung von lokaler/HA/OpenWeatherMap-Quelle,
per-Metrik-Priorisierung, Frische-/Stale-Fälle, fehlende Werte, Score,
klassische Bewertung, Fahrfenster, Alternativstarts und DST-Fallback. Die
redigierte Diagnostics-Quelle, die WebSocket-Vertragszeichen und die
Forecast-Abgrenzung aus Sensorattributen sind durch Contract-Tests abgedeckt.

Nicht ausgeführt sind Config-Flow/Options-Flow gegen HA, Setup/Unload/Reload
echter Config Entries, mehrere HA-Instanzen, echter Coordinator-Lifecycle,
HA-Weather-Adapter mit HA-State-Machine, authentifizierter HA-WebSocket gegen
eine laufende Instanz und native Diagnostics-Ausgabe.

## Hot-Cutover-Simulation

`tests/test_phase4_cutover.py` simuliert den Ablauf mit Fixture-Daten. Die
Simulation bestätigt:

1. Entfernung nur der sechs exakt identifizierten alten REST-/Template-
   Entities;
2. Erhalt einer gemeinsam genutzten OpenWeatherMap-Entity;
3. Entfernung nur der alten Bike-Weather-Karte;
4. Einfügen der neuen Karte an derselben Kartenliste;
5. unveränderten Erhalt der globalen Mushroom-, Button-Card- und Vertical-
   Stack-Ressourcen;
6. vollständige Wiederherstellung aus einer vorherigen Sicherung.

Das ist eine In-Memory-Simulation. Es wurde kein Bereinigungsskript gegen VM
104 ausgeführt; produktive YAML, Dashboards, Entity Registry, Helfer,
Automationen, Skripte und Wetterintegrationen blieben unverändert.

## Vorgesehene Produktiv-Checklisten

### Hot-Cutover nach ausdrücklicher Freigabe

- [ ] aktuellen HA-/Entity-/Dashboard-Zustand erneut read-only aufnehmen;
- [ ] reguläres Backup und separate YAML-/Dashboard-Sicherungen prüfen;
- [ ] exakte Löschliste mit Registry- und Kartenpfad bestätigen;
- [ ] alte REST-/Template-Blöcke und ausschließlich alte Karte entfernen;
- [ ] YAML validieren und kontrolliert reloaden;
- [ ] neue Integration installieren und Config Flow ausführen;
- [ ] Quellen, Profil, Card und WebSocket/Score/Fahrfenster prüfen;
- [ ] nur eindeutig verwaiste alte Registry-Einträge bereinigen;
- [ ] Abschlussprüfung und Ergebnis dokumentieren.

### Rollback

- [ ] bei kritischem Fehler stoppen und nicht weiter migrieren;
- [ ] gesicherte YAML-/Dashboard-Blöcke wiederherstellen;
- [ ] neue Config Entry entfernen, falls bereits angelegt;
- [ ] alte Karte einsetzen und YAML/Dashboard validieren;
- [ ] Reload/Restart kontrolliert durchführen und Altbestand prüfen.

## Offene Risiken und Voraussetzungen

- HA-Version im isolierten Test muss an die tatsächlich produktiv geplante
  Version angeglichen werden; der verfügbare Resolver zielte auf 2026.2.3.
- Die produktive Ausfallzeit ist ohne HA-Lifecycle-Test nicht seriös messbar.
- Die sechs alten Komponenten und der exakte Lovelace-Pfad müssen unmittelbar
  vor dem Cutover erneut anhand Live-Zustand/Registry bestätigt werden.
- Ein echter Browser-Test muss gegen eine isolierte HA-Instanz mit gültiger
  Authentifizierung und registrierter Resource wiederholt werden.
- Hassfest, HACS und Gitleaks müssen in CI oder einer bereitgestellten
  isolierten Toolchain grün laufen.

## Git- und Sicherheitsgrenzen

Lokale Arbeitsbasis vor dieser Phase: `f7ecc29`, `68ad8ef`, `3f8b0a2`.
Diese Phase enthält nur lokale Workspace-Änderungen. Es gab keinen Push, kein
Tag, kein Release, keine VM-104-Änderung, keine produktive YAML-/Dashboard-
Änderung und keine Verwendung produktiver API-Schlüssel.
