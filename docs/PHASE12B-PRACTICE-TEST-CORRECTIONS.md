# Phase 12B – Praxistest-Korrekturen

## Nachgewiesene Ursachen

Die spontane Abfahrt wurde korrekt aus der lokalen Kartenpersistenz gelesen und
als `start_at` an `bike_weather/spontaneous_ride` gesendet. Das sichtbare
`07:30 · 60 Minuten` stammte nicht aus diesem Backend-Aufruf: Die abschließende
Detailzeile der Karte zeigte weiterhin die alte Konfigurationszeile
`ride_start`/`ride_duration_minutes`. Diese irreführende Darstellung wurde
entfernt. Ein Regressionstest prüft jetzt den exakten 13:30-WebSocket-Wert.

Die sechs alten allgemeinen Forecast-Kacheln wurden noch zusätzlich zur neuen
Struktur gerendert. Sie werden nicht mehr angezeigt; die Forecast-Daten bleiben
für Backend-Bewertungen verfügbar.

## Änderungen

- Kartenstruktur ist kompakt: aktuelles Wetter, heutige Fahrten, morgen,
  spontane Fahrt;
- alte Forecast-Kachelgruppe entfernt;
- veraltete `Fahrzeitfenster`-Detailzeile entfernt;
- Datums-/Zeitdarstellung verwendet HA-Sprache und HA-Zeitzone;
- automatische Entry-Erkennung, Options Flow und spontane Backend-Bewertung
  unverändert erhalten;
- stündliche Slot-Überlappung und fehlende Daten bleiben konservativ:
  fehlende zeitliche Abdeckung wird nicht mit fehlenden Einzelwerten vermischt;
- `manifest.json`, Release-Tag und GitHub-Prerelease enthalten die numerische
  Version `0.3.0-beta.1`. HACS zeigt bei Auswahl eines Branches naturgemäß den
  Commit; für eine Versionsanzeige muss der veröffentlichte Release-Tag gewählt
  werden.

## Qualitätssicherung

Gezielte Browser-Karteninteraktion, exakter 13:30-Aufruf, Entfernung der alten
Kacheln, Python-Zeitfenster-/DST-Regressionen sowie bestehende Python-,
Frontend-, HACS-, Hassfest- und Gitleaks-Prüfungen wurden ausgeführt. Ein
produktiver HA- oder Dashboard-Test wurde nicht durchgeführt.

PR: https://github.com/balronu/ha-bike-weather/pull/12 (offen).
