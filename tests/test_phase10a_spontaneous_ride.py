import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

_CORE_SPEC = importlib.util.spec_from_file_location(
    "bike_weather_runtime_core",
    Path(__file__).parents[1] / "custom_components/bike_weather/core.py",
)
_CORE = importlib.util.module_from_spec(_CORE_SPEC)
assert _CORE_SPEC.loader is not None
sys.modules["bike_weather_runtime_core"] = _CORE
_CORE_SPEC.loader.exec_module(_CORE)

DataQuality = _CORE.DataQuality
ForecastSlot = _CORE.ForecastSlot
RideProfile = _CORE.RideProfile
WeatherSource = _CORE.WeatherSource
assess_ride_window = _CORE.assess_ride_window


SOURCE = WeatherSource("ha_weather", "Forecast", "ha_weather", "home_assistant", True)
RETRIEVED = datetime(2026, 10, 16, 10, tzinfo=UTC)


def slot(start, *, temperature=18, wind=5, gust=10, rain=0, probability=0, minutes=60):
    return ForecastSlot(
        SOURCE,
        start,
        start + timedelta(minutes=minutes),
        RETRIEVED,
        temperature_c=temperature,
        feels_like_c=temperature,
        wind_kmh=wind,
        gust_kmh=gust,
        precipitation_mm=rain,
        precipitation_probability_pct=probability,
    )


def test_complete_window_uses_worst_interval_and_aggregate_values():
    start = datetime(2026, 10, 16, 15, tzinfo=UTC)
    result = assess_ride_window(
        [slot(start), slot(start + timedelta(hours=1), rain=1.2, probability=80)],
        start_at=start,
        duration=timedelta(hours=2),
    )

    assert result.assessment.quality is DataQuality.GOOD
    assert result.assessment.status == "good"
    assert result.assessment.score is not None and result.assessment.score < 100
    assert result.maximum_precipitation_mm == 1.2
    assert result.maximum_precipitation_probability_pct == 80
    assert result.slot_count == 2


def test_partial_forecast_never_becomes_positive():
    start = datetime(2026, 10, 16, 15, tzinfo=UTC)
    result = assess_ride_window(
        [slot(start)], start_at=start, duration=timedelta(hours=2)
    )

    assert result.assessment.status == "unknown"
    assert result.assessment.score is None
    assert result.assessment.quality is DataQuality.PARTIAL
    assert result.covered_until == start + timedelta(hours=1)


def test_cross_midnight_window_is_evaluated_without_local_date_loss():
    zone = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 10, 16, 23, 30, tzinfo=zone)
    result = assess_ride_window(
        [slot(start.astimezone(UTC), minutes=60), slot((start + timedelta(hours=1)).astimezone(UTC), minutes=60)],
        start_at=start,
        duration=timedelta(minutes=90),
    )

    assert result.end_at == start + timedelta(minutes=90)
    assert result.assessment.status == "good"
    assert result.slot_count == 2


def test_dst_transition_keeps_aware_window_and_forecast_coverage():
    zone = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 10, 25, 1, 30, tzinfo=zone)
    utc_start = start.astimezone(UTC)
    result = assess_ride_window(
        [slot(utc_start), slot(utc_start + timedelta(hours=1)), slot(utc_start + timedelta(hours=2))],
        start_at=start,
        duration=timedelta(hours=2),
        profile=RideProfile(),
    )

    assert result.start_at.tzinfo is not None
    assert result.covered_until is not None and result.covered_until >= result.end_at
