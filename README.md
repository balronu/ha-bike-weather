![Bike Weather](assets/branding/readme-banner.png)

# Bike Weather – Fahrradwetter für Home Assistant

🇩🇪 **Deutsch** | [🇬🇧 English](README.en.md)

> **Veröffentlicht: `v0.1.0-beta.3` – nicht als Stable-Version verwenden.**
> Die nachfolgend beschriebene Beta-4-Arbeit ist noch nicht veröffentlicht.
> Installation und Praxistest über HACS erfolgen ausschließlich durch den Nutzer.

## Überblick

Bike Weather erzeugt aus einer Home-Assistant-Wetterentität, OpenWeatherMap
und/oder einer lokalen Wetterstation einen nachvollziehbaren Fahrradwetter-
Score von 0 bis 100. Temperatur, Wind und Regen werden pro Messgröße mit
Frischeprüfung priorisiert:

1. lokaler Wetterstationssensor, wenn aktiviert und gültig;
2. konfigurierter Wetteranbieter;
3. unbekannt, wenn keine belastbaren Daten vorliegen.

Fehlende oder ungültige Werte werden nie stillschweigend als 0 behandelt.

## Unveröffentlichte Beta-4-Arbeit

- native EntitySelectoren statt freier Entity-ID-Eingabe;
- eindeutige Vorauswahl kompatibler lokaler Sensoren;
- unabhängige Sensoren für Außentemperatur, Windgeschwindigkeit und Regenrate;
- Einheiten: °C/°F, km/h/m/s/mph sowie mm/h und in/h;
- Provider-Auswahl mit verständlichen deutschen und englischen Beschriftungen;
- Options Flow mit vorausgefüllten und verlustfrei gespeicherten Einstellungen;
- responsive custom:bike-weather-card mit Editor, Score, Messwerten,
  Datenquelle, Datenqualität, Fahrzeitfenster und Prognose;
- neues Logo, README-Banner, Social Preview und konsistente Dokumentation.
- reparierter Options Flow für Home Assistant 2026.10; bestehende Beta-2- und
  Beta-3-Konfigurationen mit leeren Optionswerten bleiben erhalten.

## Voraussetzungen und Installation

Home Assistant 2026.10.x oder neuer und HACS werden vorausgesetzt.

1. In HACS Benutzerdefinierte Repositories öffnen.
2. balronu/ha-bike-weather als Repository-Typ Integration hinzufügen.
3. Vorabversionen aktivieren und den veröffentlichten Release `v0.1.0-beta.3` auswählen.
4. Nach dem Download Home Assistant nach Aufforderung neu starten.
5. Einstellungen → Geräte & Dienste → Integration hinzufügen → Bike Weather.

Eine manuelle Lovelace-Ressource ist nicht erforderlich. Die Karte wird
idempotent als versionierte Ressource registriert. Unabhängige vorhandene
Lovelace-Ressourcen werden nicht verändert.

## Einrichtung

### Wetteranbieter

Der Provider kann sein:

- Home-Assistant-Wetterintegration: eine passende weather.*-Entität wird
  über EntitySelector gewählt;
- OpenWeatherMap: API-Schlüssel wird nur für diesen Provider benötigt;
- Kein zusätzlicher Wetteranbieter: nur lokale Sensoren.

Beispiele wie weather.openweathermap oder weather.forecast_home sind nicht
fest codiert.

### Lokale Wetterstation

Aktiviere Lokale Wetterstationssensoren verwenden und wähle unabhängig:

- Außentemperatur;
- Windgeschwindigkeit;
- Regenrate.

Bei einer GW1100A können beispielsweise
sensor.gw1100a_v2_2_3_outdoor_temperature,
sensor.gw1100a_v2_2_3_wind_speed und
sensor.gw1100a_v2_2_3_rain_rate verwendet werden. Diese IDs sind nur
Beispiele. Andere kompatible Wetterstationen werden über Geräteeigenschaften
und Einheiten unterstützt. Bei mehreren Kandidaten bleibt die Auswahl leer,
damit keine falsche Entität automatisch gewählt wird.

### Optionen nachträglich ändern

Der Options Flow erhält bestehende Werte und erlaubt Provider, Entitäten,
Datenalter, Aktualisierung, Score-Grenze, Fahrzeitfenster und Fahrtdauer zu
ändern. Nicht bearbeitete Beta-2-Einstellungen bleiben erhalten.

## Lovelace-Karte

~~~yaml
type: custom:bike-weather-card
entry_id: DEINE_CONFIG_ENTRY_ID
show_forecast: true
show_details: true
ride_start: "07:30"
ride_duration_minutes: 60
~~~

Die Karte zeigt Score, Bewertung, Temperatur, Wind, Regenrate, Prognose,
Fahrzeitfenster, Fahrtdauer, Datenquelle und Datenqualität. Fehlende oder
veraltete Daten werden ausdrücklich angezeigt. Der visuelle Karteneditor
kann entry_id, Prognose/Details, Startzeit und Fahrtdauer ändern.

## Bewertung

Der Score ist ein konservativer gewichteter Wert zwischen 0 und 100. Er
berücksichtigt Temperatur, Wind, Böen, Regen, Regenwahrscheinlichkeit und
gefühlte Temperatur. Fehlende Faktoren reduzieren die Datenqualität; ein
unvollständiger Datensatz wird nicht als uneingeschränkt gute Fahrt
ausgegeben. Die tatsächlichen Standardwerte stehen im gebündelten Core und
werden durch Tests abgesichert.

## Datenschutz und Einschränkungen

Lokale Sensoren und Home-Assistant-Wetterdaten bleiben lokal. OpenWeatherMap
wird nur bei ausdrücklicher Auswahl und mit eigenem API-Schlüssel kontaktiert.
Beta 3 ist nicht als Stable freigegeben; Beta 4 ist noch nicht veröffentlicht.
Produktive HA-Installation,
HACS-Update und Praxistest sind nicht Bestandteil dieses Branches.

## Entwicklung und Tests

~~~bash
PYTHONPATH=. python3 -m pytest -q
python3 -m unittest discover -s tests -p 'test_*.py'
ruff check .
mypy bike_weather_core
python3 -m compileall -q bike_weather_core custom_components/bike_weather tests
node --check custom_components/bike_weather/www/bike-weather-card.js
~~~

Hassfest, HACS-Validierung und Gitleaks laufen zusätzlich über GitHub Actions.
Echte Screenshots aus einer produktiven Home-Assistant-Installation sind in
diesem Branch nicht enthalten; die Browser-/HA-Laufzeitprüfung bleibt offen.

## Dateien und Branding

- [Englische README](README.en.md)
- [Konfiguration](docs/CONFIGURATION.md)
- [Karte](docs/CARD.md)
- [Installation](docs/INSTALLATION.md)
- [Branding-Hinweise](BRANDING.md)
- [Entwurf der Beta-4-Release Notes](docs/releases/v0.1.0-beta.4.md)

## Lizenz

MIT, siehe [LICENSE](LICENSE).
