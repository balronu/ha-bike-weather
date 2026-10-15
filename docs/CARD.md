# `bike-weather-card`

Die Karte wird als versioniertes Bundle aus der Integration geladen und
registriert sich idempotent. Sie ruft ausschließlich den authentifizierten
WebSocket-Befehl `bike_weather/card_data` auf; Forecast-Payloads werden nicht
als große Sensorattribute gespeichert. Status, Score, aktuelle Messwerte,
Quelle, Qualität und Fehlerzustände sind textlich sichtbar.

Konfiguration: `entry_id`, `compact`, `show_forecast`, `show_windows` und
`show_details`. Die Zeitleiste zeigt ausschließlich bereits im Coordinator
bewertete Forecast-Slots; das Frontend berechnet keinen Score.
