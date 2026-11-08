#!/usr/bin/env python3
"""Validate and summarize a completed A04i joint recovery run."""

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
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import run_joint_recovery as runner
from summarize_x3_validation import _cell_summary

KEYS = ("family", "phase", "case", "stratum", "threshold", "extractor", "rule")
GATE_METRICS = (
    "onset_effective_coverage", "end_effective_coverage",
    "short_outside_mar_may_completeness", "false_confirmed_per_year",
    "operational_confirmation_unsafe_per_year", "total_bias",
    "operational_confirmation_premature_fraction",
    "operational_confirmation_missing_fraction",
)


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _validate_receipt(receipt: dict[str, Any], directory: Path) -> None:
    if receipt.get("status") != "completed":
        raise ValueError("run receipt is not completed")
    families = receipt.get("families")
    if not isinstance(families, dict) or not families:
        raise ValueError("receipt has no qualified families")
    tasks = runner.build_tasks(families)
    expected = runner.manifest_counts(tasks)
    for key in ("histories", "metric_rows", "ledger_records"):
        if receipt.get(f"expected_{key}") != expected[key] or receipt.get(
                f"completed_{key}", receipt.get(key)) != expected[key]:
            raise ValueError(f"receipt {key} count does not match the dynamic manifest")
    if receipt.get("candidate_ref") != runner.CANDIDATE_REF:
        raise ValueError("receipt candidate reference differs")
    metrics = directory / "metrics.csv"
    ledger = directory / "x4_threshold10_ledger.jsonl.gz"
    if receipt.get("metrics_sha256") != runner.sha256(metrics):
        raise ValueError("metrics.csv does not match receipt hash")
    if receipt.get("ledger_sha256") != runner.sha256(ledger):
        raise ValueError("ledger does not match receipt hash")
    freeze = runner.git_commit(str(receipt.get("freeze_commit", "")))
    if receipt.get("validation_base") != runner.FREEZE_BASE + freeze:
        raise ValueError("validation seed namespace differs from freeze")
    runtime = receipt.get("runtime_source_sha256")
    if (not isinstance(runtime, dict) or set(runtime) != set(runner.RUNTIME_SOURCES)
            or runner.verify_source_tree(freeze, runtime) != runtime):
        raise ValueError("receipt runtime source manifest differs from frozen bytes")
    if runtime.get("scripts/summarize_joint_recovery.py") != runner.sha256(Path(__file__)):
        raise ValueError("decision source differs from run receipt")
    candidate_commit, candidate_hash = runner.candidate_source_hash()
    if receipt.get("candidate_commit") != candidate_commit or receipt.get("candidate_file_sha256") != candidate_hash:
        raise ValueError("candidate source differs from receipt")
    if receipt.get("input_manifest_sha256") != runner.sha256(runner.ROOT / "configs/a04i_inputs.json"):
        raise ValueError("input manifest differs from receipt")
    if receipt.get("selected_manifest_sha256") != runner.sha256(runner.ROOT / "configs/a04i_selected.json"):
        raise ValueError("selected configuration manifest differs from receipt")
    for field, digest_field in (("inputs_path", "inputs_sha256"),
                                ("parameters_path", "parameters_sha256"),
                                ("qualification_path", "qualification_sha256")):
        relative = receipt.get(field)
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError(f"receipt {field} is not project-relative")
        path = (runner.ROOT / relative).resolve()
        try:
            path.relative_to(runner.ROOT)
        except ValueError as exc:
            raise ValueError(f"receipt {field} escapes the project") from exc
        if receipt.get(digest_field) != runner.sha256(path):
            raise ValueError(f"receipt {digest_field} does not match {field}")


