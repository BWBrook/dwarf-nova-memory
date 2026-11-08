"""Prefix-causal forecast predictors and truth-free outcome evidence (A10, proposed).

A forecast is issued at each X4 causal end confirmation. Its predictors come from
X4 applied only to rows observed at or before the emission time, so no later
observation can change them. Outcome evidence comes separately from retrospective
X4 on the full record and is never an input to a predictor.
"""

import math

from dnmem.extract import visits
from dnmem.extract_x4 import THRESHOLD, VISIT_SPAN, causal_confirmations, x4_episodes

DEFINITION_VERSION = "a10-prefix-v2"
LOOKBACK = 400.0
COVERAGE_HOLE = 7.0
PREVIOUS_MARGIN = 30.0


def prefix_rows(rows: list[dict], cutoff: float, lookback: float = LOOKBACK) -> list[dict]:
    return [r for r in rows if cutoff - lookback < float(r["JD"]) <= cutoff]


def _longest_hole(times: list[float], start: float, stop: float) -> tuple[float, float | None]:
    anchors = [start] + [t for t in times if start < t < stop] + [stop]
    holes = [(b - a, a) for a, b in zip(anchors, anchors[1:])]
    longest = max(h for h, _ in holes)
    return longest, next((a for h, a in holes if h > COVERAGE_HOLE), None)


def forecast_features(rows: list[dict], emission: dict, threshold: float = THRESHOLD,
                      latency: float = 0.0, lookback: float = LOOKBACK) -> dict:
    """Predictors for one emission, computed from rows with JD <= emitted_at only."""
    if not math.isfinite(latency) or latency < 0 or not math.isfinite(lookback) or lookback <= 0:
        raise ValueError("latency must be nonnegative and lookback positive")
    cutoff = emission["emitted_at"]
    window = prefix_rows(rows, cutoff, lookback)
    episodes = [e for e in x4_episodes(window, threshold) if e["peak_t"] < cutoff] if window else []
    since = emission["bright_first_at"] - VISIT_SPAN - 1.0
    current = next((i for i in range(len(episodes) - 1, -1, -1)
                    if (episodes[i]["end_hi"] if episodes[i]["end_hi"] is not None else episodes[i]["peak_t"]) >= since),
                   None)
    record = {"definition_version": DEFINITION_VERSION, "threshold": threshold,
              "emission_index": emission["emission_index"], "emitted_at": cutoff,
              "issue_time": cutoff + latency, "latency": latency, "bright_first_at": emission["bright_first_at"],
              "prefix_start": cutoff - lookback, "prefix_rows": len(window),
              "prefix_last_jd": max((float(r["JD"]) for r in window), default=None),
              "episode_found": current is not None, "landmark_available": False}
    keys = ("onset_t", "onset_lo", "onset_hi", "onset_method", "end_t", "end_lo", "end_hi", "end_method",
            "peak_mag", "confirmation", "n_onset_fit", "n_end_fit")
    if current is None:
        record.update({k: None for k in keys})
        record.update(duration=None, age_at_issue=None, previous_end_t=None, previous_gap=None,
                      previous_gap_covered=None, previous_longest_hole=None)
        return record
    e = episodes[current]
    record.update({k: e[k] for k in keys})
    ok = e["onset_t"] is not None and e["end_t"] is not None
    record["duration"] = e["end_t"] - e["onset_t"] if ok else None
    record["age_at_issue"] = record["issue_time"] - e["end_t"] if e["end_t"] is not None else None
    record["landmark_available"] = bool(e["end_t"] is not None and math.isfinite(e["end_t"])
                                         and e["end_t"] <= cutoff)
    earlier = [p for p in episodes[:current] if p["confirmed_event"] and p["end_t"] is not None
               and p["onset_lo"] is not None and p["onset_lo"] > cutoff - lookback + PREVIOUS_MARGIN]
    if earlier and e["onset_t"] is not None and earlier[-1]["end_t"] < e["onset_t"]:
        p = earlier[-1]
        times = sorted(v["t"] for v in visits(window, threshold))
        longest, _ = _longest_hole(times, p["end_t"], e["onset_t"])
        record.update(previous_end_t=p["end_t"], previous_gap=e["onset_t"] - p["end_t"],
                      previous_gap_covered=longest <= COVERAGE_HOLE, previous_longest_hole=longest)
    else:
        record.update(previous_end_t=None, previous_gap=None, previous_gap_covered=None,
                      previous_longest_hole=None)
    return record


