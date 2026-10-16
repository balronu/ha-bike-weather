![Bike Weather](assets/branding/readme-banner.png)

# Bike Weather for Home Assistant

[Deutsch](README.md) | **English**

[![Stable](https://img.shields.io/github/v/release/balronu/ha-bike-weather?sort=semver&label=Stable)](https://github.com/balronu/ha-bike-weather/releases/latest)
[![CI](https://github.com/balronu/ha-bike-weather/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/balronu/ha-bike-weather/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://www.hacs.xyz/)
[![License](https://img.shields.io/github/license/balronu/ha-bike-weather)](LICENSE)

Bike Weather evaluates how suitable the weather is for cycling using local
weather data and available forecasts. Scores from 0 to 100 remain explainable:
missing or stale values are shown as unknown or limited quality instead of
being silently treated as good.

## Features

- current cycling weather with score, status, reasons and data quality;
- Home Assistant weather forecasts and optional local weather-station sensors;
- independent temperature, wind-speed and rain-rate sensors;
- independent regular outbound and return rides with weekdays, times and
  durations;
- conservative tomorrow forecast for 06:00–22:00;
- spontaneous bike ride with a selectable departure and 15–120 minute duration;
- shared Python scoring for current values and forecast windows;
- transparent distinction between forecast gaps and missing individual values;
- responsive Lovelace card with editor and automatic integration discovery;
- German and English user interface.

## Requirements

- Home Assistant 2026.10.x or newer;
- HACS for the preferred installation path;
- at least one weather.* entity providing forecast data;
- optional compatible outdoor-temperature, wind-speed and rain-rate sensors;
- OpenWeatherMap is optional and requires an API key only when selected.

Real production browser/HA end-to-end tests and screenshots are not part of
this release. Automated HA-fixture, Hassfest and HACS checks are documented
and run in GitHub Actions.

## HACS installation

1. Open **Custom repositories** in HACS.
2. Add balronu/ha-bike-weather as an **Integration** repository.
3. Select the published Stable release v0.3.0.
4. Restart Home Assistant when requested.
5. Add **Bike Weather** under **Settings → Devices & services**.

Stable is the regular installation path; pre-releases are not required. No
manual Lovelace resource is needed.

## Setup

Select a weather data source in the Config Flow. Optional local sensors, data
age, refresh interval, score threshold and ride settings can then be chosen.
The Options Flow preserves existing values when settings are changed.

Temperature, wind speed and rain rate sensors are selected independently. When
multiple candidates exist, the integration does not make a risky automatic
choice. Sensor IDs depend on the installation.

## Regular rides and tomorrow forecast

Outbound and return rides are configured independently. Each ride supports
weekdays, time and duration, for example an outbound ride Monday–Friday at
07:30 for 30 minutes and a return ride Monday, Tuesday, Thursday and Friday at
13:30 for 30 minutes.

The tomorrow forecast covers 06:00–22:00. High precipitation probability,
missing precipitation amounts or incomplete forecast coverage conservatively
produce limited or unknown suitability. Positive windows are not presented
when forecast coverage is incomplete.

## Spontaneous bike ride

The card evaluates every hourly forecast interval touched by the selected
departure and duration. Temporal gaps are distinguished from present
intervals with missing individual values. With complete time coverage but
missing scoring factors, the card shows limited quality and the missing factor.
The frontend does not calculate a separate score.

## Lovelace card

    type: custom:bike-weather-card
    show_forecast: true
    show_details: true
    ride_start: "15:00"
    ride_duration_minutes: 60

The integration registers the versioned card idempotently and does not modify
unrelated existing Lovelace resources.

## Scoring and data quality

The score considers temperature, wind, gusts, rain, precipitation probability
and apparent temperature. It is a weighted value from 0 to 100. Missing or
stale factors lower data quality; incomplete data cannot produce an
unrestricted positive ride assessment.

## Troubleshooting and updates

- Check that the selected weather.* entity provides forecast data.
- Check selected entities and units in the Options Flow.
- Restart Home Assistant after a HACS update when HACS requests it.
- If an old card resource remains, check the browser cache and Lovelace
  resources; the current version is normally registered automatically.
- For reproducible issues, include logs, the Home Assistant version and the
  data-quality reason without API keys or private data.

## Development and tests

    PYTHONPATH=. python3 -m pytest -q
    python3 -m unittest discover -s tests -p 'test_*.py'
    ruff check .
    mypy bike_weather_core
    python3 -m compileall -q bike_weather_core custom_components/bike_weather tests
    node --check custom_components/bike_weather/www/bike-weather-card.js

GitHub Actions additionally run frontend, HA-fixture, Hassfest, HACS and
Gitleaks checks.

## Documentation

- [German documentation](README.md)
- [Configuration](docs/CONFIGURATION.md)
- [Card](docs/CARD.md)
- [Installation](docs/INSTALLATION.md)
- [Weather sources](docs/WEATHER_SOURCES.md)
- [Stable release notes](docs/releases/v0.3.0.md)

## Contributing and license

Bug reports and improvements are welcome through GitHub issues or pull
requests. Do not publish credentials, private entity attributes or private
location data. The project is released under the [MIT license](LICENSE).
