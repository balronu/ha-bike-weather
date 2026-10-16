# Phase 12D – Stable-Veröffentlichung

## Ergebnis

Bike Weather v0.3.0 wurde am 16.10.2026 als Stable veröffentlicht.

- Repository: https://github.com/balronu/ha-bike-weather
- PR #12: https://github.com/balronu/ha-bike-weather/pull/12
- PR-12-Merge-Commit und Stable-Release-Commit: edcd665b0e60ba228a3e278aa0f8eacc4c21ccf3
- Stable-Tag: v0.3.0
- Stable-Release: https://github.com/balronu/ha-bike-weather/releases/tag/v0.3.0
- Release-Status: veröffentlicht, nicht Draft, kein Pre-Release, Latest

## Git-Zusammenführung

PR #13 (docs: align bilingual beta documentation) wurde als
e05de20d8f38369bd16f89aaca01d83071c4554e in main übernommen. Dieser Stand
wurde konfliktfrei in fix/phase12b-stable-prep integriert. Die
Phase-12B/12C-Korrekturen blieben erhalten; Entity-IDs, Config Entries und
produktive Home-Assistant-Konfigurationen wurden nicht verändert.

Nach der Stable-Vorbereitung wurde PR #12 auf main gemergt. Der annotierte Tag
v0.3.0 zeigt auf den Merge-Commit edcd665; es wurde kein Tag verschoben oder
überschrieben.

## Versionierung und Dokumentation

Die Version 0.3.0 ist in Manifest, Diagnostics, Kartenkonstante und
Frontend-Bundle synchronisiert. Die README-Struktur ist:

- README.md: vollständige deutsche Hauptdokumentation;
- README.de.md: stabiler deutscher Einstiegspunkt;
- README.en.md: vollständige englische Übersetzung;
- docs/releases/v0.3.0.md: deutsche und englische Release Notes.

Die Dokumentation beschreibt Stable als regulären HACS-Installationsweg und
nennt den nicht durchgeführten produktiven Browser-/HA-E2E-Test ausdrücklich.

## CI und Qualitätssicherung

PR-12-CI, Main-CI und Tag-CI waren auf den jeweiligen exakten Commits grün:

- Python/pytest, Ruff, mypy und Compileall;
- Frontend und JavaScript;
- HA-Fixture;
- Hassfest;
- HACS;
- Gitleaks;
- Validate.

Lokale Zusatzprüfungen für JSON, JavaScript, Compileall, Ruff, mypy,
Frontend-Interaktion, README-Links und git diff --check waren erfolgreich.

## Beta-Bereinigung

Nach erfolgreicher Stable-Tag-CI wurden ausschließlich die alten GitHub-
Release-Objekte entfernt:

- v0.1.0-beta.1 bis v0.1.0-beta.7;
- v0.2.0-beta.1 und v0.2.0-beta.2;
- v0.3.0-beta.1.

Alle historischen Git-Tags und Commits blieben erhalten. Der Stable-Release
v0.3.0 blieb bestehen und ist Latest.

## HACS und produktive Grenzen

Die Repository-Metadaten (hacs.json) sind unverändert kompatibel. Die
Release-Version ist über den Stable-GitHub-Release für HACS verfügbar. Eine
produktive HACS-Installation, Home Assistant VM 104, Proxmox,
Lovelace-Dashboards, Config Entries, Entity-IDs, Automationen und Neustarts
wurden nicht verändert oder ausgeführt.

## Bekannte Einschränkung

Der produktive Browser-/HA-E2E-Test wurde nicht durchgeführt. Die automatisierte
HA-Fixture-Prüfung und die übrigen CI-Gates waren erfolgreich.
