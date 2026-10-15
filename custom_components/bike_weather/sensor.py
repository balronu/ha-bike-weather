"""Native sensors for Bike Weather."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPrecipitationDepth,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class BikeDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS = (
    BikeDescription(
        key="assessment",
        translation_key="assessment",
        icon="mdi:bike",
        value_fn=lambda d: d["classic"].status,
    ),
    BikeDescription(
        key="score",
        translation_key="score",
        icon="mdi:gauge",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d["score"].score,
    ),
    BikeDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda d: d["current"].temperature_c,
    ),
    BikeDescription(
        key="wind",
        translation_key="wind",
        icon="mdi:weather-windy",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        value_fn=lambda d: d["current"].wind_kmh,
    ),
    BikeDescription(
        key="rain",
        translation_key="rain",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        value_fn=lambda d: d["current"].precipitation_mm,
    ),
    BikeDescription(
        key="data_quality",
        translation_key="data_quality",
        icon="mdi:database-check",
        value_fn=lambda d: d["quality"],
    ),
    BikeDescription(
        key="active_source",
        translation_key="active_source",
        icon="mdi:source-branch",
        value_fn=lambda d: ", ".join(d["active_sources"]) or None,
    ),
    BikeDescription(
        key="last_success",
        translation_key="last_success",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:update",
        value_fn=lambda d: d["last_success"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BikeWeatherSensor(coordinator, entry, description) for description in SENSORS
    )


class BikeWeatherSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Bike Weather",
        )

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if self.entity_description.key in {"assessment", "score"}:
            assessment = data["score"]
            return {
                "classic": data["classic"].status,
                "score": assessment.score,
                "reasons": list(assessment.reasons),
            }
        if self.entity_description.key == "data_quality":
            return {
                "errors": data["errors"],
                "forecast_coverage": data["forecast_coverage"],
            }
        return {}
