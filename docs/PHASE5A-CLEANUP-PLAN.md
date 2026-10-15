# Bike Weather – Phase 5A: Read-only Altlastenprüfung und Bereinigungsplan

**Prüfdatum:** 2026-10-15  
**Zielsystem:** Home Assistant OS auf VM 104 (`192.168.178.126`)  
**HA-Version:** 2026.10.1  
**Status:** READ-ONLY abgeschlossen; keine Bereinigung ausgeführt

## 1. Sicherheits- und Änderungsgrenze

Die Prüfung erfolgte ausschließlich lesend über den Proxmox-QEMU-Gastagenten im
aktiven HA-Konfigurationsverzeichnis
`/mnt/data/supervisor/homeassistant`. Es wurden keine Dateien geschrieben,
keine Backups erzeugt, keine Dashboards oder Registry-Einträge geändert, kein
Reload/Neustart ausgeführt und keine Beta installiert.

VM 104, produktive YAML-Dateien, Dashboards und Zugangsdaten bleiben
unverändert. Die in den alten REST-URLs vorhandenen API-Schlüssel wurden nicht
in diesen Bericht übernommen. Vor einer späteren Bereinigung sollte ihre
Auslagerung nach `!secret` bzw. eine Rotation separat bewertet werden; das ist
nicht Bestandteil dieses Plans.

## 2. Aktive Konfigurationsquellen

In `configuration.yaml` sind aktiv:

```yaml
sensor: !include sensor.yaml
template: !include template.yaml
homeassistant:
  packages: !include_dir_named packages
```

Die Include-Zeilen befinden sich in `configuration.yaml` bei 17–18; die
Packages-Include-Zeile bei 143. Die vorhandene Datei
`sensor.yaml.sb-c029b468-CWiwAx/sensor.yaml` ist nicht aktiv eingebunden und
wurde nicht verändert. Mehrere alte `template.yaml.bak-*`-Dateien sind ebenfalls
nicht aktive Includes und werden nicht als produktive Konfiguration behandelt.

Der separate ADS-B-REST-Block in `sensor.yaml` ist nicht Fahrradwetter und muss
erhalten bleiben.

## 3. Gefundene alte Fahrradwetter-Komponenten

### 3.1 REST-Sensoren – ausschließlich Fahrradwetter

Aktive Datei: `sensor.yaml`

| Zeilen | Entity | Funktion | Entscheidung |
|---:|---|---|---|
| 6–12 | `sensor.raw_fahrrad_forecast` | OWM-3-Stunden-Forecast-Rohdaten, Attribut `list` | später entfernen |
| 14–24 | `sensor.fahrradwetter_heute` | OWM-Aktuelltemperatur mit Wetter-/Wind-/Regenattributen | später entfernen |

Die beiden URLs sind direkte, nur für diese alten Fahrradwetter-Sensoren
verwendete OpenWeatherMap-Aufrufe. Die gemeinsam genutzte HA-Integration
`weather.openweathermap` und ihre Sensoren sind davon getrennt und bleiben
erhalten.

### 3.2 Template-Sensoren – gemeinsam in einem Block

Aktive Datei: `template.yaml`, Fahrradwetter-Block Zeile 811–988.

| Zeile/Unique ID | Entity | Abhängigkeiten |
|---:|---|---|
| 820–821 / `fahrradwetter_aktuell` | `sensor.fahrradwetter_aktuell` | GW1100A-Außentemperatur/-wind/-regen, Fallback `sensor.fahrradwetter_heute` |
| 866–867 / `fahrradwetter_tagesverlauf` | `sensor.fahrradwetter_nachster_block` | `sensor.raw_fahrrad_forecast` |
| 900–901 / `fahrradwetter_morgen_0630` | `sensor.fahrradwetter_morgen_06_00` | `sensor.raw_fahrrad_forecast` |
| 946–947 / `fahrradwetter_morgen_1600` | `sensor.fahrradwetter_morgen_15_00` | `sensor.raw_fahrrad_forecast` |

Die vier Sensordefinitionen können später als zusammenhängender, klar
markierter Block entfernt werden. Andere Template-Sensoren in derselben Datei
bleiben unverändert.

## 4. Entity-Registry und aktueller Zustand

Die sechs alten Entity-IDs waren zum Prüfzeitpunkt als Zustände vorhanden:

- `sensor.fahrradwetter_aktuell`
- `sensor.fahrradwetter_heute`
- `sensor.fahrradwetter_morgen_06_00`
- `sensor.fahrradwetter_morgen_15_00`
- `sensor.fahrradwetter_nachster_block`
- `sensor.raw_fahrrad_forecast`

Für die vier YAML-Template-Sensoren lieferte die Entity-Registry aktive
Einträge mit `platform: template`, ohne Config-Entry und ohne Gerät:

