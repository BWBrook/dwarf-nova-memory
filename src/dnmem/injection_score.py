"""Independent scoring for SS Cyg event injection/recovery experiments."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import math
from statistics import mean, median


VISIT_SPAN = 0.15
SHORT_SPLIT = 12.0
MINIMAL_OUTBURST = 5.0


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _number(value):
    return float(value) if _finite(value) else None


def _midpoint(record: dict, low: str, high: str):
    lo, hi = _number(record.get(low)), _number(record.get(high))
    return None if lo is None or hi is None else (lo + hi) / 2.0


def _observer(row: dict) -> str:
    name = (row.get("obsName") or "").strip().casefold()
    return name or str(row.get("by") or "").strip().casefold() or "unknown"


def _is_limit(row: dict) -> bool:
    return str(row.get("fainterThan", "0")).strip().casefold() in {"1", "true", "t", "yes"}


def _visits(rows: list[dict], threshold: float) -> list[dict]:
    """Collapse rows independently to one informative vote per observer visit."""
    usable = []
    for position, row in enumerate(rows):
        if row.get("band") != "Vis." or row.get("val") != "V" or not _finite(row.get("JD")):
            continue
        if not _finite(row.get("mag")):
            continue
        usable.append((float(row["JD"]), position, row))
    usable.sort(key=lambda item: (item[0], str(item[2].get("obsID", item[1]))))

    by_observer = defaultdict(list)
    for jd, position, row in usable:
        by_observer[_observer(row)].append((jd, position, row))

    collapsed = []
    for who, own in by_observer.items():
        groups = []
        for item in own:
            if groups and item[0] - groups[-1][0][0] <= VISIT_SPAN:
                groups[-1].append(item)
            else:
                groups.append([item])
        for group in groups:
            detections = [float(row["mag"]) for _, _, row in group if not _is_limit(row)]
            limits = [float(row["mag"]) for _, _, row in group if _is_limit(row)]
            if detections:
                value = median(detections)
                cls = "B" if value <= threshold else "F"
            elif limits and max(limits) >= threshold:
                value, cls = None, "F"
            else:
                continue
            collapsed.append({"t": median(jd for jd, _, _ in group), "observer": who,
                              "cls": cls, "value": value})
    return sorted(collapsed, key=lambda visit: (visit["t"], visit["observer"]))


def _episode_core(episode: dict):
    onset = _number(episode.get("onset_hi"))
    end = _number(episode.get("end_lo"))
    peak = _number(episode.get("peak_t"))
    return onset, end, peak


def _overlaps(episode: dict, event: dict) -> bool:
    onset, end, peak = _episode_core(episode)
    truth_onset, truth_end = float(event["onset"]), float(event["end"])
    if onset is not None and end is not None and end > onset:
        return max(onset, truth_onset) < min(end, truth_end)
    return peak is not None and truth_onset <= peak <= truth_end


def _matching(episodes: list[dict], truth: list[dict]):
    ep_edges = {i: set() for i in range(len(episodes))}
    truth_edges = {j: set() for j in range(len(truth))}
    for i, episode in enumerate(episodes):
        for j, event in enumerate(truth):
            if _overlaps(episode, event):
                ep_edges[i].add(j)
                truth_edges[j].add(i)
    unique_ep = {}
    unique_truth = {}
    for i, neighbours in ep_edges.items():
        if len(neighbours) == 1:
            j = next(iter(neighbours))
            if len(truth_edges[j]) == 1:
                unique_ep[i] = j
                unique_truth[j] = i
    return ep_edges, truth_edges, unique_ep, unique_truth


def _rate(numerator: int, denominator: int):
    return numerator / denominator if denominator else None


def _bias(errors: list[float]):
    return mean(errors) if errors else None


def _rmse(errors: list[float]):
    return math.sqrt(mean(error * error for error in errors)) if errors else None


def _month(jd: float) -> int:
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (epoch + timedelta(days=float(jd) - 2440587.5)).month


def _truth_type(event: dict) -> str:
    supplied = str(event.get("type", "")).strip().casefold()
    if supplied.startswith("l"):
        return "long"
    if supplied.startswith("s"):
        return "short"
    return "long" if float(event["end"]) - float(event["onset"]) >= SHORT_SPLIT else "short"


def _boundary_metrics(reference: list[int], truth: list[dict], episodes: list[dict],
                      unique_truth: dict[int, int], low: str, high: str, truth_key: str,
                      prefix: str) -> dict:
    covered = 0
    finite = 0
    errors = []
    widths = []
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        lo, hi = _number(episodes[i].get(low)), _number(episodes[i].get(high))
        if lo is None or hi is None or hi <= lo:
            continue
        finite += 1
        target = float(truth[j][truth_key])
        covered += lo <= target <= hi
        errors.append((lo + hi) / 2.0 - target)
        widths.append(hi - lo)
    denominator = len(reference)
    return {
        f"{prefix}_effective_covered": covered,
        f"{prefix}_effective_coverage": _rate(covered, denominator),
        f"{prefix}_finite_matched_count": finite,
        f"{prefix}_conditional_coverage": _rate(covered, finite),
        f"{prefix}_midpoint_bias": _bias(errors),
        f"{prefix}_midpoint_rmse": _rmse(errors),
        f"{prefix}_mean_width": mean(widths) if widths else None,
    }


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged = []
    for lo, hi in sorted(intervals):
        if hi <= lo:
            continue
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def _opportunity(visits: list[dict], start: float, stop: float):
    """Exact fraction of five-day starts having visits from two observers."""
    domain_lo, domain_hi = start, stop - MINIMAL_OUTBURST
    if domain_hi <= domain_lo:
        return 1.0, None
    by_observer = defaultdict(list)
    for visit in visits:
        lo = max(domain_lo, visit["t"] - MINIMAL_OUTBURST)
        hi = min(domain_hi, visit["t"])
        if hi > lo:
            by_observer[visit["observer"]].append((lo, hi))
    changes = defaultdict(int)
    for intervals in by_observer.values():
        for lo, hi in _merge_intervals(intervals):
            changes[lo] += 1
            changes[hi] -= 1
    count = 0
    previous = domain_lo
    covered = 0.0
    first_bad = None
    for point in sorted(changes):
        if point < domain_lo or point > domain_hi:
            continue
        if point > previous:
            if count >= 2:
                covered += point - previous
            elif first_bad is None:
                first_bad = previous
        count += changes[point]
        previous = point
    if previous < domain_hi:
        if count >= 2:
            covered += domain_hi - previous
        elif first_bad is None:
            first_bad = previous
    return covered / (domain_hi - domain_lo), first_bad


def _c1(visits: list[dict], start: float, stop: float, limit: float):
    times = [visit["t"] for visit in visits if start < visit["t"] < stop]
    anchors = [start] + sorted(times) + [stop]
    gaps = [(b - a, a) for a, b in zip(anchors, anchors[1:])]
    longest = max(gap for gap, _ in gaps)
    first_bad = next((at for gap, at in gaps if gap > limit), None)
    return longest <= limit, first_bad, longest


def _pearson(x: list[float], y: list[float]):
    xbar, ybar = mean(x), mean(y)
    xx = sum((value - xbar) ** 2 for value in x)
    yy = sum((value - ybar) ** 2 for value in y)
    if xx <= 0.0 or yy <= 0.0:
        return None
    return sum((a - xbar) * (b - ybar) for a, b in zip(x, y)) / math.sqrt(xx * yy)


def _partial_corr(values: list[tuple[float, float, float]]):
    if len(values) < 5:
        return None
    x, y, z = ([row[column] for row in values] for column in range(3))
    rxy, rxz, ryz = _pearson(x, y), _pearson(x, z), _pearson(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    denominator = (1.0 - rxz * rxz) * (1.0 - ryz * ryz)
    if denominator <= 1e-15:
        return None
    result = (rxy - rxz * ryz) / math.sqrt(denominator)
    return max(-1.0, min(1.0, result))


def _difference(left, right):
    return None if left is None or right is None else left - right


def _confirmation_metrics(reference: list[int], truth: list[dict], episodes: list[dict],
                          unique_truth: dict[int, int], visits: list[dict], visit_times: list[float]) -> dict:
    lags = []
    missing = 0
    candidates = 0
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        candidates += 1
        last_bright = _number(episodes[i].get("end_lo"))
        if last_bright is None:
            missing += 1
            continue
        next_onset = float(truth[j + 1]["onset"]) if j + 1 < len(truth) else math.inf
        seen = set()
        confirmation = None
        lower = bisect_right(visit_times, last_bright)
        upper = bisect_left(visit_times, next_onset)
        for visit in visits[lower:upper]:
            if visit["cls"] != "F":
                continue
            seen.add(visit["observer"])
            if len(seen) >= 2:
                confirmation = visit["t"]
                break
        if confirmation is None:
            missing += 1
        else:
            lags.append(confirmation - float(truth[j]["end"]))
    return {
        "confirmation_candidate_count": candidates,
        "confirmation_observed_count": len(lags),
        "confirmation_missing_count": missing,
        "confirmation_missing_rate": _rate(missing, candidates),
        "confirmation_lag_mean": mean(lags) if lags else None,
        "confirmation_lag_median": median(lags) if lags else None,
        "confirmation_lag_rmse": _rmse(lags),
        "confirmation_negative_lag_count": sum(lag < 0.0 for lag in lags),
    }


def score_run(rows: list[dict], episodes: list[dict], truth: list[dict], start: float,
              stop: float, threshold: float = 10.0) -> list[dict]:
    """Score one injection/recovery replicate under each prespecified coverage rule."""
    if not _finite(start) or not _finite(stop) or float(stop) <= float(start):
        raise ValueError("stop must be finite and greater than start")
    start, stop, threshold = float(start), float(stop), float(threshold)
    ordered_truth = sorted((dict(event) for event in truth), key=lambda event: (float(event["onset"]),
                                                                                 str(event.get("id", ""))))
    confirmed = [dict(episode) for episode in episodes if episode.get("confirmed_event", True)]
    confirmed.sort(key=lambda episode: (_number(episode.get("peak_t")) if _number(episode.get("peak_t")) is not None
                                        else math.inf))
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
    short_complete = sum(bool(truth_edges[j]) for j in short_reference)

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
        "short_outside_mar_may_complete_count": short_complete,
        "short_outside_mar_may_completeness": _rate(short_complete, len(short_reference)),
        "confirmed_extracted_count": len(confirmed),
        "false_confirmed_count": sum(not neighbours for neighbours in ep_edges.values()),
        "false_confirmed_per_year": (sum(not neighbours for neighbours in ep_edges.values()) /
                                     ((stop - start) / 365.25)),
        "split_truth_count": sum(len(neighbours) > 1 for neighbours in truth_edges.values()),
        "split_excess_count": sum(max(0, len(neighbours) - 1) for neighbours in truth_edges.values()),
        "merged_episode_count": sum(len(neighbours) > 1 for neighbours in ep_edges.values()),
        "merged_excess_count": sum(max(0, len(neighbours) - 1) for neighbours in ep_edges.values()),
    }
    base.update(_boundary_metrics(reference, ordered_truth, confirmed, unique_truth,
                                  "onset_lo", "onset_hi", "onset", "onset"))
    base.update(_boundary_metrics(reference, ordered_truth, confirmed, unique_truth,
                                  "end_lo", "end_hi", "end", "end"))

    duration_errors = []
    type_errors = 0
    duration_count = 0
    for j in reference:
        i = unique_truth.get(j)
        if i is None:
            continue
        onset_mid = _midpoint(confirmed[i], "onset_lo", "onset_hi")
        end_mid = _midpoint(confirmed[i], "end_lo", "end_hi")
        onset_lo, onset_hi = _number(confirmed[i].get("onset_lo")), _number(confirmed[i].get("onset_hi"))
        end_lo, end_hi = _number(confirmed[i].get("end_lo")), _number(confirmed[i].get("end_hi"))
        if (onset_mid is None or end_mid is None or onset_hi <= onset_lo or end_hi <= end_lo):
            continue
        recovered_duration = end_mid - onset_mid
        true_duration = float(ordered_truth[j]["end"]) - float(ordered_truth[j]["onset"])
        duration_errors.append(recovered_duration - true_duration)
        recovered_type = "long" if recovered_duration >= SHORT_SPLIT else "short"
        type_errors += recovered_type != _truth_type(ordered_truth[j])
        duration_count += 1
    base.update({
        "duration_finite_matched_count": duration_count,
        "duration_midpoint_bias": _bias(duration_errors),
        "duration_midpoint_rmse": _rmse(duration_errors),
        "type_misclassified_count": type_errors,
        "type_misclassification_rate": _rate(type_errors, duration_count),
    })
    base.update(_confirmation_metrics(reference, ordered_truth, confirmed, unique_truth, visits, visit_times))

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
        q_start = _midpoint(current, "end_lo", "end_hi")
        q_stop = _midpoint(following, "onset_lo", "onset_hi")
        pair_data.append({"valid": q_start is not None and q_stop is not None and q_stop > q_start,
                          "start": q_start, "stop": q_stop, "current": i, "following": i + 1})

    rules = (("C1_4", 4.0), ("C1_7", 7.0), ("C2_095", 0.95))
    results = []
    for rule, criterion in rules:
        scored_pairs = []
        for pair in pair_data:
            scored = dict(pair)
            if not pair["valid"]:
                scored.update({"passed": False, "censor": pair["start"], "diagnostic": None})
            else:
                lower = bisect_left(visit_times, pair["start"])
                upper = bisect_right(visit_times, pair["stop"])
                interval_visits = visits[lower:upper]
            if pair["valid"] and rule.startswith("C1"):
                passed, censor, longest = _c1(interval_visits, pair["start"], pair["stop"], criterion)
                scored.update({"passed": passed, "censor": censor, "diagnostic": longest})
            elif pair["valid"]:
                fraction, censor = _opportunity(interval_visits, pair["start"], pair["stop"])
                scored.update({"passed": fraction >= criterion, "censor": censor,
                               "diagnostic": fraction})
            scored_pairs.append(scored)

        passed = [pair for pair in scored_pairs if pair["passed"]]
        censored = [pair for pair in scored_pairs if not pair["passed"]]
        censor_times = [pair["censor"] for pair in censored if pair["censor"] is not None]
        hidden_passed = 0
        mapped_trueconsecutive = 0
        rejected_trueconsecutive = 0
        for pair in scored_pairs:
            left, right = pair["current"], pair["following"]
            left_truth, right_truth = unique_ep.get(left), unique_ep.get(right)
            consecutive = (left_truth is not None and right_truth is not None and
                           right_truth == left_truth + 1)
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
            previous_onset = _midpoint(confirmed[i - 1], "onset_lo", "onset_hi")
            following_end = _midpoint(confirmed[i + 1], "end_lo", "end_hi")
            if (previous_onset is None or following_end is None or previous_onset < start + 2.0 or
                    following_end > stop - 2.0):
                continue
            onset_mid = _midpoint(confirmed[i], "onset_lo", "onset_hi")
            end_mid = _midpoint(confirmed[i], "end_lo", "end_hi")
            if onset_mid is None or end_mid is None:
                continue
            recovered_values.append((end_mid - onset_mid,
                                     following_pair["stop"] - following_pair["start"],
                                     preceding_pair["stop"] - preceding_pair["start"]))
            indices = (unique_ep.get(i - 1), unique_ep.get(i), unique_ep.get(i + 1))
            if (None in indices or indices[1] != indices[0] + 1 or indices[2] != indices[1] + 1 or
                    not set(indices).issubset(reference_set)):
                continue
            previous, current, following = (ordered_truth[index] for index in indices)
            selected_truth_values.append((float(current["end"]) - float(current["onset"]),
                                          float(following["onset"]) - float(current["end"]),
                                          float(current["onset"]) - float(previous["end"])))
            recovered_matched_values.append((end_mid - onset_mid,
                                              following_pair["stop"] - following_pair["start"],
                                              preceding_pair["stop"] - preceding_pair["start"]))

        recovered_r = _partial_corr(recovered_values)
        selected_oracle_r = _partial_corr(selected_truth_values)
        recovered_matched_r = _partial_corr(recovered_matched_values)
        total_bias = _difference(recovered_r, oracle_r_all)
        selection_bias = _difference(selected_oracle_r, oracle_r_all)
        boundary_bias = _difference(recovered_matched_r, selected_oracle_r)
        row = dict(base)
        row.update({
            "rule": rule,
            "rule_value": criterion,
            "pair_count": len(scored_pairs),
            "invalid_pair_count": sum(not pair["valid"] for pair in scored_pairs),
            "eligible_count": len(passed),
            "censored_count": len(censored),
            "censor_time_min": min(censor_times) if censor_times else None,
            "censor_time_mean": mean(censor_times) if censor_times else None,
            "censor_time_max": max(censor_times) if censor_times else None,
            "coverage_diagnostic_mean": mean(pair["diagnostic"] for pair in scored_pairs
                                               if pair["diagnostic"] is not None) if any(
                                                   pair["diagnostic"] is not None for pair in scored_pairs) else None,
            "pairs_passed": len(passed),
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
            "total_bias": total_bias,
            "selection_bias": selection_bias,
            "boundary_bias": boundary_bias,
            "oracle_r_all_undefined": oracle_r_all is None,
            "recovered_r_undefined": recovered_r is None,
            "selected_oracle_r_undefined": selected_oracle_r is None,
            "recovered_matched_r_undefined": recovered_matched_r is None,
            "total_bias_undefined": total_bias is None,
            "selection_bias_undefined": selection_bias is None,
            "boundary_bias_undefined": boundary_bias is None,
        })
        results.append(row)
    return results


__all__ = ["score_run"]
