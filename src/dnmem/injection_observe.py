"""Bounded in-memory observation model for injection/recovery checks."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import hashlib
import math
import random
from statistics import median
from typing import Any

_DEFAULT_SIGMA = 0.2
_MIN_SIGMA = 0.1


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite numeric")
    return result


def _flag(value: Any, label: str) -> str:
    value = str(value).strip()
    if value not in {"0", "1"}:
        raise ValueError(f"{label} must be '0' or '1'")
    return value


def _observer(row: Mapping[str, Any]) -> str:
    identity = str(row.get("obsName") or row.get("by") or "").strip().casefold()
    if not identity:
        raise ValueError("selected row requires a non-empty by or obsName observer")
    return identity


def _quantiles(values: Iterable[float]) -> dict[str, float | None]:
    values = sorted(values)
    if not values:
        return {"q25": None, "q50": None, "q75": None}
    def pick(frac: float) -> float:
        return values[min(len(values) - 1, int(frac * (len(values) - 1) + 0.5))]
    return {"q25": pick(.25), "q50": pick(.50), "q75": pick(.75)}


def _mad(values: Sequence[float], centre: float) -> float:
    return median(abs(value - centre) for value in values)


def _selected(rows: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate selected native rows and return public and private views."""
    if isinstance(rows, (str, bytes)):
        raise ValueError("rows must be an iterable of row mappings")
    try:
        source_rows = list(rows)
    except TypeError as exc:
        raise ValueError("rows must be an iterable of row mappings") from exc
    if not source_rows:
        raise ValueError("rows must not be empty")
    selected: list[tuple[Mapping[str, Any], str, float, float, bool, float | None]] = []
    seen: set[str] = set()
    for index, row in enumerate(source_rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"rows[{index}] must be a mapping")
        if row.get("band") != "Vis." or row.get("val") != "V":
            continue
        jd = _finite(row.get("JD"), f"rows[{index}] JD")
        source_id = row.get("obsID")
        if source_id not in (None, ""):
            source_id = str(source_id)
            if source_id in seen:
                raise ValueError("duplicate source obsID in selected rows")
            seen.add(source_id)
        identity = _observer(row)
        is_limit = _flag(row.get("fainterThan", "0"), f"rows[{index}] fainterThan") == "1"
        magnitude = _finite(row.get("mag"), f"rows[{index}] mag")
        selected.append((row, identity, jd, magnitude, is_limit, magnitude if is_limit else None))
    if not selected:
        raise ValueError("no Vis./V rows to prepare")
    identities = sorted({identity for _, identity, *_ in selected})
    pseudonyms = {identity: f"o{index:04d}" for index, identity in enumerate(identities, 1)}
    schedule: list[dict[str, Any]] = []
    internal: list[dict[str, Any]] = []
    for source, identity, jd, magnitude, is_limit, limit in selected:
        observer_id = pseudonyms[identity]
        # Only source limits cross the serializable schedule boundary. Positive
        # source magnitudes stay in this local calibration view.
        schedule.append({"JD": source["JD"], "t": jd, "band": "Vis.", "val": "V",
                         "observer_id": observer_id, "slot_limit": limit})
        internal.append({"jd": jd, "native_jd": source["JD"], "observer_id": observer_id,
                         "magnitude": magnitude, "is_limit": is_limit, "limit": limit})
    return schedule, internal


