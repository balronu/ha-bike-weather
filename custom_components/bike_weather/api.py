"""Authenticated websocket API for the Lovelace card and diagnostics helpers."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import DOMAIN, WS_CARD_DATA, WS_LIST_ENTRIES

_REGISTERED = "websocket_registered"


async def async_setup_websocket(hass: HomeAssistant) -> None:
    if hass.data.get(DOMAIN, {}).get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, _card_data)
    websocket_api.async_register_command(hass, _list_entries)
    hass.data.setdefault(DOMAIN, {})[_REGISTERED] = True


@websocket_api.websocket_command({vol.Required("type"): WS_LIST_ENTRIES})
@websocket_api.async_response
async def _list_entries(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the non-secret, currently known Bike Weather entries."""
    entries = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        state = getattr(entry.state, "value", str(entry.state))
        entries.append(
            {
                "entry_id": entry.entry_id,
                "title": entry.title or "Bike Weather",
                "state": state,
                "available": entry.state is ConfigEntryState.LOADED,
            }
        )
    connection.send_result(msg["id"], {"entries": entries})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_CARD_DATA, vol.Required("entry_id"): str}
)
@websocket_api.async_response
async def _card_data(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    coordinator = hass.data.get(DOMAIN, {}).get(msg["entry_id"])
    if coordinator is None:
        connection.send_error(msg["id"], "not_found", "Bike Weather entry not found")
        return
    data = coordinator.data
    connection.send_result(
        msg["id"],
        {
            "entry_id": msg["entry_id"],
            "assessment": data["classic"].status,
            "score": data["score"].score,
            "quality": data["quality"],
            "sources": data["active_sources"],
            "last_success": data["last_success"].isoformat(),
            "current": _observation(data["current"]),
            "forecast": _forecast(data["forecast"]),
            "errors": data["errors"],
        },
    )


def _observation(item):
    return {
        "temperature_c": item.temperature_c,
        "wind_kmh": item.wind_kmh,
        "precipitation_mm": item.precipitation_mm,
        "condition": item.condition,
    }


def _forecast(items):
    result = []
    for item in items:
        if hasattr(item, "isoformat"):
            continue
        result.append(
            {
                key: (value.isoformat() if hasattr(value, "isoformat") else value)
                for key, value in item.items()
                if key
                in {
                    "datetime",
                    "ends_at",
                    "temperature",
                    "wind_speed",
                    "precipitation",
                    "precipitation_probability",
                    "condition",
                    "status",
                    "score",
                    "quality",
                }
            }
        )
    return result[:48]
