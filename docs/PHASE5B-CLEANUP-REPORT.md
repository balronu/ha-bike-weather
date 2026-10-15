# Bike Weather – Phase 5B: Bereinigung der alten Fahrradwetter-Lösung

**Datum:** 2026-10-15  
**Ziel:** Home Assistant OS VM 104  
**HA-Version:** 2026.10.1  
**Status:** PASS – alte manuelle Fahrradwetter-Lösung entfernt  
**Beta-Installation:** nicht durchgeführt

## Sicherheitsrahmen

Die Änderungen wurden erst nach erneuter Prüfung gegen
`docs/PHASE5A-CLEANUP-PLAN.md` und nach einem erfolgreichen HA-Vollbackup
ausgeführt. Es wurden keine HACS-Änderungen, keine neue Lovelace-Karte und
keine Bike-Weather-Installation vorgenommen.

Backup:

- Name: `before-bike-weather-phase5b-cleanup`
- Backup-ID: `cd6b7438`
- Status: `Backup completed successfully`
- Größe: 804638720 Bytes
- Dauer: 44 Sekunden
- Zeitpunkt: 2026-10-15 08:53:31 +02:00

## Durchgeführte Änderungen

### PASS – YAML

Aus der aktiv eingebundenen `sensor.yaml` wurden ausschließlich die beiden
alten Fahrradwetter-REST-Blöcke entfernt:

- `sensor.raw_fahrrad_forecast`
- `sensor.fahrradwetter_heute`

Aus dem aktiv eingebundenen `template.yaml` wurde ausschließlich der markierte
Fahrradwetter-Block entfernt. Betroffen waren:

- `sensor.fahrradwetter_aktuell`
- `sensor.fahrradwetter_nachster_block`
- `sensor.fahrradwetter_morgen_06_00`
- `sensor.fahrradwetter_morgen_15_00`

Nach der Änderung lief der HA-Konfigurationscheck erfolgreich durch. Der
verbleibende Fahrradwetter-Kommentar in `sensor.yaml` ist nur Dokumentation und
enthält keine aktive Definition.

### PASS – Lovelace

Im Storage-Dashboard `lovelace`, View `weather` (`/lovelace/weather`), wurde
mit Config-Hash-Locking ausschließlich Abschnitt 5 entfernt: die alte
Fahrradwetter-Titelkarte und der verschachtelte `custom:button-card`-Stack.

Die Änderung wurde durch Home Assistant committed und nach dem Schreiben
verifiziert. Die View bleibt vorhanden; alle übrigen Wetterkarten und
Abschnitte blieben erhalten.

Die gemeinsam verwendeten Lovelace-Ressourcen, insbesondere
`button-card`, Mushroom und Vertical-Stack-in-Card, wurden nicht entfernt.

### PASS – Entity Registry

Nach dem YAML-Reload blieben die vier Template-Entities als `unavailable`
Registry-Einträge bestehen. Nach eindeutiger Zuordnung zu den entfernten
Definitionen und erneuter Verbraucherprüfung wurden ausschließlich diese vier
Einträge entfernt:

- `sensor.fahrradwetter_aktuell`
- `sensor.fahrradwetter_morgen_06_00`
- `sensor.fahrradwetter_morgen_15_00`
- `sensor.fahrradwetter_nachster_block`

Die beiden REST-Sensoren verschwanden nach dem HA-Neustart vollständig; für sie
war kein Registry-Eintrag zu entfernen.

## Reload und Neustart

- `template.reload`: PASS
- HA-Konfigurationsreload: PASS, 16 Komponenten neu geladen
- Der Wrapper konnte den ungezielten `sensor.reload`-Service nicht ausführen,
  weil er fälschlich eine Ziel-Entity verlangte. Es erfolgten keine falschen
  Zielaufrufe.
- Kontrollierter HA-Core-Neustart: PASS, von HA bestätigt und nach ca. 60
  Sekunden wieder erreichbar

Der Neustart war erforderlich, damit die alten REST-Plattformen und ihre
laufenden Zustände vollständig aus dem Prozess verschwinden.

## Abschlussvalidierung

| Prüfung | Status | Ergebnis |
|---|---|---|
| HA-Konfigurationscheck | PASS | `ha core check` erfolgreich |
| YAML-Dateien | PASS | Keine aktiven alten Sensorblöcke mehr |
| Alte Entitäten | PASS | Suche liefert 0 Treffer |
| Entity Registry | PASS | Vier verwaiste Template-Einträge entfernt; REST-Einträge nicht vorhanden |
| Lovelace `/lovelace/weather` | PASS | Keine `fahrrad`-Referenzen mehr |
| Dashboard-Write | PASS | Config-Hash danach `b5aa52d3b6ee90c9` |
| OpenWeatherMap | PASS | Gemeinsame OpenWeatherMap-Sensoren weiterhin vorhanden und mit Zuständen |
| MET Norway / GW1100A / ADS-B | PASS | Nicht verändert; keine Bereinigung dieser Komponenten |
| Automationen/Scripts/Szenen/Helfer | PASS | Keine Fahrradwetter-Referenzen gefunden |
| Backup | PASS | `cd6b7438` erfolgreich erstellt |
| Bike Weather Beta installieren | NOT RUN | ausdrücklich nicht Teil dieser Phase |
| HACS ändern | NOT RUN | ausdrücklich nicht durchgeführt |
| Neue Lovelace-Karte | NOT RUN | ausdrücklich nicht eingerichtet |

## Reste und Einschränkungen

- Der alte Fahrradwetter-Kommentar in `sensor.yaml` bleibt als harmloser
  Kommentar bestehen.
- Nicht aktive historische `sensor.yaml`-/`template.yaml`-Backupdateien wurden
  nicht gelöscht.
- API-Schlüssel, die zuvor inline in den alten REST-URLs standen, wurden im
  Rahmen dieser Bereinigung nicht rotiert. Eine separate Rotation bzw.
  Auslagerung nach `!secret` kann später geprüft werden.
- Die neue Bike-Weather-Beta wurde nicht installiert und nicht produktiv
  getestet.

## Ergebnis

**Phase 5B: PASS für die beauftragte Altlastenbereinigung.**

Die alte manuelle Fahrradwetter-Lösung ist aus der aktiven YAML-Konfiguration,
dem Storage-Dashboard und der Entity Registry entfernt. Die gemeinsamen
Wetterquellen und Lovelace-Ressourcen bleiben erhalten. Die nächste Phase –
Installation und Praxistest von Bike Weather v0.1.0-beta.1 – ist weiterhin ein
separater, noch nicht ausgeführter Schritt.