- `fahrradwetter_aktuell`
- `fahrradwetter_morgen_0630`
- `fahrradwetter_morgen_1600`
- `fahrradwetter_tagesverlauf`

Für die beiden REST-Sensoren lieferte die Registry-Abfrage keinen Eintrag,
obwohl beide Zustände aktiv waren. Das ist vor der späteren Entfernung erneut
über HA-UI/API zu verifizieren; daraus darf nicht automatisch auf verwaiste
Registry-Einträge geschlossen werden. Registry-Dateien werden nicht direkt
bearbeitet.

## 5. Verbraucher- und Referenzprüfung

### PASS – Konfigurationsoberflächen

Die gezielte HA-Konfigurationssuche nach allen sechs Entity-IDs ergab:

- keine Treffer in Automationen,
- keine Treffer in Scripts,
- keine Treffer in Szenen,
- keine Treffer in Helfern,
- `partial: false`, also keine zeitbudgetbedingte Teilauswertung.

Der lesende YAML-Scan außerhalb von `sensor.yaml` und `template.yaml` ergab
ebenfalls keine weiteren Fahrradwetter-Referenzen in den aktiven YAML-/Package-
Dateien. Die Referenzen innerhalb des Definitionsblocks selbst sind oben
aufgeführt.

### PASS – Dashboard-Lokalisation

Das Storage-Dashboard `lovelace` (`Übersicht`) enthält die View:

- URL: `/lovelace/weather`
- View-Titel: `Wetter`
- View-Index: 18 von 38
- View-Typ: `sections`
- Abschnitt: Index 5 (sechster Abschnitt)
- Kartenpfad: `config['views'][18]['sections'][5]['cards']`

Der alte Fahrradwetter-Bereich besteht dort aus:

1. `custom:mushroom-title-card` mit Titel `🚲 Fahrradwetter` und Untertitel
   `Jetzt, nächster Block und morgen`.
2. `custom:vertical-stack-in-card` mit einer verschachtelten
   `custom:button-card`. Deren JavaScript referenziert:
   - `sensor.fahrradwetter_heute`
   - `sensor.fahrradwetter_nachster_block`
   - `sensor.fahrradwetter_morgen_06_00`
   - `sensor.fahrradwetter_morgen_15_00`

Die Karte referenziert nicht `sensor.fahrradwetter_aktuell` und nicht
`sensor.raw_fahrrad_forecast`. Im zweiten Storage-Dashboard
`dashboard_wohnmobil` wurden keine Fahrradwetter-Treffer gefunden.

### PASS – Lovelace-Ressourcenabgrenzung

Es sind 83 Ressourcen registriert (82 Module, 1 CSS, 4 Inline-Ressourcen).
Keine URL oder Inline-Ressource ist als Fahrradwetter-spezifisch erkennbar.
Die alte Karte nutzt die gemeinsam verwendete Ressource
`/hacsfiles/button-card/button-card.js`; diese Ressource darf nicht entfernt
werden. Gleiches gilt für Mushroom, Vertical-Stack-in-Card und alle übrigen
gemeinsam verwendeten Ressourcen.

## 6. Gemeinsam genutzte Komponenten – ausdrücklich behalten

Bei der späteren Bereinigung nicht anfassen:

- HA-Integration `weather.openweathermap` und zugehörige gemeinsame Sensoren,
- MET Norway,
- GW1100A-Wetterstation und deren Sensoren,
- den ADS-B-REST-Block in `sensor.yaml`,
- alle übrigen Templates in `template.yaml`,
- andere Wetterkarten und Automationen,
- gemeinsam verwendete Lovelace-Ressourcen, insbesondere `button-card`.

Der Template-Sensor `sensor.fahrradwetter_aktuell` liest GW1100A-Werte als
bevorzugte lokale Quelle. Diese Abhängigkeit bedeutet nicht, dass GW1100A
entfernt werden darf; beim Entfernen wird nur der alte Fahrradwetter-Ableger
entfernt.

## 7. Präziser Bereinigungsplan (noch nicht ausführen)

Die folgenden Schritte benötigen eine separate ausdrückliche Freigabe.

1. **Vorher-Zustand sichern:** HA-Vollbackup über die unterstützte HA-Oberfläche
   bzw. Supervisor-Funktion erstellen und dessen Abschluss prüfen. Zusätzlich
   die aktuelle `sensor.yaml`, `template.yaml` und das vollständige
   `lovelace`-Dashboard mit Config-Hash exportieren. Backup-Verschlüsselung und
   Wiederherstellbarkeit bestätigen.
