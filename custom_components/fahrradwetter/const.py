"""Constants for the Fahrradwetter integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "fahrradwetter"

CONF_API_KEY = "api_key"
CONF_LANGUAGE = "language"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MIN_GOOD_SCORE = "min_good_score"
CONF_IDEAL_TEMP_MIN = "ideal_temp_min"
CONF_IDEAL_TEMP_MAX = "ideal_temp_max"
CONF_ACCEPTABLE_TEMP_MIN = "acceptable_temp_min"
CONF_ACCEPTABLE_TEMP_MAX = "acceptable_temp_max"
CONF_MAX_RAIN = "max_rain"
CONF_MAX_POP = "max_pop"
CONF_MAX_WIND = "max_wind"
CONF_MAX_GUST = "max_gust"

DEFAULT_NAME = "Fahrradwetter"
DEFAULT_LANGUAGE = "de"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_MIN_GOOD_SCORE = 70
DEFAULT_IDEAL_TEMP_MIN = 12.0
DEFAULT_IDEAL_TEMP_MAX = 24.0
DEFAULT_ACCEPTABLE_TEMP_MIN = 5.0
DEFAULT_ACCEPTABLE_TEMP_MAX = 30.0
DEFAULT_MAX_RAIN = 0.3
DEFAULT_MAX_POP = 40
DEFAULT_MAX_WIND = 7.0
DEFAULT_MAX_GUST = 11.0

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL)

OPENWEATHERMAP_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
