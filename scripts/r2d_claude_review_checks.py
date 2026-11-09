"""Claude's review of the R2d precision screen: recount from retained trial lines, joint
rejection structure and fixed-sequence (association, then forecast gain) operating characteristics.

Synthetic only. Reads ignored `outputs/r2d_precision_67c45ab/*-trials.jsonl`, checks each file's
hash against the committed summary, and writes aggregates. Usage:

    python3 scripts/r2d_claude_review_checks.py > data/provenance/r2d_claude_review/checks.json
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs" / "r2d_precision_67c45ab"
SUMMARY = ROOT / "data" / "provenance" / "r2d_precision" / "summary.json"


def exact_interval(k, n, level=0.95):
    from scipy.stats import beta
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return [lo, hi]


def rate(k, n):
    return {"k": k, "n": n, "rate": k / n, "mc95": exact_interval(k, n)}


def case_stats(path):
    trials = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ok = [t for t in trials if t.get("status") == "passed"]
    n = len(ok)

    def rej(t, cl, stat):
        return bool(t["methods"][cl][stat]["reject_one_sided"])

    out = {"trials": len(trials), "passed": n}
    for cl in ("star", "halves"):
        g = [rej(t, cl, "gain") for t in ok]
        s = [rej(t, cl, "score") for t in ok]
        out[cl] = {
            "gain": rate(sum(g), n), "score": rate(sum(s), n),
            "both": rate(sum(a and b for a, b in zip(g, s)), n),
            "gain_without_score": rate(sum(a and not b for a, b in zip(g, s)), n),
            "fixed_sequence_gain_claim": rate(sum(a and b for a, b in zip(g, s)), n),
            "gain_given_nonidentity": rate(sum(a for a, t in zip(g, ok) if not t["gain_identity"]),
                                           sum(not t["gain_identity"] for t in ok)),
        }
    flips = [bool(t["score_sign_flip"]["reject_one_sided"]) for t in ok]
    g = [rej(t, "star", "gain") for t in ok]
    out["sign_flip"] = {"score": rate(sum(flips), n),
                        "then_star_gain": rate(sum(a and b for a, b in zip(flips, g)), n)}
    betas = [t["beta_hat"] for t in ok]
    out["identity"] = rate(sum(t["gain_identity"] for t in ok), n)
    out["beta_hat_mean"] = sum(betas) / n
    out["beta_hat_zero_fraction"] = sum(b == 0 for b in betas) / n
    proj = [t["conditional_local_signal_projection"] for t in ok if t.get("conditional_local_signal_projection") is not None]
    out["mean_local_signal_projection"] = sum(proj) / len(proj) if proj else None
    overshoot = [t for t in ok if t.get("conditional_local_signal_projection") and t["beta_hat"] > 2 * t["conditional_local_signal_projection"] > 0]
    out["beta_hat_above_twice_projection"] = rate(len(overshoot), n)
    return out, ok


def main():
    summary = json.loads(SUMMARY.read_text())
    cases = summary["cases"]
    cases = cases if isinstance(cases, dict) else {c["case"]: c for c in cases}
    report, hashes_ok, recount_ok = {}, {}, {}
    pooled = {"strict_oracle_predictive_null": {"star-score": [0, 0], "sign-flip": [0, 0], "star-gain": [0, 0]}}
    for name, c in cases.items():
        path = RUN / f"{name}-trials.jsonl"
        hashes_ok[name] = hashlib.sha256(path.read_bytes()).hexdigest() == c["trials_sha256"]
        stats, ok = case_stats(path)
        stats["settings"] = c["settings"]
        recount_ok[name] = (stats["star"]["gain"]["k"] == c["methods"]["star-gain"]["rejections"]
                            and stats["star"]["score"]["k"] == c["methods"]["star-score"]["rejections"]
                            and stats["sign_flip"]["score"]["k"] == c["methods"]["star-score-sign-flip"]["rejections"])
        report[name] = stats
        cls = c["settings"].get("null_class")
        if cls in pooled:
            for key, k in (("star-score", stats["star"]["score"]["k"]), ("sign-flip", stats["sign_flip"]["score"]["k"]),
                           ("star-gain", stats["star"]["gain"]["k"])):
                pooled[cls][key][0] += k
                pooled[cls][key][1] += stats["passed"]
    pooled_out = {cls: {k: rate(*v) for k, v in d.items()} for cls, d in pooled.items()}
    from scipy.stats import binom
    p_fail_one_cell = float(binom.sf(100, 2000, 0.05))
    json.dump({
        "scope": "synthetic R2d screen only; recount of retained trial lines; no observations",
        "trial_hashes_match_summary": all(hashes_ok.values()),
        "rejection_recounts_match_summary": all(recount_ok.values()),
        "pooled_strict_null": pooled_out,
        "all_cases_gain_reject_without_score_reject": {
            cl: sum(r[cl]["gain_without_score"]["k"] for r in report.values()) for cl in ("star", "halves")},
        "all_cases_trials": sum(r["passed"] for r in report.values()),
        "per_cell_screen_note": {"exact_5pct_test_fails_observed_le_5pct_in_2000_trials": p_fail_one_cell,
                                 "four_independent_cells_any_fail": 1 - (1 - p_fail_one_cell) ** 4},
        "cases": report,
    }, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
