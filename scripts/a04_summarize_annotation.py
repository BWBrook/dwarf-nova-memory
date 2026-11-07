#!/usr/bin/env python3
"""Boundary precision and shared-endpoint error from a committed A04 annotation.

Reads only the annotation CSV. Deliberately reports no duration-gap correlation:
the focal estimand stays unexamined while extraction rules are being fixed.
"""

import argparse
import csv
import math
from pathlib import Path
import statistics as st


def f(row, key):
    return float(row[key]) if row[key] else None


def summarize(rows):
    clean = [r for r in rows if r["event_class"] == "normal" and r["onset_earliest_jd"] and r["end_latest_jd"]
             and f(r, "onset_latest_jd") - f(r, "onset_earliest_jd") < 4.0]
    on_w = [f(r, "onset_envelope_end_jd") - f(r, "onset_earliest_jd") for r in clean]
    end_w = [f(r, "end_latest_jd") - f(r, "end_envelope_start_jd") for r in clean]
    on_v1 = [f(r, "onset_latest_jd") - f(r, "onset_earliest_jd") for r in clean]
    end_v1 = [f(r, "end_latest_jd") - f(r, "end_earliest_jd") for r in clean]
    on_mid = {r["event_id"]: (f(r, "onset_earliest_jd") + f(r, "onset_envelope_end_jd")) / 2 for r in clean}
    end_mid = {r["event_id"]: (f(r, "end_envelope_start_jd") + f(r, "end_latest_jd")) / 2 for r in clean}
    durations = [end_mid[e] - on_mid[e] for e in on_mid]
    gaps = []
    for k, r in enumerate(rows[:-1]):
        nxt = rows[k + 1]
        if r["event_id"] in end_mid and nxt["event_id"] in on_mid and r["missed_event_possible"] == "no":
            gaps.append(on_mid[nxt["event_id"]] - end_mid[r["event_id"]])
    v_end = st.mean(w * w / 12 for w in end_w)
    v_on = st.mean(w * w / 12 for w in on_w)
    v_end_worst = st.mean(w * w / 4 for w in end_w)
    sd_d, sd_q = st.stdev(durations), st.stdev(gaps)
    shift = lambda v: -v / math.sqrt((sd_d ** 2 + v) * (sd_q ** 2 + v))
    conf_lag = [f(r, "end_confirmed_jd") - f(r, "end_latest_jd") for r in clean if r["end_confirmed_jd"]]
    det_lag = [f(r, "onset_detected_jd") - f(r, "onset_latest_jd") for r in clean if r["onset_detected_jd"]]
    types = {t: sum(r["type_cm92_v1"] == t for r in rows) for t in ("long", "short", "ambiguous")}
    q = lambda xs: f"median {st.median(xs):.2f}, max {max(xs):.2f}"
    return {
        "events": len(rows), "clean_events": len(clean), "clean_gap_pairs": len(gaps),
        "types_v1": types,
        "mechanical_fragments_merged": sum(int(r["candidates"].split("-")[-1]) - int(r["candidates"].split("-")[0])
                                           for r in rows),
        "interleaved_events": sum(int(r["n_interleaved_faint"]) > 0 for r in rows),
        "onset_width_v1_d": q(on_v1), "end_width_v1_d": q(end_v1),
        "onset_width_envelope_d": q(on_w), "end_width_envelope_d": q(end_w),
        "sd_end_error_uniform_d": round(math.sqrt(v_end), 3), "sd_onset_error_uniform_d": round(math.sqrt(v_on), 3),
        "sd_duration_mid_d": round(sd_d, 2), "sd_gap_mid_d": round(sd_q, 2),
        "shared_end_corr_shift_at_r0": round(shift(v_end), 4),
        "shared_end_corr_shift_worst_case": round(shift(v_end_worst), 4),
        "shared_end_corr_shift_if_sd_1d": round(shift(1.0), 4),
        "end_confirm_lag_after_first_faint_d": q(conf_lag), "onset_detect_lag_after_first_bright_d": q(det_lag),
        "unverified_consecutive_pairs": sum(r["consecutive_with_next"] == "unverified" for r in rows),
        "missed_event_possible_pairs": sum(r["missed_event_possible"] == "possible" for r in rows),
        "pairs": sum(bool(r["consecutive_with_next"]) for r in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation", type=Path)
    args = parser.parse_args()
    with open(args.annotation, newline="") as handle:
        rows = list(csv.DictReader(handle))
    for key, value in summarize(rows).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
