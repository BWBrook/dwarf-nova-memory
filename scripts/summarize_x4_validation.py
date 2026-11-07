#!/usr/bin/env python3
"""Summarize and gate a completed A04g X4 validation run."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

import run_x4_validation as runner
from summarize_x3_validation import _cell_summary

KEYS = ("case", "family", "stratum", "phase", "threshold", "extractor", "rule")
GATE_METRICS = (
    "onset_effective_coverage", "end_effective_coverage",
    "short_outside_mar_may_completeness", "false_confirmed_per_year",
    "operational_confirmation_unsafe_per_year", "total_bias",
    "operational_confirmation_premature_fraction",
    "operational_confirmation_missing_fraction",
)


def _number(value: Any) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _validate_receipt(receipt: dict[str, Any], directory: Path) -> None:
    if receipt.get("status") != "completed":
        raise ValueError("run receipt is not completed")
    for key, expected in (("expected_histories", 16600), ("expected_metric_rows", 51800),
                          ("completed_histories", 16600), ("completed_metric_rows", 51800),
                          ("expected_ledger_records", 33200), ("ledger_records", 33200)):
        if receipt.get(key) != expected:
            raise ValueError(f"receipt {key} is not {expected}")
    if receipt.get("candidate_ref") != runner.CANDIDATE_REF:
        raise ValueError("receipt candidate reference differs")
    metrics = directory / "metrics.csv"
    ledger = directory / "x4_threshold10_ledger.jsonl.gz"
    if receipt.get("metrics_sha256") != runner.sha256(metrics):
        raise ValueError("metrics.csv does not match receipt hash")
    if receipt.get("ledger_sha256") != runner.sha256(ledger):
        raise ValueError("X4 ledger does not match receipt hash")
    freeze = runner.git_commit(str(receipt.get("freeze_commit", "")))
    if receipt.get("validation_base") != runner.FREEZE_BASE + freeze:
        raise ValueError("validation seed namespace differs from freeze")
    runtime = receipt.get("runtime_source_sha256")
    if not isinstance(runtime, dict):
        raise ValueError("receipt has no runtime source manifest")
    observed_runtime = runner.verify_source_tree(freeze, runtime)
    if observed_runtime != runtime:
        raise ValueError("receipt runtime source manifest does not match frozen bytes")
    if runtime.get("scripts/summarize_x4_validation.py") != runner.sha256(Path(__file__)):
        raise ValueError("decision source differs from run receipt")
    candidate_commit, candidate_hash = runner.candidate_source_hash()
    if receipt.get("candidate_commit") != candidate_commit or receipt.get("candidate_file_sha256") != candidate_hash:
        raise ValueError("candidate source differs from run receipt")
    for field, expected_path in (("inputs_path", "inputs_sha256"),
                                 ("parameters_path", "parameters_sha256"),
                                 ("qualification_path", "qualification_sha256")):
        relative = receipt.get(field)
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError(f"receipt {field} is not a project-relative path")
        path = (runner.ROOT / relative).resolve()
        try:
            path.relative_to(runner.ROOT)
        except ValueError as exc:
            raise ValueError(f"receipt {field} escapes the project") from exc
        if receipt.get(expected_path) != runner.sha256(path):
            raise ValueError(f"receipt {expected_path} does not match {field}")
    for field, relative in (("input_manifest_sha256", "configs/a04g_inputs.json"),
                            ("benchmark_manifest_sha256", "configs/a04g_benchmark.json")):
        if receipt.get(field) != runner.sha256(runner.ROOT / relative):
            raise ValueError(f"receipt {field} does not match the frozen manifest")
    config = json.loads((runner.ROOT / "configs/a04g_inputs.json").read_text())
    if receipt.get("calibration_receipt_sha256") != config.get("calibration_receipt_sha256"):
        raise ValueError("receipt calibration chain differs from the frozen manifest")
    if runner._hash_map(receipt.get("calibration_attempts_sha256"), "receipt calibration attempts") != runner._hash_map(
            config.get("calibration_attempts_sha256"), "manifest calibration attempts"):
        raise ValueError("receipt calibration attempts differ from the frozen manifest")


def _key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(row[name] for name in KEYS)


def _validate_rows(rows: list[dict[str, Any]], receipt: dict[str, Any]) -> None:
    expected = set()
    for task in runner.build_tasks():
        base = (task["case"], task["family"], task["stratum"], task["phase"], task["replicate"])
        for threshold in task["thresholds"]:
            for rule in runner.RULES:
                expected.add((*base, str(float(threshold)), "X4", rule))
                for finder in task["reference_extractors"]:
                    expected.add((*base, "10.0", finder, rule))
    seen = set()
    base = receipt["validation_base"]
    for number, row in enumerate(rows, start=2):
        if any(not row.get(field) for field in KEYS):
            raise ValueError(f"metrics row {number} has an incomplete key")
        threshold = _number(row["threshold"])
        if threshold not in runner.THRESHOLDS:
            raise ValueError(f"metrics row {number} has an invalid threshold")
        replicate = int(row["replicate"])
        key = (row["case"], row["family"], row["stratum"], row["phase"], replicate,
               str(float(threshold)), row["extractor"], row["rule"])
        if key in seen:
            raise ValueError(f"duplicate metrics row {number}")
        seen.add(key)
        if row["extractor"] not in runner.FINDERS or row["rule"] not in runner.RULES:
            raise ValueError(f"metrics row {number} has an invalid finder/rule")
        seed = runner.seed_for(base, row["case"], row["family"], row["stratum"], row["phase"], replicate)
        expected_seeds = (seed, runner.seed_for(seed, "truth"), runner.seed_for(seed, "measurement"))
        observed = tuple(int(row[field]) for field in ("seed", "truth_seed", "measurement_seed"))
        if observed != expected_seeds:
            raise ValueError(f"seed stream mismatch at row {number}")
    if seen != expected:
        raise ValueError(f"metrics grid mismatch: {len(expected - seen)} missing, {len(seen - expected)} extra")
    heavy = {"pair_records", "operational_confirmation_first_records", "operational_confirmation_emissions"}
    if heavy.intersection(rows[0].keys() if rows else ()):
        raise ValueError("heavy pair/emission arrays must not be in metrics.csv")


def _cell(key: tuple[str, ...], rows: list[dict[str, Any]]) -> dict[str, Any]:
    old_key = (key[0], key[2], key[3], key[4], key[5], key[6])
    summary = _cell_summary(old_key, rows)
    summary["family"] = key[1]
    summary = {"case": key[0], "family": key[1], "stratum": key[2], "phase": key[3],
               "threshold": key[4], "extractor": key[5], "rule": key[6],
               **{k: v for k, v in summary.items() if k not in {
                   "case", "stratum", "phase", "threshold", "extractor", "rule"}}}
    criteria = dict(summary["criteria"])
    if key[3] == "diverse":
        no_match = summary["metrics"].get("cadence_no_match_fraction", {})
        criteria["diverse_cadence_no_match"] = (
            "PASS" if no_match.get("estimate") is not None and no_match["estimate"] <= .10
            else "INCONCLUSIVE")
    if key[0] == "gross" and key[5] == "X4":
        criteria = {name: criteria[name] for name in (
            "false_confirmed_per_year", "operational_confirmation_unsafe_per_year")}
    if summary["extraction_errors"]:
        verdict = "FAIL"
    elif any(value == "FAIL" for value in criteria.values()):
        verdict = "FAIL"
    elif all(value == "PASS" for value in criteria.values()):
        verdict = "PASS"
    else:
        verdict = "INCONCLUSIVE"
    summary["criteria"] = criteria
    summary["verdict"] = verdict
    return summary


def candidate_decisions(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for rule in runner.RULES:
        regular = [cell for cell in cells if cell["extractor"] == "X4" and cell["rule"] == rule
                   and cell["threshold"] == "10.0" and cell["case"] in ("primary", "structured")]
        gross = [cell for cell in cells if cell["extractor"] == "X4" and cell["rule"] == rule
                 and cell["threshold"] == "10.0" and cell["case"] == "gross"]
        selected = regular + gross
        statuses = [cell["verdict"] for cell in selected]
        decisions.append({"extractor": "X4", "rule": rule, "required_regular_cells": 24,
                          "required_gross_cells": 6, "observed_regular_cells": len(regular),
                          "observed_gross_cells": len(gross), "cell_verdicts": statuses,
                          "verdict": "PASS" if len(regular) == 24 and len(gross) == 6
                          and all(status == "PASS" for status in statuses)
                          else "FAIL" if any(status == "FAIL" for status in statuses) else "INCONCLUSIVE"})
    return decisions


def summarize(directory: Path, output: Path) -> dict[str, Any]:
    directory, output = Path(directory), Path(output)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    receipt = json.loads((directory / "receipt.json").read_text())
    _validate_receipt(receipt, directory)
    with (directory / "metrics.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 51800:
        raise ValueError(f"metrics.csv has {len(rows)} rows, expected 51800")
    _validate_rows(rows, receipt)
    with gzip.open(directory / "x4_threshold10_ledger.jsonl.gz", "rt", encoding="utf-8") as handle:
        ledger_records = sum(1 for line in handle if line.strip())
    if ledger_records != 33200:
        raise ValueError(f"X4 ledger has {ledger_records} records, expected 33200")
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_key(row)].append(row)
    cells = [_cell(key, grouped[key]) for key in sorted(grouped)]
    decisions = candidate_decisions(cells)
    selected_rule = next((rule for rule in runner.RULES
                          if next(item for item in decisions if item["rule"] == rule)["verdict"] == "PASS"), None)
    summary = {"scope": "A04g independent X4 validation; synthetic histories only",
               "run_receipt": receipt, "input_metrics_sha256": runner.sha256(directory / "metrics.csv"),
               "summarizer_source_sha256": runner.sha256(Path(__file__)),
               "cells": cells, "candidate_decisions": decisions,
               "selected": {"extractor": "X4", "rule": selected_rule} if selected_rule else None,
               "expected_grid_rows": 51800, "expected_ledger_records": 33200}
    output.mkdir(parents=False, exist_ok=False)
    (output / "fullsummary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    fields = list(KEYS) + ["replicates", "extraction_errors", "verdict", "selected_rule"]
    for metric in GATE_METRICS:
        fields.extend((f"{metric}_estimate", f"{metric}_lower", f"{metric}_upper"))
    with (output / "reviewed_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for cell in cells:
            row = {key: cell[key] for key in KEYS}
            row.update({"replicates": cell["replicates"], "extraction_errors": cell["extraction_errors"],
                        "verdict": cell["verdict"], "selected_rule": selected_rule or ""})
            for metric in GATE_METRICS:
                values = cell["metrics"].get(metric, {})
                row[f"{metric}_estimate"] = values.get("estimate")
                row[f"{metric}_lower"] = values.get("lower")
                row[f"{metric}_upper"] = values.get("upper")
            writer.writerow(row)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.run_directory, args.output)


if __name__ == "__main__":
    main()
