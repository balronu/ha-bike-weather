"""Offline simulation of the explicitly scoped Bike Weather hot cutover."""

from __future__ import annotations

from copy import deepcopy

OLD_REST_IDS = {"sensor.raw_fahrrad_forecast", "sensor.fahrradwetter_aktuell"}
OLD_TEMPLATE_IDS = {
    "sensor.fahrradwetter_heute",
    "sensor.fahrradwetter_naechster_block",
    "sensor.fahrradwetter_morgen_06_00",
    "sensor.fahrradwetter_morgen_15_00",
}


def _cutover(config: dict) -> dict:
    """Apply only exact, pre-identified records to an in-memory fixture."""
    result = deepcopy(config)
    result["yaml_entities"] = [
        entity
        for entity in result["yaml_entities"]
        if entity["entity_id"] not in OLD_REST_IDS | OLD_TEMPLATE_IDS
    ]
    result["lovelace_cards"] = [
        card for card in result["lovelace_cards"] if card["card_id"] != "old-bike-weather"
    ]
    result["lovelace_cards"].append(
        {"card_id": "bike-weather", "type": "custom:bike-weather-card"}
    )
    result["integration"] = {"domain": "bike_weather", "version": "0.1.0-beta.2"}
    return result


def test_cutover_removes_only_exact_legacy_records_and_keeps_shared_resources():
    fixture = {
        "yaml_entities": [
            *({"entity_id": value, "kind": "bike-weather"} for value in OLD_REST_IDS),
            *({"entity_id": value, "kind": "bike-weather"} for value in OLD_TEMPLATE_IDS),
            {"entity_id": "sensor.shared_openweathermap", "kind": "shared"},
        ],
        "lovelace_cards": [
            {"card_id": "old-bike-weather", "type": "custom:old-card"},
            {"card_id": "shared-weather", "type": "weather-forecast"},
        ],
        "lovelace_resources": [
            {"url": "/hacsfiles/mushroom.js"},
            {"url": "/hacsfiles/button-card.js"},
            {"url": "/hacsfiles/vertical-stack-in-card.js"},
        ],
    }

    result = _cutover(fixture)

    assert {item["entity_id"] for item in result["yaml_entities"]} == {
        "sensor.shared_openweathermap"
    }
    assert {item["card_id"] for item in result["lovelace_cards"]} == {
        "shared-weather",
        "bike-weather",
    }
    assert result["lovelace_resources"] == fixture["lovelace_resources"]


def test_rollback_restores_the_complete_saved_fixture():
    fixture = {
        "yaml_entities": [{"entity_id": "sensor.raw_fahrrad_forecast"}],
        "lovelace_cards": [{"card_id": "old-bike-weather"}],
        "lovelace_resources": [{"url": "/hacsfiles/mushroom.js"}],
    }
    backup = deepcopy(fixture)
    cutover = _cutover(fixture)

    restored = deepcopy(backup)

    assert cutover != fixture
    assert restored == fixture
