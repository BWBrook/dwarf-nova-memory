"""Independent reference ledger and outcome-evidence contract for A10.

This module intentionally contains no forecast model or score.  It is a small
contract implementation used to compare the prefix ledger and its truth-free
coarsening against another implementation before model fitting.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from dnmem.extract import THRESHOLD, VISIT_SPAN, visits
from dnmem.extract_x4 import x4_episodes
from dnmem.extract_x4 import causal_confirmations


DEFINITION_VERSION = "a10-prefix-v3"
_COVERAGE_DAYS = 7.0
_BOUNDARY_MARGIN = VISIT_SPAN + 1.0


def _number(value: Any, name: str, *, finite: bool = True) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if finite and not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _optional_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _positive_duration(episode: Mapping[str, Any] | None) -> float | None:
    """Return a finite positive point duration, or mark it unavailable."""
    if episode is None:
        return None
    onset = _optional_number(episode.get("onset_t"))
    end = _optional_number(episode.get("end_t"))
    if onset is None or end is None or end <= onset:
        return None
    return end - onset


def _jd(row: Mapping[str, Any]) -> float:
    # Native data use JD.  Accept nativeJD as a narrow convenience for the
    # normalized fixture format without changing the extraction input.
    value = row.get("JD", row.get("nativeJD"))
    return _number(value, "row JD")


def _validate_parameters(threshold: Any, latency: Any, lookback: Any) -> tuple[float, float, float]:
    threshold_f = _number(threshold, "threshold")
    latency_f = _number(latency, "latency")
    lookback_f = _number(lookback, "lookback")
    if latency_f < 0:
        raise ValueError("latency must be non-negative")
    if lookback_f <= 0:
        raise ValueError("lookback must be positive")
    return threshold_f, latency_f, lookback_f


def _validate_bounds(start: Any, stop: Any) -> tuple[float | None, float | None]:
    start_f = None if start is None else _number(start, "start")
    stop_f = None if stop is None else _number(stop, "stop")
    if start_f is not None and stop_f is not None and start_f > stop_f:
        raise ValueError("start must not exceed stop")
    return start_f, stop_f


def _copy_episode_fields(episode: Mapping[str, Any] | None) -> dict[str, Any]:
    names = (
        "onset_t", "onset_lo", "onset_hi", "onset_method", "end_t", "end_lo",
        "end_hi", "end_method", "peak_mag", "confirmation", "n_onset_fit",
        "n_end_fit",
    )
    if episode is None:
        return {name: None for name in names}
    return {name: episode.get(name) for name in names}


def _prefix_episodes(rows: Sequence[Mapping[str, Any]], threshold: float, cutoff: float,
                    bright_first_at: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    episodes = [dict(e) for e in x4_episodes(list(rows), threshold)]
    episodes = [e for e in episodes if (_optional_number(e.get("peak_t")) is not None
                                        and _optional_number(e.get("peak_t")) < cutoff)]
    episodes.sort(key=lambda e: _optional_number(e.get("peak_t")))
    current_candidates = []
    for episode in episodes:
        reach = _optional_number(episode.get("end_hi"))
        if reach is None:
            reach = _optional_number(episode.get("peak_t"))
        if reach is not None and reach >= bright_first_at - _BOUNDARY_MARGIN:
            current_candidates.append(episode)
    return episodes, current_candidates


def _previous_fields(episodes: Sequence[Mapping[str, Any]], current: Mapping[str, Any] | None,
                     prefix_rows: Sequence[Mapping[str, Any]], threshold: float,
                     prefix_start: float) -> dict[str, Any]:
    result = {
        "previous_end_t": None,
        "previous_gap": None,
        "previous_longest_hole": None,
        "previous_gap_covered": None,
        "previous_duration": None,
        "earlier_gaps": [],
    }
    if current is None:
        return result
    current_onset = _optional_number(current.get("onset_t"))
    current_peak = _optional_number(current.get("peak_t"))
    if current_peak is None:
        return result
    current_position = next((i for i, e in enumerate(episodes) if e is current), len(episodes))
    candidates = []
    for episode in episodes[:current_position]:
        end_t = _optional_number(episode.get("end_t"))
        onset_lo = _optional_number(episode.get("onset_lo"))
        peak_t = _optional_number(episode.get("peak_t"))
        if (episode.get("confirmed_event") and end_t is not None and onset_lo is not None
                and onset_lo > prefix_start + 30.0 and peak_t is not None and peak_t < current_peak):
            candidates.append((peak_t, episode))
    if not candidates:
        return result
    previous = max(candidates, key=lambda item: item[0])[1]
    previous_end = _optional_number(previous.get("end_t"))
    previous_onset = _optional_number(previous.get("onset_t"))
    if previous_onset is not None and previous_onset > prefix_start + 30.0:
        result["previous_duration"] = _positive_duration(previous)
    visit_times = [_optional_number(v.get("t")) for v in visits(list(prefix_rows), threshold)]
    visit_times = sorted(t for t in visit_times if t is not None)

    def gap_metrics(end: float | None, onset: float | None) -> tuple[float, float, bool] | None:
        if end is None or onset is None or onset <= end:
            return None
        inside = [t for t in visit_times if end < t < onset]
        times = [end, *inside, onset]
        spacings = [right - left for left, right in zip(times, times[1:])]
        if not spacings:
            return None
        gap = onset - end
        return gap, max(spacings), max(spacings) <= _COVERAGE_DAYS

    metrics = gap_metrics(previous_end, current_onset)
    if metrics is not None:
        gap, longest_hole, covered = metrics
        result.update(
            previous_end_t=previous_end,
            previous_gap=gap,
            previous_longest_hole=longest_hole,
            previous_gap_covered=covered,
        )

    # Earlier gaps are formed from the confirmed episode sequence, stopping
    # before ``previous`` so the immediately preceding current gap is excluded.
    confirmed = [episode for episode in episodes[:current_position]
                 if episode.get("confirmed_event")]
    previous_confirmed_position = next(
        (i for i, episode in enumerate(confirmed) if episode is previous), None
    )
    if previous_confirmed_position is not None:
        earlier = []
        for older, newer in zip(confirmed[:previous_confirmed_position],
                                confirmed[1:previous_confirmed_position + 1]):
            older_onset = _optional_number(older.get("onset_t"))
            newer_onset = _optional_number(newer.get("onset_t"))
            if (older_onset is None or newer_onset is None or previous_onset is None
                    or older_onset <= prefix_start + 30.0
                    or newer_onset <= prefix_start + 30.0
                    or newer_onset > previous_onset):
                continue
            pair = gap_metrics(_optional_number(older.get("end_t")), newer_onset)
            if pair is None:
                continue
            earlier.append(math.log(pair[0])) if pair[2] else None
        result["earlier_gaps"] = earlier[-6:]
    return result


def forecast_features(rows: Sequence[Mapping[str, Any]], emission: Mapping[str, Any],
                      threshold: float = THRESHOLD, latency: float = 0,
                      lookback: float = 400) -> dict[str, Any]:
    """Build one forecast's prefix-causal feature record."""
    threshold_f, latency_f, lookback_f = _validate_parameters(threshold, latency, lookback)
    emitted_at = _number(emission.get("emitted_at"), "emission emitted_at")
    bright_first_at = _number(emission.get("bright_first_at"), "emission bright_first_at")
    emission_index = emission.get("emission_index")
    prefix_start = emitted_at - lookback_f
    prefix = [dict(row) for row in rows if prefix_start < _jd(row) <= emitted_at]
    prefix_jds = [_jd(row) for row in prefix]
    episodes, current_candidates = _prefix_episodes(prefix, threshold_f, emitted_at, bright_first_at)
    current = current_candidates[-1] if current_candidates else None
    copied = _copy_episode_fields(current)
    onset_t = _optional_number(copied["onset_t"])
    end_t = _optional_number(copied["end_t"])
    issue_time = emitted_at + latency_f
    result: dict[str, Any] = {
        "definition_version": DEFINITION_VERSION,
        "threshold": threshold_f,
        "emission_index": emission_index,
        "emitted_at": emitted_at,
        "issue_time": issue_time,
        "latency": latency_f,
        "bright_first_at": bright_first_at,
        "prefix_start": prefix_start,
        "prefix_rows": len(prefix),
        "prefix_last_jd": max(prefix_jds) if prefix_jds else None,
        "episode_found": current is not None,
        **copied,
        "duration": _positive_duration(current),
        "age_at_issue": issue_time - end_t if end_t is not None else None,
        "landmark_available": current is not None and end_t is not None and end_t <= emitted_at,
    }
    result.update(_previous_fields(episodes, current, prefix, threshold_f, prefix_start))
    return result


