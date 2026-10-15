"""HA-independent runtime core bundled with the Bike Weather integration."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from math import isfinite
from typing import Any


class DataQuality(StrEnum):
    GOOD = "good"
    PARTIAL = "partial"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class WeatherSource:
    source_id: str
    label: str
    kind: str
    provider: str
    is_forecast: bool = False


@dataclass(frozen=True, slots=True)
class WeatherObservation:
    source: WeatherSource
    observed_at: datetime
    retrieved_at: datetime
    temperature_c: float | None = None
    feels_like_c: float | None = None
    wind_kmh: float | None = None
    gust_kmh: float | None = None
    precipitation_mm: float | None = None
    rain_rate_mmh: float | None = None
    precipitation_probability_pct: float | None = None
    condition: str | None = None
    quality: DataQuality = DataQuality.GOOD
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ForecastSlot:
    source: WeatherSource
    starts_at: datetime
    ends_at: datetime
    retrieved_at: datetime
    temperature_c: float | None = None
    feels_like_c: float | None = None
    wind_kmh: float | None = None
    gust_kmh: float | None = None
    precipitation_mm: float | None = None
    rain_rate_mmh: float | None = None
    precipitation_probability_pct: float | None = None
    condition: str | None = None
    quality: DataQuality = DataQuality.GOOD
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RideProfile:
    min_temperature_c: float = 10.0
    max_wind_kmh: float = 15.0
    max_rain_mm: float = 0.0
    ideal_temperature_min_c: float = 12.0
    ideal_temperature_max_c: float = 24.0
    acceptable_temperature_min_c: float = 5.0
    acceptable_temperature_max_c: float = 30.0
    max_gust_kmh: float = 40.0
    max_precipitation_probability_pct: float = 40.0
    weight_temperature: float = 30.0
    weight_wind: float = 20.0
    weight_gust: float = 15.0
    weight_rain: float = 20.0
    weight_probability: float = 10.0
    weight_feels_like: float = 5.0


@dataclass(frozen=True, slots=True)
class RideAssessment:
    status: str
    score: int | None
    quality: DataQuality
    source_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    factor_scores: Mapping[str, float | None] = field(default_factory=dict)
    factor_weights_used: float = 0.0


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(UTC)


def normalize_temperature_c(value: Any, unit: str | None) -> float | None:
    number = _number(value)
    if number is None:
        return None
    unit = str(unit or "").lower()
    if unit in {"°f", "f"}:
        return (number - 32) * 5 / 9
    if unit in {"°c", "c", ""}:
        return number
    return None


def normalize_wind_kmh(value: Any, unit: str | None) -> float | None:
    number = _number(value)
    if number is None:
        return None
    unit = str(unit or "").lower()
    if unit in {"m/s", "mps", "ms-1"}:
        return number * 3.6
    if unit == "mph":
        return number * 1.609344
    if unit in {"km/h", "kph", ""}:
        return number
    return None


def normalize_rain_rate_mmh(value: Any, unit: str | None) -> float | None:
    number = _number(value)
    if number is None:
        return None
    unit = str(unit or "").lower()
    if unit in {"in", "inch", "inches", "in/h", "inch/h"}:
        return number * 25.4
    if unit in {"mm", "mm/h", ""}:
        return number
    return None


def from_ha_weather_state(source, state, *, retrieved_at, observed_at=None):
    attrs = _mapping(state.get("attributes", state))
    retrieved_at = _aware(retrieved_at)
    observed_at = _aware(observed_at or retrieved_at)
    return WeatherObservation(
        source, observed_at, retrieved_at,
        normalize_temperature_c(attrs.get("temperature"), attrs.get("temperature_unit")),
        _number(attrs.get("apparent_temperature")),
        normalize_wind_kmh(attrs.get("wind_speed"), attrs.get("wind_speed_unit")),
        precipitation_mm=normalize_rain_rate_mmh(attrs.get("precipitation"), attrs.get("precipitation_unit")),
        precipitation_probability_pct=_number(attrs.get("precipitation_probability")),
        condition=state.get("state") or None,
        metadata={"entity_id": state["entity_id"]} if state.get("entity_id") else {},
    )


def from_ha_forecast(source, forecast: Iterable[Mapping[str, Any]], *, retrieved_at, default_interval=timedelta(hours=1)):
    retrieved_at = _aware(retrieved_at)
    rows = [row for row in forecast if isinstance(row, Mapping) and isinstance(row.get("datetime"), datetime)]
    starts = [_aware(row["datetime"]) for row in rows]
    result = []
    for index, row in enumerate(rows):
        end = starts[index + 1] if index + 1 < len(starts) and starts[index + 1] > starts[index] else starts[index] + default_interval
        result.append(ForecastSlot(
            source, starts[index], end, retrieved_at,
            _number(row.get("temperature")),
            _number(row.get("apparent_temperature")),
            normalize_wind_kmh(row.get("wind_speed"), row.get("wind_speed_unit")),
            normalize_wind_kmh(row.get("wind_gust"), row.get("wind_speed_unit")),
            normalize_rain_rate_mmh(row.get("precipitation"), row.get("precipitation_unit")),
            precipitation_probability_pct=_number(row.get("precipitation_probability")),
            condition=row.get("condition") if isinstance(row.get("condition"), str) else None,
        ))
    return tuple(result)


def from_openweather(source, payload, *, retrieved_at, interval=timedelta(hours=3)):
    retrieved_at = _aware(retrieved_at)
    current = _owm_observation(source, payload, retrieved_at) if isinstance(payload.get("main"), Mapping) else None
    slots = []
    for raw in payload.get("list", ()):
        if not isinstance(raw, Mapping) or _number(raw.get("dt")) is None:
            continue
        starts = datetime.fromtimestamp(float(raw["dt"]), UTC)
        slots.append(_owm_slot(source, raw, starts, starts + interval, retrieved_at))
    return current, tuple(slots)


def _owm_observation(source, raw, retrieved):
    main, wind, rain = _mapping(raw.get("main")), _mapping(raw.get("wind")), _mapping(raw.get("rain"))
    weather = raw.get("weather") if isinstance(raw.get("weather"), list) else []
    observed = datetime.fromtimestamp(float(raw.get("dt", retrieved.timestamp())), UTC)
    return WeatherObservation(source, observed, retrieved, _number(main.get("temp")), _number(main.get("feels_like")), normalize_wind_kmh(wind.get("speed"), "m/s"), normalize_wind_kmh(wind.get("gust"), "m/s"), normalize_rain_rate_mmh(rain.get("1h"), "mm"), condition=weather[0].get("description") if weather and isinstance(weather[0], Mapping) else None)


def _owm_slot(source, raw, starts, ends, retrieved):
    main, wind, rain = _mapping(raw.get("main")), _mapping(raw.get("wind")), _mapping(raw.get("rain"))
    weather = raw.get("weather") if isinstance(raw.get("weather"), list) else []
    probability = _number(raw.get("pop"))
    return ForecastSlot(source, starts, ends, retrieved, _number(main.get("temp")), _number(main.get("feels_like")), normalize_wind_kmh(wind.get("speed"), "m/s"), normalize_wind_kmh(wind.get("gust"), "m/s"), normalize_rain_rate_mmh(rain.get("3h"), "mm"), precipitation_probability_pct=probability * 100 if probability is not None else None, condition=weather[0].get("description") if weather and isinstance(weather[0], Mapping) else None)


def choose_metric_observations(observations, priorities, *, now, max_age):
    now = _aware(now)
    valid = [item for item in observations if item.quality == DataQuality.GOOD and now - item.retrieved_at <= max_age and item.retrieved_at <= now + timedelta(seconds=1)]
    fields = {"temperature": "temperature_c", "feels_like": "feels_like_c", "wind": "wind_kmh", "gust": "gust_kmh", "rain": "precipitation_mm", "rain_rate": "rain_rate_mmh", "probability": "precipitation_probability_pct"}
    return {metric: next((item for source_id in source_ids for item in valid if item.source.source_id == source_id and getattr(item, fields.get(metric, metric), None) is not None), None) for metric, source_ids in priorities.items()}


def _quality(values):
    return DataQuality.GOOD if all(value is not None for value in values) else DataQuality.PARTIAL


def assess_classic(observation, profile=None):
    profile = profile or RideProfile()
    quality = _quality((observation.temperature_c, observation.wind_kmh, observation.precipitation_mm))
    if quality != DataQuality.GOOD:
        return RideAssessment("unknown", None, quality, (observation.source.source_id,), ("Bewertungsdaten unvollständig",))
    good = observation.temperature_c > profile.min_temperature_c and observation.wind_kmh < profile.max_wind_kmh and observation.precipitation_mm <= profile.max_rain_mm
    return RideAssessment("good" if good else "bad", 100 if good else 0, quality, (observation.source.source_id,), ("Grenzwerte erfüllt" if good else "Mindestens ein Grenzwert verletzt",))


def _band(value, low, high, ideal_low, ideal_high):
    if value is None:
        return None
    if ideal_low <= value <= ideal_high:
        return 100.0
    if value < low or value > high:
        return 0.0
    return 100.0 * (value - low) / max(ideal_low - low, 0.001) if value < ideal_low else 100.0 * (high - value) / max(high - ideal_high, 0.001)


def _lower_is_better(value, limit, hard_limit):
    if value is None:
        return None
    if value <= limit:
        return 100.0
    if value >= hard_limit:
        return 0.0
    return 100.0 * (hard_limit - value) / (hard_limit - limit)


def assess_score(observation, profile=None):
    profile = profile or RideProfile()
    temperature = observation.feels_like_c if observation.feels_like_c is not None else observation.temperature_c
    scores = {
        "temperature": _band(temperature, profile.acceptable_temperature_min_c, profile.acceptable_temperature_max_c, profile.ideal_temperature_min_c, profile.ideal_temperature_max_c),
        "wind": _lower_is_better(observation.wind_kmh, profile.max_wind_kmh, profile.max_wind_kmh * 2.5),
        "gust": _lower_is_better(observation.gust_kmh, profile.max_gust_kmh, profile.max_gust_kmh * 1.75),
        "rain": _lower_is_better(observation.precipitation_mm, profile.max_rain_mm, max(profile.max_rain_mm + 3.0, 3.0)),
        "probability": _lower_is_better(observation.precipitation_probability_pct, profile.max_precipitation_probability_pct, 100.0),
        "feels_like": _band(observation.feels_like_c, profile.acceptable_temperature_min_c, profile.acceptable_temperature_max_c, profile.ideal_temperature_min_c, profile.ideal_temperature_max_c),
    }
    weights = {"temperature": profile.weight_temperature, "wind": profile.weight_wind, "gust": profile.weight_gust, "rain": profile.weight_rain, "probability": profile.weight_probability, "feels_like": profile.weight_feels_like}
    total = sum(weights.values())
    used = sum(weights[name] for name, value in scores.items() if value is not None)
    raw = sum(weights[name] * value for name, value in scores.items() if value is not None)
    score = round(max(0.0, min(100.0, raw / total))) if total else 0
    quality = DataQuality.GOOD if used == total else DataQuality.PARTIAL
    status = "good" if score >= 70 and quality == DataQuality.GOOD else "unknown" if quality != DataQuality.GOOD else "bad"
    reasons = tuple(name for name, value in scores.items() if value is None) or ("Alle Score-Faktoren vorhanden",)
    return RideAssessment(status, score, quality, (observation.source.source_id,), reasons, scores, used)


__all__ = ["DataQuality", "ForecastSlot", "RideAssessment", "RideProfile", "WeatherObservation", "WeatherSource", "assess_classic", "assess_score", "choose_metric_observations", "from_ha_forecast", "from_ha_weather_state", "from_openweather", "normalize_rain_rate_mmh", "normalize_temperature_c", "normalize_wind_kmh"]
