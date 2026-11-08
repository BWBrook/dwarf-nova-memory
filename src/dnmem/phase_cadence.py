"""Candidate-blind phase-aligned resampling of historical observing attention.

Profiles are built from X1 event boundaries and anonymous observation slots.
Scheduling is truth-conditioned simulation machinery, not an operational replay:
synthetic event intervals and magnitudes determine the target phase anchors.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
import hashlib
import math
import random
import re
from statistics import median
from typing import Any

from .extract import visits, x1_vote_episodes
from .injection_observe import prepare_schedule


THRESHOLD = 10.0
CORE_FRACTION = 0.5
QUIET_PADDING_DAYS = 2.0
YEAR_DAYS = 365.25
_OBSERVER_ID = re.compile(r"^o[0-9]{4}$")


@dataclass(frozen=True)
class PhaseCadenceConfig:
    """Bounded donor-selection and numerical settings."""

    era_radius_days: float = 5 * YEAR_DAYS
    season_window_days: float = 75.0
    donor_pool_size: int = 8
    history_grid_days: float = 0.25


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite numeric")
    return result


def _identity(row: Mapping[str, Any]) -> str:
    value = str(row.get("obsName") or row.get("by") or "").strip().casefold()
    if not value:
        raise ValueError("selected row requires a non-empty by or obsName observer")
    return value


def _rng(seed: Any, label: str) -> random.Random:
    digest = hashlib.sha256(f"{seed!r}\0{label}".encode()).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def _season_distance(left: float, right: float) -> float:
    difference = abs((left % YEAR_DAYS) - (right % YEAR_DAYS))
    return min(difference, YEAR_DAYS - difference)


def _configuration(config: PhaseCadenceConfig | Mapping[str, Any] | None) -> PhaseCadenceConfig:
    if config is None:
        result = PhaseCadenceConfig()
    elif isinstance(config, PhaseCadenceConfig):
        result = config
    elif isinstance(config, Mapping):
        allowed = set(PhaseCadenceConfig.__dataclass_fields__)
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"unknown phase cadence config keys: {sorted(unknown)}")
        result = PhaseCadenceConfig(**config)
    else:
        raise ValueError("config must be PhaseCadenceConfig, a mapping, or None")
    if (
        not math.isfinite(float(result.era_radius_days))
        or result.era_radius_days <= 0
        or not math.isfinite(float(result.season_window_days))
        or not 0 < result.season_window_days <= YEAR_DAYS / 2
        or not isinstance(result.donor_pool_size, int)
        or result.donor_pool_size < 1
        or not math.isfinite(float(result.history_grid_days))
        or not 0 < result.history_grid_days <= 1.0
    ):
        raise ValueError("phase cadence config values are outside their bounded domains")
    return result


def _normalized_id_map(
    identities: Sequence[str], supplied: Mapping[str, str] | None
) -> dict[str, str]:
    if supplied is None:
        return {
            identity: f"o{index:04d}"
            for index, identity in enumerate(sorted(set(identities)), 1)
        }
    if not isinstance(supplied, Mapping):
        raise ValueError("id_map must be a mapping")
    normalized: dict[str, str] = {}
    for raw_identity, raw_id in supplied.items():
        identity = str(raw_identity).strip().casefold()
        observer_id = str(raw_id)
        if not identity or not _OBSERVER_ID.fullmatch(observer_id):
            raise ValueError("id_map must map non-empty identities to oNNNN IDs")
        if identity in normalized and normalized[identity] != observer_id:
            raise ValueError("id_map contains conflicting normalized identities")
        normalized[identity] = observer_id
    if len(set(normalized.values())) != len(normalized):
        raise ValueError("id_map observer IDs must be unique")
    missing = sorted(set(identities) - set(normalized))
    if missing:
        raise ValueError(f"id_map is missing {len(missing)} selected observers")
    return normalized


def _night_points(source_visits: Sequence[Mapping[str, Any]]) -> list[tuple[float, float]]:
    by_day: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for visit in source_visits:
        value = visit.get("value")
        if value is not None:
            by_day[math.floor(float(visit["t"]))].append(
                (float(visit["t"]), float(value))
            )
    return [
        (median(time for time, _ in values), median(value for _, value in values))
        for _, values in sorted(by_day.items())
    ]


def _crossing(left: tuple[float, float], right: tuple[float, float], level: float) -> float:
    left_t, left_y = left
    right_t, right_y = right
    if right_t <= left_t or right_y == left_y:
        return right_t
    fraction = (level - left_y) / (right_y - left_y)
    return left_t + min(1.0, max(0.0, fraction)) * (right_t - left_t)


def _real_anchors(episode: Mapping[str, Any], source_visits: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    keys = ("onset_lo", "onset_hi", "end_lo", "end_hi")
    if any(episode.get(key) is None for key in keys):
        return None
    onset = median((_finite(episode["onset_lo"], "onset_lo"), _finite(episode["onset_hi"], "onset_hi")))
    end = median((_finite(episode["end_lo"], "end_lo"), _finite(episode["end_hi"], "end_hi")))
    if end <= onset:
        return None
    points = [point for point in _night_points(source_visits) if onset <= point[0] <= end]
    if len(points) < 3:
        return None
    ordered_levels = sorted(value for _, value in points)
    lower_count = max(1, math.ceil(0.2 * len(ordered_levels)))
    robust_peak = median(ordered_levels[:lower_count])
    if not robust_peak < THRESHOLD - 0.2:
        return None
    core_level = robust_peak + CORE_FRACTION * (THRESHOLD - robust_peak)
    core_indices = [index for index, (_, value) in enumerate(points) if value <= core_level]
    if not core_indices:
        return None
    first, last = core_indices[0], core_indices[-1]
    core_rise = points[first][0] if first == 0 else _crossing(points[first - 1], points[first], core_level)
    core_fade = points[last][0] if last == len(points) - 1 else _crossing(points[last], points[last + 1], core_level)
    anchors = (
        onset - QUIET_PADDING_DAYS,
        onset,
        core_rise,
        core_fade,
        end,
        end + QUIET_PADDING_DAYS,
    )
    if any(right - left <= 1e-6 for left, right in zip(anchors, anchors[1:])):
        return None
    return {
        "quiet_before": anchors[0],
        "onset": anchors[1],
        "core_rise": anchors[2],
        "core_fade": anchors[3],
        "end": anchors[4],
        "quiet_after": anchors[5],
        "robust_peak_level": robust_peak,
        "core_level": core_level,
    }


def _anchor_tuple(anchors: Mapping[str, Any]) -> tuple[float, ...]:
    return tuple(
        _finite(anchors[key], f"anchor {key}")
        for key in ("quiet_before", "onset", "core_rise", "core_fade", "end", "quiet_after")
    )


def _phase_fractions(anchors: Mapping[str, Any]) -> dict[str, float]:
    values = _anchor_tuple(anchors)
    duration = values[4] - values[1]
    return {
        "rise": (values[2] - values[1]) / duration,
        "core": (values[3] - values[2]) / duration,
        "decline": (values[4] - values[3]) / duration,
    }


def build_profiles(
    rows: Iterable[Mapping[str, Any]],
    model: Mapping[str, Mapping[str, Any]] | None = None,
    id_map: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build anonymous X1 phase profiles from the complete native row set.

    IDs are assigned from every supplied Vis./V row before event filtering.
    Raw observer and source identifiers are never returned.
    """

    if isinstance(rows, (str, bytes)):
        raise ValueError("rows must be an iterable of mappings")
    try:
        source_rows = list(rows)
    except TypeError as exc:
        raise ValueError("rows must be an iterable of mappings") from exc
    default_schedule = prepare_schedule(source_rows)
    selected = [
        (index, row)
        for index, row in enumerate(source_rows)
        if isinstance(row, Mapping) and row.get("band") == "Vis." and row.get("val") == "V"
    ]
    identities = [_identity(row) for _, row in selected]
    mapping = _normalized_id_map(identities, id_map)
    if id_map is None:
        observed_mapping: dict[str, str] = {}
        for (_, row), slot in zip(selected, default_schedule):
            observed_mapping.setdefault(_identity(row), slot["observer_id"])
        if mapping != observed_mapping:
            raise AssertionError("observer pseudonym mapping diverged from prepare_schedule")
    schedule: list[dict[str, Any]] = []
    for (source_index, row), slot in zip(selected, default_schedule):
        copied = dict(slot)
        copied["observer_id"] = mapping[_identity(row)]
        copied["source_slot"] = source_index
        schedule.append(copied)
    required_ids = set(mapping.values())
    if model is not None:
        if not isinstance(model, Mapping):
            raise ValueError("model must be a mapping")
        missing = sorted(required_ids - {str(key) for key in model})
        if missing:
            raise ValueError(f"model is missing {len(missing)} mapped observer IDs")

    source_visits = visits(source_rows, threshold=THRESHOLD)
    episodes = x1_vote_episodes(source_rows, threshold=THRESHOLD)
    profiles: list[dict[str, Any]] = []
    skipped = Counter()
    for episode in episodes:
        anchors = _real_anchors(episode, source_visits)
        if anchors is None:
            skipped["insufficient_phase_anchors"] += 1
            continue
        anchor_values = _anchor_tuple(anchors)
        own_slots = [
            {
                "JD": float(slot["t"]),
                "t": float(slot["t"]),
                "band": "Vis.",
                "val": "V",
                "observer_id": slot["observer_id"],
                "slot_limit": slot.get("slot_limit"),
                "source_slot": slot["source_slot"],
            }
            for slot in schedule
            if anchor_values[0] <= float(slot["t"]) <= anchor_values[-1]
        ]
        if not own_slots:
            skipped["empty_profile"] += 1
            continue
        profile_id = f"p{len(profiles) + 1:04d}"
        observed_days = sorted({math.floor(slot["t"]) for slot in own_slots})
        first_day = math.floor(anchor_values[0])
        last_day = math.floor(anchor_values[-1])
        profiles.append(
            {
                "profile_id": profile_id,
                "epoch": float(episode["peak_t"]),
                "season_anchor": anchors["onset"],
                "duration": anchors["end"] - anchors["onset"],
                "anchors": anchors,
                "phase_fractions": _phase_fractions(anchors),
                "slots": own_slots,
                "observed_source_days": observed_days,
                "missing_source_days": (last_day - first_day + 1) - len(observed_days),
            }
        )
    observer_digest = hashlib.sha256("\n".join(sorted(required_ids)).encode()).hexdigest()
    return {
        "schema": "dnmem.phase_profiles.v1",
        "threshold": THRESHOLD,
        "core_fraction": CORE_FRACTION,
        "quiet_padding_days": QUIET_PADDING_DAYS,
        "observer_mapping": {
            "scheme": "sorted casefold(obsName or by), full supplied Vis./V set, one-based oNNNN",
            "n_observers": len(required_ids),
            "observer_id_sha256": observer_digest,
            "model_checked": model is not None,
            "external_id_map": id_map is not None,
        },
        "profiles": profiles,
        "summary": {
            "selected_rows": len(schedule),
            "x1_episodes": len(episodes),
            "profiles": len(profiles),
            "skipped": dict(sorted(skipped.items())),
        },
    }


