# Bike Weather – Phase 7B Abschlussprüfung

**Prüfdatum:** 2026-10-15  
**Repository:** https://github.com/balronu/ha-bike-weather  
**Pull Request:** https://github.com/balronu/ha-bike-weather/pull/1  
**Branch:** `feature/v0.1.0-beta.3-ui-branding`  
**Zielversion:** `v0.1.0-beta.3`

## Gesamturteil

**PARTIAL – PR bereit für menschliche Review, Merge-Empfehlung: JA, aber
nicht automatisch mergen.**

Die statischen Verträge, lokalen Qualitätsgates und alle Remote-PR-Gates
sind für den final geprüften HEAD erfolgreich. Zwei konkrete Fehler wurden
im bestehenden PR-Branch behoben: der Options Flow validiert nun dieselben
Provider-Voraussetzungen wie der Config Flow, und die Lovelace-Karte
übersetzt Status-, Qualitäts-, Quellen- und Fehlerwerte. Eine echte
Home-Assistant-Laufzeitprüfung mit Config-/Options-Flow, Browser-Konsole und
Desktop-/Smartphone-Rendering war in dieser isolierten Umgebung nicht
möglich. Die Aktivierung einer GitHub-Social-Preview konnte über die
Repository-API nicht verifiziert werden und wird daher nicht behauptet.

## Ergebnis je Prüfbereich

| Bereich | Ergebnis | Beleg / Einschränkung |
|---|---|---|
| Config Flow / Options Flow | **PARTIAL** | Native EntitySelectoren für `weather` und lokale `sensor`-Entitäten vorhanden; eindeutige Vorschläge; Provider- und API-Key-Validierung im Config- und Options Flow. HA-Laufzeitimport fehlt lokal, daher keine echte UI-Ausführung. |
| Beta-2-Migration | **PASS (statisch)** | Config-Flow-Version bleibt `1`; Beta-2-Schlüssel und Datentypen sind kompatibel, es ist keine Migration erforderlich. Bestehende Werte werden im Options Flow aus `data` und `options` zusammengeführt. Live-Restore nicht ausgeführt. |
| Deutsch / Englisch | **PASS (statisch)** | `strings.json`, `translations/de.json` und `translations/en.json` haben gleiche Feldschlüssel. Provider-Labels, Flow-Texte, Sensorbezeichnungen und Karten-Texte sind lokalisiert. Technische Kartenwerte werden in der finalen Karte übersetzt. |
| Lovelace-Karte | **PARTIAL** | Versionierte Ressource, idempotente Registrierung, Editor, WebSocket-Datenabruf, Missing/Stale-Darstellung und responsive CSS statisch geprüft; JavaScript-Syntax grün. Browser-Konsole, echte HA-Ressourcenregistrierung sowie Desktop-/Smartphone-Rendering nicht ausgeführt. |
| Branding | **PARTIAL** | Logo, Banner und Social Preview vorhanden; Pfade in README-Dateien geprüft. Abmessungen und Größen unten. Repository-Beschreibung und Topics gesetzt. Social-Preview-Status ist über die API nicht verifizierbar (404), daher keine Aktivierungsbehauptung. |
| Dokumentation | **PASS** | `README.md`, `README.en.md`, kompatibles `README.de.md`, Installations-, Konfigurations-, Quellen- und Karten-Dokumentation sowie Beta-3-Release-Notes geprüft; HACS, lokale Wetterstation, Provider/Fallback, Score, Zeitfenster und YAML-Beispiel enthalten. Beta-2-Verweise beschreiben ausschließlich Kompatibilität/Migration. |
| Tests / CI | **PASS** | Lokale und Remote-Gates siehe unten; alle Checks für den finalen HEAD erfolgreich. |

## Gefundene und behobene Fehler

### 1. Options Flow ließ ungültige Provider-Auswahl zu – behoben

Der Options Flow speicherte zuvor `OpenWeatherMap` ohne API-Schlüssel sowie
`Kein zusätzlicher Wetteranbieter` ohne aktivierte lokale Sensoren. Beide
Fälle werden jetzt mit denselben Fehlern wie im Config Flow zurückgewiesen:
`api_key_required` und `no_source`.

### 2. Lovelace-Karte zeigte technische Schlüssel – behoben

Die Karte zeigte zuvor Werte wie `good`, `partial`, `local`,
`provider_error` und rohe WebSocket-Fehlertexte direkt an. Die finale Karte
übersetzt nun Status, Datenqualität, Quellen und bekannte Datenfehler in
Deutsch/Englisch und verwendet für Transportfehler eine lokalisierte
Meldung.

## Config-/Options-Flow-Prüfung

- `EntitySelector(domain="weather")` für HA-Wetterentitäten.
- `EntitySelector(domain="sensor", device_class="temperature")` für
  Temperatur.
