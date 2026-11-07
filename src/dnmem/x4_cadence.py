"""State-conditioned cadence with episode-level bright-day donor progression."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import math
import random
from statistics import median
from typing import Any

from .extract import SPLIT_GAP, x1_vote_episodes


THRESHOLD = 10.0
ERA_RADIUS_DAYS = 5 * 365.25
QUIET_RADIUS_DAYS = 15
DONOR_POOL_SIZE = 8


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite numeric")
    return result


def _rng(seed: Any, label: str) -> random.Random:
    digest = hashlib.sha256(f"{seed!r}\0{label}".encode()).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def _evaluate(history: Any, times: Sequence[float]) -> list[float]:
    if not hasattr(history, "evaluate"):
        raise ValueError("history must provide evaluate(times)")
    values = list(history.evaluate(times))
    if len(values) != len(times):
        raise ValueError("history.evaluate returned the wrong number of magnitudes")
    return [_finite(value, "history magnitude") for value in values]


def _validated_days(days: Sequence[Mapping[str, Any]]) -> dict[int, dict[str, Any]]:
    if isinstance(days, (str, bytes)) or not isinstance(days, Sequence):
        raise ValueError("days must be a sequence of day mappings")
    table: dict[int, dict[str, Any]] = {}
    for index, raw in enumerate(days):
        if not isinstance(raw, Mapping):
            raise ValueError(f"days[{index}] must be a mapping")
        day_value = _finite(raw.get("day"), f"days[{index}] day")
        day = int(day_value)
        if day_value != day:
            raise ValueError(f"days[{index}] day must be an integer native-JD day")
        if day in table:
            raise ValueError("days must contain unique native-JD days")
        state = raw.get("state")
        if state not in {"B", "F", "mixed", "unknown"}:
            raise ValueError(f"days[{index}] has an unsupported state")
        slots = raw.get("slots")
        if isinstance(slots, (str, bytes)) or not isinstance(slots, Sequence) or not slots:
            raise ValueError(f"days[{index}] slots must be a non-empty sequence")
        copied = []
        for slot_index, slot in enumerate(slots):
            if not isinstance(slot, Mapping):
                raise ValueError(f"days[{index}] slots[{slot_index}] must be a mapping")
            when = _finite(slot.get("t", slot.get("JD")), f"days[{index}] slot time")
            if math.floor(when) != day:
                raise ValueError(f"days[{index}] contains a slot from another native-JD day")
            copied.append(dict(slot))
        table[day] = {"day": day, "state": state, "slots": copied}
    return table


def _donor_episodes(table: Mapping[int, Mapping[str, Any]]) -> list[list[int]]:
    bright = sorted(day for day, record in table.items() if record["state"] == "B")
    episodes: list[list[int]] = []
    for day in bright:
        if not episodes or day - episodes[-1][-1] > SPLIT_GAP:
            episodes.append([day])
        else:
            episodes[-1].append(day)
    return episodes


def _bright_target_runs(
    ordered_days: Sequence[int], wanted: Mapping[int, str], history: Any
) -> list[list[int]]:
    if not ordered_days:
        return []
    midpoint_days = list(range(ordered_days[0] + 1, ordered_days[-1]))
    midpoint_values = _evaluate(history, [day + 0.5 for day in midpoint_days])
    midpoint_bright = {
        day: value <= THRESHOLD for day, value in zip(midpoint_days, midpoint_values)
    }
    runs: list[list[int]] = []
    current: list[int] = []
    for day in ordered_days:
        if wanted[day] != "B":
            if current:
                runs.append(current)
                current = []
            continue
        connected = not current or all(
            midpoint_bright[between] for between in range(current[-1] + 1, day)
        )
        if current and not connected:
            runs.append(current)
            current = []
        current.append(day)
    if current:
        runs.append(current)
    return runs


def _choose_bright_donors(
    run: Sequence[int], episodes: Sequence[Sequence[int]], seed: Any
) -> tuple[list[int] | None, int | None]:
    midpoint = median(run)
    eligible = [
        (index, list(episode))
        for index, episode in enumerate(episodes)
        if len(episode) >= len(run)
        and abs(median(episode) - midpoint) <= ERA_RADIUS_DAYS
    ]
    if not eligible:
        return None, None
    minimum_surplus = min(len(episode) - len(run) for _, episode in eligible)
    matched = [
        item for item in eligible if len(item[1]) - len(run) <= minimum_surplus + 2
    ]
    matched.sort(key=lambda item: (abs(median(item[1]) - midpoint), item[1][0]))
    local = matched[:DONOR_POOL_SIZE]
    rng = _rng(seed, f"bright-run:{run[0]}:{run[-1]}:{len(run)}")
    index, episode = local[rng.randrange(len(local))]
    offset = rng.randrange(len(episode) - len(run) + 1)
    return episode[offset : offset + len(run)], index


def _shifted_slots(
    donor: Mapping[str, Any], target_day: int, start: float, stop: float
) -> tuple[list[dict[str, Any]], int]:
    donor_day = int(donor["day"])
    shift = target_day - donor_day
    output: list[dict[str, Any]] = []
    omitted = 0
    for slot in donor["slots"]:
        when = _finite(slot.get("t", slot.get("JD")), "slot time") + shift
        if start <= when < stop:
            output.append({**slot, "JD": when, "t": when})
        else:
            omitted += 1
    return output, omitted


def _reuse_summary(
    uses: Sequence[tuple[str, int]], episode_uses: Sequence[int]
) -> dict[str, int | float]:
    counts = Counter(uses)
    bright_counts = Counter(day for state, day in uses if state == "B")
    episode_counts = Counter(episode_uses)
    return {
        "assignments": len(uses),
        "unique_donor_days": len(counts),
        "reused_assignments": len(uses) - len(counts),
        "reuse_fraction": (len(uses) - len(counts)) / len(uses) if uses else 0.0,
        "max_donor_day_use": max(counts.values(), default=0),
        "bright_assignments": sum(bright_counts.values()),
        "bright_unique_donor_days": len(bright_counts),
        "bright_reused_assignments": sum(bright_counts.values()) - len(bright_counts),
        "bright_reuse_fraction": (
            (sum(bright_counts.values()) - len(bright_counts)) / sum(bright_counts.values())
            if bright_counts
            else 0.0
        ),
        "bright_max_donor_day_use": max(bright_counts.values(), default=0),
        "bright_donor_episode_assignments": len(episode_uses),
        "unique_bright_donor_episodes": len(episode_counts),
        "max_bright_donor_episode_use": max(episode_counts.values(), default=0),
    }


def diverse_state_schedule(
    days: Sequence[Mapping[str, Any]],
    history: Any,
    start: float,
    stop: float,
    seed: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Borrow state-compatible cadence without repeating one bright donor day.

    Each synthetic bright run is mapped in order to distinct days from one
    era-local real bright episode. Donor episodes are matched only on their
    number of observed bright days and epoch; the following real gap is never
    inspected. Quiet targets retain an already-faint day or use the nearest
    faint donor within 15 days.
    """
    start_value = _finite(start, "start")
    stop_value = _finite(stop, "stop")
    if stop_value <= start_value:
        raise ValueError("stop must be greater than start")
    supplied = _validated_days(days)
    table: dict[int, dict[str, Any]] = {}
    input_boundary_rows = 0
    for day, record in supplied.items():
        kept = []
        for slot in record["slots"]:
            when = _finite(slot.get("t", slot.get("JD")), "slot time")
            if start_value <= when < stop_value:
                kept.append(slot)
            else:
                input_boundary_rows += 1
        if kept:
            table[day] = {**record, "slots": kept}
    ordered = sorted(table)
    for day in ordered:
        if day < math.floor(start_value) or day >= math.ceil(stop_value):
            raise ValueError("days must lie within the requested native-JD window")

    representative_times = [
        median(_finite(slot.get("t", slot.get("JD")), "slot time") for slot in table[day]["slots"])
        for day in ordered
    ]
    wanted = {
        day: "B" if value <= THRESHOLD else "F"
        for day, value in zip(ordered, _evaluate(history, representative_times))
    }
    episodes = _donor_episodes(table)
    bright_runs = _bright_target_runs(ordered, wanted, history)
    assignments: dict[int, tuple[int, str, int | None]] = {}
    matched_runs = 0
    unmatched_runs = 0
    episode_uses: list[int] = []
    for run in bright_runs:
        donors, episode_index = _choose_bright_donors(run, episodes, seed)
        if donors is None:
            unmatched_runs += 1
            for day in run:
                assignments[day] = (day, "unmatched", None)
            continue
        matched_runs += 1
        episode_uses.append(episode_index)
        for day, donor in zip(run, donors):
            assignments[day] = (donor, "B", episode_index)

    faint_days = sorted(day for day, record in table.items() if record["state"] == "F")
    for day in ordered:
        if wanted[day] != "F":
            continue
        if table[day]["state"] == "F":
            assignments[day] = (day, "F", None)
            continue
        candidates = [donor for donor in faint_days if abs(donor - day) <= QUIET_RADIUS_DAYS]
        if not candidates:
            assignments[day] = (day, "unmatched", None)
            continue
        distance = min(abs(donor - day) for donor in candidates)
        tied = [donor for donor in candidates if abs(donor - day) == distance]
        rng = _rng(seed, f"quiet-day:{day}")
        assignments[day] = (tied[rng.randrange(len(tied))], "F", None)

    output: list[dict[str, Any]] = []
    boundary_rows_omitted = input_boundary_rows
    borrowed_days = 0
    no_match_days = 0
    uses: list[tuple[str, int]] = []
    for day in ordered:
        donor_day, state, _ = assignments[day]
        borrowed_days += donor_day != day
        no_match_days += state == "unmatched"
        if state != "unmatched":
            uses.append((state, donor_day))
        shifted, omitted = _shifted_slots(table[donor_day], day, start_value, stop_value)
        output.extend(shifted)
        boundary_rows_omitted += omitted
    output.sort(key=lambda row: (float(row["JD"]), str(row.get("observer_id", ""))))

    calendar_days = math.ceil(stop_value) - math.floor(start_value)
    metadata = {
        "observed_target_days": len(table),
        "borrowed_days": borrowed_days,
        "no_match_days": no_match_days,
        "no_match_fraction": no_match_days / len(table) if table else 1.0,
        "empty_days_preserved": calendar_days - len(table),
        "boundary_rows_omitted": boundary_rows_omitted,
        "bright_runs": len(bright_runs),
        "bright_runs_matched": matched_runs,
        "bright_runs_unmatched": unmatched_runs,
        "donor_reuse": _reuse_summary(uses, episode_uses),
        "scope": (
            "episode-progressive bright cadence and nearest-day faint cadence; "
            "conditioning uses state, observed bright-day count, and epoch, never the following gap"
        ),
    }
    return output, metadata


