# Phase 2 – Architecture

## Status

Local offline prototype only. The productive Home Assistant VM, its YAML, its
entities and its dashboard are out of scope and were not changed.

## Boundaries

```text
HA adapter (future Phase 3)
  Config Entry / Options Flow / Coordinator / entities / diagnostics
                              |
                    bike_weather_core
       models -> normalization -> source selection
                              |
             classic assessment + provisional score
                              |
                    ride-window evaluation
```

`bike_weather_core/` has no Home Assistant, aiohttp, network, Recorder or
filesystem dependency. A future adapter owns authentication, entity lookup and
polling. Provider modules translate data into the core models; scoring never
reads entity IDs or raw provider payloads.

## Source strategy

Each metric is selected independently. The future default order is:

1. explicitly selected local sensor observation;
2. configured HA `weather.*` entity;
3. explicitly configured direct provider;
4. explicitly configured fallback source.

The core requires a source ID, measurement/retrieval timestamps, unit-normalized
values and a quality state. Freshness is checked before priority. Missing rain
does not become zero, and missing wind does not become calm.

Direct API providers are opt-in. Their credentials and URLs belong to the
future adapter/config entry and never enter the core or tests.

## Future Home Assistant adapter

The existing local `custom_components/fahrradwetter/` code is retained as a
legacy candidate for comparison. It is not the Phase 2 architecture: it is
OpenWeatherMap-only, uses the old domain, requires a direct key, has no local
source selection and exposes a large forecast attribute. The future integration
will use domain `bike_weather`, stable Config Entry IDs and a coordinator whose
payload is bounded and diagnostics-safe.

Planned Config Flow fields: name, location source, latitude/longitude, HA
weather entity, direct provider and secret, local metric entities, profile.
Planned Options Flow fields: per-metric priorities, freshness, thresholds,
weights, ride windows and polling. No flow is installed in VM 104 in this
phase.

## Error policy

Provider errors are represented as unavailable/invalid quality, not as zeros.
An assessment is `unknown` when mandatory classic inputs are absent. Partial
score data receives a confidence reduction. Last-known-good is not part of the
core and, if added later, must have an explicit age limit and stale diagnostic.
