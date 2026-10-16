"""Redacted diagnostics for Bike Weather."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import CONF_API_KEY, DOMAIN

TO_REDACT = {CONF_API_KEY, "latitude", "longitude", "location", "token", "password"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    data = coordinator.data if coordinator and coordinator.data else {}
    options = async_redact_data({**entry.data, **entry.options}, TO_REDACT)
    return {
        "integration_version": "0.3.0",
        "entry": options,
        "provider": options.get("provider"),
        "sources": data.get("active_sources", []),
        "quality": data.get("quality"),
        "last_success": _iso(data.get("last_success")),
        "errors": data.get("errors", []),
        "forecast_coverage": data.get("forecast_coverage", 0),
        "score_profile": {
            key: options[key]
            for key in ("min_temperature_c", "max_wind_kmh", "max_rain_mm", "min_score")
            if key in options
        },
    }


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value
