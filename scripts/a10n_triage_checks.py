"""A10n exploratory triage checks for the external review (not a confirmation).

Reads the retained 1960-2017 primary run (already opened in A10i) and the
committed A10d simulation report. Writes aggregates only: no per-issuance
score, event time or observer identity leaves the retained directory.

    uv run python scripts/a10n_triage_checks.py \
        --run outputs/a10h_live_repair_5e39aeb \
        --output data/provenance/a10n_triage/checks.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

from scipy import stats

JD_1960 = 2436934.0
BLOCK_DAYS = 6 * 365.25
NULL_CASES = {("v2-phase", c) for c in ("null", "offset", "gross", "adaptive", "structured")} | {("v4-phase", "null")}


def cr1(rows: list[dict]) -> dict:
    n = len(rows)
    blocks: dict[int, list[float]] = {}
    for r in rows:
        blocks.setdefault(r["block"], []).append(r["gain"])
    mean = sum(r["gain"] for r in rows) / n
    g = len(blocks)
    se = math.sqrt(g / (g - 1) * sum((len(v) * (sum(v) / len(v) - mean)) ** 2 for v in blocks.values()) / n ** 2)
    t = stats.t.ppf(0.95, g - 1)
    return {"n": n, "blocks": g, "mean": mean, "lower90": mean - t * se, "upper90": mean + t * se}


def censor_audit(ledger: list[dict], evidence: list[dict], scores: list[dict]) -> dict:
    cases = [i for i, e in enumerate(evidence) if e["kind"] == "right_censored"]
    relation = {}
    for i in cases:
        cut = evidence[i]["censor_at"]
        nxt = ledger[i + 1] if i + 1 < len(ledger) else None
        if nxt is None:
            rel = "no_later_emission"
        elif nxt["repeat_of_previous"]:
            later = next((evidence[j] for j in range(i + 2, len(evidence)) if evidence[j]["kind"] == "interval"), None)
            rel = "after" if later and later["onset_lo"] >= cut else "check"
        else:
            lo, hi = nxt["onset_lo"], nxt["onset_hi"]
            rel = "after" if lo >= cut else ("before" if hi <= cut else "straddles")
        key = f"{evidence[i]['reason']}:{rel}"
        relation[key] = relation.get(key, 0) + 1
    gains = [s["gain_M3_M2"] for s in scores]
    six = sum(gains[i] for i in cases)
    return {
        "censored": len(cases),
        "reason_and_next_emitted_onset_relation": relation,
        "censored_total_contribution": six,
        "mean_all": sum(gains) / len(gains),
        "mean_excluding_censored": (sum(gains) - six) / (len(gains) - len(cases)),
        "limit": "Relation uses the next emitted outburst's onset bracket; the evidence builder's actual "
                 "candidate (first confirmed episode after emission) must be confirmed by Codex.",
    }


def end_width_split(ledger: list[dict], scores: list[dict]) -> dict:
    rows = [{"width": f["end_hi"] - f["end_lo"], "gain": s["gain_M3_M2"],
             "block": int((s["issue_time"] - JD_1960) // BLOCK_DAYS)} for f, s in zip(ledger, scores)]
    widths = [r["width"] for r in rows]
    med = statistics.median(widths)
    t1, t2 = statistics.quantiles(widths, n=3)
    rho = stats.spearmanr(widths, [r["gain"] for r in rows])
    return {
        "all": cr1(rows),
        "end_bracket_width_days": {"median": med, "tercile_cuts": [t1, t2], "min": min(widths), "max": max(widths)},
        "narrow_half": cr1([r for r in rows if r["width"] <= med]),
        "wide_half": cr1([r for r in rows if r["width"] > med]),
        "terciles": [cr1([r for r in rows if lo < r["width"] <= hi])
                     for lo, hi in ((-math.inf, t1), (t1, t2), (t2, math.inf))],
        "spearman_width_gain": {"rho": rho.statistic, "p": rho.pvalue},
        "prediction_stated_before_run": "An endpoint-error pathway predicts gain concentrated in wide end brackets.",
    }


def null_gains(path: Path) -> list[dict]:
    out = []
    with path.open() as fh:
        for r in csv.DictReader(fh):
            if r["variant"] == "primary" and r["cluster_years"] == "6" and r["comparison"] == "gain_M3_M2":
                out.append({"family": r["family"], "case": r["case"], "nominal_null": (r["family"], r["case"]) in NULL_CASES,
                            "mean_gain": float(r["mean_gain"]), "trial_sd": float(r["trial_sd"]),
                            "mc_se": float(r["trial_sd"]) / math.sqrt(int(r["trials"])),
                            "confirmations": f"{r['successes']}/{r['trials']}"})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--simulations", type=Path, default=Path("data/simulations/a10d_20261108/comparisons.csv"))
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    ledger = json.loads((a.run / "ledger-0.0.json").read_text())
    evidence = json.loads((a.run / "evidence-0.0.json").read_text())
    scores = json.loads((a.run / "primary-scores.json").read_text())
    result = {"label": "A10n exploratory, post-result triage checks; not a confirmation",
              "censor_audit": censor_audit(ledger, evidence, scores),
              "end_width_split": end_width_split(ledger, scores),
              "simulated_gain_M3_M2": null_gains(a.simulations)}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, default=float) + "\n")
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()
