"""Config flow for Fahrradwetter."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FahrradwetterApiError, FahrradwetterClient
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
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class FahrradwetterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fahrradwetter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = FahrradwetterClient(
                async_get_clientsession(self.hass),
                user_input[CONF_API_KEY],
                user_input[CONF_LATITUDE],
                user_input[CONF_LONGITUDE],
                user_input[CONF_LANGUAGE],
            )
            try:
                await client.async_get_forecast()
            except FahrradwetterApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_LATITUDE]:.5f}_{user_input[CONF_LONGITUDE]:.5f}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(
                {
                    CONF_NAME: DEFAULT_NAME,
                    CONF_LATITUDE: self.hass.config.latitude,
                    CONF_LONGITUDE: self.hass.config.longitude,
                    CONF_LANGUAGE: DEFAULT_LANGUAGE,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return FahrradwetterOptionsFlow(config_entry)


class FahrradwetterOptionsFlow(config_entries.OptionsFlow):
    """Handle Fahrradwetter options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        values = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(values),
        )


def _base_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")): str,
            vol.Required(
                CONF_LATITUDE, default=defaults.get(CONF_LATITUDE)
            ): vol.Coerce(float),
            vol.Required(
                CONF_LONGITUDE, default=defaults.get(CONF_LONGITUDE)
            ): vol.Coerce(float),
            vol.Required(
                CONF_LANGUAGE, default=defaults.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            ): str,
        }
    )


def _options_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=15, max=1440)),
            vol.Required(
                CONF_MIN_GOOD_SCORE,
                default=defaults.get(CONF_MIN_GOOD_SCORE, DEFAULT_MIN_GOOD_SCORE),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Required(
                CONF_IDEAL_TEMP_MIN,
                default=defaults.get(CONF_IDEAL_TEMP_MIN, DEFAULT_IDEAL_TEMP_MIN),
            ): vol.Coerce(float),
            vol.Required(
                CONF_IDEAL_TEMP_MAX,
                default=defaults.get(CONF_IDEAL_TEMP_MAX, DEFAULT_IDEAL_TEMP_MAX),
            ): vol.Coerce(float),
            vol.Required(
                CONF_ACCEPTABLE_TEMP_MIN,
                default=defaults.get(
                    CONF_ACCEPTABLE_TEMP_MIN, DEFAULT_ACCEPTABLE_TEMP_MIN
                ),
            ): vol.Coerce(float),
            vol.Required(
                CONF_ACCEPTABLE_TEMP_MAX,
                default=defaults.get(
                    CONF_ACCEPTABLE_TEMP_MAX, DEFAULT_ACCEPTABLE_TEMP_MAX
                ),
            ): vol.Coerce(float),
            vol.Required(
                CONF_MAX_RAIN,
                default=defaults.get(CONF_MAX_RAIN, DEFAULT_MAX_RAIN),
            ): vol.Coerce(float),
            vol.Required(
                CONF_MAX_POP,
                default=defaults.get(CONF_MAX_POP, DEFAULT_MAX_POP),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            vol.Required(
                CONF_MAX_WIND,
                default=defaults.get(CONF_MAX_WIND, DEFAULT_MAX_WIND),
            ): vol.Coerce(float),
            vol.Required(
                CONF_MAX_GUST,
                default=defaults.get(CONF_MAX_GUST, DEFAULT_MAX_GUST),
            ): vol.Coerce(float),
        }
    )
