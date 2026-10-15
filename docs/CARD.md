# `bike-weather-card`

Die Karte wird als versioniertes Bundle aus der Integration geladen und
registriert sich idempotent. Sie ruft ausschließlich den authentifizierten
WebSocket-Befehl `bike_weather/card_data` auf; Forecast-Payloads werden nicht
als große Sensorattribute gespeichert. Status, Score, aktuelle Messwerte,
Quelle, Qualität und Fehlerzustände sind textlich sichtbar.

Konfiguration: entry_id, show_forecast, show_details, ride_start und
ride_duration_minutes. Die Zeitleiste zeigt ausschließlich bereits im
Coordinator bewertete Forecast-Slots; das Frontend berechnet keinen Score.

Die Karte erkennt die HA-Sprache (Deutsch/Englisch), bleibt in schmalen
Ansichten ohne horizontalen Überlauf und markiert fehlende oder veraltete
Daten. Registrierung von Karte und Editor ist idempotent; die Ressource wird
mit der Integrationsversion cache-busted.
