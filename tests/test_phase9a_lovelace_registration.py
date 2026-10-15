"""Regression contracts for the Beta 5 Lovelace bundle registration."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
INIT = ROOT / "custom_components" / "bike_weather" / "__init__.py"
CARD = ROOT / "custom_components" / "bike_weather" / "www" / "bike-weather-card.js"


def test_card_uses_current_async_static_path_api_with_legacy_fallback():
    source = INIT.read_text()

    assert "StaticPathConfig" in source
    assert "async_register_static_paths" in source
    assert "await hass.http.async_register_static_paths(" in source
    assert 'StaticPathConfig(CARD_URL, str(card_path), cache_headers=True)' in source
    assert 'add_extra_js_url(hass, f"{CARD_URL}?v={CARD_VERSION}")' in source
    assert "hass.http.register_static_path(" in source


def test_card_bundle_contract_remains_idempotent_and_versioned():
    source = CARD.read_text()

    assert 'customElements.get("bike-weather-card")' in source
    assert 'customElements.define("bike-weather-card", BikeWeatherCard)' in source
    assert 'customElements.get("bike-weather-card-editor")' in source
    assert 'window.BIKE_WEATHER_CARD_VERSION = VERSION' in source
    assert 'const VERSION = "0.1.0-beta.6"' in source


def test_card_editor_initializes_before_hass_or_set_config():
    source = CARD.read_text()

    assert "constructor() { super(); this.config =" in source
    assert "...(config || {})" in source
    assert "if (!this.config) return;" in source


def test_ha_weather_uses_response_forecast_service_not_state_attribute():
    source = (ROOT / "custom_components" / "bike_weather" / "coordinator.py").read_text()

    assert '"get_forecasts"' in source
    assert '"type": "hourly"' in source
    assert "return_response=True" in source
    assert 'state.attributes.get("forecast", [])' not in source
