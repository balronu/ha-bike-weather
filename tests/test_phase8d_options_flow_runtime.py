"""Behavioral Options Flow coverage with a small HA 2026.10-compatible harness.

The repository CI does not install the full Home Assistant test fixture.  This
test therefore loads the real integration flow against minimal stand-ins for
the HA flow and selector APIs, exercising schema construction, defaults,
validation, save/reopen behavior, and sensor suggestions without pretending
to be a full Home Assistant runtime test.
"""

from __future__ import annotations

import asyncio
import importlib
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import voluptuous as vol

ROOT = Path(__file__).parents[1]
FLOW_MODULE = "custom_components.bike_weather.config_flow"


class _SelectorConfig:
    def __init__(self, **config):
        self.config = config


class _Selector:
    def __init__(self, config):
        self.config = config.config

    def __call__(self, value):
        return value


class _FlowBase:
    def __init__(self):
        self.hass = None
        self._config_entry = None

    @property
    def config_entry(self):
        return self._config_entry

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}


class _ConfigFlowBase(_FlowBase):
    def __init_subclass__(cls, **kwargs):
        # The real HA base consumes the domain keyword in class definition.
        return super().__init_subclass__()


def _install_home_assistant_stubs(monkeypatch):
    homeassistant = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigFlow = _ConfigFlowBase
    config_entries.OptionsFlow = _FlowBase

    const = types.ModuleType("homeassistant.const")
    const.CONF_LATITUDE = "latitude"
    const.CONF_LONGITUDE = "longitude"

    core = types.ModuleType("homeassistant.core")
    core.callback = lambda function: function

    selector = types.ModuleType("homeassistant.helpers.selector")
    selector.EntitySelector = _Selector
    selector.EntitySelectorConfig = _SelectorConfig
    selector.SelectSelector = _Selector
    selector.SelectSelectorConfig = _SelectorConfig
    selector.SelectSelectorMode = SimpleNamespace(DROPDOWN="dropdown")

    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    for name, module in {
        "homeassistant": homeassistant,
        "homeassistant.config_entries": config_entries,
        "homeassistant.const": const,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.selector": selector,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)

    package = types.ModuleType("custom_components.bike_weather")
    package.__path__ = [str(ROOT / "custom_components" / "bike_weather")]
    monkeypatch.setitem(sys.modules, "custom_components.bike_weather", package)
    sys.modules.pop(FLOW_MODULE, None)


@pytest.fixture
def flow_module(monkeypatch):
    _install_home_assistant_stubs(monkeypatch)
    return importlib.import_module(FLOW_MODULE)


class _States:
    def __init__(self, states):
        self._states = states

    def async_all(self, domain):
        return [state for state in self._states if state.entity_id.split(".", 1)[0] == domain]


def _hass():
    return SimpleNamespace(
        config=SimpleNamespace(language="de-DE", latitude=52.1, longitude=13.2),
        states=_States(
            [
                SimpleNamespace(
                    entity_id="sensor.gw1100a_outdoor_temperature",
                    attributes={"device_class": "temperature", "unit_of_measurement": "°C"},
                ),
                SimpleNamespace(
                    entity_id="sensor.gw1100a_wind",
                    attributes={"device_class": "wind_speed", "unit_of_measurement": "km/h"},
                ),
                SimpleNamespace(
                    entity_id="sensor.gw1100a_rain_rate",
                    attributes={"device_class": "precipitation_intensity", "unit_of_measurement": "mm/h"},
                ),
            ]
        ),
    )


def _entry(data=None, options=None):
    return SimpleNamespace(
        entry_id="entry-bike-weather",
        data=data or {},
        options=options or {},
    )


def _attach(flow, hass, entry):
    flow.hass = hass
    flow._config_entry = entry
    return flow


def test_empty_options_flow_builds_gw1100a_defaults_and_reopens(flow_module):
    """An existing entry with empty options gets usable local sensor defaults."""
    hass = _hass()
    entry = _entry(
        {
            flow_module.CONF_PROVIDER: flow_module.PROVIDER_HA,
            flow_module.CONF_WEATHER_ENTITY: "weather.home",
            flow_module.CONF_LOCAL_ENABLED: False,
        }
    )
    flow = _attach(flow_module.BikeWeatherOptionsFlow(), hass, entry)

    initial = asyncio.run(flow.async_step_init())
    assert initial["type"] == "form"
    normalized = initial["data_schema"]({})
    assert normalized[flow_module.CONF_WEATHER_ENTITY] == "weather.home"
    assert normalized[flow_module.CONF_REFRESH_MINUTES] == 15
    assert normalized[flow_module.CONF_TEMPERATURE_ENTITY] == "sensor.gw1100a_outdoor_temperature"
    assert normalized[flow_module.CONF_WIND_ENTITY] == "sensor.gw1100a_wind"
    assert normalized[flow_module.CONF_RAIN_ENTITY] == "sensor.gw1100a_rain_rate"

    normalized.update(
        {
            flow_module.CONF_LOCAL_ENABLED: True,
            flow_module.CONF_REFRESH_MINUTES: 30,
            flow_module.CONF_MAX_AGE_MINUTES: 120,
        }
    )
    saved = asyncio.run(flow.async_step_init(normalized))
    assert saved["type"] == "create_entry"

    entry.options = saved["data"]
    reopened = _attach(flow_module.BikeWeatherOptionsFlow(), hass, entry)
    reopened_form = asyncio.run(reopened.async_step_init())
    reopened_values = reopened_form["data_schema"]({})
    assert reopened_values[flow_module.CONF_LOCAL_ENABLED] is True
    assert reopened_values[flow_module.CONF_REFRESH_MINUTES] == 30
    assert reopened_values[flow_module.CONF_MAX_AGE_MINUTES] == 120
    assert reopened_values[flow_module.CONF_TEMPERATURE_ENTITY] == "sensor.gw1100a_outdoor_temperature"


def test_options_flow_rejects_empty_source_without_losing_entry(flow_module):
    hass = _hass()
    entry = _entry(
        {
            flow_module.CONF_PROVIDER: flow_module.PROVIDER_HA,
            flow_module.CONF_WEATHER_ENTITY: "weather.home",
            flow_module.CONF_LOCAL_ENABLED: False,
        }
    )
    flow = _attach(flow_module.BikeWeatherOptionsFlow(), hass, entry)
    result = asyncio.run(
        flow.async_step_init(
            {
                flow_module.CONF_PROVIDER: flow_module.PROVIDER_NONE,
                flow_module.CONF_LOCAL_ENABLED: False,
            }
        )
    )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "no_source"}
    assert entry.data[flow_module.CONF_WEATHER_ENTITY] == "weather.home"


def test_entity_selector_config_keeps_domains_and_device_classes(flow_module):
    schema = flow_module._options_schema({}, "en")
    fields = {key.schema if isinstance(key, (vol.Required, vol.Optional)) else key: value for key, value in schema.schema.items()}
    assert fields[flow_module.CONF_TEMPERATURE_ENTITY].config == {
        "domain": "sensor",
        "device_class": "temperature",
    }
    assert fields[flow_module.CONF_WIND_ENTITY].config == {
        "domain": "sensor",
        "device_class": "wind_speed",
    }
    assert fields[flow_module.CONF_RAIN_ENTITY].config == {"domain": "sensor"}
