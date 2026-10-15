"""Regression contracts for the Home Assistant 2026.10 Options Flow API."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
FLOW = ROOT / "custom_components" / "bike_weather" / "config_flow.py"


def _classes() -> dict[str, ast.ClassDef]:
    tree = ast.parse(FLOW.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def test_options_factory_uses_home_assistant_managed_entry_property():
    """HA now injects config_entry; custom assignment raises AttributeError."""
    source = FLOW.read_text(encoding="utf-8")
    assert "return BikeWeatherOptionsFlow()" in source

    options_flow = _classes()["BikeWeatherOptionsFlow"]
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "__init__"
        for node in options_flow.body
    )

    class ModernOptionsFlow:
        """Small model of HA's read-only OptionsFlow.config_entry property."""

        @property
        def config_entry(self):
            return object()

    with pytest.raises(AttributeError, match="has no setter"):
        ModernOptionsFlow().config_entry = object()


def test_beta2_data_with_empty_options_keeps_all_option_defaults():
    """A Beta-2 entry is valid when persisted options are empty."""
    source = FLOW.read_text(encoding="utf-8")
    beta2_data = {
        "provider": "ha_weather",
        "weather_entity": "weather.home",
        "local_enabled": False,
    }
    beta2_options: dict[str, object] = {}
    values = {**beta2_data, **beta2_options}
    assert values["weather_entity"] == "weather.home"
    assert "refresh_minutes" not in values

    options_flow = _classes()["BikeWeatherOptionsFlow"]
    init_step = next(
        node
        for node in options_flow.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_step_init"
    )
    attributes = {
        node.attr
        for node in ast.walk(init_step)
        if isinstance(node, ast.Attribute)
    }
    assert "config_entry" in attributes
    assert "options" in source
    assert "values = {**self.config_entry.data, **self.config_entry.options}" in source
    assert "default=values.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)" in source
    assert "default=values.get(CONF_MAX_AGE_MINUTES, DEFAULT_MAX_AGE_MINUTES)" in source
