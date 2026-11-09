"""Claude's R2a/c review checks and R2b rule diagnostics. Aggregates only.

Gain-free on the opened SS Cyg record before JD 2458119.5: no model is fitted,
no forecast is scored and no duration-gap relation is computed. The power
section is a separate reimplementation of the R2c score-level design with its
own code and seeds.
"""
import bisect
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import integrate
from scipy.stats import beta as beta_dist
from scipy.stats import t as t_dist

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.extract_x5 import decisive_visits  # noqa: E402

STOP, EVAL0, DEV0 = 2458119.5, 2436934.5, 2418672.5
BLOCK = 6 * 365.25
THR, BAND = 10.0, 1.0
FEATURES = ROOT / "outputs/r2a_features_956d33c"
SIGMA_M2, LOG_MEDIAN_M2 = 0.27773344012254203, 3.5749116935853764
B_HISTORY = 0.38


def period(t):
    return "development" if DEV0 <= t < EVAL0 else "evaluation" if EVAL0 <= t < STOP else None


def share(xs, cut):
    return sum(x <= cut for x in xs) / len(xs)


def dist(xs):
    xs = sorted(xs)
    return {"n": len(xs), "median": statistics.median(xs), "p90": xs[int(.9 * len(xs))],
            "mean_square": statistics.fmean(x * x for x in xs),
            "share_le_0p5": share(xs, .5), "share_le_1": share(xs, 1.0)}


def load_rows():
    rows = json.loads((ROOT / "outputs/r1_censor_audit/validated-rows.json").read_text())
    return sorted((r for r in rows if r["band"] == "Vis." and r["val"] == "V" and float(r["JD"]) < STOP),
                  key=lambda r: (float(r["JD"]), r["obsID"]))


