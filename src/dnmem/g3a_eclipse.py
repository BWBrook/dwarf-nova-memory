"""Frozen hold-star feasibility guards, not eclipse correction or certification."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import math
from statistics import median

import numpy as np

from dnmem.extract import VISIT_SPAN, observer
from dnmem.extract_x4 import ARM_MARGIN, CONFIRM_MARGIN, _closed_visits
from dnmem.extract_x5 import x5_episodes

CUTOFF = 2447892.5
PERIODS = {"U Gem": .17690618, "IP Peg": .15820764}
PHASES = tuple(i / 16 for i in range(16))
WIDTHS, DEPTHS, JITTERS = (.10, .25), (1., 3.), (0., .03)
SCATTER = .22
NAMESPACE = "g3a-eclipse-feasibility-v1"


def reduce_observer_nights(rows, mode):
    """One derived estimate per observer/JD night, released after that night.

    Both reductions use the same fixed night-boundary timestamps. A full-night
    statistic cannot be inserted into an earlier report; its last arrival is
    unknown until the night closes. Existing visits add another 0.15 day.
    Native rows are not mutated; derived provenance retains source support.
    """
    if mode not in {"median", "brightest"}:
        raise ValueError("reduction must be median or brightest")
    grouped = defaultdict(list)
    for row in rows:
        if row["band"] != "Vis." or row["val"] != "V":
            continue
        t = float(row["JD"])
        if not math.isfinite(t) or not 0 < t < CUTOFF:
            raise ValueError("hold-star reduction requires pre-1990 native JD")
        grouped[observer(row), math.floor(t)].append(row)
    result = []
    for (who, night), group in sorted(grouped.items()):
        if night + 1. >= CUTOFF:
            continue
        positive = [float(r["mag"]) for r in group if r["fainterThan"] == "0"]
        limits = [float(r["mag"]) for r in group if r["fainterThan"] == "1"]
        if not positive and not limits:
            raise ValueError("unresolved limiting flag")
        value = (median(positive) if mode == "median" else min(positive)) if positive else max(limits)
        if not math.isfinite(value):
            raise ValueError("nonfinite magnitude")
        source = sorted(group, key=lambda r: (float(r["JD"]), r["obsID"]))
        row = dict(source[-1])
        row.update(obsID=f"g3a-night:{who}:{night}", JD=str(night + 1.), mag=str(value),
                   fainterThan="0" if positive else "1", uncert="",
                   g3a_reduction=mode, g3a_source_ids=[r["obsID"] for r in source],
                   g3a_source_first_jd=source[0]["JD"], g3a_source_last_jd=source[-1]["JD"])
        result.append(row)
    return sorted(result, key=lambda r: (float(r["JD"]), r["obsID"]))


def two_night_confirmations(rows, threshold=10.):
    """Keep X4 arming, requiring two observers AND nights to confirm faintness."""
    if not math.isfinite(threshold):
        raise ValueError("threshold must be finite")
    strong, bright_observers, faint_observers, faint_nights = defaultdict(set), set(), set(), set()
    first = last = faint_first = None
    armed, emissions = False, []
    closed = _closed_visits(rows, threshold)
    i = 0
    while i < len(closed):
        at = closed[i]["closed_at"]
        j = i + 1
        while j < len(closed) and closed[j]["closed_at"] == at:
            j += 1
        batch, i = closed[i:j], j
        bright = [v for v in batch if v["cls"] == "B"]
        if bright:
            faint_observers.clear(); faint_nights.clear(); faint_first = None
            if not bright_observers:
                first = at
            for vote in bright:
                bright_observers.add(vote["observer"])
                if vote["value"] <= threshold - ARM_MARGIN:
                    strong[vote["observer"]].add(vote["night"])
            last = at
            armed = armed or len(strong) >= 2 or any(len(n) >= 2 for n in strong.values())
            continue
        faint = [v for v in batch if v["faint_level"] >= threshold + CONFIRM_MARGIN]
        if not faint:
            continue
        if not faint_observers:
            faint_first = at
        faint_observers.update(v["observer"] for v in faint)
        faint_nights.update(v["night"] for v in faint)
        if len(faint_observers) < 2 or len(faint_nights) < 2:
            continue
        if armed:
            emissions.append(dict(emission_index=len(emissions), emitted_at=at,
                                  bright_first_at=first, last_bright_at=last,
                                  faint_first_at=faint_first, faint_observer_count=len(faint_observers),
                                  faint_night_count=len(faint_nights), bright_observer_count=len(bright_observers),
                                  strong_bright_observer_count=len(strong),
                                  g3a_eclipse_rule="two-observers-and-two-nights"))
        strong.clear(); bright_observers.clear(); faint_observers.clear(); faint_nights.clear()
        first = last = faint_first = None
        armed = False
    return emissions


def _time(event):
    return event["onset_t"] if event.get("onset_t") is not None else event["peak_t"]


def _match(left, right, tolerance=3.):
    candidates = sorted((abs(_time(a) - _time(b)), i, j)
                        for i, a in enumerate(left) for j, b in enumerate(right)
                        if abs(_time(a) - _time(b)) <= tolerance)
    used_left, used_right, pairs = set(), set(), []
    for _, i, j in candidates:
        if i not in used_left and j not in used_right:
            pairs.append((i, j)); used_left.add(i); used_right.add(j)
    return pairs


def _quantiles(values):
    return (float(np.median(values)), float(np.quantile(values, .9))) if values else (None, None)


def compare_reductions(median_rows, brightest_rows, threshold, median_qualification, brightest_qualification):
    """Compare extraction outputs and the same ordinary gates without fitting."""
    left = [e for e in x5_episodes(median_rows, threshold) if e["confirmed_event"]]
    right = [e for e in x5_episodes(brightest_rows, threshold) if e["confirmed_event"]]
    pairs = _match(left, right)
    denominator = max(len(left), len(right))
    matching = len(pairs) / denominator if denominator else None
    agreement = sum(left[i]["onset_report_eligible"] == right[j]["onset_report_eligible"]
                    for i, j in pairs) / denominator if denominator else None
    counts = [int(q["df_outcome_supported_marked"]) for q in (median_qualification, brightest_qualification)]
    feature_counts = [int(q["df_feature_supported_marked"]) for q in (median_qualification, brightest_qualification)]
    relative = abs(counts[0] - counts[1]) / max(counts) if max(counts) else None
    spans = [abs(left[i]["bright_span"] - right[j]["bright_span"]) for i, j in pairs
             if left[i].get("bright_span") is not None and right[j].get("bright_span") is not None]
    q50, q90 = _quantiles(spans)
    gates = dict(ordinary_both=all(q["ordinary_passed"] for q in (median_qualification, brightest_qualification)),
                 episode_matching=matching is not None and matching >= .9,
                 eligible_window_agreement=agreement is not None and agreement >= .9,
                 supported_count_agreement=relative is not None and relative <= .1,
                 span_sample=len(spans) >= 20,
                 span_median=q50 is not None and q50 <= 1., span_p90=q90 is not None and q90 <= 2.)
    return dict(passed=all(gates.values()), gates=gates, confirmed_counts=[len(left), len(right)],
                matched_events=len(pairs), matching_fraction=matching, eligible_agreement_fraction=agreement,
                supported_counts=counts, supported_relative_difference=relative, matched_span_pairs=len(spans),
                feature_supported_counts=feature_counts,
                matched_span_abs_difference_median=q50, matched_span_abs_difference_p90=q90)


def _synthetic_template(rows, threshold, star):
    source = sorted(rows, key=lambda r: (float(r["JD"]), r["obsID"]))
    times = np.asarray([float(r["JD"]) for r in source])
    if not len(times) or np.any(~np.isfinite(times)) or np.any(times <= 0) or np.any(times >= CUTOFF):
        raise ValueError("synthetic eclipse cadence must be pre-1990")
    onsets = np.arange(times.min() + 10., times.max() - 30., 60.)
    duration = np.where(np.arange(len(onsets)) % 2 == 0, 12., 18.)
    truths = [dict(onset_t=float(t), end_t=float(t + d), span=float(d - 3.), index=i)
              for i, (t, d) in enumerate(zip(onsets, duration))]
    magnitude = np.full(len(times), threshold + 2.)
    for start, length in zip(onsets, duration):
        phase = times - start
        active = (phase >= -2.) & (phase <= length + 4.)
        value = np.where(phase < 2., threshold - phase,
                         np.where(phase <= length - 4., threshold - 2., threshold + .5 * (phase - length)))
        magnitude[active] = value[active]
    seed = int.from_bytes(hashlib.sha256(f"{NAMESPACE}|{star}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    magnitude += rng.normal(0., SCATTER, len(times))
    nights = np.floor(times).astype(int)
    keys, inverse = np.unique(nights, return_inverse=True)
    jitter = rng.uniform(-1., 1., len(keys))[inverse]
    return source, times, magnitude, jitter, truths, seed


def _synthetic_rows(source, magnitude):
    return [{**r, "mag": str(float(value)), "fainterThan": "0", "uncert": ""}
            for r, value in zip(source, magnitude)]


def _recovery(rows, threshold, truths, mode):
    reduced = reduce_observer_nights(rows, mode)
    episodes = [e for e in x5_episodes(reduced, threshold) if e["confirmed_event"]]
    pairs = _match(truths, episodes)
    recovered = {i for i, _ in pairs}
    errors = [abs(episodes[j]["bright_span"] - truths[i]["span"]) for i, j in pairs
              if episodes[j].get("bright_span") is not None]
    q50, q90 = _quantiles(errors)
    alerts = two_night_confirmations(reduced, threshold)
    bad = 0
    for alert in alerts:
        active = [t for t in truths if t["onset_t"] - 2 <= alert["bright_first_at"] <= t["end_t"]]
        if len(active) != 1 or alert["emitted_at"] < active[0]["end_t"]:
            bad += 1
    early = bad / len(alerts) if alerts else None
    return dict(recovered=recovered, count=len(recovered), alerts=len(alerts), early_count=bad,
                early_fraction=early, span_count=len(errors), span_error_median=q50, span_error_p90=q90)


def eclipse_sensitivity(rows, star, threshold):
    """Fixed synthetic dip envelope on supplied early cadence; never fits real magnitudes."""
    if star not in PERIODS or not math.isfinite(threshold):
        raise ValueError("unknown hold star or nonfinite threshold")
    rows = [r for r in rows if r["band"] == "Vis." and r["val"] == "V"]
    if not rows:
        return dict(passed=False, status="inconclusive", reason="no eligible cadence", cases=0)
    source, times, magnitude, jitter, truths, seed = _synthetic_template(rows, threshold, star)
    baseline_rows = _synthetic_rows(source, magnitude)
    baseline = {mode: _recovery(baseline_rows, threshold, truths, mode) for mode in ("median", "brightest")}
    def accurate(record):
        return (record["early_fraction"] is not None and record["early_fraction"] < .02
                and record["span_error_median"] is not None and record["span_error_median"] <= 1.
                and record["span_error_p90"] is not None and record["span_error_p90"] <= 2.)
    public_baseline = {mode: {k: v for k, v in record.items() if k != "recovered"}
                       for mode, record in baseline.items()}
    if any(record["count"] < 20 or not accurate(record) for record in baseline.values()):
        return dict(passed=False, status="inconclusive", reason="baseline cadence/trapezoids fail minimum recovery or accuracy",
                    seed=seed, baseline=public_baseline, cases=0, injected_events=len(truths))
    results = []
    for phase in PHASES:
        for width in WIDTHS:
            for depth in DEPTHS:
                for amplitude in JITTERS:
                    orbital = ((times - times.min()) / PERIODS[star] + phase + amplitude * jitter) % 1.
                    dip = np.minimum(orbital, 1. - orbital) <= width / 2.
                    altered = _synthetic_rows(source, magnitude + depth * dip)
                    reductions = {}
                    for mode in ("median", "brightest"):
                        record = _recovery(altered, threshold, truths, mode)
                        retention = len(record["recovered"] & baseline[mode]["recovered"]) / baseline[mode]["count"]
                        reductions[mode] = {k: v for k, v in record.items() if k != "recovered"}
                        reductions[mode].update(relative_recovery=retention, passed=retention >= .9 and accurate(record))
                    results.append(dict(phase=phase, width_cycles=width, depth_mag=depth,
                                        jitter_cycles=amplitude, reductions=reductions,
                                        passed=all(r["passed"] for r in reductions.values())))
    return dict(passed=all(r["passed"] for r in results), status="passed" if all(r["passed"] for r in results) else "failed",
                scope="conditional all-positive synthetic reports at retained native timestamps; fixed trapezoids, not eclipse correction",
                namespace=NAMESPACE, seed=seed, period_days=PERIODS[star], scatter_mag=SCATTER,
                injected_events=len(truths), baseline=public_baseline, cases=len(results),
                failed_cases=sum(not r["passed"] for r in results), results=results)


def qualify_eclipse_star(rows, star_config, stop=CUTOFF):
    """Combine the ordinary gain-free screen and both frozen eclipse guards."""
    from dnmem.g3a_qualification import qualify_star

    star, threshold = star_config["name"], float(star_config["threshold"])
    if star not in PERIODS or not star_config["eclipsing_hold"] or stop != CUTOFF:
        raise ValueError("only the two approved holds before the fixed 1990 split")
    reductions, reports = {}, {}
    for mode in ("median", "brightest"):
        reduced = reduce_observer_nights(rows, mode)
        reductions[mode] = reduced
        reports[mode] = qualify_star(reduced, star, threshold, eclipse_passed=False,
                                    emissions=two_night_confirmations(reduced, threshold))
    comparison = compare_reductions(reductions["median"], reductions["brightest"], threshold,
                                    reports["median"], reports["brightest"])
    synthetic = eclipse_sensitivity(rows, star, threshold)
    passed = comparison["passed"] and synthetic["passed"]
    return {**reports["median"], "qualified": passed, "eclipse_passed": passed,
            "eclipse_guard_scope": "feasibility robustness only; fixed JD-night reductions and synthetic dip envelope, not phase correction",
            "eclipse_reduction_comparison": comparison, "eclipse_synthetic": synthetic,
            "eclipse_ordinary_reductions": reports, "analysis_reduction_if_later_used": "median"}
