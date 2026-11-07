#!/usr/bin/env python3
"""Reproduce conditional endpoint-error examples without an empirical D–Q correlation."""

import csv
import json
import math
from pathlib import Path
import statistics as st

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with (ROOT / "data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    f = lambda r, k: float(r[k]) if r[k] else None
    clean = [r for r in rows if r["event_class"] == "normal" and r["onset_earliest_jd"] and r["end_latest_jd"]
             and f(r, "onset_latest_jd") - f(r, "onset_earliest_jd") < 4]
    on = {r["event_id"]: (f(r, "onset_earliest_jd") + f(r, "onset_envelope_end_jd"))/2 for r in clean}
    end = {r["event_id"]: (f(r, "end_envelope_start_jd") + f(r, "end_latest_jd"))/2 for r in clean}
    pairs = [(r, n) for r, n in zip(rows, rows[1:]) if r["event_id"] in end and n["event_id"] in on
             and r["missed_event_possible"] == "no"]
    sd_d = st.stdev(end[key] - on[key] for key in on)
    sd_q = st.stdev(on[n["event_id"]] - end[r["event_id"]] for r, n in pairs)
    variance = st.mean((f(r, "end_latest_jd") - f(r, "end_envelope_start_jd"))**2/12 for r in clean)
    shift = lambda v, rho: (rho*sd_d*sd_q-v)/math.sqrt((sd_d**2+v)*(sd_q**2+v))-rho
    examples = [{"hypothetical_raw_rho": rho, "uniform_shift": shift(variance, rho),
                 "endpoint_extremes_shift": shift(3*variance, rho)} for rho in (0.0, 0.13, 0.223)]
    print(json.dumps({"uniform_end_error_variance_d2": variance, "duration_scale_d": sd_d,
                      "gap_scale_d": sd_q, "duration_scale_events": len(clean), "gap_scale_pairs": len(pairs),
                      "unverified_gap_scale_pairs": sum(r["consecutive_with_next"] != "verified" for r, n in pairs),
                      "independent_centered_end_error_examples": examples,
                      "same_sd_correlated_error_counterexample_rho": math.sqrt(variance)/math.sqrt(sd_d**2+variance),
                      "scope": "conditional analytical sensitivities and a counterexample; no empirical correlation or partial coefficient calculated"}, indent=2))


if __name__ == "__main__":
    main()
