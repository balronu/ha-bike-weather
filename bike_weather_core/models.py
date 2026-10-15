"""Typed domain models for Bike Weather."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import StrEnum


class DataQuality(StrEnum):
    """Quality of a source value or derived assessment."""

    GOOD = "good"
    PARTIAL = "partial"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"


Metric = str


@dataclass(frozen=True, slots=True)
class WeatherSource:
    """A configured source, without credentials or HA-specific state."""

    source_id: str
    label: str
    kind: str  # local, ha_weather, direct_api
    provider: str
    is_forecast: bool = False


@dataclass(frozen=True, slots=True)
class WeatherObservation:
    """A normalized current observation.

    Missing measurements remain ``None``.  ``retrieved_at`` is separate from
    the measurement time so freshness can be evaluated without guessing.
    """

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
    """A normalized forecast interval."""

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
    """Configurable provisional scoring profile."""

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
    stale_after: timedelta = timedelta(minutes=90)


@dataclass(frozen=True, slots=True)
class RideWindow:
    """A one-off or recurring local-time ride window."""

    start_at: datetime | None = None
    local_start: time | None = None
    duration: timedelta = timedelta(hours=1)
    weekdays: frozenset[int] | None = None  # Monday=0; None means every day
    label: str = "Ride window"

    def resolve(self, on_date: date, tzinfo) -> tuple[datetime, datetime] | None:
        """Resolve this window to an aware interval on ``on_date``."""
        if self.start_at is not None:
            if self.start_at.tzinfo is None:
                raise ValueError("start_at must be timezone-aware")
            if self.start_at.date() != on_date:
                return None
            start = self.start_at
        elif self.local_start is not None:
            if self.weekdays is not None and on_date.weekday() not in self.weekdays:
                return None
            start = datetime.combine(on_date, self.local_start, tzinfo=tzinfo)
        else:
            raise ValueError("RideWindow needs start_at or local_start")
        if self.duration <= timedelta(0):
            raise ValueError("duration must be positive")
        return start, start + self.duration


@dataclass(frozen=True, slots=True)
class RideAssessment:
    """Classic and score results with explicit quality and evidence."""

    status: str  # good, bad, unknown
    score: int | None
    quality: DataQuality
    source_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    factor_scores: Mapping[str, float | None] = field(default_factory=dict)
    factor_weights_used: float = 0.0
    window: tuple[datetime, datetime] | None = None
