# Phase 10A – Spontane Fahrradtour

Status: implementiert auf `feature/phase10a-spontaneous-ride`, noch nicht
gemergt, getaggt oder veröffentlicht.

## Architekturentscheidung

Die Karte nutzt den vorhandenen authentifizierten WebSocket-Kanal. Der neue
Befehl `bike_weather/spontaneous_ride` liest den bereits aktualisierten
Coordinator-Forecast und ändert weder Coordinator noch Config Entry. Die
gemeinsame Python-Scorefunktion `assess_score` wird pro berührtem Forecast-
Intervall wiederverwendet; im JavaScript existiert keine zweite Bewertungslogik.

## Backend-Schnittstelle

Eingabe: optional `entry_id`, lokales `start_at` im Format
`YYYY-MM-DDTHH:MM`, Home-Assistant-`timezone` und eine Dauer aus 15/30/45/60/
90/120 Minuten. Ohne `entry_id` wird nur bei genau einer geladenen Integration
automatisch gewählt. Ungültige Eingaben, unbekannte Einträge und vergangene
Zeitpunkte werden abgewiesen. Die Antwort enthält Start/Ende, Score, Status,
Qualität, Kennzahlen, Begründungscodes, Abdeckung und Forecast-Zeitstempel.

## Forecast- und Score-Auswertung

Alle Forecast-Slots, die das Zeitfenster berühren, werden berücksichtigt. Die
Abdeckung wird ohne Interpolation geprüft; ein fehlender Slot liefert keine
uneingeschränkt positive Empfehlung. Der kombinierte Score ist der schwächste
Intervallscore. Zusätzlich werden Mittelwerte für Temperatur/Wind sowie
Maxima für Wind, Böen, Regen und Regenwahrscheinlichkeit ausgegeben. Regen,
Wind- und Temperaturbegründungen entstehen aus diesen tatsächlichen Werten
und den unveränderten Profilgrenzen.

## Zeitfenster und Zeitzonen

Die Karte sendet eine lokale Datum/Uhrzeit plus HA-Zeitzone. Das Backend macht
daraus einen aware `datetime`; damit funktionieren Folgetage, Fahrten über
Mitternacht sowie Sommer-/Winterzeit ohne Browser-Zeitzonenannahme. Eine
vergangene Eingabe wird nicht stillschweigend zum nächsten Tag verschoben.

## Speicherung und Frontend

Datum/Uhrzeit und Dauer werden nach 350 ms entprellt abgefragt und nach 500 ms
im kartenbezogenen Browser-`localStorage` gespeichert. Das ist reversibel,
ändert keine Lovelace-Storage-Datei und beeinflusst andere Karten nicht, wenn
`spontaneous_ride_storage_key` für gleichartige Karten unterschiedlich gesetzt
wird. Ohne Schreibberechtigung bzw. privaten Speicher bleibt die Berechnung
verfügbar. Die native `datetime-local`-Auswahl ist mobilfreundlich; CSS fällt
bei schmalen Ansichten auf eine Spalte zurück.

## Tests und Ergebnisse

Hinzugefügte Regressionen decken vollständige und lückenhafte Abdeckung,
Regen/Wind als schlechtestes Intervall, Mitternacht und Europe/Berlin-DST ab.
Frontend-Syntax und bestehende Kartenverträge werden weiter geprüft.
Die lokale vollständige pytest-Sammlung ist ohne installierte
Home-Assistant-Abhängigkeit blockiert; der HA-Fixture-/Hassfest-/HACS-Lauf ist
für den PR vorgesehen. Die genaue CI-Matrix wird nach dem Push ergänzt.

## PR und Einschränkungen

PR: https://github.com/balronu/ha-bike-weather/pull/9 (offen, nicht gemergt).

Die Vorhersage bleibt stündlich und darf keine Minutengenauigkeit vortäuschen.
Die Browser-Persistenz ist nicht synchronisiert zwischen Geräten. Keine
produktive HA-Installation, kein Dashboard, keine Config Entry und keine
HACS-Installation wurde geändert.

## Empfehlung für den ersten Praxistest

Nach separater Freigabe die veröffentlichte Testversion zunächst mit einer
einzigen Karte und einer kurzen 15-Minuten-Fahrt gegen die sichtbare
Forecast-Abdeckung vergleichen. Erst danach längere Zeitfenster und mehrere
Karten prüfen; keine bestehende reguläre Fahrzeit ersetzen.
