# Wetterquellen

1. Konfigurierte lokale Temperatur-, Wind- und Regensensoren.
2. Eine vorhandene HA-Wetterentität.
3. OpenWeatherMap nur bei expliziter Provider- und Schlüsselkonfiguration.

Die Auswahl erfolgt pro Messgröße und nur für frische, verfügbare Werte. Regen
bleibt von Regenrate getrennt. Aktualisierungszeit, verwendete Quelle und
Datenqualität werden diagnostizierbar gehalten. Direkte Providerabfragen sind
nicht erforderlich, wenn eine HA-Wetterentität verwendet wird.
