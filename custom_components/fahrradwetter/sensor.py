"""Sensor platform for Fahrradwetter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FahrradwetterCoordinator


@dataclass(frozen=True, kw_only=True)
class FahrradwetterSensorEntityDescription(SensorEntityDescription):
    """Description for Fahrradwetter sensors."""

    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


SENSORS: tuple[FahrradwetterSensorEntityDescription, ...] = (
    FahrradwetterSensorEntityDescription(
        key="recommendation",
        translation_key="recommendation",
        icon="mdi:bike",
        value_fn=lambda data: data["recommendation"],
        attr_fn=lambda data: {
            "score": data["score"],
            "reason": data["reason"],
            "next_good_slot": _serialize_slot(data.get("next_good_slot")),
            "today_best_slot": _serialize_slot(data.get("today_best_slot")),
            "tomorrow_best_slot": _serialize_slot(data.get("tomorrow_best_slot")),
        },
    ),
    FahrradwetterSensorEntityDescription(
        key="score",
        translation_key="score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        value_fn=lambda data: data["score"],
        attr_fn=lambda data: {"reason": data["reason"]},
    ),
    FahrradwetterSensorEntityDescription(
        key="next_good_time",
        translation_key="next_good_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-clock",
        value_fn=lambda data: _slot_datetime(data.get("next_good_slot")),
        attr_fn=lambda data: data.get("next_good_slot") or {},
    ),
    FahrradwetterSensorEntityDescription(
        key="today_best_score",
        translation_key="today_best_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-partly-cloudy",
        value_fn=lambda data: _slot_value(data.get("today_best_slot"), "score"),
        attr_fn=lambda data: data.get("today_best_slot") or {},
    ),
    FahrradwetterSensorEntityDescription(
        key="tomorrow_best_score",
        translation_key="tomorrow_best_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-sunny",
        value_fn=lambda data: _slot_value(data.get("tomorrow_best_slot"), "score"),
        attr_fn=lambda data: data.get("tomorrow_best_slot") or {},
    ),
    FahrradwetterSensorEntityDescription(
        key="forecast_slots",
        translation_key="forecast_slots",
        icon="mdi:code-json",
        value_fn=lambda data: data["raw_count"],
        attr_fn=lambda data: {
            "slots": [_serialize_slot(slot) for slot in data.get("forecast_slots", [])]
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fahrradwetter sensors."""
    coordinator: FahrradwetterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        FahrradwetterSensor(coordinator, entry, description)
        for description in SENSORS
    )


class FahrradwetterSensor(
    CoordinatorEntity[FahrradwetterCoordinator], SensorEntity
):
    """Representation of a Fahrradwetter sensor."""

    entity_description: FahrradwetterSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FahrradwetterCoordinator,
        entry: ConfigEntry,
        description: FahrradwetterSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Fahrradwetter",
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        if self.entity_description.attr_fn is None:
            return {}
        return self.entity_description.attr_fn(self.coordinator.data)


def _slot_value(slot: dict[str, Any] | None, key: str) -> Any:
    if slot is None:
        return None
    return slot.get(key)


def _slot_datetime(slot: dict[str, Any] | None) -> datetime | None:
    if slot is None:
        return None
    return slot.get("datetime")


def _serialize_slot(slot: dict[str, Any] | None) -> dict[str, Any] | None:
    if slot is None:
        return None
    result = dict(slot)
    if isinstance(result.get("datetime"), datetime):
        result["datetime"] = result["datetime"].isoformat()
    return result
