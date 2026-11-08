#!/usr/bin/env python3

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OUT = Path(
    sys.argv[2] if len(sys.argv) > 2
    else ROOT / "outputs/a04i_recovery_independent_audit"
).resolve()
RUN = ROOT / "outputs/a04i_recovery_20261108"
ERAS = ("1910_1929", "1930_1949", "1950_1959")
RULES = ("C1_7", "C2_095")
CASES = {"primary": 400, "structured": 400, "gross": 400,
         "alternative": 200, "offset": 200}
REFERENCE_EXTRACTORS = ("X1", "X2", "X3")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def seed_for(base: object, *labels: object) -> int:
    payload = "|".join(map(str, (base,) + labels)).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def git(*args: str, binary: bool = False):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=not binary
    ).strip() if not binary else subprocess.check_output(["git", *args], cwd=ROOT)


def thresholds(case: str, replicate: int) -> tuple[float, ...]:
    if case == "primary" and replicate < 200:
        return (9.5, 10.0, 10.5)
    if case == "alternative":
        return (9.5, 10.0, 10.5)
    return (10.0,)


receipt = json.loads((RUN / "receipt.json").read_text())
families = receipt["families"]
base = receipt["validation_base"]

tasks: list[tuple[str, str, str, str, int]] = []
expected_metrics: set[tuple[object, ...]] = set()
expected_ledger: set[tuple[object, ...]] = set()
for family, configuration in sorted(families.items()):
    phase = str(configuration["phase"])
    for case, count in CASES.items():
        for era in ERAS:
            for replicate in range(count):
                task = (family, phase, case, era, replicate)
                tasks.append(task)
                for rule in RULES:
                    expected_ledger.add((*task, rule))
                for threshold in thresholds(case, replicate):
                    for rule in RULES:
                        expected_metrics.add((*task, str(float(threshold)), "X4", rule))
                        if threshold == 10.0 and replicate < 25:
                            for extractor in REFERENCE_EXTRACTORS:
                                expected_metrics.add((*task, "10.0", extractor, rule))

hash_checks: dict[str, dict[str, object]] = {}


def add_hash(label: str, path: Path, expected: str) -> None:
    actual = sha256_file(path)
    hash_checks[label] = {
        "path": str(path.relative_to(ROOT)), "expected": expected,
        "actual": actual, "match": actual == expected,
    }


add_hash("metrics", RUN / "metrics.csv", receipt["metrics_sha256"])
add_hash("ledger", RUN / "x4_threshold10_ledger.jsonl.gz", receipt["ledger_sha256"])
for path_field, digest_field in (
    ("inputs_path", "inputs_sha256"),
    ("parameters_path", "parameters_sha256"),
    ("qualification_path", "qualification_sha256"),
):
    add_hash(path_field, ROOT / receipt[path_field], receipt[digest_field])
add_hash(
    "input_manifest", ROOT / "configs/a04i_inputs.json",
    receipt["input_manifest_sha256"],
)
add_hash(
    "selected_manifest", ROOT / "configs/a04i_selected.json",
    receipt["selected_manifest_sha256"],
)

freeze = receipt["freeze_commit"]
runtime_checks: dict[str, dict[str, object]] = {}
for relative, expected in sorted(receipt["runtime_source_sha256"].items()):
    path = ROOT / relative
    current = sha256_file(path)
    frozen = hashlib.sha256(git("show", f"{freeze}:{relative}", binary=True)).hexdigest()
    runtime_checks[relative] = {
        "expected": expected, "current": current, "frozen": frozen,
        "match": expected == current == frozen,
    }

candidate_path = ROOT / "src/dnmem/extract_x4.py"
candidate_current = sha256_file(candidate_path)
candidate_frozen = hashlib.sha256(
    git("show", f"{receipt['candidate_commit']}:src/dnmem/extract_x4.py", binary=True)
).hexdigest()
candidate_check = {
    "ref": receipt["candidate_ref"],
    "commit": receipt["candidate_commit"],
    "resolved_commit": git("rev-parse", f"{receipt['candidate_ref']}^{{commit}}"),
    "receipt_sha256": receipt["candidate_file_sha256"],
    "current_sha256": candidate_current,
    "candidate_commit_sha256": candidate_frozen,
}
candidate_check["match"] = (
    candidate_check["resolved_commit"] == candidate_check["commit"]
    and candidate_current == candidate_frozen == receipt["candidate_file_sha256"]
)

seen_metrics: set[tuple[object, ...]] = set()
metric_task_seeds: dict[tuple[object, ...], tuple[int, int, int]] = {}
metric_errors = 0
metric_rows = 0
seed_mismatches = 0
cadence_metadata_missing = 0
with (RUN / "metrics.csv").open(newline="") as handle:
    reader = csv.DictReader(handle)
    heavy_fields = {
        "pair_records", "operational_confirmation_first_records",
        "operational_confirmation_emissions",
    }
    heavy_fields_absent = not heavy_fields.intersection(reader.fieldnames or ())
    for row in reader:
        metric_rows += 1
        replicate = int(row["replicate"])
        threshold = str(float(row["threshold"]))
        task = (
            row["family"], row["phase"], row["case"], row["stratum"], replicate,
        )
        key = (*task, threshold, row["extractor"], row["rule"])
        if key in seen_metrics:
            raise RuntimeError(f"duplicate metric key: {key}")
        seen_metrics.add(key)
        seed = seed_for(base, task[0], task[2], task[3], task[4])
        expected_seeds = (seed, seed_for(seed, "truth"), seed_for(seed, "measurement"))
        observed_seeds = tuple(int(row[name]) for name in (
            "seed", "truth_seed", "measurement_seed"
        ))
        if observed_seeds != expected_seeds:
            seed_mismatches += 1
        prior = metric_task_seeds.setdefault(task, observed_seeds)
        if prior != observed_seeds:
            seed_mismatches += 1
        if not row.get("cadence_metadata"):
            cadence_metadata_missing += 1
        if row.get("extraction_error", "").strip().casefold() not in {
            "", "0", "false", "none", "null"
        }:
            metric_errors += 1

