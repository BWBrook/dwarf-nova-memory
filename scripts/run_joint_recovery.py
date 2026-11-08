#!/usr/bin/env python3
"""Run the bounded A04i joint-waveform recovery grid."""

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

FREEZE_BASE = "a04i-validation|"
QUALIFICATION_BASE = "a04i-qualification|"
CANDIDATE_REF = "352a09e"
ERAS = ("1910_1929", "1930_1949", "1950_1959")
CASES = ("primary", "structured", "gross", "alternative", "offset")
THRESHOLDS = (9.5, 10.0, 10.5)
RULES = ("C1_7", "C2_095")
FINDERS = ("X1", "X2", "X3", "X4")
CADENCE_FLAT_FIELDS = (
    "observed_target_days", "borrowed_days", "no_match_days", "no_match_fraction",
    "empty_days_preserved", "boundary_rows_omitted", "output_observed_days",
    "additional_empty_days", "total_empty_days", "bright_runs", "bright_runs_matched",
    "bright_runs_unmatched",
)

# This is deliberately a code/data identity list, not a qualification manifest.
RUNTIME_SOURCES = (
    "scripts/run_joint_recovery.py", "scripts/summarize_joint_recovery.py",
    "scripts/summarize_x3_validation.py", "src/dnmem/joint_benchmark.py",
    "src/dnmem/phase_cadence.py", "src/dnmem/injection_truth.py",
    "src/dnmem/injection_truth_v2.py", "src/dnmem/injection_truth_v4.py",
    "src/dnmem/injection_observe.py", "src/dnmem/injection_score.py",
    "src/dnmem/extract.py", "src/dnmem/extract_x3.py", "src/dnmem/extract_x4.py",
    "src/dnmem/x3_validation_score.py", "src/dnmem/x4_validation.py",
    "src/dnmem/x4_benchmark.py",
    "src/dnmem/x4_cadence.py", "src/dnmem/coverage.py", "src/dnmem/aavso.py",
    "configs/a04i_selected.json", "configs/a04i_inputs.json",
)


def seed_for(base: Any, *labels: Any) -> int:
    """Match the project seed helper used by the benchmark."""
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
    return {str(key): _digest(item, f"{label}[{key}]") for key, item in value.items()}


def git_commit(commit: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(commit)):
        raise ValueError("freeze commit must be a full 40-hex hash")
    try:
        resolved = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("freeze commit is not present in Git") from exc
    if resolved != str(commit).lower():
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
        ["git", "rev-parse", "--verify", f"{CANDIDATE_REF}^{{commit}}"], cwd=ROOT, text=True
    ).strip()
    current = sha256(ROOT / "src/dnmem/extract_x4.py")
    if current != git_blob_sha256(commit, "src/dnmem/extract_x4.py"):
        raise ValueError("working X4 source differs from the 352a09e candidate")
    return commit, current


def verify_source_tree(freeze_commit: str, paths: Iterable[str] = RUNTIME_SOURCES) -> dict[str, str]:
    result = {}
    for relative in paths:
        current = sha256(ROOT / relative)
        if current != git_blob_sha256(freeze_commit, relative):
            raise ValueError(f"working source differs from freeze commit: {relative}")
        result[relative] = current
    return result


def canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), allow_nan=False)


def project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError as exc:
        raise ValueError(f"receipt path is outside the project: {path}") from exc


