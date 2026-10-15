# Hot-Cutover und Rollback

Die bisherigen Entitäten (`sensor.fahrradwetter_aktuell`, `..._heute`,
`..._nachster_block`, `..._morgen_06_00`, `..._morgen_15_00` und
`sensor.raw_fahrrad_forecast`) werden nicht übernommen. Neue Unique IDs sind an
Config Entry und Integrationsdomain gebunden.

Nach ausdrücklicher Freigabe: Zustand und reguläre Backups prüfen, betroffene
YAML- und Dashboard-Konfiguration separat sichern, nur die zwei eindeutig
zugeordneten REST-Sensoren, vier Template-Sensoren und die alte
Fahrradwetter-Karte entfernen, YAML validieren/reloaden, danach Bike Weather
installieren und die neue Karte an derselben Stelle einsetzen. Gemeinsame
OpenWeatherMap-/MET-Norway-/GW1100A-Ressourcen sowie globale Lovelace-
Ressourcen bleiben unangetastet.

Rollback: Reload/Restart stoppen, die gesicherten YAML- und Dashboard-Blöcke
wiederherstellen, validieren, den neuen Config Entry entfernen und die alte
Karte wieder einsetzen. Erwartete Ausfallzeit ist ohne HA-Laufzeittest nicht
seriös abschätzbar; sie umfasst mindestens die kontrollierte Validierung und
den notwendigen Reload.
