"""Causal, synthetic adaptive-observing-effort stress policy.

This is deliberately a stress policy rather than a fitted observing model.
Each native-JD day receives one retention draw.  The draw is made before any
row from that day is inspected, and only retained rows can update the simple
bright/faint controller.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import math
import random
from typing import Any


_DEFAULT_KEEP = 1.0
_LIMIT_VALUES = {"1", "true", "t", "yes", "y"}
_NOT_LIMIT_VALUES = {"0", "false", "f", "no", "n", ""}


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite numeric")
    return result


def _probability(value: Any, label: str) -> float:
    result = _finite(value, label)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{label} must be between 0 and 1")
    return result


def _is_limit(value: Any, label: str) -> bool:
    text = str(value).strip().casefold()
    if text in _LIMIT_VALUES:
        return True
    if text in _NOT_LIMIT_VALUES:
        return False
    raise ValueError(f"{label} must identify an upper limit with 0/1 or true/false")


def _rng(seed: Any) -> random.Random:
    """Make a deterministic generator without depending on Python hash randomization."""

    digest = hashlib.sha256(repr(seed).encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def _row_evidence(row: Mapping[str, Any], threshold: float) -> tuple[bool, bool]:
    """Return (clearly bright, clearly faint) for one eligible native row."""

    if row.get("band") != "Vis." or row.get("val") != "V":
        return False, False
    limit = _is_limit(row.get("fainterThan", "0"), "fainterThan")
    raw_magnitude = row.get("mag")
    if raw_magnitude in (None, "") and limit:
        raw_magnitude = row.get("limit_magnitude")
    magnitude = _finite(raw_magnitude, "selected row magnitude")
    if not limit and magnitude <= threshold - 0.5:
        return True, False
    if magnitude >= threshold + 0.5:
        return False, True
    return False, False


def _validated_rows(rows: Iterable[Mapping[str, Any]]) -> list[tuple[float, int, Mapping[str, Any]]]:
    if isinstance(rows, (str, bytes)):
        raise ValueError("rows must be an iterable of row mappings")
    try:
        supplied = list(rows)
    except TypeError as exc:
        raise ValueError("rows must be an iterable of row mappings") from exc
    prepared: list[tuple[float, int, Mapping[str, Any]]] = []
    for index, row in enumerate(supplied):
        if not isinstance(row, Mapping):
            raise ValueError(f"rows[{index}] must be a mapping")
        jd = _finite(row.get("JD"), f"rows[{index}] JD")
        prepared.append((jd, index, row))
    prepared.sort(key=lambda item: (item[0], item[1]))
    return prepared


def thin_adaptive(
    rows: Iterable[Mapping[str, Any]],
    seed: Any,
    threshold: float = 10.0,
    *,
    short_keep: float = 0.35,
    long_keep: float = 1.0,
    split_days: float = 12.0,
    reset_days: float = 60.0,
) -> tuple[list[Mapping[str, Any]], dict[str, Any]]:
    """Thin a synthetic native stream using a causal mark-dependent controller.

    Rows are grouped by ``floor(JD)``.  One Bernoulli draw is made per day,
    before inspecting that day's rows.  All rows in a retained day are
    returned in native-JD/stable-input order and are not modified.
    """

    threshold_value = _finite(threshold, "threshold")
    short_value = _probability(short_keep, "short_keep")
    long_value = _probability(long_keep, "long_keep")
    split_value = _finite(split_days, "split_days")
    reset_value = _finite(reset_days, "reset_days")
    if split_value < 0.0:
        raise ValueError("split_days must be non-negative")
    if reset_value <= 0.0:
        raise ValueError("reset_days must be positive")

    prepared = _validated_rows(rows)
    days: dict[int, list[tuple[float, int, Mapping[str, Any]]]] = {}
    for item in prepared:
        days.setdefault(math.floor(item[0]), []).append(item)

    rng = _rng(seed)
    keep_probability = _DEFAULT_KEEP
    bright_state = False
    first_bright_day: float | None = None
    last_bright_day: float | None = None
    closure_day: float | None = None
    faint_days: set[int] = set()
    kept_rows: list[Mapping[str, Any]] = []
    kept_days = 0
    dropped_days = 0
    controller_updates: list[dict[str, Any]] = []

    for day, day_rows in sorted(days.items()):
        # The reset test is based only on time already elapsed since a prior
        # closure.  It occurs before this day's preassigned retention draw.
        if (
            not bright_state
            and closure_day is not None
            and day - closure_day >= reset_value
        ):
            # Reset is explicitly to the initial high-cadence state, not to a
            # user-supplied long-episode probability.
            keep_probability = _DEFAULT_KEEP
            closure_day = None

        # Once a retained bright row arms an episode, every subsequent day is
        # high-cadence until the episode closes.  This assignment is still
        # before the day's draw; a bright row found today cannot affect today's
        # already-selected probability.
        if bright_state:
            keep_probability = _DEFAULT_KEEP
        day_keep_probability = keep_probability
        day_kept = rng.random() < day_keep_probability
        if not day_kept:
            dropped_days += 1
            continue

        kept_days += 1
        kept_rows.extend(row for _, _, row in day_rows)

        # Aggregate the day's evidence before updating state so that row order
        # within a native day cannot affect the controller.
        day_bright = False
        day_faint = False
        for _, _, row in day_rows:
            bright, faint = _row_evidence(row, threshold_value)
            day_bright = day_bright or bright
            day_faint = day_faint or faint

        if day_bright:
            if not bright_state:
                first_bright_day = float(day)
                bright_state = True
                # An old closure no longer controls an active bright episode.
                closure_day = None
            last_bright_day = float(day)
            faint_days.clear()
            # The current draw was preassigned; this takes effect next day.
            keep_probability = _DEFAULT_KEEP
            continue

        if not bright_state or last_bright_day is None:
            continue

        if day_faint and day > last_bright_day:
            faint_days.add(day)
        if len(faint_days) < 2:
            continue

        proxy_duration = max(0.0, last_bright_day - (first_bright_day or last_bright_day))
        next_keep = short_value if proxy_duration < split_value else long_value
        keep_probability = next_keep
        closure_day = float(day)
        controller_updates.append(
            {
                "atJD": float(day),
                "proxy_duration": proxy_duration,
                "next_keep": next_keep,
            }
        )
        bright_state = False
        first_bright_day = None
        last_bright_day = None
        faint_days.clear()

    settings = {
        "threshold": threshold_value,
        "short_keep": short_value,
        "long_keep": long_value,
        "split_days": split_value,
        "reset_days": reset_value,
    }
    metadata = {
        "scope": (
            "synthetic causal thinning stress policy; not a realistic observing model"
        ),
        "initial_settings": {**settings, "initial_keep": _DEFAULT_KEEP},
        "final_settings": {
            **settings,
            "final_keep": keep_probability,
            "bright_state": bright_state,
            "closure_at": closure_day,
        },
        "days_input": len(days),
        "days_kept": kept_days,
        "days_dropped": dropped_days,
        "rows_input": len(prepared),
        "rows_kept": len(kept_rows),
        "controller_updates": controller_updates,
    }
    return kept_rows, metadata