def _evaluate(history: Any, times: Sequence[float], start: float, stop: float) -> list[float]:
    if not hasattr(history, "evaluate"):
        raise ValueError("history must provide evaluate(times)")
    if any(not start <= time < stop for time in times):
        raise ValueError("history evaluation attempted outside the requested half-open window")
    values = list(history.evaluate(times))
    if len(values) != len(times):
        raise ValueError("history.evaluate returned the wrong number of magnitudes")
    return [_finite(value, "history magnitude") for value in values]


def _bisect_level(history: Any, left: float, right: float, level: float, start: float, stop: float) -> float:
    left_value, right_value = _evaluate(history, [left, right], start, stop)
    for _ in range(32):
        middle = (left + right) / 2
        middle_value = _evaluate(history, [middle], start, stop)[0]
        if (left_value - level) * (middle_value - level) <= 0:
            right, right_value = middle, middle_value
        else:
            left, left_value = middle, middle_value
    return (left + right) / 2


def _scan_intervals(history: Any, start: float, stop: float, step: float) -> list[dict[str, Any]]:
    end = math.nextafter(stop, -math.inf)
    count = max(2, math.ceil((end - start) / step) + 1)
    times = [min(end, start + index * step) for index in range(count)]
    times = list(dict.fromkeys(times))
    values = _evaluate(history, times, start, stop)
    bright = [value <= THRESHOLD for value in values]
    intervals: list[dict[str, Any]] = []
    index = 0
    while index < len(times):
        if not bright[index]:
            index += 1
            continue
        first = index
        while index + 1 < len(times) and bright[index + 1]:
            index += 1
        last = index
        onset = times[first]
        end_time = times[last]
        if first > 0:
            onset = _bisect_level(history, times[first - 1], times[first], THRESHOLD, start, stop)
        if last + 1 < len(times):
            end_time = _bisect_level(history, times[last], times[last + 1], THRESHOLD, start, stop)
        intervals.append({"id": f"scan-{len(intervals) + 1}", "onset": onset, "end": end_time})
        index += 1
    return intervals


