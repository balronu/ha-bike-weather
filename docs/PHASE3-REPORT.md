# Phase 3 Report – lokale Beta-Vorbereitung

## Implementiert

- `custom_components/bike_weather/` mit Manifest `0.1.0-beta.1`
- Config Flow und Options Flow mit Quellen- und Profilvalidierung
- DataUpdateCoordinator, HA-/lokale-/OpenWeatherMap-Adapter und per-Metrik-Fallback
- acht native Sensoren ohne große Forecast-Attribute
- redigierte Diagnostics
- authentifizierter WebSocket-Datenvertrag für `bike-weather-card`
- versioniertes, idempotentes Lovelace-Bundle mit Lade-/Fehlerzuständen
- deutsche und englische Übersetzungen sowie Contract-Tests

## Hot-Cutover-Vorbereitung

**Noch nicht ausgeführt:** VM 104, produktive YAML, Dashboards, Entities,
Secrets und gemeinsame Wetterquellen wurden nicht verändert.

Altbestand-Matrix: zwei OpenWeatherMap-REST-Sensoren und vier
Fahrradwetter-Template-Sensoren in `sensor.yaml`/`template.yaml`; bekannte alte
Entities sind in `docs/MIGRATION.md` aufgeführt. Vor dem Cutover müssen Entity
Registry, Helfer, Automationen, Skripte und der exakte Dashboard-Kartenpfad
read-only erneut geprüft und mit Hash/Backup gesichert werden. Es gibt keine
pauschale Namensmuster-Löschung.

Geschützt bleiben OpenWeatherMap, MET Norway, GW1100A und alle gemeinsam
genutzten Wetter-/Lovelace-Ressourcen. Ein vorbereiteter Ablauf darf erst nach
separater Freigabe ausgeführt werden.

## Ergebnisse

| Prüfung | Ergebnis | Bemerkung |
|---|---|---|
| Phase-2 Offline-Suite | PASS | 12 Tests |
| Phase-3 Contract-Suite | PASS | 5 lokale Python-Unittest-Prüfungen |
| Python compileall | PASS | lokale Syntaxprüfung |
| JSON-Validierung | PASS | Manifest, HACS, Übersetzungen |
| Secret-Scan | NOT RUN | Gitleaks lokal nicht vorhanden; manueller Scan ohne Treffer außer Konfigurationsnamen |
| Pytest/Ruff/mypy | NOT RUN | Werkzeuge lokal nicht vorhanden |
| JavaScript-/Frontend-Test und Build | NOT RUN | Node/npm lokal nicht vorhanden |
| Hassfest/HACS | BLOCKED | keine lokale HA-/Container-/Validatorumgebung |
| HA-Initialisierung/Config Flow | NOT RUN | Home Assistant Python-Paket nicht vorhanden |
| Browserkarte | NOT RUN | kein Browser-Test ausgeführt |
| VM 104 / produktive YAML / Dashboard | NOT RUN | absichtlich nicht berührt |

## Risiken und Freigabevoraussetzungen

Vor Installation fehlen echte HA-2026.10.1-Fixture-, Browser-, Hassfest- und
HACS-Gates, die Prüfung der aktuellen Forecast-/Static-Path-API und die
vollständige Fahrfensteransicht in der Karte. Die Beta ist deshalb **NICHT
INSTALLATIONSBEREIT**. Es gab keinen Push, kein Tag und kein Release.
