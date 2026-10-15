"""Ride-window evaluation over arbitrary forecast resolutions."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, timedelta, tzinfo

from .models import ForecastSlot, RideAssessment, RideProfile, RideWindow
from .scoring import assess_classic, assess_score, merge_assessments


def _overlaps(slot: ForecastSlot, start: datetime, end: datetime) -> bool:
    return slot.ends_at > start and slot.starts_at < end


def assess_window(
    window: RideWindow,
    slots: Iterable[ForecastSlot],
    *,
    on_date: date,
    tz: tzinfo,
    profile: RideProfile | None = None,
    mode: str = "score",
) -> RideAssessment:
    """Assess every forecast interval touched by a ride window."""
    resolved = window.resolve(on_date, tz)
    profile = profile or RideProfile()
    if resolved is None:
        return merge_assessments((), window=None)
    start, end = resolved
    relevant = tuple(slot for slot in slots if _overlaps(slot, start, end))
    assess = assess_score if mode == "score" else assess_classic
    return merge_assessments(
        (assess(slot, profile) for slot in relevant), window=(start, end)
    )


def find_alternative_starts(
    slots: Iterable[ForecastSlot],
    *,
    search_start: datetime,
    search_end: datetime,
    duration: timedelta,
    step: timedelta,
    profile: RideProfile | None = None,
    mode: str = "score",
    minimum_score: int = 70,
) -> tuple[tuple[datetime, RideAssessment], ...]:
    """Return candidate starts using only real forecast slots.

    No interpolation is performed.  A candidate is evaluated only when its
    whole interval is covered by forecast slots; this avoids false precision.
    """
    if search_start.tzinfo is None or search_end.tzinfo is None:
        raise ValueError("search bounds must be timezone-aware")
    if duration <= timedelta(0) or step <= timedelta(0):
        raise ValueError("duration and step must be positive")
    slots = tuple(sorted(slots, key=lambda slot: slot.starts_at))
    profile = profile or RideProfile()
    result: list[tuple[datetime, RideAssessment]] = []
    current = search_start
    while current + duration <= search_end:
        end = current + duration
        relevant = tuple(slot for slot in slots if _overlaps(slot, current, end))
        if relevant and _covered_without_gap(relevant, current, end):
            assess = assess_score if mode == "score" else assess_classic
            combined = merge_assessments(
                (assess(slot, profile) for slot in relevant), window=(current, end)
            )
            if combined.status == "good" and (combined.score or 0) >= minimum_score:
                result.append((current, combined))
        current += step
    return tuple(result)


def _covered_without_gap(
    slots: tuple[ForecastSlot, ...], start: datetime, end: datetime
) -> bool:
    cursor = start
    for slot in slots:
        if slot.starts_at > cursor:
            return False
        cursor = max(cursor, slot.ends_at)
        if cursor >= end:
            return True
    return cursor >= end
