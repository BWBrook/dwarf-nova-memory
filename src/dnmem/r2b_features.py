"""R2b causal observed clocks, harmonized scheduled-anchor histories and controls."""

from __future__ import annotations

from bisect import bisect_right
import math

from dnmem.extract import THRESHOLD, VISIT_SPAN
from dnmem.extract_x3 import BAND
from dnmem.extract_x4 import causal_confirmations
from dnmem.extract_x5 import decisive_visits
from dnmem.prefix_features import COVERAGE_HOLE, LOOKBACK, PREVIOUS_MARGIN, forecast_features
from dnmem import r2_features as previous

DEFINITION_VERSION = "r2b-scheduled-anchor-features-v2"


def decoupled_schedule(emissions, observed, stop=None):
    closed = sorted(observed, key=lambda v: (v["available_at"], v["observer"]))
    faint = [v for v in closed if v["decisive"] == "F"]
    faint_availability = [v["available_at"] for v in faint]
    bright_availability = [v["available_at"] for v in closed if v["decisive"] == "B"]
    audit = []
    for emission in emissions:
        original = emission["emitted_at"]
        index = bisect_right(faint_availability, emission["last_bright_at"])
        selected = faint[index] if index < len(faint) else None
        issue = max(original, selected["available_at"]) if selected else None
        status = "scheduled"
        if selected is None:
            status = "no_decisive_faint_before_record_end"
        elif stop is not None and issue >= stop:
            status = "past_issue_cutoff"
        elif bisect_right(bright_availability, issue) > bisect_right(bright_availability, original):
            status = "aborted_decisive_bright_before_delayed_issue"
        audit.append({"emission_index": emission["emission_index"],
                      "original_issue_time": original,
                      "original_bright_first_at": emission["bright_first_at"],
                      "original_last_bright_at": emission["last_bright_at"],
                      "issue_time": issue,
                      "anchor": selected["last_at"] if selected else None,
                      "anchor_first_at": selected["first_at"] if selected else None,
                      "anchor_available_at": selected["available_at"] if selected else None,
                      "delay_days": issue - original if issue is not None else None,
                      "coincident_with_emission_index": None,
                      "status": status})
    representatives = {}
    for row in audit:
        if row["status"] != "scheduled":
            continue
        key = (row["issue_time"], row["anchor"], row["anchor_first_at"], row["anchor_available_at"])
        if key in representatives:
            row.update(status="coincident_pending_issue",
                       coincident_with_emission_index=representatives[key])
        else:
            representatives[key] = row["emission_index"]
    issued = [s["issue_time"] for s in audit if s["status"] == "scheduled"]
    if any(right <= left for left, right in zip(issued, issued[1:])):
        raise ValueError("DF schedule does not have unique increasing issue times")
    return audit


def _cadence_result(status="not_available"):
    return {"value_days": None, "available_at": None,
            "lower_raw_at": None, "upper_raw_at": None, "status": status}


def cadence_gaps(context, schedule, episode, issue, threshold=THRESHOLD, margin=BAND):
    """Raw positive-report gaps; numerical limits never become exact positives."""
    observed = [v for v in context["observed"] if v["available_at"] <= issue]
    row_by_id = {r["obsID"]: r for r in context["rows"]}
    positive = [(float(row_by_id[i]["JD"]), v["available_at"])
                for v in observed for i in v["ids"]
                if row_by_id[i]["fainterThan"] == "0"
                and float(row_by_id[i]["mag"]) < threshold + margin]
    end, onset = _cadence_result("no_prior_positive"), _cadence_result("no_eligible_onset_window")
    if schedule is not None and schedule["anchor_available_at"] <= issue:
        before = [(t, available) for t, available in positive if t < schedule["anchor_first_at"]]
        if before:
            lower, available = max(before)
            end = {"value_days": schedule["anchor"] - lower,
                   "available_at": max(available, schedule["anchor_available_at"]),
                   "lower_raw_at": lower, "upper_raw_at": schedule["anchor"],
                   "status": "available"}
    if episode is not None and episode["onset_report_eligible"]:
        lower = episode["onset_lower_last_at"]
        after = [(t, available) for t, available in positive if t > lower]
        if after:
            upper, available = min(after)
            onset = {"value_days": upper - lower,
                     "available_at": max(available, episode["onset_lower_first_at"] + VISIT_SPAN),
                     "lower_raw_at": lower, "upper_raw_at": upper, "status": "available"}
        else:
            onset = _cadence_result("no_subsequent_positive")
    return end, onset