def _configuration_map(parameters: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw = parameters.get("families", parameters)
    if not isinstance(raw, Mapping):
        raise ValueError("parameters must contain a family configuration map")
    result = {}
    for family, value in raw.items():
        if not isinstance(value, Mapping):
            continue
        config = dict(value.get("configuration", value))
        config.setdefault("family", str(family))
        result[str(family)] = config
    if not result:
        raise ValueError("parameters contain no family configurations")
    return result


def grid_sha256(configurations: Mapping[str, Mapping[str, Any]]) -> str:
    grid = [list(item) for item in sorted(expected_grid(build_tasks(configurations)))]
    return hashlib.sha256(_json_value(grid).encode()).hexdigest()


def validate_qualification(path: Path, parameters: Mapping[str, Any], freeze: str,
                           inputs_hash: str, parameters_hash: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    receipt = json.loads(path.read_text())
    if receipt.get("stage") != "a04i-qualification":
        raise ValueError("A04i qualification receipt has the wrong stage")
    if receipt.get("freeze_commit") != freeze or receipt.get("seed_base") != QUALIFICATION_BASE + freeze:
        raise ValueError("qualification is bound to a different freeze")
    if receipt.get("inputs_sha256") != inputs_hash or receipt.get("selected_config_sha256") != parameters_hash:
        raise ValueError("qualification is bound to different inputs or selected configurations")
    if receipt.get("replicates_per_pair") != 150:
        raise ValueError("qualification does not use the frozen 150-replicate pair screen")
    pairs = receipt.get("pairs")
    eligible = receipt.get("eligible_pair_ids")
    if not isinstance(pairs, Mapping) or not isinstance(eligible, list) or not eligible:
        raise ValueError("qualification has no eligible pair set")
    if eligible != sorted(set(map(str, eligible))):
        raise ValueError("eligible pair IDs are not sorted and unique")
    marked = sorted(str(pair_id) for pair_id, entry in pairs.items()
                    if isinstance(entry, Mapping) and entry.get("eligible") is True)
    if marked != [str(item) for item in eligible]:
        raise ValueError("eligible pair IDs do not match the qualification marks")
    parameter_map = _configuration_map(parameters)
    if set(pairs) != set(parameter_map):
        raise ValueError("qualification pair set differs from selected configurations")
    from a04i_pipeline import BASE_SOURCES, assess_samples
    evidence = _hash_map(receipt.get("qualification_attempts_sha256"), "qualification attempts")
    if set(evidence) != {c["configuration_id"] + ".json" for c in parameter_map.values()}:
        raise ValueError("qualification evidence does not cover every selected pair")
    for pair_id, config in parameter_map.items():
        attempt_path = path.parent / (config["configuration_id"] + ".json")
        if sha256(attempt_path) != evidence[attempt_path.name]:
            raise ValueError("qualification replicate evidence changed")
        attempt = json.loads(attempt_path.read_text())
        if canonical(attempt["configuration"]) != canonical(config):
            raise ValueError("qualification attempt configuration changed")
        expected = {"configuration": config, **assess_samples(attempt["samples"], inputs)}
        if canonical(expected) != canonical(pairs[pair_id]):
            raise ValueError("qualification eligibility differs from replicate evidence")
    for pair_id in eligible:
        pair_id = str(pair_id)
        entry = pairs.get(pair_id)
        if not isinstance(entry, Mapping) or entry.get("eligible") is not True:
            raise ValueError(f"eligible pair is not marked eligible: {pair_id}")
        configuration = entry.get("configuration")
        if not isinstance(configuration, Mapping) or pair_id not in parameter_map:
            raise ValueError(f"eligible pair lacks selected configuration: {pair_id}")
        if canonical(configuration) != canonical(parameter_map[pair_id]):
            raise ValueError(f"pair configuration differs from selected config: {pair_id}")
        for block_name in ("waveform", "cadence"):
            block = entry.get(block_name)
            if (not isinstance(block, Mapping) or block.get("valid") is not True
                    or block.get("pass") is not True or block.get("replicates") != 150):
                raise ValueError(f"pair {pair_id} failed {block_name} predictive gate")
        if entry.get("valid_records") != 150:
            raise ValueError(f"pair {pair_id} lacks all 150 valid records")
        diversity = entry.get("diversity")
        if not isinstance(diversity, Mapping) or set(diversity) != set(ERAS):
            raise ValueError(f"pair {pair_id} lacks all era diversity gates")
        if any(not isinstance(value, Mapping) or value.get("passed") is not True
               for value in diversity.values()):
            raise ValueError(f"pair {pair_id} failed an era diversity gate")
    selected_path = ROOT / "configs/a04i_selected.json"
    if not selected_path.is_file() or sha256(selected_path) != parameters_hash:
        raise ValueError("selected configuration manifest is not the qualified bytes")
    manifest_path = ROOT / "configs/a04i_inputs.json"
    if not manifest_path.is_file():
        raise ValueError("missing A04i input manifest")
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, Mapping):
        raise ValueError("A04i input manifest is not an object")
    if manifest.get("prepared_inputs_sha256") != inputs_hash or manifest.get("selected_config_sha256") != parameters_hash:
        raise ValueError("A04i input manifest anchors differ")
    grid_hash = _digest(manifest.get("grid_sha256"), "A04i grid")
    if receipt.get("grid_sha256") != grid_hash or sha256(ROOT / "configs/a04i_grid.json") != grid_hash:
        raise ValueError("qualification finite grid differs from manifest")
    _digest(manifest.get("original_inputs_sha256"), "original inputs")
    _digest(manifest.get("preparation_receipt_sha256"), "preparation receipt")
    calibration_hash = _digest(manifest.get("calibration_receipt_sha256"), "calibration receipt")
    if receipt.get("calibration_receipt_sha256") != calibration_hash:
        raise ValueError("qualification calibration receipt differs from manifest")
    calibration_commit = git_commit(str(manifest.get("calibration_source_commit", "")))
    attempts = _hash_map(manifest.get("calibration_attempts_sha256"), "calibration attempts")
    if _hash_map(receipt.get("calibration_attempts_sha256"), "qualification calibration attempts") != attempts:
        raise ValueError("qualification calibration attempts differ from manifest")
    source_hashes = _hash_map(receipt.get("source_sha256"), "qualification source_sha256")
    if set(source_hashes) != set(BASE_SOURCES):
        raise ValueError("qualification source manifest is incomplete")
    for relative, observed in source_hashes.items():
        if observed != git_blob_sha256(freeze, relative) or observed != sha256(ROOT / relative):
            raise ValueError(f"qualification source differs from freeze: {relative}")
    return {"receipt": receipt, "eligible": [str(item) for item in eligible],
            "calibration_source_commit": calibration_commit,
            "calibration_receipt_sha256": calibration_hash,
            "calibration_attempts_sha256": attempts,
            "grid_sha256": grid_hash,
            "source_sha256": source_hashes}


def qualified_configurations(parameters: Mapping[str, Any], qualification: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract only the pre-recovery eligible family configurations.

    The qualification producer supplies ``eligible_pair_ids`` and ``pairs``.
    No family is filtered using recovery output.
    """
    selected = qualification.get("pairs")
    eligible = qualification.get("eligible_pair_ids")
    if not isinstance(selected, Mapping) or not isinstance(eligible, list) or not eligible:
        raise ValueError("qualification has no eligible pair configurations")
    parameter_map = _configuration_map(parameters)
    result = {}
    for raw_family in eligible:
        family = str(raw_family)
        if family not in selected or family not in parameter_map:
            raise ValueError(f"eligible family lacks a frozen configuration: {family}")
        selected_value = selected[family]
        config = dict(selected_value.get("configuration", selected_value)) if isinstance(selected_value, Mapping) else None
        if config is None:
            raise ValueError(f"selected family configuration is not an object: {family}")
        supplied = parameter_map[family]
        if canonical(config) != canonical(supplied):
            raise ValueError(f"family parameters differ from qualification: {family}")
        if "family" not in config or "phase" not in config:
            raise ValueError(f"family configuration lacks family/phase identity: {family}")
        result[family] = {**supplied, "pair_id": family}
    return result


def _thresholds(case: str, replicate: int) -> tuple[float, ...]:
    if case == "primary" and replicate < 200:
        return THRESHOLDS
    if case == "alternative":
        return THRESHOLDS
    return (10.0,)


def build_tasks(configurations: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    tasks = []
    for family, config in configurations.items():
        for case, reps in (("primary", 400), ("structured", 400), ("gross", 400),
                           ("alternative", 200), ("offset", 200)):
            for stratum in ERAS:
                for replicate in range(reps):
                    tasks.append({
                        "family": family, "phase": str(config["phase"]), "case": case,
                        "stratum": stratum, "replicate": replicate,
                        "thresholds": _thresholds(case, replicate),
                        "reference_extractors": ("X1", "X2", "X3") if replicate < 25 else (),
                    })
    return tasks


def expected_grid(tasks: Iterable[Mapping[str, Any]]) -> set[tuple[Any, ...]]:
    grid = set()
    for task in tasks:
        base = (task["family"], task["phase"], task["case"], task["stratum"], task["replicate"])
        for threshold in task["thresholds"]:
            for rule in RULES:
                grid.add((*base, str(float(threshold)), "X4", rule))
                if math.isclose(float(threshold), 10.0):
                    for finder in task["reference_extractors"]:
                        grid.add((*base, "10.0", finder, rule))
    return grid


def manifest_counts(tasks: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    tasks = list(tasks)
    return {"histories": len(tasks), "metric_rows": len(expected_grid(tasks)),
            "ledger_records": 2 * len(tasks)}


def _json_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _flatten(score: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    heavy_names = {"pair_records", "operational_confirmation_first_records",
                   "operational_confirmation_emissions"}
    row, ledger = {}, {}
    for key, value in score.items():
        if key in heavy_names:
            ledger[key] = value
        elif isinstance(value, (dict, list, tuple)):
            row[key] = _json_value(value)
        else:
            row[key] = value
    return row, ledger


def _case_process(case: str) -> tuple[str, bool, bool]:
    return {"primary": ("null", False, False), "structured": ("structured", False, False),
            "gross": ("null", False, True), "alternative": ("alternative", False, False),
            "offset": ("null", True, False)}[case]


def _run_task(task: Mapping[str, Any], inputs: Mapping[str, Any], config: Mapping[str, Any], base: str):
    from dnmem.extract import x1_vote_episodes, x2_median_hysteresis
    from dnmem.extract_x3 import x3_fitted_episodes
    from dnmem.extract_x4 import x4_episodes
    from dnmem.x3_validation_score import score_validation as reference_score
    from dnmem.x4_validation import score_validation as x4_score
    from dnmem.joint_benchmark import generate_observations
    from dnmem.x4_benchmark import seed_for as benchmark_seed_for

    stratum = next(item for item in inputs["strata"] if item["stratum"] == task["stratum"])
    seed = benchmark_seed_for(base, task["family"], task["case"], task["stratum"], task["replicate"])
    process, offset, gross = _case_process(task["case"])
    rows, history, generator, cadence, contamination = generate_observations(
        inputs, config, stratum, seed, process=process, offset=offset, gross=gross)
    start, stop = float(stratum["start"]), float(stratum["stop"])
    task_rows, ledgers = [], []
    flat_cadence = {f"cadence_{key}": cadence.get(key, "") for key in CADENCE_FLAT_FIELDS}
    cadence_for_csv = dict(cadence)
    cadence_for_csv.pop("events", None)
    cadence_metadata = _json_value(cadence_for_csv)
    cadence_events = cadence.get("events", [])
    contamination_value = _json_value(contamination) if contamination else ""
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
                row = {"family": task["family"], "phase": task["phase"], "case": task["case"],
                       "stratum": task["stratum"], "replicate": task["replicate"], "seed": seed,
                       "truth_seed": benchmark_seed_for(seed, "truth"),
                       "measurement_seed": benchmark_seed_for(seed, "measurement"),
                       "threshold": float(threshold), "extractor": name,
                       "extraction_error": extraction_error, "cadence_metadata": cadence_metadata,
                       "contamination": contamination_value, **flat_cadence, **flat}
                task_rows.append(row)
                if name == "X4" and math.isclose(float(threshold), 10.0):
                    ledgers.append({"family": task["family"], "phase": task["phase"],
                                    "case": task["case"], "stratum": task["stratum"],
                                    "replicate": task["replicate"], "seed": seed, "threshold": 10.0,
                                    "rule": score.get("rule"), "cadence_events": cadence_events,
                                    **ledger})
    return task_rows, ledgers


_INPUTS = None
_CONFIGS = None
_BASE = None


def _init_worker(inputs, configs, base):
    global _INPUTS, _CONFIGS, _BASE
    _INPUTS, _CONFIGS, _BASE = inputs, configs, base


def _worker(task):
    return _run_task(task, _INPUTS, _CONFIGS[task["family"]], _BASE)


def _fields(rows: list[dict[str, Any]]) -> list[str]:
    preferred = ["family", "phase", "case", "stratum", "replicate", "seed", "truth_seed",
                 "measurement_seed", "threshold", "extractor", "rule", "extraction_error",
                 "cadence_metadata"]
    keys = set().union(*(row.keys() for row in rows))
    return preferred + sorted(keys.difference(preferred))


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    freeze = git_commit(args.freeze_commit)
    if (subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != freeze
            or subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)):
        raise ValueError("recovery requires the clean freeze at HEAD")
    inputs, inputs_hash = json.loads(args.inputs.read_text()), sha256(args.inputs)
    parameters, parameters_hash = json.loads(args.parameters.read_text()), sha256(args.parameters)
    qualification_info = validate_qualification(args.qualification, parameters, freeze, inputs_hash, parameters_hash, inputs)
    qualification = qualification_info["receipt"]
    configs = qualified_configurations(parameters, qualification)
    tasks = build_tasks(configs)
    expected = manifest_counts(tasks)
    source_hashes = verify_source_tree(freeze)
    candidate_commit, candidate_hash = candidate_source_hash()
    if not args.output.parent.exists():
        raise FileNotFoundError(f"output parent does not exist: {args.output.parent}")
    args.output.mkdir(parents=False, exist_ok=False)
    base = FREEZE_BASE + freeze
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    receipt = {"status": "running", "validation_base": base, "freeze_commit": freeze,
               "actual_commit": actual, "candidate_ref": CANDIDATE_REF,
               "candidate_commit": candidate_commit, "candidate_file_sha256": candidate_hash,
               "runtime": {"python": sys.version, "platform": platform.platform()},
               "runtime_source_sha256": source_hashes, "inputs_sha256": inputs_hash,
               "parameters_sha256": parameters_hash,
               "selected_config_sha256": parameters_hash,
               "qualification_sha256": sha256(args.qualification), "families": configs,
               "qualification_source_sha256": qualification_info["source_sha256"],
               "calibration_source_commit": qualification_info["calibration_source_commit"],
               "calibration_receipt_sha256": qualification_info["calibration_receipt_sha256"],
               "calibration_attempts_sha256": qualification_info["calibration_attempts_sha256"],
               "grid_sha256": qualification_info["grid_sha256"],
               "input_manifest_sha256": sha256(ROOT / "configs/a04i_inputs.json"),
               "selected_manifest_sha256": sha256(ROOT / "configs/a04i_selected.json"),
               "inputs_path": project_relative(args.inputs), "parameters_path": project_relative(args.parameters),
               "qualification_path": project_relative(args.qualification),
               "expected_histories": expected["histories"], "expected_metric_rows": expected["metric_rows"],
               "expected_ledger_records": expected["ledger_records"]}
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    metrics_path, ledger_path = args.output / "metrics.csv", args.output / "x4_threshold10_ledger.jsonl.gz"
    completed = metric_count = ledger_count = 0
    pool = None
    iterator = ((_run_task(task, inputs, configs[task["family"]], base) for task in tasks)
                if args.workers == 1 else None)
    if iterator is None:
        pool = ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker,
                                   initargs=(inputs, configs, base))
        iterator = pool.map(_worker, tasks)
    try:
        writer = None
        with metrics_path.open("w", newline="") as metrics, ledger_path.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as ledger:
                for rows, records in iterator:
                    if writer is None:
                        writer = csv.DictWriter(metrics, fieldnames=_fields(rows),
                                                lineterminator="\n", extrasaction="raise")
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
    if (completed, metric_count, ledger_count) != (expected["histories"], expected["metric_rows"], expected["ledger_records"]):
        raise RuntimeError("A04i recovery did not complete its fixed manifest")
    if verify_source_tree(freeze) != source_hashes or candidate_source_hash() != (candidate_commit, candidate_hash):
        raise RuntimeError("runtime source identity changed during recovery")
    if (sha256(args.inputs) != inputs_hash or sha256(args.parameters) != parameters_hash
            or sha256(args.qualification) != receipt["qualification_sha256"]):
        raise RuntimeError("recovery inputs changed during execution")
    receipt.update({"status": "completed", "completed_histories": completed,
                    "completed_metric_rows": metric_count, "ledger_records": ledger_count,
                    "metrics_sha256": sha256(metrics_path), "ledger_sha256": sha256(ledger_path),
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
