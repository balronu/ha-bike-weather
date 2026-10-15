"""Data coordinator for Fahrradwetter."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BikeWeatherThresholds,
    FahrradwetterApiError,
    FahrradwetterClient,
    build_bike_weather,
)
from .const import (
    CONF_ACCEPTABLE_TEMP_MAX,
    CONF_ACCEPTABLE_TEMP_MIN,
    CONF_API_KEY,
    CONF_IDEAL_TEMP_MAX,
    CONF_IDEAL_TEMP_MIN,
    CONF_LANGUAGE,
    CONF_MAX_GUST,
    CONF_MAX_POP,
    CONF_MAX_RAIN,
    CONF_MAX_WIND,
    CONF_MIN_GOOD_SCORE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ACCEPTABLE_TEMP_MAX,
    DEFAULT_ACCEPTABLE_TEMP_MIN,
    DEFAULT_IDEAL_TEMP_MAX,
    DEFAULT_IDEAL_TEMP_MIN,
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_GUST,
    DEFAULT_MAX_POP,
    DEFAULT_MAX_RAIN,
    DEFAULT_MAX_WIND,
    DEFAULT_MIN_GOOD_SCORE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

LOGGER = logging.getLogger(__name__)


class FahrradwetterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and score Fahrradwetter data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        options = {**entry.data, **entry.options}
        self._client = FahrradwetterClient(
            async_get_clientsession(hass),
            options[CONF_API_KEY],
            float(options["latitude"]),
            float(options["longitude"]),
            options.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
        )
        self._thresholds = BikeWeatherThresholds(
            min_good_score=int(options.get(CONF_MIN_GOOD_SCORE, DEFAULT_MIN_GOOD_SCORE)),
            ideal_temp_min=float(options.get(CONF_IDEAL_TEMP_MIN, DEFAULT_IDEAL_TEMP_MIN)),
            ideal_temp_max=float(options.get(CONF_IDEAL_TEMP_MAX, DEFAULT_IDEAL_TEMP_MAX)),
            acceptable_temp_min=float(
                options.get(CONF_ACCEPTABLE_TEMP_MIN, DEFAULT_ACCEPTABLE_TEMP_MIN)
            ),
            acceptable_temp_max=float(
                options.get(CONF_ACCEPTABLE_TEMP_MAX, DEFAULT_ACCEPTABLE_TEMP_MAX)
            ),
            max_rain=float(options.get(CONF_MAX_RAIN, DEFAULT_MAX_RAIN)),
            max_pop=int(options.get(CONF_MAX_POP, DEFAULT_MAX_POP)),
            max_wind=float(options.get(CONF_MAX_WIND, DEFAULT_MAX_WIND)),
            max_gust=float(options.get(CONF_MAX_GUST, DEFAULT_MAX_GUST)),
        )

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=int(options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            forecast = await self._client.async_get_forecast()
        except FahrradwetterApiError as err:
            raise UpdateFailed(str(err)) from err

        return build_bike_weather(forecast, self._thresholds)