def forecast_ledger(rows: Sequence[Mapping[str, Any]], threshold: float = THRESHOLD,
                    latency: float = 0, lookback: float = 400, start: float | None = None,
                    stop: float | None = None) -> list[dict[str, Any]]:
    """Build and optionally issue-time-filter the complete causal forecast ledger."""
    threshold_f, latency_f, lookback_f = _validate_parameters(threshold, latency, lookback)
    start_f, stop_f = _validate_bounds(start, stop)
    emissions = [dict(e) for e in causal_confirmations(list(rows), threshold_f)]
    emissions.sort(key=lambda e: _number(e.get("emitted_at"), "emission emitted_at"))
    features = [forecast_features(rows, emission, threshold_f, latency_f, lookback_f)
                for emission in emissions]
    for previous, current in zip(features, features[1:]):
        previous_onset = _optional_number(previous.get("onset_t"))
        current_onset = _optional_number(current.get("onset_t"))
        current["repeat_of_previous"] = (
            previous_onset is not None and current_onset is not None
            and abs(current_onset - previous_onset) < 1.0
        )
    if features:
        features[0]["repeat_of_previous"] = False
    issue_times = [_number(f["issue_time"], "issue_time") for f in features]
    if any(right <= left for left, right in zip(issue_times, issue_times[1:])):
        raise ValueError("forecast issue times must be strictly increasing")
    return [f for f in features
            if (start_f is None or f["issue_time"] >= start_f)
            and (stop_f is None or f["issue_time"] < stop_f)]


