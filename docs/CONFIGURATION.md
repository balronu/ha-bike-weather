# Konfiguration

Der Config Flow erlaubt lokale Sensoren, eine vorhandene HA-Wetterentität oder
den ausdrücklich aktivierten direkten OpenWeatherMap-Provider. Temperatur,
Wind und Regen können unabhängig voneinander aus lokalen Quellen priorisiert
werden. Fehlende Werte bleiben fehlend; sie werden nicht zu Null.

Im Options Flow werden Datenalter, Aktualisierung, Grenzwerte, Score-Schwelle
und das Standard-Fahrfenster geändert. Änderungen laden den Config Entry über
die unterstützte HA-Entry-API neu.
