# Bike Weather – Phase 6A: Config-Flow-Diagnose

**Prüfdatum:** 2026-10-15  
**Produktivsystem:** Home Assistant OS VM 104  
**HA Core:** 2026.10.1  
**Installierte Bike-Weather-Version:** 0.1.0-beta.1  
**Status:** Ursache gefunden; lokaler Fix umgesetzt und geprüft

## 1. Produktive READ-ONLY-Diagnose

Die Installation unter `custom_components/bike_weather/` ist vollständig
vorhanden. Gelesen wurden insbesondere:

- `manifest.json`
- `__init__.py`
- `config_flow.py`
- `const.py`
- die übrigen Integrationsdateien, Übersetzungen und das Karten-Bundle

Das Manifest enthält:

- `domain: bike_weather`
- `config_flow: true`
- `version: 0.1.0-beta.1`
- `requirements: []`

Die Config-Flow-Klasse `BikeWeatherConfigFlow` ist mit
`domain=DOMAIN` registriert. Der Flow-Code selbst ist in VM 104 bytegenau
identisch mit dem lokalen Beta-Stand.

## 2. Tatsächlicher Traceback und Ursache

Der HA-Fehlerlog enthält zum fehlgeschlagenen Flow:

```text
2026-10-15 09:09:29.502 ERROR [custom_components.bike_weather]
Error occurred loading flow for integration bike_weather:
No module named 'bike_weather_core'
```

Ursache:

1. `custom_components/bike_weather/coordinator.py` importierte das Modul
   `bike_weather_core` als Top-Level-Paket.
2. Dieses Paket lag im Entwicklungsrepository nur unter dem Repository-Root.
3. HACS installiert jedoch die Integration unter
   `custom_components/bike_weather/` und installiert kein beliebiges
   Repository-Root-Paket als Python-Abhängigkeit.
4. Beim Laden des Config-Flow-Moduls importiert Home Assistant die
   Integrationsmodule; der fehlende Coordinator-Import verhindert dadurch die
   Flow-Registrierung.
5. Die Oberfläche zeigt als Folge lediglich `Invalid handler specified`.

Damit handelt es sich nicht um einen fehlenden `config_flow`-Schlüssel oder
eine falsche `DOMAIN`-Registrierung, sondern um einen HACS-Package-Fehler.

Die HA-Logs enthielten zusätzlich nur die allgemeine Warnung, dass die Custom
Integration nicht von Home Assistant getestet ist. Andere aktuelle Fehler
betrafen fremde Integrationen und waren für Bike Weather nicht ursächlich.

## 3. Lokaler Fix

Geändert wurden ausschließlich Entwicklungsrepository-Dateien:

- `custom_components/bike_weather/coordinator.py`
  - Import von `bike_weather_core` auf den integrationsinternen Import
    `from .core import ...` umgestellt.
- `custom_components/bike_weather/core.py`
  - HA-unabhängiger Runtime-Core direkt innerhalb des HACS-Pakets ergänzt.
  - Enthält die vom Coordinator benötigten Modelle, Normalisierung,
    Quellenpriorisierung sowie Classic-/Score-Bewertung.
- `tests/test_phase3_contract.py`
  - Regressionstest ergänzt, der den integrationsinternen Import und die
    mitgelieferte Core-Datei erzwingt.

Die produktive VM wurde nicht geändert. Es wurde keine HACS-Installation,
kein HA-Konfigurationsreload und kein geplanter Neustart ausgeführt.

## 4. Validierung

| Prüfung | Status | Ergebnis |
|---|---|---|
| Produktive Manifest-/Dateiprüfung | PASS | Integration vollständig, Version beta.1 |
| Produktiver HA-Fehlerlog | PASS | exakte Ursache `No module named 'bike_weather_core'` |
| Lokaler Regressionstest | PASS | 20 pytest bestanden |
| Ruff | PASS | keine Befunde |
| mypy | PASS | Core ohne Befunde |
| Python Compileall | PASS | Integration und Tests kompilieren |
| Lovelace JavaScript-Syntax | PASS | `node --check` bestanden |
| Gebündelter Core-Smoke-Test | PASS | HA-State-Normalisierung und Classic-Score bestanden |
| Produktiver Config-Flow nach Fix | NOT RUN | Fix noch nicht veröffentlicht/installiert |
| VM-104-Änderung | NOT RUN | ausdrücklich nicht durchgeführt |
| HA-Neustart/Reload als Reparatur | NOT RUN | ausdrücklich nicht durchgeführt |
| GitHub-Release | NOT RUN | ausdrücklich nicht durchgeführt |

### Diagnostischer Nebeneffekt

Ein einmaliger direkter Importversuch im laufenden HA-Core-Container zur
Traceback-Bestätigung wurde wegen Speicherdruck mit Exit-Code 137 beendet; der
Supervisor/Watchdog startete den Core-Container anschließend wieder. Dieser
Versuch wurde nicht wiederholt. Es wurden dabei keine Dateien, Config Entries,
Dashboards oder Secrets geändert. Die eigentliche Ursache konnte anschließend
über den gebundenen HA-Fehlerlog eindeutig ermittelt werden.

## 5. Beta-Bewertung

`v0.1.0-beta.1` ist für HACS-Installation **nicht funktionsfähig**, weil der
Runtime-Core nicht im Integrationspaket enthalten war.

Ein neues Release ist erforderlich:

- Ziel: `v0.1.0-beta.2`
- Voraussetzung: lokale CI und Packaging-Prüfungen bestehen; anschließend
  GitHub-Release und HACS-Update separat freigeben.
- Keine vollständige produktive HA-Laufzeitvalidierung behaupten, bevor beta.2
  tatsächlich installiert und der Config Flow auf VM 104 erfolgreich geöffnet
  wurde.

## 6. Offene nächste Schritte

1. Lokalen Commit prüfen und freigeben.
2. Beta.2 in GitHub/CI veröffentlichen – erst nach separater Freigabe.
3. beta.2 auf VM 104 über HACS aktualisieren.
4. Config Flow öffnen und mindestens Config Flow, Options Flow und Setup
   validieren.
5. Erst danach die produktive Bike-Weather-Konfiguration und Karte einrichten.
