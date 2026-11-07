"""Independent causal confirmation logic for the X4 validation harness."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from statistics import median

from dnmem.extract_x4 import causal_confirmations as _reference_causal_confirmations
from dnmem.injection_score import _matching
from dnmem.x3_validation_score import (
    _operational_confirmation_metrics,
    score_validation as _x3_score_validation,
)


VISIT_SPAN = 0.15
CONFIRM_MARGIN = 0.5


def _number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _observer(row: dict) -> str:
    return (row.get("obsName") or "").strip().casefold() or row["by"]


def _closed_visits(rows: list[dict], threshold: float) -> list[dict]:
    usable = []
    for position, row in enumerate(rows):
        if row.get("band") != "Vis." or row.get("val") != "V":
            continue
        jd = _number(row.get("JD"))
        magnitude = _number(row.get("mag"))
        if jd is None or magnitude is None:
            continue
        usable.append((jd, str(row.get("obsID", position)), position, row))
    usable.sort(key=lambda item: (item[0], item[1], item[2]))

    by_observer: dict[str, list[tuple[float, str, int, dict]]] = defaultdict(list)
    for item in usable:
        by_observer[_observer(item[3])].append(item)

    closed = []
    for who, own in by_observer.items():
        groups: list[list[tuple[float, str, int, dict]]] = []
        for item in own:
            if groups and item[0] - groups[-1][0][0] <= VISIT_SPAN:
                groups[-1].append(item)
            else:
                groups.append([item])
        for group in groups:
            detections = [_number(item[3].get("mag")) for item in group
                          if str(item[3].get("fainterThan", "0")) != "1"]
            limits = [_number(item[3].get("mag"))
                      for item in group if str(item[3].get("fainterThan", "0")) == "1"]
            if detections:
                level = median(detections)
                label = "B" if level <= threshold else "F"
            elif limits and max(limits) >= threshold:
                level = max(limits)
                label = "F"
            else:
                continue
            first_jd = group[0][0]
            closed.append({
                "closed_at": first_jd + VISIT_SPAN,
                "first_jd": first_jd,
                "night": math.floor(first_jd),
                "observer": who,
                "cls": label,
                "level": level,
            })
    return sorted(closed, key=lambda visit: (visit["closed_at"], visit["observer"]))


def causal_confirmation_emissions(rows: list[dict], threshold: float = 10.0) -> list[dict]:
    """Return immutable X4 causal end-confirmation emissions.

    Visits are available only when their fixed window closes. Equal close times
    are atomic: any bright vote resets faint evidence and suppresses same-time
    faint votes. Strong bright evidence arms a provisional event only after two
    observers, or after one observer has supplied strong visits on two nights.
    """
    threshold = float(threshold)
    if not math.isfinite(threshold):
        raise ValueError("threshold must be finite")

    bright_observers: set[str] = set()
    strong_bright_nights: dict[str, set[int]] = defaultdict(set)
    faint_observers: set[str] = set()
    bright_first_at = None
    last_bright_at = None
    faint_first_at = None
    armed = False
    emissions = []

    def reset() -> None:
        nonlocal bright_first_at, last_bright_at, faint_first_at, armed
        bright_observers.clear()
        strong_bright_nights.clear()
        faint_observers.clear()
        bright_first_at = None
        last_bright_at = None
        faint_first_at = None
        armed = False

    visits = _closed_visits(rows, threshold)
    position = 0
    while position < len(visits):
        close_time = visits[position]["closed_at"]
        end = position + 1
        while end < len(visits) and visits[end]["closed_at"] == close_time:
            end += 1
        batch = visits[position:end]
        position = end

        bright = [visit for visit in batch if visit["cls"] == "B"]
        if bright:
            faint_observers.clear()
            faint_first_at = None
            if not bright_observers:
                bright_first_at = close_time
            bright_observers.update(visit["observer"] for visit in bright)
            last_bright_at = close_time
            for visit in bright:
                if visit["level"] <= threshold - CONFIRM_MARGIN:
                    strong_bright_nights[visit["observer"]].add(visit["night"])
            strong_observer_count = len(strong_bright_nights)
            repeated_night_evidence = any(len(nights) >= 2
                                          for nights in strong_bright_nights.values())
            armed = armed or strong_observer_count >= 2 or repeated_night_evidence
            continue

        strong_faint = [visit for visit in batch
                        if visit["level"] >= threshold + CONFIRM_MARGIN]
        if not strong_faint:
            continue
        if not faint_observers:
            faint_first_at = close_time
        faint_observers.update(visit["observer"] for visit in strong_faint)
        if len(faint_observers) < 2:
            continue

        if armed:
            emissions.append({
                "emission_index": len(emissions),
                "emitted_at": close_time,
                "bright_first_at": bright_first_at,
                "last_bright_at": last_bright_at,
                "faint_first_at": faint_first_at,
                "bright_observer_count": len(bright_observers),
                "strong_bright_observer_count": len(strong_bright_nights),
                "faint_observer_count": len(faint_observers),
            })
        reset()

    return emissions


def _emission_bytes(emissions: list[dict]) -> bytes:
    return json.dumps(emissions, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def reference_checked_emissions(rows: list[dict], threshold: float = 10.0) -> list[dict]:
    """Return independent emissions only after exact reference concordance."""
    independent = causal_confirmation_emissions(rows, threshold)
    reference = _reference_causal_confirmations(rows, threshold)
    independent_bytes = _emission_bytes(independent)
    reference_bytes = _emission_bytes(reference)
    if independent_bytes != reference_bytes:
        independent_hash = hashlib.sha256(independent_bytes).hexdigest()
        reference_hash = hashlib.sha256(reference_bytes).hexdigest()
        raise RuntimeError(
            "X4 causal emission harness mismatch before recovery scoring: "
            f"independent_sha256={independent_hash}, reference_sha256={reference_hash}"
        )
    return independent


def score_validation(rows: list[dict], episodes: list[dict], truth: list[dict], start: float,
                     stop: float, threshold: float = 10.0, *, audit_prefix: bool = False) -> list[dict]:
    """Score X4, replacing only X3's operational-confirmation metrics."""
    if _number(start) is None or _number(stop) is None or float(stop) <= float(start):
        raise ValueError("stop must be finite and greater than start")
    start, stop, threshold = float(start), float(stop), float(threshold)
    emissions = reference_checked_emissions(rows, threshold)

    scored = _x3_score_validation(
        rows, episodes, truth, start, stop, threshold, audit_prefix=audit_prefix)
    ordered_truth = sorted((dict(event) for event in truth),
                           key=lambda event: (float(event["onset"]), str(event.get("id", ""))))
    all_episodes = sorted(
        (dict(episode, _candidate_index=index) for index, episode in enumerate(episodes)),
        key=lambda episode: (_number(episode.get("peak_t")) or math.inf),
    )
    confirmed = [episode for episode in all_episodes if episode.get("confirmed_event", True)]
    _, _, _, unique_truth = _matching(confirmed, ordered_truth)
    reference = [j for j, event in enumerate(ordered_truth)
                 if start + 2.0 <= float(event["onset"]) and float(event["end"]) <= stop - 2.0]
    operational = _operational_confirmation_metrics(
        reference, [j for j in reference if j in unique_truth], ordered_truth, emissions)
    for result in scored:
        result.update(operational)
    return scored


__all__ = [
    "causal_confirmation_emissions",
    "reference_checked_emissions",
    "score_validation",
]
