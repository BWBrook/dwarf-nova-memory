"""X3: X1-style event detection with fitted threshold-crossing intervals (A04d).

Detection follows X1: observer-visit votes, a nightly majority label, and
runs of non-faint nights that hold a bright night, with runs at most three
nights apart merged. One change: a run is split only at an observing gap
longer than 7 d. SS Cyg cannot finish an outburst, sit through a quiescence
and rise again in that time.

Each boundary interval is a posterior interval for the time at which a local
straight line crosses the threshold. The line is fitted to observer-night
median estimates within 1 mag of the threshold. Its slope has a log-normal
prior and is integrated over a grid. The scatter comes from the residuals,
shrunk towards 0.25 mag. Votes more than 1 mag from the threshold clip the
interval. The point estimate (`onset_t`, `end_t`) is the posterior median
within the clipped interval. When no estimate lies within 1 mag, the interval
falls back to X1's adjacency bracket and the point estimate to its midpoint;
every vote near it is then far from the threshold.

The 0.99 level was chosen on Claude's A04d training batch to give about 95%
conditional coverage under realistic morphology. It is a calibrated
operating point, not a nominal guarantee.
"""

from __future__ import annotations

import math
from statistics import NormalDist, median

from dnmem.extract import MIN_QUIET_NIGHTS, THRESHOLD, _episode, _nights, _runs, visits

SPLIT_GAP = 7.0
BAND = 1.0
WINDOW = 2.5
SIGMA0 = 0.25
NU0 = 4.0
ONSET_PRIOR = (0.8, 0.8)
END_PRIOR = (0.35, 0.45)
LEVEL = 0.99
GRID = 41
CONFIRM_MARGIN = 0.5
DEFINITION_VERSION = "a04d-x3-v1"

_NORMAL = NormalDist()


def crossing_posterior(points: list[tuple[float, float]], threshold: float, sign: int,
                       prior: tuple[float, float], sigma0: float = SIGMA0, nu0: float = NU0,
                       grid: int = GRID) -> list[tuple[float, float, float]] | None:
    """Posterior for when m(t) = threshold + s (t - t_c) reaches the threshold.

    `sign` is -1 for a rise (magnitude falls) and +1 for a decline. `prior` is the median
    and log-scale SD of |s| in mag/d. The intercept has a flat prior. Given s, t_c is
    Gaussian, so the marginal is a mixture over the slope grid: (weight, mean, sd) triples.
    """
    n = len(points)
    if n == 0:
        return None
    med, sdlog = prior
    tbar = sum(t for t, _ in points) / n
    ybar = sum(y for _, y in points) / n
    sxx = sum((t - tbar) ** 2 for t, _ in points)
    sxy = sum((t - tbar) * (y - ybar) for t, y in points)
    ols = sxy / sxx if sxx > 0 else 0.0
    rss = sum((y - ybar - ols * (t - tbar)) ** 2 for t, y in points) if n >= 3 and sxx > 0 else 0.0
    var = (nu0 * sigma0 ** 2 + rss) / (nu0 + max(n - 2, 0))
    comps = []
    for k in range(grid):
        z = -3.0 + 6.0 * k / (grid - 1)
        s = sign * med * math.exp(sdlog * z)
        logw = -0.5 * z * z - (sxx * (s - ols) ** 2 / (2 * var) if sxx > 0 else 0.0)
        comps.append((logw, tbar + (threshold - ybar) / s, math.sqrt(var / n) / abs(s)))
    top = max(c[0] for c in comps)
    weights = [math.exp(c[0] - top) for c in comps]
    total = sum(weights)
    return [(w / total, mu, sd) for w, (_, mu, sd) in zip(weights, comps)]


def _cdf(comps: list[tuple[float, float, float]], x: float) -> float:
    return sum(w * _NORMAL.cdf((x - mu) / sd) for w, mu, sd in comps)


