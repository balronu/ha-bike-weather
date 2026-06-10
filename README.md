# Fahrradwetter

Fahrradwetter is a custom Home Assistant integration that rates upcoming bike
weather from the OpenWeatherMap 5 day / 3 hour forecast. It replaces hard-coded
template sensors with a reusable UI-configured integration.

## Features

- Uses OpenWeatherMap forecast data for any configured latitude/longitude
- Configurable thresholds for temperature, rain, rain probability, wind and gusts
- Provides a compact recommendation, numeric score and best riding windows
- Can be installed through HACS as a custom repository

## Sensors

After setup, Home Assistant creates these sensors for the configured location:

- `sensor.<name>_empfehlung`: `good`, `ok` or `bad`
- `sensor.<name>_score`: current 3-hour block score from 0 to 100
- `sensor.<name>_nachstes_gutes_zeitfenster`: timestamp of the next good slot
- `sensor.<name>_bester_score_heute`: best daytime score today
- `sensor.<name>_bester_score_morgen`: best daytime score tomorrow
- `sensor.<name>_vorhersageblocke`: number of raw forecast blocks, with the next
  blocks in attributes

The recommendation sensor includes useful attributes such as `reason`,
`next_good_slot`, `today_best_slot` and `tomorrow_best_slot`.

## Installation with HACS

1. Open Home Assistant.
2. Go to **HACS**.
3. Open the three-dot menu in the top-right corner.
4. Select **Custom repositories**.
5. Add the GitHub repository URL.
6. Select **Integration** as the repository type.
7. Click **Add**.
8. Search for **Fahrradwetter** in HACS and install it.
9. Restart Home Assistant.

HACS custom repository handling is documented by HACS itself: add the repository
URL, select the correct type and click **ADD**. See the HACS custom repository
docs: https://www.hacs.xyz/docs/faq/custom_repositories/

## Setup

1. In Home Assistant, go to **Settings** -> **Devices & services**.
2. Click **Add integration**.
3. Search for **Fahrradwetter**.
4. Enter:
   - OpenWeatherMap API key
   - latitude
   - longitude
   - language, for example `de`
5. Save.

You can change scoring thresholds later from the integration's **Configure**
button.

## OpenWeatherMap API key

Create a free API key at OpenWeatherMap and enable access to the 5 day / 3 hour
forecast API. The integration calls:

```text
https://api.openweathermap.org/data/2.5/forecast
```

The integration uses metric units.

## Example dashboard card

```yaml
type: markdown
content: |
  {% set rec = states('sensor.fahrradwetter_empfehlung') %}
  {% set score = states('sensor.fahrradwetter_score') %}
  {% set next = states('sensor.fahrradwetter_nachstes_gutes_zeitfenster') %}
  {% set reason = state_attr('sensor.fahrradwetter_empfehlung', 'reason') %}

  ## Fahrradwetter

  Empfehlung: **{{ rec }}**
  Score: **{{ score }} %**
  Grund: {{ reason }}

  {% if next not in ['unknown', 'unavailable', 'none', ''] %}
  Nächstes gutes Zeitfenster: **{{ as_datetime(next).strftime('%d.%m. %H:%M') }}**
  {% else %}
  Kein gutes Zeitfenster in der aktuellen Vorhersage.
  {% endif %}
```

## Automations

Example: notify when a good bike window appears.

```yaml
alias: Fahrradwetter - gute Bedingungen
trigger:
  - platform: numeric_state
    entity_id: sensor.fahrradwetter_score
    above: 70
condition: []
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Fahrradwetter
      message: >
        Gute Bedingungen: {{ states('sensor.fahrradwetter_score') }} %.
        {{ state_attr('sensor.fahrradwetter_empfehlung', 'reason') }}
mode: single
```

## Development

Repository layout:

```text
custom_components/fahrradwetter/
  __init__.py
  api.py
  config_flow.py
  const.py
  coordinator.py
  manifest.json
  sensor.py
  strings.json
  translations/
hacs.json
```

For HACS publication, this repository includes HACS and Hassfest GitHub Actions.
HACS requires a `hacs.json` in the repository root, and HACS integration
repositories need a Home Assistant `manifest.json` with the usual metadata.
See:

- https://www.hacs.xyz/docs/publish/start/
- https://www.hacs.xyz/docs/publish/integration/
- https://developers.home-assistant.io/docs/creating_integration_manifest/
