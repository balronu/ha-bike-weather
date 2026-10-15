"""Provider payload normalization and independent metric prioritization."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime, timedelta
from math import isfinite
from typing import Any

from .models import DataQuality, ForecastSlot, Metric, WeatherObservation, WeatherSource


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


def _wind_kmh(value: Any, unit: str | None) -> float | None:
    number = _number(value)
    if number is None:
        return None
    if unit in {"m/s", "mps", "ms-1"}:
        return number * 3.6
    if unit in {"mph"}:
        return number * 1.609344
    return number


def _rain_mm(value: Any, unit: str | None) -> float | None:
    number = _number(value)
    if number is None:
        return None
    if unit in {"in", "inch", "inches"}:
        return number * 25.4
    return number


def from_ha_weather_state(
    source: WeatherSource,
    state: Mapping[str, Any],
    *,
    retrieved_at: datetime,
    observed_at: datetime | None = None,
) -> WeatherObservation:
    """Normalize a HA weather entity state without inventing missing values."""
    attrs = _mapping(state.get("attributes", state))
    retrieved_at = _aware(retrieved_at)
    observed_at = _aware(observed_at or retrieved_at)
    wind_unit = attrs.get("wind_speed_unit")
    rain_unit = attrs.get("precipitation_unit")
    return WeatherObservation(
        source=source,
        observed_at=observed_at,
        retrieved_at=retrieved_at,
        temperature_c=_number(attrs.get("temperature")),
        feels_like_c=_number(attrs.get("apparent_temperature")),
        wind_kmh=_wind_kmh(attrs.get("wind_speed"), wind_unit),
        precipitation_mm=_rain_mm(attrs.get("precipitation"), rain_unit),
        precipitation_probability_pct=_number(attrs.get("precipitation_probability")),
        condition=state.get("state") if state.get("state") else None,
        quality=DataQuality.GOOD,
        metadata={"entity_id": state.get("entity_id")}
        if state.get("entity_id")
        else {},
    )


def from_ha_forecast(
    source: WeatherSource,
    forecast: Iterable[Mapping[str, Any]],
    *,
    retrieved_at: datetime,
    default_interval: timedelta = timedelta(hours=1),
) -> tuple[ForecastSlot, ...]:
    """Normalize the generic HA weather forecast contract.

    Providers may expose hourly or coarser entries.  The interval is inferred
    from the next entry when available; no artificial intermediate values are
    created.
    """
    retrieved_at = _aware(retrieved_at)
    rows = [
        row
        for row in forecast
        if isinstance(row, Mapping) and isinstance(row.get("datetime"), datetime)
    ]
    starts = [_aware(row["datetime"]) for row in rows]
    result: list[ForecastSlot] = []
    for index, row in enumerate(rows):
        end = (
            starts[index + 1]
            if index + 1 < len(starts) and starts[index + 1] > starts[index]
            else starts[index] + default_interval
        )
        result.append(
            ForecastSlot(
                source=source,
                starts_at=starts[index],
                ends_at=end,
                retrieved_at=retrieved_at,
                temperature_c=_number(row.get("temperature")),
                feels_like_c=_number(row.get("apparent_temperature")),
                wind_kmh=_wind_kmh(row.get("wind_speed"), row.get("wind_speed_unit")),
                gust_kmh=_wind_kmh(row.get("wind_gust"), row.get("wind_speed_unit")),
                precipitation_mm=_rain_mm(
                    row.get("precipitation"), row.get("precipitation_unit")
                ),
                precipitation_probability_pct=_number(
                    row.get("precipitation_probability")
                ),
                condition=row.get("condition")
                if isinstance(row.get("condition"), str)
                else None,
            )
        )
    return tuple(result)


def from_openweather(
    source: WeatherSource,
    payload: Mapping[str, Any],
    *,
    retrieved_at: datetime,
    interval: timedelta = timedelta(hours=3),
) -> tuple[WeatherObservation | None, tuple[ForecastSlot, ...]]:
    """Normalize OWM current or forecast payloads.

    The function accepts payloads with either a current ``main`` object or a
    forecast ``list``.  No API key or URL is accepted here, keeping credentials
    outside the domain model and tests.
    """
    retrieved_at = _aware(retrieved_at)
    current: WeatherObservation | None = None
    if isinstance(payload.get("main"), Mapping):
        current = _owm_observation(source, payload, retrieved_at)
    slots: list[ForecastSlot] = []
    for raw in payload.get("list", ()):
        if not isinstance(raw, Mapping) or _number(raw.get("dt")) is None:
            continue
        starts = datetime.fromtimestamp(float(raw["dt"]), UTC)
        slots.append(_owm_slot(source, raw, starts, starts + interval, retrieved_at))
    return current, tuple(slots)


def _owm_observation(
    source: WeatherSource, raw: Mapping[str, Any], retrieved: datetime
) -> WeatherObservation:
    main = _mapping(raw.get("main"))
    wind = _mapping(raw.get("wind"))
    rain = _mapping(raw.get("rain"))
    weather = raw.get("weather") if isinstance(raw.get("weather"), list) else []
    dt = datetime.fromtimestamp(float(raw.get("dt", retrieved.timestamp())), UTC)
    return WeatherObservation(
        source=source,
        observed_at=dt,
        retrieved_at=retrieved,
        temperature_c=_number(main.get("temp")),
        feels_like_c=_number(main.get("feels_like")),
        wind_kmh=_wind_kmh(wind.get("speed"), "m/s"),
        gust_kmh=_wind_kmh(wind.get("gust"), "m/s"),
        precipitation_mm=_rain_mm(rain.get("1h"), "mm"),
        precipitation_probability_pct=None,
        condition=weather[0].get("description")
        if weather and isinstance(weather[0], Mapping)
        else None,
    )


def _owm_slot(
    source: WeatherSource,
    raw: Mapping[str, Any],
    starts: datetime,
    ends: datetime,
    retrieved: datetime,
) -> ForecastSlot:
    main = _mapping(raw.get("main"))
    wind = _mapping(raw.get("wind"))
    rain = _mapping(raw.get("rain"))
    weather = raw.get("weather") if isinstance(raw.get("weather"), list) else []
    probability = _number(raw.get("pop"))
    probability_pct = probability * 100 if probability is not None else None
    return ForecastSlot(
        source=source,
        starts_at=starts,
        ends_at=ends,
        retrieved_at=retrieved,
        temperature_c=_number(main.get("temp")),
        feels_like_c=_number(main.get("feels_like")),
        wind_kmh=_wind_kmh(wind.get("speed"), "m/s"),
        gust_kmh=_wind_kmh(wind.get("gust"), "m/s"),
        precipitation_mm=_rain_mm(rain.get("3h"), "mm"),
        precipitation_probability_pct=probability_pct,
        condition=weather[0].get("description")
        if weather and isinstance(weather[0], Mapping)
        else None,
        metadata={"raw_interval": interval_seconds(starts, ends)},
    )


def interval_seconds(starts_at: datetime, ends_at: datetime) -> int:
    """Return an interval length for diagnostics."""
    return max(0, int((ends_at - starts_at).total_seconds()))


def choose_metric_observations(
    observations: Iterable[WeatherObservation],
    priorities: Mapping[Metric, tuple[str, ...]],
    *,
    now: datetime,
    max_age: timedelta,
) -> dict[Metric, WeatherObservation | None]:
    """Choose each metric independently by priority, availability and age."""
    now = _aware(now)
    valid = [
        item
        for item in observations
        if item.quality == DataQuality.GOOD
        and now - item.retrieved_at <= max_age
        and item.retrieved_at <= now + timedelta(seconds=1)
    ]
    result: dict[Metric, WeatherObservation | None] = {}
    fields = {
        "temperature": "temperature_c",
        "feels_like": "feels_like_c",
        "wind": "wind_kmh",
        "gust": "gust_kmh",
        "rain": "precipitation_mm",
        "rain_rate": "rain_rate_mmh",
        "probability": "precipitation_probability_pct",
    }
    for metric, source_ids in priorities.items():
        field_name = fields.get(metric, metric)
        result[metric] = next(
            (
                item
                for source_id in source_ids
                for item in valid
                if item.source.source_id == source_id
                and getattr(item, field_name, None) is not None
            ),
            None,
        )
    return result
