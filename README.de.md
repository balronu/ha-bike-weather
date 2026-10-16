# Bike Weather – deutsche Dokumentation

Dies ist die kompatible deutsche README-Datei. Die vollständige deutsche
Dokumentation steht in [README.md](README.md).

Die aktuelle Entwicklungsversion `v0.3.0-beta.1` ergänzt regelmäßige Fahrten und eine verständliche Morgenprognose. Die spontane Fahrt bleibt erhalten.

Die vorherige Vorabversion `v0.2.0-beta.2` verbessert den Config Flow mit nativen
EntitySelectoren, erkennt eindeutige lokale Wetterstationssensoren,
normalisiert °C/°F, km/h/m/s/mph und Regenraten, lokalisiert Provider und
Options Flow und bringt eine responsive Karte mit visuellem Editor. Zusätzlich
sichert sie den Options Flow gegen leere Optionen, gespeicherte lokale Sensoren
und erneutes Öffnen unter Home Assistant 2026.10 ab; bestehende Beta-2- bis
Beta-4-Einträge bleiben erhalten.

Installation, Konfiguration, Datenpriorität, Score, Datenschutz, Tests und
Einschränkungen sind vollständig in [README.md](README.md) beschrieben.
Die Karte enthält zusätzlich **Spontane Fahrradtour** mit Datum/Uhrzeit,
15–120 Minuten Fahrtdauer, vollständiger Forecast-Abdeckung, konservativer
Bewertung über die bestehende Python-Logik und lokaler Wiederherstellung der
Karteneingaben. Die vollständige deutsche Dokumentation steht in
[README.md](README.md) und im [Phase-10A-Bericht](docs/PHASE10A-SPONTANEOUS-RIDE.md).
Beta 2 trennt zusätzlich vollständige Forecast-Abdeckung mit fehlenden
Bewertungsfaktoren sauber von echten Forecast-Lücken. Produktive HACS-
Installation und Praxistest erfolgen ausschließlich durch den Nutzer.
