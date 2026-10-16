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
CONF_RIDE_OUTBOUND_ENABLED = "ride_outbound_enabled"
CONF_RIDE_OUTBOUND_NAME = "ride_outbound_name"
CONF_RIDE_OUTBOUND_START = "ride_outbound_start"
CONF_RIDE_OUTBOUND_DURATION = "ride_outbound_duration_minutes"
CONF_RIDE_OUTBOUND_WEEKDAYS = "ride_outbound_weekdays"
CONF_RIDE_RETURN_ENABLED = "ride_return_enabled"
CONF_RIDE_RETURN_NAME = "ride_return_name"
CONF_RIDE_RETURN_START = "ride_return_start"
CONF_RIDE_RETURN_DURATION = "ride_return_duration_minutes"
CONF_RIDE_RETURN_WEEKDAYS = "ride_return_weekdays"
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
DEFAULT_RIDE_START = "15:00"
DEFAULT_RIDE_DURATION = 60
DEFAULT_RIDE_OUTBOUND_ENABLED = False
DEFAULT_RIDE_OUTBOUND_NAME = "Hinfahrt"
DEFAULT_RIDE_OUTBOUND_START = "07:30:00"
DEFAULT_RIDE_RETURN_ENABLED = False
DEFAULT_RIDE_RETURN_NAME = "Rückfahrt"
DEFAULT_RIDE_RETURN_START = "13:30:00"
DEFAULT_RIDE_DURATION_OPTIONS = (15, 30, 45, 60, 90, 120, 180, 240)
DEFAULT_RIDE_WEEKDAYS = (0, 1, 2, 3, 4)
TOMORROW_START_HOUR = 6
TOMORROW_END_HOUR = 22
DEFAULT_PROFILE = "standard"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=DEFAULT_REFRESH_MINUTES)
CARD_URL = "/bike_weather/bike-weather-card.js"
WS_CARD_DATA = "bike_weather/card_data"
WS_SPONTANEOUS_RIDE = "bike_weather/spontaneous_ride"
WS_LIST_ENTRIES = "bike_weather/list_entries"
WS_PLANNING_DATA = "bike_weather/planning_data"
CARD_VERSION = "0.3.0"
