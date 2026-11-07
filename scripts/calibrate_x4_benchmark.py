#!/usr/bin/env python3
"""Morphology-only calibration and fresh qualification for A04g; no X4 scoring."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.x4_benchmark import observed_history
from dnmem.validation_morphology import records, summary, qualify

ACCEPTED_CACHE = "89825f1b6c92f53713fc800e4be1668ba96200b35f2c44c1ee650bf806f2a5fb"
V2_PARAMETERS_SHA256 = "aa0302035e86a3c0edd2681753d2cae41587cafa186f9392441d6882d7dfed34"
ERAS = ("1910_1929", "1930_1949", "1950_1959")
SOURCES = (
    "scripts/calibrate_x4_benchmark.py", "src/dnmem/x4_benchmark.py",
    "src/dnmem/injection_truth.py", "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_truth_v3.py", "src/dnmem/injection_observe.py",
    "src/dnmem/x3_observation.py", "src/dnmem/x4_cadence.py",
    "src/dnmem/validation_morphology.py", "src/dnmem/extract.py",
    "src/dnmem/coverage.py", "src/dnmem/aavso.py",
    "configs/a04e_benchmark.json",
    "docs/protocols/a04g-x4-independent-validation-v1.md",
)
INPUTS = None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")


def provenance():
    return {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
            "source_sha256": {p: digest(ROOT / p) for p in SOURCES}, "python": sys.version}


def diversity_counts(rows, start, stop):
    from dnmem.extract import x1_vote_episodes
    return [e["n_bright_observers"] for e in x1_vote_episodes(rows)
            if start <= e["peak_t"] < stop and e["onset_lo"] is not None
            and e["end_hi"] is not None and e["end_hi"] - e["onset_lo"] >= 4]


def describe(counts):
    from statistics import median
    return {"episodes": len(counts), "median": median(counts) if counts else None,
            "share_le_1": sum(c <= 1 for c in counts) / len(counts) if counts else None,
            "share_le_2": sum(c <= 2 for c in counts) / len(counts) if counts else None}


def diversity_gate(real, synthetic):
    present = synthetic["episodes"] > 0 and real["median"] > 0
    relative = abs(synthetic["median"] / real["median"] - 1) if present else None
    difference = abs(synthetic["share_le_2"] - real["share_le_2"]) if present else None
    return {"passed": present and relative <= .15 and difference <= .05,
            "median_relative_error": relative, "share_le_2_difference": difference,
            "median_tolerance": .15, "share_tolerance": .05}


def prepare(args):
    from dnmem.coverage import combine_acquisitions
    if digest(args.original) != ACCEPTED_CACHE:
        raise ValueError("not the accepted pre1960 input cache")
    original = json.loads(args.original.read_text())
    paths = sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml"))
    sources = {p.parent.name: digest(p) for p in paths}
    if len(paths) != 12 or sources != original["source_sha256"]:
        raise ValueError("native source identities changed")
    rows, _ = combine_acquisitions(paths)
    if any(not 2413559.5 <= float(r["JD"]) <= 2436934.0 for r in rows):
        raise ValueError("reserved or out-of-scope row")
    rows = [r for r in rows if float(r["JD"]) >= 2418672.5]
    targets = {s["stratum"]: describe(diversity_counts(rows, s["start"], s["stop"]))
               for s in original["strata"] if s["stratum"] in ERAS}
    args.output.mkdir(parents=True, exist_ok=False)
    write_json(args.output / "inputs.json", {**original, "real_diversity": targets})
    write_json(args.output / "preparation_receipt.json",
               {"original_inputs_sha256": ACCEPTED_CACHE, "source_sha256": sources,
                "real_diversity": targets, "inputs_sha256": digest(args.output / "inputs.json")})
    print(json.dumps(targets, indent=2))


def load_worker(path):
    global INPUTS
    INPUTS = json.loads(Path(path).read_text())


def morphology_one(task):
    parameters, family, era, phase, rep, base, thresholds = task
    specification = {"case": "morphology", "family": family, "stratum": era,
                     "phase": phase, "replicate": rep}
    rows, history, _, s, _, cadence, _ = observed_history(INPUTS, parameters, specification, base)
    return {"era": era, "phase": phase,
            "records": {str(t): records(rows, t) for t in thresholds},
            "diversity_counts": diversity_counts(rows, s["start"], s["stop"]),
            "cadence": cadence, "geometry": history.diagnostics}


def evaluate(pool, parameters, family, replicates, base, thresholds):
    output = {}
    for phase in ("random", "diverse"):
        tasks = [(parameters, family, era, phase, rep, base, thresholds)
                 for era in ERAS for rep in range(replicates)]
        results = list(pool.map(morphology_one, tasks))
        summaries = {str(t): summary([r for result in results for r in result["records"][str(t)]])
                     for t in thresholds}
        morphology = qualify(INPUTS["real_morphology"]["10.0"], summaries["10.0"])
        diversity = {}
        for era in ERAS:
            observed = describe([c for r in results if r["era"] == era for c in r["diversity_counts"]])
            diversity[era] = {"summary": observed,
                              "gate": diversity_gate(INPUTS["real_diversity"][era], observed)}
        no_match = sum(r["cadence"].get("no_match_fraction", 0) for r in results) / len(results)
        output[phase] = {"morphology": morphology, "summaries": summaries, "diversity": diversity,
                         "mean_no_match_fraction": no_match,
                         "cadence": [r["cadence"] for r in results],
                         "geometry": [r["geometry"] for r in results],
                         "passed": morphology["passed"] and no_match <= .1 and
                         (phase == "random" or all(v["gate"]["passed"] for v in diversity.values()))}
    return output


def distance(phases):
    total = 0
    for p in phases.values():
        for c in p["morphology"]["comparisons"].values():
            if c.get("relative_error") is not None:
                total += (c["relative_error"] / .15) ** 2
            elif c.get("absolute_difference") is not None:
                total += (c["absolute_difference"] / .15) ** 2
            elif c.get("factor") is not None:
                import math
                total += (math.log(c["factor"]) / math.log(1.5)) ** 2
            elif not c["passed"]:
                total += 1000
    return total


def execute(args):
    global INPUTS
    INPUTS = json.loads(args.inputs.read_text())
    preparation = json.loads((args.inputs.parent / "preparation_receipt.json").read_text())
    if preparation["inputs_sha256"] != digest(args.inputs) or preparation["original_inputs_sha256"] != ACCEPTED_CACHE:
        raise ValueError("prepared input identity changed")
    start_provenance = provenance()
    v2_path = ROOT / "configs/a04e_benchmark.json"
    if digest(v2_path) != V2_PARAMETERS_SHA256:
        raise ValueError("v2 configuration differs from the accepted A04e family")
    v2 = json.loads(v2_path.read_text())
    if args.command == "calibrate":
        from dnmem.injection_truth_v3 import ShapeConfig
        configurations = [{"v2": v2, "v3": {"shape_config": asdict(ShapeConfig(
                             rise_rate_median=rise, decline_rate_median=decline)),
                             "noise_multiplier": noise}}
                          for rise, decline, noise in product((.8, .95, 1.1), (.34, .40, .46), (.85, .95, 1.1))]
        base, reps, thresholds = "a04g-calibration-20261108", 2, (10.0,)
    else:
        if start_provenance["commit"] != args.freeze_commit or subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=ROOT):
            raise ValueError("qualification requires the clean freeze at HEAD")
        for name, expected in start_provenance["source_sha256"].items():
            blob = subprocess.check_output(["git", "show", f"{args.freeze_commit}:{name}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != expected:
                raise ValueError("qualification source differs from freeze")
        anchor = json.loads((ROOT / "configs/a04g_inputs.json").read_text())
        if (anchor["prepared_inputs_sha256"] != digest(args.inputs)
                or anchor["preparation_receipt_sha256"] != digest(args.inputs.parent / "preparation_receipt.json")
                or anchor["original_inputs_sha256"] != ACCEPTED_CACHE
                or anchor["parameters_sha256"] != digest(args.parameters)
                or anchor["calibration_receipt_sha256"] != digest(args.calibration)):
            raise ValueError("input/calibration chain differs from freeze")
        calibration = json.loads(args.calibration.read_text())
        if (calibration["mode"] != "calibrate" or calibration["configuration_count"] != 27
                or calibration["replicates_per_era_phase"] != 2
                or calibration["seed_base"] != "a04g-calibration-20261108"
                or calibration["inputs_sha256"] != digest(args.inputs)):
            raise ValueError("not the finite calibration")
        for name, expected in calibration["source_sha256"].items():
            blob = subprocess.check_output(["git", "show", f"{anchor['calibration_source_commit']}:{name}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != expected:
                raise ValueError("calibration source is not preserved at its recorded commit")
        if set(anchor["calibration_attempts_sha256"]) != {"v2.json", *(f"attempt_{i:02d}.json" for i in range(27))}:
            raise ValueError("incomplete calibration attempt map")
        attempts = []
        for name, expected in anchor["calibration_attempts_sha256"].items():
            if digest(args.calibration.parent / name) != expected:
                raise ValueError("calibration attempt changed")
            if name != "v2.json":
                attempts.append(json.loads((args.calibration.parent / name).read_text()))
        passing = [r for r in attempts if r["passed"]]
        chosen = min(passing, key=lambda r: (r["distance"], r["index"])) if passing else None
        if chosen is None or chosen != calibration["selected"]:
            raise ValueError("calibration selection is not the frozen finite-grid winner")
        configurations = [json.loads(args.parameters.read_text())]
        if configurations[0] != calibration["selected"]["parameters"]:
            raise ValueError("parameters differ from deterministic calibration selection")
        base, reps, thresholds = "a04g-qualification|" + args.freeze_commit, 32, (9.5, 10., 10.5)
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    with ProcessPoolExecutor(args.workers, initializer=load_worker, initargs=(str(args.inputs.resolve()),)) as pool:
        v2_phases = evaluate(pool, configurations[0], "v2", reps, base, thresholds)
        write_json(args.output / "v2.json", v2_phases)
        for index, parameters in enumerate(configurations):
            phases = evaluate(pool, parameters, "v3", reps, base, thresholds)
            result = {"index": index, "parameters": parameters, "phases": phases,
                      "passed": all(v["passed"] for v in phases.values()), "distance": distance(phases)}
            results.append(result)
            write_json(args.output / f"attempt_{index:02d}.json", result)
            print(f"{index+1}/{len(configurations)} morphology configurations; passed={result['passed']}; distance={result['distance']:.3f}", flush=True)
    passing = [r for r in results if r["passed"]]
    selected = min(passing, key=lambda r: (r["distance"], r["index"])) if passing else None
    if provenance() != start_provenance:
        raise ValueError("benchmark sources changed during morphology execution")
    receipt = {**start_provenance, "mode": args.command, "seed_base": base,
               "inputs_sha256": digest(args.inputs), "configuration_count": len(configurations),
               "replicates_per_era_phase": reps, "selected": selected, "v2": v2_phases,
               "all_passed": selected is not None and all(v["passed"] for v in v2_phases.values())}
    if args.command == "qualify":
        receipt.update({"freeze_commit": args.freeze_commit, "parameters_sha256": digest(args.parameters),
                        "calibration_receipt_sha256": digest(args.calibration),
                        "calibration_attempts_sha256": anchor["calibration_attempts_sha256"]})
    write_json(args.output / "receipt.json", receipt)
    if selected:
        write_json(args.output / "parameters.json", selected["parameters"])
    if not receipt["all_passed"]:
        raise SystemExit("benchmark qualification failed; no candidate recovery authorized")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--original", type=Path, default=ROOT / "outputs/a04e_inputs_verified_20261107/inputs.json")
    prep.add_argument("--output", type=Path, required=True)
    for name in ("calibrate", "qualify"):
        p = sub.add_parser(name)
        p.add_argument("--inputs", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--workers", type=int, default=4)
        if name == "qualify":
            p.add_argument("--parameters", type=Path, required=True)
            p.add_argument("--calibration", type=Path, required=True)
            p.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    prepare(args) if args.command == "prepare" else execute(args)


if __name__ == "__main__":
    main()
