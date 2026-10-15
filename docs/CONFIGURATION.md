# Konfiguration

Der Config Flow erlaubt lokale Sensoren, eine vorhandene HA-Wetterentität oder
den ausdrücklich aktivierten direkten OpenWeatherMap-Provider. Temperatur,
Wind und Regen können unabhängig voneinander aus lokalen Quellen priorisiert
werden. Fehlende Werte bleiben fehlend; sie werden nicht zu Null.

Der Config Flow verwendet native EntitySelectoren für Wetterentitäten sowie
Temperatur-, Wind- und Regensensoren. Sensoren werden nur dann vorausgewählt,
wenn anhand von Device Class und Einheit genau ein Kandidat erkannt wird.
GW1100A-Entity-IDs sind Beispiele und nicht fest codiert.

Unterstützte lokale Einheiten sind °C/°F, km/h/m/s/mph und mm/h/in/h. Eine
unbekannte Einheit oder ein nicht verfügbarer Wert wird nicht zu 0. Im
Options Flow werden Datenalter, Aktualisierung, Grenzwerte, Score-Schwelle
und das Standard-Fahrfenster geändert. Änderungen laden den Config Entry über
die unterstützte HA-Entry-API neu.