def prepare_schedule(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return Vis./V cadence rows with stable pseudonymous observer IDs.

    Native times are retained as ``JD`` and numeric ``t``.  The returned list
    contains no source observer strings, source IDs, or positive magnitudes.
    Source limits are retained as ``slot_limit`` for simulation censoring.
    """
    schedule, _ = _selected(rows)
    return schedule


def _episode_exclusions(episodes: Iterable[Mapping[str, Any]] | None) -> list[tuple[float, float]]:
    if episodes is None:
        return []
    exclusions = []
    for index, episode in enumerate(episodes):
        if not isinstance(episode, Mapping):
            raise ValueError(f"x1_episodes[{index}] must be a mapping")
        starts = [_finite(episode[key], f"x1_episodes[{index}] onset") for key in ("onset_lo", "onset_hi")
                  if episode.get(key) not in (None, "")]
        ends = [_finite(episode[key], f"x1_episodes[{index}] end") for key in ("end_lo", "end_hi")
                if episode.get(key) not in (None, "")]
        if not starts or not ends:
            continue
        lower, upper = min(starts), max(ends)
        if upper < lower:
            raise ValueError(f"x1_episodes[{index}] has reversed boundaries")
        exclusions.append((lower - 2.0, upper + 2.0))
    return exclusions


def calibrate(rows: Iterable[Mapping[str, Any]], x1_episodes: Iterable[Mapping[str, Any]] | None = None) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Calibrate observer offsets/scatters and return model plus public summary."""
    schedule, internal = _selected(rows)
    exclusions = _episode_exclusions(x1_episodes)
    all_bins: dict[int, dict[str, list[float]]] = {}
    limits: dict[str, list[float]] = {}
    for row in internal:
        observer_id = row["observer_id"]
        limits.setdefault(observer_id, [])
        if row["is_limit"]:
            limits[observer_id].append(row["limit"])
            continue
        day = math.floor(row["jd"])
        all_bins.setdefault(day, {}).setdefault(observer_id, []).append(row["magnitude"])
    collapsed = {day: {observer: median(values) for observer, values in observers.items()}
                 for day, observers in all_bins.items()}
    residuals: dict[str, list[float]] = {}
    plateau: list[float] = []
    plateau_bins = 0
    usable_bins = 0
    for day, observers in collapsed.items():
        if len(observers) < 2:
            continue
        quiet = not any(day < upper and day + 1 > lower for lower, upper in exclusions)
        if quiet:
            usable_bins += 1
        is_plateau = median(observers.values()) <= 9.0
        plateau_bins += is_plateau
        for observer_id, value in observers.items():
            peers = [other for other_id, other in observers.items() if other_id != observer_id]
            residual = value - median(peers)
            if quiet:
                residuals.setdefault(observer_id, []).append(residual)
            if is_plateau:
                plateau.append(residual)
    model: dict[str, dict[str, Any]] = {}
    for observer_id in sorted({row["observer_id"] for row in internal}):
        own = residuals.get(observer_id, [])
        if own:
            centre = median(own)
            offset = centre * len(own) / (len(own) + 10.0)
            sigma = max(_MIN_SIGMA, 1.4826 * _mad(own, centre))
        else:
            offset, sigma = 0.0, _DEFAULT_SIGMA
        model[observer_id] = {"offset": offset, "sigma": sigma,
                              "median_limit": median(limits[observer_id]) if limits[observer_id] else None,
                              "n_residuals": len(own)}
    summary = {
        "n_rows": len(schedule), "n_detections": sum(not row["is_limit"] for row in internal),
        "n_limits": sum(row["is_limit"] for row in internal), "n_observers": len(model),
        "native_jd_min": min(row["jd"] for row in internal),
        "native_jd_max": max(row["jd"] for row in internal), "calibration_bins": usable_bins,
        "plateau_bins": plateau_bins,
        "offset_quantiles": _quantiles(params["offset"] for params in model.values()),
        "sigma_quantiles": _quantiles(params["sigma"] for params in model.values()),
        "plateau_residual_quantiles": _quantiles(plateau),
    }
    return model, summary


def _seed(seed: Any, label: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{seed!r}\0{label}".encode()).digest()[:16], "big")


def simulate_rows(schedule: Sequence[Mapping[str, Any]], magnitudes: Sequence[Any], model: Mapping[str, Mapping[str, Any]] | None, seed: Any) -> list[dict[str, Any]]:
    """Emit synthetic native-shaped rows with no truth fields."""
    if isinstance(schedule, (str, bytes)) or not isinstance(schedule, Sequence) or not schedule:
        raise ValueError("schedule must be a non-empty schedule list")
    if isinstance(magnitudes, (str, bytes)):
        raise ValueError("magnitudes must be a finite numeric sequence")
    try:
        magnitudes = list(magnitudes)
    except TypeError as exc:
        raise ValueError("magnitudes must be a finite numeric sequence") from exc
    if len(magnitudes) != len(schedule):
        raise ValueError("magnitudes length must equal schedule length")
    truth = [_finite(value, f"magnitudes[{index}]") for index, value in enumerate(magnitudes)]
    observers = {str(row.get("observer_id")) for row in schedule}
    if model is None:
        params = {observer: {"offset": 0.0, "sigma": _DEFAULT_SIGMA, "median_limit": None} for observer in observers}
    else:
        params = {}
        for observer in observers:
            supplied = model.get(observer)
            if not isinstance(supplied, Mapping):
                raise ValueError(f"model missing observer {observer}")
            offset = _finite(supplied.get("offset"), f"model {observer} offset")
            sigma = _finite(supplied.get("sigma"), f"model {observer} sigma")
            if sigma < 0:
                raise ValueError(f"model {observer} sigma must be non-negative")
            limit = supplied.get("median_limit")
            params[observer] = {"offset": offset, "sigma": sigma,
                                "median_limit": None if limit is None else _finite(limit, f"model {observer} median_limit")}
    observer_keys = sorted({(str(row["observer_id"]), math.floor(_finite(row.get("t", row.get("JD")), "schedule time"))) for row in schedule})
    days = sorted({math.floor(_finite(row.get("t", row.get("JD")), "schedule time")) for row in schedule})
    observer_rng = random.Random(_seed(seed, "observer-bin"))
    bin_rng = random.Random(_seed(seed, "bin"))
    row_rng = random.Random(_seed(seed, "row"))
    shared_observer = {key: observer_rng.gauss(0.0, 1.0) for key in observer_keys}
    shared_bin = {day: bin_rng.gauss(0.0, 1.0) for day in days}
    output = []
    for index, (row, true_mag) in enumerate(zip(schedule, truth), 1):
        observer_id = str(row["observer_id"])
        day = math.floor(_finite(row.get("t", row.get("JD")), "schedule time"))
        observer = params[observer_id]
        sigma = observer["sigma"]
        measured = (true_mag + observer["offset"] + sigma / math.sqrt(2) * shared_observer[(observer_id, day)]
                    + sigma / math.sqrt(2) * row_rng.gauss(0.0, 1.0) + .05 * shared_bin[day])
        measured = round(measured, 1)
        slot_limit = row.get("slot_limit")
        limit = None if slot_limit is None else _finite(slot_limit, "schedule slot_limit")
        if limit is None:
            limit = observer["median_limit"]
        if limit is not None and measured > limit:
            emitted_mag, flag = limit, "1"
        else:
            emitted_mag, flag = measured, "0"
        output.append({"obsID": f"syn{index:06d}", "JD": row.get("JD", row.get("t")),
                      "mag": emitted_mag, "uncert": "", "fainterThan": flag,
                      "band": "Vis.", "by": observer_id, "obsName": observer_id, "val": "V"})
    return output


__all__ = ["prepare_schedule", "calibrate", "simulate_rows"]
