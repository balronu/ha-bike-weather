![Bike Weather](assets/branding/readme-banner.png)

# Bike Weather – Fahrradwetter für Home Assistant

**Deutsch** | [English](README.en.md)

[![Stable](https://img.shields.io/github/v/release/balronu/ha-bike-weather?sort=semver&label=Stable)](https://github.com/balronu/ha-bike-weather/releases/latest)
[![CI](https://github.com/balronu/ha-bike-weather/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/balronu/ha-bike-weather/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://www.hacs.xyz/)
[![License](https://img.shields.io/github/license/balronu/ha-bike-weather)](LICENSE)

Der aktuelle Stable-Stand ist v0.3.1. Dieser Hotfix entfernt die alte
allgemeine Forecast-Darstellung vollständig aus der Karte.

Bike Weather bewertet anhand lokaler Wetterdaten und verfügbarer Prognosen,
wie gut sich das Wetter zum Fahrradfahren eignet. Die Bewertung von 0 bis 100
bleibt nachvollziehbar: fehlende oder veraltete Werte werden als unbekannt
beziehungsweise eingeschränkt dargestellt und nicht stillschweigend als gut
behandelt.

## Funktionen

- aktuelles Fahrradwetter mit Score, Status, Begründungen und Datenqualität;
- Home-Assistant-Wetterprognosen sowie optionale lokale Wetterstation;
- unabhängige Sensoren für Temperatur, Wind und Regenrate;
- regelmäßige Hinfahrt und Rückfahrt mit individuellen Wochentagen, Uhrzeiten
  und Fahrtdauern;
- konservative Morgenprognose für 06:00–22:00;
- spontane Fahrradtour mit frei wählbarer Abfahrtszeit und 15–120 Minuten;
- gemeinsame Python-Scorelogik für aktuelle Werte und Forecast-Zeitfenster;
- transparente Trennung zwischen Forecast-Lücken und fehlenden Einzelwerten;
- responsive Lovelace-Karte mit Editor und automatischer Integrationserkennung;
- deutsche und englische Oberfläche.

## Voraussetzungen

- Home Assistant 2026.10.x oder neuer;
- HACS für die bevorzugte Installation;
- mindestens eine weather.*-Entität für Forecast-Daten;
- optional kompatible Sensoren für Außentemperatur, Windgeschwindigkeit und
  Regenrate;
- OpenWeatherMap ist optional und benötigt nur bei Auswahl dieses Providers
  einen eigenen API-Schlüssel.

Echte produktive Browser-/HA-E2E-Tests und Screenshots sind nicht Bestandteil
dieses Releases. Die automatisierten HA-Fixture-, Hassfest- und HACS-Prüfungen
sind dokumentiert und laufen in GitHub Actions.

## Installation über HACS

1. HACS → **Benutzerdefinierte Repositories** öffnen.
2. balronu/ha-bike-weather als Repository-Typ **Integration** hinzufügen.
3. Den veröffentlichten Stable-Release v0.3.1 auswählen.
4. Home Assistant nach Aufforderung neu starten.
5. Unter **Einstellungen → Geräte & Dienste** die Integration **Bike Weather**
   hinzufügen.

Die Stable-Version ist der reguläre Installationsweg; Vorabversionen werden
nicht benötigt. Eine manuelle Lovelace-Ressource ist nicht erforderlich.

## Einrichtung

Im Config Flow wird eine Wetterdatenquelle ausgewählt. Danach können optional
lokale Sensoren, Datenalter, Aktualisierungsintervall, Score-Grenze und die
Fahrzeitoptionen konfiguriert werden. Der Options Flow übernimmt vorhandene
Werte, sodass bestehende Konfigurationen erhalten bleiben.

Die lokalen Sensoren werden unabhängig für Temperatur, Windgeschwindigkeit und
Regenrate gewählt. Bei mehreren möglichen Kandidaten erfolgt keine riskante
automatische Auswahl. Die Sensor-IDs sind installationsabhängig.

## Regelmäßige Fahrten und Morgenprognose

Hinfahrt und Rückfahrt sind unabhängig konfigurierbar. Für jede Fahrt können
Wochentage, Uhrzeit und Dauer gesetzt werden, zum Beispiel Hinfahrt Montag bis
Freitag um 07:30 für 30 Minuten und Rückfahrt Montag, Dienstag, Donnerstag und
Freitag um 13:30 für 30 Minuten.

Die Morgenprognose betrachtet 06:00–22:00. Hohe Regenwahrscheinlichkeit,
fehlende Niederschlagsmengen oder unvollständige Forecast-Abdeckung führen
konservativ zu eingeschränkter beziehungsweise unbekannter Eignung. Positive
Zeitfenster werden bei unvollständiger Abdeckung nicht vorgetäuscht.

## Spontane Fahrradtour

Die Karte bewertet alle berührten stündlichen Forecast-Intervalle einer frei
gewählten Abfahrt und Dauer. Zeitlücken werden von vorhandenen Intervallen mit
fehlenden Einzelwerten unterschieden. Bei vollständiger zeitlicher Abdeckung,
aber fehlenden Bewertungsfaktoren, zeigt die Karte die eingeschränkte Qualität
und den fehlenden Faktor. Das Frontend berechnet keinen eigenen Score.

## Lovelace-Karte

    type: custom:bike-weather-card
    show_forecast: true
    show_details: true
    ride_start: "15:00"
    ride_duration_minutes: 60

Die Integration registriert die versionierte Karte idempotent. Vorhandene
unabhängige Lovelace-Ressourcen werden nicht verändert.

## Bewertung und Datenqualität

Der Score berücksichtigt Temperatur, Wind, Böen, Regen,
Regenwahrscheinlichkeit und gefühlte Temperatur. Die Bewertung ist ein
gewichteter Wert von 0 bis 100. Fehlende oder veraltete Faktoren senken die
Datenqualität; ein unvollständiger Datensatz wird nicht als uneingeschränkt
geeignete Fahrt ausgegeben.

## Fehlerbehebung und Updates

- Prüfe, ob die gewählte weather.*-Entität Forecast-Daten liefert.
- Prüfe im Options Flow die ausgewählten Entitäten und deren Einheiten.
- Nach einem HACS-Update Home Assistant neu starten, wenn HACS dies meldet.
- Bei einer alten Kartenressource Browser-Cache und Lovelace-Ressourcen prüfen;
  die aktuelle Version wird normalerweise automatisch registriert.
- Für reproduzierbare Fehler bitte Logs, Home-Assistant-Version und die
  Datenqualitätsbegründung ohne API-Schlüssel oder private Daten melden.

## Entwicklung und Tests

    PYTHONPATH=. python3 -m pytest -q
    python3 -m unittest discover -s tests -p 'test_*.py'
    ruff check .
    mypy bike_weather_core
    python3 -m compileall -q bike_weather_core custom_components/bike_weather tests
    node --check custom_components/bike_weather/www/bike-weather-card.js

GitHub Actions führen zusätzlich Frontend-, HA-Fixture-, Hassfest-, HACS- und
Gitleaks-Prüfungen aus.

## Dokumentation

- [Konfiguration](docs/CONFIGURATION.md)
- [Karte](docs/CARD.md)
- [Installation](docs/INSTALLATION.md)
- [Wetterquellen](docs/WEATHER_SOURCES.md)
- [Stable-Release Notes](docs/releases/v0.3.1.md)

## Mitwirkung und Lizenz

Fehlerberichte und Verbesserungen sind als GitHub Issue oder Pull Request
willkommen. Bitte keine Zugangsdaten, privaten Entity-Attribute oder privaten
Standortdaten veröffentlichen. Das Projekt steht unter der [MIT-Lizenz](LICENSE).
