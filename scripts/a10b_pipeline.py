#!/usr/bin/env python3
"""Frozen synthetic A10 concordance, then bounded forecast-model development."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import statistics as st
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from dnmem import prefix_features, prefix_reference
from dnmem.forecast_experiment import CASES, ERAS, concordance_stream, score_trial, variant_spec
from dnmem.x4_benchmark import seed_for

SOURCES = (
    "scripts/a10b_pipeline.py", "src/dnmem/forecast_experiment.py",
    "src/dnmem/prefix_features.py", "src/dnmem/prefix_reference.py",
    "src/dnmem/ledger_forecast.py", "src/dnmem/adaptive_effort.py",
    "src/dnmem/joint_benchmark.py", "src/dnmem/phase_cadence.py",
    "src/dnmem/injection_truth.py", "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_truth_v4.py", "src/dnmem/injection_observe.py",
    "src/dnmem/x4_benchmark.py", "src/dnmem/extract.py",
    "src/dnmem/extract_x3.py", "src/dnmem/extract_x4.py",
    "configs/a04i_selected.json", "configs/a04i_inputs.json",
    "configs/a10b_controls.json", "docs/protocols/a10b-model-controls-v1.md",
    "pyproject.toml", "uv.lock",
)
INPUTS = CONFIGS = BASE = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, allow_nan=False, indent=2) + "\n")


def state(freeze):
    import numpy, scipy
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != freeze or len(freeze) != 40 or subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT):
        raise ValueError("production requires the clean full source freeze at HEAD")
    hashes = {p: sha(ROOT/p) for p in SOURCES}
    for p, h in hashes.items():
        blob = subprocess.check_output(["git", "show", f"{freeze}:{p}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != h:
            raise ValueError("source differs from freeze")
    for name in ("extract_x4.py", "extract_x3.py", "extract.py"):
        relative = "src/dnmem/"+name
        original = subprocess.check_output(["git", "show", "352a09e:"+relative], cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != hashes[relative]:
            raise ValueError("X4 or a shared dependency differs from the qualified candidate")
    return {"freeze_commit": freeze, "source_sha256": hashes,
            "environment": {"python": sys.version, "numpy": numpy.__version__,
                            "scipy": scipy.__version__, "platform": platform.platform()}}


def initialize(input_path, base):
    global INPUTS, CONFIGS, BASE
    INPUTS = json.loads(Path(input_path).read_text())
    CONFIGS = json.loads((ROOT/"configs/a04i_selected.json").read_text())
    BASE = base


def concordance_task(index):
    rows, meta = concordance_stream(INPUTS, CONFIGS, index, BASE)
    checks = []
    for latency in (0., 2.):
        left = prefix_features.forecast_ledger(rows, latency=latency, start=meta["start"], stop=meta["stop"])
        right = prefix_reference.forecast_ledger(rows, latency=latency, start=meta["start"], stop=meta["stop"])
        le = prefix_features.outcome_evidence(rows, left, stop=meta["stop"])
        re = prefix_reference.outcome_evidence(rows, right, stop=meta["stop"])
        for kind, a, b in (("ledger", left, right), ("evidence", le, re)):
            if a != b:
                raise ValueError(f"independent {kind} mismatch: history {index}, latency {latency}")
        checks.append({"latency": latency, "issued": len(left),
                       "candidate_sha256": hashlib.sha256(canonical([left, le]).encode()).hexdigest(),
                       "reference_sha256": hashlib.sha256(canonical([right, re]).encode()).hexdigest()})
    return {"index": index, "family": meta["family"], "case": meta["case"], "era": meta["era"],
            "seed": meta["seed"], "checks": checks}


def control_task(task):
    family, case, replicate = task
    try:
        result, scores = score_trial(INPUTS, CONFIGS[family], case, replicate, BASE)
        return {"task": list(task), "success": True, "result": result}, scores
    except Exception as exc:
        return {"task": list(task), "success": False, "error_type": type(exc).__name__,
                "error": str(exc)}, []


def tasks_from_config():
    c = json.loads((ROOT/"configs/a10b_controls.json").read_text())
    return [(family, case, rep) for family, entry in c["families"].items()
            for case in entry["cases"] for rep in range(entry["replicates"])]


def guard_concordance(path, initial, inputs_hash):
    receipt = json.loads(path.read_text())
    if (receipt.get("stage") != "a10b-concordance" or receipt.get("status") != "completed"
            or receipt.get("state") != initial
            or receipt.get("inputs_sha256") != inputs_hash or receipt.get("histories") != 100
            or receipt.get("seed_base") != "a10b-concordance|"+initial["freeze_commit"]):
        raise ValueError("concordance receipt does not cover this frozen run")
    records_path = path.parent/"records.json"
    if receipt.get("records_sha256") != sha(records_path):
        raise ValueError("concordance records changed")
    records = json.loads(records_path.read_text())
    if len(records) != 100 or [r["index"] for r in records] != list(range(100)):
        raise ValueError("concordance does not contain the complete 100-history grid")
    for r in records:
        index = r["index"]
        family = "v2-phase" if index < 80 else "v4-phase"
        case, era = CASES[index % len(CASES)], ERAS[(index // len(CASES)) % 3]
        if (r["family"], r["case"], r["era"], r["seed"]) != (
                family, case, era, seed_for(receipt["seed_base"], "concordance", index, family, case, era)):
            raise ValueError("concordance history identity differs from fixed grid")
        if [c["latency"] for c in r["checks"]] != [0., 2.]:
            raise ValueError("missing latency comparison")
        if any(c["issued"] < 1 or len(c["candidate_sha256"]) != 64
               or c["candidate_sha256"] != c["reference_sha256"] for c in r["checks"]):
            raise ValueError("ledger/evidence disagreement")
    return receipt


def summarize_trials(records):
    from scipy.stats import t
    grouped = {}
    for rec in records:
        if not rec["success"]:
            continue
        r = rec["result"]
        for variant, comparisons in r["results"].items():
            for comparison, values in comparisons.items():
                grouped.setdefault((r["family"], r["case"], variant, comparison), []).append(values)
    planned = {}
    for family, case, replicate in tasks_from_config():
        for variant, *_ in variant_spec(case, replicate):
            for comparison in ("gain_M1_M0", "gain_M2_M0", "gain_M3_M2"):
                key = (family, case, variant, comparison)
                planned[key] = planned.get(key, 0)+1
    result = []
    for key, expected_count in sorted(planned.items()):
        values = grouped.get(key, [])
        means = [v["estimate"] for v in values]
        n, m = len(means), st.fmean(means) if means else None
        sd = st.stdev(means) if n > 1 else None
        radius = float(t.ppf(.975, n-1))*sd/(n**.5) if sd is not None else None
        result.append({"family": key[0], "case": key[1], "variant": key[2], "comparison": key[3],
                       "expected_replicates": expected_count, "failed_or_missing_replicates": expected_count-n,
                       "replicates": n, "mean_gain_nats": m, "block_gain_sd": sd,
                       "mc_lower": m-radius if radius is not None else None,
                       "mc_upper": m+radius if radius is not None else None,
                       "mean_scored_issues": st.fmean(v["n"] for v in values) if values else None,
                       "positive_trials": sum(v > 0 for v in means),
                       "diagnostic_intervals_positive": sum(v["lower"] is not None and v["lower"] > 0 for v in values)})
    return result


def paired_stress_contrasts(records):
    from scipy.stats import t
    available = {tuple(r["task"]): r["result"] for r in records if r["success"]}
    rows = []
    for case in ("gross", "offset", "adaptive"):
        for variant, *_ in variant_spec(case, 0):
            for comparison in ("gain_M1_M0", "gain_M2_M0", "gain_M3_M2"):
                differences = []
                for rep in range(8):
                    baseline = available.get(("v2-phase", "null", rep))
                    stressed = available.get(("v2-phase", case, rep))
                    if baseline and stressed:
                        differences.append(stressed["results"][variant][comparison]["estimate"]-
                                           baseline["results"][variant][comparison]["estimate"])
                n = len(differences)
                mean = st.fmean(differences) if n else None
                radius = float(t.ppf(.975,n-1))*st.stdev(differences)/(n**.5) if n > 1 else None
                rows.append({"case": case, "variant": variant, "comparison": comparison,
                             "paired_trials": n, "expected_pairs": 8, "stress_minus_null": mean,
                             "mc_lower": mean-radius if radius is not None else None,
                             "mc_upper": mean+radius if radius is not None else None,
                             "scope": "paired synthetic trials; stress can change the issuance population"})
    return rows


def run(args):
    initial = state(args.freeze_commit)
    anchor = json.loads((ROOT/"configs/a04i_inputs.json").read_text())
    if sha(ROOT/"configs/a04i_selected.json") != anchor["selected_config_sha256"]:
        raise ValueError("benchmark configuration differs from the frozen input anchor")
    for relative in ("configs/a04i_inputs.json", "configs/a04i_selected.json"):
        original = subprocess.check_output(["git", "show", "b3741b3:"+relative], cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != sha(ROOT/relative):
            raise ValueError("not the retained A04i benchmark/input specification")
    inputs_hash = sha(args.inputs)
    if inputs_hash != anchor["prepared_inputs_sha256"]:
        raise ValueError("not the frozen pre1960-derived benchmark inputs")
    base = "a10b-"+args.stage+"|"+args.freeze_commit
    if args.stage == "controls":
        guard_concordance(args.concordance, initial, inputs_hash)
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    receipt = {"stage": "a10b-"+args.stage, "status": "running", "state": initial,
               "inputs_sha256": inputs_hash, "seed_base": base}
    write(args.output/"receipt.json", receipt)
    records = []
    score_count = 0
    tasks = list(range(100)) if args.stage == "concordance" else tasks_from_config()
    with ProcessPoolExecutor(args.workers, initializer=initialize,
                             initargs=(str(args.inputs.resolve()), base)) as pool:
        if args.stage == "concordance":
            for result in pool.map(concordance_task, tasks):
                records.append(result)
                if len(records) % 10 == 0:
                    print(f"{len(records)}/100 independent concordance histories", flush=True)
        else:
            with (args.output/"scores.jsonl").open("w") as scores:
                for record, rows in pool.map(control_task, tasks):
                    records.append(record)
                    family, case, rep = record["task"]
                    write(args.output/f"{family}-{case}-{rep:03d}.json", record)
                    for row in rows:
                        scores.write(canonical({"family": family, "case": case, "replicate": rep, **row})+"\n")
                        score_count += 1
                    scores.flush()
                    print(f"{len(records)}/{len(tasks)} full-chain trials: {family}/{case}/{rep}: "
                          f"{'complete' if record['success'] else record['error_type']}", flush=True)
    if state(args.freeze_commit) != initial or sha(args.inputs) != inputs_hash:
        raise ValueError("source/input state changed during production")
    write(args.output/"records.json", records)
    receipt.update(status="completed", records_sha256=sha(args.output/"records.json"),
                   elapsed_seconds=time.monotonic()-started)
    if len(records) != len(tasks):
        raise ValueError("incomplete prescribed task grid")
    if args.stage == "concordance":
        receipt["histories"] = len(records)
    if args.stage == "controls":
        expected_rows = sum(v["gain_M3_M2"]["n"] for r in records if r["success"]
                            for v in r["result"]["results"].values())
        if score_count != expected_rows:
            raise ValueError("score row count differs from per-trial variant results")
        receipt.update(trials=len(records), successful_trials=sum(r["success"] for r in records),
                       failed_trials=sum(not r["success"] for r in records),
                       score_rows=score_count,
                       concordance_receipt_sha256=sha(args.concordance),
                       scores_sha256=sha(args.output/"scores.jsonl"),
                       trial_file_sha256={f.name: sha(f) for f in sorted(args.output.glob("v*.json"))})
        if receipt["failed_trials"]:
            receipt["status"] = "completed_with_failures"
        write(args.output/"summary.json", {"freeze_commit": args.freeze_commit,
              "records_sha256": receipt["records_sha256"], "scores_sha256": receipt["scores_sha256"],
              "complete": not receipt["failed_trials"], "rows": summarize_trials(records),
              "paired_stress_contrasts": paired_stress_contrasts(records),
              "scope": "bounded synthetic development pilot; small replicate counts do not calibrate final inference"})
        receipt["summary_sha256"] = sha(args.output/"summary.json")
    write(args.output/"receipt.json", receipt)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=("concordance", "controls"))
    p.add_argument("--freeze-commit", required=True)
    p.add_argument("--inputs", type=Path, default=ROOT/"outputs/a04i_inputs_frozen_20261108/inputs.json")
    p.add_argument("--concordance", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--workers", type=int, choices=(1, 2, 3, 4), default=4)
    run(p.parse_args())
