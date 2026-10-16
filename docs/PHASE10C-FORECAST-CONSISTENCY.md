# Phase 10C – Forecast-Konsistenz und Bewertungsstatus

## Diagnose

Die produktive Prüfung am 16.10.2026 ergab eine geladene Bike-Weather-
Config-Entry und eine aktive Wetterquelle. Die Coordinator-Implementierung
holt stündliche Daten über `weather.get_forecasts` und normalisiert sie in
`ForecastSlot`. Die reguläre Forecast-Karte und die spontane Fahrt verwenden
danach dieselbe Python-Funktion `assess_score`; die Karte berechnet keinen
eigenen Score.

Zeiten werden als aware `datetime` verarbeitet. HA-Zeitstempel mit UTC-Offset
und lokale Karteneingaben werden auf derselben Zeitachse verglichen. Ein
Forecast-Intervall ab 14:00 deckt nicht rückwirkend 13:30 ab. Für eine Fahrt
13:30–14:30 ist die Abdeckung daher nur vollständig, wenn auch ein Intervall
ab 13:00 oder ein äquivalentes überlappendes Intervall vorliegt. Es wird nicht
zwischen stündlichen Punkten interpoliert.

## Ursache

Die gemeinsame Scorelogik war fachlich konservativ und lieferte bei fehlender
Niederschlagsmenge weiterhin einen numerischen Teilscore, aber mit
`quality=partial` und `status=unknown`. Die WebSocket-Begründungszuordnung
interpretierte jede solche partielle Qualität als `forecast_unavailable`.
Dadurch konnten Temperatur, Wind, Böen und Regenwahrscheinlichkeit angezeigt
werden, während gleichzeitig fälschlich „keine Prognosedaten“ erschien.

## Korrektur

Die API trennt jetzt drei Fälle:

1. keine berührten Forecast-Slots → `forecast_unavailable`,
2. berührte Slots mit Lücke bis zum Fahrtende →
   `forecast_coverage_incomplete`,
3. vollständige Abdeckung mit fehlenden Faktoren → konkrete Begründung wie
   `precipitation_unavailable` oder `feels_like_unavailable`.

Der Teilscore bleibt sichtbar, wird aber weiterhin als `unknown` bewertet,
wenn kritische Score-Faktoren fehlen. Damit entsteht keine unbegründet positive
Empfehlung. Vollständig fehlende oder veraltete Forecast-Daten bleiben
unverfügbar beziehungsweise veraltet.

## Tests

Ergänzt wurden Regressionen für 13:30–14:30 mit stündlichen Slots,
vollständige und partielle Abdeckung, Score 80 mit vollständigen beziehungsweise
fehlenden Faktoren, sowie die Trennung von leerer und lückenhafter Abdeckung.
Die bestehenden Tests decken zusätzlich UTC/lokale Zeit, Mitternacht und DST
ab. Die Änderung verwendet weiterhin ausschließlich `assess_score`.

Die Browser-Persistenz der spontanen Eingaben bleibt absichtlich pro Browser
und Gerät lokal. Mehrere Geräte oder Browser können deshalb unterschiedliche
Abfahrtszeiten und Dauern anzeigen; das beeinflusst weder Coordinator noch
andere Karten.

## Praxishinweis

Vor der nächsten Beta sollte die Karte mit einem vollständig abgedeckten
Zeitfenster und einem Fenster getestet werden, dessen erste Stunde fehlt. Die
Anzeige muss dann zwischen „Daten fehlen für einen Faktor“ und „Forecast-
Abdeckung unvollständig“ unterscheiden. Der Nutzer führt diesen Test nach
separater produktiver Aktualisierung durch.

Keine Home-Assistant-, Config-Entry-, Entity-ID-, Dashboard-, HACS- oder
VM-104-Änderung wurde vorgenommen. Es wurde kein Merge, Tag oder Release
erstellt.