def observer_diversity(
    rows: Sequence[Mapping[str, Any]], start: float | None = None, stop: float | None = None
) -> dict[str, Any]:
    """Summarize bright-observer counts for era-filtered, finite X1 episodes."""
    start_value = None if start is None else _finite(start, "start")
    stop_value = None if stop is None else _finite(stop, "stop")
    if start_value is not None and stop_value is not None and stop_value <= start_value:
        raise ValueError("stop must be greater than start")
    episodes = x1_vote_episodes(list(rows), threshold=THRESHOLD)
    eligible = []
    for episode in episodes:
        onset = episode.get("onset_lo")
        end = episode.get("end_hi")
        if onset is None or end is None:
            continue
        onset_value = float(onset)
        end_value = float(end)
        peak = float(episode["peak_t"])
        if not all(math.isfinite(value) for value in (onset_value, end_value, peak)):
            continue
        if end_value - onset_value < 4.0:
            continue
        if start_value is not None and peak < start_value:
            continue
        if stop_value is not None and peak >= stop_value:
            continue
        eligible.append(episode)
    counts = [int(episode["n_bright_observers"]) for episode in eligible]
    return {
        "all_x1_episodes": len(episodes),
        "eligible_episodes": len(eligible),
        "counts": counts,
        "median_bright_observers": float(median(counts)) if counts else None,
        "share_le_2": sum(count <= 2 for count in counts) / len(counts) if counts else None,
        "confirmed_episodes": sum(bool(episode["confirmed_event"]) for episode in eligible),
        "unconfirmed_episodes": sum(not episode["confirmed_event"] for episode in eligible),
        "minimum_boundary_span_days": 4.0,
        "era_start": start_value,
        "era_stop": stop_value,
    }


__all__ = ["diverse_state_schedule", "observer_diversity"]
