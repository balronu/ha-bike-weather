"""Static contracts for Beta 5 packaging and UI boundaries."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "bike_weather"


def test_beta6_version_is_consistent():
    manifest = json.loads((INTEGRATION / "manifest.json").read_text())
    assert manifest["version"] == "0.1.0-beta.6"
    const = (INTEGRATION / "const.py").read_text()
    assert 'CARD_VERSION = "0.1.0-beta.6"' in const


def test_runtime_core_is_bundled_and_no_external_runtime_import_remains():
    assert (INTEGRATION / "core.py").is_file()
    coordinator = (INTEGRATION / "coordinator.py").read_text()
    assert "from .core import" in coordinator
    assert "bike_weather_core" not in coordinator


def test_config_flow_uses_native_selectors_and_no_hardcoded_gw1100a_ids():
    flow = (INTEGRATION / "config_flow.py").read_text()
    assert "EntitySelector" in flow
    assert "SelectSelector" in flow
    assert "gw1100a" not in flow.lower()


def test_options_flow_revalidates_provider_requirements():
    flow = (INTEGRATION / "config_flow.py").read_text()
    options = flow.split("class BikeWeatherOptionsFlow", 1)[1].split(
        "def _entity", 1
    )[0]
    assert 'errors["base"] = "no_source"' in options
    assert 'errors["base"] = "api_key_required"' in options
    assert 'errors=errors' in options


def test_translations_have_matching_field_keys():
    strings = json.loads((INTEGRATION / "strings.json").read_text())
    de = json.loads((INTEGRATION / "translations" / "de.json").read_text())
    en = json.loads((INTEGRATION / "translations" / "en.json").read_text())
    for document in (de, en):
        assert document["config"]["step"]["user"]["data"].keys() == strings["config"]["step"]["user"]["data"].keys()
        assert document["options"]["step"]["init"]["data"].keys() == strings["options"]["step"]["init"]["data"].keys()


def test_branding_dimensions_and_card_version():
    import struct

    def size(path):
        with path.open("rb") as handle:
            handle.read(16)
            return struct.unpack(">II", handle.read(8))

    assert size(INTEGRATION / "brand" / "icon.png") == (512, 512)
    assert size(ROOT / "assets" / "branding" / "readme-banner.png") == (1280, 320)
    assert size(ROOT / "assets" / "branding" / "social-preview.png") == (1280, 640)
    card = (INTEGRATION / "www" / "bike-weather-card.js").read_text()
    assert 'VERSION = "0.1.0-beta.6"' in card
    assert "config-changed" in card
    assert "translatedStatus" in card
    assert "translatedQuality" in card
    assert "translatedSource" in card
    assert "providerError" in card
    assert "connectionError" in card
