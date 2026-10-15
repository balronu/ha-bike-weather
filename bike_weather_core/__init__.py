"""Provider-neutral offline core for Bike Weather.

The package intentionally has no Home Assistant or network dependency.  The
future HA adapter can translate Config Entries and provider payloads into these
models without coupling scoring to entity IDs or Recorder state.
"""

from .models import (
    DataQuality,
    ForecastSlot,
    RideAssessment,
    RideProfile,
    RideWindow,
    WeatherObservation,
    WeatherSource,
)
from .normalize import (
    choose_metric_observations,
    from_ha_forecast,
    from_ha_weather_state,
    from_openweather,
    normalize_rain_rate_mmh,
    normalize_temperature_c,
    normalize_wind_kmh,
)
from .scoring import assess_classic, assess_score
from .windows import assess_window, find_alternative_starts

__all__ = [
    "DataQuality",
    "ForecastSlot",
    "RideAssessment",
    "RideProfile",
    "RideWindow",
    "WeatherObservation",
    "WeatherSource",
    "assess_classic",
    "assess_score",
    "assess_window",
    "choose_metric_observations",
    "find_alternative_starts",
    "from_ha_forecast",
    "from_ha_weather_state",
    "from_openweather",
    "normalize_rain_rate_mmh",
    "normalize_temperature_c",
    "normalize_wind_kmh",
]