def _record_interval(record: Any, index: int) -> dict[str, Any] | None:
    interval = None
    method = getattr(record, "threshold_interval", None)
    if callable(method):
        interval = method(THRESHOLD)
    if interval is not None:
        onset, end = interval
    elif isinstance(record, Mapping) and record.get("onset") is not None and record.get("end") is not None:
        onset, end = record["onset"], record["end"]
    elif hasattr(record, "onset_jd") and hasattr(record, "end_jd"):
        onset, end = record.onset_jd, record.end_jd
    elif hasattr(record, "onset") and hasattr(record, "end"):
        onset, end = record.onset, record.end
    else:
        return None
    onset_value = _finite(onset, "event onset")
    end_value = _finite(end, "event end")
    if end_value <= onset_value:
        return None
    identifier = record.get("id", index) if isinstance(record, Mapping) else getattr(record, "event_id", index)
    return {"id": str(identifier), "onset": onset_value, "end": end_value}


def _history_intervals(
    history: Any, start: float, stop: float, config: PhaseCadenceConfig
) -> list[dict[str, Any]]:
    records: Sequence[Any] | None = None
    if hasattr(history, "events"):
        records = tuple(history.events)
    elif hasattr(history, "catalogue"):
        catalogue = history.catalogue
        if callable(catalogue):
            try:
                catalogue = catalogue(THRESHOLD)
            except TypeError:
                catalogue = catalogue()
        if not isinstance(catalogue, (str, bytes)) and isinstance(catalogue, Sequence):
            records = catalogue
    intervals = [] if records is None else [
        parsed for index, record in enumerate(records) if (parsed := _record_interval(record, index)) is not None
    ]
    if records is None or not intervals:
        intervals = _scan_intervals(history, start, stop, config.history_grid_days)
    clipped = [record for record in intervals if record["end"] > start and record["onset"] < stop]
    clipped.sort(key=lambda record: (record["onset"], record["end"], record["id"]))
    unique: list[dict[str, Any]] = []
    seen: set[tuple[float, float]] = set()
    for record in clipped:
        key = (round(record["onset"], 9), round(record["end"], 9))
        if key not in seen:
            unique.append(record)
            seen.add(key)
    return unique


