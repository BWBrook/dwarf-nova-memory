#!/usr/bin/env python3
"""Run the frozen, synthetic X3 validation manifest.

The input cache contains only the already prepared cadence and marginal
calibration.  This runner never passes truth to an extractor and writes a new
output directory for every invocation.
"""

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
import random
import re
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FREEZE_BASE = "a04d-validation|"
CANDIDATE_COMMIT = "c0353c0"
PRE1960_STOP = 2436934.5
THRESHOLDS = (9.5, 10.0, 10.5)
RULES = ("C1_7", "C2_095")
EXTRACTORS = ("X1", "X2", "X3")
CASES = ("primary", "structured", "alternative", "offset", "v1", "early")
EXPECTED_AGGREGATE_CELLS = 324
RUNTIME_SOURCES = (
    "scripts/run_x3_validation.py",
    "src/dnmem/injection_truth.py",
    "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_observe.py",
    "src/dnmem/injection_score.py",
    "src/dnmem/extract.py",
    "src/dnmem/extract_x3.py",
    "src/dnmem/x3_observation.py",
    "src/dnmem/x3_validation_score.py",
    "docs/protocols/a04e-x3-independent-validation-v1.md",
    "configs/a04e_benchmark.json",
    "configs/a04e_inputs.json",
)
QUALIFICATION_SOURCES = (
    "scripts/calibrate_x3_benchmark.py",
    "scripts/run_injection_recovery.py",
    "src/dnmem/injection_truth.py",
    "src/dnmem/injection_truth_v2.py",
    "src/dnmem/injection_observe.py",
    "src/dnmem/x3_observation.py",
    "src/dnmem/validation_morphology.py",
    "src/dnmem/extract.py",
    "src/dnmem/coverage.py",
    "src/dnmem/aavso.py",
    "docs/protocols/a04e-x3-independent-validation-v1.md",
    "configs/a04e_benchmark.json",
    "configs/a04e_inputs.json",
)


def seed_for(base: Any, *labels: Any) -> int:
    """Return the established first-eight-byte SHA256 stream seed."""
    text = "|".join(map(str, (base,) + labels)).encode()
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "big")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite numeric")
    return number


def _hash_map(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{label} must be a non-empty source hash mapping")
    result = {}
    for key, digest in value.items():
        digest = str(digest).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"{label} contains an invalid SHA256 for {key}")
        result[str(key)] = digest
    return result


def _row_time(row: Mapping[str, Any], label: str) -> float:
    values = [row[key] for key in ("t", "JD") if key in row]
    if not values:
        raise ValueError(f"{label} must contain t or JD")
    numbers = [_finite(value, f"{label} {key}")
               for key, value in ((key, row[key]) for key in ("t", "JD") if key in row)]
    if any(number >= PRE1960_STOP for number in numbers):
        raise ValueError(f"{label} contains observations at or after the pre-1960 boundary")
    return numbers[0]


def _check_rows(rows: Any, label: str, source_hashes: Mapping[str, str]) -> None:
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"{label}[{index}] must be a mapping")
        _row_time(row, f"{label}[{index}]")
        for key in ("source_sha256", "source_hash"):
            if key in row and str(row[key]).lower() not in source_hashes.values():
                raise ValueError(f"{label}[{index}] has source hash metadata not in source_sha256")


