"""Bounded six-star R2d supplement. Requires a root source freeze before execution."""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy

from r2d_precision import execute_case

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "data/provenance/g3a_preparation/six-star-design.json"
SOURCES = ["scripts/g3a_six_star_precision.py", "scripts/r2d_precision.py",
           "src/dnmem/r2d_simulation.py", "tests/test_r2d_simulation.py", "tests/test_r2d_precision.py",
           "data/provenance/g3a_preparation/six-star-design.json"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute_supplement(task):
    case, design, output = task
    result = execute_case(task)
    joint = {cl: Counter() for cl in ("star", "halves")}
    with (Path(output) / (case["id"] + "-trials.jsonl")).open() as stream:
        for line in stream:
            row = json.loads(line)
            if row["status"] != "passed":
                continue
            for cl, counts in joint.items():
                score = row["methods"][cl]["score"]["reject_one_sided"]
                gain = row["methods"][cl]["gain"]["reject_one_sided"]
                counts["both"] += score and gain
                counts["gain_without_score"] += gain and not score
                counts["score_without_gain"] += score and not gain
                counts["neither"] += not score and not gain
    result["sequence_counts"] = {cl:dict(counts) for cl,counts in joint.items()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("one to four local workers only")
    freeze = subprocess.check_output(["git", "rev-parse", args.freeze_commit], cwd=ROOT, text=True).strip()
    hashes = {}
    for name in SOURCES:
        frozen = subprocess.check_output(["git", "show", freeze + ":" + name], cwd=ROOT)
        hashes[name] = sha(ROOT / name)
        if hashlib.sha256(frozen).hexdigest() != hashes[name]:
            raise ValueError("source differs from requested freeze: " + name)
    design = json.loads(DESIGN.read_text())
    if len(design["cases"]) != 8 or design["replicates_per_case"] != 2000 or any(c["stars"] != 6 for c in design["cases"]):
        raise ValueError("supplement must contain exactly eight six-star cases with2000replicates each")
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(execute_supplement, [(case, design, str(args.output)) for case in design["cases"]]))
    summary = dict(scope=design["scope"], selection=design["selection"], cases=cases,
                   limitations=design["limits"], seed_namespace=design["namespace"])
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    receipt = dict(freeze_commit=freeze, source_sha256=hashes, namespace=design["namespace"],
                   seed_rule="first eight SHA256 bytes big endian of namespace|case|replicate",
                   workers=args.workers, started_unix=started, elapsed_seconds=time.time() - started,
                   python=sys.version, numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(),
                   summary_sha256=sha(args.output / "summary.json"),
                   attempted=sum(c["attempted"] for c in cases), failures=sum(c["failures"] for c in cases))
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(cases=len(cases), attempted=receipt["attempted"], failures=receipt["failures"])))
    raise SystemExit(bool(receipt["failures"]))


if __name__ == "__main__":
    main()