def _target_anchors(
    history: Any,
    interval: Mapping[str, Any],
    start: float,
    stop: float,
    step: float,
) -> dict[str, Any] | None:
    onset = max(start, float(interval["onset"]))
    end = min(math.nextafter(stop, -math.inf), float(interval["end"]))
    if end <= onset:
        return None
    count = max(3, math.ceil((end - onset) / step) + 1)
    times = [min(end, onset + index * step) for index in range(count)]
    times = list(dict.fromkeys(times))
    values = _evaluate(history, times, start, stop)
    minimum = min(values)
    if not minimum < THRESHOLD - 0.2:
        return None
    core_level = minimum + CORE_FRACTION * (THRESHOLD - minimum)
    core = [index for index, value in enumerate(values) if value <= core_level]
    if not core:
        return None
    first, last = core[0], core[-1]
    core_rise = times[first]
    core_fade = times[last]
    if first > 0:
        core_rise = _bisect_level(history, times[first - 1], times[first], core_level, start, stop)
    if last + 1 < len(times):
        core_fade = _bisect_level(history, times[last], times[last + 1], core_level, start, stop)
    anchors = {
        "quiet_before": onset - QUIET_PADDING_DAYS,
        "onset": onset,
        "core_rise": core_rise,
        "core_fade": core_fade,
        "end": end,
        "quiet_after": end + QUIET_PADDING_DAYS,
        "peak_level": minimum,
        "peak_t": times[min(range(len(values)), key=values.__getitem__)],
        "core_level": core_level,
    }
    values_tuple = _anchor_tuple(anchors)
    if any(right - left <= 1e-6 for left, right in zip(values_tuple, values_tuple[1:])):
        return None
    return anchors


