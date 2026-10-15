"""Config and options flows for Bike Weather."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import *


class BikeWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a provider-neutral Bike Weather entry."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_PROVIDER) == PROVIDER_NONE and not user_input.get(
                CONF_LOCAL_ENABLED
            ):
                errors["base"] = "no_source"
            elif user_input.get(
                CONF_PROVIDER
            ) == PROVIDER_OPENWEATHER and not user_input.get(CONF_API_KEY):
                errors["base"] = "api_key_required"
            else:
                await self.async_set_unique_id(user_input[CONF_NAME].strip().lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(self.hass),
            errors=errors,
            description_placeholders=_suggestions(self.hass),
        )

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
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(values, self.config_entry.hass.config.language),
            description_placeholders=_suggestions(self.config_entry.hass),
        )


def _entity(domain: str, device_class: str | None = None):
    config = {"domain": domain}
    if device_class:
        config["device_class"] = device_class
    return EntitySelector(EntitySelectorConfig(**config))


def _provider_selector(language: str = "de"):
    labels = {
        "de": {
            PROVIDER_HA: "Home-Assistant-Wetterintegration",
            PROVIDER_OPENWEATHER: "OpenWeatherMap",
            PROVIDER_NONE: "Kein zusätzlicher Wetteranbieter",
        },
        "en": {
            PROVIDER_HA: "Home Assistant weather integration",
            PROVIDER_OPENWEATHER: "OpenWeatherMap",
            PROVIDER_NONE: "No additional weather provider",
        },
    }.get(language.split("-")[0], {
        PROVIDER_HA: "Home Assistant weather integration",
        PROVIDER_OPENWEATHER: "OpenWeatherMap",
        PROVIDER_NONE: "No additional weather provider",
    })
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                {"value": key, "label": labels[key]}
                for key in (PROVIDER_HA, PROVIDER_OPENWEATHER, PROVIDER_NONE)
            ],
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


def _suggestions(hass):
    def pick(kind):
        candidates = []
        for state in hass.states.async_all("sensor"):
            unit = str(state.attributes.get("unit_of_measurement", "")).lower()
            device_class = state.attributes.get("device_class")
            if kind == "temperature" and (device_class == "temperature" or unit in {"°c", "°f", "c", "f"}) or kind == "wind" and (device_class == "wind_speed" or unit in {"km/h", "m/s", "mph"}) or kind == "rain" and (device_class in {"precipitation_intensity", "precipitation"} or unit in {"mm/h", "in/h", "mm", "in"}):
                candidates.append(state.entity_id)
        return candidates[0] if len(candidates) == 1 else ""
    return {
        "temperature_entity": pick("temperature"),
        "wind_entity": pick("wind"),
        "rain_entity": pick("rain"),
    }


def _user_schema(hass):
    suggestions = _suggestions(hass)
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=DEFAULT_NAME): vol.All(
                str, vol.Length(min=1, max=64)
            ),
            vol.Required(CONF_PROVIDER, default=DEFAULT_PROVIDER): _provider_selector(hass.config.language),
            vol.Optional(CONF_WEATHER_ENTITY, default=""): _entity("weather"),
            vol.Optional(CONF_API_KEY, default=""): str,
            vol.Required(CONF_LOCAL_ENABLED, default=False): bool,
            vol.Optional(CONF_TEMPERATURE_ENTITY, default=suggestions["temperature_entity"]): _entity("sensor", "temperature"),
            vol.Optional(CONF_WIND_ENTITY, default=suggestions["wind_entity"]): _entity("sensor", "wind_speed"),
            vol.Optional(CONF_RAIN_ENTITY, default=suggestions["rain_entity"]): _entity("sensor"),
            vol.Required(CONF_LATITUDE, default=hass.config.latitude): vol.Coerce(
                float
            ),
            vol.Required(CONF_LONGITUDE, default=hass.config.longitude): vol.Coerce(
                float
            ),
        }
    )


def _options_schema(values, language: str = "de"):
    return vol.Schema(
        {
            vol.Required(
                CONF_PROVIDER, default=values.get(CONF_PROVIDER, DEFAULT_PROVIDER)
            ): _provider_selector(language),
            vol.Optional(
                CONF_WEATHER_ENTITY, default=values.get(CONF_WEATHER_ENTITY, "")
            ): _entity("weather"),
            vol.Optional(CONF_API_KEY, default=values.get(CONF_API_KEY, "")): str,
            vol.Required(
                CONF_LOCAL_ENABLED, default=values.get(CONF_LOCAL_ENABLED, False)
            ): bool,
            vol.Optional(
                CONF_TEMPERATURE_ENTITY, default=values.get(CONF_TEMPERATURE_ENTITY, "")
            ): _entity("sensor", "temperature"),
            vol.Optional(
                CONF_WIND_ENTITY, default=values.get(CONF_WIND_ENTITY, "")
            ): _entity("sensor", "wind_speed"),
            vol.Optional(
                CONF_RAIN_ENTITY, default=values.get(CONF_RAIN_ENTITY, "")
            ): _entity("sensor"),
            vol.Required(
                CONF_REFRESH_MINUTES,
                default=values.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            vol.Required(
                CONF_MAX_AGE_MINUTES,
                default=values.get(CONF_MAX_AGE_MINUTES, DEFAULT_MAX_AGE_MINUTES),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            vol.Required(
                CONF_MIN_TEMPERATURE,
                default=values.get(CONF_MIN_TEMPERATURE, DEFAULT_MIN_TEMPERATURE),
            ): vol.Coerce(float),
            vol.Required(
                CONF_MAX_WIND, default=values.get(CONF_MAX_WIND, DEFAULT_MAX_WIND)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=300)),
            vol.Required(
                CONF_MAX_RAIN, default=values.get(CONF_MAX_RAIN, DEFAULT_MAX_RAIN)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
            vol.Required(
                CONF_MIN_SCORE, default=values.get(CONF_MIN_SCORE, DEFAULT_MIN_SCORE)
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            vol.Required(
                CONF_RIDE_START, default=values.get(CONF_RIDE_START, DEFAULT_RIDE_START)
            ): str,
            vol.Required(
                CONF_RIDE_DURATION,
                default=values.get(CONF_RIDE_DURATION, DEFAULT_RIDE_DURATION),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
        }
    )
