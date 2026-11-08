#!/usr/bin/env python3
"""One finite calibration, fresh joint qualification, and no candidate scoring."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import statistics as st
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from a04h_morphology_targets import features, statistics, WAVEFORM, CADENCE, NAMES
from a04i_predictive_gate import check_block
from dnmem.joint_benchmark import generate_observations
from dnmem.x4_benchmark import seed_for
from dnmem.x4_cadence import observer_diversity

ACCEPTED_INPUT = "572f24f553c7be443c888483ede4c50c67979b05ce75901eeb0470512fa72811"
ERAS = ("1910_1929", "1930_1949", "1950_1959")
BASE_SOURCES = (
    "scripts/a04i_pipeline.py", "scripts/a04i_predictive_gate.py",
    "scripts/a04h_morphology_targets.py", "src/dnmem/joint_benchmark.py",
    "src/dnmem/phase_cadence.py", "src/dnmem/injection_truth_v4.py",
    "src/dnmem/injection_truth_v2.py", "src/dnmem/injection_truth.py",
    "src/dnmem/injection_observe.py", "src/dnmem/x4_benchmark.py",
    "src/dnmem/x4_cadence.py", "src/dnmem/extract.py",
    "src/dnmem/coverage.py", "src/dnmem/aavso.py",
    "configs/a04e_benchmark.json", "configs/a04i_grid.json",
    "data/simulations/a04h_morphology_targets_20261108.json",
    "docs/protocols/a04i-joint-validation-v1.md",
)
INPUTS = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def source_state():
    return {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {name: sha(ROOT / name) for name in BASE_SOURCES},
            "python": sys.version}


def clean_source_state():
    initial = source_state()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT):
        raise ValueError("benchmark execution requires a clean source commit")
    for name, expected in initial["source_sha256"].items():
        blob = subprocess.check_output(["git", "show", f"{initial['commit']}:{name}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("benchmark source differs from HEAD")
    return initial


def describe_counts(values):
    return {"episodes": len(values), "median": st.median(values) if values else None,
            "share_le_2": sum(x <= 2 for x in values) / len(values) if values else None}


def prepare(args):
    from dnmem.coverage import combine_acquisitions
    from dnmem.phase_cadence import build_profiles
    initial = clean_source_state()
    if sha(args.original) != ACCEPTED_INPUT:
        raise ValueError("not the accepted pre1960 cache")
    original = json.loads(args.original.read_text())
    paths = sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml"))
    actual = {p.parent.name: sha(p) for p in paths}
    if len(paths) != 12 or actual != original["source_sha256"]:
        raise ValueError("native source identities changed")
    rows, _ = combine_acquisitions(paths)
    if any(not 2413559.5 <= float(r["JD"]) <= 2436934.0 for r in rows):
        raise ValueError("out-of-scope/reserved native row")
    profiles = build_profiles(rows, model=original["brightness_model"])
    expected_bounds = [("1910_1929", 2418672.5, 2425977.5),
                       ("1930_1949", 2425977.5, 2433282.5),
                       ("1950_1959", 2433282.5, 2436934.0)]
    if [(s["stratum"], s["start"], s["stop"]) for s in original["strata"] if s["stratum"] in ERAS] != expected_bounds:
        raise ValueError("not the frozen half-open era bounds")
    records, counts, diversity, years = [], {}, {}, 0.0
    for s in original["strata"]:
        if s["stratum"] not in ERAS:
            continue
        sliced = [r for r in rows if float(s["start"]) <= float(r["JD"]) < float(s["stop"])]
        rs = features(sliced)
        records.extend(rs)
        counts[s["stratum"]] = len(rs)
        diversity[s["stratum"]] = describe_counts(observer_diversity(sliced, s["start"], s["stop"])["counts"])
        years += (s["stop"] - s["start"]) / 365.25
    target = statistics(records, years)
    if counts != dict(zip(ERAS, (141, 123, 70))) or profiles["summary"]["profiles"] != 398:
        raise ValueError("real feature/profile counts differ from the predeclared input")
    if set(target) != set(NAMES) or any(not math.isfinite(v) for v in target.values()):
        raise ValueError("invalid real target vector")
    payload = {**original, "phase_profiles": profiles, "joint_targets": target,
               "joint_target_counts": counts, "joint_diversity": diversity, "joint_exposure_years": years}
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "inputs.json", payload)
    receipt = {"preparation_commit": initial["commit"], "code_source_sha256": initial["source_sha256"],
               "original_inputs_sha256": ACCEPTED_INPUT, "inputs_sha256": sha(args.output / "inputs.json"),
               "source_sha256": actual, "real_targets": target, "real_counts": counts,
               "diversity": diversity, "exposure_years": years,
               "profile_summary": profiles["summary"],
               "operator_sha256": sha(ROOT / "scripts/a04h_morphology_targets.py"),
               "profile_builder_sha256": sha(ROOT / "src/dnmem/phase_cadence.py")}
    if source_state() != initial:
        raise ValueError("sources changed during preparation")
    write(args.output / "preparation_receipt.json", receipt)
    print(json.dumps({"real_counts": counts, "targets": target, "diversity": diversity,
                      "profiles": profiles["summary"]}, indent=2))


def make_grid(args):
    from dnmem.phase_cadence import PhaseCadenceConfig
    from dnmem.injection_truth_v4 import ShapeConfig
    cadence = asdict(PhaseCadenceConfig())
    v2 = json.loads((ROOT / "configs/a04e_benchmark.json").read_text())
    result = [{"configuration_id": "v2-00", "pair_id": "v2-phase", "family": "v2", "phase": "phase",
               "shape_config": v2["shape_config"], "noise_multiplier": v2["noise_multiplier"],
               "cadence_config": cadence}]
    index = 0
    for rise, decline in ((.667, .333), (.8, .37), (.95, .4)):
        for level, coupling, scatter in ((8.32, -.045, .22), (8.37, -.055, .25), (8.42, -.065, .28)):
            cfg = ShapeConfig(rise_rate_median=rise, decline_rate_median=decline,
                              rise_rate_log_spread=.65, decline_rate_log_spread=.23,
                              peak_level=level, peak_duration_coupling=coupling, peak_scatter=scatter)
            result.append({"configuration_id": f"v4-{index:02d}", "pair_id": "v4-phase",
                           "family": "v4", "phase": "phase", "shape_config": asdict(cfg),
                           "noise_multiplier": .95, "cadence_config": cadence})
            index += 1
    if args.output.exists():
        raise FileExistsError("grid already exists")
    write(args.output, {"calibration_replicates": 16, "qualification_replicates": 150,
                        "configurations": result,
                        "scope": "one fixed phase policy; no variance/covariance search; fixed nuisance bounds"})
    print(f"wrote {len(result)} configurations")


def load_worker(path):
    global INPUTS
    INPUTS = json.loads(Path(path).read_text())


def one_record(task):
    configuration, replicate, base = task
    rs, diversity, metadata, years = [], {}, {}, 0.0
    for s in INPUTS["strata"]:
        if s["stratum"] not in ERAS:
            continue
        seed = seed_for(base, configuration["pair_id"], s["stratum"], replicate)
        rows, history, _, cadence, _ = generate_observations(INPUTS, configuration, s, seed)
        rs.extend(features(rows))
        diversity[s["stratum"]] = observer_diversity(rows, s["start"], s["stop"])["counts"]
        metadata[s["stratum"]] = {"cadence": {k: v for k, v in cadence.items() if k != "events"},
                                   "geometry": history.diagnostics}
        years += (s["stop"] - s["start"]) / 365.25
    try:
        vector = statistics(rs, years)
        if set(vector) != set(NAMES) or any(not math.isfinite(v) for v in vector.values()):
            raise ValueError("incomplete or nonfinite synthetic feature vector")
    except (ValueError, ZeroDivisionError, st.StatisticsError) as exc:
        return {"replicate": replicate, "valid": False, "reason": str(exc), "metadata": metadata}
    return {"replicate": replicate, "valid": True, "statistics": vector,
            "diversity": diversity, "metadata": metadata}


def diversity_check(samples, inputs=None):
    inputs = INPUTS if inputs is None else inputs
    result = {}
    for era in ERAS:
        d = describe_counts([x for s in samples for x in s["diversity"][era]])
        real = inputs["joint_diversity"][era]
        valid = d["median"] is not None and real["median"] > 0
        result[era] = {"summary": d, "real": real, "passed": bool(valid and
                       abs(d["median"] / real["median"] - 1) <= .15 and
                       abs(d["share_le_2"] - real["share_le_2"]) <= .05)}
    return result


def assess_samples(samples, inputs):
    valid = (len(samples) == 150 and [s["replicate"] for s in samples] == list(range(150))
             and all(s["valid"] for s in samples))
    vectors = [s["statistics"] for s in samples] if valid else []
    waveform = check_block(inputs["joint_targets"], vectors, WAVEFORM)
    cadence = check_block(inputs["joint_targets"], vectors, CADENCE)
    diversity = diversity_check(samples, inputs) if valid else {}
    eligible = (waveform["pass"] and cadence["pass"] and len(diversity) == 3
                and all(d["passed"] for d in diversity.values()))
    return {"waveform": waveform, "cadence": cadence, "diversity": diversity,
            "eligible": bool(eligible), "valid_records": sum(s["valid"] for s in samples)}


def objective(samples, scales):
    if any(not s["valid"] for s in samples):
        return None
    return sum(((st.mean(s["statistics"][name] for s in samples) - INPUTS["joint_targets"][name]) /
                scales[name]) ** 2 for name in NAMES)


def validate_chain(args):
    anchor = json.loads((ROOT / "configs/a04i_inputs.json").read_text())
    if (anchor["prepared_inputs_sha256"] != sha(args.inputs)
            or anchor["selected_config_sha256"] != sha(args.selected)
            or anchor["calibration_receipt_sha256"] != sha(args.calibration)
            or anchor["preparation_receipt_sha256"] != sha(args.inputs.parent / "preparation_receipt.json")
            or anchor["original_inputs_sha256"] != ACCEPTED_INPUT
            or anchor["grid_sha256"] != sha(ROOT / "configs/a04i_grid.json")):
        raise ValueError("frozen input/calibration chain differs")
    calibration = json.loads(args.calibration.read_text())
    if (calibration["stage"] != "a04i-calibration" or calibration["seed_base"] != "a04i-calibration-20261108"
            or calibration["replicates_per_configuration"] != 16
            or calibration["commit"] != anchor["calibration_source_commit"]
            or calibration["inputs_sha256"] != sha(args.inputs)
            or calibration["grid_sha256"] != sha(ROOT / "configs/a04i_grid.json")):
        raise ValueError("not the predeclared single calibration grid")
    if set(calibration["source_sha256"]) != set(BASE_SOURCES):
        raise ValueError("incomplete calibration source manifest")
    for name, expected in calibration["source_sha256"].items():
        blob = subprocess.check_output(["git", "show", f"{anchor['calibration_source_commit']}:{name}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("calibration source not preserved")
    grid = json.loads((ROOT / "configs/a04i_grid.json").read_text())
    expected_configs = {c["configuration_id"] + ".json": c for c in grid["configurations"]}
    if (set(anchor["calibration_attempts_sha256"]) != set(expected_configs)
            or calibration["configuration_count"] != len(expected_configs)):
        raise ValueError("incomplete finite calibration grid")
    reference = json.loads((ROOT / "data/simulations/a04h_morphology_targets_20261108.json").read_text())["v2_random"]
    scales = {**reference["waveform"]["synthetic_sd"], **reference["cadence"]["synthetic_sd"]}
    if calibration["fixed_objective_scales"] != scales:
        raise ValueError("calibration objective scales changed")
    attempts = []
    for name, expected in anchor["calibration_attempts_sha256"].items():
        p = args.calibration.parent / name
        if sha(p) != expected:
            raise ValueError("calibration attempt changed")
        attempt = json.loads(p.read_text())
        if (attempt["configuration"] != expected_configs[name]
                or len(attempt["samples"]) != 16
                or [s["replicate"] for s in attempt["samples"]] != list(range(16))
                or attempt["objective"] != objective(attempt["samples"], scales)):
            raise ValueError("calibration attempt differs from the frozen grid/objective")
        attempts.append(attempt)
    selected = {}
    for family in ("v2", "v4"):
        valid = [a for a in attempts if a["configuration"]["family"] == family and a["objective"] is not None]
        if valid:
            chosen = min(valid, key=lambda a: (a["objective"], a["configuration"]["configuration_id"]))
            selected[chosen["configuration"]["pair_id"]] = chosen["configuration"]
    if selected != json.loads(args.selected.read_text()) or selected != calibration["selected"]:
        raise ValueError("selected configurations are not finite-grid winners")
    return anchor


def execute(args):
    global INPUTS
    INPUTS = json.loads(args.inputs.read_text())
    prep = json.loads((args.inputs.parent / "preparation_receipt.json").read_text())
    if prep["inputs_sha256"] != sha(args.inputs) or prep["original_inputs_sha256"] != ACCEPTED_INPUT:
        raise ValueError("prepared input identity differs")
    initial = clean_source_state()
    if (prep["operator_sha256"] != sha(ROOT / "scripts/a04h_morphology_targets.py")
            or prep["profile_builder_sha256"] != sha(ROOT / "src/dnmem/phase_cadence.py")
            or prep["code_source_sha256"] != initial["source_sha256"]):
        raise ValueError("preparation code differs from the frozen benchmark")
    grid = json.loads((ROOT / "configs/a04i_grid.json").read_text())
    if args.command == "calibrate":
        configurations, n, base = grid["configurations"], 16, "a04i-calibration-20261108"
    else:
        if initial["commit"] != args.freeze_commit or subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT):
            raise ValueError("qualification requires clean freeze at HEAD")
        anchor = validate_chain(args)
        for name, expected in initial["source_sha256"].items():
            blob = subprocess.check_output(["git", "show", f"{args.freeze_commit}:{name}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != expected:
                raise ValueError("qualification source differs from freeze")
        configurations, n, base = list(json.loads(args.selected.read_text()).values()), 150, "a04i-qualification|" + args.freeze_commit
    reference = json.loads((ROOT / "data/simulations/a04h_morphology_targets_20261108.json").read_text())["v2_random"]
    scales = {**reference["waveform"]["synthetic_sd"], **reference["cadence"]["synthetic_sd"]}
    if set(scales) != set(NAMES) or any(not math.isfinite(s) or s <= 0 for s in scales.values()):
        raise ValueError("invalid fixed calibration scales")
    args.output.mkdir(parents=True, exist_ok=False)
    attempts, pairs = [], {}
    with ProcessPoolExecutor(args.workers, initializer=load_worker, initargs=(str(args.inputs.resolve()),)) as pool:
        for c in configurations:
            samples = list(pool.map(one_record, [(c, rep, base) for rep in range(n)]))
            attempt = {"configuration": c, "samples": samples, "objective": objective(samples, scales)}
            write(args.output / (c["configuration_id"] + ".json"), attempt)
            attempts.append(attempt)
            print(f"{c['configuration_id']}: {n} real-sized records; objective={attempt['objective']}", flush=True)
            if args.command == "qualify":
                pairs[c["pair_id"]] = {"configuration": c, **assess_samples(samples, INPUTS)}
    if source_state() != initial or sha(args.inputs) != prep["inputs_sha256"]:
        raise ValueError("sources changed during benchmark execution")
    receipt = {**initial, "stage": "a04i-" + ("calibration" if args.command == "calibrate" else "qualification"),
               "seed_base": base, "inputs_sha256": sha(args.inputs), "grid_sha256": sha(ROOT / "configs/a04i_grid.json")}
    if args.command == "calibrate":
        selected = {}
        for family in ("v2", "v4"):
            options = [a for a in attempts if a["configuration"]["family"] == family and a["objective"] is not None]
            if options:
                a = min(options, key=lambda a: (a["objective"], a["configuration"]["configuration_id"]))
                selected[a["configuration"]["pair_id"]] = a["configuration"]
        receipt.update({"replicates_per_configuration": n, "selected": selected, "configuration_count": len(configurations),
                        "fixed_objective_scales": scales})
        write(args.output / "selected.json", selected)
    else:
        receipt.update({"freeze_commit": args.freeze_commit, "selected_config_sha256": sha(args.selected),
                        "replicates_per_pair": n, "pairs": pairs,
                        "eligible_pair_ids": sorted(k for k, v in pairs.items() if v["eligible"]),
                        "calibration_receipt_sha256": sha(args.calibration),
                        "calibration_attempts_sha256": anchor["calibration_attempts_sha256"],
                        "qualification_attempts_sha256": {
                            c["configuration_id"] + ".json": sha(args.output / (c["configuration_id"] + ".json"))
                            for c in configurations}})
    write(args.output / "receipt.json", receipt)
    if args.command == "qualify" and not receipt["eligible_pair_ids"]:
        raise SystemExit("no pair qualified; X4 recovery remains unrun")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--original", type=Path, default=ROOT / "outputs/a04g_inputs_20261108/inputs.json")
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("grid")
    p.add_argument("--output", type=Path, default=ROOT / "configs/a04i_grid.json")
    for name in ("calibrate", "qualify"):
        p = sub.add_parser(name)
        p.add_argument("--inputs", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--workers", type=int, default=4)
        if name == "qualify":
            p.add_argument("--selected", type=Path, required=True)
            p.add_argument("--calibration", type=Path, required=True)
            p.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args)
    elif args.command == "grid":
        make_grid(args)
    else:
        execute(args)


if __name__ == "__main__":
    main()
