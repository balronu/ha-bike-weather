# Bike Weather – Phase 8A Options-Flow-Report

Stand: 2026-10-15  
Arbeitsbranch: `fix/phase8a-options-flow`  
Produktiv beobachtete Version: `0.1.0-beta.3`  
Home Assistant: `2026.10.1`

## Ergebnis

Der Fehler ist reproduzierbar diagnostiziert und lokal minimal behoben. Die
produktive Home-Assistant-Instanz wurde ausschließlich lesend abgefragt. Es
wurde kein Options Flow gestartet, kein Import-/Reload-Versuch ausgeführt,
keine Config Entry geändert und kein Neustart durchgeführt.

## Produktive Diagnose

Der geladene Config Entry ist:

- Domain: `bike_weather`
- Entry-ID: `01M4ZJKXPY72VZWE5JNRMB8J0P`
- Zustand: `loaded`
- Options Flow: unterstützt
- Installierte Version: `0.1.0-beta.3`

Die read-only HACS-Information bestätigt für `balronu/ha-bike-weather` die
installierte Version `v0.1.0-beta.3`; HACS meldet als verfügbare Fassung den
Beta-3-Main-Commit `1cc785d` und keinen installierten Fix.

Der Read-only-Options-Schema-Abruf schlägt für diesen Entry fehl. Die
produktiven Logs enthalten den folgenden relevanten Traceback:

```text
File "/config/custom_components/bike_weather/config_flow.py", line 54,
    in async_get_options_flow
    return BikeWeatherOptionsFlow(config_entry)
File "/config/custom_components/bike_weather/config_flow.py", line 61,
    in __init__
    self.config_entry = config_entry
AttributeError: property 'config_entry' of 'BikeWeatherOptionsFlow' object
has no setter
```

Damit entsteht der 500-Fehler beim Erzeugen des Options-Flow-Objekts, noch
bevor das Formularschema oder gespeicherte Werte validiert werden. Das
erklärt, warum das Öffnen des Options-Flows scheitert, obwohl die Sensoren
normal liefern.

Die produktive Integration ist weiterhin `loaded`; die Bike-Weather-Sensoren
liefern Werte. Für den Options-Flow wurden keine zusätzlichen Diagnose- oder
Schreiboperationen ausgeführt.

## Ursache

Beta 3 verwendet noch das ältere Muster:

```python
return BikeWeatherOptionsFlow(config_entry)

class BikeWeatherOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
```

In HA 2026.10 stellt die Basisklasse `OptionsFlow` `config_entry` als
schreibgeschützte, von Home Assistant verwaltete Property bereit. Die
Zuweisung im eigenen Konstruktor ist deshalb ungültig. Der Fehler ist kein
EntitySelector-, Übersetzungs-, Voluptuous- oder Beta-2-Datenfehler.

## Beta-2-Kompatibilität

Die Options-Seite liest weiterhin:

```python
values = {**self.config_entry.data, **self.config_entry.options}
```

Damit bleiben bestehende Beta-2-Konfigurationen kompatibel, auch wenn
`options` leer ist: die ursprünglichen Werte aus `data` werden verwendet und
fehlende optionale Felder erhalten die vorhandenen Defaults des Schemas. Es
ist keine Migration, Löschung oder Neuerstellung eines Config Entries nötig.

## Implementierter Fix

`custom_components/bike_weather/config_flow.py` wurde minimal angepasst:

- `async_get_options_flow` erzeugt `BikeWeatherOptionsFlow()` ohne
  Konstruktorargument.
- Der eigene `__init__` wurde entfernt.
- Die HA-verwaltete `self.config_entry`-Property wird weiter in
  `async_step_init` verwendet.
- Provider-Validierung, EntitySelectoren, Defaults und deutsche/englische
  Übersetzungen bleiben unverändert.
- Entity-IDs, Config-Entry-Daten, Sensoren und Dashboard-Inhalte werden nicht
  verändert.

## Regressionstests

Neu: `tests/test_phase8a_options_flow.py`

Die Tests prüfen:

1. Factory und Options-Flow entsprechen der schreibgeschützten HA-Property;
   das alte setter-auslösende Konstrukt wird ausgeschlossen.
2. Die Beta-2-Struktur mit `data` und leerem `options` bleibt über den
   bestehenden Merge-Pfad und die Schema-Defaults abgedeckt.

Die bestehenden Beta-3-Contracts für Config Flow, Übersetzungen, Paketform,
Branding und Laufzeit-Core bleiben aktiv.

## Testergebnisse

| Prüfung | Ergebnis |
|---|---|
| Pytest inkl. Phase-8A-Regression | **29 passed** |
| Ruff | **PASS** |
| Python Compileall | **PASS** |
| `git diff --check` | **PASS** |
| Mypy | **nicht lokal verfügbar** |
| Hassfest | **noch nicht remote ausgeführt** |
| HACS | **noch nicht remote ausgeführt** |
| Gitleaks | **noch nicht remote ausgeführt** |
| GitHub Actions | **noch nicht ausgeführt; Branch ist lokal und nicht gepusht** |

Die fehlenden Remote-Gates sind keine behaupteten Erfolge. Sie benötigen einen
Push des separaten Branches oder eine verfügbare Hassfest-/HACS-Umgebung.

## Beta-4-Einschätzung

**Ja, v0.1.0-beta.4 ist erforderlich.** Beta 3 enthält einen produktiven
Options-Flow-Fehler, der die Bearbeitung bestehender Konfigurationen blockiert.
Der Fix ist klein und rückwärtskompatibel, sollte aber als neue Beta-Version
veröffentlicht werden, damit HACS und Home Assistant ein Paket mit dem
behobenen Code erhalten.

Beta 4 darf erst nach ausdrücklicher Freigabe gemergt, getaggt oder
veröffentlicht werden. Dieser Branch enthält derzeit nur den lokalen Fix und
diesen Bericht; es wurden kein Merge, kein Tag, kein Release und keine
produktive Änderung vorgenommen.

## Offene Punkte

- Remote CI, Hassfest, HACS und Gitleaks müssen nach einem autorisierten Push
  des Branches erfolgreich durchlaufen.
- Danach kann separat über Merge und Beta-4-Veröffentlichung entschieden
  werden.
- Die bestehende Beta-3-Installation auf VM 104 bleibt bis dahin unverändert.
