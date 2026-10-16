![Bike Weather](assets/branding/readme-banner.png)

# Bike Weather for Home Assistant

[🇩🇪 Deutsch](README.md) | 🇬🇧 **English**

> **Current development target: `v0.3.0-beta.1`.** Phase 11A adds independent regular rides and a conservative tomorrow forecast while preserving the spontaneous ride. HACS
> installation and practical testing are performed only by the user.

## Overview

Bike Weather combines a Home Assistant weather entity, OpenWeatherMap and/or
local weather-station sensors into an explainable cycling score from 0 to 100.
Temperature, wind and rain are selected independently with freshness checks:

1. a configured local weather-station sensor when enabled and valid;
2. the configured weather provider;
3. unknown when no trustworthy value is available.

Missing and invalid values are never silently treated as zero.

## Phase 10A/10C: Spontaneous bike ride

The card now includes a **Spontaneous bike ride** section. Departure is a
date/time in Home Assistant's timezone and duration is selectable as 15, 30,
45, 60, 90 or 120 minutes. The backend evaluates every touched hourly
forecast interval with the shared Python score logic; gaps produce unknown or
limited quality and the frontend never calculates a second score. Inputs are
debounced and restored per card/integration from browser `localStorage` when
available. Existing card configurations remain compatible.

When the forecast window is fully covered but individual scoring factors are
missing, the card shows the partial score with limited data quality and an
unknown suitability status, together with the missing factor. This is kept
distinct from a temporal forecast gap or completely missing forecast data;
hourly forecasts are never interpolated into false minute precision.

## Features in the current beta `v0.3.0-beta.1`

- independent regular outbound and return rides with weekdays, times and duration;
- a conservative tomorrow forecast for 06:00–22:00;
- shared score logic for regular, tomorrow and spontaneous rides;
- clear states for rides that are not planned today or have already passed.

The following features from the Beta 7 line remain included:

- native EntitySelectors instead of free-form entity IDs;
- automatic selection only when exactly one compatible sensor is found;
- independent outdoor-temperature, wind-speed and rain-rate sensors;
- °C/°F, km/h/m/s/mph and mm/h/in/h normalization;
- understandable German and English provider labels;
- prefilled Options Flow preserving existing values;
- responsive custom:bike-weather-card with editor, score, metrics, source,
  quality, ride window and forecast;
- new logo, README banner, social preview and synchronized documentation.
- fully hardened Options Flow compatibility with Home Assistant 2026.10;
  existing Beta 2 through Beta 4 entries with empty options remain supported.
- static Lovelace card routing through the current HA 2026.10 API with a legacy
  fallback; the versioned resource remains automatically and idempotently registered.

## Requirements and installation

Home Assistant 2026.10.x or newer and HACS are required.

1. Open Custom repositories in HACS.
2. Add balronu/ha-bike-weather as an Integration repository.
3. Enable beta versions and select the desired published release.
4. Restart Home Assistant when requested after download.
5. Add Bike Weather under Settings → Devices & services.

No manual Lovelace resource is required. The integration registers its
versioned card resource idempotently and does not touch unrelated resources.

## Setup

Choose Home Assistant weather integration, OpenWeatherMap, or no additional
provider. A weather entity is selected through EntitySelector; examples such
as weather.openweathermap are not hard-coded. An API key is requested only
for OpenWeatherMap.

Enable local weather-station sensors to select outdoor temperature, wind speed
and rain rate independently. A GW1100A may expose sensor IDs such as
sensor.gw1100a_v2_2_3_outdoor_temperature,
sensor.gw1100a_v2_2_3_wind_speed and sensor.gw1100a_v2_2_3_rain_rate.
These are examples only. If several candidates exist, no automatic choice is
made.

The Options Flow keeps existing provider, entity, freshness, refresh, score,
ride-window and duration values when opened and saved.

## Lovelace card

~~~yaml
type: custom:bike-weather-card
show_forecast: true
show_details: true
ride_start: "15:00"
ride_duration_minutes: 60
~~~

The card shows the score, assessment, temperature, wind, rain rate, forecast,
ride window, duration, source and data quality. The spontaneous ride also
shows departure, arrival, score, assessment, temperature, wind, gusts, rain,
rain probability, coverage and data-derived reasons. Missing or stale data is
explicitly visible. The integration is detected automatically; the visual
editor changes entry_id, forecast/details, start time and duration.

## Score and limitations

The conservative weighted score uses temperature, wind, gusts, rain,
precipitation probability and apparent temperature. Missing factors lower
data quality and cannot produce an unrestricted positive result. Local and
Home Assistant weather data stay local; OpenWeatherMap is contacted only
when explicitly selected. `v0.3.0-beta.1` is not a stable release and has no
productive HA runtime validation or real production screenshots.

## Development and tests

~~~bash
PYTHONPATH=. python3 -m pytest -q
python3 -m unittest discover -s tests -p 'test_*.py'
ruff check .
mypy bike_weather_core
python3 -m compileall -q bike_weather_core custom_components/bike_weather tests
node --check custom_components/bike_weather/www/bike-weather-card.js
~~~

Hassfest, HACS validation and Gitleaks run through GitHub Actions.

## Links

- [German documentation](README.md)
- [Configuration](docs/CONFIGURATION.md)
- [Card](docs/CARD.md)
- [Installation](docs/INSTALLATION.md)
- [Branding](BRANDING.md)
- [Beta 7 release notes](docs/releases/v0.1.0-beta.7.md)
- [Phase 10A implementation report](docs/PHASE10A-SPONTANEOUS-RIDE.md)

## License

MIT, see [LICENSE](LICENSE).
