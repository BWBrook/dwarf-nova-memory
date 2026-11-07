"""A04 protocol v1: classify native visual rows and bracket bright runs.

Mechanical candidates for annotator review; not a frozen extraction rule.
"""

from __future__ import annotations

THRESHOLD = 10.0
MISS_GAP_DAYS = 4.0
DEFINITION_VERSION = "a04-v1"


def row_class(row: dict, threshold: float = THRESHOLD) -> str:
    mag = float(row["mag"])
    if row["fainterThan"] == "1":
        return "F" if mag >= threshold else "N"
    return "B" if mag <= threshold else "F"


def observer(row: dict) -> str:
    return (row.get("obsName") or "").strip().casefold() or row["by"]


def _first_second_observer(rows: list[dict]) -> dict | None:
    first = observer(rows[0])
    return next((row for row in rows[1:] if observer(row) != first), None)


def candidate_runs(rows: list[dict], threshold: float = THRESHOLD) -> list[dict]:
    usable = sorted((row for row in rows if row["val"] == "V"),
                    key=lambda row: (float(row["JD"]), row["obsID"]))
    informative = [(row, row_class(row, threshold)) for row in usable]
    informative = [(row, label) for row, label in informative if label != "N"]
    runs, i = [], 0
    while i < len(informative):
        if informative[i][1] != "B":
            i += 1
            continue
        j = i
        while j + 1 < len(informative) and informative[j + 1][1] == "B":
            j += 1
        bright = [row for row, _ in informative[i:j + 1]]
        before = informative[i - 1][0] if i > 0 else None
        after = informative[j + 1][0] if j + 1 < len(informative) else None
        faint_after = []
        for row, label in informative[j + 1:]:
            if label == "B":
                break
            faint_after.append(row)
        second = _first_second_observer(bright)
        confirm = _first_second_observer(faint_after) if faint_after else None
        peak = min(bright, key=lambda row: (float(row["mag"]), float(row["JD"])))
        runs.append({
            "onset_earliest": before, "onset_latest": bright[0],
            "end_earliest": bright[-1], "end_latest": after,
            "left_censored": before is None, "right_censored": after is None,
            "onset_detected": second, "end_confirmed": confirm,
            "n_bright": len(bright), "n_bright_observers": len({observer(row) for row in bright}),
            "peak": peak,
        })
        i = j + 1
    return runs


def coverage_gaps(rows: list[dict], threshold: float = THRESHOLD,
                  minimum: float = MISS_GAP_DAYS) -> list[tuple[float, float]]:
    times = sorted(float(row["JD"]) for row in rows
                   if row["val"] == "V" and row_class(row, threshold) != "N")
    return [(a, b) for a, b in zip(times, times[1:]) if b - a > minimum]


def bounds(run: dict, following: dict | None = None) -> dict:
    jd = lambda key, r=run: float(r[key]["JD"]) if r[key] is not None else None
    out = {"duration_min": jd("end_earliest") - jd("onset_latest"), "duration_max": None,
           "gap_min": None, "gap_max": None}
    if not run["left_censored"] and not run["right_censored"]:
        out["duration_max"] = jd("end_latest") - jd("onset_earliest")
    if following is not None and not run["right_censored"] and not following["left_censored"]:
        out["gap_min"] = float(following["onset_earliest"]["JD"]) - jd("end_latest")
        out["gap_max"] = float(following["onset_latest"]["JD"]) - jd("end_earliest")
    return out