def _record_end(rows: Sequence[Mapping[str, Any]], threshold: float, stop: Any) -> float:
    if stop is not None:
        return _number(stop, "stop")
    observed = visits(list(rows), threshold)
    times = [_optional_number(v.get("t")) for v in observed]
    times = [t for t in times if t is not None]
    if not times:
        raise ValueError("record end cannot be inferred from rows")
    return max(times)


def _coverage_time(visit_times: Sequence[float], issue: float, record_end: float) -> float | None:
    """Return the first C1/7 coverage-loss time, retaining gaps spanning issue."""
    times = sorted(t for t in visit_times if t <= record_end)
    before = [t for t in times if t <= issue]
    anchor = before[-1] if before else issue
    future = [t for t in times if t > issue]
    timeline = [anchor, *future, record_end]
    compact = []
    for value in timeline:
        if not compact or value != compact[-1]:
            compact.append(value)
    for left, right in zip(compact, compact[1:]):
        if right - left > _COVERAGE_DAYS and right > issue and left < record_end:
            return max(left, issue)
    return None


def _censor_point(coverage: float | None, next_issue: float | None,
                  record_end: float) -> tuple[float, str]:
    candidates = [(record_end, "record_end")]
    if coverage is not None:
        candidates.append((coverage, "coverage"))
    if next_issue is not None:
        candidates.append((next_issue, "superseded"))
    return min(candidates, key=lambda pair: (pair[0], pair[1]))


