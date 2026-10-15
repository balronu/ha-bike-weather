# Phase 2 – Data model

Implemented in `bike_weather_core/models.py` and `normalize.py`.

## Models

- `WeatherSource`: stable source ID, kind, provider and forecast flag.
- `WeatherObservation`: current measured values and separate observed/retrieved
  timestamps.
- `ForecastSlot`: interval-based forecast values; the interval is preserved
  from the provider (one hour, three hours, or another resolution).
- `DataQuality`: good, partial, stale, unavailable or invalid.
- `RideProfile`: classic thresholds, provisional score weights and freshness.
- `RideWindow`: one-off or recurring local-time start plus duration.
- `RideAssessment`: classic status, score, quality, source IDs, reasons and
  factor evidence.

All internal timestamps must be timezone-aware and are normalized to UTC by the
normalizers. Display timezone conversion belongs to the adapter/UI boundary.

## Units and missing data

- Temperature: °C.
- Wind and gusts: km/h; m/s and mph are converted explicitly.
- Precipitation: mm; inches are converted explicitly.
- Probability: percent from 0 to 100.

`None` means absent. It is never silently converted to `0`. In particular,
rain amount, rain rate and precipitation probability remain separate fields;
they are not interchangeable.

## Provider inputs

`from_ha_weather_state()` handles a generic HA weather state, while
`from_ha_forecast()` preserves the intervals exposed by its forecast list.
`from_openweather()` handles current and `/forecast` payloads without receiving
an API key. The latter is deliberate: secrets must remain in a future adapter.

## Source selection

`choose_metric_observations()` receives a per-metric priority map. It discards
stale/unavailable observations first, then chooses the first configured source
that actually supplies that metric. Thus temperature may come from a local
station while wind comes from a HA weather entity, with both choices visible in
the resulting source IDs.

## Recorder boundary

The model is intentionally not a sensor attribute payload. A future entity
adapter should publish compact summaries and bounded diagnostic fields. Full
forecast lists must not be placed in state attributes, respecting the live
16 KiB Recorder warning documented in the Phase 1 report.
