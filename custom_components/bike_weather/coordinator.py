"""Coordinator that joins configured HA entities and optional direct provider data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import *
from .core import (
    DataQuality,
    RideProfile,
    WeatherObservation,
    WeatherSource,
    assess_classic,
    assess_score,
    choose_metric_observations,
    from_ha_forecast,
    from_ha_weather_state,
    from_openweather,
)

LOGGER = logging.getLogger(__name__)
OWM_URL = "https://api.openweathermap.org/data/2.5/forecast"


class BikeWeatherCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch, normalize and assess weather for one config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass, self.entry = hass, entry
        self.options = {**entry.data, **entry.options}
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(
                minutes=int(
                    self.options.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
                )
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        observations: list[WeatherObservation] = []
        forecast: list[dict[str, Any]] = []
        forecast_slots = []
        errors: list[str] = []
        if self.options.get(CONF_LOCAL_ENABLED):
            local = self._local_observation(now)
            if local is not None:
                observations.append(local)
        provider = self.options.get(CONF_PROVIDER, DEFAULT_PROVIDER)
        if provider == PROVIDER_HA and self.options.get(CONF_WEATHER_ENTITY):
            entity_id = self.options[CONF_WEATHER_ENTITY]
            state = self.hass.states.get(entity_id)
            if state and state.state not in ("unknown", "unavailable"):
                source = WeatherSource(
                    "ha_weather", entity_id, "ha_weather", "home_assistant"
                )
                normalized = from_ha_weather_state(
                    source,
                    {
                        "entity_id": entity_id,
                        "state": state.state,
                        "attributes": state.attributes,
                    },
                    retrieved_at=now,
                )
                observations.append(normalized)
                forecast = list(state.attributes.get("forecast", []))
                forecast_slots = list(
                    from_ha_forecast(source, forecast, retrieved_at=now)
                )
            else:
                errors.append("ha_weather_unavailable")
        elif provider == PROVIDER_OPENWEATHER:
            try:
                source, current, slots = await self._fetch_openweather(now)
                forecast_slots = list(slots)
                if current:
                    observations.append(current)
                forecast = [
                    {
                        "datetime": s.starts_at,
                        "temperature": s.temperature_c,
                        "wind_speed": s.wind_kmh,
                        "precipitation": s.precipitation_mm,
                        "precipitation_probability": s.precipitation_probability_pct,
                        "condition": s.condition,
                    }
                    for s in slots
                ]
            except (ClientError, TimeoutError, ValueError) as err:
                LOGGER.debug("OpenWeatherMap update failed: %s", err)
                errors.append("provider_error")
        selected = choose_metric_observations(
            observations,
            {
                "temperature": ("local", "ha_weather", "openweathermap"),
                "feels_like": ("local", "ha_weather", "openweathermap"),
                "wind": ("local", "ha_weather", "openweathermap"),
                "gust": ("local", "ha_weather", "openweathermap"),
                "rain": ("local", "ha_weather", "openweathermap"),
                "rain_rate": ("local", "ha_weather", "openweathermap"),
                "probability": ("local", "ha_weather", "openweathermap"),
            },
            now=now,
            max_age=timedelta(
                minutes=int(
                    self.options.get(CONF_MAX_AGE_MINUTES, DEFAULT_MAX_AGE_MINUTES)
                )
            ),
        )
        current = _merge_selected(selected, now)
        profile = self._profile()
        classic = assess_classic(current, profile)
        score = assess_score(current, profile)
        quality = score.quality.value
        sources = sorted(
            {item.source.source_id for item in selected.values() if item is not None}
        )
        timeline = _forecast_assessments(forecast_slots, profile)
        return {
            "current": current,
            "classic": classic,
            "score": score,
            "quality": quality,
            "active_sources": sources,
            "forecast": timeline[:48],
            "last_success": now,
            "errors": errors,
            "forecast_coverage": len(forecast),
        }

    def _local_observation(self, now: datetime) -> WeatherObservation | None:
        def value(entity_key: str):
            entity_id = self.options.get(entity_key)
            state = self.hass.states.get(entity_id) if entity_id else None
            if not state or state.state in ("unknown", "unavailable"):
                return None
            try:
                return float(state.state)
            except (TypeError, ValueError):
                return None

        temperature, wind, rain = (
            value(CONF_TEMPERATURE_ENTITY),
            value(CONF_WIND_ENTITY),
            value(CONF_RAIN_ENTITY),
        )
        if temperature is None and wind is None and rain is None:
            return None
        source = WeatherSource("local", "Local weather station", "local", "ha_sensor")
        return WeatherObservation(
            source=source,
            observed_at=now,
            retrieved_at=now,
            temperature_c=temperature,
            wind_kmh=wind,
            precipitation_mm=rain,
            quality=DataQuality.GOOD
            if all(x is not None for x in (temperature, wind, rain))
            else DataQuality.PARTIAL,
        )

    async def _fetch_openweather(self, now):
        session = async_get_clientsession(self.hass)
        params = {
            "appid": self.options[CONF_API_KEY],
            "lat": self.options.get("latitude"),
            "lon": self.options.get("longitude"),
            "units": "metric",
            "lang": self.hass.config.language,
        }
        async with session.get(OWM_URL, params=params, timeout=20) as response:
            response.raise_for_status()
            payload = await response.json()
        source = WeatherSource(
            "openweathermap", "OpenWeatherMap", "direct_api", "openweathermap", True
        )
        current, slots = from_openweather(source, payload, retrieved_at=now)
        return source, current, slots

    def _profile(self) -> RideProfile:
        return RideProfile(
            min_temperature_c=float(
                self.options.get(CONF_MIN_TEMPERATURE, DEFAULT_MIN_TEMPERATURE)
            ),
            max_wind_kmh=float(self.options.get(CONF_MAX_WIND, DEFAULT_MAX_WIND)),
            max_rain_mm=float(self.options.get(CONF_MAX_RAIN, DEFAULT_MAX_RAIN)),
        )


def _merge_selected(selected, now):
    first = next((x for x in selected.values() if x is not None), None)
    if first is None:
        return WeatherObservation(
            WeatherSource("none", "No source", "none", "none"),
            now,
            now,
            quality=DataQuality.UNAVAILABLE,
        )
    return WeatherObservation(
        source=first.source,
        observed_at=first.observed_at,
        retrieved_at=first.retrieved_at,
        temperature_c=_metric_field(selected, "temperature", "temperature_c"),
        feels_like_c=_metric_field(selected, "feels_like", "feels_like_c"),
        wind_kmh=_metric_field(selected, "wind", "wind_kmh"),
        gust_kmh=_metric_field(selected, "gust", "gust_kmh"),
        precipitation_mm=_metric_field(selected, "rain", "precipitation_mm"),
        rain_rate_mmh=_metric_field(selected, "rain_rate", "rain_rate_mmh"),
        precipitation_probability_pct=_metric_field(
            selected, "probability", "precipitation_probability_pct"
        ),
        condition=first.condition,
        quality=DataQuality.GOOD
        if all(
            _metric_field(selected, metric, field) is not None
            for metric, field in (
                ("temperature", "temperature_c"),
                ("wind", "wind_kmh"),
                ("rain", "precipitation_mm"),
            )
        )
        else DataQuality.PARTIAL,
        metadata={
            "metric_sources": {
                key: value.source.source_id
                for key, value in selected.items()
                if value is not None
            }
        },
    )


def _metric_field(selected, metric, field):
    value = selected.get(metric)
    return getattr(value, field, None) if value is not None else None


def _forecast_assessments(slots, profile):
    """Publish compact, already-scored slots for the authenticated card API."""
    result = []
    for slot in slots:
        assessment = assess_score(slot, profile)
        result.append(
            {
                "datetime": slot.starts_at,
                "ends_at": slot.ends_at,
                "temperature": slot.temperature_c,
                "wind_speed": slot.wind_kmh,
                "precipitation": slot.precipitation_mm,
                "condition": slot.condition,
                "status": assessment.status,
                "score": assessment.score,
                "quality": assessment.quality.value,
            }
        )
    return result
