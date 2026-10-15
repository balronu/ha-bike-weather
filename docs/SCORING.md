# Bewertung

Die klassische Bewertung nutzt weiterhin strikt `Temperatur > 10 °C`, `Wind <
15 km/h` und `Regen <= 0 mm`; fehlende Pflichtdaten ergeben `unknown`.

Der erklärbare Score kombiniert Temperatur, Wind, Böen, Regen,
Regenwahrscheinlichkeit und gefühlte Temperatur. Fehlende Faktoren senken die
Konfidenz und können keinen künstlich positiven Score erzeugen. Das Frontend
berechnet keinen Score, sondern stellt ausschließlich die Integrationsdaten
dar.
