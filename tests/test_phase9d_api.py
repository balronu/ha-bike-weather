"""Read-only Config Entry discovery contracts for Phase 9D."""

from __future__ import annotations

import asyncio
import unittest
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

        self.assertEqual(registered, ["_card_data", "_list_entries"])

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