- `EntitySelector(domain="sensor", device_class="wind_speed")` für Wind.
- `EntitySelector(domain="sensor")` für Regen; Device Class und Einheiten
  werden bei automatischen Vorschlägen berücksichtigt.
- Automatische Vorauswahl erfolgt nur bei genau einem Kandidaten; bei null
  oder mehreren Kandidaten bleibt sie leer.
- Providerwerte sind technische Speicherwerte, sichtbare Labels werden für
  Deutsch/Englisch lokalisiert.
- Andere Wetterstationen sind nicht über IDs beschränkt; Auswahl erfolgt
  über native HA-EntitySelectoren.
- Bestehende Beta-2-Werte werden beim Options-Formular aus Entry-Daten und
  Optionen wiederhergestellt.
- Eine echte HA-Formularausführung war lokal wegen fehlendem
  `homeassistant`-Pythonpaket nicht möglich; Hassfest und die statischen
  Contracts liefen erfolgreich.

## Branding-Ergebnisse

| Datei | Abmessungen | Format / Größe |
|---|---:|---:|
| `custom_components/bike_weather/brand/icon.png` | 512 × 512 | RGBA PNG, ca. 224 KiB |
| `assets/branding/readme-banner.png` | 1280 × 320 | RGB PNG, ca. 520 KiB |
| `assets/branding/social-preview.png` | 1280 × 640 | RGB PNG, ca. 1.1 MiB |

Die Pfade werden in `README.md` und `README.en.md` relativ korrekt
verwendet. Repository-Beschreibung ist `Home Assistant Bike Weather
integration and Lovelace card`; Topics sind `bike-weather`, `hacs`,
`home-assistant` und `home-assistant-integration`. Der Social-Preview-
Endpoint des GitHub-Repositories antwortete mit HTTP 404; ob ein Preview in
den Repository-Einstellungen hinterlegt ist, bleibt deshalb **nicht
verifiziert**. Die lokalen Brand-Dateien sind keine offizielle Home
Assistant Brands-Freigabe; eine solche Freigabe wird nicht behauptet.

## Tatsächlich ausgeführte lokale Prüfungen

- `PYTHONPATH=. .venv-phase4/bin/pytest -q` → **27 passed**
- `python3 -m unittest discover -s tests -p 'test_*.py'` → **19 passed**
- Ruff → **PASS**
- mypy für `bike_weather_core` → **PASS**
- Compileall für Core, Integration und Tests → **PASS**
- JSON-Parsing aller relevanten JSON-Dateien → **PASS**
- `node --check custom_components/bike_weather/www/bike-weather-card.js` → **PASS**
- Markdown-Links auf lokale Ziele → **PASS**
- zusätzliche statische Flow-/Karten-Contracts → **PASS**

Nicht lokal ausführbar:

- echte HA-Config-/Options-Flow-Laufzeitprüfung;
- echte Browser-Konsole sowie Smartphone-/Desktop-Screenshotprüfung;
- produktive HACS-/HA-Installation.

## Remote-CI für den finalen HEAD

Finaler geprüfter HEAD: `8b5ed1e746d6177344383f1f87cd36920800ebba`.

- GitHub Actions **CI / Python** → **PASS**
- **Gitleaks** → **PASS**
- **HACS** → **PASS**
- **Hassfest** → **PASS**
- doppelt ausgelöste PR-Checks für denselben HEAD → ebenfalls **PASS**

Die GitHub-Warnungen zu künftigem Node.js- und Ubuntu-Runner-Wechsel sind
keine Fehler dieses PRs.

## Git- und PR-Status

- Fix-Commit: `8b5ed1e` (`fix: validate options and localize card states`)
- Nach diesem Bericht folgt ausschließlich ein Dokumentations-Commit im
  bestehenden PR-Branch.
- PR #1: **OPEN**, **CLEAN**, **MERGEABLE**, nicht gemergt.
- Kein Tag und kein GitHub-Release für Beta 3 erstellt.

## Verbindliche Grenzen eingehalten

Es wurden keine Änderungen an VM 104, Home Assistant, HACS-Installation,
Dashboards oder produktiven Secrets vorgenommen. Es wurde kein Merge, Tag
oder Release ausgeführt.

## Merge-Empfehlung

**JA zur manuellen Freigabe und anschließendem Merge von PR #1**, sofern der
Betreiber die ausdrücklich offenen Laufzeitprüfungen akzeptiert oder sie
nach der HACS-Installation separat durchführt. **Kein automatischer Merge in
diesem Auftrag.** Nach dem Merge sollten HACS-Installation, HA-Reload und
die echte Kartenprüfung als eigener, freigegebener Lauf erfolgen.