def schedules(rows):
    visits = decisive_visits(rows, THR, BAND)
    closed = sorted(visits, key=lambda v: (v["available_at"], v["observer"]))
    faint = [v for v in closed if v["decisive"] == "F"]
    faint_av = [v["available_at"] for v in faint]
    thr_bright = [v for v in closed if v["cls"] == "B"]
    thr_av = [v["available_at"] for v in thr_bright]
    dec_av = sorted(v["available_at"] for v in closed if v["decisive"] == "B")
    below11 = sorted(v["last_at"] for v in visits if v["value"] is not None and v["value"] < THR + BAND)
    below11_first = sorted(v["first_at"] for v in visits if v["value"] is not None and v["value"] < THR + BAND)
    audit = json.loads((FEATURES / "df_schedule_audit-unreleased.json").read_text())
    x5 = json.loads((ROOT / "outputs/r2a_x5_diagnostics_fe6dbf4/episodes-unreleased.json").read_text())
    onsets = sorted(e["onset_report_lo"] for e in x5 if e.get("onset_report_lo") is not None)

    def count(av, lo, hi):
        return bisect.bisect_right(av, hi) - bisect.bisect_right(av, lo)

    triggers = Counter()
    brightest = []
    for row in audit:
        if row["status"] != "aborted_bright_before_delayed_issue":
            continue
        lo, hi = row["original_issue_time"], row["issue_time"]
        values = [thr_bright[i]["value"] for i in range(bisect.bisect_right(thr_av, lo), bisect.bisect_right(thr_av, hi))]
        values = [v for v in values if v is not None]
        triggers[(period(lo) or "pre1910", "decisive" if min(values) <= THR - BAND else "threshold_only")] += 1
        brightest.append(min(values))
    result = {"v1_abort_triggers": {f"{p}|{k}": n for (p, k), n in sorted(triggers.items())},
              "v1_abort_brightest_trigger_mag": {"n": len(brightest), "median": statistics.median(brightest),
                                                 "share_le_9": share(brightest, THR - BAND)}}
    rules = {}
    cadence = {}
    for rule in ("v1_threshold_abort", "decisive_abort"):
        by = defaultdict(list)
        for row in audit:
            p = period(row["original_issue_time"])
            if p is None:
                continue
            original = row["original_issue_time"]
            k = bisect.bisect_right(faint_av, row["original_last_bright_at"])
            if k >= len(faint):
                by[p].append({"status": "no_faint"})
                continue
            f = faint[k]
            issue = max(original, f["available_at"])
            av = thr_av if rule == "v1_threshold_abort" else dec_av
            if count(av, original, issue):
                by[p].append({"status": "aborted"})
                continue
            j = bisect.bisect_right(onsets, original)
            nxt = onsets[j] if j < len(onsets) else None
            m = bisect.bisect_left(below11, f["first_at"]) - 1
            lo_b, hi_b = row["original_bright_first_at"] - 0.15, row["original_last_bright_at"]
            current = [e for e in x5 if lo_b <= e["peak_t"] <= hi_b and e.get("onset_report_eligible")]
            c_on = None
            if len(current) == 1:
                after = bisect.bisect_right(below11_first, current[0]["onset_lower_last_at"])
                if after < len(below11_first):
                    c_on = below11_first[after] - current[0]["onset_lower_last_at"]
            by[p].append({"status": "scheduled", "delay": issue - original,
                          "past_next_onset": nxt is not None and issue >= nxt,
                          "c_end": f["last_at"] - below11[m] if m >= 0 else None, "c_on": c_on})
        rules[rule] = {p: {"original": len(v), "status": dict(Counter(x["status"] for x in v)),
                           "median_delay_days": statistics.median(x["delay"] for x in v if x["status"] == "scheduled"),
                           "issued_at_or_after_next_onset_lo": sum(x.get("past_next_onset", False) for x in v)}
                       for p, v in sorted(by.items())}
        if rule == "decisive_abort":
            cadence = {p: [x for x in v if x["status"] == "scheduled"] for p, v in by.items()}
    result["schedules"] = rules
    median_gap = math.exp(LOG_MEDIAN_M2)
    fisher = (1 + SIGMA_M2 ** 2) * math.exp(2 * SIGMA_M2 ** 2) / (SIGMA_M2 ** 2 * median_gap ** 2)
    ceiling = {"assumptions": "lognormal location Fisher information at the frozen M2 working scale; "
                              "small-shift approximation; exact report ordering at the m=11 crossings; physical "
                              "rise/decline times not mark-dependent beyond physics; history coefficient planning "
                              "value 0.38; per-issue shift bound c_end + b*(c_on + previous c_end), squared",
               "fisher_per_day2": fisher, "history_coefficient": B_HISTORY}
    for p in ("development", "evaluation"):
        issued = cadence[p]
        shifts = []
        for prev, cur in zip(issued, issued[1:]):
            if None not in (prev["c_end"], cur["c_end"], cur["c_on"]):
                shifts.append(cur["c_end"] + B_HISTORY * (cur["c_on"] + prev["c_end"]))
        bound = fisher / 2 * statistics.fmean(s * s for s in shifts)
        ceiling[p] = {"anchor_cadence_gap_days": dist([x["c_end"] for x in issued if x["c_end"] is not None]),
                      "onset_cadence_gap_days": dist([x["c_on"] for x in issued if x["c_on"] is not None]),
                      "shift_bound_days": dist(shifts), "ceiling": bound}
    result["cadence_ceiling_planning"] = ceiling
    return result


def block_structure():
    def icc(pairs):
        groups = defaultdict(list)
        for t, v in pairs:
            groups[math.floor((t - EVAL0) / BLOCK)].append(v)
        groups = {k: v for k, v in groups.items() if len(v) >= 2}
        values = [x for v in groups.values() for x in v]
        n, k = len(values), len(groups)
        grand = statistics.fmean(values)
        msb = sum(len(v) * (statistics.fmean(v) - grand) ** 2 for v in groups.values()) / (k - 1)
        msw = sum((x - statistics.fmean(v)) ** 2 for v in groups.values() for x in v) / (n - k)
        n0 = (n - sum(len(v) ** 2 for v in groups.values()) / n) / (k - 1)
        means = [statistics.fmean(groups[b]) for b in sorted(groups)]
        m = statistics.fmean(means)
        acf = sum((a - m) * (b - m) for a, b in zip(means, means[1:])) / sum((a - m) ** 2 for a in means)
        return {"n": n, "blocks": k, "icc_anova": (msb - msw) / (msb + (n0 - 1) * msw), "block_mean_lag1_acf": acf}

    result = {"scope": "log-mark features only; no outcome, fit or score"}
    for name in ("point_original", "df"):
        features = json.loads((FEATURES / f"{name}-unreleased.json").read_text())
        for label, lo, hi in (("1910_1959", DEV0, EVAL0), ("1960_2017", EVAL0, STOP)):
            result[f"{name}|{label}"] = icc([(f["issue_time"], math.log(f["mark"])) for f in features
                                              if f.get("mark") and f["mark"] > 0 and lo <= f["issue_time"] < hi])
    return result


