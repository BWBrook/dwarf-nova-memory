"""Independent scoring for the A04d X3 validation candidate.

The scorer deliberately leaves the frozen A04c scorer unchanged.  It uses X3
point estimates for durations and quiet intervals, retains interval endpoints
for coverage, and treats candidate-level uncertainty as censoring rather than
quiet time.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import defaultdict
import math
from statistics import mean, median

from dnmem.extract import VISIT_SPAN, visits as extractor_visits
from dnmem.extract_x3 import CONFIRM_MARGIN, _faint_level, x3_fitted_episodes
from dnmem.injection_score import (
    SHORT_SPLIT,
    _bias,
    _c1,
    _difference,
    _matching,
    _month,
    _number,
    _observer,
    _opportunity,
    _partial_corr,
    _rate,
    _rmse,
    _truth_type,
    _visits,
)


_AUDIT_FIELDS = (
    "onset_lo",
    "onset_hi",
    "onset_t",
    "onset_method",
    "end_lo",
    "end_hi",
    "end_t",
    "end_method",
    "peak_t",
    "gap_split",
    "confirmed_event",
    "confirmed",
)


def _midpoint(record: dict, prefix: str):
    lo, hi = _number(record.get(f"{prefix}_lo")), _number(record.get(f"{prefix}_hi"))
    return None if lo is None or hi is None else (lo + hi) / 2.0


def _point(record: dict, prefix: str):
    point = _number(record.get(f"{prefix}_t"))
    return point if point is not None else _midpoint(record, prefix)


def _equal(left, right, tolerance: float = 1e-9) -> bool:
    if _number(left) is not None and _number(right) is not None:
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)
    return left == right


def _episode_overlap(left: dict, right: dict) -> bool:
    left_lo = _number(left.get("onset_hi")) or _number(left.get("peak_t"))
    left_hi = _number(left.get("end_lo")) or _number(left.get("peak_t"))
    right_lo = _number(right.get("onset_hi")) or _number(right.get("peak_t"))
    right_hi = _number(right.get("end_lo")) or _number(right.get("peak_t"))
    if None in (left_lo, left_hi, right_lo, right_hi):
        return False
    return max(left_lo, right_lo) <= min(left_hi, right_hi)


def _prefix_match(target: dict, candidates: list[dict]):
    overlaps = [candidate for candidate in candidates if _episode_overlap(target, candidate)]
    if len(overlaps) == 1:
        return overlaps[0], False
    target_peak = _number(target.get("peak_t"))
    if target_peak is None or not candidates:
        return None, len(overlaps) > 1
    ranked = sorted(candidates, key=lambda candidate: (
        abs((_number(candidate.get("peak_t")) or math.inf) - target_peak),
        _number(candidate.get("peak_t")) or math.inf,
    ))
    if len(ranked) > 1:
        first = abs((_number(ranked[0].get("peak_t")) or math.inf) - target_peak)
        second = abs((_number(ranked[1].get("peak_t")) or math.inf) - target_peak)
        if math.isclose(first, second, rel_tol=0.0, abs_tol=1e-9):
            return None, True
    return ranked[0], len(overlaps) > 1


def _potential_confirmation_times(rows: list[dict], target: dict, threshold: float) -> list[float]:
    """Times at which a prefix could first contain two post-bright faint observers."""
    votes = extractor_visits(rows, threshold)
    limits = {str(row.get("obsID")): float(row["mag"])
              for row in rows if str(row.get("fainterThan")) == "1" and _number(row.get("mag")) is not None}
    lower = _number(target.get("onset_lo"))
    if lower is None:
        lower = _number(target.get("peak_t"))
    upper = _number(target.get("confirmed"))
    seen: set[str] = set()
    candidates = []
    issued_since_bright = False
    for vote in votes:
        if lower is not None and vote["t"] < lower:
            continue
        if upper is not None and vote["t"] > upper:
            break
        if vote["cls"] == "B":
            seen.clear()
            issued_since_bright = False
            continue
        if _faint_level(vote, limits) < threshold + CONFIRM_MARGIN:
            continue
        seen.add(vote["observer"])
        if len(seen) >= 2 and not issued_since_bright:
            candidates.append(vote["t"])
            issued_since_bright = True
    if upper is not None:
        candidates.append(upper)
    return sorted(set(candidates))


def _closed_visits(rows: list[dict], threshold: float) -> list[dict]:
    """Observer visits classified only when the 0.15 d visit window closes."""
    usable = []
    for position, row in enumerate(rows):
        if row.get("band") != "Vis." or row.get("val") != "V":
            continue
        jd, magnitude = _number(row.get("JD")), _number(row.get("mag"))
        if jd is None or magnitude is None:
            continue
        usable.append((jd, position, row))
    usable.sort(key=lambda item: (item[0], str(item[2].get("obsID", item[1]))))
    by_observer = defaultdict(list)
    for item in usable:
        by_observer[_observer(item[2])].append(item)

    closed = []
    for who, own in by_observer.items():
        groups = []
        for item in own:
            if groups and item[0] - groups[-1][0][0] <= VISIT_SPAN:
                groups[-1].append(item)
            else:
                groups.append([item])
        for group in groups:
            detections = [float(row["mag"]) for _, _, row in group
                          if str(row.get("fainterThan", "0")) != "1"]
            limits = [float(row["mag"]) for _, _, row in group
                      if str(row.get("fainterThan", "0")) == "1"]
            if detections:
                value = median(detections)
                label = "B" if value <= threshold else "F"
                confirmation_level = value
            elif limits and max(limits) >= threshold:
                value, label, confirmation_level = None, "F", max(limits)
            else:
                continue
            first_jd = group[0][0]
            closed.append({
                "closed_at": first_jd + VISIT_SPAN,
                "first_jd": first_jd,
                "last_jd": max(item[0] for item in group),
                "observer": who,
                "cls": label,
                "value": value,
                "confirmation_level": confirmation_level,
                "row_count": len(group),
            })
    return sorted(closed, key=lambda visit: (visit["closed_at"], visit["observer"]))


def causal_confirmation_emissions(rows: list[dict], threshold: float = 10.0) -> list[dict]:
    """Execute an immutable causal confirmation wrapper over closed visits.

    Two distinct bright observers arm the wrapper.  A bright visit clears
    accumulated faint evidence.  Once armed, the first two distinct observers
    at least ``CONFIRM_MARGIN`` mag fainter than the threshold emit a record.
    The same faint evidence closes an unarmed provisional bright sequence
    without emitting.  An emission is never withdrawn; two fresh bright
    observers are required to re-arm the wrapper.  Equal close times are one
    batch; any bright evidence resets the batch and same-time faint evidence
    is ignored.
    """
    bright_observers: set[str] = set()
    faint_observers: set[str] = set()
    bright_first_at = None
    last_bright_at = None
    faint_first_at = None
    armed = False
    emissions = []
    closed_visits = _closed_visits(rows, float(threshold))
    position = 0
    while position < len(closed_visits):
        close_time = closed_visits[position]["closed_at"]
        end = position + 1
        while end < len(closed_visits) and closed_visits[end]["closed_at"] == close_time:
            end += 1
        batch = closed_visits[position:end]
        position = end
        bright = [visit for visit in batch if visit["cls"] == "B"]
        if bright:
            faint_observers.clear()
            faint_first_at = None
            if not bright_observers:
                bright_first_at = close_time
            bright_observers.update(visit["observer"] for visit in bright)
            last_bright_at = close_time
            armed = armed or len(bright_observers) >= 2
            continue
        strong_faint = [visit for visit in batch
                        if visit["confirmation_level"] >= threshold + CONFIRM_MARGIN]
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
                "faint_observer_count": len(faint_observers),
                "trigger_visit_first_jd": min(visit["first_jd"] for visit in strong_faint),
                "trigger_visit_last_jd": max(visit["last_jd"] for visit in strong_faint),
                "trigger_visit_closed_at": close_time,
            })
        bright_observers.clear()
        faint_observers.clear()
        bright_first_at = None
        last_bright_at = None
        faint_first_at = None
        armed = False
    return emissions


def audit_final_confirmation_prefix(rows: list[dict], episodes: list[dict],
                                    threshold: float = 10.0) -> dict:
    """Audit the final confirmed candidate against outputs available at issue time.

    Besides reproducing the literal full-catalogue confirmation at its reported
    time, this checks earlier possible issue times.  An earlier prefix
    confirmation that changes or vanishes in the full catalogue is selective
    disappearance and fails the operational audit.
    """
    ordered = sorted((dict(episode) for episode in episodes if episode.get("confirmed_event", True)),
                     key=lambda episode: (_number(episode.get("peak_t")) or math.inf))
    if not ordered:
        return {
            "auditable": False,
            "reason": "no_confirmed_candidate",
            "reported_confirmation_prefix_measurable": None,
            "no_selective_disappearance": None,
            "passed": None,
            "records": [],
        }
    target = ordered[-1]
    reported = _number(target.get("confirmed"))
    cutoffs = _potential_confirmation_times(rows, target, float(threshold))
    records = []
    for cutoff in cutoffs:
        prefix_rows = [row for row in rows
                       if _number(row.get("JD")) is not None and float(row["JD"]) <= cutoff]
        prefix_candidates = [episode for episode in x3_fitted_episodes(prefix_rows, float(threshold))
                             if episode.get("confirmed_event", True)]
        matched, ambiguous = _prefix_match(target, prefix_candidates)
        differences = [] if matched is not None else ["candidate_missing_or_ambiguous"]
        if matched is not None:
            differences.extend(field for field in _AUDIT_FIELDS
                               if not _equal(target.get(field), matched.get(field)))
        prefix_confirmation = _number(matched.get("confirmed")) if matched is not None else None
        records.append({
            "cutoff": cutoff,
            "is_reported_cutoff": reported is not None and _equal(cutoff, reported),
            "candidate_found": matched is not None,
            "candidate_match_ambiguous": ambiguous,
            "prefix_confirmation": prefix_confirmation,
            "full_confirmation": reported,
            "confirmation_matches_full": _equal(prefix_confirmation, reported),
            "discrepant_fields": differences,
        })
    reported_records = [record for record in records if record["is_reported_cutoff"]]
    reported_measurable = (reported is not None and len(reported_records) == 1
                           and reported_records[0]["candidate_found"]
                           and reported_records[0]["confirmation_matches_full"])
    disappeared = [record for record in records
                   if not record["is_reported_cutoff"] and record["prefix_confirmation"] is not None
                   and not record["confirmation_matches_full"]]
    no_disappearance = not disappeared
    return {
        "auditable": reported is not None or bool(records),
        "reason": None if reported is not None or records else "no_reported_or_potential_confirmation",
        "full_candidate_peak_t": _number(target.get("peak_t")),
        "full_reported_confirmation": reported,
        "reported_confirmation_prefix_measurable": reported_measurable if reported is not None else None,
        "no_selective_disappearance": no_disappearance,
        "selective_disappearance_count": len(disappeared),
        "passed": reported_measurable and no_disappearance if reported is not None else None,
        "records": records,
    }


def _boundary_metrics(reference: list[int], truth: list[dict], episodes: list[dict],
                      unique_truth: dict[int, int], prefix: str) -> dict:
    covered = 0
    finite = 0
    errors = []
    widths = []
    by_method = {"fit": {"reference": 0, "finite": 0, "covered": 0},
                 "adjacency": {"reference": 0, "finite": 0, "covered": 0},
                 "other": {"reference": 0, "finite": 0, "covered": 0}}
    truth_key = prefix
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        episode = episodes[i]
        method = str(episode.get(f"{prefix}_method", "other")).casefold()
        method = method if method in {"fit", "adjacency"} else "other"
        by_method[method]["reference"] += 1
        lo, hi = _number(episode.get(f"{prefix}_lo")), _number(episode.get(f"{prefix}_hi"))
        if lo is None or hi is None or hi <= lo:
            continue
        finite += 1
        by_method[method]["finite"] += 1
        target = float(truth[j][truth_key])
        is_covered = lo <= target <= hi
        covered += is_covered
        by_method[method]["covered"] += is_covered
        point = _point(episode, prefix)
        if point is not None:
            errors.append(point - target)
        widths.append(hi - lo)
    denominator = len(reference)
    output = {
        f"{prefix}_effective_covered": covered,
        f"{prefix}_effective_coverage": _rate(covered, denominator),
        f"{prefix}_finite_matched_count": finite,
        f"{prefix}_conditional_coverage": _rate(covered, finite),
        f"{prefix}_point_bias": _bias(errors),
        f"{prefix}_point_rmse": _rmse(errors),
        f"{prefix}_mean_width": mean(widths) if widths else None,
        f"{prefix}_fallback_count": by_method["adjacency"]["reference"],
        f"{prefix}_fallback_rate": _rate(by_method["adjacency"]["reference"],
                                          sum(item["reference"] for item in by_method.values())),
    }
    for method, counts in by_method.items():
        output[f"{prefix}_{method}_reference_count"] = counts["reference"]
        output[f"{prefix}_{method}_finite_count"] = counts["finite"]
        output[f"{prefix}_{method}_covered"] = counts["covered"]
        output[f"{prefix}_{method}_effective_coverage"] = _rate(counts["covered"], counts["reference"])
        output[f"{prefix}_{method}_conditional_coverage"] = _rate(counts["covered"], counts["finite"])
    return output


def _grouped_completeness(reference: list[int], truth: list[dict], truth_edges: dict[int, set[int]],
                          unique_truth: dict[int, int], group, levels=()) -> dict:
    counts = defaultdict(lambda: {"reference_count": 0, "complete_count": 0,
                                  "unique_complete_count": 0})
    for level in levels:
        counts[str(level)]
    for j in reference:
        key = str(group(truth[j]))
        counts[key]["reference_count"] += 1
        counts[key]["complete_count"] += bool(truth_edges[j])
        counts[key]["unique_complete_count"] += j in unique_truth
    output = {}
    for key, item in sorted(counts.items()):
        output[key] = {**item,
                       "completeness": _rate(item["complete_count"], item["reference_count"]),
                       "unique_completeness": _rate(item["unique_complete_count"],
                                                    item["reference_count"])}
    return output


def _batch_confirmation_metrics(reference: list[int], truth: list[dict], episodes: list[dict],
                                unique_truth: dict[int, int]) -> dict:
    lags = []
    missing = 0
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        confirmation = _number(episodes[i].get("confirmed"))
        if confirmation is None:
            missing += 1
        else:
            lags.append(confirmation - float(truth[j]["end"]))
    candidates = sum(j in unique_truth for j in reference)
    premature = sum(lag < 0.0 for lag in lags)
    return {
        "batch_confirmation_candidate_count": candidates,
        "batch_confirmation_observed_count": len(lags),
        "batch_confirmation_missing_count": missing,
        "batch_confirmation_missing_rate": _rate(missing, candidates),
        "batch_confirmation_lag_mean": mean(lags) if lags else None,
        "batch_confirmation_lag_median": median(lags) if lags else None,
        "batch_confirmation_lag_rmse": _rmse(lags),
        "batch_confirmation_premature_count": premature,
        "batch_confirmation_premature_rate_issued": _rate(premature, len(lags)),
        "batch_confirmation_premature_rate_conservative": _rate(premature, candidates),
    }


def _emission_truth_edges(emissions: list[dict], truth: list[dict]):
    edges = {}
    for emission in emissions:
        lo, hi = emission["bright_first_at"], emission["last_bright_at"]
        edges[emission["emission_index"]] = [
            j for j, event in enumerate(truth)
            if max(lo, float(event["onset"])) <= min(hi, float(event["end"]))
        ]
    return edges


def _operational_confirmation_metrics(reference: list[int], unique_reference: list[int],
                                      truth: list[dict], emissions: list[dict]) -> dict:
    edges = _emission_truth_edges(emissions, truth)
    assigned = defaultdict(list)
    false_count = 0
    ambiguous_count = 0
    ledger = []
    for emission in emissions:
        neighbours = edges[emission["emission_index"]]
        if len(neighbours) == 1:
            truth_index = neighbours[0]
            assigned[truth_index].append(emission)
            status = "assigned"
        elif neighbours:
            truth_index = None
            ambiguous_count += 1
            status = "ambiguous"
        else:
            truth_index = None
            false_count += 1
            status = "false"
        ledger.append({**emission, "truth_index": truth_index,
                       "truth_id": truth[truth_index].get("id") if truth_index is not None else None,
                       "match_status": status, "overlapping_truth_indices": neighbours})

    first_records = []
    for j in reference:
        matches = sorted(assigned.get(j, []), key=lambda emission: emission["emitted_at"])
        if not matches:
            first_records.append({"truth_index": j, "truth_id": truth[j].get("id"),
                                  "emission_index": None, "emitted_at": None,
                                  "true_end": float(truth[j]["end"]), "lag": None,
                                  "duplicate_emission_count": 0})
            continue
        first = matches[0]
        lag = first["emitted_at"] - float(truth[j]["end"])
        first_records.append({"truth_index": j, "truth_id": truth[j].get("id"),
                              "emission_index": first["emission_index"],
                              "emitted_at": first["emitted_at"],
                              "true_end": float(truth[j]["end"]), "lag": lag,
                              "duplicate_emission_count": len(matches) - 1})

    def summarise(indices):
        index_set = set(indices)
        selected = [record for record in first_records if record["truth_index"] in index_set]
        lags = [record["lag"] for record in selected if record["lag"] is not None]
        missing = sum(record["lag"] is None for record in selected)
        premature = sum(lag < 0.0 for lag in lags)
        duplicates = sum(record["duplicate_emission_count"] for record in selected)
        return {"denominator": len(selected), "lags": lags, "missing": missing,
                "premature": premature, "duplicates": duplicates}

    primary = summarise(unique_reference)
    all_truth = summarise(reference)
    return {
        "operational_confirmation_candidate_count": primary["denominator"],
        "operational_confirmation_observed_count": len(primary["lags"]),
        "operational_confirmation_missing_count": primary["missing"],
        "operational_confirmation_missing_rate": _rate(primary["missing"], primary["denominator"]),
        "operational_confirmation_lag_mean": mean(primary["lags"]) if primary["lags"] else None,
        "operational_confirmation_lag_median": median(primary["lags"]) if primary["lags"] else None,
        "operational_confirmation_lag_rmse": _rmse(primary["lags"]),
        "operational_confirmation_premature_count": primary["premature"],
        "operational_confirmation_premature_rate_issued": _rate(primary["premature"], len(primary["lags"])),
        "operational_confirmation_premature_rate_conservative": _rate(primary["premature"],
                                                                        primary["denominator"]),
        "operational_confirmation_all_truth_count": all_truth["denominator"],
        "operational_confirmation_all_truth_observed_count": len(all_truth["lags"]),
        "operational_confirmation_all_truth_missing_count": all_truth["missing"],
        "operational_confirmation_all_truth_missing_rate": _rate(all_truth["missing"],
                                                                   all_truth["denominator"]),
        "operational_confirmation_all_truth_premature_count": all_truth["premature"],
        "operational_confirmation_all_truth_premature_rate_issued": _rate(all_truth["premature"],
                                                                            len(all_truth["lags"])),
        "operational_confirmation_false_emission_count": false_count,
        "operational_confirmation_ambiguous_emission_count": ambiguous_count,
        "operational_confirmation_duplicate_emission_count": primary["duplicates"],
        "operational_confirmation_all_truth_duplicate_emission_count": all_truth["duplicates"],
        "operational_confirmation_emission_count": len(emissions),
        "operational_confirmation_first_records": first_records,
        "operational_confirmation_emissions": ledger,
        "operational_confirmation_early_gate_passed": (
            _rate(primary["premature"], len(primary["lags"])) < 0.02 if primary["lags"] else None),
        "operational_confirmation_missing_gate_passed": (
            _rate(primary["missing"], primary["denominator"]) < 0.05
            if primary["denominator"] else None),
    }


def _barriers(all_episodes: list[dict], left: dict, right: dict) -> list[dict]:
    left_peak, right_peak = _number(left.get("peak_t")), _number(right.get("peak_t"))
    if left_peak is None or right_peak is None:
        return []
    return [episode for episode in all_episodes
            if not episode.get("confirmed_event", True)
            and (peak := _number(episode.get("peak_t"))) is not None
            and left_peak < peak < right_peak]


def score_validation(rows: list[dict], episodes: list[dict], truth: list[dict], start: float,
                     stop: float, threshold: float = 10.0, *, audit_prefix: bool = False) -> list[dict]:
    """Score one X3 validation replicate under C1(7 d) and C2(0.95)."""
    if _number(start) is None or _number(stop) is None or float(stop) <= float(start):
        raise ValueError("stop must be finite and greater than start")
    start, stop, threshold = float(start), float(stop), float(threshold)
    ordered_truth = sorted((dict(event) for event in truth),
                           key=lambda event: (float(event["onset"]), str(event.get("id", ""))))
    all_episodes = sorted((dict(episode, _candidate_index=index) for index, episode in enumerate(episodes)),
                          key=lambda episode: (_number(episode.get("peak_t")) or math.inf))
    confirmed = [episode for episode in all_episodes if episode.get("confirmed_event", True)]
    visits = _visits(rows, threshold)
    visit_times = [visit["t"] for visit in visits]
    ep_edges, truth_edges, unique_ep, unique_truth = _matching(confirmed, ordered_truth)

    reference = [j for j, event in enumerate(ordered_truth)
                 if start + 2.0 <= float(event["onset"]) and float(event["end"]) <= stop - 2.0]
    reference_set = set(reference)
    completeness_count = sum(bool(truth_edges[j]) for j in reference)
    unique_count = sum(j in unique_truth for j in reference)
    short_reference = [j for j in reference
                       if float(ordered_truth[j]["end"]) - float(ordered_truth[j]["onset"]) < SHORT_SPLIT
                       and _month(float(ordered_truth[j]["onset"])) not in {3, 4, 5}]
    prefix_audit = (audit_final_confirmation_prefix(rows, episodes, threshold) if audit_prefix else
                    {"auditable": False, "reason": "not_performed; immutable causal emissions scored separately",
                     "passed": None, "reported_confirmation_prefix_measurable": None,
                     "no_selective_disappearance": None, "records": []})
    causal_emissions = causal_confirmation_emissions(rows, threshold)
    base = {
        "threshold": threshold,
        "window_start": start,
        "window_stop": stop,
        "exposure_years": (stop - start) / 365.25,
        "reference_event_count": len(reference),
        "completeness_count": completeness_count,
        "completeness": _rate(completeness_count, len(reference)),
        "unique_completeness_count": unique_count,
        "unique_completeness": _rate(unique_count, len(reference)),
        "short_outside_mar_may_count": len(short_reference),
        "short_outside_mar_may_complete_count": sum(bool(truth_edges[j]) for j in short_reference),
        "short_outside_mar_may_completeness": _rate(sum(bool(truth_edges[j]) for j in short_reference),
                                                       len(short_reference)),
        "completeness_by_true_type": _grouped_completeness(
            reference, ordered_truth, truth_edges, unique_truth, _truth_type,
            levels=("short", "long")),
        "completeness_by_gregorian_month": _grouped_completeness(
            reference, ordered_truth, truth_edges, unique_truth,
            lambda event: _month(float(event["onset"])), levels=range(1, 13)),
        "confirmed_extracted_count": len(confirmed),
        "unconfirmed_barrier_count": sum(not episode.get("confirmed_event", True)
                                          for episode in all_episodes),
        "false_confirmed_count": sum(not neighbours for neighbours in ep_edges.values()),
        "false_confirmed_per_year": (sum(not neighbours for neighbours in ep_edges.values()) /
                                     ((stop - start) / 365.25)),
        "split_truth_count": sum(len(neighbours) > 1 for neighbours in truth_edges.values()),
        "split_excess_count": sum(max(0, len(neighbours) - 1) for neighbours in truth_edges.values()),
        "merged_episode_count": sum(len(neighbours) > 1 for neighbours in ep_edges.values()),
        "merged_excess_count": sum(max(0, len(neighbours) - 1) for neighbours in ep_edges.values()),
        "confirmation_prefix_audit": prefix_audit,
        "confirmation_prefix_audit_scope": "final_confirmed_candidate",
        "confirmation_prefix_audit_passed": prefix_audit["passed"],
        "confirmation_reported_prefix_measurable": prefix_audit["reported_confirmation_prefix_measurable"],
        "confirmation_final_candidate_no_selective_disappearance": prefix_audit["no_selective_disappearance"],
    }
    base.update(_boundary_metrics(reference, ordered_truth, confirmed, unique_truth, "onset"))
    base.update(_boundary_metrics(reference, ordered_truth, confirmed, unique_truth, "end"))
    base.update(_batch_confirmation_metrics(reference, ordered_truth, confirmed, unique_truth))
    base.update(_operational_confirmation_metrics(
        reference, [j for j in reference if j in unique_truth], ordered_truth, causal_emissions))

    duration_errors = []
    type_errors = 0
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        onset, end = _point(confirmed[i], "onset"), _point(confirmed[i], "end")
        if onset is None or end is None:
            continue
        recovered_duration = end - onset
        true_duration = float(ordered_truth[j]["end"]) - float(ordered_truth[j]["onset"])
        duration_errors.append(recovered_duration - true_duration)
        type_errors += ("long" if recovered_duration >= SHORT_SPLIT else "short") != _truth_type(ordered_truth[j])
    base.update({
        "duration_finite_matched_count": len(duration_errors),
        "duration_point_bias": _bias(duration_errors),
        "duration_point_rmse": _rmse(duration_errors),
        "type_misclassified_count": type_errors,
        "type_misclassification_rate": _rate(type_errors, len(duration_errors)),
    })

    truth_all_values = []
    for j in range(1, len(ordered_truth) - 1):
        if {j - 1, j, j + 1}.issubset(reference_set):
            previous, current, following = ordered_truth[j - 1:j + 2]
            truth_all_values.append((float(current["end"]) - float(current["onset"]),
                                     float(following["onset"]) - float(current["end"]),
                                     float(current["onset"]) - float(previous["end"])))
    oracle_r_all = _partial_corr(truth_all_values)

    pair_data = []
    for i in range(len(confirmed) - 1):
        current, following = confirmed[i], confirmed[i + 1]
        q_start, q_stop = _point(current, "end"), _point(following, "onset")
        pair_data.append({
            "pair_index": i,
            "current": i,
            "following": i + 1,
            "current_candidate_index": current["_candidate_index"],
            "following_candidate_index": following["_candidate_index"],
            "start": q_start,
            "stop": q_stop,
            "valid": q_start is not None and q_stop is not None and q_stop > q_start,
            "barriers": _barriers(all_episodes, current, following),
        })

    results = []
    for rule, criterion in (("C1_7", 7.0), ("C2_095", 0.95)):
        scored_pairs = []
        for pair in pair_data:
            structural_reasons = []
            structural_times = []
            current, following = confirmed[pair["current"]], confirmed[pair["following"]]
            if not pair["valid"]:
                structural_reasons.append("invalid_point_bounds")
            if current.get("gap_split", False):
                structural_reasons.append("current_gap_split")
                if pair["start"] is not None:
                    structural_times.append(pair["start"])
            if following.get("gap_split", False):
                structural_reasons.append("following_gap_split")
                if pair["stop"] is not None:
                    structural_times.append(pair["stop"])
            if pair["barriers"]:
                structural_reasons.append("unconfirmed_bright_barrier")
                structural_times.extend(_number(item.get("peak_t")) for item in pair["barriers"]
                                        if _number(item.get("peak_t")) is not None)

            cadence_passed = False
            cadence_censor = None
            diagnostic = None
            if pair["valid"]:
                lower = bisect_left(visit_times, pair["start"])
                upper = bisect_right(visit_times, pair["stop"])
                interval_visits = visits[lower:upper]
                if rule == "C1_7":
                    cadence_passed, cadence_censor, diagnostic = _c1(
                        interval_visits, pair["start"], pair["stop"], criterion)
                else:
                    diagnostic, cadence_censor = _opportunity(interval_visits, pair["start"], pair["stop"])
                    cadence_passed = diagnostic >= criterion
            reasons = list(structural_reasons)
            if pair["valid"] and not cadence_passed:
                reasons.append("cadence_failure")
            censor_times = structural_times + ([cadence_censor] if cadence_censor is not None else [])
            passed = pair["valid"] and cadence_passed and not structural_reasons
            scored_pairs.append({
                "pair_index": pair["pair_index"],
                "current_candidate_index": pair["current_candidate_index"],
                "following_candidate_index": pair["following_candidate_index"],
                "start": pair["start"],
                "stop": pair["stop"],
                "valid": pair["valid"],
                "passed": passed,
                "censor_time": min(censor_times) if censor_times else None,
                "censor_reasons": reasons,
                "diagnostic": diagnostic,
                "barrier_candidate_indices": [item["_candidate_index"] for item in pair["barriers"]],
            })

        passed_pairs = [pair for pair in scored_pairs if pair["passed"]]
        censored_pairs = [pair for pair in scored_pairs if not pair["passed"]]
        hidden_passed = 0
        mapped_trueconsecutive = 0
        rejected_trueconsecutive = 0
        for pair in scored_pairs:
            left, right = pair["pair_index"], pair["pair_index"] + 1
            left_truth, right_truth = unique_ep.get(left), unique_ep.get(right)
            consecutive = (left_truth is not None and right_truth is not None
                           and right_truth == left_truth + 1)
            if consecutive:
                mapped_trueconsecutive += 1
                rejected_trueconsecutive += not pair["passed"]
            if pair["passed"] and pair["valid"]:
                endpoint_truth = ep_edges[left] | ep_edges[right]
                if any(j not in endpoint_truth and pair["start"] <= float(event["onset"])
                       and float(event["end"]) <= pair["stop"]
                       for j, event in enumerate(ordered_truth)):
                    hidden_passed += 1

        recovered_values = []
        selected_truth_values = []
        recovered_matched_values = []
        for i in range(1, len(confirmed) - 1):
            preceding_pair, following_pair = scored_pairs[i - 1], scored_pairs[i]
            if not preceding_pair["passed"] or not following_pair["passed"]:
                continue
            previous_onset = _point(confirmed[i - 1], "onset")
            following_end = _point(confirmed[i + 1], "end")
            if (previous_onset is None or following_end is None or previous_onset < start + 2.0
                    or following_end > stop - 2.0):
                continue
            onset, end = _point(confirmed[i], "onset"), _point(confirmed[i], "end")
            if onset is None or end is None:
                continue
            recovered_values.append((end - onset,
                                     following_pair["stop"] - following_pair["start"],
                                     preceding_pair["stop"] - preceding_pair["start"]))
            indices = (unique_ep.get(i - 1), unique_ep.get(i), unique_ep.get(i + 1))
            if (None in indices or indices[1] != indices[0] + 1 or indices[2] != indices[1] + 1
                    or not set(indices).issubset(reference_set)):
                continue
            previous, current, following = (ordered_truth[index] for index in indices)
            selected_truth_values.append((float(current["end"]) - float(current["onset"]),
                                          float(following["onset"]) - float(current["end"]),
                                          float(current["onset"]) - float(previous["end"])))
            recovered_matched_values.append((end - onset,
                                              following_pair["stop"] - following_pair["start"],
                                              preceding_pair["stop"] - preceding_pair["start"]))

        recovered_r = _partial_corr(recovered_values)
        selected_oracle_r = _partial_corr(selected_truth_values)
        recovered_matched_r = _partial_corr(recovered_matched_values)
        censor_times = [pair["censor_time"] for pair in censored_pairs if pair["censor_time"] is not None]
        row = dict(base)
        row.update({
            "rule": rule,
            "rule_value": criterion,
            "pair_count": len(scored_pairs),
            "invalid_pair_count": sum(not pair["valid"] for pair in scored_pairs),
            "eligible_count": len(passed_pairs),
            "censored_count": len(censored_pairs),
            "censor_time_min": min(censor_times) if censor_times else None,
            "censor_time_mean": mean(censor_times) if censor_times else None,
            "censor_time_max": max(censor_times) if censor_times else None,
            "coverage_diagnostic_mean": (mean(pair["diagnostic"] for pair in scored_pairs
                                                 if pair["diagnostic"] is not None)
                                           if any(pair["diagnostic"] is not None for pair in scored_pairs)
                                           else None),
            "pair_records": scored_pairs,
            "pairs_passed": len(passed_pairs),
            "hidden_passed": hidden_passed,
            "mapped_trueconsecutive": mapped_trueconsecutive,
            "rejected_trueconsecutive": rejected_trueconsecutive,
            "oracle_all_n": len(truth_all_values),
            "association_n": len(recovered_values),
            "selected_association_n": len(selected_truth_values),
            "oracle_r_all": oracle_r_all,
            "recovered_r": recovered_r,
            "selected_oracle_r": selected_oracle_r,
            "recovered_matched_r": recovered_matched_r,
            "total_bias": _difference(recovered_r, oracle_r_all),
            "selection_bias": _difference(selected_oracle_r, oracle_r_all),
            "boundary_bias": _difference(recovered_matched_r, selected_oracle_r),
            "oracle_r_all_undefined": oracle_r_all is None,
            "recovered_r_undefined": recovered_r is None,
            "selected_oracle_r_undefined": selected_oracle_r is None,
            "recovered_matched_r_undefined": recovered_matched_r is None,
            "total_bias_undefined": _difference(recovered_r, oracle_r_all) is None,
            "selection_bias_undefined": _difference(selected_oracle_r, oracle_r_all) is None,
            "boundary_bias_undefined": _difference(recovered_matched_r, selected_oracle_r) is None,
        })
        results.append(row)
    return results


__all__ = ["audit_final_confirmation_prefix", "causal_confirmation_emissions", "score_validation"]