def _quantile(comps: list[tuple[float, float, float]], p: float) -> float:
    lo = min(mu - 8 * sd for _, mu, sd in comps)
    hi = max(mu + 8 * sd for _, mu, sd in comps)
    for _ in range(50):
        mid = (lo + hi) / 2
        if _cdf(comps, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def crossing_interval(points: list[tuple[float, float]], threshold: float, sign: int,
                      prior: tuple[float, float], level: float = LEVEL) -> tuple[float, float] | None:
    """Central posterior interval for the crossing time, or None without estimates."""
    comps = crossing_posterior(points, threshold, sign, prior)
    if comps is None:
        return None
    tail = (1 - level) / 2
    return _quantile(comps, tail), _quantile(comps, 1 - tail)


def _boundary(points, threshold, sign, prior, clip_lo, clip_hi, adjacency):
    """Interval and point estimate: clipped posterior, or the adjacency bracket without estimates."""
    comps = crossing_posterior(points, threshold, sign, prior)
    if comps is None:
        lo, hi = adjacency
        return lo, hi, None if None in adjacency else (lo + hi) / 2, "adjacency"
    tail = (1 - LEVEL) / 2
    lo, hi = _clip((_quantile(comps, tail), _quantile(comps, 1 - tail)), clip_lo, clip_hi)
    estimate = _quantile(comps, (_cdf(comps, lo) + _cdf(comps, hi)) / 2)
    return lo, hi, min(max(estimate, lo), hi), "fit"


def _faint_level(vote: dict, limits: dict[str, float]) -> float:
    if vote["value"] is not None:
        return vote["value"]
    return max((limits[i] for i in vote["ids"] if i in limits), default=-math.inf)


def _clip(fit: tuple[float, float], lo: float | None, hi: float | None) -> tuple[float, float]:
    clipped = (max(fit[0], lo) if lo is not None else fit[0], min(fit[1], hi) if hi is not None else fit[1])
    if clipped[0] < clipped[1]:
        return clipped
    return (min(fit[0], lo if lo is not None else fit[0]), max(fit[1], hi if hi is not None else fit[1]))


def x3_fitted_episodes(rows: list[dict], threshold: float = THRESHOLD) -> list[dict]:
    votes = visits(rows, threshold)
    nights = _nights(votes)
    label = {}
    for k, vs in nights.items():
        nb = sum(v["cls"] == "B" for v in vs)
        label[k] = "B" if 2 * nb > len(vs) else "F" if 2 * nb < len(vs) else "M"
    runs = [(run, split) for run, split in _runs(sorted(nights), lambda k: label[k] != "F", SPLIT_GAP)
            if any(label[k] == "B" for k in run)]
    merged: list[tuple[list[int], bool]] = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= MIN_QUIET_NIGHTS:
            previous, previous_split = merged.pop()
            run = previous + [k for k in sorted(nights) if previous[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    episodes = []
    for run, split in merged:
        inside = sorted((v for k in run for v in nights[k]), key=lambda v: (v["t"], v["ids"][0]))
        episodes.append(_episode(votes, inside, split))

    groups: dict[tuple[str, int], list[dict]] = {}
    for v in votes:
        if v["value"] is not None:
            groups.setdefault((v["observer"], math.floor(v["t"])), []).append(v)
    estimates = sorted((median(v["t"] for v in g), median(v["value"] for v in g)) for g in groups.values())
    limits = {r["obsID"]: float(r["mag"]) for r in rows if r.get("fainterThan") == "1"}
    level = {id(v): _faint_level(v, limits) for v in votes}
    far_faint = [v["t"] for v in votes if v["cls"] == "F" and level[id(v)] >= threshold + BAND]
    far_bright = [v["t"] for v in votes if v["value"] is not None and v["value"] <= threshold - BAND]
    confirm_faint = [v for v in votes if v["cls"] == "F" and level[id(v)] >= threshold + CONFIRM_MARGIN]

    for i, e in enumerate(episodes):
        prev_peak = episodes[i - 1]["peak_t"] if i else -math.inf
        next_peak = episodes[i + 1]["peak_t"] if i + 1 < len(episodes) else math.inf
        peak = e["peak_t"]
        first_far_b = min((t for t in far_bright if prev_peak < t <= peak), default=peak)
        pre_far_f = max((t for t in far_faint if prev_peak < t < peak), default=prev_peak)
        clip_on = (max((t for t in far_faint if prev_peak < t < first_far_b), default=None),
                   min((t for t in far_bright if pre_far_f < t <= peak), default=None))
        last_far_b = max((t for t in far_bright if peak <= t < next_peak), default=peak)
        post_far_f = min((t for t in far_faint if peak < t < next_peak), default=next_peak)
        clip_end = (max((t for t in far_bright if peak <= t < post_far_f), default=None),
                    min((t for t in far_faint if last_far_b < t < next_peak), default=None))

        adj_on, adj_end = (e["onset_lo"], e["onset_hi"]), (e["end_lo"], e["end_hi"])
        lo = (adj_on[0] if adj_on[0] is not None else adj_on[1]) - WINDOW
        on_pts = [(t, y) for t, y in estimates if max(lo, prev_peak) < t <= min(adj_on[1] + WINDOW, peak)
                  and abs(y - threshold) <= BAND]
        hi = (adj_end[1] if adj_end[1] is not None else adj_end[0]) + WINDOW
        end_pts = [(t, y) for t, y in estimates if max(adj_end[0] - WINDOW, peak) <= t < min(hi, next_peak)
                   and abs(y - threshold) <= BAND]
        e["onset_lo"], e["onset_hi"], e["onset_t"], e["onset_method"] = _boundary(
            on_pts, threshold, -1, ONSET_PRIOR, *clip_on, adj_on)
        e["end_lo"], e["end_hi"], e["end_t"], e["end_method"] = _boundary(
            end_pts, threshold, 1, END_PRIOR, *clip_end, adj_end)
        e["n_onset_fit"], e["n_end_fit"] = len(on_pts), len(end_pts)

        seen, e["confirmed"] = set(), None
        if adj_end[1] is None:
            continue
        last_b = max((v["t"] for v in votes if v["cls"] == "B" and peak <= v["t"] < adj_end[1]), default=peak)
        for v in confirm_faint:
            if last_b < v["t"] < next_peak:
                seen.add(v["observer"])
                if len(seen) == 2:
                    e["confirmed"] = v["t"]
                    break
    return episodes
