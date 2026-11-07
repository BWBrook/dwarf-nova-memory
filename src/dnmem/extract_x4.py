"""X4: X3 with a systematic timing floor, single-observer confirmation and margin arming (A04f).

X3 (`extract_x3.py`, frozen at `c0353c0`) failed A04e. A04f traced the failure to
three mechanisms, and X4 changes only those:

1. **Interval calibration.** X3's crossing posterior treated observer errors as
   independent, so intervals narrowed as 1/sqrt(n) and undercovered at large n.
   X4 adds a shared error of SYSTEMATIC mag to the mean level near the crossing.
2. **Confirmation.** X3 confirmed an episode only with bright votes from two
   distinct observers. X4 also confirms one observer's episode when that observer
   reports it bright on at least two nights, once at least CONFIRM_MARGIN mag
   brighter than the threshold, and no other observer reports it at least
   CONFIRM_MARGIN mag faint on any of those nights.
3. **Operational confirmation.** `causal_confirmations` is the observation-time
   rule. It arms only on bright evidence at least ARM_MARGIN mag past the
   threshold, so near-threshold noise in a decline tail cannot re-arm it after
   an emission. X4 episodes carry no retrospective `confirmed` field.

SYSTEMATIC was chosen on Claude's training family (smooth morphology), not on
the A04e benchmark. Everything else is X3's.
"""

from __future__ import annotations

from collections import defaultdict
import math
from statistics import median

from dnmem.extract import MIN_QUIET_NIGHTS, THRESHOLD, VISIT_SPAN, _episode, _nights, _runs, visits
from dnmem.extract_x3 import (BAND, CONFIRM_MARGIN, END_PRIOR, GRID, LEVEL, NU0, ONSET_PRIOR, SIGMA0,
                              SPLIT_GAP, WINDOW, _cdf, _clip, _faint_level, _quantile)

SYSTEMATIC = 0.05
ARM_MARGIN = 0.5
DEFINITION_VERSION = "a04f-x4-v1"


def crossing_posterior(points: list[tuple[float, float]], threshold: float, sign: int,
                       prior: tuple[float, float]) -> list[tuple[float, float, float]] | None:
    """X3's slope-mixture posterior for the crossing time, with a shared level error added."""
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
    var = (NU0 * SIGMA0 ** 2 + rss) / (NU0 + max(n - 2, 0))
    level_sd = math.sqrt(var / n + SYSTEMATIC ** 2)
    comps = []
    for k in range(GRID):
        z = -3.0 + 6.0 * k / (GRID - 1)
        s = sign * med * math.exp(sdlog * z)
        logw = -0.5 * z * z - (sxx * (s - ols) ** 2 / (2 * var) if sxx > 0 else 0.0)
        comps.append((logw, tbar + (threshold - ybar) / s, level_sd / abs(s)))
    top = max(c[0] for c in comps)
    weights = [math.exp(c[0] - top) for c in comps]
    total = sum(weights)
    return [(w / total, mu, sd) for w, (_, mu, sd) in zip(weights, comps)]


def _boundary(points, threshold, sign, prior, clip_lo, clip_hi, adjacency):
    comps = crossing_posterior(points, threshold, sign, prior)
    if comps is None:
        lo, hi = adjacency
        return lo, hi, None if None in adjacency else (lo + hi) / 2, "adjacency"
    tail = (1 - LEVEL) / 2
    lo, hi = _clip((_quantile(comps, tail), _quantile(comps, 1 - tail)), clip_lo, clip_hi)
    estimate = _quantile(comps, (_cdf(comps, lo) + _cdf(comps, hi)) / 2)
    return lo, hi, min(max(estimate, lo), hi), "fit"


def _single_observer_confirmed(votes: list[dict], level: dict[int, float], lo: float, hi: float,
                               threshold: float) -> bool:
    bright = [v for v in votes if v["cls"] == "B" and lo <= v["t"] <= hi]
    observers = {v["observer"] for v in bright}
    if len(observers) != 1:
        return False
    nights = {math.floor(v["t"]) for v in bright}
    if len(nights) < 2 or min(v["value"] for v in bright) > threshold - CONFIRM_MARGIN:
        return False
    return not any(v["observer"] not in observers and math.floor(v["t"]) in nights
                   and level[id(v)] >= threshold + CONFIRM_MARGIN for v in votes)


