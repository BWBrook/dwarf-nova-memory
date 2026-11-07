#!/usr/bin/env python3
"""Aggregate A04c screening metrics with replicate-level Monte Carlo intervals."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from itertools import product
from pathlib import Path
from statistics import mean, stdev

KEYS = ("stratum", "phase", "process", "threshold", "extractor", "rule")
RATIOS = {
    "onset_coverage": ("onset_effective_covered", "reference_event_count"),
    "end_coverage": ("end_effective_covered", "reference_event_count"),
    "conditional_onset_coverage": ("onset_effective_covered", "onset_finite_matched_count"),
    "conditional_end_coverage": ("end_effective_covered", "end_finite_matched_count"),
    "short_completeness": ("short_outside_mar_may_complete_count", "short_outside_mar_may_count"),
    "completeness": ("completeness_count", "reference_event_count"),
    "false_per_year": ("false_confirmed_count", "exposure_years"),
    "hidden_passed_fraction": ("hidden_passed", "pairs_passed"),
    "rejected_true_fraction": ("rejected_trueconsecutive", "mapped_trueconsecutive"),
    "type_error": ("type_misclassified_count", "duration_finite_matched_count"),
    "missing_confirmation_fraction": ("confirmation_missing_count", "confirmation_candidate_count"),
    "negative_confirmation_fraction": ("confirmation_negative_lag_count", "confirmation_observed_count"),
}
MEANS = ("oracle_r_all", "recovered_r", "total_bias", "selected_oracle_r", "recovered_matched_r",
         "selection_bias", "boundary_bias", "unmatched_bias",
         "eligible_count", "censored_count", "association_n", "onset_midpoint_bias", "end_midpoint_bias",
         "onset_midpoint_rmse", "end_midpoint_rmse", "onset_mean_width", "end_mean_width",
         "split_truth_count", "split_excess_count", "merged_episode_count", "merged_excess_count",
         "duration_midpoint_bias", "duration_midpoint_rmse", "confirmation_lag_mean",
         "confirmation_lag_median", "confirmation_lag_rmse", "invalid_pair_count")


def number(row, key):
    value = row.get(key)
    return None if value in (None, "", "None") else float(value)


def ratio_interval(rows, numerator, denominator):
    pairs = [(number(r, numerator), number(r, denominator)) for r in rows]
    if any(a is None or b is None for a, b in pairs):
        raise ValueError(f"missing aggregation count: {numerator}/{denominator}")
    exposure = sum(b for _, b in pairs)
    if exposure == 0:
        return {"estimate": None, "lower": None, "upper": None, "mcse": None, "undefined": len(rows)}
    estimate = sum(a for a, _ in pairs) / exposure
    residuals = [a - estimate*b for a, b in pairs]
    se = stdev(residuals) / math.sqrt(len(rows)) / (exposure/len(rows)) if len(rows) > 1 else None
    return {"estimate": estimate, "mcse": se, "lower": estimate - 1.96*se if se is not None else None,
            "upper": estimate + 1.96*se if se is not None else None, "undefined": 0}


def mean_interval(rows, key):
    values = [number(r, key) for r in rows]
    finite = [x for x in values if x is not None]
    if not finite:
        return {"estimate": None, "lower": None, "upper": None, "mcse": None, "undefined": len(rows)}
    estimate = mean(finite)
    se = stdev(finite)/math.sqrt(len(finite)) if len(finite) > 1 else None
    return {"estimate": estimate, "mcse": se, "lower": estimate - 1.96*se if se is not None else None,
            "upper": estimate + 1.96*se if se is not None else None, "undefined": len(rows)-len(finite)}


def gate(metric, bound, direction):
    lo, hi = metric["lower"], metric["upper"]
    if metric["undefined"] or lo is None or hi is None:
        return "INCONCLUSIVE"
    if direction == "above":
        return "PASS" if lo >= bound else "FAIL" if hi < bound else "INCONCLUSIVE"
    if direction == "below":
        return "PASS" if hi < bound else "FAIL" if lo >= bound else "INCONCLUSIVE"
    return "PASS" if lo > -bound and hi < bound else "FAIL" if lo >= bound or hi <= -bound else "INCONCLUSIVE"


def summarize(directory, output):
    receipt = json.loads((directory / "receipt.json").read_text())
    replicate_path = directory / "replicates.csv"
    if hashlib.sha256(replicate_path.read_bytes()).hexdigest() != receipt["replicates_sha256"]:
        raise ValueError("run receipt does not match replicate bytes")
    groups = defaultdict(list)
    with replicate_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            recovered, matched = number(row, "recovered_r"), number(row, "recovered_matched_r")
            row["unmatched_bias"] = None if recovered is None or matched is None else recovered - matched
            groups[tuple(row[k] for k in KEYS)].append(row)
    expected = set(product(("1900_1909", "1910_1929", "1930_1949", "1950_1959"),
                           ("random", "aligned"), ("null", "alternative"), ("9.5", "10.0", "10.5"),
                           ("X1", "X2"), ("C1_4", "C1_7", "C2_095")))
    if set(groups) != expected:
        raise ValueError("simulation grid is missing cells or contains unspecified cells")
    results, flat = [], []
    for key, rows in sorted(groups.items()):
        if len(rows) != receipt["replicates_per_cell"] or {int(r["replicate"]) for r in rows} != set(range(receipt["replicates_per_cell"])):
            raise ValueError("missing or duplicated simulation replicate")
        metrics = {name: ratio_interval(rows, *counts) for name, counts in RATIOS.items()}
        metrics.update({name: mean_interval(rows, name) for name in MEANS})
        criteria = {name: gate(metrics[name], bound, direction) for name, bound, direction in (
            ("onset_coverage", .9, "above"), ("end_coverage", .9, "above"),
            ("short_completeness", .95, "above"), ("false_per_year", .2, "below"),
            ("total_bias", .02, "inside"))}
        errors = sum(bool(r["extraction_error"]) for r in rows)
        verdict = "FAIL" if "FAIL" in criteria.values() or errors else "PASS" if set(criteria.values()) == {"PASS"} else "INCONCLUSIVE"
        eligible_gate = key[1] == "random" and key[2] == "null" and float(key[3]) == 10 and key[0] != "1900_1909"
        result = {**dict(zip(KEYS, key)), "replicates": len(rows), "selection_gate": eligible_gate,
                  "extraction_errors": errors, "criteria": criteria, "verdict": verdict, "metrics": metrics}
        results.append(result)
        row = {**dict(zip(KEYS, key)), "replicates": len(rows), "selection_gate": eligible_gate,
               "extraction_errors": errors, "verdict": verdict, **{k+"_gate": v for k, v in criteria.items()}}
        for name, metric in metrics.items():
            row.update({name+"_"+suffix: value for suffix, value in metric.items()})
        flat.append(row)
    output.mkdir(parents=True, exist_ok=False)
    decisions = []
    for candidate, rule in product(("X1", "X2"), ("C1_4", "C1_7", "C2_095")):
        cells = [r for r in results if r["selection_gate"] and r["extractor"] == candidate and r["rule"] == rule]
        verdicts = {r["verdict"] for r in cells}
        verdict = "FAIL" if "FAIL" in verdicts else "PASS" if verdicts == {"PASS"} else "INCONCLUSIVE"
        decisions.append({"extractor": candidate, "rule": rule, "verdict": verdict,
                          "mean_eligible_pairs_across_three_strata": sum(r["metrics"]["eligible_count"]["estimate"] for r in cells)})
    passing = [d for d in decisions if d["verdict"] == "PASS"]
    chosen = max(passing, key=lambda d: d["mean_eligible_pairs_across_three_strata"]) if passing else None
    (output / "summary.json").write_text(json.dumps({"run_receipt": receipt, "cells": results,
        "candidate_decisions": decisions, "selected": chosen,
        "aggregation_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "ratio-of-counts rates and means of replicate diagnostics; 95% normal Monte Carlo intervals"}, indent=2, allow_nan=False)+"\n")
    with (output / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)
    selected = [r for r in flat if r["selection_gate"]]
    print(json.dumps([{k: r[k] for k in (*KEYS, "verdict", "onset_coverage_estimate", "end_coverage_estimate",
                                        "short_completeness_estimate", "false_per_year_estimate", "total_bias_estimate")}
                      for r in selected], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.directory, args.output)