def _profiles(profiles: Any) -> list[dict[str, Any]]:
    if isinstance(profiles, Mapping):
        if profiles.get("threshold", THRESHOLD) != THRESHOLD:
            raise ValueError("profile threshold must be 10.0")
        if profiles.get("core_fraction", CORE_FRACTION) != CORE_FRACTION:
            raise ValueError("profile core fraction is incompatible")
        profiles = profiles.get("profiles")
    if isinstance(profiles, (str, bytes)) or not isinstance(profiles, Sequence):
        raise ValueError("profiles must be profile data or a profile sequence")
    output = []
    identifiers = set()
    for index, raw in enumerate(profiles):
        if not isinstance(raw, Mapping):
            raise ValueError(f"profiles[{index}] must be a mapping")
        copied = dict(raw)
        identifier = str(copied.get("profile_id", f"p{index + 1:04d}"))
        if identifier in identifiers:
            raise ValueError("profile IDs must be unique")
        identifiers.add(identifier)
        anchors = _anchor_tuple(copied.get("anchors", {}))
        if any(right <= left for left, right in zip(anchors, anchors[1:])):
            raise ValueError("profile anchors must increase strictly")
        slots = copied.get("slots")
        if isinstance(slots, (str, bytes)) or not isinstance(slots, Sequence) or not slots:
            raise ValueError("every profile must contain slots")
        copied["profile_id"] = identifier
        copied["duration"] = anchors[4] - anchors[1]
        copied["phase_fractions"] = _phase_fractions(copied["anchors"])
        copied["epoch"] = _finite(copied.get("epoch", (anchors[1] + anchors[4]) / 2), "profile epoch")
        copied["season_anchor"] = _finite(copied.get("season_anchor", anchors[1]), "profile season anchor")
        output.append(copied)
    return output


