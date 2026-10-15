"""Offline tests for the provider-neutral Bike Weather core."""

from __future__ import annotations

import unittest
from datetime import UTC, date, datetime, timedelta, time
from zoneinfo import ZoneInfo

from bike_weather_core import (
    DataQuality,
    ForecastSlot,
    RideProfile,
    RideWindow,
    WeatherObservation,
    WeatherSource,
    assess_classic,
    assess_score,
    assess_window,
    choose_metric_observations,
    find_alternative_starts,
    from_ha_forecast,
    from_ha_weather_state,
    from_openweather,
)


NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)
LOCAL = WeatherSource("local", "Local station", "local", "station")
ONLINE = WeatherSource("online", "HA weather", "ha_weather", "generic")
OWM = WeatherSource("owm", "Direct provider", "direct_api", "openweathermap")


def observation(source=LOCAL, **kwargs):
    values = dict(
        source=source, observed_at=NOW, retrieved_at=NOW,
        temperature_c=15.0, feels_like_c=15.0, wind_kmh=8.0,
        gust_kmh=15.0, precipitation_mm=0.0,
        precipitation_probability_pct=0.0,
    )
    values.update(kwargs)
    return WeatherObservation(**values)


def slot(start: datetime, source=ONLINE, **kwargs):
    values = dict(
        source=source, starts_at=start, ends_at=start + timedelta(hours=1),
        retrieved_at=NOW, temperature_c=15.0, feels_like_c=15.0,
        wind_kmh=8.0, gust_kmh=15.0, precipitation_mm=0.0,
        precipitation_probability_pct=0.0,
    )
    values.update(kwargs)
    return ForecastSlot(**values)


class NormalizationTests(unittest.TestCase):
    def test_ha_weather_units_are_normalized_without_filling_missing_rain(self):
        result = from_ha_weather_state(
            ONLINE,
            {
                "entity_id": "weather.example",
                "state": "cloudy",
                "attributes": {
                    "temperature": 18,
                    "wind_speed": 5,
                    "wind_speed_unit": "m/s",
                    "temperature_unit": "°C",
                    "precipitation_unit": "mm",
                },
            },
            retrieved_at=NOW,
        )
        self.assertEqual(result.wind_kmh, 18.0)
        self.assertIsNone(result.precipitation_mm)

    def test_openweather_forecast_converts_speed_and_probability(self):
        current, slots = from_openweather(
            OWM,
            {"list": [{"dt": NOW.timestamp(), "main": {"temp": 12, "feels_like": 11},
                       "wind": {"speed": 2, "gust": 3}, "pop": 0.4,
                       "rain": {"3h": 0.2}, "weather": [{"description": "Rain"}]}]},
            retrieved_at=NOW,
        )
        self.assertIsNone(current)
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].wind_kmh, 7.2)
        self.assertEqual(slots[0].gust_kmh, 10.8)
        self.assertEqual(slots[0].precipitation_probability_pct, 40.0)

    def test_generic_ha_forecast_preserves_provider_resolution(self):
        slots = from_ha_forecast(
            ONLINE,
            [{"datetime": NOW, "temperature": 12, "wind_speed": 10, "wind_speed_unit": "km/h"},
             {"datetime": NOW + timedelta(hours=1), "temperature": 13, "wind_speed": 11, "wind_speed_unit": "km/h"}],
            retrieved_at=NOW,
        )
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0].ends_at, NOW + timedelta(hours=1))
        self.assertEqual(slots[0].wind_kmh, 10)

    def test_each_metric_uses_its_own_priority(self):
        local = observation(temperature_c=20, wind_kmh=None, precipitation_mm=None)
        online = observation(ONLINE, temperature_c=5, wind_kmh=10, precipitation_mm=0.2)
        selected = choose_metric_observations(
            [local, online],
            {"temperature": ("local", "online"), "wind": ("local", "online"), "rain": ("local", "online")},
            now=NOW,
            max_age=timedelta(minutes=30),
        )
        self.assertIs(selected["temperature"], local)
        self.assertIs(selected["wind"], online)
        self.assertIs(selected["rain"], online)

    def test_stale_sources_are_not_selected(self):
        old = observation(retrieved_at=NOW - timedelta(hours=2))
        selected = choose_metric_observations([old], {"temperature": ("local",)}, now=NOW, max_age=timedelta(minutes=30))
        self.assertIsNone(selected["temperature"])