def observing_rate(observed, emission, issue, threshold=THRESHOLD, margin=BAND):
    lower, upper = emission["bright_first_at"] - VISIT_SPAN, emission["last_bright_at"]
    closed = [v for v in observed if v["available_at"] <= issue and lower <= v["t"] <= upper]
    bright_times = sorted({v["t"] for v in closed if v["decisive"] == "B"})
    result = {"value_per_day": None, "log_value": None, "available_at": None,
              "observer_nights": 0, "span_start": None, "span_stop": None,
              "status": "no_decisive_bright_span",
              "definition": "all closed observer-night visits within the decisive-bright span / (span+1 day)"}
    if len(bright_times) < 2:
        return result
    start, stop = bright_times[0], bright_times[-1]
    included = [v for v in closed if start <= v["t"] <= stop]
    count = len({(v["observer"], math.floor(v["t"])) for v in included})
    rate = count / (stop - start + 1.0)
    result.update(value_per_day=rate, log_value=math.log(rate),
                  available_at=max(v["available_at"] for v in included), observer_nights=count,
                  span_start=start, span_stop=stop, status="available")
    return result


def _scheduled_anchor(episode, schedules, emissions, issue):
    matches = []
    for index, schedule in schedules.items():
        emission = emissions[index]
        if (schedule["status"] == "scheduled" and schedule["issue_time"] <= issue
                and emission["bright_first_at"] - VISIT_SPAN <= episode["raw_peak_t"] <= emission["last_bright_at"]):
            matches.append(schedule)
    if len(matches) != 1:
        return None, "no_scheduled_anchor" if not matches else "ambiguous_scheduled_anchor"
    if matches[0]["anchor"] <= episode["raw_peak_t"]:
        return None, "scheduled_anchor_not_after_peak"
    return matches[0], None


def _gap_history(context, current, issue, schedules, emissions, threshold=THRESHOLD):
    episodes = context["episodes"]
    edge = context["prefix_start"] + PREVIOUS_MARGIN
    history = []
    for left, right in zip(episodes[:current], episodes[1:current + 1]):
        schedule, reason = _scheduled_anchor(left, schedules, emissions, issue)
        raw_gap = longest = covered = logged = None
        end = onset = _cadence_result()
        if reason is None:
            if min(left["raw_n_bright_observers"], right["raw_n_bright_observers"]) < 2:
                reason = "insufficient_raw_bright_observers"
            elif not all(e["onset_report_eligible"] and e["onset_report_lo"] > edge for e in (left, right)):
                reason = "incomplete_window_onset"
            elif schedule["anchor_first_at"] <= context["prefix_start"]:
                reason = "anchor_support_outside_prefix"
            elif right["onset_upper_first_at"] + VISIT_SPAN > issue:
                reason = "onset_support_not_available"
            elif right["onset_report_lo"] <= schedule["anchor"]:
                reason = "nonpositive_adjacent_gap"
            else:
                raw_gap = right["onset_report_lo"] - schedule["anchor"]
                longest = previous._longest_hole(context["times"], schedule["anchor"], right["onset_report_lo"])
                covered = longest <= COVERAGE_HOLE
                logged = math.log(raw_gap) if covered else None
                reason = "covered_adjacent_gap" if covered else "coverage_hole"
                end, _ = cadence_gaps(context, schedule, None, issue, threshold)
                _, onset = cadence_gaps(context, None, right, issue, threshold)
        history.append({"gap_id": left["raw_candidate_id"] + ":" + right["raw_candidate_id"],
                        "left_candidate_id": left["raw_candidate_id"],
                        "right_candidate_id": right["raw_candidate_id"],
                        "log_gap": logged, "available_at": issue, "raw_gap": raw_gap,
                        "covered": covered, "longest_hole": longest, "reason": reason,
                        "clock_anchor": schedule["anchor"] if schedule else None,
                        "anchor_emission_index": schedule["emission_index"] if schedule else None,
                        "anchor_available_at": schedule["anchor_available_at"] if schedule else None,
                        "onset_support": right["onset_report_lo"],
                        "left_cadence_end_days": end["value_days"],
                        "left_cadence_end_available_at": end["available_at"],
                        "right_cadence_on_days": onset["value_days"],
                        "right_cadence_on_available_at": onset["available_at"]})
    if len({row["gap_id"] for row in history}) != len(history):
        raise ValueError("duplicate timing observation in one feature history")
    return history


def point_feature(indexed, times, emission, issue, threshold=THRESHOLD, lookback=LOOKBACK):
    context = previous._prefix_context(indexed, times, issue, threshold, lookback, "point")
    feature = previous._base_feature(emission, issue, "point", context)
    feature["definition_version"] = DEFINITION_VERSION
    observed = decisive_visits(context["rows"], threshold)
    feature["flux_proxy"] = previous.bright_span_flux_proxy(observed, emission, issue, threshold)
    feature["observer_rate"] = observing_rate(observed, emission, issue, threshold)
    feature["cadence_end"], feature["cadence_on"] = _cadence_result("DF_only"), _cadence_result("DF_only")
    feature["current_raw_peak_at"] = None
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
    episode = episodes[current]
    feature.update(candidate_id=episode["raw_candidate_id"], event_eligible=True,
                   current_raw_peak_at=episode["raw_peak_t"])
    anchor, onset = episode.get("end_t"), episode.get("onset_t")
    if previous._finite(anchor) and anchor <= issue:
        feature.update(clock_anchor=anchor, status="point_clock_available")
        if previous._finite(onset) and anchor > onset:
            feature["mark"] = anchor - onset
    else:
        feature["status"] = "point_clock_unavailable"
    previous._attach_history(feature, context, current, issue, "point")
    return feature


