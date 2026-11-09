"""Frozen R2b development fits and exploratory evaluation on retained data."""

import argparse
from collections import Counter
from datetime import date
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.r2b_features import prepare_feature_ledgers
from dnmem.r2b_models import fit_bases, fit_mark, local_lag_index
from dnmem.r2b_scoring import (aggregate_contrast, outcome_evidence,
                                paired_clock_gain, residual_diagnostics, score_contrast)

SOURCES = ("docs/protocols/r2b-execution-v1.md", "configs/r2b_execution.json", "scripts/r2b_execute.py",
           "scripts/r2b_feature_preparation.py", "src/dnmem/r2b_features.py", "src/dnmem/r2b_models.py",
           "src/dnmem/r2b_scoring.py", "src/dnmem/r2_features.py", "src/dnmem/r2_models.py",
           "src/dnmem/r2_scores.py", "src/dnmem/extract_x5.py", "src/dnmem/extract_x4.py",
           "src/dnmem/extract_x3.py", "src/dnmem/extract.py", "src/dnmem/prefix_features.py",
           "tests/test_r2b_features.py", "tests/test_r2b_models.py", "tests/test_r2b_scoring.py",
           "tests/test_r2b_execution.py", "uv.lock")
CLOCKS = ("point_original", "df", "point_at_df")


def require_periods(config):
    expected = {"training_start": 1910, "training_stop": 1960, "evaluation_stop": 2018}
    for key, year in expected.items():
        if config[key] != date(year, 1, 1).toordinal() + 1721424.5:
            raise ValueError("configuration differs from the authorized period: " + key)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def rehearsal_rows(config):
    rng = np.random.default_rng(config["rehearsal_seed"])
    events, onset = [], config["rehearsal_first_onset"]
    for i in range(config["rehearsal_episodes"]):
        width = float(10. if i % 2 else 17.)
        events.append((onset, width))
        onset += width + float(math.exp(3.65 + .1 * math.log(width / 13.) + .24 * rng.normal()))
    rows = []
    for night in range(math.floor(events[0][0]) - 50, math.ceil(events[-1][0] + 90)):
        for observer, offset in (("invented-A", .1), ("invented-B", .3)):
            t = night + offset
            mag = 12.
            for start, width in events:
                age = t - start
                if -2. <= age < 2.:
                    mag = min(mag, 10. - age)
                elif 2. <= age < width - 2.:
                    mag = min(mag, 8.)
                elif width - 2. <= age < width + 2.:
                    mag = min(mag, 10. + age - width)
            rows.append({"obsID": "synthetic-" + str(len(rows)), "JD": t,
                         "mag": mag + float(rng.normal(0., .06)), "fainterThan": "0",
                         "obsName": observer, "by": observer, "band": "Vis.", "val": "V"})
    return rows


def summarize_scores(scores):
    bounds = [r for r in scores if r["bounds_lower"] is not None]
    return {"working": aggregate_contrast(scores),
            "algebraically_known_contrasts": aggregate_contrast(scores, "known_contrast"),
            "point_sensitivity": aggregate_contrast(scores, "point_gain"),
            "deterministic_bounds": {"n": len(bounds),
                "lower_mean": statistics.fmean(r["bounds_lower"] for r in bounds) if bounds else None,
                "upper_mean": statistics.fmean(r["bounds_upper"] for r in bounds) if bounds else None,
                "scope": "fixed realized observation-C mixed functional; conditional A0/A1 and survival"},
            "base_routes": dict(Counter(r.get("base_route", "paired") for r in scores)),
            "marked_routes": dict(Counter(r.get("marked_route", "paired") for r in scores)),
            "reasons": dict(Counter(r.get("reason", "paired") for r in scores)),
            "supported_identities": sum(r.get("identical_forecasts", False) and r["gain"] is not None for r in scores),
            "unsupported_identities": sum(r.get("identical_forecasts", False) and r["gain"] is None for r in scores)}


def model_metadata(rule):
    fit = rule.metadata["base_fit"]
    theta = rule.timing.parameters
    if rule.timing.rung == "B2":
        bounds = [(-5., 8.), (-.95, .95), (math.log(1e-4), 0.), (math.log(.03), math.log(2.))]
        boundaries = [i for i, (value, (lo, hi)) in enumerate(zip(theta, bounds))
                      if min(abs(value - lo), abs(value - hi)) < 1e-6]
    else:
        boundaries = []
    return {"rung": rule.timing.rung, "beta": rule.beta, "marker": rule.marker,
            "cadence_beta": rule.cadence_beta, "base_stable": fit["stable"],
            "base_objective": fit["objective"], "multistart_spread": fit["multistart_spread"],
            "successful_starts": sum(r["successful"] for r in fit["attempts"]),
            "declared_starts": len(fit["attempts"]), "B2_parameter_boundary_indices": boundaries,
            "training_rows": rule.metadata["training_rows"], "timing_rows": rule.metadata["timing_rows"],
            "offset_fit": rule.metadata.get("offset_fit"),
            "design_rank": fit.get("design_rank"), "design_columns": fit.get("design_columns")}


