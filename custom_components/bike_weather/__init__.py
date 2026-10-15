"""Bike Weather Home Assistant integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .api import async_setup_websocket
from .const import CARD_URL, CARD_VERSION, DOMAIN, PLATFORMS
from .coordinator import BikeWeatherCoordinator

_CARD_REGISTERED = "card_registered"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the card bundle and authenticated data endpoint once."""
    if not hass.data.get(DOMAIN, {}).get(_CARD_REGISTERED):
        www = Path(__file__).parent / "www"
        # The fallback keeps this usable across the 2026.x static-path API transition.
        if hasattr(hass.http, "register_static_path"):
            hass.http.register_static_path(
                CARD_URL, str(www / "bike-weather-card.js"), cache_headers=True
            )
        add_extra_js_url(hass, f"{CARD_URL}?v={CARD_VERSION}")
        await async_setup_websocket(hass)
        hass.data.setdefault(DOMAIN, {})[_CARD_REGISTERED] = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one isolated config entry."""
    coordinator = BikeWeatherCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one entry and its entities."""
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
