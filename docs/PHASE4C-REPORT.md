# Bike Weather – Phase 4C: HA-Laufzeitvalidierung

Datum: 2026-10-15  
Kandidat: `0.1.0-beta.1`  
Arbeitsbaum: `main`, vor diesem Bericht sauber; kein Push, kein Tag, kein Release

## Entscheidung

**NICHT FREIGEGEBEN / NOT READY FOR BETA.**

Die HA-unabhängigen Prüfungen sind grün. Eine vollständige Home-Assistant-
Laufzeitvalidierung war trotz kontrollierter Reparatur des ursprünglichen
`setuptools`-Problems nicht reproduzierbar verfügbar. Deshalb werden Config
Flow, Options Flow, Entry-Lifecycle, Coordinator, Sensoren, authentifizierter
WebSocket, Resource-/Cache-Verhalten und der gemeinsame HA-/Browser-Test nicht
als bestanden gewertet.

## Testumgebungen

| Komponente | Status | Nachweis |
|---|---|---|
| bestehende `.venv-phase4` | PASS | erhalten, Python 3.13.5, pip 26.2.1 |
| System-Python | PASS | Python 3.13.5; keine weiteren Python-3.11/3.12-Interpreter gefunden |
| `uv` / `virtualenv` | NOT RUN | nicht vorhanden |
| HA-Testkopie | BLOCKED | isolierte Kopie der `.venv-phase4`, keine Produktivänderung |
| VM 104 / produktives HA | NOT RUN | ausdrücklich nicht angefasst |

## Build-Blocker und kontrollierter Lösungsversuch

Die analysierte Paketkette lautet:

```text
homeassistant==2026.2.3
└─ home-assistant-bluetooth==1.13.1
   └─ habluetooth>=3.0
      ├─ bleak
      ├─ bleak-retry-connector
      ├─ bluetooth-adapters
      ├─ bluetooth-auto-recovery
      ├─ bluetooth-data-tools
      └─ dbus-fast (Linux)
```

Es wurde kein inkompatibler harter Bluetooth-Pin nachgewiesen. Der ursprüngliche
freie Resolverlauf geriet durch neuere `habluetooth`-Kandidaten bis 7.1.2 und
Source-Builds von `bluetooth-data-tools>=1.29.24` in langes Backtracking.

Für einen kontrollierten Pfad wurden ausschließlich feste, kompatible Kandidaten
verwendet:

```text
HA 2026.2.3
home-assistant-bluetooth 1.13.1
habluetooth 6.1.0
bluetooth-data-tools 1.28.4
bleak 3.0.2
bleak-retry-connector 4.7.1
bluetooth-adapters 2.4.0
bluetooth-auto-recovery 1.6.4
dbus-fast 5.2.0
```

Ergebnisse der begrenzten Versuche:

1. Die venv-Erstellung per `ensurepip` ist weiterhin blockiert, weil
   `python3.13-venv` systemseitig fehlt.
2. Eine Kopie der bestehenden `.venv-phase4` konnte verwendet werden.
3. Der erste PEP-517-Versuch scheiterte bei `lru-dict==1.3.0`, weil im
   isolierten Build `setuptools>=61` fehlte.
4. Ein offizielles `setuptools==80.9.0`-Wheel wurde nur in der temporären Kopie
   installiert; `--no-build-isolation` ließ den `lru-dict`-Metadaten-Build
   erfolgreich passieren.
5. Danach wurden ein beschädigtes altes `tzdata`-Wheel ersetzt und fehlende
   offizielle Wheels für `pytz==2026.5` und `pyrfc3339==2.1.1` ergänzt.
6. Der Lauf stoppte kontrolliert am nächsten fehlenden Transitiv-Wheel
   `anyio`; es gab keinen weiteren Resolverlauf und keine Systeminstallation.

Damit ist die Ursache des ursprünglichen `lru-dict`-Fehlers behoben, aber das
verfügbare Wheelhouse ist für die vollständige HA-Installation nicht vollständig.
Konkreter nächster Weg: CI-Runner oder vorab vollständig erzeugtes, signiertes
Wheelhouse für HA 2026.2.3 mit `python3.13-venv`, `setuptools`, allen exakten
HA-Transitivabhängigkeiten und anschließendem Fixture-Lauf.

## Ausgeführte Prüfungen

| Prüfung | Status | Ergebnis |
|---|---|---|
| pytest Offline-Suite | PASS | 19/19 Tests |
| unittest Offline-Suite | PASS | 17/17 Tests |
| Ruff | PASS | keine Befunde |
| mypy | PASS | keine Befunde im Core |
| compileall | PASS | Core, beide Integrationspfade und Tests |
| JSON/Manifest/HACS-Struktur | PASS | 9 JSON-Dateien parsebar |
| JavaScript-Syntax | PASS | `node --check` |
| Git-Diff-Check | PASS | keine Whitespace-Fehler |
| Gitleaks | PASS | v8.30.0, 7 Commits gescannt, keine Leaks |
| Config Flow / Options Flow gegen HA | BLOCKED | keine HA-Laufzeit |
| Setup / Unload / Reload / mehrere Entries | BLOCKED | keine HA-Laufzeit |
| Coordinator / Sensoren / Wetterquellen | BLOCKED | keine HA-Laufzeit |
| authentifizierter WebSocket / Prognosedaten | BLOCKED | keine HA-Laufzeit |
| Lovelace Resource-Registration / HTTP-Cache | BLOCKED | kein HA-Webserver |
| gemeinsamer HA-/Browser-End-to-End-Test | BLOCKED | keine HA-Laufzeit |

## Hassfest und HACS

Die Workflows `.github/workflows/hassfest.yml` und
`.github/workflows/hacs.yml` sind vorhanden und strukturell nachvollziehbar.

| Validator | Status | Ursache |
|---|---|---|
| Hassfest | NOT RUN / BLOCKED | kein standalone Runner, Docker und Podman fehlen; keine GitHub-Veröffentlichung |
| HACS-Validator | NOT RUN / BLOCKED | kein standalone Runner, Docker und Podman fehlen; keine GitHub-Veröffentlichung |

Die lokalen Ersatzprüfungen für Manifest, Übersetzungen, Versionswert,
`hacs.json`, Integrationsstruktur und JavaScript-Bundle sind PASS, ersetzen
Hassfest/HACS aber nicht.

## Git- und Sicherheitsstatus

- Letzter vorheriger Commit: `76fe93e`.
- Änderungen in dieser Phase: nur dieser Bericht.
- Kein Push, kein Tag, kein Release und keine GitHub-Veröffentlichung.
- Keine VM-104-, HA-, YAML-, Dashboard- oder Produktivdateiänderung.
- Arbeitsbaum vor Berichtserstellung sauber; nach dem Bericht folgt ein lokaler
  Dokumentationscommit.

## Schlussfolgerung

`v0.1.0-beta.1` einschließlich Lovelace-Karte ist **nicht installationsbereit**.
Freigabe ist erst nach einem erfolgreichen HA-Fixture-Lauf auf dem exakten
Kandidaten sowie grünen Hassfest- und HACS-Gates zulässig.
