"""Claude's independent R2b review diagnostics: recomputed gains, efficient mark score tests,
era-drift decomposition, observing-rate structure, clock-by-mark crossing and development fits.

Exploratory and post-result. Reads only the retained, ignored R2b run outputs (SS Cyg before
JD 2458119.5). Writes aggregates only. Usage:

    uv run --quiet python scripts/r2b_claude_review_checks.py \
        > data/provenance/r2b_claude_review/checks.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.special import log_ndtr
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs" / "r2b_real_5fb69c6"
ORIGIN = 2436934.5
LOG_SQRT_2PI = 0.5 * math.log(2 * math.pi)
MODELS = {
    "df": ["B0.duration", "B1.duration", "B2.duration", "B2.flux", "B2.rate", "B2.cadence"],
    "point_at_df": ["B0.duration", "B1.duration", "B2.duration", "B2.flux"],
    "point_original": ["B0.duration", "B1.duration", "B2.duration", "B2.flux"],
}


def load(name):
    return json.loads((RUN / name).read_text())


def log_phi(x):
    return -0.5 * x * x - LOG_SQRT_2PI


def logdiff(a, b):
    return a + math.log(-math.expm1(b - a))


def route(sig, issue):
    if sig["kind"] == "right_censored":
        return ("censor", sig["censor_at"])
    lo, hi, cut = sig["onset_lo"], sig["onset_hi"], sig["fixed_cutoff"]
    if hi <= cut:
        return ("interval", lo, hi)
    return ("censor", lo if lo < cut else cut)


def score_and_derivative(anchor, issue, mu, sigma, outcome):
    """Conditional lognormal working log score and its derivative in the location."""
    def logsf(w):
        x = (math.log(w) - mu) / sigma
        return float(log_ndtr(-x)), x

    if outcome[0] == "interval":
        xl = (math.log(outcome[1] - anchor) - mu) / sigma
        xh = (math.log(outcome[2] - anchor) - mu) / sigma
        if xl >= 0:
            mass = logdiff(float(log_ndtr(-xl)), float(log_ndtr(-xh)))
        else:
            mass = logdiff(float(log_ndtr(xh)), float(log_ndtr(xl)))
        deriv = (math.exp(log_phi(xl) - mass) - math.exp(log_phi(xh) - mass)) / sigma
    else:
        mass, xc = logsf(outcome[1] - anchor)
        deriv = math.exp(log_phi(xc) - mass) / sigma
    age = issue - anchor
    if age > 0:
        la, xa = logsf(age)
        mass -= la
        deriv -= math.exp(log_phi(xa) - la) / sigma
    return mass, deriv


def block(issue, years):
    return math.floor((issue - ORIGIN) / (years * 365.25))


def cr1_mean(values, issues, years):
    groups = {}
    for v, t in zip(values, issues):
        groups.setdefault(block(t, years), []).append(v)
    n, g = len(values), len(groups)
    mean = sum(values) / n
    var = g / (g - 1) * sum(sum(x - mean for x in vs) ** 2 for vs in groups.values()) / n ** 2
    se = math.sqrt(var)
    q = float(student_t.ppf(.95, g - 1))
    return {"mean": mean, "se": se, "lower90": mean - q * se, "upper90": mean + q * se, "blocks": g,
            "t": mean / se if se > 0 else None}


def score_test(contrib, issues, years):
    """Uncentred cluster-robust score statistic for H0: mark coefficient zero."""
    groups = {}
    for c, t in zip(contrib, issues):
        groups.setdefault(block(t, years), []).append(c)
    g = len(groups)
    s = sum(contrib)
    var = g / (g - 1) * sum(sum(vs) ** 2 for vs in groups.values())
    z = s / math.sqrt(var) if var > 0 else None
    return {"statistic": z, "blocks": g, "one_sided_p_t": float(student_t.sf(z, g - 1)) if z is not None else None}


def mark_value(feature, marker):
    if marker == "duration":
        v = feature.get("mark")
    elif marker == "flux":
        v = (feature.get("flux_proxy") or {}).get("value_threshold_flux_days")
    elif marker == "rate":
        v = (feature.get("observer_rate") or {}).get("value_per_day")
    else:
        v = feature.get("mark")
    return float(v) if v is not None and math.isfinite(float(v)) and float(v) > 0 else None


def rows_for(clock, model, params, features):
    marker = model.split(".")[1]
    p = params[clock][model]
    beta, center, scale = p["beta"], p["mark_center"], p["mark_scale"]
    feats = {f["emission_index"]: f for f in features}
    out, max_err, shift_err = [], 0.0, 0.0
    for r in load(f"{clock}-{model}-scores-unreleased.json"):
        if r["status"] != "scored":
            continue
        b, m = r["base_clock"], r["marked_clock"]
        outcome = route(r["outcome_signature"], b["issue"])
        base, ub = score_and_derivative(b["anchor"], b["issue"], b["mu"], b["sigma"], outcome)
        marked, _ = score_and_derivative(m["anchor"], m["issue"], m["mu"], m["sigma"], outcome)
        max_err = max(max_err, abs(base - r["baseline_score"]), abs(marked - r["marked_score"]))
        f = feats[r["emission_index"]]
        raw = mark_value(f, marker if marker != "cadence" else "duration")
        usable = r["base_route"] in ("B0", "B1", "B2") and raw is not None
        z = (math.log(raw) - center) / scale if usable else 0.0
        if marker != "cadence":
            shift_err = max(shift_err, abs((m["mu"] - b["mu"]) - beta * z))
        out.append({"emission_index": r["emission_index"], "issue": r["issue_time"], "gain": marked - base,
                    "base": base, "u": ub, "z": z, "has_mark": usable, "raw_mark": raw,
                    "anchor": b["anchor"], "mu": b["mu"], "sigma": b["sigma"], "outcome": outcome,
                    "route": r["base_route"], "signature": r["outcome_signature"]})
    return out, max_err, shift_err


def information(rows, h=1e-4):
    total = 0.0
    for r in rows:
        if not r["has_mark"]:
            continue
        _, up = score_and_derivative(r["anchor"], r["issue"], r["mu"] + h, r["sigma"], r["outcome"])
        _, um = score_and_derivative(r["anchor"], r["issue"], r["mu"] - h, r["sigma"], r["outcome"])
        total += r["z"] ** 2 * (-(up - um) / (2 * h))
    return total


def demeaned(rows, years):
    groups = {}
    for r in rows:
        if r["has_mark"]:
            groups.setdefault(block(r["issue"], years), []).append(r["z"])
    means = {k: sum(v) / len(v) for k, v in groups.items()}
    return [(r["z"] - means[block(r["issue"], years)]) if r["has_mark"] else 0.0 for r in rows], means


def causal_centred(rows, history, k=10):
    """Mark minus the mean of the previous k available marks in the same clock population."""
    series = sorted(history, key=lambda v: v[0])
    out = []
    for r in rows:
        if not r["has_mark"]:
            out.append(0.0)
            continue
        past = [z for t, z in series if t < r["issue"]][-k:]
        out.append(r["z"] - sum(past) / len(past) if past else 0.0)
    return out


def resolved_at(outcome):
    return outcome[2] if outcome[0] == "interval" else outcome[1]


def gain_with(rows, beta, zs, shifts=None):
    out = []
    for r, z, c in zip(rows, zs, shifts or [0.0] * len(rows)):
        base, _ = score_and_derivative(r["anchor"], r["issue"], r["mu"] + c, r["sigma"], r["outcome"])
        marked, _ = score_and_derivative(r["anchor"], r["issue"], r["mu"] + c + beta * z, r["sigma"], r["outcome"])
        out.append((marked - base, base))
    return out


def causal_recalibration(rows, k=20, h=1e-4):
    """Location correction from the previous k evaluation forecasts resolved by issue (one Newton step)."""
    stats = []
    for r in rows:
        _, up = score_and_derivative(r["anchor"], r["issue"], r["mu"] + h, r["sigma"], r["outcome"])
        _, um = score_and_derivative(r["anchor"], r["issue"], r["mu"] - h, r["sigma"], r["outcome"])
        stats.append((resolved_at(r["outcome"]), r["u"], -(up - um) / (2 * h)))
    shifts = []
    for r in rows:
        past = sorted((s for s in stats if s[0] <= r["issue"]), key=lambda s: s[0])[-k:]
        info = sum(s[2] for s in past)
        shifts.append(sum(s[1] for s in past) / info if past and info > 0 else 0.0)
    return shifts


def recalibrated(rows, shifts, beta, issues):
    pairs = gain_with(rows, beta, [r["z"] for r in rows], shifts)
    us = [score_and_derivative(r["anchor"], r["issue"], r["mu"] + c, r["sigma"], r["outcome"])[1]
          for r, c in zip(rows, shifts)]
    contrib = [r["z"] * u for r, u in zip(rows, us)]
    return {"mean_base_score": sum(b for _, b in pairs) / len(pairs),
            "mean_base_score_original": sum(r["base"] for r in rows) / len(rows),
            "gain_six": cr1_mean([g for g, _ in pairs], issues, 6),
            "gain_twelve": cr1_mean([g for g, _ in pairs], issues, 12),
            "score_test_six": score_test(contrib, issues, 6),
            "score_test_twelve": score_test(contrib, issues, 12),
            "score_test_independent": sum(contrib) / math.sqrt(sum(c * c for c in contrib)),
            "mean_location_score": sum(us) / len(us)}


def analyse(clock, model, params, features, history):
    rows, max_err, shift_err = rows_for(clock, model, params, features)
    issues = [r["issue"] for r in rows]
    contrib = [r["z"] * r["u"] for r in rows]
    info = information(rows)
    beta_dev = params[clock][model]["beta"]
    gains = [r["gain"] for r in rows]
    zbar = sum(r["z"] for r in rows if r["has_mark"]) / max(1, sum(r["has_mark"] for r in rows))
    s = sum(contrib)
    gain6, gain12 = cr1_mean([r["gain"] for r in rows], issues, 6), cr1_mean([r["gain"] for r in rows], issues, 12)
    zw6, means6 = demeaned(rows, 6)
    zc = causal_centred(rows, history)
    between = [means6[block(r["issue"], 6)] * r["u"] if r["has_mark"] else 0.0 for r in rows]
    beta_eval = s / info if info > 0 else None
    n_mark = sum(r["has_mark"] for r in rows)
    result = {
        "scored": len(rows), "with_mark": n_mark,
        "recompute_max_abs_error": max_err, "mark_shift_max_abs_error": shift_err if model.split(".")[1] != "cadence" else None,
        "development_beta": params[clock][model]["beta"],
        "gain_six": gain6, "gain_twelve": gain12,
        "score_test_independent": s / math.sqrt(sum(c * c for c in contrib)),
        "score_test_six": score_test(contrib, issues, 6), "score_test_twelve": score_test(contrib, issues, 12),
        "score_test_centred_six": centred_score(contrib, issues, 6),
        "score_test_centred_twelve": centred_score(contrib, issues, 12),
        "evaluation_one_step_beta": beta_eval,
        "evaluation_one_step_kl_per_forecast": beta_eval ** 2 * info / (2 * len(rows)) if beta_eval else None,
        "within_block_score_six": score_test([z * r["u"] for z, r in zip(zw6, rows)], issues, 6),
        "between_block_share_of_statistic": sum(between) / s if s else None,
        "causal_centred_score_six": score_test([z * r["u"] for z, r in zip(zc, rows)], issues, 6),
        "causal_centred_score_twelve": score_test([z * r["u"] for z, r in zip(zc, rows)], issues, 12),
        "mean_base_location_score": sum(r["u"] for r in rows) / len(rows),
        "base_location_score_six": cr1_mean([r["u"] for r in rows], issues, 6),
        "mean_mark_z_evaluation": sum(r["z"] for r in rows if r["has_mark"]) / n_mark if n_mark else None,
        "gain_t_independent": (sum(gains) / len(gains)) / (float(np.std(gains, ddof=1)) / math.sqrt(len(gains))),
        "gain_evaluation_centred_mark_six": cr1_mean(
            [g for g, _ in gain_with(rows, beta_dev, [(r["z"] - zbar) if r["has_mark"] else 0.0 for r in rows])], issues, 6),
        "gain_causal_centred_mark_six": cr1_mean([g for g, _ in gain_with(rows, beta_dev, zc)], issues, 6),
        "causal_base_recalibration_k20": recalibrated(rows, causal_recalibration(rows), beta_dev, issues),
    }
    shifts = causal_recalibration(rows)
    u_recal = [score_and_derivative(r["anchor"], r["issue"], r["mu"] + c, r["sigma"], r["outcome"])[1]
               for r, c in zip(rows, shifts)]
    guarded = [z * u for z, u in zip(zc, u_recal)]
    result["drift_guarded"] = {
        "definition": "causally centred mark (minus mean of previous ten marks) scored at the causally recalibrated base",
        "score_uncentred_six": score_test(guarded, issues, 6)["statistic"],
        "score_uncentred_twelve": score_test(guarded, issues, 12)["statistic"],
        "score_centred_six": centred_score(guarded, issues, 6),
        "score_centred_twelve": centred_score(guarded, issues, 12),
        "score_independent": sum(guarded) / math.sqrt(sum(c * c for c in guarded)),
        "gain_six": cr1_mean([g for g, _ in gain_with(rows, beta_dev, zc, shifts)], issues, 6),
        "gain_twelve": cr1_mean([g for g, _ in gain_with(rows, beta_dev, zc, shifts)], issues, 12),
    }
    if beta_eval and beta_eval > beta_dev / 2:
        result["predicted_score_to_gain_ratio"] = beta_eval / (beta_eval - beta_dev / 2)
    result["observed_centred_score_to_gain_t_ratio_six"] = result["score_test_centred_six"] / gain6["t"]
    result["design_effect_centred_six_raw"] = (result["score_test_independent"] / result["score_test_centred_six"]) ** 2
    result["design_effect_centred_six_guarded"] = (result["drift_guarded"]["score_independent"]
                                                   / result["drift_guarded"]["score_centred_six"]) ** 2
    result["within_block_score_centred_six"] = centred_score([z * r["u"] for z, r in zip(zw6, rows)], issues, 6)
    result["causal_centred_score_centred_six"] = centred_score([z * r["u"] for z, r in zip(zc, rows)], issues, 6)
    if gain6["t"] and result["score_test_six"]["statistic"]:
        result["score_to_gain_t_ratio_six"] = result["score_test_six"]["statistic"] / gain6["t"]
    return result, rows


def eras(rows_by_key):
    table = {}
    for key, rows in rows_by_key.items():
        groups = {}
        for r in rows:
            groups.setdefault(block(r["issue"], 6), []).append(r)
        table[key] = [{"block": b, "n": len(v),
                       "mean_z": float(np.mean([r["z"] for r in v if r["has_mark"]])) if any(r["has_mark"] for r in v) else None,
                       "mean_u": float(np.mean([r["u"] for r in v])),
                       "mean_gain": float(np.mean([r["gain"] for r in v]))} for b, v in sorted(groups.items())]
        zs = [x["mean_z"] for x in table[key] if x["mean_z"] is not None]
        us = [x["mean_u"] for x in table[key] if x["mean_z"] is not None]
        table[key + ":block_corr_z_u"] = float(np.corrcoef(zs, us)[0, 1])
    return table


def rate_structure(features_by_period):
    out = {}
    for period, feats in features_by_period.items():
        triples = []
        for f in feats:
            span, rate = mark_value(f, "duration"), mark_value(f, "rate")
            nights = (f.get("observer_rate") or {}).get("observer_nights")
            if span and rate and nights:
                triples.append((f["issue_time"], math.log(span), math.log(rate), math.log(nights)))
        a = np.array(triples)
        c = np.corrcoef(a.T)
        out[period] = {"n": len(a), "corr_log_span_log_rate": c[1, 2], "corr_log_span_log_observer_nights": c[1, 3],
                       "corr_time_log_rate": c[0, 2], "corr_time_log_span": c[0, 1],
                       "mean_log_span": float(a[:, 1].mean()), "mean_log_rate": float(a[:, 2].mean())}
    return out


def era_levels():
    """Mean measured log previous gap and log mark by twelve-year block (features only)."""
    out = {}
    for clock in ("df", "point_at_df"):
        for period in ("development", "evaluation"):
            groups = {}
            for f in load(f"{clock}-{period}-features-unreleased.json"):
                gap = f.get("previous_gap")
                if gap and f.get("previous_gap_covered") is True:
                    mark = mark_value(f, "duration")
                    groups.setdefault(block(f["issue_time"], 12), []).append((math.log(gap), math.log(mark) if mark else None))
            allv = [v for vs in groups.values() for v in vs]
            out[f"{clock}:{period}"] = {
                "n": len(allv), "mean_log_gap": float(np.mean([g for g, _ in allv])),
                "mean_log_mark": float(np.mean([m for _, m in allv if m is not None])),
                "blocks": [{"block": b, "n": len(vs), "mean_log_gap": float(np.mean([g for g, _ in vs])),
                            "geometric_mean_gap_days": float(math.exp(np.mean([g for g, _ in vs]))),
                            "mean_log_mark": float(np.mean([m for _, m in vs if m is not None]))}
                           for b, vs in sorted(groups.items())]}
    return out


def crossing(params, rows, features):
    """Score tests for each clock's base paired with the other population's mark (same issues)."""
    out = {}
    pairs = {"df_base_with_point_duration": ("df", "point_at_df"), "point_base_with_df_span": ("point_at_df", "df")}
    for label, (base_clock, mark_clock) in pairs.items():
        p = params[mark_clock]["B2.duration"]
        feats = {f["emission_index"]: f for f in features[mark_clock]}
        for rung in ("B0", "B1", "B2"):
            base_rows = rows[(base_clock, rung + ".duration")]
            contrib, issues = [], []
            for r in base_rows:
                raw = mark_value(feats[r["emission_index"]], "duration")
                z = (math.log(raw) - p["mark_center"]) / p["mark_scale"] if raw and r["route"] == rung else 0.0
                contrib.append(z * r["u"])
                issues.append(r["issue"])
            out[f"{label}:{rung}"] = {"six": score_test(contrib, issues, 6), "twelve": score_test(contrib, issues, 12)}
    return out


def centred_score(contrib, issues, years):
    groups = {}
    for c, t in zip(contrib, issues):
        groups.setdefault(block(t, years), []).append(c)
    g, n, s = len(groups), len(contrib), sum(contrib)
    var = g / (g - 1) * sum((sum(vs) - s * len(vs) / n) ** 2 for vs in groups.values())
    return s / math.sqrt(var)


def log_density(w, mu, sigma):
    x = (math.log(w) - mu) / sigma
    return log_phi(x) - math.log(w * sigma)


def mixed_bounds(rows, beta):
    lows, highs = [], []
    for r in rows:
        sig = r["signature"]
        lo, hi, cut = sig["onset_lo"], sig["onset_hi"], sig["fixed_cutoff"]
        a, mb, s, mm = r["anchor"], r["mu"], r["sigma"], r["mu"] + beta * r["z"]
        age = r["issue"] - a

        def lsf(w, mu):
            return float(log_ndtr(-(math.log(w) - mu) / s)) if w > 0 else 0.0

        cond = lsf(age, mm) - lsf(age, mb)

        def dens(t):
            return log_density(t - a, mm, s) - log_density(t - a, mb, s) - cond

        if lo is None or hi is None:
            cut = sig["censor_at"] if sig.get("censor_at") is not None else cut
        surv = (lsf(cut - a, mm) - lsf(cut - a, mb)) - cond
        if lo is None or hi is None:
            vals = [surv]
        elif hi <= cut:
            vals = [dens(lo), dens(hi)]
        elif lo >= cut:
            vals = [surv]
        else:
            vals = [dens(lo), dens(cut), surv]
        lows.append(min(vals))
        highs.append(max(vals))
    return {"cases": len(lows), "lower_mean": sum(lows) / len(lows), "upper_mean": sum(highs) / len(highs)}


def claim_checks(params, rows):
    from scipy.integrate import quad
    mu, s = math.log(40.0), 0.4

    def kl(age, shift):
        sp = float(np.exp(log_ndtr(-(math.log(age) - mu) / s)))
        sq = float(np.exp(log_ndtr(-(math.log(age - shift) - mu) / s))) if age > shift else 1.0

        def f(t, d):
            w = t - d
            return math.exp(log_density(w, mu, s)) if w > 0 else 0.0

        def integrand(t):
            p = f(t, 0) / sp
            return p * (math.log(p) - math.log(f(t, shift) / sq)) if p > 0 else 0.0

        return quad(integrand, age, math.inf, limit=400, epsabs=1e-14, epsrel=1e-12)[0]

    def j_unconditional():
        def integrand(w):
            x = (math.log(w) - mu) / s
            score = (x / s + 1) / w
            return math.exp(log_density(w, mu, s)) * score * score
        return quad(integrand, 0, math.inf, limit=400)[0]

    counts = {}
    for name in ("df", "point_at_df", "point_original"):
        dev, ev = load(f"{name}-development-features-unreleased.json"), load(f"{name}-evaluation-features-unreleased.json")
        counts[name] = {"development": len(dev), "evaluation": len(ev),
                        "evaluation_anchor_previous_mark": sum(
                            f.get("clock_anchor") is not None and f.get("previous_gap") is not None
                            and f.get("previous_gap_covered") is True and mark_value(f, "duration") is not None for f in ev)}
    df_ev = {f["emission_index"]: f for f in load("df-evaluation-features-unreleased.json")}
    pt_ev = {f["emission_index"]: f for f in load("point_at_df-evaluation-features-unreleased.json")}

    def markable(f):
        return (f.get("clock_anchor") is not None and f.get("previous_gap") is not None
                and f.get("previous_gap_covered") is True and mark_value(f, "duration") is not None)

    counts["jointly_markable"] = sum(markable(df_ev[i]) and markable(pt_ev[i]) for i in df_ev if i in pt_ev)
    j = j_unconditional()
    return {
        "C53_kl_issue_age_2_shift_1": kl(2.0, 1.0), "C53_local_quadratic": j / 2,
        "C53_kl_issue_age_10_shift_9": kl(10.0, 9.0),
        "C54_counts": counts,
        "C57_df_B2_bounds": mixed_bounds(rows[("df", "B2.duration")], params["df"]["B2.duration"]["beta"]),
    }


def development_fits(params):
    from dnmem.r2_models import TimingRule, evidence_score  # noqa: F401  (Codex's frozen code, for base predictions only)
    out = {}
    for clock in ("df", "point_at_df", "point_original"):
        feats = load(f"{clock}-development-features-unreleased.json")
        ev = {e["emission_index"]: e for e in load(f"{clock}-development-evidence-unreleased.json")}
        for rung in ("B0", "B1", "B2"):
            p = params[clock][rung + ".duration"]
            rule = TimingRule.from_dict({**p["timing"], "beta": 0.0})
            contrib, issues, nll, n, dev_rows = [], [], 0.0, 0, []
            for f in feats:
                e = ev[f["emission_index"]]
                if e["kind"] == "excluded" or f.get("clock_anchor") is None:
                    continue
                clock_obj, route_name = rule.predict(f)
                if route_name != rung:
                    continue
                outcome = ("interval", e["onset_lo"], e["onset_hi"]) if e["kind"] == "interval" else ("censor", e["censor_at"])
                if e["kind"] not in ("interval", "right_censored"):
                    continue
                s, u = score_and_derivative(clock_obj.anchor, clock_obj.issue, clock_obj.mu, clock_obj.sigma, outcome)
                nll -= s
                n += 1
                raw = mark_value(f, "duration")
                z = (math.log(raw) - p["mark_center"]) / p["mark_scale"] if raw else 0.0
                contrib.append(z * u)
                issues.append(f["issue_time"])
                dev_rows.append({"anchor": clock_obj.anchor, "issue": clock_obj.issue, "mu": clock_obj.mu,
                                 "sigma": clock_obj.sigma, "outcome": outcome, "u": u, "base": s})
            shifts = causal_recalibration(dev_rows)
            recal = sum(score_and_derivative(r["anchor"], r["issue"], r["mu"] + c, r["sigma"], r["outcome"])[0]
                        for r, c in zip(dev_rows, shifts))
            out[f"{clock}:{rung}"] = {"timing_rows": n, "nll": nll, "nll_causal_recalibrated_k20": -recal,
                                      "score_test_independent": sum(contrib) / math.sqrt(sum(c * c for c in contrib)),
                                      "score_test_six": score_test(contrib, issues, 6)}
    return out


def main():
    sys.path.insert(0, str(ROOT / "src"))
    params = load("parameters-unreleased.json")
    features = {c: load(f"{c}-evaluation-features-unreleased.json") for c in MODELS}
    dev_features = {c: load(f"{c}-development-features-unreleased.json") for c in MODELS}
    results, rows = {}, {}
    for clock, models in MODELS.items():
        for model in models:
            marker = model.split(".")[1]
            p = params[clock][model]
            history = []
            for f in dev_features[clock] + features[clock]:
                raw = mark_value(f, marker if marker != "cadence" else "duration")
                if raw:
                    history.append((f["issue_time"], (math.log(raw) - p["mark_center"]) / p["mark_scale"]))
            results[f"{clock}:{model}"], rows[(clock, model)] = analyse(clock, model, params, features[clock], history)
    h3 = [(a["gain"] - b["gain"], a["issue"]) for a, b in zip(rows[("df", "B2.duration")], rows[("point_at_df", "B2.duration")])
          if a["emission_index"] == b["emission_index"]]
    paired = {}
    for rung in ("B0", "B1", "B2"):
        a_rows = {r["emission_index"]: r for r in rows[("df", rung + ".duration")]}
        b_rows = {r["emission_index"]: r for r in rows[("point_at_df", rung + ".duration")]}
        common = sorted(set(a_rows) & set(b_rows), key=lambda i: a_rows[i]["issue"])
        diffs = [a_rows[i]["gain"] - b_rows[i]["gain"] for i in common]
        paired[rung] = {"n": len(common), "six": cr1_mean(diffs, [a_rows[i]["issue"] for i in common], 6),
                        "twelve": cr1_mean(diffs, [a_rows[i]["issue"] for i in common], 12)}
    report = {
        "scope": "exploratory post-result review of retained R2b outputs; SS Cyg before JD2458119.5; aggregates only",
        "run": str(RUN.relative_to(ROOT)),
        "contrasts": results,
        "paired_clock_difference": paired,
        "h3_pairs": len(h3),
        "era_blocks": eras({"df:B0": rows[("df", "B0.duration")], "df:B2": rows[("df", "B2.duration")],
                            "point_at_df:B0": rows[("point_at_df", "B0.duration")],
                            "df:B2.rate": rows[("df", "B2.rate")]}),
        "era_levels_twelve_year": era_levels(),
        "rate_structure": rate_structure({"development": dev_features["df"], "evaluation": features["df"]}),
        "clock_by_mark_crossing": crossing(params, rows, features),
        "development": development_fits(params),
        "claim_checks": claim_checks(params, rows),
    }
    json.dump(report, sys.stdout, indent=1, default=float)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
