"""Classic and provisional Bike Weather scoring."""

from __future__ import annotations

from typing import Iterable

from .models import DataQuality, ForecastSlot, RideAssessment, RideProfile, WeatherObservation


def _quality(values: Iterable[object | None]) -> DataQuality:
    values = tuple(values)
    return DataQuality.GOOD if all(value is not None for value in values) else DataQuality.PARTIAL


def assess_classic(
    observation: WeatherObservation | ForecastSlot,
    profile: RideProfile = RideProfile(),
) -> RideAssessment:
    """Preserve the reference strict operators without treating missing as zero."""
    values = (observation.temperature_c, observation.wind_kmh, observation.precipitation_mm)
    quality = _quality(values)
    source_ids = (observation.source.source_id,)
    if quality != DataQuality.GOOD:
        return RideAssessment("unknown", None, quality, source_ids, ("Bewertungsdaten unvollständig",))
    good = (
        observation.temperature_c > profile.min_temperature_c
        and observation.wind_kmh < profile.max_wind_kmh
        and observation.precipitation_mm <= profile.max_rain_mm
    )
    return RideAssessment(
        "good" if good else "bad", 100 if good else 0, quality, source_ids,
        ("Grenzwerte erfüllt" if good else "Mindestens ein Grenzwert verletzt",),
    )


def _band(value: float | None, low: float, high: float, ideal_low: float, ideal_high: float) -> float | None:
    if value is None:
        return None
    if ideal_low <= value <= ideal_high:
        return 100.0
    if value < low or value > high:
        return 0.0
    if value < ideal_low:
        return 100.0 * (value - low) / max(ideal_low - low, 0.001)
    return 100.0 * (high - value) / max(high - ideal_high, 0.001)


def _lower_is_better(value: float | None, limit: float, hard_limit: float) -> float | None:
    if value is None:
        return None
    if value <= limit:
        return 100.0
    if value >= hard_limit:
        return 0.0
    return 100.0 * (hard_limit - value) / (hard_limit - limit)


def assess_score(
    observation: WeatherObservation | ForecastSlot,
    profile: RideProfile = RideProfile(),
) -> RideAssessment:
    """Compute the provisional weighted score conservatively.

    Missing factors are excluded from the numerator but also reduce the score
    by the missing weight through the confidence multiplier.  Thus incomplete
    data cannot produce an artificially positive 100.
    """
    scores = {
        "temperature": _band(observation.feels_like_c if observation.feels_like_c is not None else observation.temperature_c,
                             profile.acceptable_temperature_min_c,
                             profile.acceptable_temperature_max_c,
                             profile.ideal_temperature_min_c,
                             profile.ideal_temperature_max_c),
        "wind": _lower_is_better(observation.wind_kmh, profile.max_wind_kmh, profile.max_wind_kmh * 2.5),
        "gust": _lower_is_better(observation.gust_kmh, profile.max_gust_kmh, profile.max_gust_kmh * 1.75),
        "rain": _lower_is_better(observation.precipitation_mm, profile.max_rain_mm, max(profile.max_rain_mm + 3.0, 3.0)),
        "probability": _lower_is_better(observation.precipitation_probability_pct,
                                         profile.max_precipitation_probability_pct, 100.0),
        "feels_like": _band(observation.feels_like_c, profile.acceptable_temperature_min_c,
                             profile.acceptable_temperature_max_c, profile.ideal_temperature_min_c,
                             profile.ideal_temperature_max_c),
    }
    weights = {
        "temperature": profile.weight_temperature, "wind": profile.weight_wind,
        "gust": profile.weight_gust, "rain": profile.weight_rain,
        "probability": profile.weight_probability, "feels_like": profile.weight_feels_like,
    }
    total = sum(weights.values())
    used = sum(weights[name] for name, value in scores.items() if value is not None)
    raw = sum(weights[name] * value for name, value in scores.items() if value is not None)
    score = round(max(0.0, min(100.0, raw / total))) if total else 0
    reasons = tuple(name for name, value in scores.items() if value is None)
    if not reasons:
        reasons = ("Alle Score-Faktoren vorhanden",)
    quality = DataQuality.GOOD if used == total else DataQuality.PARTIAL
    return RideAssessment(
        "good" if score >= 70 and quality == DataQuality.GOOD else "unknown" if quality != DataQuality.GOOD else "bad",
        score, quality, (observation.source.source_id,), reasons, scores, used,
    )


def merge_assessments(assessments: Iterable[RideAssessment], window=None) -> RideAssessment:
    """Conservatively combine intervals: the weakest score/status wins."""
    items = tuple(assessments)
    if not items:
        return RideAssessment("unknown", None, DataQuality.UNAVAILABLE, (), ("Keine Prognoseintervalle",), window=window)
    if any(item.status == "unknown" for item in items):
        status = "unknown"
    else:
        status = "good" if all(item.status == "good" for item in items) else "bad"
    scores = [item.score for item in items if item.score is not None]
    quality = DataQuality.GOOD if all(item.quality == DataQuality.GOOD for item in items) else DataQuality.PARTIAL
    return RideAssessment(status, min(scores) if scores else None, quality,
                          tuple(dict.fromkeys(source for item in items for source in item.source_ids)),
                          tuple(dict.fromkeys(reason for item in items for reason in item.reasons)),
                          window=window)
