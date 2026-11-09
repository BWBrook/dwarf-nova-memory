"""Synthetic paired-score planning; no photometry, archive or fitted R2 baseline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.stats import beta as beta_distribution, norm, t as student_t

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/provenance/r2c_catalogue_power/power-design.json"
NAMESPACE = "r2c-power-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_for(scenario, replicate):
    payload = f"{NAMESPACE}|{scenario}|{replicate}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def capped_star_weights(counts, cap=.4):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 1 or np.any(counts <= 0) or not 0 < cap <= 1 or len(counts) * cap < 1 - 1e-12:
        raise ValueError("invalid or infeasible star-weight cap")
    result = np.zeros(len(counts))
    remaining = np.ones(len(counts), dtype=bool)
    mass = 1.0
    while remaining.any():
        proposed = mass * counts[remaining] / counts[remaining].sum()
        over = proposed > cap
        indices = np.flatnonzero(remaining)
        if not over.any():
            result[indices] = proposed
            break
        fixed = indices[over]
        result[fixed] = cap
        remaining[fixed] = False
        mass = 1.0 - result.sum()
    if not np.isclose(result.sum(), 1) or np.max(result) > cap + 1e-12:
        raise ValueError("star-weight cap failed")
    return result


def event_counts(total, stars, allocation):
    fractions = np.ones(stars) / stars
    if allocation == "imbalanced":
        fractions = np.array([.6] + [.4 / (stars - 1)] * (stars - 1))
    elif allocation != "balanced":
        raise ValueError("unknown allocation")
    exact = total * fractions
    counts = np.floor(exact).astype(int)
    for index in np.argsort(-(exact - counts), kind="stable")[:total - counts.sum()]:
        counts[index] += 1
    if counts.sum() != total or np.any(counts < 6):
        raise ValueError("too few events for the six-block design")
    return counts


def effect_profile(stars, gain, cv):
    if gain < 0 or cv < 0:
        raise ValueError("negative gain or heterogeneity")
    if not cv:
        return np.full(stars, math.sqrt(2 * gain))
    quantiles = norm.ppf((np.arange(stars) + .5) / stars)
    lo, hi = 0.0, 5.0
    for _ in range(70):
        middle = (lo + hi) / 2
        values = np.exp(middle * quantiles)
        if values.std() / values.mean() < cv:
            lo = middle
        else:
            hi = middle
    values = np.exp((lo + hi) / 2 * quantiles)
    return math.sqrt(2 * gain) * values / math.sqrt(np.mean(values ** 2))


def block_process(rng, blocks, serial):
    result = rng.normal(size=blocks)
    for index in range(1, blocks):
        result[index] = serial * result[index - 1] + math.sqrt(1 - serial ** 2) * result[index]
    return result


def observations(rng, count, effect, reliability, mark_icc, residual_icc, serial):
    block = np.arange(count) * 6 // count
    mark_state = block_process(rng, 6, serial)
    residual_state = block_process(rng, 6, serial)
    mark = math.sqrt(mark_icc) * mark_state[block] + math.sqrt(1 - mark_icc) * rng.normal(size=count)
    error = math.sqrt(residual_icc) * residual_state[block] + math.sqrt(1 - residual_icc) * rng.normal(size=count)
    measured = math.sqrt(reliability) * mark + math.sqrt(1 - reliability) * rng.normal(size=count)
    return measured, effect * mark + error, block


def positive_offset(mark, residual):
    denominator = float(np.dot(mark, mark))
    if not denominator > 0:
        raise ValueError("unidentified duration offset")
    return max(0.0, float(np.dot(mark, residual)) / denominator)


def paired_scores(mark, response, baseline, coefficient):
    if coefficient == 0.0:
        return np.zeros_like(mark)
    shift = coefficient * mark
    return shift * (response - baseline) - .5 * shift ** 2


def weighted_cr1(scores, star, block, counts, weights):
    row_weight = weights[star] / counts[star]
    estimate = float(np.dot(row_weight, scores))
    cluster = star * 6 + block
    sums = np.bincount(cluster, weights=row_weight * (scores - estimate), minlength=len(counts) * 6)
    groups = len(sums)
    se = math.sqrt(groups / (groups - 1) * float(np.dot(sums, sums)))
    radius = float(student_t.ppf(.95, groups - 1)) * se
    return {"estimate": estimate, "se": se, "lower90": estimate - radius,
            "upper90": estimate + radius, "clusters": groups}


def trial(scenario, replicate):
    rng = np.random.default_rng(seed_for(scenario["id"], replicate))
    stars = scenario["stars"]
    counts = event_counts(scenario["test_forecasts"], stars, scenario["allocation"])
    weights = capped_star_weights(counts)
    effects = effect_profile(stars, scenario["nominal_oracle_gain"], scenario["effect_cv"])
    own_mark, own_residual, intercepts = [], [], []
    for effect in effects:
        x, y, _ = observations(rng, scenario["development_per_star"], effect, scenario["mark_reliability"],
                               scenario["mark_icc"], scenario["residual_icc"], scenario["serial_block_phi"])
        intercept = float(np.mean(y))
        own_mark.append(x)
        own_residual.append(y - intercept)
        intercepts.append(intercept)
    fitted = positive_offset(np.concatenate(own_mark), np.concatenate(own_residual))
    known = math.sqrt(scenario["mark_reliability"]) * float(np.mean(effects))
    xs, ys, labels, blocks = [], [], [], []
    for index, (count, effect) in enumerate(zip(counts, effects)):
        x, y, block = observations(rng, count, effect, scenario["mark_reliability"],
                                   scenario["mark_icc"], scenario["residual_icc"], scenario["serial_block_phi"])
        xs.append(x); ys.append(y); blocks.append(block); labels.append(np.full(count, index))
    x, y, star, block = map(np.concatenate, (xs, ys, labels, blocks))
    result = {}
    for name, coefficient, baseline in (("known_rule", known, np.zeros_like(x)),
                                         ("fitted_rule", fitted, np.asarray(intercepts)[star])):
        scores = paired_scores(x, y, baseline, coefficient)
        summary = weighted_cr1(scores, star, block, counts, weights)
        expected = float(np.dot(weights, coefficient * math.sqrt(scenario["mark_reliability"]) * effects - .5 * coefficient ** 2))
        summary.update(coefficient=coefficient, conditional_expected_gain=expected,
                       confirmed=summary["lower90"] > 0,
                       contains_conditional_mean=summary["lower90"] <= expected <= summary["upper90"],
                       maximum_star_weight=float(np.max(weights)))
        result[name] = summary
    return result


def exact_binomial(successes, trials):
    return {"successes": successes, "trials": trials, "rate": successes / trials,
            "rate_mc_se": math.sqrt(successes / trials * (1 - successes / trials) / trials),
            "lower95": float(beta_distribution.ppf(.025, successes, trials - successes + 1)) if successes else 0.0,
            "upper95": float(beta_distribution.ppf(.975, successes + 1, trials - successes)) if successes < trials else 1.0}


def run(config, output):
    summary = []
    with (output / "replicates.jsonl").open("w") as handle:
        for scenario in config["scenarios"]:
            results = {"known_rule": [], "fitted_rule": []}
            for replicate in range(config["replicates"]):
                result = trial(scenario, replicate)
                handle.write(json.dumps({"scenario": scenario["id"], "replicate": replicate,
                                         "seed": seed_for(scenario["id"], replicate), "results": result}) + "\n")
                for name, row in result.items():
                    results[name].append(row)
            for name, rows in results.items():
                nonidentity = [r for r in rows if r["coefficient"] > 0]
                summary.append({**scenario, "rule": name,
                                "confirmation": exact_binomial(sum(r["confirmed"] for r in rows), len(rows)),
                                "coverage90": exact_binomial(sum(r["contains_conditional_mean"] for r in rows), len(rows)),
                                "nonidentity_coverage90": exact_binomial(sum(r["contains_conditional_mean"] for r in nonidentity), len(nonidentity)) if nonidentity else None,
                                "nonidentity_histories": len(nonidentity),
                                "mean_observed_gain": statistics.fmean(r["estimate"] for r in rows),
                                "mean_conditional_expected_gain": statistics.fmean(r["conditional_expected_gain"] for r in rows),
                                "median_reported_se": statistics.median(r["se"] for r in rows),
                                "coefficient_zero_fraction": sum(r["coefficient"] == 0 for r in rows) / len(rows),
                                "maximum_star_weight": max(r["maximum_star_weight"] for r in rows),
                                "clusters": rows[0]["clusters"]})
            print("completed " + scenario["id"], flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve previous results; output already exists")
    for path in (Path(__file__), args.config, ROOT / "tests/test_r2c_power.py"):
        relative = path.resolve().relative_to(ROOT)
        committed = subprocess.check_output(["git", "show", f"{args.freeze_commit}:{relative}"], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != sha(path):
            raise ValueError(f"{relative} differs from declared freeze")
    config = json.loads(args.config.read_text())
    if config["namespace"] != NAMESPACE:
        raise ValueError("seed namespace differs")
    args.output.mkdir(parents=True)
    started = time.monotonic()
    receipt = {"label": "score-level planning; no extraction or observational access",
               "freeze_commit": args.freeze_commit, "source_sha256": sha(__file__),
               "config_sha256": sha(args.config), "replicates_per_scenario": config["replicates"],
               "namespace": NAMESPACE, "python": sys.version, "numpy": np.__version__, "platform": platform.platform()}
    receipt["scipy"] = scipy.__version__
    (args.output / "receipt.json").write_text(json.dumps(dict(receipt, status="running"), indent=2) + "\n")
    summary = run(config, args.output)
    if receipt["source_sha256"] != sha(__file__) or receipt["config_sha256"] != sha(args.config):
        raise ValueError("source/configuration changed while running; preserve incomplete outputs")
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    receipt.update(status="completed", elapsed_seconds=time.monotonic() - started,
                   files_sha256={p.name: sha(p) for p in args.output.iterdir() if p.name != "receipt.json"})
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