seen_ledger: set[tuple[object, ...]] = set()
ledger_records = 0
ledger_seed_mismatches = 0
ledger_array_failures = 0
with gzip.open(RUN / "x4_threshold10_ledger.jsonl.gz", "rt", encoding="utf-8") as handle:
    for line in handle:
        ledger_records += 1
        record = json.loads(line)
        key = tuple(record[name] for name in (
            "family", "phase", "case", "stratum", "replicate", "rule"
        ))
        if key in seen_ledger:
            raise RuntimeError(f"duplicate ledger key: {key}")
        seen_ledger.add(key)
        expected_seed = seed_for(base, key[0], key[2], key[3], key[4])
        if record.get("seed") != expected_seed:
            ledger_seed_mismatches += 1
        if record.get("threshold") != 10.0:
            raise RuntimeError(f"non-10 threshold ledger record: {key}")
        if not all(isinstance(record.get(name), list) for name in (
            "pair_records", "operational_confirmation_first_records",
            "operational_confirmation_emissions", "cadence_events",
        )):
            ledger_array_failures += 1

receipt_count_checks = {
    "expected_histories": receipt.get("expected_histories") == len(tasks),
    "completed_histories": receipt.get("completed_histories") == len(tasks),
    "expected_metric_rows": receipt.get("expected_metric_rows") == len(expected_metrics),
    "completed_metric_rows": receipt.get("completed_metric_rows") == len(expected_metrics),
    "expected_ledger_records": receipt.get("expected_ledger_records") == len(expected_ledger),
    "ledger_records": receipt.get("ledger_records") == len(expected_ledger),
}
grid_checks = {
    "metric_row_count": metric_rows == len(expected_metrics),
    "metric_exact_grid": seen_metrics == expected_metrics,
    "ledger_record_count": ledger_records == len(expected_ledger),
    "ledger_exact_grid": seen_ledger == expected_ledger,
    "metric_seed_mismatches": seed_mismatches == 0,
    "ledger_seed_mismatches": ledger_seed_mismatches == 0,
    "metric_extraction_errors": metric_errors == 0,
    "cadence_metadata_complete": cadence_metadata_missing == 0,
    "ledger_arrays_complete": ledger_array_failures == 0,
    "heavy_fields_absent_from_metrics": heavy_fields_absent,
}

head = git("rev-parse", "HEAD")
receipt_contract = {
    "status_completed": receipt.get("status") == "completed",
    "head_is_freeze": head == freeze,
    "actual_commit_is_freeze": receipt.get("actual_commit") == freeze,
    "validation_base": base == f"a04i-validation|{freeze}",
    "single_eligible_family": sorted(families) == ["v2-phase"],
}

all_pass = all(item["match"] for item in hash_checks.values())
all_pass = all_pass and all(item["match"] for item in runtime_checks.values())
all_pass = all_pass and bool(candidate_check["match"])
all_pass = all_pass and all(receipt_count_checks.values())
all_pass = all_pass and all(grid_checks.values())
all_pass = all_pass and all(receipt_contract.values())

result = {
    "scope": "independent integrity audit; no recovery verdict read or computed here",
    "head": head,
    "freeze": freeze,
    "counts": {
        "expected_histories": len(tasks), "expected_metric_rows": len(expected_metrics),
        "observed_metric_rows": metric_rows, "expected_ledger_records": len(expected_ledger),
        "observed_ledger_records": ledger_records,
    },
    "receipt_contract": receipt_contract,
    "receipt_count_checks": receipt_count_checks,
    "hash_checks": hash_checks,
    "runtime_source_checks": runtime_checks,
    "candidate_check": candidate_check,
    "grid_checks": grid_checks,
    "integrity_pass": all_pass,
}
(OUT / "integrity_audit.json").write_text(
    json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
)

print("A04i independent recovery integrity audit")
print(f"HEAD={head}")
print(f"freeze={freeze}")
print(f"histories={len(tasks)} metrics={metric_rows} ledger={ledger_records}")
print(f"metrics_exact_grid={grid_checks['metric_exact_grid']}")
print(f"ledger_exact_grid={grid_checks['ledger_exact_grid']}")
print(f"seed_mismatches={seed_mismatches + ledger_seed_mismatches}")
print(f"extraction_errors={metric_errors}")
print(f"all_hashes_match={all(item['match'] for item in hash_checks.values())}")
print(f"all_runtime_sources_match={all(item['match'] for item in runtime_checks.values())}")
print(f"candidate_identity_match={candidate_check['match']}")
print(f"integrity_pass={all_pass}")
if not all_pass:
    raise SystemExit(1)