def _validate_rows(rows: list[dict[str, Any]], receipt: dict[str, Any]) -> None:
    tasks = runner.build_tasks(receipt["families"])
    expected = runner.expected_grid(tasks)
    seen = set()
    base = receipt["validation_base"]
    for number, row in enumerate(rows, start=2):
        if any(not row.get(field) for field in KEYS):
            raise ValueError(f"metrics row {number} has an incomplete key")
        threshold = _number(row["threshold"])
        if threshold not in runner.THRESHOLDS:
            raise ValueError(f"metrics row {number} has an invalid threshold")
        replicate = int(row["replicate"])
        key = (row["family"], row["phase"], row["case"], row["stratum"],
               replicate, str(float(threshold)), row["extractor"], row["rule"])
        if key in seen:
            raise ValueError(f"duplicate metrics row {number}")
        seen.add(key)
        if row["extractor"] not in runner.FINDERS or row["rule"] not in runner.RULES:
            raise ValueError(f"metrics row {number} has an invalid finder/rule")
        seed = runner.seed_for(base, row["family"], row["case"], row["stratum"], replicate)
        expected_seeds = (seed, runner.seed_for(seed, "truth"), runner.seed_for(seed, "measurement"))
        observed = tuple(int(row[field]) for field in ("seed", "truth_seed", "measurement_seed"))
        if observed != expected_seeds:
            raise ValueError(f"seed stream mismatch at row {number}")
        if not row.get("cadence_metadata"):
            raise ValueError(f"metrics row {number} has no cadence metadata")
    if seen != expected:
        raise ValueError(f"metrics grid mismatch: {len(expected - seen)} missing, {len(seen - expected)} extra")
    heavy = {"pair_records", "operational_confirmation_first_records", "operational_confirmation_emissions"}
    if heavy.intersection(rows[0].keys() if rows else ()):
        raise ValueError("heavy pair/emission arrays must not be in metrics.csv")


def _validate_ledger(path: Path, receipt: dict[str, Any]) -> None:
    tasks = runner.build_tasks(receipt["families"])
    expected = {(t["family"], t["phase"], t["case"], t["stratum"], t["replicate"], rule)
                for t in tasks for rule in runner.RULES}
    seen = set()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            key = tuple(record[name] for name in ("family", "phase", "case", "stratum", "replicate", "rule"))
            if key not in expected or key in seen or record["threshold"] != 10.0:
                raise ValueError("duplicate, unknown or non-threshold-10 ledger record")
            if record["seed"] != runner.seed_for(receipt["validation_base"], key[0], key[2], key[3], key[4]):
                raise ValueError("ledger seed differs from its history")
            for name in ("pair_records", "operational_confirmation_first_records",
                         "operational_confirmation_emissions", "cadence_events"):
                if not isinstance(record.get(name), list):
                    raise ValueError("ledger is missing a retained evidence array")
            seen.add(key)
    if seen != expected:
        raise ValueError("ledger does not contain the exact two-rule history grid")


def _cell(key: tuple[str, ...], rows: list[dict[str, Any]]) -> dict[str, Any]:
    old_key = (key[2], key[3], key[1], key[4], key[5], key[6])
    summary = _cell_summary(old_key, rows)
    summary = {"family": key[0], "phase": key[1], "case": key[2], "stratum": key[3],
               "threshold": key[4], "extractor": key[5], "rule": key[6],
               **{k: v for k, v in summary.items() if k not in {
                   "case", "stratum", "phase", "threshold", "extractor", "rule"}}}
    if key[2] == "gross" and key[5] == "X4":
        summary["criteria"] = {name: summary["criteria"][name] for name in (
            "false_confirmed_per_year", "operational_confirmation_unsafe_per_year")}
    criteria = summary["criteria"]
    if summary["extraction_errors"]:
        verdict = "FAIL"
    elif any(value == "FAIL" for value in criteria.values()):
        verdict = "FAIL"
    elif all(value == "PASS" for value in criteria.values()):
        verdict = "PASS"
    else:
        verdict = "INCONCLUSIVE"
    summary["verdict"] = verdict
    summary["gate_criteria"] = tuple(criteria)
    return summary