2. **Referenzen unmittelbar vor Änderung erneut prüfen:** Entity-Suche,
   Automationen, Scripts, Szenen, Helfer, Packages, alle Dashboards und
   Registry erneut lesen. Wegen der fehlenden Registry-Antwort für die beiden
   REST-Sensoren deren Status ausdrücklich klären.
3. **YAML bereinigen:** ausschließlich `sensor.yaml` Zeile 6–24 (die beiden
   alten REST-Blöcke) und `template.yaml` Zeile 811–988 (der markierte
   Fahrradwetter-Block) entfernen. Den ADS-B-Block und alle übrigen Blöcke
   unverändert lassen.
4. **Storage-Dashboard bereinigen:** im Dashboard `lovelace`, View
   `weather`, Abschnitt 5 ausschließlich die Fahrradwetter-Titelkarte und den
   verschachtelten alten Button-Card-Stack entfernen. Vorher mit Config-Hash
   sperren; keine direkte `.storage`-Bearbeitung durchführen. Die gemeinsame
   `button-card`-Ressource bleibt registriert.
5. **Konfiguration validieren:** unterstützte HA-Konfigurationsprüfung
   ausführen und Fehler vollständig beheben, bevor ein Reload erfolgt.
6. **Gezielt reloaden:** sofern die HA-Version dies unterstützt,
   `sensor.reload` und `template.reload` ausführen. Die Storage-Lovelace-
   Änderung wird über die Dashboard-Konfiguration wirksam; kein Neustart ist
   allein für diese Kartenentfernung erforderlich. Falls HA eine vollständige
   Validierung oder Neustart verlangt, diesen erst nach Freigabe und Backup
   durchführen.
7. **Nachprüfung:** alte YAML-IDs, Dashboard-Referenzen, Zustände und
   Registry-Einträge suchen; verbleibende gemeinsame OpenWeatherMap-, MET-
   Norway-, GW1100A- und Dashboard-Funktionen prüfen; Logs auf neue Fehler
   prüfen.
8. **Erst danach:** separat freigegebene HACS-Installation und Einrichtung der
   Bike-Weather-Beta durchführen. Das ist nicht Teil dieser Phase.

## 8. Backup- und Rollback-Verfahren

### YAML

- Vorherige Dateien unverändert und mit Zeitstempel außerhalb des aktiven
  Bearbeitungsvorgangs sichern.
- Bei Fehlern die beiden Originaldateien vollständig wiederherstellen,
  Konfiguration erneut validieren und anschließend nur die nötigen
  YAML-Reloads ausführen.
- Keine systemweiten oder produktfremden Dateien überschreiben.

### Lovelace

- Vollständige Dashboard-Konfiguration und Config-Hash vor der Änderung
  speichern.
- Bei Fehlern die gespeicherte Konfiguration über die unterstützte Dashboard-
  API mit aktuellem Hash wiederherstellen. Nicht direkt in `.storage` schreiben.

### Registry

- Registry-Einträge erst nach Verbraucherprüfung und Backup beurteilen.
- Eine Entfernung aus der Registry ist nicht als sicher durch einen einfachen
  Einzelobjekt-Rollback anzusehen; für einen verwaisten oder falsch entfernten
  Eintrag kann eine HA-Sicherung bzw. eine von HA unterstützte Wiederherstellung
  erforderlich sein.

## 9. Freigabestatus

| Prüfung | Status | Ergebnis |
|---|---|---|
| Aktive Includes und YAML-Quellen | PASS | `sensor.yaml`, `template.yaml`, Packages geprüft |
| Alte REST-Sensoren inventarisiert | PASS | 2 Blöcke in `sensor.yaml` |
| Alte Template-Sensoren inventarisiert | PASS | 4 Sensoren in `template.yaml` |
| Automationen/Scripts/Szenen/Helfer | PASS | keine Verbraucher gefunden |
| Aktive YAML-/Package-Referenzen | PASS | keine externen Treffer |
| Dashboard-Lokalisation | PASS | `/lovelace/weather`, View `weather`, Abschnitt 5 |
| Lovelace-Ressourcenabgrenzung | PASS | keine dedizierte Fahrradwetter-Ressource |
| REST-Entity-Registry-Status | BLOCKED | Zustände vorhanden, Registry-Eintrag nicht zurückgegeben; vor Entfernung erneut verifizieren |
| Änderungen an VM 104 | NOT RUN | ausdrücklich nicht ausgeführt |
| Backup/Reload/Neustart | NOT RUN | ausdrücklich nicht ausgeführt |
| Bereinigung/Installation der Beta | NOT RUN | separate Freigabe erforderlich |

**Freigabeempfehlung:** Der Bereinigungsplan ist bereit zur Prüfung. Es wurde
nichts entfernt. Vor der Ausführung ist eine separate Freigabe für Backup,
gezielte YAML-/Dashboard-Änderungen und die anschließenden Reloads erforderlich.