def validate_cache(payload: Mapping[str, Any]) -> None:
    """Validate the public cache contract without interpreting its magnitudes."""
    for key in ("durations", "gaps", "model", "brightness_model", "source_sha256", "strata"):
        if key not in payload:
            raise ValueError(f"cache missing {key}")
    source_hashes = _hash_map(payload["source_sha256"], "source_sha256")
    if not isinstance(payload["strata"], list) or not payload["strata"]:
        raise ValueError("strata must be a non-empty list")
    for index, stratum in enumerate(payload["strata"]):
        if not isinstance(stratum, Mapping):
            raise ValueError(f"strata[{index}] must be a mapping")
        for key in ("stratum", "start", "stop", "schedule", "days"):
            if key not in stratum:
                raise ValueError(f"strata[{index}] missing {key}")
        start = _finite(stratum["start"], f"strata[{index}] start")
        stop = _finite(stratum["stop"], f"strata[{index}] stop")
        if stop <= start:
            raise ValueError(f"strata[{index}] stop must exceed start")
        _check_rows(stratum["schedule"], f"strata[{index}].schedule", source_hashes)
        days = stratum["days"]
        if not isinstance(days, list):
            raise ValueError(f"strata[{index}].days must be a list")
        for day_index, day in enumerate(days):
            if not isinstance(day, Mapping) or "slots" not in day:
                raise ValueError(f"strata[{index}].days[{day_index}] must contain slots")
            _check_rows(day["slots"], f"strata[{index}].days[{day_index}].slots", source_hashes)
    if not isinstance(payload["model"], Mapping) or not isinstance(payload["brightness_model"], Mapping):
        raise ValueError("model and brightness_model must be mappings")


def load_cache(path: Path) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, Mapping):
        raise ValueError("inputs cache must contain a JSON object")
    validate_cache(payload)
    return dict(payload), _sha256(path)


def load_parameters(path: Path) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, Mapping) or "shape_config" not in payload or "noise_multiplier" not in payload:
        raise ValueError("parameters must contain shape_config and noise_multiplier")
    if not isinstance(payload["shape_config"], Mapping):
        raise ValueError("shape_config must be a mapping")
    noise = _finite(payload["noise_multiplier"], "noise_multiplier")
    if noise <= 0:
        raise ValueError("noise_multiplier must be positive")
    return dict(payload), _sha256(path)


def _required_digest(value: Any, label: str) -> str:
    digest = str(value).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"{label} must be a SHA256 digest")
    return digest


def _validate_qualification_code(receipt: Mapping[str, Any], freeze_commit: str) -> None:
    code = receipt.get("code_sha256")
    if not isinstance(code, Mapping):
        raise ValueError("qualification receipt has no code_sha256 manifest")
    for relative in QUALIFICATION_SOURCES:
        observed = _required_digest(code.get(relative), f"qualification code {relative}")
        expected = _git_blob_hash(freeze_commit, relative)
        if observed != expected:
            raise ValueError(f"qualification code hash does not match freeze blob: {relative}")


def _frozen_manifests(freeze_commit: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifests = []
    for relative in ("configs/a04e_inputs.json", "configs/a04e_benchmark.json"):
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"missing frozen configuration manifest: {relative}")
        value = json.loads(path.read_text())
        if not isinstance(value, Mapping):
            raise ValueError(f"configuration manifest is not an object: {relative}")
        if _sha256(path) != _git_blob_hash(freeze_commit, relative):
            raise ValueError(f"configuration manifest differs from freeze commit: {relative}")
        manifests.append(dict(value))
    return manifests[0], manifests[1]


