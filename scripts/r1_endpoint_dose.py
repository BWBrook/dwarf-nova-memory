#!/usr/bin/env python3
"""Exploratory paired endpoint-error diagnostic on retained A10d synthetic seeds."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import log_ndtr

from dnmem.directional_forecast import (
    DirectionalBundle, _m2_covariates, _m2_transform, _standard, fit_directional,
)
from dnmem.extract import MIN_QUIET_NIGHTS, _nights, _runs, visits
from dnmem.extract_x4 import SPLIT_GAP, VISIT_SPAN, x4_episodes
from dnmem.forecast_experiment import ERAS, crop_stratum, source_strata
from dnmem.joint_benchmark import generate_observations
from dnmem.ledger_forecast import ForecastModel, _BOUNDS, _previous_value
from dnmem.oc_statistics import cluster_interval
from dnmem.outcome_evidence_v4 import outcome_evidence as outcome_evidence_v4
from dnmem.prefix_features import (
    COVERAGE_HOLE, LOOKBACK, PREVIOUS_MARGIN, _coverage_index, _longest_hole,
    forecast_ledger, outcome_evidence,
)
from dnmem.x4_benchmark import seed_for

BASE = "a10c-oc|8f5df44b950ec5781ba1e31e074e56976909a051"
DEV_BASE = "r1-endpoint-dose-development-v1"
DOSE_BASE = "r1-endpoint-dose-v1"
SIGMAS = (0.0, 1.0, 2.0, 4.0, 6.0)
MODELS = ("M0", "M2", "M3", "P3")
INPUT = ROOT / "outputs/a04i_inputs_frozen_20261108/inputs.json"
CONFIG = ROOT / "configs/a04i_selected.json"
PROTOCOL = ROOT / "docs/protocols/r1-observation-endpoint-diagnostics-v1.md"
RETAINED = ROOT / "outputs/a10d_run_8f5df44/a10d_oc"
SOURCE_PATHS = tuple(["scripts/r1_endpoint_dose.py"] + ["src/dnmem/" + name + ".py" for name in (
    "directional_forecast", "ledger_forecast", "prefix_features", "extract", "extract_x3", "extract_x4",
    "forecast_experiment", "joint_benchmark", "injection_truth", "injection_truth_v2", "injection_observe",
    "phase_cadence", "x4_benchmark", "oc_statistics", "outcome_evidence_v4")])


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def regenerate(inputs, configuration, case, replicate, base=BASE):
    """Match A10d observations while retaining its generator's partial events."""
    strata = source_strata(inputs)
    blocks = [strata[era] for era in ERAS] * 2
    first = strata[ERAS[0]]
    blocks += [crop_stratum(first, first["start"], first["start"] + 8 * 365.25)]
    rows, truth, metadata = [], [], []
    cursor = 1000.5
    for index, source in enumerate(blocks):
        seed = seed_for(base, configuration["pair_id"], case, replicate, "block", index)
        observed, history, generator, cadence, contamination = generate_observations(
            inputs, configuration, source, seed, process=case)
        shift = cursor - source["start"]
        if abs(shift - round(shift)) > 1e-7:
            raise ValueError("noninteger source translation")
        shift = int(round(shift))
        rows.extend({**r, "JD": str(float(r["JD"]) + shift),
                     "obsID": f"synthetic-block-{index}-{r.get('obsID', '')}"} for r in observed)
        truth.extend({**event, "id": f"block-{index}-{event['id']}", "block": index,
                      **{key: event[key] + shift for key in ("onset", "end", "peak_t")}}
                     for event in generator.truth_catalogue(history, 10.0))
        stop = source["stop"] + shift
        metadata.append({"block": index, "source_era": source["stratum"], "seed": seed,
                         "source_start": source["start"], "source_stop": source["stop"],
                         "synthetic_start": cursor, "synthetic_stop": stop,
                         "cadence": {k: v for k, v in cadence.items() if k != "events"},
                         "contamination": contamination, "case": case})
        cursor = math.ceil(stop + 30 - 0.5) + 0.5
    rows.sort(key=lambda r: float(r["JD"]))
    truth.sort(key=lambda e: (e["block"], e["onset"]))
    return rows, truth, {"training_cutoff": metadata[2]["synthetic_stop"],
                         "stop": metadata[-1]["synthetic_stop"], "blocks": metadata,
                         "time_basis": "artificial relative days; integer translations of pre1960 patterns"}