def _choose_profile(
    target: Mapping[str, Any],
    profiles: Sequence[Mapping[str, Any]],
    seed: Any,
    config: PhaseCadenceConfig,
    stratum_start: float,
    stratum_stop: float,
) -> tuple[Mapping[str, Any] | None, dict[str, Any]]:
    target_fractions = _phase_fractions(target["anchors"])
    target_epoch = float(target["anchors"]["peak_t"])
    target_onset = float(target["anchors"]["onset"])
    target_duration = float(target["anchors"]["end"]) - target_onset
    eligible = [
        profile for profile in profiles
        if stratum_start <= float(profile["epoch"]) < stratum_stop
        and abs(float(profile["epoch"]) - target_epoch) <= config.era_radius_days
        and _season_distance(float(profile["season_anchor"]), target_onset) <= config.season_window_days
    ]
    if not eligible:
        return None, {"eligible": 0}

    def components(profile: Mapping[str, Any]) -> tuple[float, float, float]:
        duration_error = abs(math.log(float(profile["duration"]) / target_duration))
        phase_error = sum(
            abs(float(profile["phase_fractions"][key]) - target_fractions[key])
            for key in ("rise", "core", "decline")
        )
        return duration_error + phase_error, duration_error, phase_error

    ranked = sorted(
        eligible,
        key=lambda profile: (
            *components(profile),
            _season_distance(float(profile["season_anchor"]), target_onset),
            abs(float(profile["epoch"]) - target_epoch),
            str(profile["profile_id"]),
        ),
    )
    pool = ranked[: config.donor_pool_size]
    rng = _rng(seed, f"target:{target['id']}:{target_onset:.9f}:{target_duration:.9f}")
    chosen = pool[rng.randrange(len(pool))]
    score, duration_error, phase_error = components(chosen)
    return chosen, {
        "eligible": len(eligible),
        "pool": len(pool),
        "score": score,
        "duration_log_error": duration_error,
        "phase_fraction_error": phase_error,
        "season_distance_days": _season_distance(float(chosen["season_anchor"]), target_onset),
        "epoch_distance_days": abs(float(chosen["epoch"]) - target_epoch),
    }


def _map_time(value: float, source: tuple[float, ...], target: tuple[float, ...]) -> tuple[float, int, float]:
    if value <= source[0]:
        segment = 0
    elif value >= source[-1]:
        segment = len(source) - 2
    else:
        segment = next(index for index in range(len(source) - 1) if source[index] <= value <= source[index + 1])
    source_width = source[segment + 1] - source[segment]
    target_width = target[segment + 1] - target[segment]
    fraction = (value - source[segment]) / source_width
    return target[segment] + fraction * target_width, segment, target_width / source_width


def _validated_days(
    days: Sequence[Mapping[str, Any]], start: float, stop: float
) -> tuple[dict[int, list[dict[str, Any]]], int]:
    if isinstance(days, (str, bytes)) or not isinstance(days, Sequence):
        raise ValueError("days must be a sequence")
    table: dict[int, list[dict[str, Any]]] = {}
    boundary = 0
    for index, record in enumerate(days):
        if not isinstance(record, Mapping):
            raise ValueError(f"days[{index}] must be a mapping")
        day_value = _finite(record.get("day"), f"days[{index}] day")
        day = int(day_value)
        if day_value != day or day in table:
            raise ValueError("days must have unique integer native-JD days")
        slots = record.get("slots")
        if isinstance(slots, (str, bytes)) or not isinstance(slots, Sequence) or not slots:
            raise ValueError("each supplied day must have non-empty slots")
        kept = []
        for slot_index, slot in enumerate(slots):
            if not isinstance(slot, Mapping):
                raise ValueError(f"days[{index}] slots[{slot_index}] must be a mapping")
            when = _finite(slot.get("t", slot.get("JD")), "slot time")
            if math.floor(when) != day:
                raise ValueError("a day contains a slot from another native-JD day")
            observer_id = str(slot.get("observer_id", ""))
            if not _OBSERVER_ID.fullmatch(observer_id):
                raise ValueError("schedule slots require anonymous oNNNN observer IDs")
            if start <= when < stop:
                kept.append(
                    {
                        "JD": when,
                        "t": when,
                        "band": "Vis.",
                        "val": "V",
                        "observer_id": observer_id,
                        "slot_limit": slot.get("slot_limit"),
                    }
                )
            else:
                boundary += 1
        if kept:
            table[day] = kept
    return table, boundary


