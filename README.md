# Bike Weather – v0.1.0-beta.2

Bike Weather (`bike_weather`) is a Home Assistant custom integration that
combines configured Home Assistant weather/sensor entities or OpenWeatherMap
data into ride-oriented sensors and a Lovelace card.

**This is a beta release.** Offline and standalone browser checks pass, but this
exact release has not received live Home Assistant runtime validation. Use it
first in a disposable or otherwise recoverable Home Assistant instance.

The production VM 104 remains untouched. This release does not remove or
automatically migrate the legacy YAML/REST bicycle-weather setup.

## Included

- normalized observations and forecast slots for HA weather entities and
  OpenWeatherMap payloads;
- independent per-metric source prioritization with freshness checks;
- explainable 0–100 ride score with conservative missing-data handling;
- Home Assistant config and options flows;
- coordinator-backed sensors and authenticated card data;
- automatic Lovelace card resource registration;
- offline tests and standalone Chromium smoke coverage without credentials or
  personal coordinates.

The HA runtime, Hassfest and HACS limitations are recorded in
[docs/PHASE4D-REPORT.md](docs/PHASE4D-REPORT.md).

## Layout

```text
bike_weather_core/                 HA-independent domain core
custom_components/bike_weather/    installable Bike Weather integration
custom_components/fahrradwetter/   legacy local comparison candidate
tests/                              offline tests
docs/                               architecture, installation and release notes
```

The installable integration is `custom_components/bike_weather/`. The legacy
candidate remains under its old path so migration risks stay visible and
reviewable; it is not part of the migration procedure.

## Installation

Install the `v0.1.0-beta.2` pre-release through HACS as a custom repository
(`balronu/ha-bike-weather`, category **Integration**, pre-releases enabled).
Restart Home Assistant, add **Bike Weather** through the integration UI, and
then add the `bike-weather-card` Lovelace card with the resulting `entry_id`.

The integration registers its card resource automatically; do not remove
existing unrelated Lovelace resources. See
[docs/INSTALLATION.md](docs/INSTALLATION.md).

## Test

```bash
PYTHONPATH=. python -m pytest -q
```

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Card](docs/CARD.md)
- [Configuration](docs/CONFIGURATION.md)
- [Weather sources](docs/WEATHER_SOURCES.md)
- [Phase 4D validation report](docs/PHASE4D-REPORT.md)
- [Beta release notes](docs/releases/v0.1.0-beta.2.md)
