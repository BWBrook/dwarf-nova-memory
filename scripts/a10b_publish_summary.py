#!/usr/bin/env python3
"""Verify full A10b pilot payloads and emit compact public summaries."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
from statistics import fmean


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    if not rows:
        raise ValueError("empty summary")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(source, destination):
    receipt = json.loads((source / "receipt.json").read_text())
    if receipt["status"] not in {"completed", "completed_with_failures"}:
        raise ValueError("pilot has not finished")
    for name, key in (("records.json", "records_sha256"),
                      ("scores.jsonl", "scores_sha256"),
                      ("summary.json", "summary_sha256")):
        if sha(source / name) != receipt[key]:
            raise ValueError(f"changed payload: {name}")
    records = json.loads((source / "records.json").read_text())
    if len(records) != receipt["trials"] or len({tuple(r["task"]) for r in records}) != len(records):
        raise ValueError("trial identities do not reconcile")
    successful = {tuple(r["task"]): r["result"] for r in records if r["success"]}
    if len(successful) != receipt["successful_trials"] or len(records)-len(successful) != receipt["failed_trials"]:
        raise ValueError("trial statuses do not reconcile")
    grouped = {}
    line_count = 0
    with (source / "scores.jsonl").open() as handle:
        for line in handle:
            row = json.loads(line)
            task = (row["family"], row["case"], row["replicate"])
            if task not in successful:
                raise ValueError("score from unsuccessful trial")
            for comparison, left, right in (("gain_M1_M0", "M1", "M0"),
                                             ("gain_M2_M0", "M2", "M0"),
                                             ("gain_M3_M2", "M3", "M2")):
                if not math.isclose(row[comparison], row[left]-row[right], rel_tol=0, abs_tol=1e-12):
                    raise ValueError("paired score arithmetic differs")
                grouped.setdefault((*task, row["variant"], comparison), []).append(row[comparison])
            line_count += 1
    if line_count != receipt["score_rows"]:
        raise ValueError("score line count differs")
    for task, result in successful.items():
        for variant, comparisons in result["results"].items():
            for comparison, values in comparisons.items():
                scores = grouped[(*task, variant, comparison)]
                if len(scores) != values["n"] or not math.isclose(fmean(scores), values["estimate"], abs_tol=1e-12):
                    raise ValueError("per-trial aggregate differs")
    destination.mkdir(parents=True, exist_ok=False)
    manifest, models, details, domains = [], [], [], []
    for record in records:
        family, case, replicate = record["task"]
        name = f"{family}-{case}-{replicate:03d}.json"
        if sha(source / name) != receipt["trial_file_sha256"][name]:
            raise ValueError("trial file differs from receipt")
        if json.loads((source / name).read_text()) != record:
            raise ValueError("trial file differs from records")
        manifest.append({"family": family, "case": case, "replicate": replicate,
                         "success": record["success"], "error_type": record.get("error_type", ""),
                         "error": record.get("error", ""), "file": name,
                         "sha256": receipt["trial_file_sha256"][name]})
        if not record["success"]:
            continue
        result = record["result"]
        details.append({"task": record["task"], "counts": result["counts"],
                        "diagnostic_mapping_counts": result["diagnostic_mapping_counts"],
                        "evaluation_routes": result["evaluation_routes"]})
        for variant, scopes in result["duration_domain_diagnostics"].items():
            for scope, diagnostic in scopes.items():
                domains.append({"family": family, "case": case, "replicate": replicate,
                                "variant": variant, "scope": scope,
                                **{key: value for key, value in diagnostic.items() if not key.endswith("emission_indices")},
                                "nonpositive_ids": ";".join(map(str, diagnostic["nonpositive_mark_emission_indices"])),
                                "point_invalid_ids": ";".join(map(str, diagnostic["point_invalid_emission_indices"]))})
        for variant, bundle in result["models"].items():
            for model in [*bundle["models"].values(), bundle["r0"]]:
                convergence = model["metadata"]["convergence"]
                coefficients = model["coefficients"]
                models.append({"family": family, "case": case, "replicate": replicate,
                               "variant": variant, "model": model["name"], "n_fit": model["n_fit"],
                               "intercept": model["intercept"], "sigma": model["sigma"],
                               "beta_duration": coefficients.get("duration", ""),
                               "beta_previous_gap": coefficients.get("previous_gap", ""),
                               "beta_type": coefficients.get("duration_type", ""),
                               "beta_within": coefficients.get("duration_within", ""),
                               "optimizer_success": convergence["success"],
                               "optimizer_starts": len(convergence["starts"]),
                               "failed_optimizer_starts": sum(not start["success"] for start in convergence["starts"]),
                               "successful_start_objective_spread": max(start["objective"] for start in convergence["starts"] if start["success"]) - min(start["objective"] for start in convergence["starts"] if start["success"]),
                               "objective": convergence["objective"],
                               "boundary_parameters": ";".join(convergence["boundary_parameters"])})
    summary = json.loads((source / "summary.json").read_text())
    write_csv(destination / "trial_manifest.csv", manifest)
    write_csv(destination / "model_diagnostics.csv", models)
    write_csv(destination / "duration_domain_diagnostics.csv", domains)
    write_csv(destination / "forecast_gains.csv", summary["rows"])
    write_csv(destination / "paired_stress_contrasts.csv", summary["paired_stress_contrasts"])
    (destination / "issuance_counts.json").write_text(json.dumps(details, indent=2, sort_keys=True)+"\n")
    shutil.copyfile(source / "receipt.json", destination / "receipt.json")
    shutil.copyfile(source / "summary.json", destination / "summary.json")
    print(json.dumps({"trials": len(records), "successful_trials": len(successful),
                      "score_rows_verified": line_count, "aggregate_groups_verified": len(grouped),
                      "published_bytes": sum(p.stat().st_size for p in destination.iterdir())}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    main(args.source, args.destination)
