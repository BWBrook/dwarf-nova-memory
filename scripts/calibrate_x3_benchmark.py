#!/usr/bin/env python3
"""Calibrate and separately qualify v2 morphology without scoring X3."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.injection_truth_v2 import ShapeConfig, generate_events, magnitudes_at
from dnmem.injection_observe import simulate_rows
from dnmem.validation_morphology import records, summary, qualify
from dnmem.x3_observation import calibrate_brightness, labelled_days, state_compatible_schedule
from run_injection_recovery import seed_for, write_json

INPUTS = None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance():
    paths = [Path(__file__), ROOT / "src/dnmem/injection_truth.py", ROOT / "src/dnmem/injection_truth_v2.py",
             ROOT / "src/dnmem/injection_observe.py", ROOT / "src/dnmem/x3_observation.py",
             ROOT / "src/dnmem/validation_morphology.py", ROOT / "src/dnmem/extract.py"]
    return {"git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
            "python": sys.version, "code_sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths}}


def checked_sources(paths, expected):
    actual = {p.parent.name: digest(p) for p in paths}
    if len(paths) != 12 or len(actual) != 12 or actual != expected:
        raise ValueError("native acquisitions differ from the frozen twelve-source hash map")
    return actual


def prepare(args):
    from dnmem.coverage import combine_acquisitions
    args.output.mkdir(parents=True, exist_ok=False)
    original = json.loads(args.original.read_text())
    paths = sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml"))
    actual_sources = checked_sources(paths, original["source_sha256"])
    rows, _ = combine_acquisitions(paths)
    if any(not 2413559.5 <= float(r["JD"]) <= 2436934.0 for r in rows):
        raise ValueError("observations outside the frozen acquisition window forbidden")
    model, noise_summary = calibrate_brightness(rows, original["model"])
    days = labelled_days(rows)
    strata = []
    for s in original["strata"]:
        strata.append({**s, "days": [d for d in days if math.floor(s["start"]) <= d["day"] < math.ceil(s["stop"])]})
    real = {}
    for threshold in (9.5, 10.0, 10.5):
        real[str(threshold)] = summary(records(rows, threshold))
    payload = {**original, "brightness_model": model, "strata": strata, "real_morphology": real}
    write_json(args.output / "inputs.json", payload)
    receipt = {**provenance(), "original_inputs_sha256": digest(args.original),
               "inputs_sha256": digest(args.output / "inputs.json"), "source_sha256": actual_sources,
               "outburst_calibration": noise_summary, "real_morphology": real}
    write_json(args.output / "preparation_receipt.json", receipt)
    print(json.dumps({"outburst_calibration": noise_summary, "real_magnitude10": real["10.0"]}, indent=2))


def load_worker(path):
    global INPUTS
    INPUTS = json.loads(Path(path).read_text())


def morphology_one(task):
    configuration, era, phase, replicate, base, thresholds = task
    s = INPUTS["strata"][era]
    seed = seed_for(base, s["stratum"], phase, replicate)
    history = generate_events(INPUTS["durations"], INPUTS["gaps"], s["start"], s["stop"],
                              seed_for(seed, "truth"), shape_config=ShapeConfig(**configuration["shape_config"]))
    if phase == "state":
        schedule, cadence = state_compatible_schedule(s["days"], history, s["start"], s["stop"])
    else:
        schedule, cadence = s["schedule"], {"no_match_fraction": 0, "observed_target_days": 0}
    model = {who: {**p, "sigma": p["sigma"] * configuration["noise_multiplier"]}
             for who, p in INPUTS["brightness_model"].items()}
    photometry = simulate_rows(schedule, magnitudes_at(history, [float(r["JD"]) for r in schedule]),
                               model, seed_for(seed, "measurement"))
    return {"records": {str(threshold): records(photometry, threshold) for threshold in thresholds},
            "cadence": cadence}


def distance(check):
    total = 0.0
    for name, c in check["comparisons"].items():
        if "relative_error" in c and c["relative_error"] is not None:
            total += (c["relative_error"] / .15)**2
        elif "absolute_difference" in c and c["absolute_difference"] is not None:
            total += (c["absolute_difference"] / .15)**2
        elif c.get("factor") is not None:
            total += (math.log(c["factor"]) / math.log(1.5))**2
        elif not c["passed"]:
            total += 1000
    return total


def evaluate(pool, configuration, replicates, base, thresholds):
    output = {}
    for phase in ("random", "state"):
        tasks = [(configuration, era, phase, rep, base, thresholds) for era in (1, 2, 3) for rep in range(replicates)]
        pooled = {str(t): [] for t in thresholds}
        no_match = []
        for result in pool.map(morphology_one, tasks):
            for threshold, rs in result["records"].items():
                pooled[threshold].extend(rs)
            no_match.append(result["cadence"]["no_match_fraction"])
        summaries = {threshold: summary(rs) for threshold, rs in pooled.items()}
        check = qualify(INPUTS["real_morphology"]["10.0"], summaries["10.0"])
        mismatch = sum(no_match)/len(no_match)
        output[phase] = {"summaries": summaries, "qualification": check,
                         "mean_no_match_fraction": mismatch,
                         "passed": check["passed"] and mismatch <= .1}
    return output


def execute(args):
    global INPUTS
    INPUTS = json.loads(args.inputs.read_text())
    prep = json.loads((args.inputs.parent / "preparation_receipt.json").read_text())
    if prep["inputs_sha256"] != digest(args.inputs):
        raise ValueError("prepared inputs changed")
    args.output.mkdir(parents=True, exist_ok=False)
    if args.command == "calibrate":
        configurations = [{"shape_config": asdict(ShapeConfig(rise_rate_median=rise,
                              decline_rate_median=decline, decline_rate_log_sd=spread)), "noise_multiplier": noise}
                          for rise, decline, spread, noise in product((.75, .95), (.34, .40, .46), (.20, .35), (.95, 1.15, 1.35))]
        base, reps, thresholds = "a04e-calibration-20261107", 2, (10.0,)
    else:
        if len(args.freeze_commit) != 40 or any(c not in "0123456789abcdef" for c in args.freeze_commit):
            raise ValueError("full freeze commit required")
        configurations = [json.loads(args.parameters.read_text())]
        base, reps, thresholds = "a04e-qualification|" + args.freeze_commit, 12, (9.5, 10.0, 10.5)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=load_worker, initargs=(str(args.inputs.resolve()),)) as pool:
        for index, configuration in enumerate(configurations):
            phases = evaluate(pool, configuration, reps, base, thresholds)
            passed = all(p["passed"] for p in phases.values())
            result = {"configuration": configuration, "phases": phases, "passed": passed,
                      "distance": sum(distance(p["qualification"]) for p in phases.values())}
            results.append(result)
            write_json(args.output / f"attempt_{index:02d}.json", result)
            print(f"{index+1}/{len(configurations)} configurations; passed={passed}; distance={result['distance']:.3f}", flush=True)
    passing = [r for r in results if r["passed"]]
    selected = min(passing, key=lambda r: r["distance"]) if passing else None
    write_json(args.output / "receipt.json", {**provenance(), "inputs_sha256": digest(args.inputs),
        "seed_base": base, "replicates_per_era_phase": reps, "configuration_count": len(results),
        "selected": selected, "all_passed": bool(passing), "mode": args.command})
    if selected:
        write_json(args.output / "parameters.json", selected["configuration"])
    if not passing:
        raise SystemExit("morphology qualification failed; no extractor recovery scores may be run")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--original", type=Path, default=ROOT / "outputs/a04c_inputs_final_20261107/inputs.json")
    prep.add_argument("--output", type=Path, required=True)
    for name in ("calibrate", "qualify"):
        p = sub.add_parser(name)
        p.add_argument("--inputs", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--workers", type=int, default=4)
        if name == "qualify":
            p.add_argument("--parameters", type=Path, required=True)
            p.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    prepare(args) if args.command == "prepare" else execute(args)


if __name__ == "__main__":
    main()