def candidate_decisions(cells: list[dict[str, Any]], families: list[str]) -> list[dict[str, Any]]:
    decisions = []
    for family in families:
        for rule in runner.RULES:
            ordinary = [cell for cell in cells if cell["family"] == family and cell["rule"] == rule
                        and cell["extractor"] == "X4" and cell["threshold"] == "10.0"
                        and cell["case"] in ("primary", "structured")]
            gross = [cell for cell in cells if cell["family"] == family and cell["rule"] == rule
                     and cell["extractor"] == "X4" and cell["threshold"] == "10.0"
                     and cell["case"] == "gross"]
            selected = ordinary + gross
            statuses = [cell["verdict"] for cell in selected]
            decisions.append({"family": family, "rule": rule, "required_ordinary_cells": 6,
                              "required_gross_cells": 3, "observed_ordinary_cells": len(ordinary),
                              "observed_gross_cells": len(gross), "cell_verdicts": statuses,
                              "verdict": "PASS" if len(ordinary) == 6 and len(gross) == 3
                              and all(status == "PASS" for status in statuses)
                              else "FAIL" if any(status == "FAIL" for status in statuses) else "INCONCLUSIVE"})
    for rule in runner.RULES:
        family_decisions = [item for item in decisions if item["rule"] == rule]
        decisions.append({"scope": "global", "rule": rule, "required_families": len(families),
                          "family_verdicts": [item["verdict"] for item in family_decisions],
                          "verdict": "PASS" if len(family_decisions) == len(families)
                          and all(item["verdict"] == "PASS" for item in family_decisions)
                          else "FAIL" if any(item["verdict"] == "FAIL" for item in family_decisions)
                          else "INCONCLUSIVE"})
    return decisions


def summarize(directory: Path, output: Path) -> dict[str, Any]:
    directory, output = Path(directory), Path(output)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    receipt = json.loads((directory / "receipt.json").read_text())
    _validate_receipt(receipt, directory)
    with (directory / "metrics.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = runner.manifest_counts(runner.build_tasks(receipt["families"]))
    if len(rows) != expected["metric_rows"]:
        raise ValueError("metrics.csv row count differs from the dynamic manifest")
    _validate_rows(rows, receipt)
    _validate_ledger(directory / "x4_threshold10_ledger.jsonl.gz", receipt)
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[name] for name in KEYS)].append(row)
    cells = [_cell(key, grouped[key]) for key in sorted(grouped)]
    decisions = candidate_decisions(cells, sorted(receipt["families"]))
    selected_rule = next((rule for rule in runner.RULES
                          if next(item for item in decisions if item.get("scope") == "global" and item["rule"] == rule)["verdict"] == "PASS"), None)
    summary = {"scope": "A04i conditional retrospective joint-waveform recovery; synthetic histories only",
               "run_receipt": receipt, "input_metrics_sha256": runner.sha256(directory / "metrics.csv"),
               "summarizer_source_sha256": runner.sha256(Path(__file__)), "cells": cells,
               "candidate_decisions": decisions,
               "selected": {"extractor": "X4", "rule": selected_rule} if selected_rule else None,
               "expected_grid_rows": expected["metric_rows"], "expected_ledger_records": expected["ledger_records"]}
    output.mkdir(parents=False, exist_ok=False)
    (output / "fullsummary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    fields = list(KEYS) + ["replicates", "extraction_errors", "criteria_json", "verdict", "selected_rule"]
    for metric in GATE_METRICS:
        fields.extend((f"{metric}_estimate", f"{metric}_lower", f"{metric}_upper"))
    with (output / "reviewed_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for cell in cells:
            output_row = {key: cell[key] for key in KEYS}
            output_row.update({"replicates": cell["replicates"], "extraction_errors": cell["extraction_errors"],
                               "criteria_json": json.dumps(cell["criteria"], sort_keys=True),
                               "verdict": cell["verdict"], "selected_rule": selected_rule or ""})
            for metric in GATE_METRICS:
                values = cell["metrics"].get(metric, {})
                output_row[f"{metric}_estimate"] = values.get("estimate")
                output_row[f"{metric}_lower"] = values.get("lower")
                output_row[f"{metric}_upper"] = values.get("upper")
            writer.writerow(output_row)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.run_directory, args.output)


if __name__ == "__main__":
    main()
