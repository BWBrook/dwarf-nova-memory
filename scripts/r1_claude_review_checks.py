"""Claude's independent R1 review checks (separate code from Codex's routes). Aggregates only.

Reads retained, already opened 1896-2017 outputs (no archive request, nothing from 2018 on) and
writes aggregates to stdout: C43-C46 recomputations and a gain-free look at the corrected
decisive onset bracket.

    uv run python scripts/r1_claude_review_checks.py > data/provenance/r1_claude_review/checks.json
"""
import bisect, glob, json, math, statistics, sys
from collections import defaultdict
from scipy import optimize, stats

ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[1]) + "/"
JD0 = 2436934.5
BLOCK = 6 * 365.25


def cr1(pairs):
    n = len(pairs)
    mean = sum(g for _, g in pairs) / n
    blocks = defaultdict(list)
    for t, g in pairs:
        blocks[int((t - JD0) // BLOCK)].append(g)
    G = len(blocks)
    se = math.sqrt(G / (G - 1) * sum((sum(v) - len(v) * mean) ** 2 for v in blocks.values()) / n ** 2)
    q = stats.t.ppf(0.95, G - 1)
    return {"n": n, "blocks": G, "mean": mean, "lo": mean - q * se, "hi": mean + q * se}


out = {}
pi = json.load(open(ROOT + "outputs/r1b_frozen_0594146/per-issuance-private.json"))
sp = pi["saved_point"]
out["C44_point"] = cr1([(r["issue_time"], r["gain"]) for r in sp])
out["C44_paired"] = cr1([(r["issue_time"], r["gain"] - r["primary_gain"]) for r in sp])
out["C44_primary_same_rows"] = cr1([(r["issue_time"], r["primary_gain"]) for r in sp])
out["C44_spearman"] = stats.spearmanr([r["gain"] for r in sp], [r["primary_gain"] for r in sp]).statistic
dr = pi["decisive_report"]
st = defaultdict(int)
for r in dr:
    st[r["status"]] += 1
out["C45_status_counts"] = dict(st)
out["C45_usable"] = cr1([(r["issue_time"], r["gain"]) for r in dr if r["gain"] is not None]) if any(r["gain"] is not None for r in dr) else None

run = ROOT + "outputs/a10h_live_repair_5e39aeb/"
ledger = json.load(open(run + "ledger-0.0.json"))
evidence = json.load(open(run + "evidence-0.0.json"))
eps = sorted((e for e in json.load(open(ROOT + "outputs/r1_censor_audit/all-x4-episodes.json")) if e["confirmed_event"]),
             key=lambda e: e["peak_t"])
peaks = [e["peak_t"] for e in eps]
cens = []
for f, ev in zip(ledger, evidence):
    if ev["kind"] != "right_censored":
        continue
    cand = next((e for e in eps[bisect.bisect_right(peaks, f["emitted_at"]):]
                 if e["onset_hi"] is not None and e["onset_hi"] > f["emitted_at"]), None)
    c = ev["censor_at"]
    rel = "none" if cand is None else ("after" if cand["onset_lo"] is not None and cand["onset_lo"] >= c
                                      else "before" if cand["onset_hi"] <= c else "straddle")
    cens.append({"reason": ev["reason"], "relation": rel})
out["C43_censors"] = cens

# C46: per-history all-issued extracted means from the retained synthetic score files.
files = sorted(glob.glob(ROOT + "outputs/r1c_frozen_0594146/*-scores.jsonl"))
files = [f for f in files if "structured-000" not in f] + [ROOT + "outputs/r1c_recovery_93e52e6/structured-000-scores.jsonl"]
hist = defaultdict(dict)
nones = defaultdict(int)
for path in files:
    name = path.rsplit("/", 1)[1].replace("-scores.jsonl", "")
    case = name.split("-")[0]
    acc = defaultdict(list)
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            if r["route"] == "all_issued_extracted":
                if r["gain_M3_M2"] is None:
                    nones[(case, r["sigma"], r["kind"])] += 1
                    continue
                acc[r["sigma"]].append(r["gain_M3_M2"])
    for s, g in acc.items():
        hist[(case, s)][name] = sum(g) / len(g)
c46 = []
for (case, s), d in sorted(hist.items()):
    v = list(d.values())
    c46.append({"case": case, "sigma": s, "histories": len(v), "mean": statistics.fmean(v),
                "mc_se": statistics.stdev(v) / math.sqrt(len(v))})
out["C46_all_issued"] = c46
out["C46_none_gains"] = {str(k): v for k, v in nones.items()}

# Clip mechanism and a gain-free look at a corrected decisive bracket (positive estimates only).
vis = json.load(open(ROOT + "outputs/r1_censor_audit/visits.json"))
fb = sorted(v["t"] for v in vis if v["value"] is not None and v["value"] <= 9.0)
ff = sorted(v["t"] for v in vis if v["cls"] == "F" and v["value"] is not None and v["value"] >= 11.0)
allep = sorted(json.load(open(ROOT + "outputs/r1_censor_audit/all-x4-episodes.json")), key=lambda e: e["peak_t"])


def between(arr, lo, hi):
    return arr[bisect.bisect_right(arr, lo):bisect.bisect_left(arr, hi)]


tail_first, widths, fit_widths, none_ct, quiet_none = 0, [], [], 0, 0
for i in range(1, len(allep)):
    if not allep[i]["confirmed_event"]:
        continue
    pp, pk = allep[i - 1]["peak_t"], allep[i]["peak_t"]
    b = between(fb, pp, pk + 1e-9)
    f = between(ff, pp, pk)
    if b and f and b[0] < f[-1]:
        tail_first += 1
    quiet = f[0] if f else None  # first decisive faint after the previous peak: quiescence reached
    if quiet is None:
        quiet_none += 1
        continue
    U = next((t for t in between(fb, quiet, pk + 1e-9)), None)
    if U is None:
        none_ct += 1
        continue
    L = max(t for t in ff if quiet <= t < U)
    widths.append(U - L)
    if allep[i]["onset_lo"] is not None and allep[i]["onset_hi"] is not None:
        fit_widths.append(allep[i]["onset_hi"] - allep[i]["onset_lo"])
qs = statistics.quantiles(widths, n=20)
out["clip_mechanism"] = {
    "confirmed_with_previous": sum(1 for e in allep[1:] if e["confirmed_event"]),
    "first_far_bright_after_prev_peak_precedes_last_far_faint": tail_first,
    "corrected_bracket_available": len(widths), "no_quiescence_report": quiet_none, "no_bright_after_quiescence": none_ct,
    "corrected_width_days": {"median": statistics.median(widths), "p25": qs[4], "p75": qs[14], "p90": qs[17],
                             "share_le_2d": sum(w <= 2 for w in widths) / len(widths),
                             "share_le_5d": sum(w <= 5 for w in widths) / len(widths)},
    "x4_saved_width_days_median": statistics.median(fit_widths),
    "note": "positive estimates only (fainter-than limits omitted); whole 1896-2017 opened record; gain-free",
}
# C42: Figure 1 example by scipy lognormal and root finding (Codex used erfc and inverse normal).
params = json.load(open(run + "frozen_parameters.json"))["primary"]["models"]
chosen = min((x for x in ledger if JD0 <= x["issue_time"] < JD0 + 366 and x.get("onset_t") is not None
              and x["onset_t"] > JD0), key=lambda x: (x["issue_time"], x["emission_index"]))
age, dur = chosen["issue_time"] - chosen["end_t"], chosen["end_t"] - chosen["onset_t"]
inputs = {"previous_gap": math.log(chosen["previous_gap"]), "earlier_level": statistics.fmean(chosen["earlier_gaps"])}
c42 = {}
for name in ("M2", "M3"):
    m = params[name]
    mu = m["intercept"] + sum(m["coefficients"][k] * (inputs[k] - m["centers"][k]) / m["scales"][k] for k in inputs)
    if name == "M3":
        mu += m["coefficients"]["beta"] * (math.log(dur) - m["centers"]["mark"]) / m["scales"]["mark"]
    dist = stats.lognorm(s=m["sigma"], scale=math.exp(mu))
    surv = dist.sf(age)
    c42[name] = {"median_wait_days": optimize.brentq(lambda w: dist.sf(age + w) / surv - 0.5, 0.0, 1e4),
                 "p_within_30_days": 1 - dist.sf(age + 30.0) / surv}
out["C42_example"] = c42
json.dump(out, sys.stdout, indent=1, default=float)
