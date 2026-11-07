"""Native observation coverage only; no event extraction or predictive association."""

from collections import Counter
import math
from pathlib import Path
from statistics import median

from .aavso import read_acquisition


def combine_acquisitions(paths: list[Path]) -> tuple[list[dict], int]:
    seen, duplicated = {}, 0
    for path in paths:
        rows, _ = read_acquisition(path)
        for row in rows:
            key = row["obsID"]
            if key in seen:
                if seen[key] != row:
                    raise ValueError("conflicting native values for a repeated observation ID")
                duplicated += 1
            else:
                seen[key] = row
    return sorted(seen.values(), key=lambda row: (float(row["JD"]), row["obsID"])), duplicated


def profile(rows: list[dict], start_jd: float, end_jd: float) -> dict:
    if any(not start_jd <= float(row["JD"]) <= end_jd for row in rows):
        raise ValueError("coverage profile contains an out-of-window row")
    visual = [row for row in rows if row["band"] == "Vis." and row["val"] == "V"]
    informative = [row for row in visual if row["fainterThan"] == "0" or float(row["mag"]) >= 10]
    times = sorted({float(row["JD"]) for row in informative})
    gaps = [b-a for a, b in zip(times, times[1:])]
    identity = lambda row: (row.get("obsName") or "").strip().casefold() or row["by"]
    observer_bins = {(identity(row), math.floor(float(row["JD"]))) for row in informative}
    bins = {math.floor(value) for value in times}
    expected_bins = math.floor(end_jd) - math.floor(start_jd) + 1
    return {"native_rows": len(rows), "bands": dict(sorted(Counter(row["band"] for row in rows).items())),
            "validation_flags": dict(sorted(Counter(row["val"] for row in rows).items())),
            "visual_V_rows": len(visual), "informative_visual_V_rows_at_mag10": len(informative),
            "fainter_than_rows": sum(row["fainterThan"] == "1" for row in rows),
            "observer_JD_bin_pairs": len(observer_bins), "observed_JD_bins": len(bins),
            "window_JD_bins": expected_bins, "observed_JD_bin_fraction": len(bins) / expected_bins,
            "repeat_rows_within_observer_JD_bin": len(informative) - len(observer_bins),
            "median_informative_spacing_d": median(gaps) if gaps else None,
            "longest_internal_informative_gap_d": max(gaps) if gaps else None,
            "internal_informative_gaps_over_4d": sum(gap > 4 for gap in gaps),
            "span_before_first_informative_d": times[0] - start_jd if times else None,
            "span_after_last_informative_d": end_jd - times[-1] if times else None,
            "scope": "returned-row coverage; JD bins are noon-to-noon native bins, not verified observing nights; not detection efficiency or usable cycles"}
