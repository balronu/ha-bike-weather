"""Config and options flows for Bike Weather."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import *

class BikeWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a provider-neutral Bike Weather entry."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_PROVIDER) == PROVIDER_NONE and not user_input.get(CONF_LOCAL_ENABLED):
                errors["base"] = "no_source"
            elif user_input.get(CONF_PROVIDER) == PROVIDER_OPENWEATHER and not user_input.get(CONF_API_KEY):
                errors["base"] = "api_key_required"
            else:
                await self.async_set_unique_id(user_input[CONF_NAME].strip().lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        return self.async_show_form(step_id="user", data_schema=_user_schema(self.hass), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BikeWeatherOptionsFlow(config_entry)

class BikeWeatherOptionsFlow(config_entries.OptionsFlow):
    """Change sources and profile without changing the entry identity."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        values = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_options_schema(values))

def _user_schema(hass):
    return vol.Schema({
        vol.Required(CONF_NAME, default=DEFAULT_NAME): vol.All(str, vol.Length(min=1, max=64)),
        vol.Required(CONF_PROVIDER, default=DEFAULT_PROVIDER): vol.In([PROVIDER_HA, PROVIDER_OPENWEATHER, PROVIDER_NONE]),
        vol.Optional(CONF_WEATHER_ENTITY, default=""): str,
        vol.Optional(CONF_API_KEY, default=""): str,
        vol.Required(CONF_LOCAL_ENABLED, default=False): bool,
        vol.Optional(CONF_TEMPERATURE_ENTITY, default=""): str,
        vol.Optional(CONF_WIND_ENTITY, default=""): str,
        vol.Optional(CONF_RAIN_ENTITY, default=""): str,
        vol.Required(CONF_LATITUDE, default=hass.config.latitude): vol.Coerce(float),
        vol.Required(CONF_LONGITUDE, default=hass.config.longitude): vol.Coerce(float),
    })

def _options_schema(values):
    return vol.Schema({
        vol.Required(CONF_PROVIDER, default=values.get(CONF_PROVIDER, DEFAULT_PROVIDER)): vol.In([PROVIDER_HA, PROVIDER_OPENWEATHER, PROVIDER_NONE]),
        vol.Optional(CONF_WEATHER_ENTITY, default=values.get(CONF_WEATHER_ENTITY, "")): str,
        vol.Optional(CONF_API_KEY, default=values.get(CONF_API_KEY, "")): str,
        vol.Required(CONF_LOCAL_ENABLED, default=values.get(CONF_LOCAL_ENABLED, False)): bool,
        vol.Optional(CONF_TEMPERATURE_ENTITY, default=values.get(CONF_TEMPERATURE_ENTITY, "")): str,
        vol.Optional(CONF_WIND_ENTITY, default=values.get(CONF_WIND_ENTITY, "")): str,
        vol.Optional(CONF_RAIN_ENTITY, default=values.get(CONF_RAIN_ENTITY, "")): str,
        vol.Required(CONF_REFRESH_MINUTES, default=values.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
        vol.Required(CONF_MAX_AGE_MINUTES, default=values.get(CONF_MAX_AGE_MINUTES, DEFAULT_MAX_AGE_MINUTES)): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
        vol.Required(CONF_MIN_TEMPERATURE, default=values.get(CONF_MIN_TEMPERATURE, DEFAULT_MIN_TEMPERATURE)): vol.Coerce(float),
        vol.Required(CONF_MAX_WIND, default=values.get(CONF_MAX_WIND, DEFAULT_MAX_WIND)): vol.All(vol.Coerce(float), vol.Range(min=0, max=300)),
        vol.Required(CONF_MAX_RAIN, default=values.get(CONF_MAX_RAIN, DEFAULT_MAX_RAIN)): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
        vol.Required(CONF_MIN_SCORE, default=values.get(CONF_MIN_SCORE, DEFAULT_MIN_SCORE)): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Required(CONF_RIDE_START, default=values.get(CONF_RIDE_START, DEFAULT_RIDE_START)): str,
        vol.Required(CONF_RIDE_DURATION, default=values.get(CONF_RIDE_DURATION, DEFAULT_RIDE_DURATION)): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
    })
