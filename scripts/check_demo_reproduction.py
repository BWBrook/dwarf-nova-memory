#!/usr/bin/env python3
"""Regenerate the synthetic seed and compare numbers across runtimes."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dnmem.cli import run_demo
from dnmem.simulate import SCENARIOS

REL_TOL = 1e-12
ABS_TOL = 1e-12
FLOAT_COLUMNS = {
    "synthetic_truth.csv": {"onset", "end", "duration", "next_quiescent_gap",
                            "latent_activity", "next_onset_gap"},
    "synthetic_observations.csv": {"time_value", "magnitude", "magnitude_error", "limit_magnitude"},
    "oracle_visibility.csv": set(),
    "oracle_forecasts.csv": {"forecast_origin", "observed_gap", "duration_available_at_origin",
                             "median_gap", "lower_90", "upper_90", "log_score", "pit"},
}


def compare_csv(reference: Path, actual: Path, float_columns: set[str]) -> dict:
    with reference.open(newline="", encoding="utf-8") as left, actual.open(newline="", encoding="utf-8") as right:
        expected, observed = list(csv.reader(left)), list(csv.reader(right))
    if not expected or not observed or expected[0] != observed[0] or len(expected) != len(observed):
        raise ValueError(f"{reference.name}: header or row count changed")
    headers = expected[0]
    if not float_columns <= set(headers):
        raise ValueError(f"{reference.name}: missing expected numeric column")
    changed, max_absolute, max_relative = 0, 0.0, 0.0
    for row_number, (a, b) in enumerate(zip(expected[1:], observed[1:]), start=2):
        if len(a) != len(headers) or len(b) != len(headers):
            raise ValueError(f"{reference.name}:{row_number}: malformed row")
        for column, x, y in zip(headers, a, b):
            if column in float_columns and x != "" and y != "":
                u, v = float(x), float(y)
                if not all(math.isfinite(z) for z in (u, v)) or not math.isclose(u, v, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                    raise ValueError(f"{reference.name}:{row_number}:{column}: numeric mismatch {x} != {y}")
                if x != y:
                    changed += 1
                    difference = abs(u - v)
                    max_absolute = max(max_absolute, difference)
                    max_relative = max(max_relative, difference / max(abs(u), abs(v), 1e-300))
            elif x != y:
                raise ValueError(f"{reference.name}:{row_number}:{column}: exact field changed")
    return {"changed_numeric_cells": changed, "max_absolute_difference": max_absolute,
            "max_relative_difference": max_relative}


def compare_summary(expected, actual, path: str = "summary") -> None:
    if type(expected) is not type(actual):
        raise ValueError(f"{path}: type changed")
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise ValueError(f"{path}: keys changed")
        for key in expected:
            compare_summary(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError(f"{path}: list length changed")
        for i, (a, b) in enumerate(zip(expected, actual)):
            compare_summary(a, b, f"{path}[{i}]")
    elif isinstance(expected, float):
        if not all(math.isfinite(z) for z in (expected, actual)) or not math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            raise ValueError(f"{path}: numeric mismatch")
    elif expected != actual:
        raise ValueError(f"{path}: exact value changed")


def main() -> None:
    reference = ROOT / "outputs/seed_demo"
    expected = json.loads((reference / "summary.json").read_text(encoding="utf-8"))
    files = {f"{scenario}/{table}" for scenario in SCENARIOS for table in FLOAT_COLUMNS}
    if set(expected["sha256_csv"]) != files:
        raise ValueError("seed CSV inventory changed")
    for name in files:
        if hashlib.sha256((reference / name).read_bytes()).hexdigest() != expected["sha256_csv"][name]:
            raise ValueError(f"seed integrity failure: {name}")
    with tempfile.TemporaryDirectory(prefix="dnmem-reproduction-") as temporary:
        output = Path(temporary)
        actual = run_demo(output, seed=expected["seed"], n_events=expected["n_events_per_scenario"])
        if set(actual["sha256_csv"]) != files:
            raise ValueError("regenerated CSV inventory changed")
        comparisons = {name: compare_csv(reference / name, output / name, FLOAT_COLUMNS[Path(name).name])
                       for name in sorted(files)}
        excluded = {"python", "sha256_csv"}
        compare_summary({k: v for k, v in expected.items() if k not in excluded},
                        {k: v for k, v in actual.items() if k not in excluded})
        print(json.dumps({"status": "seed numerically reproduced", "reference_python": expected["python"],
                          "actual_python": actual["python"], "relative_tolerance": REL_TOL,
                          "absolute_tolerance": ABS_TOL, "csv_files": len(files),
                          "byte_identical_csvs": sum(expected["sha256_csv"][n] == actual["sha256_csv"][n] for n in files),
                          "changed_numeric_cells": sum(v["changed_numeric_cells"] for v in comparisons.values()),
                          "max_absolute_difference": max(v["max_absolute_difference"] for v in comparisons.values()),
                          "max_relative_difference": max(v["max_relative_difference"] for v in comparisons.values()),
                          "scope": "synthetic seed reproduction, not astronomical validation"}, indent=2))


if __name__ == "__main__":
    main()
