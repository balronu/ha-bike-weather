"""OpenWeatherMap API and Fahrradwetter scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import OPENWEATHERMAP_FORECAST_URL


class FahrradwetterApiError(Exception):
    """Raised when fetching Fahrradwetter data fails."""


@dataclass(frozen=True)
class BikeWeatherThresholds:
    """Thresholds used to score forecast slots."""

    min_good_score: int
    ideal_temp_min: float
    ideal_temp_max: float
    acceptable_temp_min: float
    acceptable_temp_max: float
    max_rain: float
    max_pop: int
    max_wind: float
    max_gust: float


class FahrradwetterClient:
    """Small client for the OpenWeatherMap 5 day / 3 hour forecast API."""

    def __init__(
        self,
        session: ClientSession,
        api_key: str,
        latitude: float,
        longitude: float,
        language: str,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._language = language

    async def async_get_forecast(self) -> dict[str, Any]:
        """Fetch forecast data from OpenWeatherMap."""
        params = {
            "appid": self._api_key,
            "lat": self._latitude,
            "lon": self._longitude,
            "units": "metric",
            "lang": self._language,
        }

        try:
            response = await self._session.get(
                OPENWEATHERMAP_FORECAST_URL,
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            data = await response.json()
        except ClientResponseError as err:
            raise FahrradwetterApiError(
                f"OpenWeatherMap returned HTTP {err.status}"
            ) from err
        except (ClientError, TimeoutError) as err:
            raise FahrradwetterApiError("Could not fetch OpenWeatherMap forecast") from err

        if not isinstance(data, dict) or not isinstance(data.get("list"), list):
            raise FahrradwetterApiError("OpenWeatherMap returned an invalid forecast")

        return data


def build_bike_weather(data: dict[str, Any], thresholds: BikeWeatherThresholds) -> dict[str, Any]:
    """Build a Fahrradwetter summary from raw OpenWeatherMap forecast data."""
    slots = [_score_slot(slot, thresholds) for slot in data.get("list", [])[:40]]
    slots = [slot for slot in slots if slot is not None]

    next_slot = slots[0] if slots else None
    next_good = next(
        (slot for slot in slots if slot["score"] >= thresholds.min_good_score),
        None,
    )
    today = _best_for_day(slots, 0)
    tomorrow = _best_for_day(slots, 1)

    score = next_slot["score"] if next_slot else 0
    recommendation = _recommendation(score, thresholds.min_good_score)

    return {
        "score": score,
        "recommendation": recommendation,
        "reason": next_slot["reason"] if next_slot else "Keine Vorhersage verfügbar",
        "next_slot": next_slot,
        "next_good_slot": next_good,
        "today_best_slot": today,
        "tomorrow_best_slot": tomorrow,
        "forecast_slots": slots[:16],
        "raw_count": len(data.get("list", [])),
        "city": data.get("city", {}),
    }


def _best_for_day(slots: list[dict[str, Any]], day_offset: int) -> dict[str, Any] | None:
    now_date = datetime.now().date()
    target = now_date + timedelta(days=day_offset)

    candidates = [
        slot
        for slot in slots
        if slot["datetime"].date() == target and 6 <= slot["datetime"].hour <= 21
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda slot: slot["score"])


def _score_slot(
    slot: dict[str, Any], thresholds: BikeWeatherThresholds
) -> dict[str, Any] | None:
    timestamp = slot.get("dt")
    if timestamp is None:
        return None

    main = slot.get("main", {})
    wind = slot.get("wind", {})
    weather_items = slot.get("weather", [])
    weather = weather_items[0] if weather_items else {}

    temp = _as_float(main.get("temp"))
    feels_like = _as_float(main.get("feels_like"), temp)
    pop = round(_as_float(slot.get("pop"), 0) * 100)
    rain = _as_float(slot.get("rain", {}).get("3h"), 0)
    wind_speed = _as_float(wind.get("speed"), 0)
    gust = _as_float(wind.get("gust"), wind_speed)

    score = 100
    reasons: list[str] = []

    score = _apply_temp_score(score, feels_like, thresholds, reasons)
    if rain > thresholds.max_rain:
        penalty = min(45, int((rain - thresholds.max_rain) * 16) + 12)
        score -= penalty
        reasons.append(f"Regen {rain:.1f} mm/3h")
    if pop > thresholds.max_pop:
        penalty = min(25, int((pop - thresholds.max_pop) / 2))
        score -= penalty
        reasons.append(f"Regenrisiko {pop}%")
    if wind_speed > thresholds.max_wind:
        penalty = min(25, int((wind_speed - thresholds.max_wind) * 5) + 8)
        score -= penalty
        reasons.append(f"Wind {wind_speed:.1f} m/s")
    if gust > thresholds.max_gust:
        penalty = min(20, int((gust - thresholds.max_gust) * 3) + 6)
        score -= penalty
        reasons.append(f"Böen {gust:.1f} m/s")

    dt = datetime.fromtimestamp(timestamp, UTC)
    score = max(0, min(100, score))

    if not reasons:
        reasons.append("Gute Bedingungen")

    return {
        "datetime": dt,
        "timestamp": dt.isoformat(),
        "score": score,
        "recommendation": _recommendation(score, thresholds.min_good_score),
        "reason": ", ".join(reasons),
        "temperature": temp,
        "feels_like": feels_like,
        "precipitation_probability": pop,
        "rain_3h": rain,
        "wind_speed": wind_speed,
        "wind_gust": gust,
        "condition": weather.get("main"),
        "description": weather.get("description"),
        "icon": weather.get("icon"),
    }


def _apply_temp_score(
    score: int,
    feels_like: float,
    thresholds: BikeWeatherThresholds,
    reasons: list[str],
) -> int:
    if thresholds.ideal_temp_min <= feels_like <= thresholds.ideal_temp_max:
        return score
    if thresholds.acceptable_temp_min <= feels_like <= thresholds.acceptable_temp_max:
        reasons.append(f"Temperatur nur ok ({feels_like:.1f} °C)")
        return score - 10

    if feels_like < thresholds.acceptable_temp_min:
        reasons.append(f"Zu kalt ({feels_like:.1f} °C)")
    else:
        reasons.append(f"Zu warm ({feels_like:.1f} °C)")
    return score - 35


def _recommendation(score: int, min_good_score: int) -> str:
    if score >= min_good_score:
        return "good"
    if score >= max(45, min_good_score - 25):
        return "ok"
    return "bad"


def _as_float(value: Any, default: float | None = 0) -> float:
    if value is None:
        return float(default or 0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default or 0)
