"""Gain-free, development-only archive qualification for G3a.

This screen reuses X4/X5 and DF timing features. It fits only the unmarked B0
base, never an offset, association or forecast contrast. Eclipse validation is
an external, explicitly supplied decision; ordinary gates remain observable
when that decision is absent.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
import math

import numpy as np

from dnmem.extract import MIN_QUIET_NIGHTS, _nights, _runs, observer, visits
from dnmem.extract_x3 import SPLIT_GAP
from dnmem.extract_x4 import causal_confirmations, x4_episodes
from dnmem.extract_x5 import decisive_visits, x5_episodes
from dnmem.r2_models import _previous, _validate
from dnmem.r2b_features import decoupled_schedule, decisive_feature
from dnmem.r2b_models import fit_bases
from dnmem.r2b_scoring import outcome_evidence

DEFINITION_VERSION = "g3a-gain-free-qualification-v1"
CUTOFF = 2447892.5
LAST_DECADE_START = date(1980, 1, 1).toordinal() + 1721424.5
MARGIN = 1.0
MIN_SUPPORTED = 40
MIN_ELIGIBLE = .7
BOUND_TOLERANCE = 1e-6


def validated_rows(rows):
    """Reject an unexpected record, rather than quietly narrowing acquisition."""
    result, seen = [], set()
    for source in rows:
        row = dict(source)
        jd, magnitude = float(row["JD"]), float(row["mag"])
        if not math.isfinite(jd) or not math.isfinite(magnitude) or jd >= CUTOFF:
            raise ValueError("G3a needs finite native reports strictly before 1990")
        try:
            date.fromordinal(math.floor(jd - 1721424.5))
        except (ValueError, OverflowError) as error:
            raise ValueError("report JD is outside the supported calendar") from error
        if row["band"] != "Vis." or row["val"] != "V" or row["fainterThan"] not in ("0", "1"):
            raise ValueError("G3a requires native validated visual reports and explicit limit flags")
        identifier = row["obsID"]
        if not identifier or identifier in seen or not observer(row):
            raise ValueError("G3a requires unique report IDs and an observer identifier")
        seen.add(identifier)
        result.append(row)
    return sorted(result, key=lambda row: (float(row["JD"]), row["obsID"]))


def coverage_summary(rows, threshold):
    years, months = {}, {}
    for row in rows:
        jd = float(row["JD"])
        day = date.fromordinal(math.floor(jd - 1721424.5))
        for table, key in ((years, day.year), (months, day.month)):
            group = table.setdefault(key, {"reports": 0, "limits": 0, "nights": set(),
                                           "observer_nights": set(), "years": set()})
            group["reports"] += 1
            group["limits"] += row["fainterThan"] == "1"
            group["nights"].add(math.floor(jd))
            group["observer_nights"].add((observer(row), math.floor(jd)))
            group["years"].add(day.year)

    def clean(table):
        return [{"year" if table is years else "month": key,
                 "reports": value["reports"], "limits": value["limits"],
                 "observed_nights": len(value["nights"]),
                 "observer_nights": len(value["observer_nights"]),
                 "contributing_years": len(value["years"])} for key, value in sorted(table.items())]

    votes = visits(rows, threshold)
    times = sorted({vote["t"] for vote in votes})
    limits = sum(row["fainterThan"] == "1" for row in rows)
    return {"reports": len(rows), "positive_reports": len(rows) - limits, "limits": limits,
            "limit_fraction": limits / len(rows) if rows else None,
            "observed_nights": len({math.floor(float(row["JD"])) for row in rows}),
            "observer_nights": len({(observer(row), math.floor(float(row["JD"]))) for row in rows}),
            "informative_visits": len(votes),
            "informative_nights": len({math.floor(vote["t"]) for vote in votes}),
            "longest_informative_spacing_days": max((b - a for a, b in zip(times, times[1:])), default=None),
            "annual": clean(years), "seasonal": clean(months)}


def morphology_screen(rows, threshold):
    """Operational sustained-brightness flag, not a subtype classifier.

    A supported run has >=10 bright nights, >=2 bright observers and no
    internal informative spacing >7 days. X4's night grouping and <=3-night
    quiet-run merge are retained. Flag one >=60-day run or three >=40-day
    runs, measured between the first and last threshold-bright votes.
    """
    votes = visits(rows, threshold)
    nights = _nights(votes)
    labels = {}
    for key, own in nights.items():
        bright = sum(vote["cls"] == "B" for vote in own)
        labels[key] = "B" if 2 * bright > len(own) else "F" if 2 * bright < len(own) else "M"
    keys = sorted(nights)
    runs = [(run, split) for run, split in _runs(keys, lambda key: labels[key] != "F", SPLIT_GAP)
            if any(labels[key] == "B" for key in run)]
    merged = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            earlier, previous_split = merged.pop()
            run = earlier + [key for key in keys if earlier[-1] < key < run[0]] + run
            split = previous_split
        merged.append((run, split))
    supported = []
    for run, _ in merged:
        own = sorted((vote for key in run for vote in nights[key]), key=lambda vote: vote["t"])
        bright = [vote for vote in own if vote["cls"] == "B"]
        first, last = bright[0]["t"], bright[-1]["t"]
        times = sorted({vote["t"] for vote in own if first <= vote["t"] <= last})
        hole = max((b - a for a, b in zip(times, times[1:])), default=0.)
        if (len({math.floor(vote["t"]) for vote in bright}) >= 10
                and len({vote["observer"] for vote in bright}) >= 2 and hole <= 7.):
            supported.append(last - first)
    long = sum(span >= 60. for span in supported)
    repeated = sum(span >= 40. for span in supported)
    return {"passed": long == 0 and repeated < 3,
            "candidate_runs": len(merged), "supported_runs": len(supported),
            "runs_at_least_60_days": long, "runs_at_least_40_days": repeated,
            "longest_supported_bright_span_days": max(supported, default=None),
            "absence_of_flag_is_not_subtype_validation": True}


def prepare_df_features(rows, threshold, *, emissions=None):
    """DF-only reuse of the frozen feature builders; retain no point clocks."""
    times = [float(row["JD"]) for row in rows]
    original = causal_confirmations(rows, threshold) if emissions is None else list(emissions)
    if (len({emission["emission_index"] for emission in original}) != len(original)
            or any(not all(math.isfinite(emission[key]) for key in (
                       "bright_first_at", "last_bright_at", "emitted_at"))
                   or not emission["bright_first_at"] <= emission["last_bright_at"] <= emission["emitted_at"] < CUTOFF
                   for emission in original)
            or any(b["emitted_at"] <= a["emitted_at"] for a, b in zip(original, original[1:]))):
        raise ValueError("emissions must have unique IDs and increasing pre-1990 issues")
    observed = decisive_visits(rows, threshold, MARGIN)
    audit = decoupled_schedule(original, observed, CUTOFF)
    by_id = {emission["emission_index"]: emission for emission in original}
    schedules = {row["emission_index"]: row for row in audit}
    features = [decisive_feature(rows, times, by_id[schedule["emission_index"]], schedule,
                                schedules, by_id, threshold)
                for schedule in audit if schedule["status"] == "scheduled"]
    _validate(features)
    return features, audit


def summarize_features(features, evidence):
    """Count usable timing/mark fields and positive-exposure outcome support."""
    _validate(features)
    by_id = {row["emission_index"]: row for row in evidence}
    if len(by_id) != len(evidence) or set(by_id) != {row["emission_index"] for row in features}:
        raise ValueError("qualification feature/outcome population mismatch")
    timed = marked = supported = zero = recent = 0
    spans, normalized_evidence = [], []
    for row in features:
        ev = dict(by_id[row["emission_index"]])
        issue = float(row["issue_time"])
        if (issue >= CUTOFF or ev["issue_time"] != issue or not all(
                math.isfinite(ev[key]) and ev[key] <= CUTOFF for key in ("computed_as_of", "evidence_available_at"))):
            raise ValueError("qualification evidence exceeds development information")
        anchored = row.get("clock_anchor") is not None and _previous(row)
        timed += anchored
        mark = row.get("mark")
        if mark is not None and not math.isfinite(float(mark)):
            raise ValueError("nonfinite decisive span")
        markable = anchored and mark is not None and float(mark) > 0
        marked += markable
        if markable:
            spans.append(float(mark))
        kind, usable = ev["kind"], False
        if kind == "interval":
            lo, hi = ev["onset_lo"], ev["onset_hi"]
            if not all(math.isfinite(value) for value in (lo, hi)) or not issue < lo < hi <= min(
                    CUTOFF, ev["computed_as_of"], ev["evidence_available_at"]):
                raise ValueError("invalid or reversed qualification onset interval")
            usable = True
        elif kind == "right_censored":
            censor = ev["censor_at"]
            if not math.isfinite(censor) or not issue <= censor <= min(
                    CUTOFF, ev["computed_as_of"], ev["evidence_available_at"]):
                raise ValueError("invalid qualification censoring support")
            usable = censor > issue
            if not usable:
                zero += 1
                ev.update(kind="excluded", reason="zero_exposure_qualification")
        elif kind != "excluded":
            raise ValueError("qualification expects interval, censor or excluded evidence")
        if markable and usable:
            supported += 1
            recent += LAST_DECADE_START <= issue < CUTOFF
        normalized_evidence.append(ev)
    return {"df_scheduled": len(features), "df_timing_supported": timed,
            "df_feature_supported_marked": marked, "df_outcome_supported_marked": supported,
            "df_zero_exposure_outcomes": zero, "supported_last_decade_count": recent,
            "supported_last_decade_rate_per_year": recent / 10.,
            "decisive_span_days_quantiles": [float(value) for value in np.quantile(spans, [.1, .5, .9])]
            if spans else None}, normalized_evidence


def base_convergence(features, evidence):
    """Fit the unmarked base; report optimization diagnostics without scores."""
    unmarked = [{**row, "mark": None} for row in features]
    try:
        base = fit_bases(unmarked, evidence, CUTOFF, rungs=("B0",))["B0"]
    except ValueError:
        return {"passed": False, "status": "insufficient_information_or_fit_failed",
                "all_starts_converged": False, "nondegenerate": False}
    metadata = base.metadata
    groups = [metadata[key] for key in ("base_fit", "constant_fit", "remaining_fit")]
    all_converged = all(group["stable"] and len(group["attempts"]) == 2
                        and all(attempt["successful"] for attempt in group["attempts"]) for group in groups)
    bounds = [(-5., 8.), (-3., 3.), (-3., 3.), (math.log(.03), math.log(2.))]
    flags = []
    for label, group in zip(("B0", "constant", "remaining"), groups):
        own_bounds = bounds if label == "B0" else [bounds[0], bounds[-1]]
        for attempt in group["attempts"]:
            theta = attempt["parameters"]
            if len(theta) != len(own_bounds) or any(value is None or not math.isfinite(value) for value in theta):
                flags.append(label + ":nonfinite_parameters")
            elif any(value <= lo + BOUND_TOLERANCE or value >= hi - BOUND_TOLERANCE
                     for value, (lo, hi) in zip(theta, own_bounds)):
                flags.append(label + ":parameter_at_bound")
    design = metadata["base_fit"]
    full_rank = design.get("design_rank") == design.get("design_columns") == 3
    nonconstant = len(base.timing.transform) == 2 and all(
        not fixed and math.isfinite(center) and math.isfinite(scale) and scale > 0
        for center, scale, fixed in base.timing.transform)
    if not full_rank:
        flags.append("B0:rank_deficient")
    if not nonconstant:
        flags.append("B0:constant_or_invalid_timing_covariate")
    nondegenerate = not flags
    return {"passed": all_converged and nondegenerate,
            "status": "passed" if all_converged and nondegenerate else "convergence_or_degeneracy_failure",
            "all_starts_converged": all_converged, "nondegenerate": nondegenerate,
            "declared_starts": sum(len(group["attempts"]) for group in groups),
            "design_rank": design.get("design_rank"), "design_columns": design.get("design_columns"),
            "degeneracy_flags": sorted(set(flags)), "timing_rows": metadata["timing_rows"],
            "not_a_global_identifiability_certificate": True}


def qualify_star(rows, star, threshold, *, stop=CUTOFF, eclipse_passed=False, emissions=None):
    """Return only aggregate qualification fields for a caller-selected reduction.

    Source identity and acquisition provenance are the adapter's responsibility.
    Native rows are nevertheless rejected on any post-split JD. Custom frozen
    emissions permit a separately validated eclipse rule without modifying X4.
    """
    if stop != CUTOFF:
        raise ValueError("G3a qualification uses the frozen 1990 split only")
    if not math.isfinite(threshold):
        raise ValueError("qualification threshold must be finite")
    if not isinstance(eclipse_passed, bool):
        raise ValueError("eclipse_passed must be an explicit boolean")
    rows = validated_rows(rows)
    coverage = coverage_summary(rows, threshold)
    closed = [vote for vote in decisive_visits(rows, threshold, MARGIN) if vote["available_at"] <= CUTOFF]
    ids = {identifier for vote in closed for identifier in vote["ids"]}
    closed_rows = [row for row in rows if row["obsID"] in ids]
    episodes = x5_episodes(closed_rows, threshold, MARGIN, episodes=x4_episodes(closed_rows, threshold))
    confirmed = [episode for episode in episodes if episode["confirmed_event"]]
    available = sum(episode["onset_report_available"] for episode in confirmed)
    eligible = sum(episode["onset_report_eligible"] for episode in confirmed)
    fraction = eligible / len(confirmed) if confirmed else None
    features, schedule = prepare_df_features(closed_rows, threshold, emissions=emissions)
    evidence = outcome_evidence(closed_rows, features, stop=CUTOFF, threshold=threshold)
    counts, evidence = summarize_features(features, evidence)
    convergence = base_convergence(features, evidence)
    morphology = morphology_screen(closed_rows, threshold)
    ordinary = (counts["df_outcome_supported_marked"] >= MIN_SUPPORTED
                and fraction is not None and fraction >= MIN_ELIGIBLE
                and convergence["passed"] and morphology["passed"])
    eclipse_required = "".join(star.casefold().split()) in ("ugem", "ippeg")
    return {"definition_version": DEFINITION_VERSION, "star": star, "threshold": threshold,
            "x5_margin": MARGIN, "cutoff_exclusive": CUTOFF, "coverage": coverage,
            "confirmed_events": len(confirmed), "x5_available_events": available,
            "x5_eligible_events": eligible, "x5_eligible_fraction": fraction,
            **counts, "schedule_status_counts": dict(Counter(row["status"] for row in schedule)),
            "base_only_convergence": convergence, "morphology": morphology,
            "eclipse_required": eclipse_required, "eclipse_passed": eclipse_passed,
            "ordinary_passed": ordinary,
            "qualified": ordinary and (not eclipse_required or eclipse_passed),
            "no_mark_fit_or_association_computed": True}


__all__ = ["DEFINITION_VERSION", "CUTOFF", "MARGIN", "qualify_star", "validated_rows",
           "coverage_summary", "morphology_screen", "prepare_df_features", "summarize_features",
           "base_convergence"]