def execute(rows, ledgers, config, output, receipt):
    start, split, stop = config["training_start"], config["training_stop"], config["evaluation_stop"]
    periods, evidence = {}, {}
    for clock in CLOCKS:
        periods[clock] = {
            "development": [r for r in ledgers[clock] if start <= r["issue_time"] < split],
            "evaluation": [r for r in ledgers[clock] if split <= r["issue_time"] < stop]}
        for period, features in periods[clock].items():
            outcomes = outcome_evidence(rows, features, stop=split if period == "development" else stop)
            evidence[(clock, period)] = outcomes
            write(output / f"{clock}-{period}-features-unreleased.json", features)
            write(output / f"{clock}-{period}-evidence-unreleased.json", outcomes)
    models = {}
    for clock in CLOCKS:
        features = periods[clock]["development"]
        outcomes = evidence[(clock, "development")]
        bases = fit_bases(features, outcomes, split)
        models[clock] = {rung + ".duration": fit_mark(base, features, outcomes, split) for rung, base in bases.items()}
        models[clock]["B2.flux"] = fit_mark(bases["B2"], features, outcomes, split, "flux")
        if clock == "df":
            models[clock]["B2.rate"] = fit_mark(bases["B2"], features, outcomes, split, "rate")
            cadence_base = fit_bases(features, outcomes, split, include_cadence=True, rungs=("B2",))["B2"]
            models[clock]["B2.cadence"] = fit_mark(cadence_base, features, outcomes, split)
        print("development fits complete: " + clock, flush=True)
    parameters = {clock: {name: model.to_dict() for name, model in own.items()} for clock, own in models.items()}
    write(output / "parameters-unreleased.json", parameters)
    parameter_sha = digest(output / "parameters-unreleased.json")
    receipt.update(stage="development_parameters_saved_before_evaluation", parameters_sha256=parameter_sha)
    write(output / "receipt.json", receipt)
    summaries, evaluation_scores, residuals, local_indices = {}, {}, {}, {}
    for clock, own in models.items():
        summaries[clock], evaluation_scores[clock], residuals[clock] = {}, {}, {}
        for name, rule in own.items():
            scores = score_contrast(periods[clock]["evaluation"], evidence[(clock, "evaluation")], rule)
            evaluation_scores[clock][name] = scores
            write(output / f"{clock}-{name}-scores-unreleased.json", scores)
            flagged_ev = outcome_evidence(rows, periods[clock]["evaluation"], stop=stop, include_flagged=True)
            flagged = score_contrast(periods[clock]["evaluation"], flagged_ev, rule)
            write(output / f"{clock}-{name}-flagged-scores-unreleased.json", flagged)
            summaries[clock][name] = {**summarize_scores(scores), "model": model_metadata(rule),
                                      "including_flagged_windows": summarize_scores(flagged)}
            if name.endswith(".duration") or name == "B2.cadence":
                residuals[clock][name] = {period: residual_diagnostics(features, evidence[(clock, period)], rule)
                                         for period, features in periods[clock].items()}
            if clock == "df" and name.endswith(".duration"):
                own_indices = [local_lag_index(rule, row) for row in periods[clock]["evaluation"]]
                write(output / f"df-{name}-local-index-unreleased.json", own_indices)
                available = [r["local_index"] for r in own_indices if r["status"] == "available"]
                local_indices[name] = {"n": len(available), "unsupported": len(own_indices) - len(available),
                                      "mean": statistics.fmean(available) if available else None,
                                      "median": statistics.median(available) if available else None,
                                      "maximum": max(available, default=None), "is_upper_bound": False}
    pair = paired_clock_gain(evaluation_scores["df"]["B2.duration"], evaluation_scores["point_at_df"]["B2.duration"])
    write(output / "H3-paired-scores-unreleased.json", pair)
    headline = {"H1": summaries["point_original"]["B2.duration"], "H2": summaries["df"]["B2.duration"],
                "H3": summarize_scores(pair)}
    populations = {clock: {period: {"issues": len(features),
                    "outcomes": dict(Counter(e["kind"] for e in evidence[(clock, period)])),
                    "reasons": dict(Counter(e["reason"] for e in evidence[(clock, period)]))}
                  for period, features in own.items()} for clock, own in periods.items()}
    result = {"label": receipt["label"], "source_freeze": receipt["freeze_commit"], "parameters_sha256": parameter_sha,
              "headline": headline, "comparisons": summaries, "populations": populations,
              "residual_proxies": residuals, "local_lag_indices": local_indices,
              "sealed_DF_B2_development_stable": models["df"]["B2.duration"].metadata["base_fit"]["stable"],
              "sealed_fallback_if_current_development_rule_applied":
                  "B2" if models["df"]["B2.duration"].metadata["base_fit"]["stable"] else "B1",
              "limits": ["post-result exploration; no confirmation", "CAR and latent containment not established",
                         "scheduled population differs from empirically supported score population",
                         "local Fisher index is not an upper bound", "residuals are midpoint proxies",
                         "finite multistart optimization is not global identification",
                         "no new observation access or protected-period access"]}
    if digest(output / "parameters-unreleased.json") != parameter_sha:
        raise ValueError("parameters changed during evaluation")
    write(output / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("rehearsal", "real"), required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--features", type=Path)
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/r1_censor_audit")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; preserve all previous receipts/results")
    relative = args.output.resolve().relative_to(ROOT)
    if subprocess.run(["git", "check-ignore", "-q", str(relative / "parameters-unreleased.json")], cwd=ROOT).returncode:
        parser.error("all individual ledgers and model outputs must be ignored")
    sources = {name: digest(ROOT / name) for name in SOURCES}
    for name, expected in sources.items():
        frozen = subprocess.check_output(["git", "show", args.freeze_commit + ":" + name], cwd=ROOT)
        if hashlib.sha256(frozen).hexdigest() != expected:
            parser.error("source differs from declared freeze: " + name)
    config = json.loads((ROOT / "configs/r2b_execution.json").read_text())
    require_periods(config)
    args.output.mkdir(parents=True)
    receipt = {"status": "running", "stage": "input_guards", "mode": args.mode,
               "label": "synthetic raw-report rehearsal" if args.mode == "rehearsal" else "real retained SS Cyg exploratory R2b",
               "freeze_commit": args.freeze_commit, "source_sha256": sources,
               "environment": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()}}
    write(args.output / "receipt.json", receipt)
    started = time.monotonic()
    try:
        if args.mode == "rehearsal":
            rows = rehearsal_rows(config)
            ledgers = prepare_feature_ledgers(rows, stop=config["evaluation_stop"])
            write(args.output / "synthetic-rows.json", rows)
        else:
            if args.features is None:
                raise ValueError("real mode requires committed-source feature preparation")
            cache = json.loads((args.cache / "private-cache-receipt.json").read_text())
            if cache["stop_jd_exclusive"] != config["evaluation_stop"]:
                raise ValueError("retained cache period differs")
            for name, metadata in cache["files"].items():
                if digest(args.cache / name) != metadata["sha256"]:
                    raise ValueError("retained cache hash differs: " + name)
            rows = json.loads((args.cache / "validated-rows.json").read_text())
            feature_receipt = json.loads((args.features / "receipt.json").read_text())
            if feature_receipt["status"] != "completed" or feature_receipt["freeze_commit"] != args.freeze_commit:
                raise ValueError("feature preparation is incomplete or from another freeze")
            if feature_receipt["cache_receipt_sha256"] != digest(args.cache / "private-cache-receipt.json"):
                raise ValueError("features and outcomes use different retained caches")
            for name, expected in feature_receipt["source_sha256"].items():
                if digest(ROOT / name) != expected:
                    raise ValueError("feature source changed: " + name)
            for name, expected in feature_receipt["output_sha256"].items():
                if digest(args.features / name) != expected:
                    raise ValueError("feature output changed: " + name)
            ledgers = {name: json.loads((args.features / (name + "-unreleased.json")).read_text()) for name in CLOCKS}
            receipt["feature_receipt_sha256"] = digest(args.features / "receipt.json")
            receipt["cache_receipt_sha256"] = digest(args.cache / "private-cache-receipt.json")
            original = json.loads((ROOT / "data/simulations/a10d_20261108/run-receipt.json").read_text())
            original_sources = original["source"]["source_sha256"]
            if len(original_sources) != 26 or any(digest(ROOT / name) != expected for name, expected in original_sources.items()):
                raise ValueError("original qualified forecasting sources changed")
            expected_parameter = "ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3"
            if digest(ROOT / "data/fits/a10e_1910_1959/frozen_parameters.json") != expected_parameter:
                raise ValueError("original frozen parameters changed")
            receipt["preserved_original_qualified_sources"] = len(original_sources)
            receipt["preserved_original_parameters_sha256"] = expected_parameter
        if any(float(row["JD"]) >= config["evaluation_stop"] or row["band"] != "Vis." or row["val"] != "V" for row in rows):
            raise ValueError("observation date/band boundary violated")
        result = execute(rows, ledgers, config, args.output, receipt)
        if sources != {name: digest(ROOT / name) for name in SOURCES}:
            raise ValueError("source changed during execution")
        receipt.update(status="completed", stage="exploratory_scores_written", elapsed_seconds=time.monotonic() - started,
                       output_sha256={p.name: digest(p) for p in args.output.iterdir() if p.name != "receipt.json"})
    except Exception as exc:
        receipt.update(status="failed", error_type=type(exc).__name__, error=str(exc), elapsed_seconds=time.monotonic() - started)
        write(args.output / "receipt.json", receipt)
        raise
    write(args.output / "receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "mode": args.mode,
                      "headline_means": {name: row["working"]["six_year"]["estimate"] for name, row in result["headline"].items()}}))


if __name__ == "__main__":
    main()