def decisive_feature(indexed, times, emission, schedule, schedules, emissions,
                     threshold=THRESHOLD, lookback=LOOKBACK):
    issue = schedule["issue_time"]
    context = previous._prefix_context(indexed, times, issue, threshold, lookback, "decisive")
    feature = previous._base_feature(emission, issue, "decisive", context)
    feature["definition_version"] = DEFINITION_VERSION
    feature["flux_proxy"] = previous.bright_span_flux_proxy(context["observed"], emission, issue, threshold)
    feature["observer_rate"] = observing_rate(context["observed"], emission, issue, threshold)
    feature["cadence_end"], feature["cadence_on"] = cadence_gaps(context, schedule, None, issue, threshold)
    feature.update(anchor_available_at=schedule["anchor_available_at"], issue_delay_days=schedule["delay_days"],
                   current_raw_peak_at=None)
    lower, upper = emission["bright_first_at"] - VISIT_SPAN, emission["last_bright_at"]
    matches = [(i, e) for i, e in enumerate(context["episodes"]) if lower <= e["raw_peak_t"] <= upper]
    feature["raw_association_candidates"] = len(matches)
    if len(matches) != 1:
        feature["status"] = "raw_candidate_not_found" if not matches else "raw_candidate_ambiguous"
        return feature
    current, episode = matches[0]
    feature.update(candidate_id=episode["raw_candidate_id"], raw_n_bright_observers=episode["raw_n_bright_observers"],
                   current_raw_peak_at=episode["raw_peak_t"])
    feature["gap_history"] = _gap_history(context, current, issue, schedules, emissions, threshold)
    if feature["gap_history"]:
        latest = feature["gap_history"][-1]
        feature["previous_gap"] = latest["raw_gap"] if latest["log_gap"] is not None else None
        feature["previous_gap_covered"] = latest["covered"]
    feature["cadence_end"], feature["cadence_on"] = cadence_gaps(context, schedule, episode, issue, threshold)
    if episode["raw_n_bright_observers"] < 2:
        feature["status"] = "insufficient_raw_bright_observers"
        return feature
    own, reason = _scheduled_anchor(episode, schedules, emissions, issue)
    feature["own_scheduled_anchor_association"] = "unique" if reason is None else reason
    feature["historical_clock_anchor"] = own["anchor"] if own else None
    if own is None:
        feature["status"] = "current_" + reason
        return feature
    if own["anchor"] != schedule["anchor"]:
        raise ValueError("own scheduled and current anchors differ")
    feature.update(event_eligible=True, clock_anchor=schedule["anchor"], status="decisive_clock_available")
    epochs = sorted({v["t"] for v in context["observed"]
                     if v["decisive"] == "B" and lower <= v["t"] <= upper})
    feature["decisive_bright_times"] = len(epochs)
    feature["mark"] = epochs[-1] - epochs[0] if len(epochs) >= 2 else None
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
    emissions_by_id = {e["emission_index"]: e for e in original}
    schedules = {s["emission_index"]: s for s in audit}
    point_original = [point_feature(indexed, times, e, e["emitted_at"], threshold, lookback)
                      for e in original if start is None or e["emitted_at"] >= start]
    df, matched = [], []
    for schedule in audit:
        issue = schedule["issue_time"]
        if schedule["status"] != "scheduled" or (start is not None and issue < start):
            continue
        emission = emissions_by_id[schedule["emission_index"]]
        df.append(decisive_feature(indexed, times, emission, schedule, schedules, emissions_by_id, threshold, lookback))
        matched.append(point_feature(indexed, times, emission, issue, threshold, lookback))
    if [(f["emission_index"], f["issue_time"]) for f in df] != [(f["emission_index"], f["issue_time"]) for f in matched]:
        raise ValueError("DF and matched point populations differ")
    for feature in point_original + df + matched:
        issue = feature["issue_time"]
        if (feature["available_at"] > issue or any(h["available_at"] > issue for h in feature["gap_history"])
                or any(feature[name]["available_at"] is not None and feature[name]["available_at"] > issue
                       for name in ("cadence_end", "cadence_on", "observer_rate"))):
            raise ValueError("feature contains future information")
    return {"point_original": point_original, "df": df, "point_at_df": matched,
            "df_schedule_audit": audit}


__all__ = ["DEFINITION_VERSION", "prepare_feature_ledgers", "decoupled_schedule",
           "point_feature", "decisive_feature", "cadence_gaps", "observing_rate"]
