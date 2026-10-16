# `bike-weather-card`

Die Karte wird als versioniertes Bundle aus der Integration geladen und
registriert sich idempotent. Sie ruft ausschließlich den authentifizierten
WebSocket-Befehl `bike_weather/card_data` auf; Forecast-Payloads werden nicht
als große Sensorattribute gespeichert. Status, Score, aktuelle Messwerte,
Quelle, Qualität und Fehlerzustände sind textlich sichtbar.

Konfiguration: optionale entry_id, show_forecast, show_details, ride_start und
ride_duration_minutes. `ride_start` bleibt als kompatibler Zeit-Default
erhalten; die spontane Fahrt erfasst in der Karte zusätzlich das konkrete
Datum. Zulässige Dauern sind 15, 30, 45, 60, 90 und 120 Minuten. Änderungen
werden entprellt an den read-only Befehl `bike_weather/spontaneous_ride`
gesendet. Die Zeitleiste und die spontane Fahrt verwenden ausschließlich
Backend-Bewertungen; das Frontend berechnet keinen Score.

Die Eingaben werden pro Karte/Integration im Browser-`localStorage` gesichert.
`spontaneous_ride_storage_key` kann für zwei Karten mit derselben Integration
explizit unterschiedlich gesetzt werden. Ohne diesen Schlüssel wird die
stabile Kartenposition im Dashboard einbezogen; beim dauerhaften Umsortieren
kann dadurch ein neuer lokaler Speicher entstehen. Ohne Browser-Speicher
funktioniert die Bewertung weiter, aber ohne Wiederherstellung.

Ohne `entry_id` fragt die Karte über den authentifizierten read-only
WebSocket-Befehl `bike_weather/list_entries` die geladenen Bike-Weather-
Integrationen ab. Eine einzelne Integration wird automatisch gewählt; bei
mehreren Integrationen fordert die Karte eine Auswahl an. Der Editor speichert
eine explizite Auswahl dauerhaft.

Die Karte erkennt die HA-Sprache (Deutsch/Englisch), bleibt in schmalen
Ansichten ohne horizontalen Überlauf und markiert fehlende oder veraltete
Daten. Registrierung von Karte und Editor ist idempotent; die Ressource wird
mit der Integrationsversion cache-busted.