def outcome_evidence(rows: Sequence[Mapping[str, Any]], ledger: Sequence[Mapping[str, Any]],
                     threshold: float = THRESHOLD, stop: float | None = None) -> list[dict[str, Any]]:
    """Attach truth-free retrospective onset evidence to each forecast."""
    threshold_f, _, _ = _validate_parameters(threshold, 0, 1)
    record_end = _record_end(rows, threshold_f, stop)
    asof_rows = [dict(row) for row in rows if _jd(row) <= record_end]
    all_episodes = [dict(e) for e in x4_episodes(asof_rows, threshold_f)
                    if e.get("confirmed_event") and _optional_number(e.get("peak_t")) is not None]
    all_episodes.sort(key=lambda e: _optional_number(e.get("peak_t")))
    visit_times = [_optional_number(v.get("t")) for v in visits(asof_rows, threshold_f)]
    visit_times = sorted(t for t in visit_times if t is not None)
    ordered_ledger = [dict(f) for f in ledger]
    issue_times = [_number(f.get("issue_time"), "ledger issue_time") for f in ordered_ledger]
    if any(right <= left for left, right in zip(issue_times, issue_times[1:])):
        raise ValueError("ledger issue times must be strictly increasing")
    if len({f.get("emission_index") for f in ordered_ledger}) != len(ordered_ledger):
        raise ValueError("ledger emission indices must be unique")
    accepted: set[int] = set()
    evidence = []
    for position, forecast in enumerate(ordered_ledger):
        issue = issue_times[position]
        base = {
            "emission_index": forecast.get("emission_index"),
            "issue_time": issue,
            "computed_as_of": record_end,
            "evidence_available_at": record_end,
            "kind": None,
            "reason": None,
            "onset_lo": None,
            "onset_hi": None,
            "onset_t": None,
            "onset_method": None,
            "onset_index": None,
            "censor_at": None,
            "overtaken": False,
            "survival_ambiguous": False,
        }
        if issue >= record_end:
            base.update(kind="excluded", reason="outside_record")
            evidence.append(base)
            continue
        emitted_at = _number(forecast.get("emitted_at"), "ledger emitted_at")
        candidate_index, candidate = next(((i, episode) for i, episode in enumerate(all_episodes)
                                           if _optional_number(episode.get("peak_t")) is not None
                                           and _optional_number(episode.get("peak_t")) > emitted_at
                                           and _optional_number(episode.get("onset_hi")) is not None
                                           and _optional_number(episode.get("onset_hi")) > emitted_at),
                                          (None, None))
        if candidate is not None:
            candidate_hi = _optional_number(candidate.get("onset_hi"))
            candidate_lo = _optional_number(candidate.get("onset_lo"))
            if candidate_hi is not None and candidate_hi <= issue:
                base.update(kind="excluded", reason="overtaken", overtaken=True)
                evidence.append(base)
                continue
            if candidate_lo is None or candidate_lo <= issue:
                base.update(kind="excluded", reason="ambiguous_survival", survival_ambiguous=True)
                evidence.append(base)
                continue
        coverage = _coverage_time(visit_times, issue, record_end)
        next_issue = issue_times[position + 1] if position + 1 < len(issue_times) else None
        censor_at, reason = _censor_point(coverage, next_issue, record_end)
        if (candidate is not None and _optional_number(candidate.get("onset_hi")) is not None
                and _optional_number(candidate.get("onset_lo")) is not None
                and _optional_number(candidate.get("onset_lo")) > issue
                and _optional_number(candidate.get("onset_hi")) <= censor_at):
            onset_index = candidate_index
            if onset_index in accepted:
                raise AssertionError("an accepted onset was reused")
            accepted.add(onset_index)
            base.update(
                kind="interval", reason="onset",
                onset_lo=candidate.get("onset_lo"), onset_hi=candidate.get("onset_hi"),
                onset_t=candidate.get("onset_t"), onset_method=candidate.get("onset_method"),
                onset_index=onset_index,
            )
        else:
            base.update(kind="right_censored", reason=reason, censor_at=censor_at)
        evidence.append(base)
    return evidence


__all__ = ["DEFINITION_VERSION", "forecast_features", "forecast_ledger", "outcome_evidence"]