def x4_episodes(rows: list[dict], threshold: float = THRESHOLD) -> list[dict]:
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
        episode = _episode(votes, inside, split)
        del episode["confirmed"]
        episodes.append(episode)

    groups: dict[tuple[str, int], list[dict]] = {}
    for v in votes:
        if v["value"] is not None:
            groups.setdefault((v["observer"], math.floor(v["t"])), []).append(v)
    estimates = sorted((median(v["t"] for v in g), median(v["value"] for v in g)) for g in groups.values())
    limits = {r["obsID"]: float(r["mag"]) for r in rows if r.get("fainterThan") == "1"}
    level = {id(v): _faint_level(v, limits) for v in votes}
    far_faint = [v["t"] for v in votes if v["cls"] == "F" and level[id(v)] >= threshold + BAND]
    far_bright = [v["t"] for v in votes if v["value"] is not None and v["value"] <= threshold - BAND]

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
        e["confirmation"] = "observers" if e["confirmed_event"] else None
        if not e["confirmed_event"]:
            span_lo = e["onset_lo"] if e["onset_lo"] is not None else peak - 3
            span_hi = e["end_hi"] if e["end_hi"] is not None else peak + 3
            if _single_observer_confirmed(votes, level, span_lo, span_hi, threshold):
                e["confirmed_event"], e["confirmation"] = True, "single_observer"
    return episodes


def _closed_visits(rows: list[dict], threshold: float) -> list[dict]:
    """Observer visits, available only when their 0.15 d window closes."""
    by_observer = defaultdict(list)
    for row in sorted((r for r in rows if r["band"] == "Vis." and r["val"] == "V"),
                      key=lambda r: (float(r["JD"]), r["obsID"])):
        by_observer[(row.get("obsName") or "").strip().casefold() or row["by"]].append(row)
    closed = []
    for who, own in by_observer.items():
        groups: list[list[dict]] = []
        for row in own:
            if groups and float(row["JD"]) - float(groups[-1][0]["JD"]) <= VISIT_SPAN:
                groups[-1].append(row)
            else:
                groups.append([row])
        for group in groups:
            positive = [float(r["mag"]) for r in group if r["fainterThan"] == "0"]
            limits = [float(r["mag"]) for r in group if r["fainterThan"] == "1"]
            if positive:
                value = median(positive)
                cls, faint_level = ("B" if value <= threshold else "F"), value
            elif max(limits) >= threshold:
                value, cls, faint_level = None, "F", max(limits)
            else:
                continue
            first = float(group[0]["JD"])
            closed.append({"closed_at": first + VISIT_SPAN, "night": math.floor(first), "observer": who,
                           "cls": cls, "value": value, "faint_level": faint_level})
    return sorted(closed, key=lambda v: (v["closed_at"], v["observer"]))


def causal_confirmations(rows: list[dict], threshold: float = THRESHOLD) -> list[dict]:
    """Observation-time end confirmations: permanent, never revised by later data.

    Bright votes clear faint evidence. The rule arms when two distinct observers,
    or one observer on two nights, report at least ARM_MARGIN mag brighter than
    the threshold. Once armed, the first two distinct observers at least
    CONFIRM_MARGIN mag fainter emit a confirmation; unarmed, the same evidence
    closes the provisional episode silently. Visits closing at the same time are
    one batch, and any bright vote in a batch suppresses its faint votes.
    """
    strong: dict[str, set[int]] = defaultdict(set)
    bright_observers: set[str] = set()
    faint_observers: set[str] = set()
    bright_first_at = last_bright_at = faint_first_at = None
    armed = False
    emissions = []
    visits_ = _closed_visits(rows, threshold)
    i = 0
    while i < len(visits_):
        close = visits_[i]["closed_at"]
        j = i
        while j < len(visits_) and visits_[j]["closed_at"] == close:
            j += 1
        batch, i = visits_[i:j], j
        bright = [v for v in batch if v["cls"] == "B"]
        if bright:
            faint_observers.clear()
            faint_first_at = None
            if not bright_observers:
                bright_first_at = close
            for v in bright:
                bright_observers.add(v["observer"])
                if v["value"] <= threshold - ARM_MARGIN:
                    strong[v["observer"]].add(v["night"])
            last_bright_at = close
            armed = armed or len(strong) >= 2 or any(len(n) >= 2 for n in strong.values())
            continue
        faint = [v for v in batch if v["faint_level"] >= threshold + CONFIRM_MARGIN]
        if not faint:
            continue
        if not faint_observers:
            faint_first_at = close
        faint_observers.update(v["observer"] for v in faint)
        if len(faint_observers) < 2:
            continue
        if armed:
            emissions.append({"emission_index": len(emissions), "emitted_at": close,
                              "bright_first_at": bright_first_at, "last_bright_at": last_bright_at,
                              "faint_first_at": faint_first_at, "bright_observer_count": len(bright_observers),
                              "strong_bright_observer_count": len(strong),
                              "faint_observer_count": len(faint_observers)})
        strong.clear()
        bright_observers.clear()
        faint_observers.clear()
        bright_first_at = last_bright_at = faint_first_at = None
        armed = False
    return emissions
