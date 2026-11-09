"""X5 decisive-report windows over unchanged X4 candidates and fitted points.

The selected reports do not establish latent-state containment. Visit medians
select reports; conservative raw time supports define the reported windows.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
import math

from dnmem.extract import THRESHOLD, VISIT_SPAN, visits
from dnmem.extract_x3 import BAND
from dnmem.extract_x4 import x4_episodes

DEFINITION_VERSION = "r2-x5-report-windows-v1"


def decisive_visits(rows: list[dict], threshold: float = THRESHOLD, margin: float = BAND,
                    votes: list[dict] | None = None) -> list[dict]:
    """Preserve frozen visit votes, adding decisive class and raw time support.

    A visit uses the median positive magnitude when any positive estimate
    exists. Only an all-limit visit can use its strongest numerical magnitude
    lower bound. Its first+0.15 clock is the frozen aggregation availability.
    """
    if not math.isfinite(threshold) or not math.isfinite(margin) or margin <= 0:
        raise ValueError("threshold and positive margin must be finite")
    source = {row["obsID"]: row for row in rows}
    if len(source) != len(rows):
        raise ValueError("X5 requires unique source observation IDs")
    result = []
    for vote in visits(rows, threshold) if votes is None else votes:
        if not vote["ids"] or any(identifier not in source for identifier in vote["ids"]):
            raise ValueError("visit refers to missing source observations")
        own = [source[identifier] for identifier in vote["ids"]]
        times = [float(row["JD"]) for row in own]
        value = vote["value"]
        limits = [float(row["mag"]) for row in own if row["fainterThan"] == "1"]
        faint_level = value if value is not None else max(limits, default=-math.inf)
        decisive = ("B" if value is not None and value <= threshold - margin else
                    "F" if vote["cls"] == "F" and faint_level >= threshold + margin else "N")
        first, last = min(times), max(times)
        if (not all(math.isfinite(t) for t in times) or not math.isfinite(faint_level)
                or not first <= vote["t"] <= last or last - first > VISIT_SPAN + 1e-9):
            raise ValueError("visit support violates the frozen aggregation rule")
        result.append({**vote, "decisive": decisive, "faint_level": faint_level,
                       "first_at": first, "last_at": last,
                       "available_at": first + VISIT_SPAN})
    return sorted(result, key=lambda v: (v["t"], v["ids"][0]))


def _window_fields(prefix: str, lower: dict | None, upper: dict | None) -> dict:
    return {
        prefix + "_report_lo": lower["first_at"] if lower else None,
        prefix + "_report_hi": upper["last_at"] if upper else None,
        prefix + "_report_lo_rep": lower["t"] if lower else None,
        prefix + "_report_hi_rep": upper["t"] if upper else None,
        prefix + "_lower_first_at": lower["first_at"] if lower else None,
        prefix + "_lower_last_at": lower["last_at"] if lower else None,
        prefix + "_upper_first_at": upper["first_at"] if upper else None,
        prefix + "_upper_last_at": upper["last_at"] if upper else None,
    }


def x5_episodes(rows: list[dict], threshold: float = THRESHOLD, margin: float = BAND,
                *, episodes: list[dict] | None = None, votes: list[dict] | None = None,
                as_of: float | None = None) -> list[dict]:
    """Add corrected decisive windows; retain all X4 candidates and fitted fields.

    Cached full-record candidates cannot be combined with an as-of cutoff.
    Forecast callers must reconstruct from their prefix, rather than borrow
    future peaks or report membership from a retrospective catalogue.
    """
    if as_of is not None:
        if episodes is not None or votes is not None:
            raise ValueError("as_of reconstruction cannot use cached candidates or visits")
        if not math.isfinite(as_of):
            raise ValueError("as_of must be finite")
        rows = [row for row in rows if float(row["JD"]) <= as_of]
    observed = decisive_visits(rows, threshold, margin, votes)
    candidates = x4_episodes(rows, threshold) if episodes is None else episodes
    if any(right["peak_t"] <= left["peak_t"] for left, right in zip(candidates, candidates[1:])):
        raise ValueError("all-candidate peak times must be strictly increasing")
    faint = [v for v in observed if v["decisive"] == "F"]
    bright = [v for v in observed if v["decisive"] == "B"]
    faint_times, bright_times = [v["t"] for v in faint], [v["t"] for v in bright]
    faint_epochs, bright_epochs = set(faint_times), set(bright_times)
    contested = faint_epochs & bright_epochs
    result = []
    for index, original in enumerate(candidates):
        e = dict(original)
        peak = e["peak_t"]
        previous = candidates[index - 1]["peak_t"] if index else None
        following = candidates[index + 1]["peak_t"] if index + 1 < len(candidates) else math.inf
        before = faint[bisect_right(faint_times, previous):bisect_left(faint_times, peak)] if previous is not None else []
        quiet = before[0] if before else None
        rising = bright[bisect_right(bright_times, quiet["t"]):bisect_right(bright_times, peak)] if quiet else []
        upper = rising[0] if rising else None
        earlier = faint[bisect_left(faint_times, quiet["t"]):bisect_left(faint_times, upper["t"])] if upper else []
        lower = earlier[-1] if earlier else None
        flags = []
        status = ("left_record_boundary" if previous is None else "no_quiescence_report" if quiet is None else
                  "faint_peak" if upper is None and e.get("peak_mag", math.inf) > threshold - margin else
                  "no_decisive_bright_after_quiescence" if upper is None else "available")
        recross = faint[bisect_right(faint_times, upper["t"]):bisect_right(faint_times, peak)] if upper else []
        if lower and upper:
            if lower["last_at"] >= upper["first_at"]:
                flags.append("overlapping_or_touching_visit_support")
            if any(v["t"] in contested for v in (quiet, lower, upper)):
                flags.append("contested_decisive_epoch")
            if quiet["first_at"] <= previous:
                flags.append("quiescence_support_crosses_previous_peak")
            if recross:
                flags.append("decisive_faint_after_bright_before_peak")
        post = faint[bisect_right(faint_times, peak):bisect_left(faint_times, following)]
        end_faint = post[0] if post else None
        ending = bright[bisect_left(bright_times, peak):bisect_left(bright_times, end_faint["t"])] if end_faint else []
        end_bright = ending[-1] if ending else None
        end_flags = []
        end_status = ("no_postpeak_quiescence_report" if end_faint is None else
                      "no_decisive_bright_before_quiescence" if end_bright is None else "available")
        if end_faint and end_bright:
            if end_bright["last_at"] >= end_faint["first_at"]:
                end_flags.append("overlapping_or_touching_visit_support")
            if end_faint["t"] in contested or end_bright["t"] in contested:
                end_flags.append("contested_decisive_epoch")
            if end_faint["last_at"] >= following:
                end_flags.append("end_support_reaches_next_peak")
        later_bright = bright[bisect_right(bright_times, end_faint["t"]):bisect_left(bright_times, following)] if end_faint else []
        span = end_bright["t"] - upper["t"] if upper and end_bright else None
        if span is not None and span < 0:
            flags.append("bright_span_reversed")
            span = None
        e.update(_window_fields("onset", lower, upper))
        e.update(_window_fields("end", end_bright, end_faint))
        e.update({"x5_definition_version": DEFINITION_VERSION, "x5_threshold": threshold,
                  "x5_margin": margin, "all_episode_index": index,
                  "previous_peak_at": previous, "next_peak_at": following if math.isfinite(following) else None,
                  "quiescence_at": quiet["t"] if quiet else None,
                  "quiescence_first_at": quiet["first_at"] if quiet else None,
                  "quiescence_last_at": quiet["last_at"] if quiet else None,
                  "onset_status": status, "onset_flags": flags,
                  "onset_report_available": lower is not None and upper is not None,
                  "onset_report_eligible": status == "available" and not flags,
                  "rise_decisive_faint_after_bright_count": len(recross),
                  "end_status": end_status, "end_flags": end_flags,
                  "end_report_available": end_bright is not None and end_faint is not None,
                  "end_report_eligible": end_status == "available" and not end_flags,
                  "end_decisive_at": end_faint["last_at"] if end_faint else None,
                  "end_decisive_representative_at": end_faint["t"] if end_faint else None,
                  "end_decisive_available_at": end_faint["available_at"] if end_faint else None,
                  "bright_first_at": upper["t"] if upper else None,
                  "bright_last_at": end_bright["t"] if end_bright else None,
                  "bright_first_raw_at": upper["first_at"] if upper else None,
                  "bright_first_raw_last_at": upper["last_at"] if upper else None,
                  "bright_last_raw_first_at": end_bright["first_at"] if end_bright else None,
                  "bright_last_raw_at": end_bright["last_at"] if end_bright else None,
                  "bright_span": span,
                  "post_end_decisive_bright_before_next_peak_count": len(later_bright),
                  "post_end_decisive_bright_before_next_peak": bool(later_bright)})
        result.append(e)
    return result


__all__ = ["DEFINITION_VERSION", "decisive_visits", "x5_episodes"]