def phase_aligned_schedule(
    days: Sequence[Mapping[str, Any]],
    profiles: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    history: Any,
    start: float,
    stop: float,
    seed: Any,
    config: PhaseCadenceConfig | Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Transfer donor visits through phase anchors and native-day masks.

    The original event-independent quiet slots remain. A mapped visit is
    emitted only when its target native-JD day existed in ``days``; originally
    empty days and seasonal gaps therefore remain unavailable.
    """

    start_value = _finite(start, "start")
    stop_value = _finite(stop, "stop")
    if stop_value <= start_value:
        raise ValueError("stop must be greater than start")
    settings = _configuration(config)
    donors = _profiles(profiles)
    day_table, input_boundary_drops = _validated_days(days, start_value, stop_value)
    intervals = _history_intervals(history, start_value, stop_value, settings)
    targets = []
    target_anchor_failures = 0
    for interval in intervals:
        anchors = _target_anchors(
            history, interval, start_value, stop_value, settings.history_grid_days
        )
        if anchors is None:
            target_anchor_failures += 1
        else:
            targets.append({"id": interval["id"], "anchors": anchors})

    event_windows = [
        (target["anchors"]["quiet_before"], target["anchors"]["quiet_after"])
        for target in targets
    ]
    quiet_rows = [
        dict(slot)
        for slots in day_table.values()
        for slot in slots
        if not any(left <= slot["t"] <= right for left, right in event_windows)
    ]
    replaced_input_slots = sum(len(slots) for slots in day_table.values()) - len(quiet_rows)
    output_records: list[tuple[dict[str, Any], str, int]] = [
        (row, "quiet", index) for index, row in enumerate(quiet_rows)
    ]
    profile_uses: Counter[str] = Counter()
    event_metadata = []
    mapped_source_visits = 0
    unavailable_drops = 0
    boundary_drops = 0
    duplicate_source_drops = 0
    donor_missing_days_total = 0
    phase_stretches: list[list[float]] = []

    for event_index, target in enumerate(targets):
        donor, match = _choose_profile(
            target, donors, seed, settings, start_value, stop_value
        )
        if donor is None:
            event_metadata.append(
                {
                    "target_event_id": target["id"],
                    "status": "unmatched",
                    "target_boundaries": target["anchors"],
                    "matching": match,
                }
            )
            continue
        profile_id = str(donor["profile_id"])
        profile_uses[profile_id] += 1
        source_anchors = _anchor_tuple(donor["anchors"])
        target_anchors = _anchor_tuple(target["anchors"])
        stretch = [
            (target_anchors[index + 1] - target_anchors[index])
            / (source_anchors[index + 1] - source_anchors[index])
            for index in range(5)
        ]
        phase_stretches.append(stretch)
        own_output: list[tuple[dict[str, Any], str, int]] = []
        source_seen = set()
        own_boundary = own_unavailable = own_duplicate = 0
        landed_days = set()
        for slot_number, slot in enumerate(donor["slots"]):
            source_key = slot.get("source_slot", slot_number)
            if source_key in source_seen:
                duplicate_source_drops += 1
                own_duplicate += 1
                continue
            source_seen.add(source_key)
            mapped_source_visits += 1
            when, _, _ = _map_time(
                _finite(slot.get("t", slot.get("JD")), "profile slot time"),
                source_anchors,
                target_anchors,
            )
            if not start_value <= when < stop_value:
                boundary_drops += 1
                own_boundary += 1
                continue
            target_day = math.floor(when)
            if target_day not in day_table:
                unavailable_drops += 1
                own_unavailable += 1
                continue
            observer_id = str(slot.get("observer_id", ""))
            if not _OBSERVER_ID.fullmatch(observer_id):
                raise ValueError("profile slots require anonymous oNNNN observer IDs")
            landed_days.add(target_day)
            own_output.append(
                (
                    {
                        "JD": when,
                        "t": when,
                        "band": "Vis.",
                        "val": "V",
                        "observer_id": observer_id,
                        "slot_limit": slot.get("slot_limit"),
                    },
                    str(target["id"]),
                    event_index,
                )
            )
        expected_days = {
            day
            for day, slots in day_table.items()
            if any(target_anchors[0] <= slot["t"] <= target_anchors[-1] for slot in slots)
        }
        donor_missing = len(expected_days - landed_days)
        donor_missing_days_total += donor_missing
        output_records.extend(own_output)
        event_metadata.append(
            {
                "target_event_id": target["id"],
                "status": "matched",
                "profile_id": profile_id,
                "target_boundaries": target["anchors"],
                "donor_boundaries": donor["anchors"],
                "phase_stretch": stretch,
                "matching": match,
                "source_visits": len(donor["slots"]),
                "emitted_visits_before_collision_merge": len(own_output),
                "boundary_drops": own_boundary,
                "unavailable_day_drops": own_unavailable,
                "duplicate_source_drops": own_duplicate,
                "donor_missing_available_days": donor_missing,
            }
        )

    merged: list[dict[str, Any]] = []
    occupied: dict[tuple[float, str], str] = {}
    overlap_collision_drops = 0
    for row, event_id, event_index in sorted(
        output_records,
        key=lambda item: (float(item[0]["t"]), str(item[0]["observer_id"]), item[2]),
    ):
        key = (round(float(row["t"]), 9), str(row["observer_id"]))
        previous_event = occupied.get(key)
        if previous_event is not None and previous_event != event_id:
            overlap_collision_drops += 1
            continue
        occupied[key] = event_id
        merged.append(row)

    calendar_days = math.ceil(stop_value) - math.floor(start_value)
    output_days = {math.floor(float(row["t"])) for row in merged}
    reuse_count = sum(profile_uses.values()) - len(profile_uses)
    flattened_stretch = [value for stretches in phase_stretches for value in stretches]
    metadata = {
        "scope": (
            "truth-conditioned generative phase alignment; donor choice uses epoch, season, "
            "duration, and within-event phase fractions, never following gap, observer count, "
            "candidate extraction, or recovery score"
        ),
        "config": asdict(settings),
        "input_observed_days": len(day_table),
        "input_slots": sum(len(slots) for slots in day_table.values()),
        "input_boundary_drops": input_boundary_drops,
        "original_empty_days_preserved": calendar_days - len(day_table),
        "quiet_slots_retained": len(quiet_rows),
        "event_window_input_slots_replaced": replaced_input_slots,
        "target_events": len(intervals),
        "target_events_with_anchors": len(targets),
        "target_anchor_failures": target_anchor_failures,
        "matched_events": sum(record["status"] == "matched" for record in event_metadata),
        "unmatched_events": sum(record["status"] == "unmatched" for record in event_metadata),
        "source_visits_considered": mapped_source_visits,
        "mapped_visits_emitted": len(merged) - len(quiet_rows),
        "unavailable_day_drops": unavailable_drops,
        "boundary_drops": boundary_drops,
        "duplicate_source_drops": duplicate_source_drops,
        "overlap_collision_drops": overlap_collision_drops,
        "donor_missing_available_days": donor_missing_days_total,
        "output_observed_days": len(output_days),
        "output_never_uses_originally_empty_day": output_days <= set(day_table),
        "donor_reuse": {
            "assignments": sum(profile_uses.values()),
            "unique_profiles": len(profile_uses),
            "reused_assignments": reuse_count,
            "reuse_fraction": reuse_count / sum(profile_uses.values()) if profile_uses else 0.0,
            "max_profile_use": max(profile_uses.values(), default=0),
        },
        "phase_stretch": {
            "segment_order": ["pre_quiet", "rise", "core", "decline", "post_quiet"],
            "minimum": min(flattened_stretch, default=None),
            "median": median(flattened_stretch) if flattened_stretch else None,
            "maximum": max(flattened_stretch, default=None),
        },
        "events": event_metadata,
    }
    return merged, metadata


__all__ = [
    "PhaseCadenceConfig",
    "build_profiles",
    "phase_aligned_schedule",
]
