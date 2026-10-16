"""Authenticated websocket API for the Lovelace card and diagnostics helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import DOMAIN, WS_CARD_DATA, WS_LIST_ENTRIES, WS_SPONTANEOUS_RIDE
from .core import DataQuality, assess_ride_window

_REGISTERED = "websocket_registered"


async def async_setup_websocket(hass: HomeAssistant) -> None:
    if hass.data.get(DOMAIN, {}).get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, _card_data)
    websocket_api.async_register_command(hass, _list_entries)
    websocket_api.async_register_command(hass, _spontaneous_ride)
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


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SPONTANEOUS_RIDE,
        vol.Optional("entry_id"): vol.All(str, vol.Length(min=1, max=64)),
        vol.Required("start_at"): vol.All(str, vol.Length(min=16, max=40)),
        vol.Required("duration_minutes"): vol.All(vol.Coerce(int), vol.In((15, 30, 45, 60, 90, 120))),
        vol.Optional("timezone"): vol.All(str, vol.Length(min=1, max=64)),
    }
)
@websocket_api.async_response
async def _spontaneous_ride(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Assess one future ride without changing coordinator or config state."""
    entry_id = msg.get("entry_id")
    entries = [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.state is ConfigEntryState.LOADED]
    if entry_id is None:
        if len(entries) != 1:
            connection.send_error(msg["id"], "entry_required", "Exactly one loaded Bike Weather entry is required")
            return
        entry_id = entries[0].entry_id
    if not any(entry.entry_id == entry_id for entry in entries):
        connection.send_error(msg["id"], "not_found", "Bike Weather entry not found or not loaded")
        return
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None or not coordinator.data:
        connection.send_error(msg["id"], "data_unavailable", "Bike Weather data is not available")
        return
    try:
        start_at = _parse_start(msg["start_at"], msg.get("timezone") or hass.config.time_zone)
    except (ValueError, ZoneInfoNotFoundError):
        connection.send_error(msg["id"], "invalid_start", "start_at must be a valid local date and time")
        return
    now = datetime.now(UTC)
    if start_at.astimezone(UTC) <= now:
        connection.send_error(msg["id"], "start_in_past", "The spontaneous ride must start in the future")
        return
    last_success = coordinator.data.get("last_success")
    max_age = timedelta(minutes=int(coordinator.options.get("max_age_minutes", 90)))
    if not isinstance(last_success, datetime) or last_success < now - max_age:
        connection.send_result(msg["id"], _unavailable_ride(entry_id, start_at, msg["duration_minutes"], "forecast_stale"))
        return
    slots = tuple(coordinator.data.get("forecast_slots", ()))
    result = assess_ride_window(
        slots,
        start_at=start_at,
        duration=timedelta(minutes=msg["duration_minutes"]),
        profile=coordinator._profile(),
    )
    reasons = _ride_reasons(result, coordinator._profile())
    connection.send_result(msg["id"], {
        "entry_id": entry_id,
        "start_at": result.start_at.isoformat(),
        "end_at": result.end_at.isoformat(),
        "duration_minutes": msg["duration_minutes"],
        "assessment": result.assessment.status,
        "status": result.assessment.status,
        "score": result.assessment.score,
        "quality": result.assessment.quality.value,
        "reason_codes": reasons[0],
        "reasons": reasons[1],
        "metrics": {
            "temperature_c": result.average_temperature_c,
            "wind_kmh": result.average_wind_kmh,
            "maximum_wind_kmh": result.maximum_wind_kmh,
            "maximum_gust_kmh": result.maximum_gust_kmh,
            "precipitation_mm": result.maximum_precipitation_mm,
            "precipitation_probability_pct": result.maximum_precipitation_probability_pct,
        },
        "forecast_coverage": {
            "slot_count": result.slot_count,
            "covered_until": result.covered_until.isoformat() if result.covered_until else None,
            "complete": result.covered_until is not None and result.covered_until >= result.end_at,
        },
        "forecast_retrieved_at": result.forecast_retrieved_at.isoformat() if result.forecast_retrieved_at else None,
    })


def _parse_start(value: str, timezone: str) -> datetime:
    """Parse the card's local datetime using Home Assistant's timezone."""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    return parsed.replace(tzinfo=ZoneInfo(timezone))


def _unavailable_ride(entry_id, start_at, duration, reason):
    end_at = start_at + timedelta(minutes=duration)
    return {
        "entry_id": entry_id, "start_at": start_at.isoformat(), "end_at": end_at.isoformat(),
        "duration_minutes": duration, "assessment": "unknown", "status": "unknown", "score": None,
        "quality": DataQuality.STALE.value, "reason_codes": [reason], "reasons": [],
        "metrics": {key: None for key in ("temperature_c", "wind_kmh", "maximum_wind_kmh", "maximum_gust_kmh", "precipitation_mm", "precipitation_probability_pct")},
        "forecast_coverage": {"slot_count": 0, "covered_until": None, "complete": False},
        "forecast_retrieved_at": None,
    }


def _ride_reasons(result, profile):
    codes = []
    coverage_complete = result.covered_until is not None and result.covered_until >= result.end_at
    if not coverage_complete:
        codes.append(
            "forecast_coverage_incomplete"
            if result.slot_count > 0 and result.covered_until is not None
            else "forecast_unavailable"
        )
    elif result.assessment.quality != DataQuality.GOOD:
        # A complete forecast window can still lack individual factors.  Do
        # not describe that as missing forecast data: the score is available,
        # but its suitability status remains unknown by design.
        missing_reasons = {
            "temperature": "temperature_unavailable",
            "feels_like": "feels_like_unavailable",
            "wind": "wind_unavailable",
            "gust": "gust_unavailable",
            "rain": "precipitation_unavailable",
            "probability": "precipitation_probability_unavailable",
        }
        codes.extend(
            missing_reasons[reason]
            for reason in result.assessment.reasons
            if reason in missing_reasons
        )
        if not any(code in missing_reasons.values() for code in codes):
            codes.append("score_data_incomplete")
    if result.maximum_precipitation_mm is not None and result.maximum_precipitation_mm > profile.max_rain_mm:
        codes.append("rain_during_ride")
    if result.maximum_precipitation_probability_pct is not None and result.maximum_precipitation_probability_pct > profile.max_precipitation_probability_pct:
        codes.append("rain_possible")
    if result.minimum_temperature_c is not None and result.minimum_temperature_c < profile.min_temperature_c:
        codes.append("temperature_below_limit")
    if result.maximum_wind_kmh is not None and result.maximum_wind_kmh >= profile.max_wind_kmh:
        codes.append("wind_above_limit")
    if result.maximum_gust_kmh is not None and result.maximum_gust_kmh >= profile.max_gust_kmh:
        codes.append("gust_above_limit")
    if not codes and result.assessment.status == "good":
        codes.append("good_conditions")
    return tuple(dict.fromkeys(codes)), tuple(dict.fromkeys(codes))
