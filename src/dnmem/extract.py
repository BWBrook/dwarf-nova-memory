"""Candidate SS Cyg event extractors for open-era injection/recovery (A05).

Observer-balanced: one observer's estimates within a visit become one vote.
Boundaries use strict-time adjacency, so a tied bright/faint epoch lies inside
an interval, never at an endpoint, and no interval has zero width. These are
development candidates, not a frozen extractor.
"""

from __future__ import annotations

import math
from statistics import median

THRESHOLD = 10.0
VISIT_SPAN = 0.15
SPLIT_GAP = 4.0
MIN_QUIET_NIGHTS = 3


def observer(row: dict) -> str:
    return (row.get("obsName") or "").strip().casefold() or row["by"]


def visits(rows: list[dict], threshold: float = THRESHOLD) -> list[dict]:
    usable = sorted((r for r in rows if r["band"] == "Vis." and r["val"] == "V"),
                    key=lambda r: (float(r["JD"]), r["obsID"]))
    by_observer: dict[str, list[dict]] = {}
    for row in usable:
        by_observer.setdefault(observer(row), []).append(row)
    out = []
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
                label = "B" if value <= threshold else "F"
            elif max(limits) >= threshold:
                value, label = None, "F"
            else:
                continue
            out.append({"t": median(float(r["JD"]) for r in group), "cls": label, "value": value,
                        "observer": who, "ids": [r["obsID"] for r in group]})
    return sorted(out, key=lambda v: (v["t"], v["ids"][0]))


def _nights(votes: list[dict]) -> dict[int, list[dict]]:
    nights: dict[int, list[dict]] = {}
    for vote in votes:
        nights.setdefault(math.floor(vote["t"]), []).append(vote)
    return nights


def _runs(keys: list[int], keep, split_gap: float) -> list[tuple[list[int], bool]]:
    runs, current, split = [], [], False
    for k in keys:
        if not keep(k):
            if current:
                runs.append((current, split))
            current, split = [], False
            continue
        if current and k - current[-1] > split_gap:
            runs.append((current, split))
            current, split = [], True
        current.append(k)
    if current:
        runs.append((current, split))
    return runs


def _episode(votes: list[dict], inside: list[dict], gap_split: bool) -> dict:
    bright = [v for v in inside if v["cls"] == "B"]
    first_b, last_b = bright[0]["t"], bright[-1]["t"]
    peak = min(bright, key=lambda v: (v["value"], v["t"]))
    faint_all = [v["t"] for v in votes if v["cls"] == "F"]
    f_before = [v["t"] for v in inside if v["cls"] == "F" and v["t"] < peak["t"]]
    f_after = [v["t"] for v in inside if v["cls"] == "F" and v["t"] > peak["t"]]
    pivot_on = max(f_before) if f_before else None
    pivot_end = min(f_after) if f_after else None
    onset_hi = min(v["t"] for v in bright if v["t"] > pivot_on) if pivot_on is not None else first_b
    end_lo = max(v["t"] for v in bright if v["t"] < pivot_end) if pivot_end is not None else last_b
    seen, detected = {bright[0]["observer"]}, None
    for v in bright[1:]:
        if v["observer"] not in seen:
            detected = v["t"]
            break
    confirm_seen, confirmed = set(), None
    for v in votes:
        if v["t"] > last_b and v["cls"] == "F":
            confirm_seen.add(v["observer"])
            if len(confirm_seen) == 2:
                confirmed = v["t"]
                break
    return {"onset_lo": max((t for t in faint_all if t < first_b), default=None), "onset_hi": onset_hi,
            "end_lo": end_lo, "end_hi": min((t for t in faint_all if t > last_b), default=None),
            "peak_t": peak["t"], "peak_mag": peak["value"], "detected": detected, "confirmed": confirmed,
            "n_bright_observers": len({v["observer"] for v in bright}), "gap_split": gap_split,
            "confirmed_event": len({v["observer"] for v in bright}) >= 2}


def x1_vote_episodes(rows: list[dict], threshold: float = THRESHOLD, split_gap: float = SPLIT_GAP,
                     min_quiet: int = MIN_QUIET_NIGHTS) -> list[dict]:
    """Night label by observer-vote majority; episodes are non-faint night runs holding a bright night.

    Runs separated by at most `min_quiet` nights merge: SS Cyg has no quiescence that short, so a
    lone faint-majority night inside a decline tail does not start a new outburst.
    """
    votes = visits(rows, threshold)
    nights = _nights(votes)
    label = {}
    for k, vs in nights.items():
        nb = sum(v["cls"] == "B" for v in vs)
        label[k] = "B" if 2 * nb > len(vs) else "F" if 2 * nb < len(vs) else "M"
    runs = [(run, split) for run, split in _runs(sorted(nights), lambda k: label[k] != "F", split_gap)
            if any(label[k] == "B" for k in run)]
    merged: list[tuple[list[int], bool]] = []
    for run, split in runs:
        if merged and not split and run[0] - merged[-1][0][-1] <= min_quiet:
            previous, previous_split = merged.pop()
            run = previous + [k for k in sorted(nights) if previous[-1] < k < run[0]] + run
            split = previous_split
        merged.append((run, split))
    episodes = []
    for run, split in merged:
        inside = sorted((v for k in run for v in nights[k]), key=lambda v: (v["t"], v["ids"][0]))
        episodes.append(_episode(votes, inside, split))
    return episodes


def x2_median_hysteresis(rows: list[dict], low: float = 9.7, high: float = 10.3, cross: float = THRESHOLD,
                         split_gap: float = SPLIT_GAP) -> list[dict]:
    """Nightly median of per-observer values (faint limits as +inf); enter at <= low, leave at >= high."""
    votes = visits(rows, cross)
    nights = _nights(votes)
    level, when = {}, {}
    for k, vs in nights.items():
        per_observer: dict[str, list[float]] = {}
        for v in vs:
            per_observer.setdefault(v["observer"], []).append(math.inf if v["value"] is None else v["value"])
        level[k] = median(median(x) for x in per_observer.values())
        when[k] = median(v["t"] for v in vs)
    keys, state, inside = sorted(nights), False, set()
    for k in keys:
        state = level[k] <= low if not state else level[k] < high
        if state:
            inside.add(k)
    episodes = []
    for run, split in _runs(keys, lambda k: k in inside, split_gap):
        before = [k for k in keys if k < run[0] and level[k] > cross]
        after = [k for k in keys if k > run[-1] and level[k] > cross]
        first = min(k for k in keys if k > (before[-1] if before else -math.inf) and level[k] <= cross)
        last = max(k for k in keys if k < (after[0] if after else math.inf) and level[k] <= cross)
        peak = min(run, key=lambda k: (level[k], k))
        observers = {v["observer"] for k in run for v in nights[k] if v["cls"] == "B"}
        episodes.append({"onset_lo": when[before[-1]] if before else None, "onset_hi": when[first],
                         "end_lo": when[last], "end_hi": when[after[0]] if after else None,
                         "peak_t": when[peak], "peak_mag": level[peak], "detected": None, "confirmed": None,
                         "n_bright_observers": len(observers), "gap_split": split,
                         "confirmed_event": len(observers) >= 2})
    return episodes


def longest_quiet_gap(vote_times: list[float], start: float, stop: float) -> float:
    """Longest spacing between sorted informative vote times in [start, stop], anchored at both ends."""
    from bisect import bisect_left, bisect_right
    inner = vote_times[bisect_right(vote_times, start):bisect_left(vote_times, stop)]
    times = [start] + inner + [stop]
    return max(b - a for a, b in zip(times, times[1:]))
