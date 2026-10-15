# Phase 2 – Migration strategy

## Existing candidate findings

The initial `custom_components/fahrradwetter/` candidate is useful as a
comparison but is not copied unchanged:

- It is tied to OpenWeatherMap direct forecast requests and an API key.
- It uses domain `fahrradwetter`, while the planned public integration domain is
  `bike_weather`.
- Its `_as_float(..., 0)` behavior turns absent rain, wind and other values into
  zeros, which can improve a score incorrectly.
- It scores only 3-hour OWM slots and has fixed today/tomorrow selection rather
  than arbitrary ride windows.
- It publishes serialized forecast data as sensor attributes, risking the live
  Recorder size limit.
- It derives dates with UTC timestamps and local `datetime.now()`, which needs
  explicit timezone tests around DST.
- It contains no local-sensor or generic HA-weather source selection.
- No offline test suite existed at the start of this phase.

Reusable concepts are the coordinator/entity separation, translation layout,
stable per-entry sensor keys and direct OWM field mapping. They are not yet
connected to the new core.

## Safe migration sequence

1. Keep the YAML/REST/template chain unchanged.
2. Build and test the `bike_weather_core` model offline.
3. Implement a separate `bike_weather` Config Entry adapter in a later gated
   phase; do not reuse productive entity IDs automatically.
4. Run the new adapter in an isolated test HA or fixture with synthetic data.
5. Compare local-vs-provider metric selection, units, freshness and window
   results against the reference chain.
6. Install in VM 104 only after explicit authorization and a separately
   verified rollback plan.
7. Migrate dashboard references only after a parallel observation period.
8. Remove legacy YAML only in a later, explicit migration phase.

The new domain should initially use new entity IDs and preserve the old IDs as
the rollback path. Historical tags and the existing local candidate are not
rewritten by this phase.

## Compatibility risks

The most important compatibility questions are wind/rain units from the local
station, source freshness semantics, DST behavior, and how an existing HA
weather entity exposes forecast intervals. These require adapter-level tests;
they are not inferred from labels.
