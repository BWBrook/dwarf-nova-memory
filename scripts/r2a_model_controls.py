"""Finite synthetic R2 timing-rule controls; no archive or real-data access."""

from __future__ import annotations

import argparse
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
from dnmem.r2_models import evidence_score, fit_ladder

NAMESPACE = "r2a-model-controls-v1"
SOURCES = ("scripts/r2a_model_controls.py", "src/dnmem/r2_models.py", "src/dnmem/r2_scores.py",
           "tests/test_r2_models.py", "docs/protocols/r2-design-v1.md")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def generate(case, replicate, n_train=120, n_test=120):
    if case not in ("stationary", "drifting", "duration"):
        raise ValueError("unknown control")
    seed = int.from_bytes(hashlib.sha256(f"{NAMESPACE}|{case}|{replicate}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    n = n_train + n_test
    marks = rng.normal(size=n + 1)
    durations = np.exp(math.log(12.) + .22 * marks)
    gaps, onsets, ends = [], [1000.], []
    old_level, level = 0., 0.
    for index in range(n + 1):
        if case == "drifting":
            level = .995 * old_level + .03 * rng.normal()
        previous = math.log(gaps[-1]) if gaps else math.log(40.)
        log_gap = math.log(40.) + level + .4 * (previous - math.log(40.) - old_level)
        log_gap += (.10 * marks[index] if case == "duration" else 0.) + .35 * rng.normal()
        gaps.append(math.exp(log_gap))
        ends.append(onsets[-1] + durations[index])
        if index < n:
            onsets.append(ends[-1] + gaps[-1])
        old_level = level
    cutoff = onsets[n_train] + .5 * durations[n_train]
    features, evidence, truth = [], [], []
    for index in range(n):
        issue, target = ends[index] + 2., onsets[index + 1]
        start = issue - 400. + 30.
        first = next((i for i in range(index + 1) if onsets[i] > start), index)
        history = []
        for right in range(max(1, first + 1), index + 1):
            value = None if right % 13 == 0 else math.log(gaps[right - 1])
            history.append({"log_gap": value, "available_at": issue})
        previous = history[-1]["log_gap"] if history else None
        feature = {"emission_index": index, "issue_time": issue, "available_at": issue,
                   "clock_anchor": None if index % 29 == 0 else ends[index],
                   "mark": None if index % 23 == 0 else float(durations[index]),
                   "previous_gap": math.exp(previous) if previous is not None else None,
                   "previous_gap_covered": previous is not None, "gap_history": history}
        asof = cutoff if index < n_train else ends[-1] + gaps[-1]
        ev = {"emission_index": index, "issue_time": issue, "computed_as_of": asof,
              "evidence_available_at": asof, "kind": "point", "onset_t": target}
        if target <= issue:
            ev.update(kind="excluded", reason="true_onset_before_issue")
        elif index < n_train and index % 17 == 0 and target > issue + 10.:
            ev.update(kind="right_censored", censor_at=issue + 10.)
        elif index < n_train and index % 7 == 0:
            ev.update(kind="interval", onset_lo=target - .2, onset_hi=target + .2)
        features.append(feature)
        evidence.append(ev)
        truth.append({"emission_index": index, "issue_time": issue, "kind": "point", "onset_t": target})
    return features, evidence, truth, {"seed": seed, "case": case, "replicate": replicate,
        "training_cutoff": cutoff, "n_train": n_train, "n_test": n_test,
        "history_policy": "400-day prefix with30-day boundary margin; every13th gap missing",
        "missing_policy": "every29th anchor and23rd mark missing; no redraws",
        "training_evidence": "point; every7th interval+-0.2day; every17th10day censor if truly surviving"}


def trial(case, replicate, output):
    rows, evidence, truth, meta = generate(case, replicate)
    cutoff = meta["training_cutoff"]
    train = [row for row in rows if row["issue_time"] < cutoff]
    train_ids = {row["emission_index"] for row in train}
    models = fit_ladder(train, [row for row in evidence if row["emission_index"] in train_ids], cutoff)
    scores, nesting_checks = [], 0
    for row, outcome in zip(rows, truth):
        if row["emission_index"] in train_ids or outcome["onset_t"] <= row["issue_time"]:
            continue
        result = {"emission_index": row["emission_index"], "issue_time": row["issue_time"]}
        for name, model in models.items():
            base, route = model.predict(row)
            marked, marked_route = model.predict(row, True)
            zero = type(model).from_dict({**model.to_dict(), "beta": 0.})
            if zero.predict(row) != zero.predict(row, True):
                raise ValueError("zero-offset prediction is not exactly nested")
            nesting_checks += 1
            plain, enriched = evidence_score(base, outcome), evidence_score(marked, outcome)
            if not all(math.isfinite(value) for value in (plain, enriched)):
                raise ValueError("nonfinite synthetic score")
            result[name] = {"base": plain, "marked": enriched, "gain": enriched - plain,
                            "base_route": route, "mark_route": marked_route}
        scores.append(result)
    summary = {"meta": meta, "scored": len(scores), "exact_zero_nesting_checks": nesting_checks,
               "training_exclusions": sum(row["kind"] == "excluded" for row in evidence if row["emission_index"] in train_ids),
               "evaluation_exclusions": meta["n_test"] - len(scores),
               "rungs": {name: {"mean_gain": statistics.fmean(row[name]["gain"] for row in scores),
                                  "mean_base_log_density": statistics.fmean(row[name]["base"] for row in scores),
                                  "beta": model.beta, "metadata": model.metadata}
                         for name, model in models.items()}}
    write(output / f"{case}-{replicate:03d}.json", {"features": rows, "training_evidence": evidence[:len(train)],
        "truth": truth, "models": {name: m.to_dict() for name, m in models.items()}, "scores": scores, "summary": summary})
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output exists; preserve prior controls")
    for path in SOURCES:
        expected = subprocess.check_output(["git", "show", args.freeze_commit + ":" + path], cwd=ROOT)
        if hashlib.sha256(expected).hexdigest() != sha(ROOT / path):
            raise ValueError("source differs from freeze: " + path)
    args.output.mkdir(parents=True)
    started = time.monotonic()
    source = {path: sha(ROOT / path) for path in SOURCES}
    receipt = {"status": "running", "label": "finite synthetic model controls, not calibration or real-data R2b",
               "freeze_commit": args.freeze_commit, "namespace": NAMESPACE, "source_sha256": source,
               "environment": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()}}
    write(args.output / "receipt.json", receipt)
    results, failures = [], []
    for case in ("stationary", "drifting", "duration"):
        for replicate in range(3):
            try:
                results.append(trial(case, replicate, args.output))
                print(f"completed {case}/{replicate}", flush=True)
            except Exception as exc:
                failures.append({"case": case, "replicate": replicate, "type": type(exc).__name__, "error": str(exc)})
                print(f"failed {case}/{replicate}: {exc}", flush=True)
    aggregate = []
    for case in ("stationary", "drifting", "duration"):
        own = [row for row in results if row["meta"]["case"] == case]
        for rung in ("B0", "B1", "B2"):
            values = [row["rungs"][rung]["mean_gain"] for row in own]
            if values:
                aggregate.append({"case": case, "rung": rung, "histories": len(values),
                    "mean_gain": statistics.fmean(values),
                    "mc_se": statistics.stdev(values) / math.sqrt(len(values)) if len(values)>1 else None,
                    "positive_offsets": sum(row["rungs"][rung]["beta"] > 0 for row in own)})
    write(args.output / "summary.json", {"label": receipt["label"], "histories_completed": len(results),
        "failures": failures, "rows": aggregate, "exact_zero_nesting_checks": sum(r["exact_zero_nesting_checks"] for r in results)})
    if source != {path: sha(ROOT / path) for path in SOURCES}:
        failures.append({"error": "source changed during control batch"})
    receipt.update(status="completed_with_failures" if failures else "completed", failures=failures,
                   elapsed_seconds=time.monotonic()-started,
                   files_sha256={p.name: sha(p) for p in args.output.iterdir() if p.name!='receipt.json'})
    write(args.output / "receipt.json", receipt)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
