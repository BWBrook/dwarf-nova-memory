"""Windowed point-clock and observed-clock predictors for gain-free R2 preparation."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
import hashlib
import json
import math
from statistics import median

from dnmem.extract import MIN_QUIET_NIGHTS, THRESHOLD, VISIT_SPAN, _nights, _runs, visits
from dnmem.extract_x3 import BAND
from dnmem.extract_x4 import SPLIT_GAP, causal_confirmations, x4_episodes
from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.prefix_features import COVERAGE_HOLE, LOOKBACK, PREVIOUS_MARGIN, forecast_features

DEFINITION_VERSION = "r2-windowed-features-v1"


def _finite(value):
    return value is not None and math.isfinite(value)


def _raw_run_metadata(observed):
    nights = _nights(observed)
    labels = {}
    for key, group in nights.items():
        bright = sum(v["cls"] == "B" for v in group)
        labels[key] = "B" if 2 * bright > len(group) else "F" if 2 * bright < len(group) else "M"
    runs = [(run, split) for run, split in _runs(sorted(nights), lambda k: labels[k] != "F", SPLIT_GAP)
            if any(labels[k] == "B" for k in run)]
    merged = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            previous, previous_split = merged.pop()
            run = previous + [k for k in sorted(nights) if previous[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    result = []
    for run, _ in merged:
        bright = sorted((v for key in run for v in nights[key] if v["cls"] == "B"),
                        key=lambda v: (v["t"], v["ids"][0]))
        peak = min(bright, key=lambda v: (v["value"], v["t"]))
        identity = hashlib.sha256(json.dumps(bright[0]["ids"], separators=(",", ":")).encode()).hexdigest()
        result.append({"raw_candidate_id": identity, "raw_peak_t": peak["t"],
                       "raw_peak_mag": peak["value"],
                       "raw_n_bright_observers": len({v["observer"] for v in bright})})
    return result


def _prefix_context(indexed, times, issue, threshold, lookback, clock):
    start = issue - lookback
    rows = indexed[bisect_right(times, start):bisect_right(times, issue)]
    if clock == "decisive":
        reports = [v for v in decisive_visits(rows, threshold) if v["available_at"] <= issue]
        identifiers = {identifier for v in reports for identifier in v["ids"]}
        rows = [row for row in rows if row["obsID"] in identifiers]
        candidates = x4_episodes(rows, threshold)
        episodes = x5_episodes(rows, threshold, episodes=candidates, votes=reports)
        observed = reports
    else:
        observed = visits(rows, threshold)
        episodes = x4_episodes(rows, threshold)
    metadata = _raw_run_metadata(observed)
    if len(episodes) != len(metadata):
        raise ValueError("raw candidate run count differs from X4")
    enriched = []
    for episode, raw in zip(episodes, metadata):
        if episode["peak_t"] != raw["raw_peak_t"] or episode["peak_mag"] != raw["raw_peak_mag"]:
            raise ValueError("raw candidate peak differs from X4")
        if episode["peak_t"] < issue:
            enriched.append({**episode, **raw})
    return {"rows": rows, "episodes": enriched, "observed": observed,
            "times": sorted(v["t"] for v in observed), "prefix_start": start,
            "prefix_last_jd": max((float(row["JD"]) for row in rows), default=None)}


def _longest_hole(times, start, stop):
    interior = times[bisect_right(times, start):bisect_left(times, stop)]
    anchors = [start] + interior + [stop]
    return max(b - a for a, b in zip(anchors, anchors[1:]))


def _endpoint_pair(left, right, context, issue, clock):
    edge = context["prefix_start"] + PREVIOUS_MARGIN
    if clock == "point":
        if not left["confirmed_event"] or not right["confirmed_event"]:
            return None, "unconfirmed_adjacent_candidate"
        if not all(_finite(e.get("onset_lo")) and e["onset_lo"] > edge for e in (left, right)):
            return None, "incomplete_window_onset"
        start, stop = left.get("end_t"), right.get("onset_t")
        if not _finite(start) or not _finite(stop) or max(start, stop) > issue:
            return None, "unavailable_point_endpoint"
    else:
        if min(left["raw_n_bright_observers"], right["raw_n_bright_observers"]) < 2:
            return None, "insufficient_raw_bright_observers"
        if not all(e["onset_report_eligible"] and e["onset_report_lo"] > edge for e in (left, right)):
            return None, "incomplete_window_onset"
        if not left["end_report_eligible"] or left["end_lower_first_at"] <= context["prefix_start"]:
            return None, "unavailable_decisive_end"
        start, stop = left["end_decisive_at"], right["onset_report_lo"]
        available = max(left["end_decisive_available_at"], right["onset_upper_first_at"] + VISIT_SPAN)
        if available > issue or start is None or stop is None:
            return None, "decisive_endpoint_not_available"
    if stop <= start:
        return None, "nonpositive_adjacent_gap"
    return (start, stop), None


def _gap_history(context, current, issue, clock):
    episodes = context["episodes"]
    history = []
    for left, right in zip(episodes[:current], episodes[1:current + 1]):
        endpoints, reason = _endpoint_pair(left, right, context, issue, clock)
        raw_gap, longest, covered, logged = None, None, None, None
        if endpoints is not None:
            raw_gap = endpoints[1] - endpoints[0]
            longest = _longest_hole(context["times"], *endpoints)
            covered = longest <= COVERAGE_HOLE
            logged = math.log(raw_gap) if covered else None
            reason = "covered_adjacent_gap" if covered else "coverage_hole"
        history.append({"gap_id": left["raw_candidate_id"] + ":" + right["raw_candidate_id"],
                        "left_candidate_id": left["raw_candidate_id"],
                        "right_candidate_id": right["raw_candidate_id"],
                        "log_gap": logged, "available_at": issue, "raw_gap": raw_gap,
                        "covered": covered, "longest_hole": longest, "reason": reason})
    if len({entry["gap_id"] for entry in history}) != len(history):
        raise ValueError("duplicate timing observation in one feature history")
    return history


def _base_feature(emission, issue, clock, context):
    return {"definition_version": DEFINITION_VERSION, "clock": clock,
            "emission_index": emission["emission_index"], "original_issue_time": emission["emitted_at"],
            "original_bright_first_at": emission["bright_first_at"],
            "original_last_bright_at": emission["last_bright_at"],
            "issue_time": issue, "available_at": issue, "clock_anchor": None, "mark": None,
            "previous_gap": None, "previous_gap_covered": None, "gap_history": [],
            "candidate_id": None, "event_eligible": False, "status": None,
            "prefix_start": context["prefix_start"], "prefix_last_jd": context["prefix_last_jd"],
            "prefix_rows": len(context["rows"]), "prefix_candidates": len(context["episodes"])}


def bright_span_flux_proxy(observed, emission, issue, threshold=THRESHOLD, margin=BAND):
    """Observer-balanced threshold-excess proxy on an observed bright span.

    This is neither complete outburst fluence nor quiescence-subtracted energy.
    Visits are positive and closed; limits never become exact flux values.
    """
    lower = emission["bright_first_at"] - VISIT_SPAN
    upper = emission["last_bright_at"]
    positive = [v for v in observed if v["value"] is not None and v["available_at"] <= issue
                and lower <= v["t"] <= upper]
    decisive = sorted({v["t"] for v in positive if v["value"] <= threshold - margin})
    result = {"status": "no_decisive_bright_span", "value_threshold_flux_days": None,
              "units": "days times positive flux excess relative to threshold flux",
              "threshold": threshold, "margin": margin, "span_start": None, "span_stop": None,
              "support_start": None, "support_stop": None, "raw_visit_support_start": None,
              "raw_visit_support_stop": None, "positive_closed_visits_in_causal_range": len(positive),
              "positive_visits": 0, "observer_nights": 0,
              "balanced_night_points": 0, "internal_gaps_days": [], "maximum_internal_gap_days": None,
              "available_at": issue,
              "reducer": "median magnitude/time per observer-night, then median across observers per night",
              "support_policy": "observed night points only; no extrapolation to bright-span edges"}
    if len(decisive) < 2:
        return result
    start, stop = decisive[0], decisive[-1]
    positive = [v for v in positive if start <= v["t"] <= stop]
    groups = {}
    for v in positive:
        groups.setdefault((v["observer"], math.floor(v["t"])), []).append(v)
    nights = {}
    for (_, night), group in groups.items():
        nights.setdefault(night, []).append((median(v["t"] for v in group), median(v["value"] for v in group)))
    balanced = sorted((median(t for t, _ in group), median(m for _, m in group)) for group in nights.values())
    result.update(span_start=start, span_stop=stop, positive_visits=len(positive), observer_nights=len(groups),
                  balanced_night_points=len(balanced),
                  raw_visit_support_start=min(v["first_at"] for v in positive),
                  raw_visit_support_stop=max(v["last_at"] for v in positive),
                  support_start=balanced[0][0], support_stop=balanced[-1][0])
    if len(balanced) < 2:
        result["status"] = "fewer_than_two_balanced_nights"
        return result
    gaps = [right[0] - left[0] for left, right in zip(balanced, balanced[1:])]
    result.update(internal_gaps_days=gaps, maximum_internal_gap_days=max(gaps))
    if max(gaps) > COVERAGE_HOLE:
        result["status"] = "internal_gap_over_seven_days"
        return result
    excess = [(t, max(10 ** (-.4 * (m - threshold)) - 1, 0.0)) for t, m in balanced]
    area = math.fsum((right[0] - left[0]) * (left[1] + right[1]) / 2
                     for left, right in zip(excess, excess[1:]))
    result.update(status="available", value_threshold_flux_days=area)
    return result


def _attach_history(feature, context, current, issue, clock):
    history = _gap_history(context, current, issue, clock)
    feature["gap_history"] = history
    if history:
        latest = history[-1]
        feature["previous_gap"] = latest["raw_gap"] if latest["log_gap"] is not None else None
        feature["previous_gap_covered"] = latest["covered"]


def point_feature(indexed, times, emission, issue, threshold=THRESHOLD, lookback=LOOKBACK):
    context = _prefix_context(indexed, times, issue, threshold, lookback, "point")
    feature = _base_feature(emission, issue, "point", context)
    feature["flux_proxy"] = bright_span_flux_proxy(decisive_visits(context["rows"], threshold), emission, issue, threshold)
    since = emission["bright_first_at"] - VISIT_SPAN - 1.0
    episodes = context["episodes"]
    current = next((i for i in range(len(episodes) - 1, -1, -1)
                    if (episodes[i]["end_hi"] if episodes[i]["end_hi"] is not None else episodes[i]["peak_t"]) >= since), None)
    frozen = forecast_features(context["rows"], {**emission, "emitted_at": issue}, threshold, lookback=lookback)
    feature["frozen_point_reference"] = {key: frozen[key] for key in (
        "duration", "previous_gap", "previous_gap_covered", "earlier_gaps", "landmark_available", "end_t", "onset_t")}
    if current is None:
        feature["status"] = "point_candidate_not_found"
        return feature
    e = episodes[current]
    feature["candidate_id"] = e["raw_candidate_id"]
    feature["event_eligible"] = True
    anchor, onset = e.get("end_t"), e.get("onset_t")
    if _finite(anchor) and anchor <= issue:
        feature["clock_anchor"] = anchor
        feature["status"] = "point_clock_available"
        if _finite(onset) and anchor > onset:
            feature["mark"] = anchor - onset
    else:
        feature["status"] = "point_clock_unavailable"
    _attach_history(feature, context, current, issue, "point")
    return feature


def decoupled_schedule(emissions, observed, stop=None):
    closed = sorted(observed, key=lambda v: (v["available_at"], v["observer"]))
    decisive_faint = [v for v in closed if v["decisive"] == "F"]
    availability = [v["available_at"] for v in decisive_faint]
    bright = [v["available_at"] for v in closed if v["cls"] == "B"]
    audit = []
    for emission in emissions:
        original = emission["emitted_at"]
        first = bisect_right(availability, emission["last_bright_at"])
        selected = decisive_faint[first] if first < len(decisive_faint) else None
        issue = max(original, selected["available_at"]) if selected else None
        row = {"emission_index": emission["emission_index"], "original_issue_time": original,
               "original_bright_first_at": emission["bright_first_at"],
               "original_last_bright_at": emission["last_bright_at"],
               "issue_time": issue, "anchor": selected["last_at"] if selected else None,
               "anchor_available_at": selected["available_at"] if selected else None,
               "status": "scheduled", "delay_days": issue - original if issue is not None else None}
        if selected is None:
            row["status"] = "no_decisive_faint_before_record_end"
        elif stop is not None and issue >= stop:
            row["status"] = "past_issue_cutoff"
        elif bisect_right(bright, issue) > bisect_right(bright, original):
            row["status"] = "aborted_bright_before_delayed_issue"
        audit.append(row)
    issued = [r["issue_time"] for r in audit if r["status"] == "scheduled"]
    if any(right <= left for left, right in zip(issued, issued[1:])):
        raise ValueError("DF schedule does not have unique increasing issue times")
    return audit


def decisive_feature(indexed, times, emission, schedule, threshold=THRESHOLD, lookback=LOOKBACK):
    issue = schedule["issue_time"]
    context = _prefix_context(indexed, times, issue, threshold, lookback, "decisive")
    feature = _base_feature(emission, issue, "decisive", context)
    feature["flux_proxy"] = bright_span_flux_proxy(context["observed"], emission, issue, threshold)
    feature.update(anchor_available_at=schedule["anchor_available_at"], issue_delay_days=schedule["delay_days"])
    lower, upper = emission["bright_first_at"] - VISIT_SPAN, emission["last_bright_at"]
    matches = [(i, e) for i, e in enumerate(context["episodes"]) if lower <= e["raw_peak_t"] <= upper]
    feature["raw_association_candidates"] = len(matches)
    if len(matches) != 1:
        feature["status"] = "raw_candidate_not_found" if not matches else "raw_candidate_ambiguous"
        return feature
    current, e = matches[0]
    feature["candidate_id"] = e["raw_candidate_id"]
    feature["raw_n_bright_observers"] = e["raw_n_bright_observers"]
    feature["current_raw_peak_at"] = e["raw_peak_t"]
    _attach_history(feature, context, current, issue, "decisive")
    if e["raw_n_bright_observers"] < 2:
        feature["status"] = "insufficient_raw_bright_observers"
        return feature
    feature.update(event_eligible=True, clock_anchor=schedule["anchor"], status="decisive_clock_available")
    bright = [v for v in context["observed"] if v["decisive"] == "B" and lower <= v["t"] <= upper]
    epochs = sorted({v["t"] for v in bright})
    feature["decisive_bright_times"] = len(epochs)
    feature["mark"] = epochs[-1] - epochs[0] if len(epochs) >= 2 else None
    first_postpeak = e["end_decisive_at"]
    feature["x5_first_postpeak_faint_anchor"] = first_postpeak
    feature["scheduled_minus_x5_anchor_days"] = schedule["anchor"] - first_postpeak if first_postpeak is not None else None
    if not schedule["anchor_available_at"] <= issue or not schedule["anchor"] <= issue:
        raise ValueError("DF anchor is not available by issue")
    return feature


def prepare_feature_ledgers(rows, threshold=THRESHOLD, *, emissions=None, start=None, stop=None,
                            lookback=LOOKBACK):
    if not math.isfinite(threshold) or not math.isfinite(lookback) or lookback <= 0:
        raise ValueError("threshold and positive lookback must be finite")
    if any(value is not None and not math.isfinite(value) for value in (start, stop)):
        raise ValueError("issue cutoffs must be finite")
    if start is not None and stop is not None and start > stop:
        raise ValueError("issue window is reversed")
    indexed = sorted((r for r in rows if r["band"] == "Vis." and r["val"] == "V"
                      and (stop is None or float(r["JD"]) < stop)), key=lambda r: (float(r["JD"]), r["obsID"]))
    times = [float(r["JD"]) for r in indexed]
    original = causal_confirmations(indexed, threshold) if emissions is None else list(emissions)
    original = [e for e in original if stop is None or e["emitted_at"] < stop]
    if (len({e["emission_index"] for e in original}) != len(original)
            or any(b["emitted_at"] <= a["emitted_at"] for a, b in zip(original, original[1:]))):
        raise ValueError("original emissions must have unique IDs and increasing issues")
    observed = decisive_visits(indexed, threshold, BAND)
    audit = decoupled_schedule(original, observed, stop)
    by_index = {e["emission_index"]: e for e in original}
    point_original = [point_feature(indexed, times, e, e["emitted_at"], threshold, lookback)
                      for e in original if start is None or e["emitted_at"] >= start]
    df, matched = [], []
    for schedule in audit:
        issue = schedule["issue_time"]
        if schedule["status"] != "scheduled" or (start is not None and issue < start):
            continue
        emission = by_index[schedule["emission_index"]]
        df.append(decisive_feature(indexed, times, emission, schedule, threshold, lookback))
        matched.append(point_feature(indexed, times, emission, issue, threshold, lookback))
    for feature in point_original + df + matched:
        if feature["available_at"] > feature["issue_time"] or any(
                h["available_at"] > feature["issue_time"] for h in feature["gap_history"]):
            raise ValueError("feature history contains future information")
    return {"point_original": point_original, "df": df, "point_at_df": matched,
            "df_schedule_audit": audit}


__all__ = ["DEFINITION_VERSION", "prepare_feature_ledgers", "decoupled_schedule",
           "point_feature", "decisive_feature", "bright_span_flux_proxy"]
