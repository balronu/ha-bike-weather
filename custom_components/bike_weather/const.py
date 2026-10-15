"""Constants for Bike Weather."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "bike_weather"
PLATFORMS = ["sensor"]
CONF_NAME = "name"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_PROVIDER = "provider"
CONF_API_KEY = "api_key"
CONF_LOCAL_ENABLED = "local_enabled"
CONF_TEMPERATURE_ENTITY = "temperature_entity"
CONF_WIND_ENTITY = "wind_entity"
CONF_RAIN_ENTITY = "rain_entity"
CONF_RAIN_RATE_ENTITY = CONF_RAIN_ENTITY
CONF_PROFILE = "profile"
CONF_OPTIONS = "options"
CONF_MAX_AGE_MINUTES = "max_age_minutes"
CONF_REFRESH_MINUTES = "refresh_minutes"
CONF_MIN_TEMPERATURE = "min_temperature_c"
CONF_MAX_WIND = "max_wind_kmh"
CONF_MAX_RAIN = "max_rain_mm"
CONF_MIN_SCORE = "min_score"
CONF_RIDE_START = "ride_start"
CONF_RIDE_DURATION = "ride_duration_minutes"
CONF_TIMEZONE = "timezone"
PROVIDER_HA = "ha_weather"
PROVIDER_OPENWEATHER = "openweathermap"
PROVIDER_NONE = "none"
DEFAULT_NAME = "Bike Weather"
DEFAULT_PROVIDER = PROVIDER_HA
DEFAULT_MAX_AGE_MINUTES = 90
DEFAULT_REFRESH_MINUTES = 15
DEFAULT_MIN_TEMPERATURE = 10.0
DEFAULT_MAX_WIND = 15.0
DEFAULT_MAX_RAIN = 0.0
DEFAULT_MIN_SCORE = 70
DEFAULT_RIDE_START = "07:30"
DEFAULT_RIDE_DURATION = 60
DEFAULT_PROFILE = "standard"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=DEFAULT_REFRESH_MINUTES)
CARD_URL = "/bike_weather/bike-weather-card.js"
WS_CARD_DATA = "bike_weather/card_data"
CARD_VERSION = "0.1.0-beta.3"
