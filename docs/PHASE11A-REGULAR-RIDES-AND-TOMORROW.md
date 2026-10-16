# Phase 11A – Regelmäßige Fahrten und Morgenprognose

## Architektur

Die Karte ruft `bike_weather/planning_data` read-only auf. Die Antwort enthält
Hinfahrt, Rückfahrt und die Tagesprognose für morgen. Der Endpoint verwendet die
bereits vom Coordinator geladenen `forecast_slots`; dadurch entstehen keine
doppelten Forecast-Serviceaufrufe und mehrere Karten beeinflussen sich nicht.

Die bestehende Python-Bewertung (`assess_score`, `assess_ride_window`) bleibt
die einzige Score-Quelle. `assess_day_forecast` aggregiert die einzelnen
Bewertungen konservativ und gruppiert nur tatsächlich abgedeckte Zeitfenster.

## Konfiguration

Der Options-Flow ergänzt zwei unabhängige Profile mit Aktivierung, Anzeigename,
Abfahrtszeit, Dauer und Montag–Sonntag als native Mehrfachauswahl. Fehlende
Optionen älterer Config Entries erhalten Defaults; bestehende Optionen,
Config-Entry-IDs und Entity-IDs bleiben unverändert.

Für heute werden deaktivierte oder nicht ausgewählte Fahrten als „Heute nicht
geplant“ angezeigt. Eine bereits vergangene Abfahrt wird als vergangen markiert
und nicht stillschweigend auf morgen verschoben. Die Morgenprognose bewertet
den festen Tagesbereich 06:00–22:00 in der Home-Assistant-Zeitzone.

## Datenqualität und Zeit

Forecast-Zeitstempel werden als timezone-aware Werte verarbeitet. Überlappende
stündliche Slots decken auch Abfahrten wie 13:30 ab; es wird nicht auf
Minutengenauigkeit interpoliert. Lücken, fehlende Score-Faktoren und veraltete
Daten führen zu `unknown` beziehungsweise eingeschränkter Datenqualität und
werden nicht als positive Empfehlung dargestellt. Geeignete und ungünstige
Zeiträume stammen ausschließlich aus vorhandenen Slots.

## Frontend und Persistenz

Die Karte zeigt heute Hinfahrt/Rückfahrt, danach die Morgenprognose und
anschließend unverändert die spontane Fahrradtour. Das Layout verwendet CSS
Grid mit Smartphone-Breakpoint ohne zusätzliche Abhängigkeiten. Die spontane
Fahrt bleibt pro Karte und Browser lokal gespeichert; regelmäßige Fahrten und
die Morgenprognose stammen aus der Integration. Deshalb können mehrere
Browser/Geräte unterschiedliche spontane Eingaben anzeigen, ohne einander zu
überschreiben.

## Tests und Einschränkungen

Abgedeckt sind vollständige/teilweise/leere Forecasts, 13:30-Fenster,
Mitternacht/DST, fehlende Faktoren, Tagesfenster, Options-Flow-Defaults,
automatische Entry-Erkennung, Karteninteraktion und JavaScript-Syntax. Die
vollständigen HA-Laufzeit-, Hassfest-, HACS-, Gitleaks- und GitHub-Actions-
Prüfungen laufen im PR-CI; ein echter Browser-E2E-Test ist lokal nicht
verfügbar.

## Empfehlung für Phase 11B

Nach grüner PR-CI zunächst mit deaktivierten Beispielprofilen testen, danach
die tatsächlichen Nutzerzeiten im Options-Flow setzen. Für Phase 11B bietet
sich eine konfigurierbare Tageszeitspanne sowie ein echter HA-Browser-E2E-Test
an.

PR: https://github.com/balronu/ha-bike-weather/pull/11 (bewusst offen).