def bright_groups(votes):
    """Raw bright-visit membership of the unchanged X4 detector's runs."""
    nights = _nights(votes)
    label = {}
    for key, own in nights.items():
        bright = sum(v["cls"] == "B" for v in own)
        label[key] = "B" if 2 * bright > len(own) else "F" if 2 * bright < len(own) else "M"
    runs = [(run, split) for run, split in _runs(sorted(nights), lambda k: label[k] != "F", SPLIT_GAP)
            if any(label[k] == "B" for k in run)]
    merged = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            previous, previous_split = merged.pop()
            run = previous + [k for k in sorted(nights) if previous[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    return [[identifier for key in run for vote in nights[key] if vote["cls"] == "B"
             for identifier in vote["ids"]] for run, _ in merged]


def prepare_contexts(rows, ledger):
    indexed = sorted(rows, key=lambda r: float(r["JD"]))
    times = [float(r["JD"]) for r in indexed]
    contexts, parents = [], {}

    def find(key):
        parents.setdefault(key, key)
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parents[max(a, b)] = min(a, b)

    for feature in ledger:
        cutoff = feature["emitted_at"]
        window = indexed[bisect_right(times, cutoff - LOOKBACK):bisect_right(times, cutoff)]
        votes = visits(window, 10.0)
        episodes = x4_episodes(window, 10.0)
        groups = bright_groups(votes)
        if len(groups) != len(episodes):
            raise ValueError("raw-run identity differs from X4 episode count")
        selected = []
        for episode, identifiers in zip(episodes, groups):
            if not identifiers:
                raise ValueError("X4 episode has no bright raw identity")
            for identifier in identifiers:
                union(identifiers[0], identifier)
            if episode["peak_t"] < cutoff:
                selected.append({**episode, "identity_member": identifiers[0]})
        since = feature["bright_first_at"] - VISIT_SPAN - 1.0
        current = next((i for i in range(len(selected) - 1, -1, -1)
                        if (selected[i]["end_hi"] if selected[i]["end_hi"] is not None
                            else selected[i]["peak_t"]) >= since), None)
        contexts.append({"feature": feature, "episodes": selected, "current": current,
                         "times": sorted(v["t"] for v in votes)})
    for context in contexts:
        for episode in context["episodes"]:
            episode["event_key"] = find(episode.pop("identity_member"))
    return contexts


def dose_z(case, replicate, event_key, dose_base=DOSE_BASE):
    return random.Random(seed_for(dose_base, case, replicate, event_key)).gauss(0.0, 1.0)


def jitter_feature(context, sigma, case, replicate, dose_base=DOSE_BASE):
    feature = dict(context["feature"])
    flags = Counter()
    episodes = []
    for original in context["episodes"]:
        e = dict(original)
        error = sigma * dose_z(case, replicate, e["event_key"], dose_base)
        for key in ("end_t", "end_lo", "end_hi"):
            if e[key] is not None:
                e[key] += error
        e["added_error"] = error
        episodes.append(e)
    current = context["current"]
    if current is None:
        return feature, {"episode_missing": 1}
    e = episodes[current]
    feature.update({key: e[key] for key in ("end_t", "end_lo", "end_hi")})
    duration = e["end_t"] - e["onset_t"] if e["end_t"] is not None and e["onset_t"] is not None else None
    feature["duration"] = duration if duration is not None and duration > 0 else None
    feature["age_at_issue"] = feature["issue_time"] - e["end_t"] if e["end_t"] is not None else None
    feature["landmark_available"] = e["end_t"] is not None and e["end_t"] <= feature["emitted_at"]
    if duration is not None and duration <= 0:
        flags["nonpositive_duration"] += 1
    if e["end_t"] is not None and e["end_t"] > feature["issue_time"]:
        flags["end_after_issue"] += 1
    feature["r1_raw_duration"] = duration
    feature["r1_added_end_error"] = e["added_error"]
    feature["r1_event_key"] = e["event_key"]
    earlier = [p for p in episodes[:current] if p["confirmed_event"] and p["end_t"] is not None
               and p["onset_lo"] is not None and p["onset_lo"] > feature["prefix_start"] + PREVIOUS_MARGIN]
    p = earlier[-1] if earlier else None
    previous_duration = p["end_t"] - p["onset_t"] if p is not None and p["onset_t"] is not None else None
    feature["previous_duration"] = previous_duration if previous_duration is not None and previous_duration > 0 else None
    if previous_duration is not None and previous_duration <= 0:
        flags["nonpositive_previous_duration"] += 1
    raw_gap = e["onset_t"] - p["end_t"] if p is not None and e["onset_t"] is not None else None
    if raw_gap is not None and raw_gap > 0:
        longest, _ = _longest_hole(context["times"], p["end_t"], e["onset_t"])
        feature.update(previous_end_t=p["end_t"], previous_gap=raw_gap,
                       previous_gap_covered=longest <= COVERAGE_HOLE, previous_longest_hole=longest)
    else:
        feature.update(previous_end_t=None, previous_gap=None, previous_gap_covered=None,
                       previous_longest_hole=None)
        if raw_gap is not None:
            flags["nonpositive_previous_gap"] += 1
    feature["r1_raw_previous_gap"] = raw_gap
    feature["r1_raw_previous_duration"] = previous_duration
    gaps = []
    confirmed = [item for item in episodes[:current] if item["confirmed_event"]]
    if p is not None and p["onset_t"] is not None:
        for left, right in zip(confirmed, confirmed[1:]):
            onset = right["onset_t"]
            if onset is None or onset > p["onset_t"]:
                continue
            if not all(item["onset_t"] is not None and item["onset_t"] > feature["prefix_start"] + PREVIOUS_MARGIN
                       for item in (left, right)) or left["end_t"] is None:
                continue
            gap = onset - left["end_t"]
            if gap <= 0:
                flags["nonpositive_history_gap"] += 1
                continue
            longest, _ = _longest_hole(context["times"], left["end_t"], onset)
            if longest <= COVERAGE_HOLE:
                gaps.append(math.log(gap))
    feature["earlier_gaps"] = gaps[-6:]
    return feature, dict(flags)


def block_at(meta, issue):
    return next((b for b in meta["blocks"] if b["synthetic_start"] <= issue < b["synthetic_stop"]), None)


def fixed_anchors(ledger, truth, meta):
    anchors, counts, classifications, used = {}, Counter(), [], set()
    for f in ledger:
        block = block_at(meta, f["issue_time"])
        available = [e for e in truth if block is not None and e["block"] == block["block"]]
        matched = [e for e in available if e["onset"] <= f["bright_first_at"] <= e["end"]]
        why, event = None, matched[0] if len(matched) == 1 else None
        repeated = event is not None and event["id"] in used
        if event is not None:
            used.add(event["id"])
        if block is None:
            why = "outside_reset_blocks"
        elif not matched:
            why = "unmatched_or_false_emission"
        elif len(matched) > 1:
            why = "multiple_truth_matches"
        elif repeated:
            why = "repeat_truth_event"
        elif event["end"] > f["issue_time"]:
            why = "true_event_not_completed"
        elif any(e["onset"] <= f["issue_time"] <= e["end"] and e["id"] != event["id"] for e in available):
            why = "new_true_event_active_at_issue"
        elif any(event["end"] < e["onset"] <= f["issue_time"] for e in available):
            why = "next_true_onset_before_issue"
        else:
            why = "fixed_anchor"
            anchors[f["emission_index"]] = event["id"]
        counts[why] += 1
        classifications.append({"emission_index": f["emission_index"], "classification": why,
                                "truth_id": event["id"] if event else None})
    return anchors, dict(counts), classifications


def administrative_cutoffs(rows, ledger, meta, stop):
    loss = _coverage_index(sorted(v["t"] for v in visits([r for r in rows if float(r["JD"]) <= stop], 10.0)), stop)
    result = {}
    for i, f in enumerate(ledger):
        block = block_at(meta, f["issue_time"])
        candidates = [(stop, "record_end")]
        if block is not None:
            candidates.append((block["synthetic_stop"], "reset_block_end"))
        hole = loss(f["issue_time"])
        if hole is not None:
            candidates.append((hole, "coverage"))
        if i + 1 < len(ledger):
            candidates.append((ledger[i + 1]["issue_time"], "superseded"))
        result[f["emission_index"]] = min(candidates)
    return result


def truth_evidence(ledger, truth, anchors, cutoffs, stop):
    by_id = {e["id"]: e for e in truth}
    evidence = []
    for f in ledger:
        index, issue = f["emission_index"], f["issue_time"]
        if index not in anchors:
            continue
        current = by_id[anchors[index]]
        candidates = [e for e in truth if e["block"] == current["block"] and e["onset"] > current["end"]]
        next_event = min(candidates, key=lambda e: e["onset"]) if candidates else None
        cutoff, why = cutoffs[index]
        if cutoff < issue:
            raise ValueError("administrative censor before issue")
        row = {"emission_index": index, "issue_time": issue, "computed_as_of": stop,
               "evidence_available_at": stop, "censor_at": None, "onset_t": None,
               "truth_id": next_event["id"] if next_event else None}
        if next_event is not None and next_event["onset"] <= issue:
            raise ValueError("fixed anchor is not still-quiescent")
        if next_event is not None and next_event["onset"] <= cutoff:
            row.update(kind="point", onset_t=next_event["onset"], reason="true_onset")
        else:
            row.update(kind="right_censored", censor_at=cutoff, reason=why)
        evidence.append(row)
    return evidence


def oracle_features(ledger, truth, anchors, contexts):
    by_id = {e["id"]: e for e in truth}
    context_by_id = {c["feature"]["emission_index"]: c for c in contexts}
    result = []
    for f in ledger:
        if f["emission_index"] not in anchors:
            continue
        event = by_id[anchors[f["emission_index"]]]
        history = sorted((e for e in truth if e["block"] == event["block"] and e["end"] < event["onset"]),
                         key=lambda e: e["onset"])
        eligible = [e for e in history if e["onset"] > f["prefix_start"] + PREVIOUS_MARGIN]
        p = eligible[-1] if eligible else None
        times = context_by_id[f["emission_index"]]["times"]
        o = {**f, "landmark_available": True, "onset_t": event["onset"],
             "onset_lo": event["onset"], "onset_hi": event["onset"],
             "end_t": event["end"], "end_lo": event["end"], "end_hi": event["end"],
             "duration": event["end"] - event["onset"], "age_at_issue": f["issue_time"] - event["end"],
             "previous_end_t": p["end"] if p else None,
             "previous_gap": event["onset"] - p["end"] if p else None,
             "previous_duration": p["end"] - p["onset"] if p else None,
             "previous_gap_covered": False, "earlier_gaps": []}
        if p is not None:
            hole, _ = _longest_hole(times, p["end"], event["onset"])
            o["previous_gap_covered"] = hole <= COVERAGE_HOLE
            gaps = []
            for left, right in zip(eligible, eligible[1:]):
                gap = right["onset"] - left["end"]
                hole, _ = _longest_hole(times, left["end"], right["onset"])
                if gap > 0 and hole <= COVERAGE_HOLE:
                    gaps.append(math.log(gap))
            o["earlier_gaps"] = gaps[-6:]
        result.append(o)
    return result


def point_loglik(evidence, endpoint, mu, sigma):
    issue = float(evidence["issue_time"])
    age = issue - endpoint
    if age < 0:
        raise ValueError("endpoint after issue")
    log_survival = lambda x: 0.0 if x <= 0 else float(log_ndtr(-(math.log(x) - mu) / sigma))
    denominator = log_survival(age)
    if evidence["kind"] == "point":
        wait = float(evidence["onset_t"]) - endpoint
        if wait <= age or wait <= 0:
            raise ValueError("truth onset is not after issue")
        z = (math.log(wait) - mu) / sigma
        numerator = -math.log(wait * sigma) - 0.5 * math.log(2 * math.pi) - 0.5 * z * z
    elif evidence["kind"] == "right_censored":
        wait = float(evidence["censor_at"]) - endpoint
        if wait < age:
            raise ValueError("truth censor before issue")
        numerator = log_survival(wait)
    else:
        raise ValueError("truth evidence must be point or right_censored")
    return numerator - denominator


def truth_scores(bundle, ledger, evidence):
    outcomes = {e["emission_index"]: e for e in evidence}
    if set(outcomes) != {f["emission_index"] for f in ledger}:
        raise ValueError("truth-score population mismatch")
    scores = []
    for feature in ledger:
        outcome = outcomes[feature["emission_index"]]
        if outcome["issue_time"] != feature["issue_time"]:
            raise ValueError("truth issue mismatch")
        row = {"emission_index": feature["emission_index"], "issue_time": feature["issue_time"],
               "kind": outcome["kind"], "reason": outcome["reason"]}
        for name in MODELS:
            route = bundle.route(feature, name)
            model = bundle.r0 if route == "R0" else bundle.models[route]
            endpoint = feature["issue_time"] if route == "R0" else feature["end_t"]
            mu = model.intercept
            if route in ("M2", "M3", "P3"):
                covariates = _m2_covariates(feature, bundle._base_transform(), bundle.local_level)
                mu += sum(model.coefficients[key] * value for key, value in covariates.items())
            if route in ("M3", "P3"):
                value = feature["previous_duration"] if route == "P3" else endpoint - feature["onset_t"]
                mu += model.coefficients["beta"] * (math.log(value) - model.centers["mark"]) / model.scales["mark"]
            row[name] = point_loglik(outcome, endpoint, mu, model.sigma)
            row[name + "_route"] = route
        row["gain_M3_M2"] = row["M3"] - row["M2"]
        row["gain_P3_M2"] = row["P3"] - row["M2"]
        row["gain_M3_P3"] = row["M3"] - row["P3"]
        if not all(math.isfinite(row[name]) for name in MODELS):
            raise ValueError("nonfinite truth score")
        scores.append(row)
    return scores


def fit_oracle(ledger, evidence, cutoff):
    """Refit the composite oracle on exact point/censor training evidence."""
    outcomes = {e["emission_index"]: e for e in evidence}
    if set(outcomes) != {f["emission_index"] for f in ledger}:
        raise ValueError("oracle population mismatch")
    if any(f["issue_time"] >= cutoff or outcomes[f["emission_index"]]["evidence_available_at"] > cutoff for f in ledger):
        raise ValueError("oracle training leakage")
    rows = [{"feature": f, "evidence": outcomes[f["emission_index"]]} for f in ledger]
    q_rows = [r for r in rows if _previous_value(r["feature"]) is not None]
    if len(q_rows) < 4:
        raise ValueError("too few oracle timing-available rows")
    transform, fixed = _m2_transform(q_rows, True)

    def fit_base(name, group, terms):
        design = np.array([[1.0] + [_m2_covariates(r["feature"], transform, True)[key] for key in terms]
                           for r in group])
        endpoints = np.array([r["feature"]["end_t"] for r in group])
        ages = np.array([r["feature"]["issue_time"] for r in group]) - endpoints
        points = np.array([r["evidence"]["kind"] == "point" for r in group])
        waits = np.array([(r["evidence"]["onset_t"] if r["evidence"]["kind"] == "point"
                           else r["evidence"]["censor_at"]) - r["feature"]["end_t"] for r in group])

        def objective(theta):
            mu, sigma = design @ theta[:-1], math.exp(theta[-1])
            logs = np.log(np.maximum(waits, 1e-300))
            log_density = -logs - math.log(sigma) - 0.5 * math.log(2 * math.pi) - 0.5 * ((logs - mu) / sigma) ** 2
            log_survival = np.where(waits > 0, log_ndtr(-(logs - mu) / sigma), 0.0)
            log_den = np.where(ages > 0, log_ndtr(-(np.log(np.maximum(ages, 1e-300)) - mu) / sigma), 0.0)
            return -float(np.sum(np.where(points, log_density, log_survival) - log_den))

        bounds = [_BOUNDS[0]] + [(0.0, 0.0) if key in fixed else _BOUNDS[1] for key in terms] + [_BOUNDS[3]]
        logs = np.log(waits[waits > 0])
        starts = [np.array([float(np.mean(logs)), *([0.0] * len(terms)), math.log(scale)]) for scale in (0.4, 0.8)]
        attempts = [minimize(objective, initial, method="L-BFGS-B", bounds=bounds) for initial in starts]
        good = [r for r in attempts if r.success and np.all(np.isfinite(r.x)) and math.isfinite(r.fun)
                and all(math.isfinite(float(value)) for i, value in enumerate(r.jac)
                        if not (1 <= i <= len(terms) and terms[i - 1] in fixed))]
        if not good:
            raise ValueError("oracle base optimization failed: " + "; ".join(str(r.message) for r in attempts))
        best = min(good, key=lambda r: r.fun)
        if best.x[-1] <= _BOUNDS[3][0] + 1e-7:
            raise ValueError("oracle residual scale degenerate")
        model = ForecastModel(name, float(best.x[0]), {key: float(best.x[i + 1]) for i, key in enumerate(terms)},
                              math.exp(best.x[-1]),
                              {"previous_gap": transform["previous_center"], "earlier_level": transform["earlier_center"]},
                              {"previous_gap": transform["previous_scale"], "earlier_level": transform["earlier_scale"]},
                              len(group), tuple(terms),
                              {"fit_kind": "exact_truth_point_censor", "objective": float(best.fun),
                               "convergence": str(best.message), "fixed_terms": [key for key in terms if key in fixed]})
        return model

    m0, m2 = fit_base("M0", rows, ()), fit_base("M2", q_rows, ("previous_gap", "earlier_level"))

    def offset(name, kind):
        group = [r for r in q_rows if r["feature"].get(kind) is not None and r["feature"][kind] > 0]
        center, scale, constant = _standard([math.log(r["feature"][kind]) for r in group])

        def objective(beta):
            total = 0.0
            for r in group:
                f = r["feature"]
                covariates = _m2_covariates(f, transform, True)
                mu = m2.intercept + sum(m2.coefficients[key] * value for key, value in covariates.items())
                mu += beta * (math.log(f[kind]) - center) / scale
                total -= point_loglik(r["evidence"], f["end_t"], mu, m2.sigma)
            return total

        beta = 0.0
        if group and not constant:
            result = minimize_scalar(objective, method="bounded", bounds=(0.0, 5.0), options={"xatol": 1e-10})
            if not result.success or not math.isfinite(result.fun):
                raise ValueError("oracle offset optimization failed")
            candidates = [(0.0, objective(0.0)), (5.0, objective(5.0)), (float(result.x), float(result.fun))]
            beta = min(candidates, key=lambda pair: pair[1])[0]
        return ForecastModel(name, m2.intercept, {**m2.coefficients, "beta": beta}, m2.sigma,
                              {**m2.centers, "mark": center}, {**m2.scales, "mark": scale},
                              len(group), m2.terms + ("beta",),
                              {"fit_kind": "exact_truth_fixed_m2_offset", "mark_kind": kind,
                               "objective": objective(beta), "zero_candidate": objective(0.0)})

    return DirectionalBundle({"M0": m0, "M2": m2, "M3": offset("M3", "duration"),
                              "P3": offset("P3", "previous_duration")}, m0, "point", 5,
                             "log_duration", True, True, False, {"training": len(rows)},
                             {"training_cutoff": cutoff, "frozen": True,
                              "scope": "composite true-end/duration/gap/history oracle on fixed anchors"})


def scored_summary(scores, origin):
    usable = [r for r in scores if r.get("gain_M3_M2") is not None]
    result = {"n": len(usable), "excluded": len(scores) - len(usable),
              "routes": {name: dict(Counter(r.get(name + "_route") for r in usable)) for name in MODELS}}
    if usable:
        for field in ("gain_M3_M2", "gain_P3_M2", "gain_M3_P3"):
            result[field] = {"mean": statistics.fmean(r[field] for r in usable)}
            if len({math.floor((r["issue_time"] - origin) / (6 * 365.25)) for r in usable}) > 1:
                result[field]["six_year_cluster"] = cluster_interval(usable, field, origin, 6)
    return result


def audit_retained_ledger(regenerated, retained):
    """Audit exact retained features, allowing one adjacent float only in log gaps."""
    if len(regenerated) != len(retained):
        raise ValueError("regenerated sigma0 ledger row count differs from retained A10d")
    accepted = []
    for position, (actual, expected) in enumerate(zip(regenerated, retained)):
        if set(actual) != set(expected):
            raise ValueError(f"retained ledger keys differ at row {position}")
        if ({key: value for key, value in actual.items() if key != "earlier_gaps"}
                != {key: value for key, value in expected.items() if key != "earlier_gaps"}
                or any(type(actual[key]) is not type(expected[key]) for key in actual if key != "earlier_gaps")):
            raise ValueError(f"retained ledger non-log-gap feature differs at row {position}")
        actual_gaps, expected_gaps = actual.get("earlier_gaps"), expected.get("earlier_gaps")
        if (not isinstance(actual_gaps, list) or not isinstance(expected_gaps, list)
                or len(actual_gaps) != len(expected_gaps)):
            raise ValueError(f"retained earlier_gaps shape differs at row {position}")
        for gap_position, (value, reference) in enumerate(zip(actual_gaps, expected_gaps)):
            if (type(value) is not float or type(reference) is not float
                    or not math.isfinite(value) or not math.isfinite(reference)):
                raise ValueError(f"retained earlier_gaps has invalid value at row {position}")
            if value == reference:
                continue
            if math.nextafter(reference, value) != value:
                raise ValueError(f"retained earlier_gaps differs by more than one ULP at row {position}")
            accepted.append({"emission_index": actual["emission_index"], "history_position": gap_position,
                             "retained": reference, "regenerated": value,
                             "retained_hex": reference.hex(), "regenerated_hex": value.hex(),
                             "signed_difference": value - reference, "adjacent_float_steps": 1})
    return accepted


def prepare_trial(case, replicate, base=BASE, inputs_path=INPUT):
    started = time.monotonic()
    inputs, config = json.loads(Path(inputs_path).read_text()), json.loads(CONFIG.read_text())["v2-phase"]
    rows, truth, meta = regenerate(inputs, config, case, replicate, base)
    ledger = forecast_ledger(rows, stop=meta["stop"])
    contexts = prepare_contexts(rows, ledger)
    for context in contexts:
        zero, _ = jitter_feature(context, 0.0, case, replicate)
        if any(zero.get(key) != value for key, value in context["feature"].items()):
            differing = [key for key, value in context["feature"].items() if zero.get(key) != value]
            raise ValueError(f"sigma0 feature identity failed: {differing}")
    anchors, counts, classifications = fixed_anchors(ledger, truth, meta)
    retained_path = RETAINED / f"v2-phase-{case}-{replicate:03d}.json"
    reproduction = {"retained_trial": None, "stream_metadata_matches": None, "retained_model_score_checked": False}
    if base == BASE and retained_path.exists():
        old = json.loads(retained_path.read_text())["result"]
        if old["stream_metadata"]["blocks"] != meta["blocks"]:
            raise ValueError("regenerated block metadata differs from retained A10d")
        reproduction.update(retained_trial=str(retained_path.relative_to(ROOT)), stream_metadata_matches=True)
        if replicate == 0:
            trace = old["audit_trace"]["ledger"]["0.0"]
            accepted = audit_retained_ledger(ledger, trace["training"] + trace["evaluation"])
            reproduction["ledger_matches_exactly"] = not accepted
            reproduction["ledger_audit_one_ulp_log_gaps"] = accepted
            reproduction["ledger_audit_passed"] = True
    return {"rows": rows, "truth": truth, "meta": meta, "ledger": ledger, "contexts": contexts,
            "anchors": anchors, "classifications": classifications, "anchor_counts": counts,
            "reproduction": reproduction, "preparation_seconds": time.monotonic() - started,
            "rows_sha256": digest(rows), "truth_sha256": digest(truth), "ledger_sha256": digest(ledger)}


def evaluate_trial(prepared, case, replicate, output, dose_base=DOSE_BASE):
    rows, truth, meta, ledger = (prepared[key] for key in ("rows", "truth", "meta", "ledger"))
    cutoff, stop = meta["training_cutoff"], meta["stop"]
    training = [f for f in ledger if f["issue_time"] < cutoff]
    testing = [f for f in ledger if f["issue_time"] >= cutoff]
    train_legacy = outcome_evidence(rows, training, stop=cutoff)
    full_legacy = {e["emission_index"]: e for e in outcome_evidence(rows, ledger, stop=stop)}
    test_legacy = [full_legacy[f["emission_index"]] for f in testing]
    legacy_bundle = fit_directional(training, train_legacy, cutoff)
    legacy_scores = legacy_bundle.scores(testing, test_legacy)
    train_extracted = outcome_evidence_v4(rows, training, stop=cutoff)
    full_extracted = {e["emission_index"]: e for e in outcome_evidence_v4(rows, ledger, stop=stop)}
    test_extracted = [full_extracted[f["emission_index"]] for f in testing]
    anchors = prepared["anchors"]
    train_truth = truth_evidence(training, truth, anchors,
                                 administrative_cutoffs(rows, training, meta, cutoff), cutoff)
    test_truth = truth_evidence(testing, truth, anchors,
                                administrative_cutoffs(rows, ledger, meta, stop), stop)
    oracle = oracle_features(ledger, truth, anchors, prepared["contexts"])
    oracle_train = [f for f in oracle if f["issue_time"] < cutoff]
    oracle_test = [f for f in oracle if f["issue_time"] >= cutoff]
    oracle_bundle = fit_oracle(oracle_train, train_truth, cutoff)
    oracle_scores = truth_scores(oracle_bundle, oracle_test, test_truth)
    record = {key: prepared[key] for key in ("meta", "anchor_counts", "classifications", "reproduction",
                                            "preparation_seconds", "rows_sha256", "truth_sha256", "ledger_sha256")}
    record.update(case=case, replicate=replicate, sigmas={},
                  oracle={"model": oracle_bundle.to_dict(), "summary": scored_summary(oracle_scores, cutoff)},
                  legacy_sigma0={"model": legacy_bundle.to_dict(), "summary": scored_summary(legacy_scores, cutoff)},
                  v4_backoff_counts={"training": sum(bool(e["censor_backoff"]) for e in train_extracted),
                                     "evaluation": sum(bool(e["censor_backoff"]) for e in test_extracted)})
    score_rows = ([{"route": "composite_oracle_truth", "sigma": 0.0, **r} for r in oracle_scores]
                  + [{"route": "legacy_v3_extracted", "sigma": 0.0, **r} for r in legacy_scores])
    write(output / f"{case}-{replicate:03d}-evidence.json", {
        "truth": truth, "training_extracted": train_extracted, "evaluation_extracted": test_extracted,
        "training_legacy_v3": train_legacy, "evaluation_legacy_v3": test_legacy,
        "training_truth": train_truth, "evaluation_truth": test_truth, "oracle_features": oracle})
    feature_handle = (output / f"{case}-{replicate:03d}-features.jsonl").open("w")
    for sigma in SIGMAS:
        features, flags = [], Counter()
        for context in prepared["contexts"]:
            feature, own_flags = jitter_feature(context, sigma, case, replicate, dose_base)
            features.append(feature)
            flags.update(own_flags)
            feature_handle.write(canonical({"sigma": sigma, "invalid_flags": own_flags, "feature": feature}) + "\n")
        train = [f for f in features if f["issue_time"] < cutoff]
        test = [f for f in features if f["issue_time"] >= cutoff]
        bundle = fit_directional(train, train_extracted, cutoff)
        extracted_scores = bundle.scores(test, test_extracted)
        anchor_test = [f for f in test if f["emission_index"] in anchors]
        paired_extracted = [r for r in extracted_scores if r["emission_index"] in anchors]
        paired_truth = truth_scores(bundle, anchor_test, test_truth)
        scored_ids = {r["emission_index"] for r in paired_extracted if r["gain_M3_M2"] is not None}
        paired_subset_truth = [r for r in paired_truth if r["emission_index"] in scored_ids]
        record["sigmas"][str(sigma)] = {"model": bundle.to_dict(), "invalid_feature_counts": dict(flags),
                                       "all_issued_extracted": scored_summary(extracted_scores, cutoff),
                                       "fixed_anchor_extracted": scored_summary(paired_extracted, cutoff),
                                       "fixed_anchor_truth": scored_summary(paired_truth, cutoff),
                                       "extracted_scoreable_anchor_truth": scored_summary(paired_subset_truth, cutoff),
                                       "extracted_unscoreable_anchor_ids": [r["emission_index"] for r in paired_extracted
                                                                           if r["gain_M3_M2"] is None]}
        for route, scores in (("all_issued_extracted", extracted_scores), ("fixed_anchor_truth", paired_truth)):
            score_rows.extend({"route": route, "sigma": sigma, "fixed_anchor": r["emission_index"] in anchors, **r}
                              for r in scores)
        if sigma == 0 and prepared["reproduction"]["retained_trial"]:
            old = json.loads((ROOT / prepared["reproduction"]["retained_trial"]).read_text())["result"]
            record["reproduction"]["retained_primary_mean"] = old["intervals"]["primary"]["6"]["gain_M3_M2"]["estimate"]
            record["reproduction"]["legacy_sigma0_primary_mean"] = record["legacy_sigma0"]["summary"]["gain_M3_M2"]["mean"]
            retained_bundle = DirectionalBundle.from_dict(old["models"]["primary"])
            replayed = retained_bundle.scores(testing, test_legacy)
            replayed_mean = statistics.fmean(r["gain_M3_M2"] for r in replayed if r["gain_M3_M2"] is not None)
            record["reproduction"]["retained_model_replayed_mean"] = replayed_mean
            record["reproduction"]["new_v3_refit_minus_retained_mean"] = (
                record["reproduction"]["legacy_sigma0_primary_mean"] - record["reproduction"]["retained_primary_mean"])
            if abs(replayed_mean - record["reproduction"]["retained_primary_mean"]) > 1e-9:
                raise ValueError("retained model replay fails A10d mean reproduction")
            record["reproduction"]["retained_model_score_checked"] = True
    record["v4_minus_v3_sigma0_gain"] = (record["sigmas"]["0.0"]["all_issued_extracted"]["gain_M3_M2"]["mean"]
                                        - record["legacy_sigma0"]["summary"]["gain_M3_M2"]["mean"])
    feature_handle.close()
    write(output / f"{case}-{replicate:03d}-record.json", record)
    with (output / f"{case}-{replicate:03d}-scores.jsonl").open("w") as handle:
        for row in score_rows:
            handle.write(canonical(row) + "\n")
    return record


def worker(case, replicate, output, prepare_only, smoke, inputs_path):
    started = time.monotonic()
    prepared = prepare_trial(case, replicate, DEV_BASE if smoke else BASE, inputs_path)
    result = {key: prepared[key] for key in ("meta", "anchor_counts", "classifications", "reproduction",
                                            "preparation_seconds", "rows_sha256", "truth_sha256", "ledger_sha256")}
    if not prepare_only:
        result = evaluate_trial(prepared, case, replicate, Path(output),
                                DOSE_BASE + "-smoke" if smoke else DOSE_BASE)
    result.update(case=case, replicate=replicate, elapsed_seconds=time.monotonic() - started,
                  worker_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024))
    write(Path(output) / f"{case}-{replicate:03d}-{'preparation' if prepare_only else 'complete'}.json", result)
    return result


def summarize(records):
    rows = []
    for case in ("null", "structured"):
        group = [r for r in records if r["case"] == case]
        if not group:
            continue
        for route in ("all_issued_extracted", "fixed_anchor_extracted", "fixed_anchor_truth", "extracted_scoreable_anchor_truth"):
            for sigma in SIGMAS:
                values = [r["sigmas"][str(sigma)][route]["gain_M3_M2"]["mean"] for r in group]
                zero = [r["sigmas"]["0.0"][route]["gain_M3_M2"]["mean"] for r in group]
                delta = [a - b for a, b in zip(values, zero)]
                rows.append({"case": case, "route": route, "sigma": sigma, "histories": len(values),
                             "mean_gain": statistics.fmean(values),
                             "mc_se": statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None,
                             "paired_sigma_minus_zero": statistics.fmean(delta),
                             "paired_mc_se": statistics.stdev(delta) / math.sqrt(len(delta)) if len(delta) > 1 else None,
                             "n_mean": statistics.fmean(r["sigmas"][str(sigma)][route]["n"] for r in group)})
        values = [r["oracle"]["summary"]["gain_M3_M2"]["mean"] for r in group]
        rows.append({"case": case, "route": "composite_oracle_truth", "sigma": 0.0, "histories": len(values),
                     "mean_gain": statistics.fmean(values),
                     "mc_se": statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None})
        values = [r["v4_minus_v3_sigma0_gain"] for r in group]
        rows.append({"case": case, "route": "v4_minus_v3_sigma0", "sigma": 0.0, "histories": len(values),
                     "mean_gain": statistics.fmean(values),
                     "mc_se": statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None,
                     "training_backoffs": sum(r["v4_backoff_counts"]["training"] for r in group),
                     "evaluation_backoffs": sum(r["v4_backoff_counts"]["evaluation"] for r in group)})
    return {"scope": "descriptive added iid Gaussian end error under fixed simulator; no real-error calibration or confirmation",
            "rows": rows}


def plot_summary(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    routes = (("all_issued_extracted", "All issued: extracted v4", "o"),
              ("fixed_anchor_extracted", "Fixed anchors: extracted v4", "s"),
              ("extracted_scoreable_anchor_truth", "Same scored anchors: true onset", "^"),
              ("fixed_anchor_truth", "All fixed anchors: true onset", "D"))
    for ax, case in zip(axes, ("null", "structured")):
        for route, label, marker in routes:
            rows = sorted((r for r in summary["rows"] if r["case"] == case and r["route"] == route),
                          key=lambda r: r["sigma"])
            if rows:
                ax.errorbar([r["sigma"] for r in rows], [r["mean_gain"] for r in rows],
                            yerr=[r["mc_se"] or 0.0 for r in rows], marker=marker, capsize=3, label=label)
        ax.axhline(0.01653, color="black", linestyle="--", linewidth=1, label="Original SS Cyg reference")
        ax.axhline(0.0, color="0.7", linewidth=0.8)
        ax.set(title=case, xlabel="Added end-error SD (days)", xticks=SIGMAS)
    axes[0].set_ylabel("History mean M3−M2 gain (nats / issuance)")
    axes[1].legend(fontsize=7, loc="best")
    fig.suptitle("Exploratory fixed-simulator endpoint dose response; bars ±1 MC SE", fontsize=11)
    fig.tight_layout()
    fig.savefig(Path(output) / "dose-response.png", dpi=180)
    fig.savefig(Path(output) / "dose-response.pdf")
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="regenerate and extract only; no fitting or dose scores")
    parser.add_argument("--smoke", action="store_true", help="outside-grid development namespace and replicate999")
    parser.add_argument("--freeze-commit")
    parser.add_argument("--case", choices=("null", "structured"), action="append")
    parser.add_argument("--replicate", type=int, action="append")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--inputs", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 4:
        parser.error("this bounded local diagnostic uses 1–4 workers")
    if args.smoke and args.replicate:
        parser.error("smoke uses only outside-grid replicate 999")
    if not args.prepare:
        if not args.freeze_commit or not PROTOCOL.exists():
            parser.error("scoring requires the committed amended protocol and --freeze-commit")
        for path in (str(PROTOCOL.relative_to(ROOT)), "scripts/r1_endpoint_dose.py", "tests/test_r1_endpoint_dose.py",
                     "src/dnmem/outcome_evidence_v4.py", "tests/test_r1_censor_audit.py"):
            committed = subprocess.check_output(["git", "show", f"{args.freeze_commit}:{path}"], cwd=ROOT)
            if hashlib.sha256(committed).hexdigest() != sha(ROOT / path):
                parser.error(f"{path} differs from declared freeze")
    tasks = [(case, replicate) for case in args.case or ("null", "structured")
             for replicate in ([999] if args.smoke else args.replicate or range(40))]
    if any(not 0 <= replicate < 40 for _, replicate in tasks) and not args.smoke:
        parser.error("production replicate must be 0..39")
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = {"status": "running", "prepare_only": args.prepare, "smoke": args.smoke,
               "seed_base": DEV_BASE if args.smoke else BASE, "dose_seed_base": DOSE_BASE,
               "tasks": tasks, "workers": args.workers,
               "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "freeze_commit": args.freeze_commit, "script_sha256": sha(__file__),
               "source_sha256": {path: sha(ROOT / path) for path in SOURCE_PATHS},
               "input_sha256": sha(args.inputs), "config_sha256": sha(CONFIG),
               "protocol_sha256": sha(PROTOCOL) if PROTOCOL.exists() else None,
               "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()}}
    write(args.output / "receipt.json", receipt)
    started, records, failures = time.monotonic(), [], []
    with ProcessPoolExecutor(args.workers) as pool:
        futures = {pool.submit(worker, case, replicate, str(args.output), args.prepare, args.smoke,
                               str(args.inputs)): (case, replicate) for case, replicate in tasks}
        for future in as_completed(futures):
            task = futures[future]
            try:
                records.append(future.result())
                print(f"completed {task[0]}/{task[1]}", flush=True)
            except Exception as exc:
                failures.append({"task": task, "error_type": type(exc).__name__, "error": str(exc)})
                print(f"failed {task[0]}/{task[1]}: {type(exc).__name__}: {exc}", flush=True)
    records.sort(key=lambda r: (r["case"], r["replicate"]))
    if not args.prepare and records:
        summary = summarize(records)
        write(args.output / "summary.json", summary)
        plot_summary(summary, args.output)
    if receipt["source_sha256"] != {path: sha(ROOT / path) for path in SOURCE_PATHS}:
        failures.append({"error": "source changed during run"})
    if receipt["input_sha256"] != sha(args.inputs) or receipt["config_sha256"] != sha(CONFIG):
        failures.append({"error": "input or configuration changed during run"})
    receipt.update(status="completed_with_failures" if failures else "completed", successful=len(records),
                   failures=failures, elapsed_seconds=time.monotonic() - started,
                   files_sha256={p.name: sha(p) for p in sorted(args.output.iterdir()) if p.name != "receipt.json"})
    write(args.output / "receipt.json", receipt)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