def forecast_ledger(rows: list[dict], threshold: float = THRESHOLD, latency: float = 0.0,
                    lookback: float = LOOKBACK, start: float | None = None, stop: float | None = None) -> list[dict]:
    """One immutable predictor record per causal emission issued in [start, stop)."""
    if not math.isfinite(latency) or latency < 0 or not math.isfinite(lookback) or lookback <= 0:
        raise ValueError("latency must be nonnegative and lookback positive")
    if ((start is not None and not math.isfinite(start)) or (stop is not None and not math.isfinite(stop))
            or (start is not None and stop is not None and stop < start)):
        raise ValueError("invalid issue window")
    ledger = []
    previous = None
    for emission in causal_confirmations(rows, threshold):
        record = forecast_features(rows, emission, threshold, latency, lookback)
        record["repeat_of_previous"] = bool(
            previous and record["onset_t"] is not None and previous["onset_t"] is not None
            and abs(record["onset_t"] - previous["onset_t"]) < 1.0)
        previous = record
        t = record["issue_time"]
        if (start is None or t >= start) and (stop is None or t < stop):
            ledger.append(record)
    return ledger


def _coverage_loss(times: list[float], issue: float, stop: float) -> float | None:
    earlier = [t for t in times if t <= issue]
    anchors = [earlier[-1] if earlier else issue]
    anchors.extend(t for t in times if issue < t <= stop)
    anchors.append(stop)
    return next((max(a, issue) for a, b in zip(anchors, anchors[1:])
                 if b - a > COVERAGE_HOLE and b > issue and a < stop), None)


def outcome_evidence(rows: list[dict], ledger: list[dict], threshold: float = THRESHOLD,
                     stop: float | None = None) -> list[dict]:
    """Common as-of evidence; excludes overtaken or ambiguous survival.

    Availability is conservatively the supplied as-of cutoff. Only frozen fits
    to separately recomputed training-prefix evidence are supported.
    """
    if any(b["issue_time"] <= a["issue_time"] for a, b in zip(ledger, ledger[1:])):
        raise ValueError("ledger issue times must be strictly increasing")
    record_end = stop if stop is not None else max((v["t"] for v in visits(rows, threshold)), default=0.0)
    if not math.isfinite(record_end):
        raise ValueError("record end must be finite")
    rows = [r for r in rows if float(r["JD"]) <= record_end]
    episodes = sorted((e for e in x4_episodes(rows, threshold) if e["confirmed_event"]),
                      key=lambda e: e["peak_t"])
    times = sorted(v["t"] for v in visits(rows, threshold))
    out = []
    assigned = set()
    for i, f in enumerate(ledger):
        tau = f["issue_time"]
        candidate = next(((j, e) for j, e in enumerate(episodes)
                          if e["peak_t"] > f["emitted_at"] and e["onset_hi"] is not None
                          and e["onset_hi"] > f["emitted_at"]), None)
        nxt = candidate[1] if candidate else None
        evidence = {"emission_index": f["emission_index"], "issue_time": tau,
                    "computed_as_of": record_end, "evidence_available_at": record_end,
                    "kind": None, "reason": None, "onset_lo": None, "onset_hi": None,
                    "onset_t": None, "onset_method": None, "onset_index": None,
                    "censor_at": None, "overtaken": False, "survival_ambiguous": False}
        if tau >= record_end:
            evidence.update(kind="excluded", reason="outside_record")
        elif nxt is not None and nxt["onset_hi"] <= tau:
            evidence.update(kind="excluded", reason="overtaken", overtaken=True)
        elif nxt is not None and (nxt["onset_lo"] is None or nxt["onset_lo"] <= tau):
            evidence.update(kind="excluded", reason="ambiguous_survival", survival_ambiguous=True)
        if evidence["kind"] is not None:
            out.append(evidence)
            continue
        hole = _coverage_loss(times, tau, record_end)
        superseded = ledger[i + 1]["issue_time"] if i + 1 < len(ledger) else None
        stops = [(t, why) for t, why in ((hole, "coverage"), (superseded, "superseded"), (record_end, "record_end"))
                 if t is not None]
        censor_at, why = min(stops)
        if nxt is not None and nxt["onset_hi"] <= censor_at:
            if candidate[0] in assigned:
                raise ValueError("confirmed onset credited to multiple forecasts")
            assigned.add(candidate[0])
            evidence.update(kind="interval", onset_lo=nxt["onset_lo"], onset_hi=nxt["onset_hi"],
                            onset_t=nxt["onset_t"], onset_method=nxt["onset_method"],
                            onset_index=candidate[0], reason="onset")
        else:
            evidence.update(kind="right_censored", censor_at=max(censor_at, tau), reason=why)
        out.append(evidence)
    return out
