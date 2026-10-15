# Installation – v0.1.0-beta.6

Diese Version ist eine HACS-Vorabversion. Aktiviere in HACS die Option für
Vorabversionen und füge `balronu/ha-bike-weather` als benutzerdefiniertes
Repository der Kategorie **Integration** hinzu. Installiere anschließend den
Beta-6-Release und starte Home Assistant nach Aufforderung neu.

Danach:

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** öffnen.
2. **Bike Weather** auswählen und eine Konfiguration anlegen.
3. Eine Home-Assistant-Wetterentität, lokale Sensoren oder einen eigenen
   OpenWeatherMap-Schlüssel konfigurieren.
4. Eine Lovelace-Karte vom Typ `custom:bike-weather-card` mit der erzeugten
   `entry_id` anlegen.

Die Integration registriert `/bike_weather/bike-weather-card.js` automatisch
über die aktuelle Home-Assistant-Static-Path-API.
Eine manuelle Ressourcenregistrierung ist nicht erforderlich. Bestehende,
andere Lovelace-Ressourcen bleiben unverändert.

## Beta-Einschränkung

Die Offline- und Browserprüfungen sind erfolgreich. Die veröffentlichte Beta
wurde jedoch nicht auf der produktiven VM 104 installiert und nicht mit
produktiven Zugangsdaten getestet. Config-/Options-Flow, Coordinator,
WebSocket und Kartenressource müssen vor einer produktiven Nutzung in der
Zielumgebung geprüft werden.

Die bestehende YAML-/REST-Lösung bleibt bis zum ausdrücklich freigegebenen
Hot-Cutover unverändert. Es gibt keinen automatischen Import, keine Entfernung
alter Fahrradwetter-Komponenten und keine Übernahme bestehender Entity-IDs.
