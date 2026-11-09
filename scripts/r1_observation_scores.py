#!/usr/bin/env python3
"""Run the frozen R1b compatibility sensitivities; private detail, public aggregates."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from dnmem.observation_scores_r1 import (STOP, VARIANTS, reconstruct_onsets,
                                       score_alternatives, stopping_cutoffs)
from check_a10d_scores import conditional_score, lognormal_sf, model_value

PROTOCOL = Path("docs/protocols/r1-observation-endpoint-diagnostics-v1.md")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def verify_protocol(commit):
    if not commit:
        raise ValueError("scoring requires an explicit protocol freeze commit")
    for path in (PROTOCOL, Path("scripts/r1_observation_scores.py"),
                 Path("src/dnmem/observation_scores_r1.py"), Path("tests/test_r1_observation_scores.py")):
        committed = subprocess.run(["git", "show", f"{commit}:{path.as_posix()}"], cwd=ROOT,
                                   check=True, capture_output=True).stdout
        if committed != (ROOT / path).read_bytes():
            raise ValueError(f"{path} differs from the supplied freeze commit")
    return digest(ROOT / PROTOCOL)


def prepare(cache):
    receipt = read_json(cache / "private-cache-receipt.json")
    for name, metadata in receipt["files"].items():
        if digest(cache / name) != metadata["sha256"]:
            raise ValueError(f"private cache hash mismatch: {name}")
    for key, name in (("extractor_sha256", "src/dnmem/extract_x4.py"),
                      ("visit_builder_sha256", "src/dnmem/extract.py")):
        if digest(ROOT / name) != receipt[key]:
            raise ValueError(f"frozen reconstruction source mismatch: {name}")
    rows = read_json(cache / "validated-rows.json")
    episodes = read_json(cache / "all-x4-episodes.json")
    votes = read_json(cache / "visits.json")
    if any(float(r["JD"]) >= STOP or r["band"] != "Vis." or r["val"] != "V" for r in rows):
        raise ValueError("retained row violates the open data scope")
    reconstructed = reconstruct_onsets(rows, episodes, votes)
    summary = {"all_episode_count": len(episodes), "confirmed_episode_count": sum(e["confirmed_event"] for e in episodes),
               "missing_lower_clip": sum(r["clip_lo"] is None for r in reconstructed),
               "missing_upper_clip": sum(r["clip_hi"] is None for r in reconstructed),
               "clip_conflicts": sum(r["clip_conflict"] for r in reconstructed),
               "missing_kernel": sum(r["components"] is None for r in reconstructed),
               "exact_frozen_onset_reconstruction": True}
    return receipt, episodes, votes, reconstructed, summary


def independent_checks(spec, ledger, evidence, saved, results):
    features = {r["emission_index"]: r for r in ledger}
    outcomes = {r["emission_index"]: r for r in evidence}
    saved_map = {r["emission_index"]: r for r in saved if r.get("gain_M3_M2") is not None}
    errors = {"original_scalar": [], "alternative_interval_survival_scalar": [], "point_scalar": []}
    for index, row in saved_map.items():
        for name in ("M2", "M3"):
            value = conditional_score(features[index], outcomes[index], spec, row[f"{name}_route"])
            errors["original_scalar"].append(abs(value - row[name]))
    for variant, rows in results.items():
        for row in rows:
            if row["status"] != "usable" or row["scores"] is None or (variant == "x4_kernel" and row["kind"] == "interval"):
                continue
            feature = features[row["emission_index"]]
            for j, route in enumerate(row["forecast_routes"]):
                if row["kind"] == "point":
                    model = spec["r0"] if route == "R0" else spec["models"][route]
                    anchor = feature["issue_time"] if route == "R0" else feature["end_t"]
                    mu = model_value(model, feature, None if route == "R0" else anchor,
                                     None if route == "R0" else anchor - feature["onset_t"])
                    wait, sigma = row["point"] - anchor, model["sigma"]
                    z = (math.log(wait) - mu) / sigma
                    value = (-0.5 * z * z - math.log(wait) - math.log(sigma)
                             - 0.5 * math.log(2 * math.pi)
                             - lognormal_sf(feature["issue_time"] - anchor, mu, sigma))
                    key = "point_scalar"
                else:
                    outcome = dict(row, emission_index=row["emission_index"], issue_time=feature["issue_time"])
                    value = conditional_score(feature, outcome, spec, route)
                    key = "alternative_interval_survival_scalar"
                errors[key].append(abs(value - row["scores"][j]))
    summary = {k: {"terms": len(v), "max_absolute_error": max(v, default=0.0)} for k, v in errors.items()}
    if any(v["max_absolute_error"] > 1e-8 for v in summary.values()):
        raise ValueError("independent scalar score validation failed")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/r1_censor_audit")
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/a10h_live_repair_5e39aeb")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true", help="reconstruct only; never open original scores")
    parser.add_argument("--freeze-commit")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output directory already exists; preserve previous runs")
    relative_output = args.output.resolve().relative_to(ROOT)
    ignored = subprocess.run(["git", "check-ignore", "-q", "--", str(relative_output / "per-issuance-private.json")], cwd=ROOT)
    if ignored.returncode != 0:
        raise ValueError("private output directory must be ignored by Git")
    protocol_sha = digest(ROOT / PROTOCOL) if args.prepare else verify_protocol(args.freeze_commit)
    args.output.mkdir(parents=True)
    receipt, episodes, votes, reconstructed, preparation = prepare(args.cache)
    write_json(args.output / "reconstructed-onsets-private.json", reconstructed)
    write_json(args.output / "preparation.json", preparation)
    hashes = {"cache_receipt": digest(args.cache / "private-cache-receipt.json"),
              "protocol": protocol_sha, "module": digest(ROOT / "src/dnmem/observation_scores_r1.py"),
              "runner": digest(__file__)}
    if args.prepare:
        write_json(args.output / "receipt.json", {"mode": "preparation_only_no_scores_opened", "hashes": hashes,
                                                   "outputs": {p.name: digest(p) for p in args.output.iterdir()}})
        print(json.dumps({"mode": "preparation_only_no_scores_opened", **preparation}, sort_keys=True))
        return
    original_receipt = read_json(args.run / "receipt.json")
    expected_receipt = receipt["input_verification"]["original_receipt_sha256"]
    if digest(args.run / "receipt.json") != expected_receipt:
        raise ValueError("original run receipt differs from the verified private cache")
    names = ("ledger-0.0.json", "evidence-0.0.json", "primary-scores.json", "frozen_parameters.json")
    for name in names:
        hashes[name] = digest(args.run / name)
        if hashes[name] != original_receipt["files_sha256"][name]:
            raise ValueError(f"original retained output hash mismatch: {name}")
    ledger = read_json(args.run / "ledger-0.0.json")
    evidence = read_json(args.run / "evidence-0.0.json")
    saved = read_json(args.run / "primary-scores.json")
    spec = read_json(args.run / "frozen_parameters.json")["primary"]
    cutoffs = stopping_cutoffs(ledger, [v["t"] for v in votes])
    results, summary = score_alternatives(spec, ledger, evidence, saved, episodes, reconstructed, cutoffs)
    summary["preparation"] = preparation
    summary["independent_checks"] = independent_checks(spec, ledger, evidence, saved, results)
    integration = [d for rows in results.values() for row in rows for d in row.get("integration", [])]
    summary["kernel_numerical_checks"] = {"terms": len(integration), **{
        key: max((d[key] for d in integration), default=0.0) for key in
        ("adaptive_relative_error", "adaptive_vs_gl128_log_error", "gl64_vs_gl128_log_error", "gl32_vs_gl64_log_error")}}
    summary["observation_diagnostics"] = {name: {
        key: sum(bool(r.get(key)) for r in rows) for key in ("missing_clip", "missing_kernel", "clip_conflict", "straddle")}
        for name, rows in results.items()}
    summary["identity_observation_status"] = {name: dict(Counter(r["observation_status"] for r in rows
                                                               if r["status"] == "identical_forecast"))
                                               for name, rows in results.items()}
    summary["label"] = "R1b exploratory post-result sensitivity; original frozen result preserved"
    summary["hashes"] = hashes
    summary["freeze_commit"] = args.freeze_commit
    write_json(args.output / "per-issuance-private.json", results)
    write_json(args.output / "summary.json", summary)
    write_json(args.output / "receipt.json", {"mode": "exploratory_scores", "hashes": hashes,
                                               "outputs": {p.name: digest(p) for p in args.output.iterdir()}})
    print(json.dumps({"completed": True, "original_population": summary["original_population"],
                      "common_usable": summary["common_usable"], "summary_sha256": digest(args.output / "summary.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