def validate_qualification(path: Path, parameters: Mapping[str, Any],
                           freeze_commit: str, cache_hash: str | None = None) -> str:
    """Enforce the independent morphology qualification gate."""
    receipt = json.loads(path.read_text())
    if not isinstance(receipt, Mapping):
        raise ValueError("qualification receipt must contain a JSON object")
    if cache_hash is None or not receipt.get("inputs_sha256"):
        raise ValueError("qualification receipt must bind prepared input cache")
    if receipt.get("inputs_sha256") != cache_hash:
        raise ValueError("qualification receipt is for different prepared inputs")
    if receipt.get("mode") != "qualify":
        raise ValueError("qualification receipt is not a qualify run")
    if receipt.get("replicates_per_era_phase") != 12:
        raise ValueError("qualification receipt does not use twelve replicates per era/phase")
    if receipt.get("configuration_count") != 1:
        raise ValueError("qualification receipt must contain exactly one configuration")
    if receipt.get("git_commit") != str(freeze_commit).lower():
        raise ValueError("qualification receipt Git commit does not match freeze commit")
    if receipt.get("dirty") is not False:
        raise ValueError("qualification receipt was produced from a dirty tree")
    _validate_qualification_code(receipt, freeze_commit)
    frozen_inputs, frozen_benchmark = _frozen_manifests(freeze_commit)
    if _required_digest(frozen_inputs.get("prepared_inputs_sha256"), "frozen prepared inputs") != cache_hash:
        raise ValueError("frozen input manifest does not bind the prepared cache")
    calibration_receipt = _required_digest(
        frozen_inputs.get("calibration_receipt_sha256"), "frozen calibration receipt",
    )
    if _required_digest(receipt.get("calibration_receipt_sha256"), "qualification calibration receipt") != calibration_receipt:
        raise ValueError("qualification receipt calibration hash differs from frozen inputs manifest")
    attempts_manifest = _hash_map(
        frozen_inputs.get("calibration_attempts_sha256"), "frozen calibration attempts",
    )
    receipt_attempts = _hash_map(
        receipt.get("calibration_attempts_sha256"), "qualification calibration attempts",
    )
    if receipt_attempts != attempts_manifest:
        raise ValueError("qualification receipt calibration attempts differ from frozen inputs manifest")
    benchmark_json = json.dumps(dict(frozen_benchmark), sort_keys=True, separators=(",", ":"), allow_nan=False)
    parameter_json = json.dumps(dict(parameters), sort_keys=True, separators=(",", ":"), allow_nan=False)
    if parameter_json != benchmark_json:
        raise ValueError("validation parameters differ from frozen benchmark manifest")
    if receipt.get("all_passed") is not True:
        raise ValueError("morphology qualification did not pass")
    selected = receipt.get("selected")
    if not isinstance(selected, Mapping) or not isinstance(selected.get("configuration"), Mapping):
        raise ValueError("qualification receipt has no selected configuration")
    expected_seed = "a04e-qualification|" + str(freeze_commit).lower()
    if receipt.get("seed_base") != expected_seed:
        raise ValueError("qualification seed base does not match freeze commit")
    left = json.dumps(dict(parameters), sort_keys=True, separators=(",", ":"), allow_nan=False)
    right = json.dumps(dict(selected["configuration"]), sort_keys=True, separators=(",", ":"), allow_nan=False)
    if left != right:
        raise ValueError("validation parameters differ from qualified configuration")
    if selected.get("passed") is not True:
        raise ValueError("selected qualification configuration did not pass")
    phases = selected.get("phases")
    if not isinstance(phases, Mapping):
        raise ValueError("selected qualification has no phase results")
    for phase_name in ("random", "state"):
        phase = phases.get(phase_name)
        if not isinstance(phase, Mapping) or phase.get("passed") is not True:
            raise ValueError(f"qualification phase did not pass: {phase_name}")
        no_match = _finite(phase.get("mean_no_match_fraction"), f"{phase_name} no-match fraction")
        if no_match > 0.1:
            raise ValueError(f"qualification phase exceeds no-match bound: {phase_name}")
        qualification = phase.get("qualification")
        if not isinstance(qualification, Mapping) or qualification.get("passed") is not True:
            raise ValueError(f"morphology gates did not pass: {phase_name}")
        gates = qualification.get("gates")
        comparisons = qualification.get("comparisons")
        if (not isinstance(gates, Mapping) or not gates or any(value is not True for value in gates.values())
                or not isinstance(comparisons, Mapping) or not comparisons
                or any(not isinstance(value, Mapping) or value.get("passed") is not True
                       for value in comparisons.values())):
            raise ValueError(f"qualification morphology gate details are incomplete: {phase_name}")
    return _sha256(path)


def _stratum_label(stratum: Mapping[str, Any]) -> str:
    return str(stratum["stratum"]).strip()


