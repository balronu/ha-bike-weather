# Phase 7 – Bike Weather Beta 3

## Status

**PARTIAL / ready for review.** The Beta-3 implementation is complete on
branch feature/v0.1.0-beta.3-ui-branding. It is not merged, tagged or
released. Productive VM 104, HACS, dashboards, YAML, secrets and Home
Assistant runtime were not changed.

## Changes

- Config Flow now uses native EntitySelector for weather entities and local
  temperature, wind-speed and rain-rate sensors.
- Suggestions are derived from device class and units; automatic selection is
  made only for exactly one candidate. GW1100A IDs are not hard-coded.
- Local values normalize °C/°F, km/h/m/s/mph and mm/h/in/h. Unknown,
  unavailable and invalid values remain missing.
- Provider labels are localized by HA language; OpenWeatherMap API key
  validation is provider-specific.
- Options Flow keeps existing Beta-2 values and exposes provider, entities,
  freshness, refresh, score and ride-window settings.
- Lovelace card is versioned 0.1.0-beta.3, idempotently registered, localized,
  responsive, editor-capable and explicit about stale/missing data.
- README.md is the complete German documentation; README.de.md is the
  compatibility entry point; README.en.md is a complete English counterpart.
- Added generated repository branding and documented that it is not official
  Home Assistant Brands artwork.
- Added Beta-3 release notes and Validate workflow for Hassfest/HACS.

## Changed files

Main areas: custom_components/bike_weather/, bike_weather_core/, tests/,
README.md, README.de.md, README.en.md, BRANDING.md, assets/branding/, docs/,
and .github/workflows/validate.yml.

## Config-/Options-Flow results

- Static selector contract: PASS.
- Translation key parity (German/English): PASS.
- Provider values remain technical storage keys, while visible labels are
  localized.
- HA-native Config Flow execution: not available in this local environment;
  must be confirmed by GitHub Hassfest and a user-run HA test.

## Translations

German and English have matching config, options and entity keys. The card
uses the active HA language for its own labels.

## Lovelace results

- JavaScript syntax: PASS.
- Idempotent custom-card/editor registration: PASS by contract.
- Responsive CSS and no horizontal overflow by layout inspection: PASS.
- Browser console, desktop/mobile rendering and live WebSocket: NOT RUN.

## Branding

- custom_components/bike_weather/brand/icon.png: 512 × 512 RGBA.
- assets/branding/readme-banner.png: 1280 × 320 PNG.
- assets/branding/social-preview.png: 1280 × 640 PNG.
- Source backgrounds are retained under assets/branding/.

## Local quality gates

- pytest: 26 passed (PYTHONPATH=. .venv-phase4/bin/pytest -q).
- unittest: 19 passed.
- Ruff: PASS.
- mypy for bike_weather_core: PASS.
- Compileall: PASS.
- JSON parsing: PASS.
- JavaScript syntax: PASS.
- Markdown local-link check: PASS.
- HACS runtime package/core-import contract: PASS.

The first pytest invocation without PYTHONPATH=. was not used as a result;
the CI-equivalent invocation passed.

## GitHub gates

The PR branch is prepared to run CI, Hassfest, HACS and Gitleaks through
GitHub Actions. Results will be recorded here after the PR is opened.

## Open limitations

- No productive HA installation, HACS update, restart, dashboard change or
  live Config-/Options-Flow test was performed.
- No real HA screenshots are included or represented as real.
- The bundled HA adapter is syntax-checked locally, but HA runtime imports
  depend on the GitHub Hassfest environment.

## Git

- Branch: feature/v0.1.0-beta.3-ui-branding
- Commit: to be filled after the final local commit
- Pull request: to be filled after opening; merge intentionally not performed
- Tag/release: none

## Recommendation

**PARTIAL** until GitHub CI/Hassfest/HACS/Gitleaks and a reviewer confirm the
PR. After green remote checks, the user can review and decide whether to merge
and later perform the HACS installation and practical HA test.
