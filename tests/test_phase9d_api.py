"""Read-only Config Entry discovery contracts for Phase 9D."""

from __future__ import annotations

import asyncio
import unittest
from datetime import UTC, datetime
from types import SimpleNamespace

from homeassistant.config_entries import ConfigEntryState

from custom_components.bike_weather import api


class _Connection:
    def __init__(self):
        self.results = []

    def send_result(self, message_id, result):
        self.results.append((message_id, result))


class _Entries:
    def __init__(self, entries):
        self._entries = entries

    def async_entries(self, domain):
        self.domain = domain
        return self._entries


class _Hass(SimpleNamespace):
    def async_create_background_task(self, coroutine, name, eager_start=True):
        return asyncio.create_task(coroutine, name=name)


class DiscoveryApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_websocket_commands_are_registered_idempotently(self):
        hass = SimpleNamespace(data={})
        registered = []
        original = api.websocket_api.async_register_command
        api.websocket_api.async_register_command = lambda _hass, handler: registered.append(handler.__name__)
        try:
            await api.async_setup_websocket(hass)
            await api.async_setup_websocket(hass)
        finally:
            api.websocket_api.async_register_command = original

        self.assertEqual(registered, ["_card_data", "_list_entries", "_spontaneous_ride", "_planning_data"])

    async def test_list_entries_returns_only_non_secret_discovery_fields(self):
        hass = _Hass(
            config_entries=_Entries(
                [
                    SimpleNamespace(
                        entry_id="one",
                        title="Garden",
                        state=ConfigEntryState.LOADED,
                        data={"api_key": "must-not-leak"},
                        options={"weather_entity": "weather.secret"},
                    ),
                    SimpleNamespace(
                        entry_id="two",
                        title="Balcony",
                        state=ConfigEntryState.SETUP_ERROR,
                        data={"api_key": "must-not-leak"},
                        options={},
                    ),
                ]
            )
        )
        connection = _Connection()

        api._list_entries(hass, connection, {"id": 7})
        await asyncio.sleep(0)

        self.assertEqual(hass.config_entries.domain, "bike_weather")
        self.assertEqual(
            connection.results,
            [
                (
                    7,
                    {
                        "entries": [
                            {"entry_id": "one", "title": "Garden", "state": "loaded", "available": True},
                            {"entry_id": "two", "title": "Balcony", "state": "setup_error", "available": False},
                        ]
                    },
                )
            ],
        )
        self.assertNotIn("api_key", repr(connection.results))
        self.assertNotIn("weather.secret", repr(connection.results))

    def test_complete_partial_quality_reports_missing_factor_not_missing_forecast(self):
        result = SimpleNamespace(
            assessment=SimpleNamespace(
                quality=api.DataQuality.PARTIAL,
                reasons=("rain",),
                status="unknown",
            ),
            covered_until=datetime(2026, 10, 16, 15, tzinfo=UTC),
            end_at=datetime(2026, 10, 16, 15, tzinfo=UTC),
            slot_count=2,
            maximum_precipitation_mm=None,
            maximum_precipitation_probability_pct=0,
            minimum_temperature_c=12,
            maximum_wind_kmh=5,
            maximum_gust_kmh=18,
        )

        codes, reasons = api._ride_reasons(result, SimpleNamespace(max_rain_mm=0, max_precipitation_probability_pct=40, min_temperature_c=10, max_wind_kmh=15, max_gust_kmh=40))

        self.assertEqual(codes, ("precipitation_unavailable",))
        self.assertEqual(reasons, codes)

    def test_empty_and_incomplete_windows_keep_coverage_reasons_distinct(self):
        base = {
            "assessment": SimpleNamespace(
                quality=api.DataQuality.PARTIAL,
                reasons=("forecast_coverage_incomplete",),
                status="unknown",
            ),
            "end_at": datetime(2026, 10, 16, 15, tzinfo=UTC),
            "maximum_precipitation_mm": None,
            "maximum_precipitation_probability_pct": None,
            "minimum_temperature_c": None,
            "maximum_wind_kmh": None,
            "maximum_gust_kmh": None,
        }
        profile = SimpleNamespace(max_rain_mm=0, max_precipitation_probability_pct=40, min_temperature_c=10, max_wind_kmh=15, max_gust_kmh=40)
        incomplete = SimpleNamespace(**base, covered_until=datetime(2026, 10, 16, 14, tzinfo=UTC), slot_count=1)
        empty = SimpleNamespace(**base, covered_until=None, slot_count=0)

        self.assertEqual(api._ride_reasons(incomplete, profile)[0], ("forecast_coverage_incomplete",))
        self.assertEqual(api._ride_reasons(empty, profile)[0], ("forecast_unavailable",))

    def test_complete_window_has_no_coverage_error_when_all_factors_exist(self):
        end = datetime(2026, 10, 16, 15, tzinfo=UTC)
        result = SimpleNamespace(
            assessment=SimpleNamespace(quality=api.DataQuality.GOOD, reasons=("Alle Score-Faktoren vorhanden",), status="good"),
            covered_until=end,
            end_at=end,
            slot_count=2,
            maximum_precipitation_mm=0,
            maximum_precipitation_probability_pct=0,
            minimum_temperature_c=18,
            maximum_wind_kmh=5,
            maximum_gust_kmh=10,
        )
        profile = SimpleNamespace(max_rain_mm=0, max_precipitation_probability_pct=40, min_temperature_c=10, max_wind_kmh=15, max_gust_kmh=40)
        codes, _ = api._ride_reasons(result, profile)
        self.assertNotIn("forecast_coverage_incomplete", codes)
        self.assertNotIn("forecast_unavailable", codes)

    def test_planned_ride_does_not_turn_unselected_day_into_score_zero(self):
        coordinator = SimpleNamespace(options={"ride_outbound_enabled": True, "ride_outbound_start": "07:30:00", "ride_outbound_weekdays": [0]})
        now = datetime(2026, 10, 16, 6, tzinfo=UTC)  # Friday
        result = api._planned_ride(coordinator, (), now, "outbound", "ride_outbound", SimpleNamespace())
        self.assertEqual(result["status"], "not_planned_today")
        self.assertIsNone(result["score"])

    def test_planned_ride_marks_today_past_without_shifting_to_tomorrow(self):
        coordinator = SimpleNamespace(options={"ride_outbound_enabled": True, "ride_outbound_start": "07:30:00", "ride_outbound_weekdays": [4]})
        now = datetime(2026, 10, 16, 8, tzinfo=UTC)  # Friday
        result = api._planned_ride(coordinator, (), now, "outbound", "ride_outbound", SimpleNamespace())
        self.assertEqual(result["status"], "past")
        self.assertTrue(result["start_at"].startswith("2026-10-16T07:30"))