def c47_c48(rows):
    source = {r["obsID"]: r for r in rows}
    bright, faint = [], []
    for v in json.loads((ROOT / "outputs/r1_censor_audit/visits.json").read_text()):
        if v["value"] is not None:
            if v["value"] <= THR - BAND:
                bright.append(v["t"])
            elif v["cls"] == "F" and v["value"] >= THR + BAND:
                faint.append(v["t"])
        elif v["cls"] == "F":
            limits = [float(source[i]["mag"]) for i in v["ids"] if i in source and source[i]["fainterThan"] == "1"]
            if limits and max(limits) >= THR + BAND:
                faint.append(v["t"])
    bright.sort(); faint.sort()
    episodes = sorted(json.loads((ROOT / "outputs/r1_censor_audit/all-x4-episodes.json").read_text()),
                      key=lambda e: e["peak_t"])

    def between(a, lo, hi):
        return a[bisect.bisect_right(a, lo):bisect.bisect_left(a, hi)]

    counts, widths = Counter(), []
    for left, right in zip(episodes, episodes[1:]):
        if not right["confirmed_event"]:
            continue
        counts["confirmed_with_previous"] += 1
        quiet = between(faint, left["peak_t"], right["peak_t"])
        if not quiet:
            counts["no_quiescence"] += 1
            continue
        upper = next(iter(between(bright, quiet[0], right["peak_t"] + 1e-9)), None)
        if upper is None:
            counts["no_bright"] += 1
            continue
        widths.append(upper - max(t for t in faint if quiet[0] <= t < upper))
    regimes = {"dense": (29.0, 49.0), "sparse": (25.0, 45.0)}
    m1 = {k: integrate.quad(lambda y: math.log(y) / (b - a), a, b)[0] for k, (a, b) in regimes.items()}
    m2 = {k: integrate.quad(lambda y: math.log(y) ** 2 / (b - a), a, b)[0] for k, (a, b) in regimes.items()}
    mu = (m1["dense"] + m1["sparse"]) / 2
    var = (m2["dense"] + m2["sparse"]) / 2 - mu * mu
    coef = (m1["dense"] - m1["sparse"]) / 2

    def gain(k, s):
        a, b = regimes[k]
        return integrate.quad(lambda y: ((math.log(y) - mu) ** 2 - (math.log(y) - mu - s * coef) ** 2)
                              / (2 * var) / (b - a), a, b)[0]

    return ({**counts, "available": len(widths), "representative_width_median_days": statistics.median(widths)},
            {"coefficient": coef, "sigma": math.sqrt(var), "expected_gain": (gain("dense", 1) + gain("sparse", -1)) / 2})


def _ar_blocks(rng, n, phi):
    z = rng.normal(size=n)
    for i in range(1, n):
        z[i] = phi * z[i - 1] + math.sqrt(1 - phi * phi) * z[i]
    return z


def _draw(rng, n, delta, icc_mark, icc_resid, phi):
    block = (np.arange(n) * 6) // n
    bm, be = _ar_blocks(rng, 6, phi), _ar_blocks(rng, 6, phi)
    x = math.sqrt(icc_mark) * bm[block] + math.sqrt(1 - icc_mark) * rng.normal(size=n)
    e = math.sqrt(icc_resid) * be[block] + math.sqrt(1 - icc_resid) * rng.normal(size=n)
    return x, delta * x + e, block


