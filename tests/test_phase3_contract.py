"""Offline contract checks for the Phase 3 package shape."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class Phase3ContractTests(unittest.TestCase):
    def test_manifest_and_hacs_metadata(self):
        manifest = json.loads(
            (ROOT / "custom_components/bike_weather/manifest.json").read_text()
        )
        self.assertEqual(manifest["domain"], "bike_weather")
        self.assertTrue(manifest["config_flow"])
        self.assertEqual(manifest["version"], "0.1.0-beta.5")
        self.assertEqual(
            json.loads((ROOT / "hacs.json").read_text())["name"], "Bike Weather"
        )

    def test_translations_are_valid_json(self):
        for path in (ROOT / "custom_components/bike_weather/translations").glob(
            "*.json"
        ):
            json.loads(path.read_text())

    def test_card_is_versioned_idempotent_and_uses_authenticated_command(self):
        card = (
            ROOT / "custom_components/bike_weather/www/bike-weather-card.js"
        ).read_text()
        self.assertIn('"bike-weather-card"', card)
        self.assertIn('"bike_weather/card_data"', card)
        self.assertIn("customElements.get", card)
        self.assertIn("static getConfigElement", card)
        self.assertIn("static getStubConfig", card)
        self.assertIn("config-changed", card)
        self.assertIn("0.1.0-beta.5", card)

    def test_forecast_is_not_exposed_as_sensor_attribute_payload(self):
        sensor = (ROOT / "custom_components/bike_weather/sensor.py").read_text()
        self.assertNotIn('"forecast":', sensor)
        self.assertNotIn('data["forecast"]', sensor)

    def test_sensitive_values_are_redacted_in_diagnostics_source(self):
        diagnostics = (
            ROOT / "custom_components/bike_weather/diagnostics.py"
        ).read_text()
        self.assertIn("async_redact_data", diagnostics)
        self.assertIn("CONF_API_KEY", diagnostics)

    def test_hacs_package_bundles_runtime_core(self):
        coordinator = (ROOT / "custom_components/bike_weather/coordinator.py").read_text()
        self.assertIn("from .core import", coordinator)
        self.assertNotIn("from bike_weather_core import", coordinator)
        self.assertTrue((ROOT / "custom_components/bike_weather/core.py").is_file())


if __name__ == "__main__":
    unittest.main()
