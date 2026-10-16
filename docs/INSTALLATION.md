# Installation – v0.3.0 Stable

Die Stable-Version v0.3.0 ist die reguläre HACS-Installation. Füge
`balronu/ha-bike-weather` als benutzerdefiniertes Repository der Kategorie
**Integration** hinzu, wähle den Stable-Release und starte Home Assistant nach
Aufforderung neu.

Danach:

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** öffnen.
2. **Bike Weather** auswählen und eine Konfiguration anlegen.
3. Eine Home-Assistant-Wetterentität, lokale Sensoren oder einen eigenen
   OpenWeatherMap-Schlüssel konfigurieren.
4. Eine Lovelace-Karte vom Typ `custom:bike-weather-card` anlegen. Bei genau
   einer geladenen Integration wird die `entry_id` automatisch erkannt.

Die Integration registriert `/bike_weather/bike-weather-card.js` automatisch
über die aktuelle Home-Assistant-Static-Path-API.
Eine manuelle Ressourcenregistrierung ist nicht erforderlich. Bestehende,
andere Lovelace-Ressourcen bleiben unverändert.

## Einschränkung

Die Offline-, Frontend- und HA-Fixture-Prüfungen sind erfolgreich. Ein echter
Browser-/HA-E2E-Test gegen die produktive VM 104 wurde jedoch nicht
durchgeführt. Die Stable-Version wurde nicht automatisch installiert und
produktive Zugangsdaten wurden nicht verwendet.

Die bestehende YAML-/REST-Lösung bleibt bis zum ausdrücklich freigegebenen
Hot-Cutover unverändert. Es gibt keinen automatischen Import, keine Entfernung
alter Fahrradwetter-Komponenten und keine Übernahme bestehender Entity-IDs.
