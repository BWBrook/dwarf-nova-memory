#!/usr/bin/env python3
"""Reconcile actual pilot fit populations, routes and original-stream replay."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def support(feature, mode, nodes):
    if feature["landmark_available"] is False:
        return None
    if mode == "point":
        return None if feature["end_t"] is None else [feature["end_t"]]
    low, high = feature["end_lo"], feature["end_hi"]
    if low is None or high is None:
        return None
    high = min(high, feature["issue_time"])
    assert high >= low-1e-12
    return [low] if high-low <= 1e-12 else [low+(high-low)*i/(nodes-1) for i in range(nodes)]


def available_duration(feature, endpoints):
    if endpoints is None:
        return False
    if feature["onset_t"] is not None:
        return all(end-feature["onset_t"] > 0 for end in endpoints)
    return feature["duration"] is not None and feature["duration"] > 0


def reconcile(source, aborted, output):
    receipt = json.loads((source/"receipt.json").read_text())
    records = json.loads((source/"records.json").read_text())
    assert receipt["status"] in {"completed", "completed_with_failures"}
    assert len(records) == 56 == receipt["trials"]
    old_records = json.loads((aborted/"records.json").read_text())
    old = {tuple(r["task"]): r["result"] for r in old_records if r["success"]}
    route_counts = defaultdict(Counter)
    score_count = 0
    with (source/"scores.jsonl").open() as handle:
        for line in handle:
            row = json.loads(line)
            key = (row["family"], row["case"], row["replicate"], row["variant"])
            assert all(math.isfinite(row[m]) for m in ("M0", "M1", "M2", "M3"))
            for model in ("M0", "M1", "M2", "M3"):
                route_counts[(*key, model)][row["route_"+model]] += 1
            score_count += 1
    replay, fits_checked, variants_checked, known_nonpositive = [], 0, 0, 0
    point_invalid, evaluated_unknown, emitted = 0, 0, 0
    failure_records = []
    for record in records:
        if not record["success"]:
            failure_records.append({k: v for k, v in record.items() if k != "result"})
            continue
        result = record["result"]
        task = tuple(record["task"])
        cutoff = result["stream_metadata"]["training_cutoff"]
        if task in old:
            subset = {k: result[k] for k in old[task]}
            assert subset == old[task], f"original successful trial changed: {task}"
            replay.append({"task": list(task), "original_result_sha256": digest(old[task]),
                           "replayed_result_subset_sha256": digest(subset), "exact": True})
        for variant, bundle in result["models"].items():
            latency = "2" if variant.endswith("_L2") else "0"
            view = ("prefix_L2" if latency == "2" else "oracle" if variant.startswith("oracle")
                    else "retrospective" if variant.startswith("retrospective") else "prefix")
            fit = result["ledger_trace"][view]["training"]
            evidence = {e["emission_index"]: e for e in result["evidence_trace"][latency]["training"]}
            counts = Counter()
            for feature in fit:
                ev = evidence[feature["emission_index"]]
                assert feature["issue_time"] < cutoff
                assert ev["computed_as_of"] <= cutoff and ev["evidence_available_at"] <= cutoff
                assert feature["emitted_at"] <= feature["issue_time"]
                if ev["kind"] == "excluded":
                    continue
                counts["R0"] += 1
                endpoints = support(feature, bundle["endpoint_mode"], bundle["nodes"])
                if endpoints is None:
                    continue
                mark = available_duration(feature, endpoints)
                previous = feature["previous_gap_covered"] is True and feature["previous_gap"] is not None and feature["previous_gap"] > 0
                counts["M0"] += 1
                counts["M1"] += int(mark)
                counts["M2"] += int(previous)
                counts["M3"] += int(mark and previous)
            for name, model in {**bundle["models"], "R0": bundle["r0"]}.items():
                assert model["n_fit"] == counts[name], (task, variant, name, model["n_fit"], counts[name])
                assert model["metadata"]["convergence"]["success"]
                fits_checked += 1
            for model in ("M0", "M1", "M2", "M3"):
                actual = dict(route_counts[(*task, variant, model)])
                assert actual == result["evaluation_routes"][variant][model]
                assert sum(actual.values()) == result["results"][variant]["gain_M3_M2"]["n"]
            domain = result["duration_domain_diagnostics"][variant]["evaluation_scored"]
            known_nonpositive += domain["nonpositive_mark_count"]
            point_invalid += domain["point_invalid_count"]
            evaluated_unknown += domain["variant_missing_landmark_count"]
            emitted += result["results"][variant]["gain_M3_M2"]["n"]
            variants_checked += 1
    assert score_count == receipt["score_rows"] == emitted
    report = {"source_freeze": receipt["state"]["freeze_commit"], "seed_base": receipt["seed_base"],
              "trials": len(records), "failed_trials": failure_records,
              "score_rows": score_count, "model_fits_reconciled": fits_checked,
              "variant_route_populations_reconciled": variants_checked,
              "nonpositive_mark_variant_issuances": known_nonpositive,
              "point_invalid_variant_issuances": point_invalid,
              "unknown_landmark_variant_issuances": evaluated_unknown,
              "original_successful_trial_exact_replays": replay,
              "count_scope": "variant-issuances repeat the same issuance across variants; not unique physical events"}
    output.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n")
    print(json.dumps({k: v for k, v in report.items() if k != "original_successful_trial_exact_replays"}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("aborted", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    reconcile(args.source, args.aborted, args.output)
