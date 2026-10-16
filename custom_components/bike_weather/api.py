"""Authenticated websocket API for the Lovelace card and diagnostics helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_MAX_AGE_MINUTES,
    DEFAULT_RIDE_WEEKDAYS,
    DOMAIN,
    TOMORROW_END_HOUR,
    TOMORROW_START_HOUR,
    WS_CARD_DATA,
    WS_LIST_ENTRIES,
    WS_PLANNING_DATA,
    WS_SPONTANEOUS_RIDE,
)
from .core import DataQuality, assess_day_forecast, assess_ride_window

_REGISTERED = "websocket_registered"


async def async_setup_websocket(hass: HomeAssistant) -> None:
    if hass.data.get(DOMAIN, {}).get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, _card_data)
    websocket_api.async_register_command(hass, _list_entries)
    websocket_api.async_register_command(hass, _spontaneous_ride)
    websocket_api.async_register_command(hass, _planning_data)
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


@websocket_api.websocket_command({
    vol.Required("type"): WS_PLANNING_DATA,
    vol.Optional("entry_id"): vol.All(str, vol.Length(min=1, max=64)),
})
@websocket_api.async_response
async def _planning_data(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return today's configured rides and tomorrow's forecast from cached slots."""
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
    zone = ZoneInfo(hass.config.time_zone)
    now = datetime.now(zone)
    tomorrow = now.date() + timedelta(days=1)
    day_start = datetime.combine(tomorrow, datetime.min.time().replace(hour=TOMORROW_START_HOUR), zone)
    day_end = datetime.combine(tomorrow, datetime.min.time().replace(hour=TOMORROW_END_HOUR), zone)
    last_success = coordinator.data.get("last_success")
    max_age = timedelta(minutes=int(coordinator.options.get("max_age_minutes", DEFAULT_MAX_AGE_MINUTES)))
    stale = not isinstance(last_success, datetime) or last_success < datetime.now(UTC) - max_age
    slots = tuple(coordinator.data.get("forecast_slots", ())) if not stale else ()
    profile = coordinator._profile()
    rides = {
        "outbound": _planned_ride(coordinator, slots, now, "outbound", "ride_outbound", profile),
        "return": _planned_ride(coordinator, slots, now, "return", "ride_return", profile),
    }
    if stale:
        tomorrow_data = _unavailable_day(day_start, day_end, "forecast_stale")
    else:
        tomorrow_data = _day_response(assess_day_forecast(slots, start_at=day_start, end_at=day_end, profile=profile), profile)
    connection.send_result(msg["id"], {
        "entry_id": entry_id,
        "timezone": hass.config.time_zone,
        "today": now.date().isoformat(),
        "rides": rides,
        "tomorrow": {"date": tomorrow.isoformat(), "weekday": tomorrow.weekday(), **tomorrow_data},
    })


def _option(options, prefix, suffix, default):
    return options.get(f"{prefix}_{suffix}", default)


def _weekdays(value):
    result = set()
    for item in value if isinstance(value, (list, tuple, set)) else ():
        try:
            day = int(item)
        except (TypeError, ValueError):
            continue
        if 0 <= day <= 6:
            result.add(day)
    return result