def select_strata(payload: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select the four strata from the frozen A04c cache contract."""
    strata = {_stratum_label(s): dict(s) for s in payload["strata"]}
    names = ("1910_1929", "1930_1949", "1950_1959")
    if set(strata) != {"1900_1909", *names}:
        raise ValueError("cache must contain exactly the four frozen calendar strata")
    return {index: strata[name] for index, name in enumerate(names, 1)}, strata["1900_1909"]


def build_tasks(payload: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Build the fixed 7,600-history task manifest in deterministic order."""
    tasks: list[dict[str, Any]] = []
    for rep in range(400):
        thresholds = THRESHOLDS if rep < 200 else (10.0,)
        for era in (1, 2, 3):
            for phase in ("random", "state"):
                tasks.append({"case": "primary", "era": era, "phase": phase,
                              "replicate": rep, "thresholds": thresholds})
    for rep in range(400):
        for era in (1, 2, 3):
            for phase in ("random", "state"):
                tasks.append({"case": "structured", "era": era, "phase": phase,
                              "replicate": rep, "thresholds": (10.0,)})
    for rep in range(200):
        for era in (1, 2, 3):
            for phase in ("random", "state"):
                tasks.append({"case": "alternative", "era": era, "phase": phase,
                              "replicate": rep, "thresholds": THRESHOLDS})
    for case in ("offset", "v1"):
        for rep in range(200):
            for era in (1, 2, 3):
                tasks.append({"case": case, "era": era, "phase": "random",
                              "replicate": rep, "thresholds": (10.0,)})
    for rep in range(200):
        for phase in ("random", "state"):
            tasks.append({"case": "early", "era": 0, "phase": phase,
                          "replicate": rep, "thresholds": THRESHOLDS})
    if len(tasks) != 7600:
        raise AssertionError(f"internal task manifest has {len(tasks)} histories, expected 7600")
    return tasks


def manifest_counts(tasks: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    histories = list(tasks)
    metric_rows = sum(len(tuple(task["thresholds"])) * len(EXTRACTORS) * len(RULES)
                      for task in histories)
    return {"histories": len(histories), "metric_rows": metric_rows}


def _copy_model(model: Mapping[str, Mapping[str, Any]], noise: float = 1.0,
                offsets: Mapping[str, float] | None = None) -> dict[str, dict[str, Any]]:
    result = {}
    for observer in sorted(model):
        params = dict(model[observer])
        params["sigma"] = _finite(params.get("sigma"), f"model {observer} sigma") * noise
        if offsets is not None:
            params["offset"] = offsets[observer]
        result[str(observer)] = params
    return result


def _fixed_offsets(model: Mapping[str, Mapping[str, Any]], seed: int) -> dict[str, float]:
    return {observer: _finite(model[observer].get("offset"), f"model {observer} offset")
            + random.Random(seed_for(seed, "fixed-offset", observer)).gauss(0.0, 0.2)
            for observer in sorted(model)}


def _cadence_metadata(summary: Mapping[str, Any], days: list[Mapping[str, Any]],
                      start: float, stop: float) -> dict[str, Any]:
    observed = summary.get("observed_target_days")
    if observed is None:
        observed = len(days)
    observed = int(observed)
    borrowed = int(summary.get("borrowed_days", 0))
    no_match = int(summary.get("no_match_days", 0))
    same_day = max(0, observed - borrowed - no_match)
    calendar_days = math.ceil(stop) - math.floor(start)
    return {
        "no_match_fraction": float(summary.get("no_match_fraction", no_match / observed if observed else 1.0)),
        "no_match_days": no_match,
        "borrowed_days": borrowed,
        "borrowed_fraction": borrowed / observed if observed else 0.0,
        "same_day_match_days": same_day,
        "same_day_match_fraction": same_day / observed if observed else 0.0,
        "observed_target_days": observed,
        "empty_days_preserved": int(summary.get("empty_days_preserved", calendar_days - observed)),
        "boundary_rows_omitted": int(summary.get("boundary_rows_omitted", 0)),
        "diagnostic_flag": "state_no_match_fraction_ge_0.1"
        if float(summary.get("no_match_fraction", 1.0)) >= 0.1 else "",
    }


def _json_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _flatten_score(score: Mapping[str, Any], *, ledger: bool) -> tuple[dict[str, Any], dict[str, Any] | None]:
    nested_keys = {"pair_records", "operational_confirmation_first_records",
                   "operational_confirmation_emissions"}
    row: dict[str, Any] = {}
    sidecar = None
    for key in sorted(score):
        value = score[key]
        # Pair/emission records are potentially enormous.  They are never
        # duplicated into the summary CSV; only the selected X3 threshold-10
        # arm receives them in the compressed sidecar.
        if key in nested_keys:
            continue
        row[key] = _json_value(value) if isinstance(value, (dict, list, tuple)) else value
    if ledger:
        sidecar = {key: score.get(key) for key in nested_keys}
    return row, sidecar


def _project_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError as exc:
        raise ValueError("receipt paths must be inside the project") from exc


def _git_commit(commit: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
            cwd=ROOT, text=True, stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("freeze-commit must resolve to a Git commit") from exc


def _git_blob_hash(commit: str, relative: str) -> str:
    try:
        content = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"freeze commit does not contain {relative}") from exc
    return hashlib.sha256(content).hexdigest()


def _candidate_source_hash() -> tuple[str, str]:
    current = _sha256(ROOT / "src/dnmem/extract_x3.py")
    try:
        committed = subprocess.check_output(
            ["git", "show", f"{CANDIDATE_COMMIT}:src/dnmem/extract_x3.py"],
            cwd=ROOT,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError("candidate commit does not contain extract_x3.py") from exc
    candidate = hashlib.sha256(committed).hexdigest()
    if current != candidate:
        raise ValueError("working X3 source differs from the c0353c0 candidate")
    return subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{CANDIDATE_COMMIT}^{{commit}}"],
        cwd=ROOT, text=True,
    ).strip(), candidate


def _runtime_source_hashes(freeze_commit: str) -> dict[str, str]:
    """Hash every runtime source and require byte identity with the freeze tree."""
    hashes = {}
    for relative in RUNTIME_SOURCES:
        current_path = ROOT / relative
        current = _sha256(current_path)
        if _git_blob_hash(freeze_commit, relative) != current:
            raise ValueError(f"working source differs from freeze commit: {relative}")
        hashes[relative] = current
    return hashes


def _run_task(task: Mapping[str, Any], payload: Mapping[str, Any], parameters: Mapping[str, Any], base: str):
    from dnmem.extract import x1_vote_episodes, x2_median_hysteresis
    from dnmem.extract_x3 import x3_fitted_episodes
    from dnmem.injection_observe import simulate_rows
    from dnmem.injection_truth import generate_events as generate_v1, magnitudes_at as magnitudes_v1, truth_catalogue as catalogue_v1
    from dnmem.injection_truth import LatentCoefficients
    from dnmem.injection_truth_v2 import ShapeConfig, generate_events as generate_v2, magnitudes_at as magnitudes_v2, truth_catalogue as catalogue_v2
    from dnmem.x3_observation import state_compatible_schedule
    from dnmem.x3_validation_score import score_validation

    era_strata, early = select_strata(payload)
    stratum = early if task["case"] == "early" else era_strata[int(task["era"])]
    start, stop = float(stratum["start"]), float(stratum["stop"])
    task_seed = seed_for(base, task["case"], stratum["stratum"], task["phase"], task["replicate"])
    history_seed = seed_for(task_seed, "truth")
    measurement_seed = seed_for(task_seed, "measurement")
    v2 = task["case"] != "v1"
    if v2:
        process = "alternative" if task["case"] in {"alternative", "structured"} else "null"
        coefficients = (LatentCoefficients(partial_duration_gap=0.0)
                        if task["case"] == "structured" else None)
        history = generate_v2(payload["durations"], payload["gaps"], start, stop, history_seed,
                              process=process, coefficients=coefficients,
                              shape_config=ShapeConfig(**dict(parameters["shape_config"])))
        catalogue = catalogue_v2
        magnitudes = magnitudes_v2
        base_model = payload["brightness_model"]
        model = _copy_model(base_model, float(parameters["noise_multiplier"]))
        if task["case"] == "offset":
            model = _copy_model(base_model, float(parameters["noise_multiplier"]),
                                _fixed_offsets(base_model, seed_for(task_seed, "offsets")))
    else:
        history = generate_v1(payload["durations"], payload["gaps"], start, stop, history_seed, process="null")
        catalogue = catalogue_v1
        magnitudes = magnitudes_v1
        model = _copy_model(payload["model"])

    schedule = list(stratum["schedule"])
    cadence = _cadence_metadata({}, stratum["days"], start, stop)
    if task["phase"] == "state":
        schedule, cadence_summary = state_compatible_schedule(stratum["days"], history, start, stop)
        cadence = _cadence_metadata(cadence_summary, stratum["days"], start, stop)
    magnitudes_at_schedule = magnitudes(history, [float(row.get("t", row["JD"])) for row in schedule])
    rows = simulate_rows(schedule, magnitudes_at_schedule, model, measurement_seed)
    task_rows: list[dict[str, Any]] = []
    task_ledgers: list[dict[str, Any]] = []
    for threshold in tuple(task["thresholds"]):
        truth = list(catalogue(history, float(threshold)))
        extractors = {
            "X1": lambda: x1_vote_episodes(rows, threshold=float(threshold)),
            "X2": lambda: x2_median_hysteresis(rows, low=float(threshold) - .3,
                                                high=float(threshold) + .3, cross=float(threshold)),
            "X3": lambda: x3_fitted_episodes(rows, threshold=float(threshold)),
        }
        for extractor_name in EXTRACTORS:
            extraction_error = ""
            try:
                episodes = extractors[extractor_name]()
            except Exception as exc:  # a failed candidate remains an observed failed row
                episodes = []
                extraction_error = type(exc).__name__
            # A scorer exception is a harness failure, not a candidate result;
            # let it terminate the run rather than manufacture an empty score.
            scores = score_validation(rows, episodes, truth, start, stop, float(threshold))
            for score in scores:
                keep_ledger = extractor_name == "X3" and math.isclose(float(threshold), 10.0)
                flat, ledger = _flatten_score(score, ledger=keep_ledger)
                row = {
                    "case": task["case"], "stratum": stratum["stratum"], "phase": task["phase"],
                    "replicate": task["replicate"], "seed": task_seed,
                    "truth_seed": history_seed, "measurement_seed": measurement_seed,
                    "extractor": extractor_name, "extraction_error": extraction_error,
                    "cadence_no_match_fraction": cadence.get("no_match_fraction"),
                    "cadence_no_match_days": cadence.get("no_match_days"),
                    "cadence_borrowed_days": cadence.get("borrowed_days"),
                    "cadence_borrowed_fraction": cadence.get("borrowed_fraction"),
                    "cadence_same_day_match_days": cadence.get("same_day_match_days"),
                    "cadence_same_day_match_fraction": cadence.get("same_day_match_fraction"),
                    "cadence_observed_target_days": cadence.get("observed_target_days"),
                    "cadence_empty_days_preserved": cadence.get("empty_days_preserved"),
                    "cadence_boundary_rows_omitted": cadence.get("boundary_rows_omitted"),
                    "cadence_diagnostic_flag": cadence.get("diagnostic_flag", ""),
                    **flat,
                }
                task_rows.append(row)
                if ledger is not None:
                    task_ledgers.append({"case": task["case"], "stratum": stratum["stratum"],
                                    "phase": task["phase"], "replicate": task["replicate"],
                                    "seed": task_seed, "truth_seed": history_seed,
                                    "threshold": float(threshold),
                                    "extractor": extractor_name, "rule": score.get("rule"),
                                    **ledger})
    return task_rows, task_ledgers


_WORKER_PAYLOAD: dict[str, Any] | None = None
_WORKER_PARAMETERS: dict[str, Any] | None = None
_WORKER_BASE: str | None = None


def _init_worker(payload: Mapping[str, Any], parameters: Mapping[str, Any], base: str) -> None:
    global _WORKER_PAYLOAD, _WORKER_PARAMETERS, _WORKER_BASE
    _WORKER_PAYLOAD = dict(payload)
    _WORKER_PARAMETERS = dict(parameters)
    _WORKER_BASE = base


def _worker(task: Mapping[str, Any]):
    if _WORKER_PAYLOAD is None or _WORKER_PARAMETERS is None or _WORKER_BASE is None:
        raise RuntimeError("worker was not initialized")
    return _run_task(task, _WORKER_PAYLOAD, _WORKER_PARAMETERS, _WORKER_BASE)


def _metric_fields(rows: list[dict[str, Any]]) -> list[str]:
    preferred = ["case", "stratum", "phase", "replicate", "seed", "truth_seed", "measurement_seed", "threshold",
                 "extractor", "rule", "extraction_error", "cadence_no_match_fraction",
                 "cadence_no_match_days", "cadence_borrowed_days", "cadence_borrowed_fraction",
                 "cadence_same_day_match_days", "cadence_same_day_match_fraction",
                 "cadence_observed_target_days", "cadence_empty_days_preserved",
                 "cadence_boundary_rows_omitted", "cadence_diagnostic_flag"]
    fields = set().union(*(row.keys() for row in rows)) if rows else set()
    return preferred + sorted(fields.difference(preferred))


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not 1 <= int(args.workers) <= 4:
        raise ValueError("workers must be between 1 and 4")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(args.freeze_commit)):
        raise ValueError("freeze-commit must be a full 40-hex commit")
    freeze_commit = str(args.freeze_commit).lower()
    resolved_freeze = _git_commit(freeze_commit)
    if resolved_freeze != freeze_commit:
        raise ValueError("freeze-commit must be the full resolved Git commit")
    payload, cache_hash = load_cache(args.inputs)
    parameters, parameter_hash = load_parameters(args.parameters)
    qualification_hash = validate_qualification(args.qualification, parameters, freeze_commit, cache_hash)
    qualification_payload = json.loads(args.qualification.read_text())
    runtime_sources = _runtime_source_hashes(freeze_commit)
    candidate_commit, candidate_file_hash = _candidate_source_hash()
    tasks = build_tasks(payload)
    expected = manifest_counts(tasks)
    args.output.mkdir(parents=False, exist_ok=False)
    base = FREEZE_BASE + freeze_commit
    started = time.monotonic()
    actual_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    running_receipt = {
        "status": "running",
        "validation_base": base,
        "freeze_commit": freeze_commit,
        "actual_commit": actual_commit,
        "candidate_ref": CANDIDATE_COMMIT,
        "candidate_commit": candidate_commit,
        "candidate_file_sha256": candidate_file_hash,
        "candidate_hash": {"commit": candidate_commit, "extract_x3_sha256": candidate_file_hash},
        "runtime_source_sha256": runtime_sources,
        "inputs_path": _project_path(args.inputs),
        "parameters_path": _project_path(args.parameters),
        "qualification_receipt": _project_path(args.qualification),
        "inputs_sha256": cache_hash,
        "cache_sha256": cache_hash,
        "parameters_sha256": parameter_hash,
        "qualification_receipt_sha256": qualification_hash,
        "calibration_receipt_sha256": qualification_payload["calibration_receipt_sha256"],
        "calibration_attempts_sha256": qualification_payload["calibration_attempts_sha256"],
        "source_sha256": payload["source_sha256"],
        "python": sys.version,
        "platform": platform.platform(),
        "workers": int(args.workers),
        "task_manifest": {"expected_histories": expected["histories"],
                          "expected_metric_rows": expected["metric_rows"],
                          "expected_aggregate_cells": EXPECTED_AGGREGATE_CELLS,
                          "cases": CASES, "thresholds": THRESHOLDS, "rules": RULES,
                          "extractors": EXTRACTORS},
    }
    _write_json(args.output / "receipt.json", running_receipt)
    if int(args.workers) == 1:
        results = (_run_task(task, payload, parameters, base) for task in tasks)
    else:
        pool = ProcessPoolExecutor(max_workers=int(args.workers), initializer=_init_worker,
                                   initargs=(payload, parameters, base))
        results = pool.map(_worker, tasks)
    metrics_path = args.output / "metrics.csv"
    ledger_path = args.output / "x3_threshold10_ledger.jsonl.gz"
    completed = 0
    metric_count = 0
    writer = None
    try:
        with metrics_path.open("w", newline="") as metrics_handle:
            with ledger_path.open("wb") as ledger_raw:
                with gzip.GzipFile(fileobj=ledger_raw, mode="wb", mtime=0, filename="") as compressed:
                    for metric_rows, ledger_rows in results:
                        if writer is None:
                            writer = csv.DictWriter(
                                metrics_handle, fieldnames=_metric_fields(metric_rows),
                                extrasaction="ignore", lineterminator="\n",
                            )
                            writer.writeheader()
                        writer.writerows(metric_rows)
                        for record in ledger_rows:
                            compressed.write((_json_value(record) + "\n").encode())
                        metric_count += len(metric_rows)
                        completed += 1
                        if completed % 20 == 0 or completed == len(tasks):
                            metrics_handle.flush()
                            compressed.flush()
                            print(f"{completed}/{len(tasks)} histories; elapsed {time.monotonic() - started:.1f} s",
                                  flush=True)
    finally:
        if int(args.workers) != 1:
            pool.shutdown()
    if completed != expected["histories"]:
        raise RuntimeError(f"completed {completed} histories, expected {expected['histories']}")
    if metric_count != expected["metric_rows"]:
        raise RuntimeError(f"completed {metric_count} metric rows, expected {expected['metric_rows']}")
    receipt = {
        "status": "completed",
        "validation_base": base,
        "freeze_commit": str(args.freeze_commit).lower(),
        "actual_commit": actual_commit,
        "candidate_ref": CANDIDATE_COMMIT,
        "candidate_commit": candidate_commit,
        "candidate_file_sha256": candidate_file_hash,
        "candidate_hash": {"commit": candidate_commit, "extract_x3_sha256": candidate_file_hash},
        "runtime_source_sha256": runtime_sources,
        "inputs_path": _project_path(args.inputs),
        "parameters_path": _project_path(args.parameters),
        "qualification_receipt": _project_path(args.qualification),
        "inputs_sha256": cache_hash,
        "cache_sha256": cache_hash,
        "parameters_sha256": parameter_hash,
        "qualification_receipt_sha256": qualification_hash,
        "calibration_receipt_sha256": qualification_payload["calibration_receipt_sha256"],
        "calibration_attempts_sha256": qualification_payload["calibration_attempts_sha256"],
        "source_sha256": payload["source_sha256"],
        "python": sys.version,
        "platform": platform.platform(),
        "workers": int(args.workers),
        "task_manifest": {"expected_histories": expected["histories"],
                          "expected_metric_rows": expected["metric_rows"],
                          "expected_aggregate_cells": EXPECTED_AGGREGATE_CELLS,
                          "cases": CASES, "thresholds": THRESHOLDS, "rules": RULES,
                          "extractors": EXTRACTORS},
        "expected_histories": expected["histories"],
        "expected_metric_rows": expected["metric_rows"],
        "expected_aggregate_cells": EXPECTED_AGGREGATE_CELLS,
        "completed_histories": completed,
        "completed_metric_rows": metric_count,
        "completion_count": completed,
        "elapsed_seconds": time.monotonic() - started,
        "metrics_sha256": _sha256(metrics_path),
        "ledger_sha256": _sha256(ledger_path),
        "metrics_hash": _sha256(metrics_path),
        "ledger_hash": _sha256(ledger_path),
        "scope": "synthetic X1/X2/X3 validation; no real-star forecast score",
    }
    _write_json(args.output / "receipt.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
