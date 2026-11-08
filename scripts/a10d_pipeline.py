#!/usr/bin/env python3
"""Frozen directional forecast calibration and independent prefix concordance."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts")]
from dnmem import prefix_features, prefix_reference
from dnmem.adaptive_effort import thin_adaptive
from dnmem.forecast_experiment import ERAS, crop_stratum, observed_block, source_strata
from dnmem.oc_experiment import run_trial, COMPARISONS
from dnmem.oc_statistics import binomial_summary, coverage_screen
from dnmem.oc_streams import _slow_observed_block
from dnmem.x4_benchmark import seed_for

SOURCES = tuple(sorted({
    "scripts/a10d_pipeline.py", "src/dnmem/oc_experiment.py", "src/dnmem/oc_streams.py",
    "src/dnmem/oc_statistics.py", "src/dnmem/directional_forecast.py",
    "src/dnmem/prefix_features.py", "src/dnmem/prefix_reference.py",
    "src/dnmem/ledger_forecast.py", "src/dnmem/forecast_experiment.py",
    "src/dnmem/adaptive_effort.py", "src/dnmem/joint_benchmark.py",
    "src/dnmem/injection_truth.py", "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_truth_v4.py", "src/dnmem/injection_observe.py",
    "src/dnmem/phase_cadence.py", "src/dnmem/x4_benchmark.py",
    "src/dnmem/extract.py", "src/dnmem/extract_x3.py", "src/dnmem/extract_x4.py",
    "configs/a04i_inputs.json", "configs/a04i_selected.json", "configs/a10d_oc.json",
    "docs/protocols/a10d-directional-oc-v1.md", "pyproject.toml", "uv.lock"}))
INPUTS = CONFIGS = BASE = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, allow_nan=False, indent=2)+"\n")


def source_state(freeze, development):
    import numpy, scipy
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT))
    if not development and (head != freeze or dirty):
        raise ValueError("production requires the clean source freeze at HEAD")
    hashes = {p: sha(ROOT/p) for p in SOURCES}
    if not development:
        for p, digest in hashes.items():
            blob = subprocess.check_output(["git", "show", f"{freeze}:{p}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != digest:
                raise ValueError("source differs from freeze")
    for name in ("extract.py", "extract_x3.py", "extract_x4.py"):
        p = "src/dnmem/"+name
        original = subprocess.check_output(["git", "show", "352a09e:"+p], cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != hashes[p]:
            raise ValueError("qualified extractor bytes changed")
    return {"head": head, "development": development, "dirty": dirty,
            "source_sha256": hashes, "environment": {
                "python": sys.version, "numpy": numpy.__version__, "scipy": scipy.__version__,
                "platform": platform.platform()}}


def initialize(path, base):
    global INPUTS, CONFIGS, BASE
    INPUTS = json.loads(Path(path).read_text())
    CONFIGS = json.loads((ROOT/"configs/a04i_selected.json").read_text())
    BASE = base


def concordance_task(index):
    family = "v2-phase" if index < 80 else "v4-phase"
    cases = ("null", "structured", "gross", "offset", "adaptive", "alternative", "slow_090", "slow_098")
    case = cases[index % 8] if index < 80 else ("null", "alternative")[index % 2]
    era = ERAS[(index//8) % 3]
    source = source_strata(INPUTS)[era]
    width = 3*365.25
    windows = max(1, int((source["stop"]-source["start"])//width))
    start = source["start"] + ((index//24) % windows)*width
    source = crop_stratum(source, start, min(start+width, source["stop"]))
    seed = seed_for(BASE, index, family, case, era)
    if case.startswith("slow_"):
        rows, _, _ = _slow_observed_block(INPUTS, CONFIGS[family], source, seed, case)
    else:
        rows, _, _ = observed_block(INPUTS, CONFIGS[family], source, seed, case, seed)
    if case == "adaptive":
        rows, _ = thin_adaptive(rows, seed_for(seed, "adaptive"))
    checks = []
    for delay in (0., 2.):
        a = prefix_features.forecast_ledger(rows, latency=delay, start=source["start"], stop=source["stop"])
        b = prefix_reference.forecast_ledger(rows, latency=delay, start=source["start"], stop=source["stop"])
        ea = prefix_features.outcome_evidence(rows, a, stop=source["stop"])
        eb = prefix_reference.outcome_evidence(rows, b, stop=source["stop"])
        if a != b or ea != eb:
            raise ValueError(f"independent prefix mismatch at {index}/{delay}")
        checks.append({"delay": delay, "issued": len(a),
                       "candidate_sha256": hashlib.sha256(canonical([a, ea]).encode()).hexdigest(),
                       "reference_sha256": hashlib.sha256(canonical([b, eb]).encode()).hexdigest()})
    return {"index": index, "family": family, "case": case, "era": era, "seed": seed, "checks": checks}


def trial_task(task, references, force_references=False):
    family, case, replicate = task
    started = time.monotonic()
    try:
        record, scores = run_trial(INPUTS, CONFIGS[family], case, replicate, BASE,
                                   references=references, force_references=force_references)
        record["elapsed_seconds"] = time.monotonic()-started
        record["worker_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)
        return {"task": list(task), "success": True, "result": record}, scores
    except Exception as exc:
        return {"task": list(task), "success": False, "error_type": type(exc).__name__, "error": str(exc)}, []


def task_grid():
    spec = json.loads((ROOT/"configs/a10d_oc.json").read_text())
    return [(family, case, replicate) for family, entry in spec["families"].items()
            for case in entry["cases"] for replicate in range(entry["replicates"])]


def summarize(records):
    groups = {}
    for record in records:
        family, case, _ = record["task"]
        groups.setdefault((family, case), []).append(record)
    rows = []
    for (family, case), group in sorted(groups.items()):
        good = [r["result"] for r in group if r["success"]]
        variants = sorted(good[0]["intervals"]) if good else []
        for variant in variants:
            for years in (3, 6):
                for field in COMPARISONS:
                    values = [r["intervals"][variant][str(years)][field] for r in good]
                    estimates = [v["estimate"] for v in values]
                    rows.append({"family": family, "case": case, "variant": variant,
                                 "cluster_years": years, "comparison": field,
                                 "mean_gain": statistics.fmean(estimates),
                                 "trial_sd": statistics.stdev(estimates) if len(estimates)>1 else None,
                                 "mean_n": statistics.fmean(v["n"] for v in values),
                                 "rejections": binomial_summary(sum(v["confirmed"] for v in values), len(values))})
    null_cases = {"null", "structured", "gross", "offset", "adaptive"}
    rate_checks = []
    for row in rows:
        if (row["case"] in null_cases and row["variant"] == "primary"
                and row["cluster_years"] == 6 and row["comparison"] == "gain_M3_M2"):
            count = row["rejections"]
            rate_checks.append({"family": row["family"], "case": row["case"], **count,
                                "screen_pass": count["rate"] <= .05,
                                "certification_pass": count["one_sided_upper95"] <= .05})
    calibration = []
    for case in ("null", "alternative"):
        eligible = [r["result"] for r in records if r["success"] and r["task"][:2] == ["v2-phase", case]]
        for years in (3, 6):
            references = [r["reference_calibration"][str(years)] for r in eligible if "reference_calibration" in r]
            if references:
                calibration.append({"case": case, "cluster_years": years, **coverage_screen(references)})
    complete = len(records) == 360 and all(r["success"] for r in records)
    coverage_ok = (len([r for r in calibration if r["cluster_years"] == 6]) == 2
                   and all(r["pass"] for r in calibration if r["cluster_years"] == 6))
    screen_ok = complete and len(rate_checks) == 6 and all(r["screen_pass"] for r in rate_checks) and coverage_ok
    return {"rows": rows, "null_rate_checks": rate_checks, "calibration": calibration,
            "complete": complete, "screen_pass": screen_ok,
            "formal_certification_pass": complete and len(rate_checks) == 6 and all(r["certification_pass"] for r in rate_checks) and coverage_ok,
            "real_fit_automatic": False,
            "scope": "observed-rate screen and joint-MC calibration; real-fit gate policy resolved separately"}


def run(args):
    development = args.stage.startswith("dev-")
    initial = source_state(args.freeze_commit, development)
    anchor = json.loads((ROOT/"configs/a04i_inputs.json").read_text())
    for name in ("configs/a04i_inputs.json", "configs/a04i_selected.json"):
        original = subprocess.check_output(["git", "show", "b3741b3:"+name], cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != sha(ROOT/name):
            raise ValueError("not the retained benchmark/input anchor")
    if sha(args.inputs) != anchor["prepared_inputs_sha256"] or sha(ROOT/"configs/a04i_selected.json") != anchor["selected_config_sha256"]:
        raise ValueError("not the frozen pre1960 benchmark cache/configuration")
    concordance = args.stage.endswith("concordance")
    base = (("a10d-development-"+args.stage)
            if development else ("a10d-concordance" if concordance else "a10c-oc"))
    base += "|"+(hashlib.sha256(canonical(initial).encode()).hexdigest() if development else args.freeze_commit)
    concordance_identity = None
    if not concordance:
        proof_bytes = args.concordance.read_bytes()
        proof = json.loads(proof_bytes)
        if proof["status"] != "completed" or proof["histories"] != 100:
            raise ValueError("100-history concordance must complete before scores")
        proof_records = args.concordance.parent/"records.json"
        record_bytes = proof_records.read_bytes()
        concordance_identity = {"receipt_sha256": hashlib.sha256(proof_bytes).hexdigest(),
                                "records_sha256": hashlib.sha256(record_bytes).hexdigest()}
        comparisons = json.loads(record_bytes)
        if (proof["input_sha256"] != sha(args.inputs) or concordance_identity["records_sha256"] != proof["records_sha256"]
                or len(comparisons) != 100 or [r["index"] for r in comparisons] != list(range(100))):
            raise ValueError("concordance identity/count/digest does not reconcile")
        for record in comparisons:
            if ([c["delay"] for c in record["checks"]] != [0., 2.]
                    or any(c["issued"] < 1 or c["candidate_sha256"] != c["reference_sha256"]
                           for c in record["checks"])):
                raise ValueError("incomplete independent concordance")
        for name in ("src/dnmem/prefix_features.py", "src/dnmem/prefix_reference.py"):
            if proof["source"]["source_sha256"][name] != initial["source_sha256"][name]:
                raise ValueError("ledger/reference changed after concordance")
        if not development and (proof["source"] != initial or proof["development"]):
            raise ValueError("production needs exact frozen source concordance")
        if proof["stage"] not in ("dev-concordance", "concordance"):
            raise ValueError("not a concordance-stage receipt")
        expected_proof_base = ("a10d-development-dev-concordance|" + hashlib.sha256(canonical(proof["source"]).encode()).hexdigest()
                               if proof["development"] else "a10d-concordance|"+proof["source"]["head"])
        if proof["seed_base"] != expected_proof_base or (not development and proof["stage"] != "concordance"):
            raise ValueError("concordance namespace does not match its source/stage contract")
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = {"stage": args.stage, "development": development, "status": "running", "source": initial,
               "seed_base": base, "input_sha256": sha(args.inputs)}
    if concordance_identity:
        receipt["concordance_identity"] = concordance_identity
    write(args.output/"receipt.json", receipt)
    started = time.monotonic()
    tasks = list(range(100)) if concordance else ([("v2-phase", "alternative", 0)] if args.stage == "dev-reference" else
                                                [("v2-phase", c, 0) for c in ("null", "slow_098", "alternative")]
                                                 if development else task_grid())
    results = {}
    with ProcessPoolExecutor(args.workers, initializer=initialize, initargs=(str(args.inputs.resolve()), base)) as pool:
        futures = {pool.submit(concordance_task, task) if concordance else
                   pool.submit(trial_task, task, not development or args.stage == "dev-reference",
                               args.stage == "dev-reference"): task for task in tasks}
        for future in as_completed(futures):
            task = futures[future]
            if concordance:
                result = future.result()
            else:
                result, scores = future.result()
                name = f"{task[0]}-{task[1]}-{task[2]:03d}"
                write(args.output/(name+".json"), result)
                with (args.output/(name+"-scores.jsonl")).open("w") as handle:
                    for row in scores:
                        handle.write(canonical({"family": task[0], "case": task[1], "replicate": task[2], **row})+"\n")
            results[task] = result
            print(f"{len(results)}/{len(tasks)} {task}: "+("match" if concordance else str(result["success"])), flush=True)
    if source_state(args.freeze_commit, development) != initial or sha(args.inputs) != receipt["input_sha256"]:
        raise ValueError("source/input changed during execution")
    if concordance_identity and concordance_identity != {
            "receipt_sha256": sha(args.concordance), "records_sha256": sha(proof_records)}:
        raise ValueError("validated concordance receipt/records changed during execution")
    records = [results[task] for task in tasks]
    write(args.output/"records.json", records)
    receipt.update(status="completed", records_sha256=sha(args.output/"records.json"),
                   elapsed_seconds=time.monotonic()-started)
    if concordance:
        receipt["histories"] = len(records)
    else:
        receipt.update(trials=len(records), successful_trials=sum(r["success"] for r in records),
                       failed_trials=sum(not r["success"] for r in records),
                       concordance_receipt_sha256=concordance_identity["receipt_sha256"])
        if receipt["failed_trials"]:
            receipt["status"] = "completed_with_failures"
        if not development:
            write(args.output/"summary.json", summarize(records))
            receipt["summary_sha256"] = sha(args.output/"summary.json")
    receipt["files_sha256"] = {p.name: sha(p) for p in sorted(args.output.iterdir()) if p.name != "receipt.json"}
    write(args.output/"receipt.json", receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("dev-concordance", "dev-smoke", "dev-reference", "concordance", "oc"))
    parser.add_argument("--freeze-commit")
    parser.add_argument("--inputs", type=Path, default=ROOT/"outputs/a04i_inputs_frozen_20261108/inputs.json")
    parser.add_argument("--concordance", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    run(parser.parse_args())