def _interval(scores, clusters):
    estimate = scores.mean()
    sums = np.bincount(clusters, weights=(scores - estimate) / len(scores))
    sums = sums[np.bincount(clusters) > 0]
    g = len(sums)
    se = math.sqrt(g / (g - 1) * float(sums @ sums))
    q = t_dist.ppf(.95, g - 1)
    return estimate - q * se, estimate + q * se


def power(gain, icc_mark, icc_resid, phi, reps, seed, stars=5, development=100, forecasts=1100):
    rng = np.random.default_rng(seed)
    n, delta = forecasts // stars, math.sqrt(2 * gain)
    tallies = {k: [0, 0, 0] for k in ("star_x_6yr", "star_x_12yr", "star_x_18yr", "star")}
    for _ in range(reps):
        xs, rs, intercepts = [], [], []
        for _s in range(stars):
            x, y, _b = _draw(rng, development, delta, icc_mark, icc_resid, phi)
            intercepts.append(y.mean()); xs.append(x); rs.append(y - y.mean())
        x_all, r_all = np.concatenate(xs), np.concatenate(rs)
        coef = max(0.0, float(x_all @ r_all / (x_all @ x_all)))
        scores, star, block = [], [], []
        for s in range(stars):
            x, y, b = _draw(rng, n, delta, icc_mark, icc_resid, phi)
            scores.append(coef * x * (y - intercepts[s]) - .5 * coef * coef * x * x)
            star.append(np.full(n, s)); block.append(b)
        scores, star, block = map(np.concatenate, (scores, star, block))
        target = coef * delta - .5 * coef * coef
        for key, clusters in (("star_x_6yr", star * 6 + block), ("star_x_12yr", star * 3 + block // 2),
                              ("star_x_18yr", star * 2 + block // 3), ("star", star)):
            lo, hi = _interval(scores, clusters)
            tally = tallies[key]
            tally[0] += lo > 0
            if coef > 0:
                tally[1] += 1
                tally[2] += lo <= target <= hi
    return {k: {"confirmation_rate": v[0] / reps,
                "confirmation_exact95": [float(beta_dist.ppf(.025, v[0], reps - v[0] + 1)) if v[0] else 0.0,
                                         float(beta_dist.ppf(.975, v[0] + 1, reps - v[0])) if v[0] < reps else 1.0],
                "nonidentity_coverage90": v[2] / v[1] if v[1] else None, "nonidentity_fits": v[1]}
            for k, v in tallies.items()}


def main():
    rows = load_rows()
    c47, c48 = c47_c48(rows)
    out = {"label": "Claude R2a/c review and R2b rule diagnostics; gain-free on SS Cyg <2018; aggregates only",
           "schedule_and_cadence": schedules(rows), "mark_block_structure": block_structure(),
           "C47_window_selection_with_limits": c47, "C48_quadrature": c48,
           "power_reimplementation": {
               "design": "5 balanced stars, 100 development and 220 test forecasts each, six blocks per star, "
                         "pooled nonnegative OLS offset, per-star intercepts; CR1 t(G-1) one-sided 5%",
               "core_g0.010": power(.010, 0, 0, 0, 4000, 20261109),
               "serial_g0.010_icc_m0.5_e0.1_phi0.7": power(.010, .5, .1, .7, 4000, 20261110),
               "null_serial_icc_m0.5_e0.1_phi0.7": power(0.0, .5, .1, .7, 4000, 20261111),
               "correlated_g0.010_icc_m0.5_e0.1_phi0": power(.010, .5, .1, 0, 3000, 34),
               "serial_g0.010_icc_m0.05_e0.1_phi0.7": power(.010, .05, .1, .7, 3000, 41),
               "serial_g0.010_icc_m0.10_e0.2_phi0.7": power(.010, .10, .2, .7, 3000, 42),
               "serial_g0.010_icc_m0.20_e0.2_phi0.7": power(.010, .20, .2, .7, 3000, 43)}}
    json.dump(out, sys.stdout, indent=1, default=float)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
