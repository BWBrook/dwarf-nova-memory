"""Prospective working-set outcome routing; frozen A10 v3 remains unchanged.

An onset working interval (L, U] crossing a stopping cutoff C supplies, under
that working-set approximation, only the lower bound L. This version backs
censoring off to L when issue < L < C < U. It does not certify physical
survival: X4's posterior intervals and decisive reports are not proven hard
bounds. This module is not used by the frozen A10 evaluation.
"""

from __future__ import annotations

from bisect import bisect_right
import math

from .extract import visits
from .extract_x4 import THRESHOLD, x4_episodes

DEFINITION_VERSION = "a10-outcome-evidence-v4"
COVERAGE_DAYS = 7.0


def _finite(value: object, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def outcome_evidence(rows: list[dict], ledger: list[dict], threshold: float = THRESHOLD,
                     stop: float | None = None) -> list[dict]:
    """Retain v3 candidates, issue exclusions and stopping causes, with backoff."""
    threshold = _finite(threshold, "threshold")
    record_end = _finite(stop, "stop") if stop is not None else max(
        (v["t"] for v in visits(rows, threshold)), default=0.0)
    forecasts = list(ledger)
    issues = [_finite(f["issue_time"], "issue_time") for f in forecasts]
    emissions = [_finite(f["emitted_at"], "emitted_at") for f in forecasts]
    if any(right <= left for left, right in zip(issues, issues[1:])):
        raise ValueError("ledger issue times must be strictly increasing")
    if len({f["emission_index"] for f in forecasts}) != len(forecasts):
        raise ValueError("ledger emission indices must be unique")
    if any(emission > issue for emission, issue in zip(emissions, issues)):
        raise ValueError("emission cannot follow issue")
    asof = [row for row in rows if _finite(row["JD"], "JD") <= record_end]
    episodes = sorted((episode for episode in x4_episodes(asof, threshold)
                       if episode["confirmed_event"]), key=lambda e: e["peak_t"])
    peaks = [episode["peak_t"] for episode in episodes]
    times = sorted(v["t"] for v in visits(asof, threshold))
    gaps = [(left, right) for left, right in zip(times, times[1:]) if right - left > COVERAGE_DAYS]
    gap_ends = [right for _, right in gaps]
    accepted = set()
    result = []
    for position, forecast in enumerate(forecasts):
        issue, emission = issues[position], emissions[position]
        chosen = next(((index, episodes[index]) for index in range(bisect_right(peaks, emission), len(episodes))
                       if episodes[index].get("onset_hi") is not None and episodes[index]["onset_hi"] > emission),
                      (None, None))
        index, episode = chosen
        lo = episode.get("onset_lo") if episode is not None else None
        hi = episode.get("onset_hi") if episode is not None else None
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("candidate onset bounds are reversed")
        evidence = {
            "emission_index": forecast["emission_index"], "issue_time": issue,
            "computed_as_of": record_end, "evidence_available_at": record_end,
            "evidence_definition_version": DEFINITION_VERSION,
            "kind": None, "reason": None,
            "onset_lo": None, "onset_hi": None, "onset_t": None,
            "onset_method": None, "onset_index": None, "censor_at": None,
            "overtaken": False, "survival_ambiguous": False,
            "candidate_index": index, "candidate_onset_lo": lo, "candidate_onset_hi": hi,
            "stopping_cutoff": None, "stopping_reason": None,
            "censor_backoff": False, "censor_backoff_days": 0.0, "censor_rule": None,
        }
        if issue >= record_end:
            evidence.update(kind="excluded", reason="outside_record")
        elif hi is not None and hi <= issue:
            evidence.update(kind="excluded", reason="overtaken", overtaken=True)
        elif episode is not None and (lo is None or lo <= issue):
            evidence.update(kind="excluded", reason="ambiguous_survival", survival_ambiguous=True)
        if evidence["kind"] is not None:
            result.append(evidence)
            continue
        coverage = None
        if not times:
            coverage = issue if record_end - issue > COVERAGE_DAYS else None
        elif issue < times[0] and times[0] - issue > COVERAGE_DAYS:
            coverage = issue
        else:
            gap = bisect_right(gap_ends, issue)
            if gap < len(gaps):
                coverage = max(issue, gaps[gap][0])
            elif record_end - times[-1] > COVERAGE_DAYS:
                coverage = max(issue, times[-1])
        stops = [(record_end, "record_end")]
        if coverage is not None:
            stops.append((coverage, "coverage"))
        if position + 1 < len(issues):
            stops.append((issues[position + 1], "superseded"))
        cutoff, cause = min(stops)
        evidence.update(stopping_cutoff=cutoff, stopping_reason=cause)
        if hi is not None and hi <= cutoff:
            if index in accepted:
                raise ValueError("confirmed onset credited to multiple forecasts")
            accepted.add(index)
            evidence.update(kind="interval", reason="onset", onset_lo=lo, onset_hi=hi,
                            onset_t=episode.get("onset_t"), onset_method=episode.get("onset_method"),
                            onset_index=index)
        else:
            backoff = lo is not None and lo < cutoff
            evidence.update(kind="right_censored", reason=cause, censor_at=lo if backoff else cutoff,
                            censor_backoff=backoff, censor_backoff_days=cutoff - lo if backoff else 0.0,
                            censor_rule="working_set_lower_bound" if backoff else "stopping_cutoff")
        result.append(evidence)
    return result


__all__ = ["DEFINITION_VERSION", "outcome_evidence"]
