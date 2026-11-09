"""Exploratory R1 observation summaries for unchanged point-end forecasts."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass
import math
from statistics import median
import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad
from scipy.special import log_ndtr, logsumexp
from scipy.stats import spearmanr, t as student_t

from dnmem.directional_forecast import DirectionalBundle
from dnmem.extract import MIN_QUIET_NIGHTS, _nights, _runs
from dnmem.extract_x3 import BAND, LEVEL, ONSET_PRIOR, SPLIT_GAP, WINDOW, _cdf, _clip, _quantile
from dnmem.extract_x4 import crossing_posterior

ORIGIN = 2436934.5
BLOCK_DAYS = 2191.5
STOP = 2458119.5
VARIANTS = ("decisive_report", "x4_kernel", "saved_point")
LOG_2PI = math.log(2 * math.pi)
NUMERIC_TOL = 1e-8


def reconstruct_onsets(rows, episodes, votes, threshold=10.0):
    """Recover X4 clips/fit points using every episode, including unconfirmed ones."""
    groups = defaultdict(list)
    for vote in votes:
        if vote["value"] is not None:
            groups[(vote["observer"], math.floor(vote["t"]))].append(vote)
    estimates = sorted((median(v["t"] for v in g), median(v["value"] for v in g))
                       for g in groups.values())
    estimate_times = [p[0] for p in estimates]
    limits = {r["obsID"]: float(r["mag"]) for r in rows if r.get("fainterThan") == "1"}
    far_faint = sorted(v["t"] for v in votes if v["cls"] == "F" and
                       (v["value"] if v["value"] is not None else
                        max((limits[i] for i in v["ids"] if i in limits), default=-math.inf))
                       >= threshold + BAND)
    far_bright = sorted(v["t"] for v in votes
                        if v["value"] is not None and v["value"] <= threshold - BAND)
    nights = _nights(votes)
    night_keys = sorted(nights)
    labels = {k: ("B" if 2 * sum(v["cls"] == "B" for v in vs) > len(vs) else
                  "F" if 2 * sum(v["cls"] == "B" for v in vs) < len(vs) else "M")
              for k, vs in nights.items()}
    runs = [(run, split) for run, split in _runs(night_keys, lambda k: labels[k] != "F", SPLIT_GAP)
            if any(labels[k] == "B" for k in run)]
    merged = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            previous_run, previous_split = merged.pop()
            run = previous_run + [k for k in night_keys if previous_run[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    if len(merged) != len(episodes):
        raise ValueError("raw detection episode count differs")
    faint_times = sorted(v["t"] for v in votes if v["cls"] == "F")
    if any(b["peak_t"] < a["peak_t"] for a, b in zip(episodes, episodes[1:])):
        raise ValueError("all episodes must retain frozen peak order")
    result, confirmed_index = [], 0
    for i, episode in enumerate(episodes):
        previous = episodes[i - 1]["peak_t"] if i else -math.inf
        peak = episode["peak_t"]
        bf = far_bright[bisect_right(far_bright, previous):bisect_right(far_bright, peak)]
        ff = far_faint[bisect_right(far_faint, previous):bisect_left(far_faint, peak)]
        first_bright, last_faint = min(bf, default=peak), max(ff, default=previous)
        fa = far_faint[bisect_right(far_faint, previous):bisect_left(far_faint, first_bright)]
        br = far_bright[bisect_right(far_bright, last_faint):bisect_right(far_bright, peak)]
        a, b = max(fa, default=None), min(br, default=None)
        inside = sorted((v for k in merged[i][0] for v in nights[k]), key=lambda v: (v["t"], v["ids"][0]))
        bright = [v for v in inside if v["cls"] == "B"]
        raw_peak = min(bright, key=lambda v: (v["value"], v["t"]))
        if raw_peak["t"] != peak:
            raise ValueError("raw detection peak differs")
        first_b = bright[0]["t"]
        before = bisect_left(faint_times, first_b)
        adjacency_lo = faint_times[before - 1] if before else None
        pivot = max((v["t"] for v in inside if v["cls"] == "F" and v["t"] < peak), default=None)
        adjacency_hi = min(v["t"] for v in bright if pivot is None or v["t"] > pivot)
        lower = max((adjacency_lo if adjacency_lo is not None else adjacency_hi) - WINDOW,
                    previous)
        upper = min(adjacency_hi + WINDOW, peak)
        points = [p for p in estimates[bisect_right(estimate_times, lower):
                                     bisect_right(estimate_times, upper)]
                  if abs(p[1] - threshold) <= BAND]
        comps = crossing_posterior(points, threshold, -1, ONSET_PRIOR)
        raw, fitted, estimate = None, (adjacency_lo, adjacency_hi), None
        if comps is not None:
            tail = (1 - LEVEL) / 2
            raw = (_quantile(comps, tail), _quantile(comps, 1 - tail))
            fitted = _clip(raw, a, b)
            estimate = _quantile(comps, (_cdf(comps, fitted[0]) + _cdf(comps, fitted[1])) / 2)
            estimate = min(max(estimate, fitted[0]), fitted[1])
        elif None not in fitted:
            estimate = sum(fitted) / 2
        if fitted != (episode["onset_lo"], episode["onset_hi"]) or estimate != episode["onset_t"]:
            raise ValueError(f"onset reconstruction differs at all-episode index {i}")
        result.append({"all_index": i, "confirmed_index": confirmed_index if episode["confirmed_event"] else None,
                       "clip_lo": a, "clip_hi": b, "points": points, "components": comps,
                       "raw_fit_interval": raw, "clip_conflict": bool(raw is not None and
                           ((a is not None and raw[1] <= a) or (b is not None and raw[0] >= b))),
                       "adjacency": [adjacency_lo, adjacency_hi]})
        confirmed_index += bool(episode["confirmed_event"])
    return result


def set_route(a, b, issue, cutoff):
    if a is None or b is None:
        return {"status": "missing_clip"}
    if not math.isfinite(a) or not math.isfinite(b):
        return {"status": "nonfinite_clip"}
    if a >= b:
        return {"status": "reversed_clip"}
    if b <= issue:
        return {"status": "overtaken"}
    if a <= issue:
        return {"status": "ambiguous_survival"}
    if b <= cutoff:
        return {"status": "usable", "kind": "interval", "onset_lo": a, "onset_hi": b}
    return {"status": "usable", "kind": "right_censored",
            "censor_at": a if a < cutoff else cutoff,
            "straddle": a < cutoff < b}


def point_route(point, issue, cutoff):
    if point is None or not math.isfinite(point):
        return {"status": "missing_point"}
    if point <= issue:
        return {"status": "overtaken"}
    if point <= cutoff:
        return {"status": "usable", "kind": "point", "point": point}
    return {"status": "usable", "kind": "right_censored", "censor_at": cutoff}


def stopping_cutoffs(ledger, vote_times, stop=STOP):
    times = sorted(vote_times)
    if any(b["issue_time"] <= a["issue_time"] for a, b in zip(ledger, ledger[1:])):
        raise ValueError("ledger issues must be strictly increasing")
    result = {}
    for i, feature in enumerate(ledger):
        issue = feature["issue_time"]
        before = bisect_right(times, issue)
        anchors = [times[before - 1] if before else issue] + times[before:] + [stop]
        hole = next((max(a, issue) for a, b in zip(anchors, anchors[1:])
                     if b - a > 7 and b > issue and a < stop), None)
        next_issue = ledger[i + 1]["issue_time"] if i + 1 < len(ledger) else None
        stops = [(t, reason) for t, reason in ((hole, "coverage"), (next_issue, "superseded"),
                                              (stop, "record_end")) if t is not None]
        cutoff, reason = min(stops)
        result[feature["emission_index"]] = {"cutoff": max(cutoff, issue), "reason": reason}
    return result


@dataclass(frozen=True)
class CalendarForecast:
    anchor: float
    issue: float
    mu: float
    sigma: float

    def logsf(self, time):
        wait = time - self.anchor
        return 0.0 if wait <= 0 else float(log_ndtr(-(math.log(wait) - self.mu) / self.sigma))

    def logpdf(self, time):
        wait = time - self.anchor
        if time <= self.issue or wait <= 0:
            return -math.inf
        z = (math.log(wait) - self.mu) / self.sigma
        return -0.5 * z * z - math.log(wait * self.sigma) - 0.5 * LOG_2PI - self.logsf(self.issue)

    def score(self, route):
        if route["kind"] == "point":
            return self.logpdf(route["point"])
        if route["kind"] == "right_censored":
            return self.logsf(route["censor_at"]) - self.logsf(self.issue)
        a, b = route["onset_lo"], route["onset_hi"]
        if a < self.issue or b <= a:
            raise ValueError("invalid event support")
        za = (math.log(a - self.anchor) - self.mu) / self.sigma if a > self.anchor else -math.inf
        zb = (math.log(b - self.anchor) - self.mu) / self.sigma
        return normal_logmass(za, zb) - self.logsf(self.issue)


def calendar_forecast(spec, feature, selected):
    if spec["endpoint_mode"] != "point":
        raise ValueError("R1b requires the frozen point-end primary")
    if selected == "R0":
        model, anchor = spec["r0"], feature["issue_time"]
    else:
        model, anchor = spec["models"][selected], feature["end_t"]
    mu = float(model["intercept"])
    for name, coefficient in model["coefficients"].items():
        if name == "previous_gap":
            x = (math.log(feature["previous_gap"]) - model["centers"][name]) / model["scales"][name]
        elif name == "earlier_level":
            gaps = feature.get("earlier_gaps") or []
            level = sum(gaps) / len(gaps) if gaps else model["centers"][name]
            x = (level - model["centers"][name]) / model["scales"][name]
        elif name == "beta":
            x = (math.log(anchor - feature["onset_t"]) - model["centers"]["mark"]) / model["scales"]["mark"]
        else:
            raise ValueError(f"unsupported frozen primary term {name}")
        mu += coefficient * x
    return CalendarForecast(float(anchor), float(feature["issue_time"]), mu, float(model["sigma"]))


def normal_logmass(a, b):
    if not a < b:
        raise ValueError("normal interval has no support")
    hi, lo = (float(log_ndtr(-a)), float(log_ndtr(-b))) if a >= 0 else (float(log_ndtr(b)), float(log_ndtr(a)))
    if lo == -math.inf:
        return hi
    if lo >= hi:
        raise ValueError("normal interval probability cannot be resolved")
    return hi + math.log(-math.expm1(lo - hi))


def kernel_score(forecast, components, a, b):
    if not components or not forecast.issue < a < b:
        raise ValueError("kernel requires finite post-issue clip support")
    comps = np.asarray(components, dtype=float)
    if (comps.ndim != 2 or comps.shape[1] != 3 or not np.all(np.isfinite(comps))
            or np.any(comps[:, 0] < 0) or np.any(comps[:, 2] <= 0)):
        raise ValueError("invalid kernel components")
    if abs(float(comps[:, 0].sum()) - 1) > 1e-12:
        raise ValueError("kernel weights are not normalized")
    zero_weights = int(np.sum(comps[:, 0] == 0))
    comps = comps[comps[:, 0] > 0]
    logweights, means, sds = np.log(comps[:, 0]), comps[:, 1], comps[:, 2]
    logmass = float(logsumexp([w + normal_logmass((a - m) / s, (b - m) / s)
                              for w, m, s in zip(logweights, means, sds)]))
    splits = {float(a), float(b)}
    for mean, sd in zip(means, sds):
        splits.update(float(mean + z * sd) for z in (-12, -8, -4, -2, 0, 2, 4, 8, 12)
                      if a < mean + z * sd < b)
    mode = forecast.anchor + math.exp(forecast.mu - forecast.sigma ** 2)
    if a < mode < b:
        splits.add(mode)
    splits = sorted(splits)

    def log_integrand(time):
        logq = float(logsumexp(logweights - np.log(sds) - 0.5 * LOG_2PI
                              - 0.5 * ((time - means) / sds) ** 2))
        return logq + forecast.logpdf(time)

    probes = splits + [(lo + hi) / 2 for lo, hi in zip(splits, splits[1:])]
    scale = max(log_integrand(t) for t in probes)
    if not math.isfinite(scale):
        raise ValueError("kernel has zero numerical integrand support")

    def integrand(time):
        return math.exp(log_integrand(time) - scale)

    with warnings.catch_warnings():
        warnings.simplefilter("error", IntegrationWarning)
        pieces = [quad(integrand, lo, hi, epsabs=1e-12, epsrel=1e-10, limit=100)
                  for lo, hi in zip(splits, splits[1:])]
    adaptive = math.fsum(p[0] for p in pieces)
    error = math.fsum(p[1] for p in pieces)
    fixed = []
    lower_edges, upper_edges = np.asarray(splits[:-1]), np.asarray(splits[1:])
    midpoints, halfwidths = (lower_edges + upper_edges) / 2, (upper_edges - lower_edges) / 2
    for nodes in (32, 64, 128):
        xs, ws = np.polynomial.legendre.leggauss(nodes)
        times = midpoints[:, None] + halfwidths[:, None] * xs[None, :]
        wait = times - forecast.anchor
        logq = logsumexp(logweights - np.log(sds) - 0.5 * LOG_2PI
                        - 0.5 * ((times[:, :, None] - means) / sds) ** 2, axis=2)
        logf = (-0.5 * ((np.log(wait) - forecast.mu) / forecast.sigma) ** 2
                - np.log(wait * forecast.sigma) - 0.5 * LOG_2PI - forecast.logsf(forecast.issue))
        fixed.append(float(np.sum(halfwidths * (np.exp(logq + logf - scale) @ ws))))
    if min(adaptive, *fixed) <= 0 or not all(math.isfinite(x) for x in [adaptive, *fixed]):
        raise ValueError("kernel quadrature has no finite positive support")
    logs = [math.log(x) for x in fixed]
    discrepancy = abs(math.log(adaptive) - logs[-1])
    convergence = abs(logs[-1] - logs[-2])
    if discrepancy > NUMERIC_TOL or convergence > NUMERIC_TOL or error / adaptive > NUMERIC_TOL:
        raise ValueError(f"kernel quadrature failed: adaptive/GL={discrepancy:g}, GL convergence={convergence:g}, relative error={error/adaptive:g}")
    return scale + math.log(adaptive) - logmass, {
        "log_clip_mass": logmass, "partitions": len(splits) - 1,
        "zero_weight_components": zero_weights,
        "adaptive_relative_error": error / adaptive, "adaptive_vs_gl128_log_error": discrepancy,
        "gl64_vs_gl128_log_error": convergence, "gl32_vs_gl64_log_error": abs(logs[1] - logs[0]),
        "tail_policy": "all Gaussian tails inside the finite clip retained; none discarded"}


def cluster_summary(rows, field="gain"):
    if not rows:
        return {"n": 0, "estimable": False}
    values = [float(r[field]) for r in rows]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("nonfinite paired score")
    mean = math.fsum(values) / len(rows)
    blocks = defaultdict(list)
    for row, value in zip(rows, values):
        if row["issue_time"] < ORIGIN:
            raise ValueError("issuance predates cluster origin")
        blocks[math.floor((row["issue_time"] - ORIGIN) / BLOCK_DAYS)].append(value)
    result = {"n": len(rows), "blocks": len(blocks), "estimate": mean, "estimable": len(blocks) > 1}
    if len(blocks) > 1:
        se = math.sqrt(len(blocks) / (len(blocks) - 1) * math.fsum(
            (math.fsum(v) - len(v) * mean) ** 2 for v in blocks.values())) / len(rows)
        radius = float(student_t.ppf(.95, len(blocks) - 1)) * se
        result.update(se=se, lower90=mean - radius, upper90=mean + radius, df=len(blocks) - 1)
    return result


def subset_summary(rows):
    usable = [r for r in rows if r.get("gain") is not None]
    result = {"usable": len(usable), "status_counts": dict(Counter(r["status"] for r in rows)),
              "routing_counts": dict(Counter(r.get("kind", "unavailable") for r in rows)),
              "original_to_alternative_kind": dict(Counter(f"{r['original_kind']}->{r.get('kind', 'unavailable')}" for r in rows)),
              "identity_count": sum(r["status"] == "identical_forecast" for r in rows),
              "alternative": cluster_summary(usable), "matched_primary": cluster_summary(usable, "primary_gain"),
              "paired_change": cluster_summary([dict(r, delta=r["gain"] - r["primary_gain"]) for r in usable], "delta")}
    if len(usable) > 1 and len({r["gain"] for r in usable}) > 1 and len({r["primary_gain"] for r in usable}) > 1:
        rho = spearmanr([r["gain"] for r in usable], [r["primary_gain"] for r in usable])
        result["spearman_primary"] = {"rho": float(rho.statistic), "p_descriptive": float(rho.pvalue)}
    else:
        result["spearman_primary"] = None
    return result


def score_alternatives(spec, ledger, evidence, primary, episodes, reconstructed, cutoffs):
    bundle = DirectionalBundle.from_dict(spec)
    by_feature = {r["emission_index"]: r for r in ledger}
    by_evidence = {r["emission_index"]: r for r in evidence}
    confirmed = [(e, reconstructed[i]) for i, e in enumerate(episodes) if e["confirmed_event"]]
    results = {name: [] for name in VARIANTS}
    for saved in primary:
        if saved.get("gain_M3_M2") is None:
            continue
        index = saved["emission_index"]
        feature, original = by_feature[index], by_evidence[index]
        issue, cutoff = feature["issue_time"], cutoffs[index]["cutoff"]
        candidate = next(((e, r) for e, r in confirmed if e["peak_t"] > feature["emitted_at"]
                          and e["onset_hi"] is not None and e["onset_hi"] > feature["emitted_at"]), None)
        if original["kind"] == "interval" and (candidate is None or
                candidate[1]["confirmed_index"] != original["onset_index"]):
            raise ValueError("original candidate association mismatch")
        routes = [bundle.route(feature, name) for name in ("M2", "M3")]
        if routes != [saved["M2_route"], saved["M3_route"]]:
            raise ValueError("frozen route mismatch")
        identical = routes[0] == routes[1]
        forecasts = [] if identical else [calendar_forecast(spec, feature, r) for r in routes]
        for name in VARIANTS:
            base = {"emission_index": index, "issue_time": issue, "original_kind": original["kind"],
                    "primary_gain": saved["gain_M3_M2"], "gain": None, "scores": None,
                    "forecast_routes": routes, "cutoff": cutoff, "cutoff_reason": cutoffs[index]["reason"]}
            if candidate is None:
                route = {"status": "usable", "kind": "right_censored", "censor_at": cutoff}
                reconstruction = None
            else:
                episode, reconstruction = candidate
                route = point_route(episode["onset_t"], issue, cutoff) if name == "saved_point" else set_route(
                    reconstruction["clip_lo"], reconstruction["clip_hi"], issue, cutoff)
                if name == "x4_kernel" and route["status"] == "usable" and route["kind"] == "interval" and reconstruction["components"] is None:
                    route = {"status": "missing_kernel"}
                base.update(all_episode_index=reconstruction["all_index"],
                            clip_conflict=reconstruction["clip_conflict"],
                            missing_clip=reconstruction["clip_lo"] is None or reconstruction["clip_hi"] is None,
                            missing_kernel=reconstruction["components"] is None)
            base.update(route)
            if identical:
                if float(saved["gain_M3_M2"]) != 0:
                    raise ValueError("identical frozen forecasts have nonzero saved contrast")
                base.update(observation_status=route["status"], status="identical_forecast", gain=0.0)
            elif route["status"] == "usable":
                try:
                    if name == "x4_kernel" and route["kind"] == "interval":
                        scored = [kernel_score(f, reconstruction["components"], route["onset_lo"], route["onset_hi"])
                                  for f in forecasts]
                        values = [s[0] for s in scored]
                        base["integration"] = [s[1] for s in scored]
                    else:
                        values = [f.score(route) for f in forecasts]
                    if not all(math.isfinite(v) for v in values):
                        raise ValueError("nonfinite alternative score")
                    base.update(scores=values, gain=values[1] - values[0])
                except (ValueError, ArithmeticError, IntegrationWarning) as exc:
                    base.update(status="numerical_failure", numerical_failure=str(exc))
            results[name].append(base)
    common = set.intersection(*(set(r["emission_index"] for r in rows if r["gain"] is not None)
                                for rows in results.values()))
    summaries = {name: subset_summary(rows) for name, rows in results.items()}
    return results, {"variants": summaries, "common_subset": {
        name: subset_summary([r for r in rows if r["emission_index"] in common])
        for name, rows in results.items()}, "original_population": len(results[VARIANTS[0]]),
        "common_usable": len(common), "block_origin": ORIGIN, "block_days": BLOCK_DAYS,
        "interpretation": "Exploratory working-score compatibility sensitivities; no latent-onset propriety claim"}
