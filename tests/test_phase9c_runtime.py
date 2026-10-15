"""Focused Phase 9C runtime contracts for HA weather response handling."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.bike_weather.coordinator import BikeWeatherCoordinator


class _Services:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def async_call(self, domain, service, data, **kwargs):
        self.calls.append((domain, service, data, kwargs))
        return self.response


class ForecastResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_ha_forecast_is_read_from_weather_service_response(self):
        services = _Services(
            {
                "weather.forecast_home": {
                    "forecast": [{"datetime": "2026-10-15T15:00:00+00:00"}]
                }
            }
        )
        coordinator = object.__new__(BikeWeatherCoordinator)
        coordinator.hass = SimpleNamespace(services=services)

        result = await coordinator._async_get_ha_forecast("weather.forecast_home")

        self.assertEqual(result, [{"datetime": "2026-10-15T15:00:00+00:00"}])
        self.assertEqual(
            services.calls,
            [
                (
                    "weather",
                    "get_forecasts",
                    {"entity_id": "weather.forecast_home", "type": "hourly"},
                    {"blocking": True, "return_response": True},
                )
            ],
        )

    async def test_ha_forecast_accepts_service_response_wrapper(self):
        services = _Services(
            {
                "service_response": {
                    "weather.forecast_home": {"forecast": [{"temperature": 17}]}
                }
            }
        )
        coordinator = object.__new__(BikeWeatherCoordinator)
        coordinator.hass = SimpleNamespace(services=services)

        self.assertEqual(
            await coordinator._async_get_ha_forecast("weather.forecast_home"),
            [{"temperature": 17}],
        )
