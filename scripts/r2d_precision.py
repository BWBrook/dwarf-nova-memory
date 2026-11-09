"""Frozen sequential point-log-gap precision screen; never reads observations."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.stats import beta as beta_distribution

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.r2d_simulation import capped_star_weights, trial

DESIGN = ROOT / "data/provenance/r2d_precision/design.json"
SOURCES = ["scripts/r2d_precision.py", "src/dnmem/r2d_simulation.py",
           "tests/test_r2d_simulation.py", "tests/test_r2d_precision.py",
           "data/provenance/r2d_precision/design.json",
           "docs/protocols/r2d-sealed-design-v1.md"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_for(namespace, case, replicate):
    return int.from_bytes(hashlib.sha256(f"{namespace}|{case}|{replicate}".encode()).digest()[:8], "big")


def exact_interval(success, count, confidence=.95):
    if count == 0:
        return None
    tail = (1-confidence)/2
    return [float(beta_distribution.ppf(tail, success, count-success+1)) if success else 0.,
            float(beta_distribution.ppf(1-tail, success+1, count-success)) if success < count else 1.]


def score_sign_flip(vectors):
    stars = vectors["star"]
    count = np.bincount(stars)
    weight = capped_star_weights(count)
    contribution = np.bincount(stars, weights=vectors["score"] * weight[stars] / count[stars])
    signs = np.asarray(list(itertools.product([-1., 1.], repeat=len(count))))
    observed = float(contribution.sum())
    p = float(np.mean(signs @ contribution >= observed - 1e-12))
    return {"p": p, "reject_one_sided": p <= .05, "minimum_p": 2.**(-len(count))}


def execute_case(task):
    case, design, output = task
    path = Path(output) / f"{case['id']}-trials.jsonl"
    if path.exists():
        raise FileExistsError(path)
    records = []
    started = time.monotonic()
    with path.open("x") as stream:
        for replicate in range(design["replicates_per_case"]):
            seed = seed_for(design["namespace"], case["id"], replicate)
            try:
                result, vectors = trial(case, seed, return_vectors=True)
                result["score_sign_flip"] = score_sign_flip(vectors)
                result["status"] = "passed"
            except Exception as error:
                result = {"status": "failed", "error_type": type(error).__name__, "error": str(error)}
            result.update(case=case["id"], replicate=replicate, seed=seed)
            stream.write(json.dumps(result, sort_keys=True, allow_nan=False)+"\n")
            records.append(result)
    summary = summarize(case, records)
    summary.update(trials_sha256=sha(path), elapsed_seconds=time.monotonic()-started)
    return summary


def summarize(case, records):
    ok = [r for r in records if r["status"] == "passed"]
    n = len(ok)
    methods = {}
    for clustering in ("halves", "star"):
        for statistic in ("gain", "score"):
            values = [r["methods"][clustering][statistic] for r in ok]
            rejects = sum(v["reject_one_sided"] for v in values)
            estimates = [v["estimate"] for v in values]
            record = {"rejections": rejects, "rate": rejects/n if n else None,
                      "exact_mc95": exact_interval(rejects, n),
                      "mean_estimate": float(np.mean(estimates)) if n else None,
                      "reject_with_negative_predictable_gain": sum(v["reject_one_sided"] and
                          r["conditional_expected_gain"] < 0 for r, v in zip(ok, values))}
            if statistic == "gain":
                covered = sum(v["covers_conditional_expected_gain"] for v in values)
                identity = [i for i, r in enumerate(ok) if not r["gain_identity"]]
                nonidentity_covered = sum(values[i]["covers_conditional_expected_gain"] for i in identity)
                record.update(covered=covered, coverage=covered/n if n else None,
                              coverage_mc95=exact_interval(covered, n),
                              nonidentity_count=len(identity), nonidentity_covered=nonidentity_covered,
                              nonidentity_coverage=nonidentity_covered/len(identity) if identity else None,
                              nonidentity_coverage_mc95=exact_interval(nonidentity_covered, len(identity)))
            methods[f"{clustering}-{statistic}"] = record
    rejected = sum(r["score_sign_flip"]["reject_one_sided"] for r in ok)
    methods["star-score-sign-flip"] = {"rejections": rejected, "rate": rejected/n if n else None,
                                      "exact_mc95": exact_interval(rejected, n),
                                      "minimum_p": 2.**(-case["stars"])}
    return {"case": case["id"], "family": case["family"], "settings": case,
            "attempted": len(records), "completed": n, "failures": len(records)-n,
            "methods": methods, "identity_count": sum(r["gain_identity"] for r in ok),
            "mean_beta": float(np.mean([r["beta_hat"] for r in ok])) if n else None,
            "mean_predictable_gain": float(np.mean([r["conditional_expected_gain"] for r in ok])) if n else None,
            "mean_predictable_score": float(np.mean([r["conditional_expected_score"] for r in ok])) if n else None,
            "positive_score_negative_gain_count": sum(r["conditional_expected_score"] > 0 and
                                                        r["conditional_expected_gain"] < 0 for r in ok),
            "mean_supported_marks": float(np.mean([r["markable_evaluation"] for r in ok])) if n else None,
            "mean_nominal_individual_oracle_gain": float(np.mean([r["nominal_direct_oracle_gain"] for r in ok])) if n else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("local resource envelope is one to four workers")
    freeze = subprocess.check_output(["git", "rev-parse", args.freeze_commit], cwd=ROOT, text=True).strip()
    hashes = {}
    for name in SOURCES:
        frozen = subprocess.check_output(["git", "show", f"{freeze}:{name}"], cwd=ROOT)
        if hashlib.sha256(frozen).hexdigest() != sha(ROOT/name):
            raise ValueError(f"source changed since freeze: {name}")
        hashes[name] = sha(ROOT/name)
    design = json.loads(DESIGN.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(execute_case, [(case, design, str(args.output)) for case in design["cases"]]))
    summary = {"scope": "independent sequential Gaussian point-log-gap screen, not calendar-yield or X5 validation",
               "selection": design["selection"], "cases": cases,
               "limitations": ["predictable path-average gain is not unconditional long-run KL",
                               "sign flips require independent symmetric star contributions; stressed empirically only",
                               "no method is selected on these same simulation outcomes",
                               "no-direct-effect scenarios may still allow predictive gain over an estimated baseline",
                               "Monte Carlo intervals are per cell, not simultaneous certifications"]}
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)+"\n")
    receipt = {"freeze_commit": freeze, "source_sha256": hashes, "namespace": design["namespace"],
               "seed_rule": "first eight SHA256 bytes big endian of namespace|case|replicate",
               "workers": args.workers, "started_unix": started, "elapsed_seconds": time.time()-started,
               "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform(),
               "summary_sha256": sha(args.output/"summary.json"),
               "attempted": sum(c["attempted"] for c in cases), "failures": sum(c["failures"] for c in cases)}
    (args.output/"receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"cases": len(cases), "attempted": receipt["attempted"], "failures": receipt["failures"],
                      "elapsed_seconds": receipt["elapsed_seconds"]}))
    if receipt["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
