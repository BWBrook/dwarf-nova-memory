#!/usr/bin/env python3
"""Compare sealed independent 1957 labels with Claude's overlapping annotation."""

import csv
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def value(row, key):
    return float(row[key]) if row[key] else None


def main() -> None:
    directory = ROOT / "data/annotations"
    seal = json.loads((directory / "a04_ss_cyg_1957_codex_blind_seal.json").read_text())
    for name, expected in seal["public_outputs_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("sealed blind artifact differs from its recorded hash")
    with (directory / "a04_ss_cyg_1956_1958_claude_v1.csv").open(newline="") as handle:
        claude = [r for r in csv.DictReader(handle) if 2435839.5 <= value(r, "onset_latest_jd") <= 2436204.5]
    with (directory / "a04_ss_cyg_1957_codex_blind_v1.csv").open(newline="") as handle:
        blind = list(csv.DictReader(handle))
    if len(claude) != len(blind):
        raise ValueError("episode counts differ; chronological pairing needs explicit adjudication")
    comparisons = []
    for a, b in zip(claude, blind):
        on_a = [value(a, k) for k in ("onset_earliest_jd", "onset_latest_jd")]
        on_b = [value(b, k) for k in ("onset_earliest_jd", "onset_latest_jd")]
        overlap_on = max(on_a[0], on_b[0]) < min(on_a[1], on_b[1])
        same_peak = value(a, "peak_jd") == value(b, "peak_jd")
        if not overlap_on and not same_peak:
            raise ValueError("chronological pairing lacks either onset overlap or a common peak")
        edge = b["end_censored"] == "true"
        ea = [value(a, k) for k in ("end_earliest_jd", "end_latest_jd")]
        eb = [value(b, k) for k in ("end_earliest_jd", "end_latest_jd")]
        comparisons.append({
            "claude_event": a["event_id"], "blind_event": b["event_id"],
            "pairing": "overlapping_onset" if overlap_on else "shared_peak_only_after_seal",
            "onset_brackets_overlap": overlap_on,
            "onset_midpoint_difference_blind_minus_claude_d": statistics.mean(on_b) - statistics.mean(on_a),
            "subset_edge_censored": edge,
            "end_brackets_overlap": None if edge else max(ea[0], eb[0]) < min(ea[1], eb[1]),
            "claude_tied_end_epoch": not edge and ea[0] == ea[1],
            "end_midpoint_difference_blind_minus_claude_d": None if edge else statistics.mean(eb) - statistics.mean(ea),
            "end_confirmation_difference_blind_minus_claude_d": None if edge else value(b, "end_confirmed_jd") - value(a, "end_confirmed_jd"),
            "type_agrees": None if edge else a["type_cm92_v1"] == b["type"],
            "following_consecutiveness_agrees": None if edge else a["consecutive_with_next"] == b["following_event_consecutive"],
        })
    complete = [r for r in comparisons if not r["subset_edge_censored"]]
    result = {"pairing_rule": "chronological pairs; strict onset-overlap reported separately; shared-peak identification is post-seal adjudication",
              "paired_episodes": len(comparisons), "strict_onset_overlap_pairs": sum(r["onset_brackets_overlap"] for r in comparisons),
              "complete_end_pairs": len(complete), "strict_end_overlap_pairs": sum(r["end_brackets_overlap"] for r in complete),
              "max_abs_onset_midpoint_difference_d": max(abs(r["onset_midpoint_difference_blind_minus_claude_d"]) for r in comparisons),
              "max_abs_end_midpoint_difference_d": max(abs(r["end_midpoint_difference_blind_minus_claude_d"]) for r in complete),
              "type_agreement_complete": sum(r["type_agrees"] for r in complete),
              "following_consecutiveness_agreement": sum(r["following_consecutiveness_agrees"] for r in complete),
              "comparisons": comparisons, "scope": "inter-annotator agreement under protocol v1; not calibrated endpoint truth or forecast validation"}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
