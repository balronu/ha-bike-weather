# Bike Weather – Phase 2 offline prototype

This repository is a local development candidate for the planned Home
Assistant custom integration **Bike Weather** (`bike_weather`). It currently
contains a provider-neutral offline core and a legacy comparison adapter under
`custom_components/fahrradwetter/`.

## Phase 2 status

Implemented locally:

- normalized observations and forecast slots for HA weather entities and
  OpenWeatherMap payloads;
- independent per-metric source prioritization with freshness checks;
- strict classic `good`/`bad`/`unknown` assessment;
- provisional explainable 0–100 score with conservative missing-data handling;
- one-off and recurring ride windows, multi-interval aggregation and
  gap-safe alternative starts;
- offline unittest coverage without credentials or personal coordinates.

The production VM 104 remains untouched. There is no installation, release,
GitHub repository, push or HACS publication from this phase.

## Layout

```text
bike_weather_core/                 HA-independent domain core
custom_components/fahrradwetter/   legacy local candidate for comparison only
tests/test_core.py                  offline tests
docs/PHASE2-*.md                    architecture, model, score and migration docs
```

The future HA adapter will use domain `bike_weather`; it is intentionally not
installed or wired in this phase. The legacy candidate remains under its old
path so its behavior and migration risks stay visible and reviewable.

## Test

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

## Documentation

- [Phase 2 architecture](docs/PHASE2-ARCHITECTURE.md)
- [Phase 2 data model](docs/PHASE2-DATA-MODEL.md)
- [Phase 2 score model](docs/PHASE2-SCORE-MODEL.md)
- [Phase 2 migration](docs/PHASE2-MIGRATION.md)
- [Phase 2 report](docs/PHASE2-REPORT.md)
- [Live inventory](../docs/FAHRRADWETTER_BESTANDSAUFNAHME_2026-10-15.md)

Score weights and partial-data policy are provisional and require explicit
approval before production wiring.
