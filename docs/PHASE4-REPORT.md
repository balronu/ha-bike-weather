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
| Home Assistant | BLOCKED | Kontrollierter Wheel-Pfad geprüft; venv-Laufzeit scheitert danach an fehlendem Build-Input `setuptools` für `lru-dict==1.3.0` |
| pytest-homeassistant-custom-component | BLOCKED | Installation zieht denselben nicht abgeschlossenen HA-Resolverpfad |
| Hassfest | NOT RUN | kein lokales Tool/Container |
| HACS-Validator | NOT RUN | kein lokales Tool/Container |
| Gitleaks | PASS | offizielles v8.30.0-Linux-x64-Binary, SHA-256 verifiziert, Scan ohne Treffer |
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

## Untersuchung der Bluetooth-Abhängigkeiten

Die Paketmetadaten aus dem abgebrochenen Resolverlauf wurden ohne erneuten
Resolverlauf ausgewertet:

```text
homeassistant==2026.2.3
└─ home-assistant-bluetooth==1.13.1
   └─ habluetooth>=3.0
      ├─ bleak>=1.0.1 (ab habluetooth 6.1.0: >=3.0.2)
      ├─ bleak-retry-connector>=4.2.0 (ab 6.1.0: >=4.6.0)
      ├─ bluetooth-adapters>=2.1.0
      ├─ bluetooth-auto-recovery>=1.5.1
      ├─ bluetooth-data-tools>=1.28.0
      └─ dbus-fast>=2.30.2 (Linux)
```

Es wurde kein widersprüchlicher harter Bluetooth-Pin gefunden. Pip wählte beim
freien Lauf jedoch neuere `habluetooth`-Kandidaten bis 7.1.2; diese verlangen
`bluetooth-data-tools>=1.29.24`. Für mehrere dieser Versionen lagen nur
Source-Distributionen vor, wodurch der Resolver wiederholt Metadaten und
Builds für `bluetooth-data-tools` erzeugte. Der beobachtete Stillstand war
damit Resolver-/Source-Build-Churn, kein nachgewiesener inkompatibler
Bluetooth-Pin.

Ein kontrollierter, kompatibler Kandidat wurde aus bereits vorhandenen Wheels
geprüft: `habluetooth==6.1.0`, `bluetooth-data-tools==1.28.4`,
`bleak==3.0.2`, `bleak-retry-connector==4.7.1`,
`bluetooth-adapters==2.4.0`, `bluetooth-auto-recovery==1.6.4` und
`dbus-fast==5.2.0`. Die Installation in eine Kopie der Offline-venv wurde
nach fester 90-Sekunden-Grenze abgebrochen, weil `lru-dict==1.3.0` nur als
Source-Paket vorlag und dessen isolierter Build `setuptools>=61` benötigte,
das in der Umgebung nicht vorhanden ist. Es wurde kein Systempaket installiert
und kein inkompatibler Versionszwang verwendet. Ein sinnvoller nächster Weg
ist ein vorab bereitgestelltes, reproduzierbares Wheelhouse inklusive
`setuptools`/`lru-dict` oder ein CI-Runner mit `python3.13-venv`; danach muss
die vollständige HA-Suite erneut gegen die festgelegte HA-Version laufen.

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
| Gitleaks | PASS | v8.30.0 offizielles Binary; Download mit festen Timeouts, SHA-256 `79a3ab57…2470a66e` verifiziert; `detect` exit 0, keine Leaks |
| Hassfest | NOT RUN | Workflow vorhanden, aber kein lokales Hassfest und kein Docker/Podman; keine Veröffentlichung zum Auslösen von CI |
| HACS-Validierung | NOT RUN | Workflow vorhanden, aber kein lokaler HACS-Runner und kein Docker/Podman; keine Veröffentlichung zum Auslösen von CI |

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

Der gezielte Chromium-Lauf auf `/usr/bin/chromium` wurde mit dem vorhandenen
Playwright-Core in einer isolierten Browserseite wiederholt:

| Browserfall | Ergebnis | Nachweis |
|---|---|---|
| Desktop 1280×900 | PASS | Registrierung genau einmal, ein `callWS`, Score/Temperatur gerendert, Editor-Event, kein Overflow |
| Mobile 390×844 | PASS | dieselben Assertions, kein Overflow |
| Browser-Konsole/Page-Fehler | PASS | keine Console-Errors und keine `pageerror`-Meldungen |
| wiederholtes Bundle-Laden | PASS | idempotente `window.customCards`-/Custom-Element-Registrierung |
| echte HA-Resource-/HTTP-Cache-Header | BLOCKED | keine laufende HA-Webserver-Instanz; nur statisches Bundle geprüft |

## Backend-Abdeckung

Offline abgedeckt sind Normalisierung von lokaler/HA/OpenWeatherMap-Quelle,
per-Metrik-Priorisierung, Frische-/Stale-Fälle, fehlende Werte, Score,
klassische Bewertung, Fahrfenster, Alternativstarts und DST-Fallback. Die
redigierte Diagnostics-Quelle, die WebSocket-Vertragszeichen und die
Forecast-Abgrenzung aus Sensorattributen sind durch Contract-Tests abgedeckt.

Nicht ausgeführt sind Config-Flow/Options-Flow gegen HA, Setup/Unload/Reload
echter Config Entries, mehrere HA-Instanzen, echter Coordinator-Lifecycle,
HA-Weather-Adapter mit HA-State-Machine, authentifizierter HA-WebSocket gegen
eine laufende Instanz und native Diagnostics-Ausgabe. Damit ist auch der
gemeinsame End-to-End-Test von Flow, Options Flow, Coordinator, WebSocket und
Karte BLOCKED.

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
- Hassfest und HACS müssen in CI oder einer bereitgestellten isolierten
  Toolchain grün laufen; Gitleaks ist lokal bereits PASS.

## Git- und Sicherheitsgrenzen

Lokale Arbeitsbasis vor dieser Phase: `f7ecc29`, `68ad8ef`, `3f8b0a2`.
Diese Phase enthält nur lokale Workspace-Änderungen. Es gab keinen Push, kein
Tag, kein Release, keine VM-104-Änderung, keine produktive YAML-/Dashboard-
Änderung und keine Verwendung produktiver API-Schlüssel.
