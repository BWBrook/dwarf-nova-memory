"""Independent post-result verification of A10j claims C20--C23.

Reads only retained development/1960--2017 ledgers and aggregate evidence.
No candidate likelihood, fitting, or A10j analysis code is imported. A fresh
vector lognormal interval/survival likelihood and Powell fits supply the route.
This is verification of exploratory calculations, never another confirmation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.special import log_ndtr, stdtrit

ROOT = Path(__file__).resolve().parents[1]
START, SPLIT, STOP = 2436934.5, 2448988.5, 2458119.5
ERAS = {"1960-2017": (START, STOP), "1960-1992": (START, SPLIT),
        "1993-2017": (SPLIT, STOP)}
PARAMETER_SHA256 = "ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def lognormal_scores(mu, sigma, age, lo, hi, censor, interval):
    mu = np.asarray(mu, dtype=float)
    with np.errstate(divide="ignore"):
        za = (np.log(age) - mu) / sigma
    result = -log_ndtr(-za)
    mask = np.asarray(interval, dtype=bool)
    with np.errstate(divide="ignore"):
        zl = (np.log(lo[mask]) - mu[mask]) / sigma
        zh = (np.log(hi[mask]) - mu[mask]) / sigma
    upper = np.where(zl >= 0.0, log_ndtr(-zl), log_ndtr(zh))
    lower = np.where(zl >= 0.0, log_ndtr(-zh), log_ndtr(zl))
    result[mask] += upper + np.log(-np.expm1(lower - upper))
    with np.errstate(divide="ignore"):
        zc = (np.log(censor[~mask]) - mu[~mask]) / sigma
    result[~mask] += log_ndtr(-zc)
    if not np.all(np.isfinite(result)):
        raise ValueError("independent likelihood produced nonfinite scores")
    return result


@dataclass
class Population:
    rows: list
    timing_ids: list
    positions: np.ndarray
    times: np.ndarray
    mu: np.ndarray
    x: np.ndarray
    long: np.ndarray
    within: np.ndarray
    age: np.ndarray
    lo: np.ndarray
    hi: np.ndarray
    censor: np.ndarray
    interval: np.ndarray
    sigma: float
    beta: float
    beta_type: float
    beta_within: float

    @classmethod
    def load(cls, folder, minimum, maximum):
        params = read(folder / "frozen_parameters.json")
        if digest(folder / "frozen_parameters.json") != PARAMETER_SHA256:
            raise ValueError("the retained forecast parameters are not the frozen bytes")
        primary, categorical = params["primary"], params["type_within"]
        assert primary["endpoint_mode"] == categorical["endpoint_mode"] == "point"
        base = primary["models"]["M2"]
        assert base == categorical["models"]["M2"]
        assert base["sigma"] == primary["models"]["M3"]["sigma"] == categorical["models"]["M3"]["sigma"]
        ledger = {r["emission_index"]: r for r in read(folder / "ledger-0.0.json")}
        evidence = {r["emission_index"]: r for r in read(folder / "evidence-0.0.json")}
        rows = read(folder / "primary-scores.json")
        timing, positions = [], []
        for position, row in enumerate(rows):
            if not minimum <= row["issue_time"] < maximum <= STOP:
                raise ValueError("input is outside the already-opened period")
            if row["M3_route"] == "M3":
                timing.append(row["emission_index"])
                positions.append(position)
            else:
                assert row["gain_M3_M2"] == 0.0
        arrays = {k: [] for k in ("mu", "x", "long", "within", "age", "lo", "hi", "censor", "interval")}
        mark = primary["models"]["M3"]
        typ = categorical["models"]["M3"]
        for identifier in timing:
            f, e = ledger[identifier], evidence[identifier]
            assert f["previous_gap_covered"] is True and f["previous_gap"] > 0
            end = f["end_t"]
            duration = end - f["onset_t"]
            assert duration > 0 and end <= f["issue_time"]
            q = (math.log(f["previous_gap"]) - base["centers"]["previous_gap"]) / base["scales"]["previous_gap"]
            logs = f["earlier_gaps"]
            level = float(np.mean(logs)) if logs else base["centers"]["earlier_level"]
            level = (level - base["centers"]["earlier_level"]) / base["scales"]["earlier_level"]
            mu = base["intercept"] + base["coefficients"]["previous_gap"] * q + base["coefficients"]["earlier_level"] * level
            category = int(duration >= 12.0)
            is_interval = e["kind"] == "interval"
            if e["kind"] not in ("interval", "right_censored"):
                raise ValueError("unexpected scored evidence kind")
            assert e["computed_as_of"] <= STOP
            lower = max(e["onset_lo"], f["issue_time"]) - end if is_interval else 1.0
            upper = e["onset_hi"] - end if is_interval else 2.0
            if is_interval:
                assert lower >= 0 and upper > lower and e["onset_hi"] < STOP
            values = dict(mu=mu,
                          x=(math.log(duration) - mark["centers"]["mark"]) / mark["scales"]["mark"],
                          long=float(category),
                          within=(math.log(duration) - typ["centers"]["mark_type"][str(category)]) / typ["scales"]["mark_within"],
                          age=f["issue_time"] - end, lo=lower, hi=upper,
                          censor=e["censor_at"] - end if not is_interval else 1.0,
                          interval=is_interval)
            for key, value in values.items():
                arrays[key].append(value)
        return cls(rows, timing, np.asarray(positions, dtype=int),
                   np.asarray([r["issue_time"] for r in rows]),
                   **{k: np.asarray(v) for k, v in arrays.items()}, sigma=base["sigma"],
                   beta=mark["coefficients"]["beta"], beta_type=typ["coefficients"]["beta_type"],
                   beta_within=typ["coefficients"]["beta_within"])

    def score(self, offset=0.0, subset=None):
        take = np.ones(len(self.mu), dtype=bool) if subset is None else subset
        offset = np.broadcast_to(offset, self.mu.shape)
        return lognormal_scores(self.mu[take] + offset[take], self.sigma, self.age[take],
                                self.lo[take], self.hi[take], self.censor[take], self.interval[take])

    def padded(self, timing_values):
        values = np.zeros(len(self.rows), dtype=float)
        values[self.positions] = timing_values
        return values


def cluster(values, times, origin):
    n = len(values)
    center = float(np.mean(values))
    block_ids = np.floor((times - origin) / (6.0 * 365.25)).astype(int)
    ids = np.unique(block_ids)
    sums = np.asarray([np.sum(values[block_ids == key] - center) for key in ids])
    g = len(ids)
    se = math.sqrt(float(np.dot(sums, sums)) * g / (g - 1)) / n
    half = float(stdtrit(g - 1, .95)) * se
    return dict(n=n, estimate=center, se=se, blocks=g, lower_90=center-half, upper_90=center+half)


def contrasts(pop, timing_values):
    values = pop.padded(timing_values)
    return {name: cluster(values[(pop.times >= lo) & (pop.times < hi)],
                          pop.times[(pop.times >= lo) & (pop.times < hi)], lo)
            for name, (lo, hi) in ERAS.items()}


def fit(pop, design, subset):
    d = np.asarray(design)
    records, candidates = [], []
    for start in (np.zeros(d.shape[1]), np.full(d.shape[1], .1), np.full(d.shape[1], -.1)):
        objective = lambda v: -float(np.sum(pop.score(d @ v, subset)))
        result = minimize(objective, start, method="Powell", bounds=[(-1.0, 1.0)]*d.shape[1],
                          options={"xtol": 1e-10, "ftol": 1e-12, "maxiter": 2000})
        record = dict(start=start.tolist(), success=bool(result.success), solution=result.x.tolist(),
                      nll=float(result.fun), evaluations=int(result.nfev), message=str(result.message))
        records.append(record)
        if result.success and np.all(np.isfinite(result.x)) and np.isfinite(result.fun):
            candidates.append((float(result.fun), result.x))
    if len(candidates) != 3:
        raise ValueError(f"independent Powell fit did not complete all starts: {records}")
    objective, beta = min(candidates, key=lambda item: item[0])
    if any(abs(v) > .999 for v in beta):
        raise ValueError("audit fit touches a working bound")
    return dict(parameters=[float(v) for v in beta], nll=objective,
                start_objective_spread=max(v[0] for v in candidates)-min(v[0] for v in candidates),
                optimization=records)


def refits(pop, eras):
    columns = dict(level=np.ones((len(pop.mu), 1)),
                   raw=np.column_stack((np.ones(len(pop.mu)), pop.x)),
                   type=np.column_stack((np.ones(len(pop.mu)), pop.long)),
                   type_within=np.column_stack((np.ones(len(pop.mu)), pop.long, pop.within)))
    results = {}
    timing_times = pop.times[pop.positions]
    for label, (lo, hi) in eras.items():
        subset = (timing_times >= lo) & (timing_times < hi)
        models = {name: fit(pop, design, subset) for name, design in columns.items()}
        null = models["level"]["nll"]
        models["raw"]["lr_vs_level"] = 2*(null-models["raw"]["nll"])
        models["type"]["lr_vs_level"] = 2*(null-models["type"]["nll"])
        models["type_within"]["lr_vs_level"] = 2*(null-models["type_within"]["nll"])
        models["type_within"]["lr_within_given_type"] = 2*(models["type"]["nll"]-models["type_within"]["nll"])
        models["timing_rows"] = int(np.sum(subset))
        results[label] = models
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT/"outputs/a10h_live_repair_5e39aeb")
    parser.add_argument("--development", type=Path, default=ROOT/"outputs/a10e_development_b80c4a9")
    parser.add_argument("--output", type=Path, default=ROOT/"outputs/a10k_exploratory_audit/summary.json")
    args = parser.parse_args()
    reference_path = ROOT/"data/provenance/a10j_postresult_review/summary.json"
    reference = read(reference_path)
    for folder in (args.run, args.development):
        for name in ("frozen_parameters.json", "ledger-0.0.json", "evidence-0.0.json", "primary-scores.json", "type_within-scores.json"):
            key = name if folder == args.run else ("development_ledger" if name == "ledger-0.0.json" else "development_" + name)
            if digest(folder/name) != reference["input_sha256"][key]:
                raise ValueError("retained input drift from the A10j evidence: " + key)
    pop = Population.load(args.run, START, STOP)
    dev = Population.load(args.development, -math.inf, START)
    zero, frozen = pop.score(), pop.score(pop.beta*pop.x)
    frozen_type = pop.score(pop.beta_type*pop.long + pop.beta_within*pop.within)
    timing_by_id = {row["emission_index"]: row for row in pop.rows if row["M3_route"] == "M3"}
    type_by_id = {row["emission_index"]: row for row in read(args.run/"type_within-scores.json")}
    errors = []
    for k, identifier in enumerate(pop.timing_ids):
        errors.extend((abs(zero[k]-timing_by_id[identifier]["M2"]),
                       abs(frozen[k]-timing_by_id[identifier]["M3"]),
                       abs(frozen_type[k]-type_by_id[identifier]["M3"])))
    assert max(errors) < 1e-9
    mean_mark = float(np.mean(pop.x)); mark_level = pop.beta*mean_mark
    shifted = pop.score(mark_level)
    centered = pop.score(pop.beta*(pop.x-mean_mark))
    fit_results = refits(pop, ERAS)
    dev_results = refits(dev, {"1910-1959": (-math.inf, START)})
    best = fit_results["1960-2017"]["level"]["parameters"][0]
    base_corrected = pop.score(best)
    raw_corrected = pop.score(best+pop.beta*pop.x)
    type_corrected = pop.score(best+pop.beta_type*pop.long+pop.beta_within*pop.within)
    level_results = dict(mean_standardized_log_duration=mean_mark, mark_level_shift=mark_level,
                         best_M2_level_shift=best, mean_unchanged_type_offset=float(np.mean(pop.beta_type*pop.long+pop.beta_within*pop.within)),
                         primary=contrasts(pop, frozen-zero), level_first=contrasts(pop, shifted-zero),
                         remaining_after_level=contrasts(pop, frozen-shifted),
                         recentered_mark=contrasts(pop, centered-zero),
                         level_after_centered=contrasts(pop, frozen-centered),
                         same_best_level_raw=contrasts(pop, raw_corrected-base_corrected),
                         same_best_level_type=contrasts(pop, type_corrected-base_corrected),
                         reduction_relative_to_original_clock_scale=1-math.exp(best),
                         original_scale_excess_relative_to_corrected_scale=math.exp(-best)-1)
    expected = reference["level_decomposition"]
    comparisons = {"xbar": abs(mean_mark-expected["evaluation_mean_standardized_log_duration"]),
                   "mark_level": abs(mark_level-expected["level_shift_implied_by_frozen_mark"]),
                   "best_level": abs(best-expected["frozen_M2_best_evaluation_level_shift"])}
    for actual, old in (("primary", "gain_frozen_M3_minus_M2"),
                        ("level_first", "level_part_M2_shifted_by_mark_level_minus_M2"),
                        ("recentered_mark", "slope_part_M3_recentred_minus_M2"),
                        ("remaining_after_level", "slope_part_M3_minus_M2_shifted_by_mark_level"),
                        ("same_best_level_raw", "M3_minus_M2_both_at_best_M2_level")):
        comparisons[actual] = max(abs(level_results[actual][era][name]-expected[old][era][name])
                                  for era in ERAS for name in ("estimate", "se", "lower_90", "upper_90"))
    comparisons["same_best_level_type"] = max(abs(level_results["same_best_level_type"][era][name]-reference["type_information"]["frozen_type_rule_gain_both_at_best_M2_level"][era][name])
                                             for era in ERAS for name in ("estimate", "se", "lower_90", "upper_90"))
    fits_comparison = {}
    for era, models in fit_results.items():
        old = reference["type_information"]["refits_frozen_M2_nuisance_free_level"][era]
        fits_comparison[era] = dict(type_contrast_difference=models["type"]["parameters"][1]-old["type_only"]["beta_type_long_minus_short"],
                                    type_lr_difference=models["type"]["lr_vs_level"]-old["type_only"]["lr_vs_level_only"],
                                    raw_lr_difference=models["raw"]["lr_vs_level"]-old["raw_log_duration"]["lr_vs_level_only"],
                                    within_lr_difference=models["type_within"]["lr_within_given_type"]-old["type_plus_within"]["lr_within_given_type"],
                                    clock_scale_ratio=math.exp(models["type"]["parameters"][1]),
                                    illustrative_scale_difference_at_36_days=36*math.expm1(models["type"]["parameters"][1]))
    old_dev = reference["type_information"]["development_refits_in_sample"]["1910-1959"]
    fresh_dev = dev_results["1910-1959"]
    dev_comparison = dict(type_contrast_difference=fresh_dev["type"]["parameters"][1]-old_dev["type_only"]["beta_type_long_minus_short"],
                          type_lr_difference=fresh_dev["type"]["lr_vs_level"]-old_dev["type_only"]["lr_vs_level_only"],
                          raw_lr_difference=fresh_dev["raw"]["lr_vs_level"]-old_dev["raw_log_duration"]["lr_vs_level_only"],
                          within_lr_difference=fresh_dev["type_within"]["lr_within_given_type"]-old_dev["type_plus_within"]["lr_within_given_type"],
                          clock_scale_ratio=math.exp(fresh_dev["type"]["parameters"][1]))
    assert max(abs(value) for key,value in dev_comparison.items() if key.endswith("difference")) < 1e-5
    assert max(comparisons.values()) < 2e-6
    assert max(abs(value) for values in fits_comparison.values() for key,value in values.items() if key.endswith("difference")) < 1e-5
    short = pop.long == 0
    total_offsets = pop.beta_type*pop.long+pop.beta_within*pop.within
    total = level_results["primary"]["1960-2017"]["estimate"]
    level = level_results["level_first"]["1960-2017"]["estimate"]
    centered_gain = level_results["recentered_mark"]["1960-2017"]["estimate"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    at_head = subprocess.run(["git", "show", "HEAD:scripts/a10k_exploratory_audit.py"], cwd=ROOT,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    script_commit = head if at_head.returncode == 0 and hashlib.sha256(at_head.stdout).hexdigest() == digest(__file__) else None
    output = dict(scope="Independent verification of exploratory C20--C23 only; no new confirmation or 2018+ access",
                  provenance=dict(base_checkout_commit=head, source_commit_with_matching_script=script_commit,
                                  script_sha256=digest(__file__), python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                  inputs={str(path.relative_to(ROOT)):digest(path) for path in [reference_path,*[folder/name for folder in (args.run,args.development) for name in ("frozen_parameters.json","ledger-0.0.json","evidence-0.0.json","primary-scores.json","type_within-scores.json")]]}),
                  independence="No dnmem module, check_a10d_scores, or a10j_postresult_review imported; fresh vector log-CDF/survival likelihood, direct covariates, Powell multistart fits, independent CR1 assembly.",
                  max_abs_frozen_score_error=max(errors), level=level_results, refits=fit_results, development_refits=dev_results,
                  numeric_comparison_to_A10j=dict(level_max_absolute_differences=comparisons,refit_differences=fits_comparison, development_refit_differences=dev_comparison),
                  limitations=dict(level_fraction_in_first_ordering=level/total,
                                   decomposition_interaction=total-level-centered_gain,
                                   decomposition_is_not_temporal_drift_removal=True,
                                   type_lr_comparison_is_nonnested_in_sample=True,
                                   estimated_level_and_refits_reuse_evaluation_outcomes=True,
                                   intervals_ignore_estimated_level_and_center_uncertainty=True,
                                   type_contrast_is_untruncated_working_clock_location_ratio=True,
                                   whole_type_within_rule_can_shorten_short_forecasts=bool(np.any(total_offsets[short] < 0)),
                                   short_forecasts_with_negative_whole_offset=int(np.sum(total_offsets[short] < 0)),
                                   short_forecast_total=int(np.sum(short)),
                                   no_within_type_equivalence_or_absence_test=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(dict(status="verified",max_abs_frozen_score_error=max(errors),max_level_difference=max(comparisons.values()),output=str(args.output))))


if __name__ == "__main__":
    main()
