"""Phase 11A regular-ride and tomorrow forecast contracts."""

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location("bike_weather_phase11a_core", Path(__file__).parents[1] / "custom_components/bike_weather/core.py")
core = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = core
spec.loader.exec_module(core)

SOURCE = core.WeatherSource("ha_weather", "Forecast", "ha_weather", "home_assistant", True)
RETRIEVED = datetime(2026, 10, 16, 10, tzinfo=UTC)


def slot(start, *, rain=0, probability=0, wind=5, temperature=18, minutes=60):
    return core.ForecastSlot(SOURCE, start, start + timedelta(minutes=minutes), RETRIEVED, temperature_c=temperature, feels_like_c=temperature, wind_kmh=wind, gust_kmh=10, precipitation_mm=rain, precipitation_probability_pct=probability)


def test_half_hour_departure_uses_overlapping_hourly_slots_and_shared_score():
    start = datetime(2026, 10, 16, 13, 30, tzinfo=UTC)
    result = core.assess_ride_window([slot(start - timedelta(minutes=30)), slot(start + timedelta(minutes=30))], start_at=start, duration=timedelta(hours=1))
    assert result.slot_count == 2
    assert result.covered_until >= result.end_at
    assert result.assessment.status == "good"


def test_tomorrow_aggregates_the_period_and_groups_actual_windows():
    start = datetime(2026, 10, 17, 6, tzinfo=UTC)
    slots = [slot(start + timedelta(hours=index), rain=2 if index == 3 else 0, probability=90 if index == 3 else 0, wind=100 if index == 3 else 5) for index in range(16)]
    result = core.assess_day_forecast(slots, start_at=start, end_at=start + timedelta(hours=16))
    assert result.assessment.status == "bad"
    assert result.assessment.score is not None and result.assessment.score < 100
    assert result.suitable_windows and result.adverse_windows
    assert result.maximum_precipitation_mm == 2


def test_partial_day_coverage_is_unknown_even_when_available_slots_score_good():
    start = datetime(2026, 10, 17, 6, tzinfo=UTC)
    result = core.assess_day_forecast([slot(start + timedelta(hours=index)) for index in range(4)], start_at=start, end_at=start + timedelta(hours=6))
    assert result.assessment.status == "unknown"
    assert result.assessment.score is None
    assert result.assessment.quality is core.DataQuality.PARTIAL
    assert not result.suitable_windows
    assert result.adverse_windows


def test_high_rain_probability_is_not_presented_as_suitable():
    start = datetime(2026, 10, 17, 6, tzinfo=UTC)
    result = core.assess_day_forecast([slot(start, probability=90)], start_at=start, end_at=start + timedelta(hours=1))
    assert result.assessment.status == "bad"
    assert result.assessment.score is not None
    assert not result.suitable_windows
    assert result.adverse_windows[0].status == "adverse"


def test_missing_factor_keeps_score_but_marks_day_quality_partial():
    zone = ZoneInfo("Europe/Berlin")
    start = datetime(2026, 10, 25, 6, tzinfo=zone)
    values = [slot((start + timedelta(hours=index)).astimezone(UTC), rain=None) for index in range(2)]
    result = core.assess_day_forecast(values, start_at=start, end_at=start + timedelta(hours=2))
    assert result.assessment.score == 80
    assert result.assessment.status == "unknown"
    assert result.assessment.quality is core.DataQuality.PARTIAL


def test_no_forecast_slots_is_unavailable_not_a_bad_weather_score():
    start = datetime(2026, 10, 17, 6, tzinfo=UTC)
    result = core.assess_day_forecast([], start_at=start, end_at=start + timedelta(hours=1))
    assert result.assessment.status == "unknown"
    assert result.assessment.score is None
    assert result.assessment.quality is core.DataQuality.UNAVAILABLE
    assert result.assessment.reasons == ("forecast_unavailable",)
