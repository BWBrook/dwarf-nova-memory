#!/usr/bin/env python3
"""Run the frozen A04g X4 validation grid without retaining its results."""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SCRIPTS = ROOT / "scripts"
FREEZE_BASE = "a04g-validation|"
CANDIDATE_REF = "352a09e"
THRESHOLDS = (9.5, 10.0, 10.5)
RULES = ("C1_7", "C2_095")
FINDERS = ("X1", "X2", "X3", "X4")
ERAS = ("1910_1929", "1930_1949", "1950_1959")
CASES = ("primary", "structured", "gross", "alternative", "legacy", "offset", "v1", "early")

RUNTIME_SOURCES = (
    "scripts/run_x4_validation.py", "scripts/summarize_x4_validation.py",
    "scripts/summarize_x3_validation.py",
    "src/dnmem/x4_benchmark.py", "src/dnmem/x4_cadence.py", "src/dnmem/x4_validation.py",
    "src/dnmem/extract_x4.py", "src/dnmem/injection_truth.py",
    "src/dnmem/injection_truth_v2.py", "src/dnmem/injection_truth_v3.py",
    "src/dnmem/injection_observe.py", "src/dnmem/injection_score.py",
    "src/dnmem/x3_observation.py",
    "src/dnmem/extract.py", "src/dnmem/extract_x3.py",
    "src/dnmem/x3_validation_score.py", "docs/protocols/a04g-x4-independent-validation-v1.md",
    "configs/a04g_inputs.json", "configs/a04g_benchmark.json",
)

QUALIFICATION_SOURCES = (
    "scripts/calibrate_x4_benchmark.py", "src/dnmem/x4_benchmark.py",
    "src/dnmem/injection_truth.py", "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_truth_v3.py", "src/dnmem/injection_observe.py",
    "src/dnmem/x3_observation.py", "src/dnmem/x4_cadence.py",
    "src/dnmem/validation_morphology.py", "src/dnmem/extract.py",
    "src/dnmem/coverage.py", "src/dnmem/aavso.py",
    "configs/a04e_benchmark.json",
    "docs/protocols/a04g-x4-independent-validation-v1.md",
)

CADENCE_FLAT_FIELDS = (
    "observed_target_days", "borrowed_days", "no_match_days", "no_match_fraction",
    "empty_days_preserved", "boundary_rows_omitted", "output_observed_days",
    "additional_empty_days", "total_empty_days", "bright_runs", "bright_runs_matched",
    "bright_runs_unmatched",
)


def seed_for(base: Any, *labels: Any) -> int:
    payload = "|".join(map(str, (base,) + labels)).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any, label: str) -> str:
    value = str(value).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"{label} must be a SHA256 digest")
    return value


def _hash_map(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{label} must be a non-empty SHA256 map")
    return {str(key): _digest(digest, f"{label}[{key}]") for key, digest in value.items()}


def git_commit(commit: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("freeze commit must be a full 40-hex hash")
    try:
        resolved = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=ROOT, text=True,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("freeze commit is not present in Git") from exc
    if resolved != commit.lower():
        raise ValueError("freeze commit must be the full resolved hash")
    return resolved


def git_blob_sha256(commit: str, relative: str) -> str:
    try:
        content = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"freeze commit does not contain {relative}") from exc
    return hashlib.sha256(content).hexdigest()


def candidate_source_hash() -> tuple[str, str]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{CANDIDATE_REF}^{{commit}}"], cwd=ROOT, text=True,
    ).strip()
    current = sha256(ROOT / "src/dnmem/extract_x4.py")
    expected = git_blob_sha256(commit, "src/dnmem/extract_x4.py")
    if current != expected:
        raise ValueError("working X4 source differs from the 352a09e candidate")
    return commit, current


def verify_source_tree(freeze_commit: str, paths: Iterable[str] = RUNTIME_SOURCES) -> dict[str, str]:
    hashes = {}
    for relative in paths:
        current = sha256(ROOT / relative)
        if current != git_blob_sha256(freeze_commit, relative):
            raise ValueError(f"working source differs from freeze commit: {relative}")
        hashes[relative] = current
    return hashes


def canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def project_relative(path: Path) -> str:
    """Return a receipt-safe project-relative path."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError as exc:
        raise ValueError(f"receipt path is outside the project: {path}") from exc


def validate_qualification(path: Path, parameters: Mapping[str, Any], freeze_commit: str,
                           inputs_hash: str, parameters_hash: str) -> str:
    receipt = json.loads(path.read_text())
    if not isinstance(receipt, Mapping) or receipt.get("mode") != "qualify":
        raise ValueError("A04g qualification receipt is not a qualify receipt")
    if receipt.get("seed_base") != FREEZE_BASE.replace("validation", "qualification") + freeze_commit:
        raise ValueError("qualification seed namespace does not match freeze")
    if receipt.get("freeze_commit") != freeze_commit or receipt.get("commit") != freeze_commit:
        raise ValueError("qualification freeze/commit does not match")
    if receipt.get("inputs_sha256") != inputs_hash or receipt.get("parameters_sha256") != parameters_hash:
        raise ValueError("qualification is bound to different inputs or parameters")
    if receipt.get("configuration_count") != 1 or receipt.get("replicates_per_era_phase") != 32:
        raise ValueError("qualification grid is not the frozen one-configuration, 32-replicate grid")
    if receipt.get("all_passed") is not True:
        raise ValueError("qualification did not pass")
    selected = receipt.get("selected")
    if not isinstance(selected, Mapping) or not isinstance(selected.get("parameters"), Mapping):
        raise ValueError("qualification has no selected parameters")
    if canonical(selected["parameters"]) != canonical(parameters):
        raise ValueError("validation parameters differ from qualified parameters")
    for family in ("v2", "v3"):
        phases = selected.get("phases") if family == "v3" else receipt.get("v2")
        if not isinstance(phases, Mapping):
            raise ValueError(f"qualification has no {family} phase results")
        for phase_name in ("random", "diverse"):
            phase = phases.get(phase_name)
            if not isinstance(phase, Mapping) or phase.get("passed") is not True:
                raise ValueError(f"qualification phase did not pass: {family}/{phase_name}")
            try:
                no_match = float(phase.get("mean_no_match_fraction"))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"qualification phase has invalid no-match cadence: {family}/{phase_name}") from exc
            if not math.isfinite(no_match) or no_match > 0.1:
                raise ValueError(f"qualification phase has excessive no-match cadence: {family}/{phase_name}")
            morphology = phase.get("morphology")
            if not isinstance(morphology, Mapping) or morphology.get("passed") is not True:
                raise ValueError(f"qualification morphology did not pass: {family}/{phase_name}")
            if phase_name == "diverse":
                diversity = phase.get("diversity")
                if not isinstance(diversity, Mapping) or set(diversity) != set(ERAS):
                    raise ValueError("diverse qualification has no observer-diversity results")
                if any(not isinstance(value, Mapping) or not isinstance(value.get("gate"), Mapping)
                       or value["gate"].get("passed") is not True
                       for value in diversity.values()):
                    raise ValueError(f"observer-diversity qualification did not pass: {family}")
    source_hashes = _hash_map(receipt.get("source_sha256"), "qualification source_sha256")
    missing_sources = set(QUALIFICATION_SOURCES).difference(source_hashes)
    if missing_sources:
        raise ValueError(f"qualification source manifest is incomplete: {sorted(missing_sources)}")
    for relative, observed in source_hashes.items():
        if observed != git_blob_sha256(freeze_commit, relative):
            raise ValueError(f"qualification source differs from freeze: {relative}")
    config_path = ROOT / "configs/a04g_inputs.json"
    if not config_path.is_file():
        raise ValueError("missing frozen A04g input manifest")
    config = json.loads(config_path.read_text())
    if not isinstance(config, Mapping):
        raise ValueError("A04g input manifest is not an object")
    if config.get("prepared_inputs_sha256") != inputs_hash:
        raise ValueError("prepared inputs do not match frozen A04g manifest")
    if config.get("parameters_sha256") != parameters_hash:
        raise ValueError("parameters do not match frozen A04g manifest")
    git_commit(str(config.get("calibration_source_commit", "")))
    _digest(config.get("calibration_receipt_sha256"), "A04g calibration receipt")
    if receipt.get("calibration_receipt_sha256") != config.get("calibration_receipt_sha256"):
        raise ValueError("qualification calibration receipt is not the frozen one")
    attempts = _hash_map(config.get("calibration_attempts_sha256"), "A04g calibration attempts")
    if _hash_map(receipt.get("calibration_attempts_sha256"), "qualification calibration attempts") != attempts:
        raise ValueError("qualification calibration attempts do not match the frozen map")
    benchmark_path = ROOT / "configs/a04g_benchmark.json"
    if not benchmark_path.is_file():
        raise ValueError("missing frozen A04g benchmark manifest")
    benchmark = json.loads(benchmark_path.read_text())
    if not isinstance(benchmark, Mapping) or canonical(parameters) != canonical(benchmark):
        raise ValueError("parameters differ from the frozen benchmark manifest")
    return sha256(path)


def load_json(path: Path) -> tuple[dict[str, Any], str]:
    value = json.loads(path.read_text())
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(value), sha256(path)


def build_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []

    def add(case, families, strata, phases, reps, thresholds):
        for family in families:
            for stratum in strata:
                for phase in phases:
                    for replicate in range(reps):
                        task = {"case": case, "family": family, "stratum": stratum,
                                "phase": phase, "replicate": replicate,
                                "thresholds": tuple(thresholds) if not callable(thresholds)
                                else tuple(thresholds(family, replicate))}
                        if case == "v1" or replicate < 25:
                            task["reference_extractors"] = ("X1", "X2", "X3")
                        else:
                            task["reference_extractors"] = ()
                        if case == "v1":
                            task["reference_extractors"] = ("X1", "X2", "X3") if replicate < 25 else ("X3",)
                        tasks.append(task)

    def primary_thresholds(family, replicate):
        return THRESHOLDS if family == "v3" and replicate < 200 else (10.0,)

    add("primary", ("v2", "v3"), ERAS, ("random", "diverse"), 400, primary_thresholds)
    add("structured", ("v2", "v3"), ERAS, ("random", "diverse"), 400, (10.0,))
    add("gross", ("v3",), ERAS, ("random", "diverse"), 400, (10.0,))
    add("alternative", ("v2", "v3"), ERAS, ("random", "diverse"), 200,
        lambda family, replicate: THRESHOLDS if family == "v3" else (10.0,))
    add("legacy", ("v2",), ERAS, ("legacy",), 200, (10.0,))
    add("offset", ("v3",), ERAS, ("random",), 200, (10.0,))
    add("v1", ("v1",), ERAS, ("random",), 200, (10.0,))
    add("early", ("v3",), ("1900_1909",), ("random", "diverse"), 200, (10.0,))
    if len(tasks) != 16600:
        raise AssertionError(f"expected 16600 histories, got {len(tasks)}")
    return tasks


def expected_grid(tasks: Iterable[Mapping[str, Any]]) -> set[tuple[Any, ...]]:
    grid = set()
    for task in tasks:
        base = (task["case"], task["family"], task["stratum"], task["phase"], task["replicate"])
        for threshold in task["thresholds"]:
            for rule in RULES:
                grid.add((*base, str(float(threshold)), "X4", rule))
                for finder in task["reference_extractors"]:
                    grid.add((*base, "10.0", finder, rule))
    return grid


def manifest_counts(tasks: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    tasks = list(tasks)
    return {"histories": len(tasks), "metric_rows": len(expected_grid(tasks)),
            "ledger_records": sum(2 for _ in tasks)}


def _json_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _flatten(score: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    heavy = {"pair_records", "operational_confirmation_first_records",
             "operational_confirmation_emissions"}
    row, ledger = {}, {}
    for key, value in score.items():
        if key in heavy:
            ledger[key] = value
        elif isinstance(value, (dict, list, tuple)):
            row[key] = _json_value(value)
        else:
            row[key] = value
    return row, ledger


def _run_task(task: Mapping[str, Any], inputs: Mapping[str, Any], parameters: Mapping[str, Any], base: str):
    from dnmem.extract import x1_vote_episodes, x2_median_hysteresis
    from dnmem.extract_x3 import x3_fitted_episodes
    from dnmem.extract_x4 import x4_episodes
    from dnmem.injection_truth import truth_catalogue as v1_catalogue
    from dnmem.x3_validation_score import score_validation as reference_score
    from dnmem.x4_benchmark import observed_history
    from dnmem.x4_validation import score_validation as x4_score

    rows, history, generator, stratum, seed, cadence, contamination = observed_history(
        inputs, parameters, task, base)
    start, stop = float(stratum["start"]), float(stratum["stop"])
    truth_seed = seed_for(seed, "truth")
    measurement_seed = seed_for(seed, "measurement")
    task_rows, ledgers = [], []
    cadence_flat = {f"cadence_{key}": cadence.get(key, "") for key in CADENCE_FLAT_FIELDS}
    cadence_flat.update({"contamination": _json_value(contamination) if contamination else ""})
    cadence_metadata = _json_value(cadence)
    for threshold in task["thresholds"]:
        truth = list(generator.truth_catalogue(history, float(threshold)))
        finders = [("X4", lambda: x4_episodes(rows, threshold=float(threshold)), x4_score)]
        if math.isclose(float(threshold), 10.0):
            finders.extend([
                ("X1", lambda: x1_vote_episodes(rows, threshold=10.0), reference_score),
                ("X2", lambda: x2_median_hysteresis(rows, low=9.7, high=10.3, cross=10.0), reference_score),
                ("X3", lambda: x3_fitted_episodes(rows, threshold=10.0), reference_score),
            ])
        selected = {name: (factory, scorer) for name, factory, scorer in finders
                    if name == "X4" or name in task["reference_extractors"]}
        for name, (factory, scorer) in selected.items():
            extraction_error = ""
            try:
                episodes = factory()
            except Exception as exc:
                episodes = []
                extraction_error = type(exc).__name__
            scores = scorer(rows, episodes, truth, start, stop, float(threshold))
            for score in scores:
                flat, ledger = _flatten(score)
                row = {"case": task["case"], "family": task["family"],
                       "stratum": task["stratum"], "phase": task["phase"],
                       "replicate": task["replicate"], "seed": seed,
                       "truth_seed": truth_seed, "measurement_seed": measurement_seed,
                       "threshold": float(threshold), "extractor": name,
                       "extraction_error": extraction_error, "cadence_metadata": cadence_metadata,
                       **cadence_flat, **flat}
                task_rows.append(row)
                if name == "X4" and math.isclose(float(threshold), 10.0):
                    ledgers.append({"case": task["case"], "family": task["family"],
                                    "stratum": task["stratum"], "phase": task["phase"],
                                    "replicate": task["replicate"], "seed": seed,
                                    "threshold": 10.0, "rule": score.get("rule"), **ledger})
    return task_rows, ledgers


_PAYLOAD = None
_PARAMETERS = None
_BASE = None


def _init_worker(inputs, parameters, base):
    global _PAYLOAD, _PARAMETERS, _BASE
    _PAYLOAD, _PARAMETERS, _BASE = inputs, parameters, base


def _worker(task):
    return _run_task(task, _PAYLOAD, _PARAMETERS, _BASE)


def _fields(rows: list[dict[str, Any]]) -> list[str]:
    preferred = ["case", "family", "stratum", "phase", "replicate", "seed", "truth_seed",
                 "measurement_seed", "threshold", "extractor", "rule", "extraction_error",
                 "cadence_metadata"]
    keys = set().union(*(row.keys() for row in rows))
    return preferred + sorted(keys.difference(preferred))


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    freeze = git_commit(args.freeze_commit)
    inputs, inputs_hash = load_json(args.inputs)
    parameters, parameters_hash = load_json(args.parameters)
    qualification_hash = validate_qualification(args.qualification, parameters, freeze, inputs_hash, parameters_hash)
    qualification = json.loads(args.qualification.read_text())
    sources = verify_source_tree(freeze)
    candidate_commit, candidate_hash = candidate_source_hash()
    tasks = build_tasks()
    expected = manifest_counts(tasks)
    if expected["metric_rows"] != 51800 or expected["ledger_records"] != 33200:
        raise AssertionError(f"unexpected A04g manifest counts: {expected}")
    inputs_path = project_relative(args.inputs)
    parameters_path = project_relative(args.parameters)
    qualification_path = project_relative(args.qualification)
    args.output.mkdir(parents=False, exist_ok=False)
    base = FREEZE_BASE + freeze
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    receipt = {"status": "running", "validation_base": base, "freeze_commit": freeze,
               "actual_commit": actual, "candidate_ref": CANDIDATE_REF,
               "candidate_commit": candidate_commit, "candidate_file_sha256": candidate_hash,
               "runtime": {"python": sys.version, "platform": platform.platform(),
                           "implementation": platform.python_implementation()},
               "runtime_source_sha256": sources, "inputs_sha256": inputs_hash,
               "parameters_sha256": parameters_hash, "qualification_sha256": qualification_hash,
               "qualification_source_sha256": qualification["source_sha256"],
               "calibration_receipt_sha256": qualification["calibration_receipt_sha256"],
               "calibration_attempts_sha256": qualification["calibration_attempts_sha256"],
               "inputs_path": inputs_path,
               "parameters_path": parameters_path,
               "qualification_path": qualification_path,
               "input_manifest_sha256": sha256(ROOT / "configs/a04g_inputs.json"),
               "benchmark_manifest_sha256": sha256(ROOT / "configs/a04g_benchmark.json"),
               "expected_histories": expected["histories"], "expected_metric_rows": expected["metric_rows"],
               "expected_ledger_records": expected["ledger_records"]}
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    metrics_path, ledger_path = args.output / "metrics.csv", args.output / "x4_threshold10_ledger.jsonl.gz"
    completed = metric_count = ledger_count = 0
    pool = None
    iterator = ((_run_task(task, inputs, parameters, base) for task in tasks)
                if args.workers == 1 else None)
    if iterator is None:
        pool = ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker,
                                   initargs=(inputs, parameters, base))
        iterator = pool.map(_worker, tasks)
    try:
        writer = None
        with metrics_path.open("w", newline="") as metrics, ledger_path.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as ledger:
                for rows, records in iterator:
                    if writer is None:
                        writer = csv.DictWriter(metrics, fieldnames=_fields(rows),
                                                lineterminator="\n", extrasaction="ignore")
                        writer.writeheader()
                    writer.writerows(rows)
                    for record in records:
                        ledger.write((_json_value(record) + "\n").encode())
                    completed += 1
                    metric_count += len(rows)
                    ledger_count += len(records)
                    if completed % 20 == 0 or completed == len(tasks):
                        metrics.flush(); ledger.flush()
                        print(f"{completed}/{len(tasks)} histories", flush=True)
    finally:
        if pool is not None:
            pool.shutdown()
    if (completed != expected["histories"] or metric_count != expected["metric_rows"]
            or ledger_count != expected["ledger_records"]):
        raise RuntimeError("A04g validation did not complete the fixed manifest")
    post_sources = verify_source_tree(freeze)
    if post_sources != sources or candidate_source_hash() != (candidate_commit, candidate_hash):
        raise RuntimeError("runtime source identity changed during validation")
    receipt.update({"status": "completed", "completed_histories": completed,
                    "completed_metric_rows": metric_count, "metrics_sha256": sha256(metrics_path),
                    "ledger_sha256": sha256(ledger_path), "ledger_records": ledger_count,
                    "elapsed_seconds": time.monotonic() - started})
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