class ScoringTests(unittest.TestCase):
    def test_classic_boundaries_are_strict_and_missing_is_unknown(self):
        profile = RideProfile(min_temperature_c=10, max_wind_kmh=15, max_rain_mm=0)
        self.assertEqual(assess_classic(observation(temperature_c=10), profile).status, "bad")
        self.assertEqual(assess_classic(observation(wind_kmh=15), profile).status, "bad")
        self.assertEqual(assess_classic(observation(precipitation_mm=0.01), profile).status, "bad")
        self.assertEqual(assess_classic(observation(precipitation_mm=None), profile).status, "unknown")

    def test_score_is_explainable_and_missing_values_lower_confidence(self):
        complete = assess_score(observation(), RideProfile())
        partial = assess_score(observation(gust_kmh=None, precipitation_probability_pct=None), RideProfile())
        self.assertEqual(complete.quality, DataQuality.GOOD)
        self.assertEqual(complete.score, 100)
        self.assertEqual(partial.quality, DataQuality.PARTIAL)
        self.assertLess(partial.score, complete.score)
        self.assertIn("gust", partial.reasons)

    def test_wind_regression_does_not_treat_meters_per_second_as_kmh(self):
        # The old dashboard converted m/s to km/h before comparison.
        result = assess_classic(observation(wind_kmh=18.0))
        self.assertEqual(result.status, "bad")


class WindowTests(unittest.TestCase):
    def test_multi_interval_window_uses_worst_interval(self):
        starts = datetime(2026, 1, 16, 6, tzinfo=UTC)
        slots = [slot(starts), slot(starts + timedelta(hours=1), precipitation_mm=1.0)]
        window = RideWindow(start_at=starts, duration=timedelta(hours=2))
        result = assess_window(window, slots, on_date=date(2026, 1, 16), tz=UTC, mode="classic")
        self.assertEqual(result.status, "bad")
        self.assertEqual(result.score, 0)

    def test_recurring_window_and_midnight_duration(self):
        window = RideWindow(local_start=time(23, 30), duration=timedelta(hours=2), weekdays=frozenset({3}))
        result = window.resolve(date(2026, 1, 15), UTC)
        self.assertEqual(result[1].date(), date(2026, 1, 16))
        self.assertIsNone(window.resolve(date(2026, 1, 16), UTC))

    def test_dst_fallback_keeps_timezone_aware_window(self):
        berlin = ZoneInfo("Europe/Berlin")
        window = RideWindow(local_start=time(1, 30), duration=timedelta(hours=2))
        start, end = window.resolve(date(2026, 10, 25), berlin)
        self.assertIsNotNone(start.tzinfo)
        self.assertIsNotNone(end.tzinfo)
        self.assertEqual((end.astimezone(UTC) - start.astimezone(UTC)).total_seconds(), 3 * 3600)

    def test_alternative_starts_require_real_coverage_no_interpolation(self):
        start = datetime(2026, 1, 16, 6, tzinfo=UTC)
        candidates = find_alternative_starts(
            [slot(start), slot(start + timedelta(hours=2))],
            search_start=start, search_end=start + timedelta(hours=4),
            duration=timedelta(hours=1), step=timedelta(hours=1),
        )
        self.assertEqual(tuple(item[0] for item in candidates), (start, start + timedelta(hours=2)))


if __name__ == "__main__":
    unittest.main()