def _planned_ride(coordinator, slots, now, key, prefix, profile):
    options = coordinator.options
    enabled = bool(_option(options, prefix, "enabled", False))
    name = str(_option(options, prefix, "name", "Hinfahrt" if key == "outbound" else "Rückfahrt"))
    start_text = str(_option(options, prefix, "start", "07:30:00" if key == "outbound" else "13:30:00"))
    duration = int(_option(options, prefix, "duration_minutes", 30))
    weekdays = _weekdays(_option(options, prefix, "weekdays", DEFAULT_RIDE_WEEKDAYS))
    base = {"key": key, "name": name, "enabled": enabled, "start_time": start_text[:5], "duration_minutes": duration, "weekdays": sorted(weekdays)}
    if not enabled:
        return {**base, "status": "disabled", "assessment": "unknown", "score": None, "quality": DataQuality.UNAVAILABLE.value, "reason_codes": []}
    if now.weekday() not in weekdays:
        return {**base, "status": "not_planned_today", "assessment": "unknown", "score": None, "quality": DataQuality.UNAVAILABLE.value, "reason_codes": ["not_planned_today"]}
    try:
        parsed = datetime.strptime(start_text[:8], "%H:%M:%S").time() if len(start_text) >= 8 else datetime.strptime(start_text, "%H:%M").time()
    except ValueError:
        return {**base, "status": "invalid", "assessment": "unknown", "score": None, "quality": DataQuality.INVALID.value, "reason_codes": ["invalid_start"]}
    start_at = datetime.combine(now.date(), parsed, now.tzinfo)
    end_at = start_at + timedelta(minutes=duration)
    base.update({"start_at": start_at.isoformat(), "end_at": end_at.isoformat()})
    if start_at <= now:
        return {**base, "status": "past", "assessment": "unknown", "score": None, "quality": DataQuality.UNAVAILABLE.value, "reason_codes": ["past"]}
    result = assess_ride_window(slots, start_at=start_at, duration=timedelta(minutes=duration), profile=profile)
    codes, _ = _ride_reasons(result, profile)
    return {**base, "status": result.assessment.status, "assessment": result.assessment.status, "score": result.assessment.score, "quality": result.assessment.quality.value, "reason_codes": list(codes), "metrics": _ride_metrics(result), "forecast_coverage": {"slot_count": result.slot_count, "covered_until": result.covered_until.isoformat() if result.covered_until else None, "complete": result.covered_until is not None and result.covered_until >= result.end_at}}


def _ride_metrics(result):
    return {"temperature_c": result.average_temperature_c, "minimum_temperature_c": result.minimum_temperature_c, "wind_kmh": result.average_wind_kmh, "maximum_wind_kmh": result.maximum_wind_kmh, "maximum_gust_kmh": result.maximum_gust_kmh, "precipitation_mm": result.maximum_precipitation_mm, "precipitation_probability_pct": result.maximum_precipitation_probability_pct}


def _day_response(result, profile):
    codes = list(dict.fromkeys(result.assessment.reasons))
    if result.maximum_precipitation_mm is not None and result.maximum_precipitation_mm > profile.max_rain_mm:
        codes.append("rain_during_day")
    if result.maximum_precipitation_probability_pct is not None and result.maximum_precipitation_probability_pct > profile.max_precipitation_probability_pct:
        codes.append("rain_possible")
    if result.maximum_wind_kmh is not None and result.maximum_wind_kmh >= profile.max_wind_kmh:
        codes.append("wind_above_limit")
    return {"status": result.assessment.status, "assessment": result.assessment.status, "score": result.assessment.score, "quality": result.assessment.quality.value, "start_at": result.start_at.isoformat(), "end_at": result.end_at.isoformat(), "reason_codes": list(dict.fromkeys(codes)), "metrics": {"minimum_temperature_c": result.minimum_temperature_c, "maximum_temperature_c": result.maximum_temperature_c, "wind_kmh": result.average_wind_kmh, "maximum_wind_kmh": result.maximum_wind_kmh, "maximum_gust_kmh": result.maximum_gust_kmh, "precipitation_mm": result.maximum_precipitation_mm, "precipitation_probability_pct": result.maximum_precipitation_probability_pct}, "forecast_coverage": {"slot_count": result.slot_count, "covered_until": result.covered_until.isoformat() if result.covered_until else None, "complete": result.covered_until is not None and result.covered_until >= result.end_at}, "suitable_windows": [_window_response(item) for item in result.suitable_windows], "adverse_windows": [_window_response(item) for item in result.adverse_windows], "forecast_retrieved_at": result.forecast_retrieved_at.isoformat() if result.forecast_retrieved_at else None}


def _window_response(item):
    return {"start_at": item.start_at.isoformat(), "end_at": item.end_at.isoformat(), "status": item.status, "score": item.score}


def _unavailable_day(start_at, end_at, reason):
    return {"status": "unknown", "assessment": "unknown", "score": None, "quality": DataQuality.STALE.value, "start_at": start_at.isoformat(), "end_at": end_at.isoformat(), "reason_codes": [reason], "metrics": {key: None for key in ("minimum_temperature_c", "maximum_temperature_c", "wind_kmh", "maximum_wind_kmh", "maximum_gust_kmh", "precipitation_mm", "precipitation_probability_pct")}, "forecast_coverage": {"slot_count": 0, "covered_until": None, "complete": False}, "suitable_windows": [], "adverse_windows": []}


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
