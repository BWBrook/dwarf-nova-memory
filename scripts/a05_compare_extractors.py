#!/usr/bin/env python3
"""Score candidate extractors against both A04 annotations; profile X1 over the open era.

Needs the gitignored native exports locally. Reports event agreement and
coverage counts only; no duration-gap association is computed.
"""

import argparse
import csv
import json
import math
from pathlib import Path
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import read_acquisition
from dnmem.coverage import combine_acquisitions
from dnmem.extract import longest_quiet_gap, visits, x1_vote_episodes, x2_median_hysteresis

ANN = ROOT / "data/annotations"
F = lambda r, k: float(r[k]) if r.get(k) else None


def references():
    with open(ANN / "a04_ss_cyg_1956_1958_claude_v1.csv", newline="") as h:
        claude = list(csv.DictReader(h))
    with open(ANN / "a04_ss_cyg_1957_adjudication.csv", newline="") as h:
        fixes = {(r["claude_event"], r["boundary"]): r for r in csv.DictReader(h)}
    ref = []
    for r in claude:
        on = [F(r, "onset_earliest_jd"), F(r, "onset_envelope_end_jd")]
        end = [F(r, "end_envelope_start_jd"), F(r, "end_latest_jd")]
        for key, interval in (("onset", on), ("end", end)):
            fix = fixes.get((r["event_id"], key))
            if fix:
                interval[:] = [float(fix["adjudicated_lo_jd"]), float(fix["adjudicated_hi_jd"])]
        ref.append({"id": r["event_id"], "on": on, "end": end, "peak": F(r, "peak_jd"),
                    "confirmed": r["event_class"] == "normal"})
    with open(ANN / "a04_ss_cyg_1957_codex_blind_v1.csv", newline="") as h:
        blind = [{"id": r["event_id"], "on": [F(r, "onset_earliest_jd"), F(r, "onset_latest_jd")],
                  "end": [F(r, "end_earliest_jd"), F(r, "end_latest_jd")], "peak": F(r, "peak_jd"),
                  "confirmed": r["event_class"] == "normal", "censored": r["end_censored"] == "true"}
                 for r in csv.DictReader(h)]
    return ref, blind


def mid(interval):
    return None if None in interval else (interval[0] + interval[1]) / 2


def overlaps(a, b):
    return None not in a + b and max(a[0], b[0]) <= min(a[1], b[1])


def score(episodes, refs, window):
    lo, hi = window
    eps = [e for e in episodes if (e["onset_lo"] or e["onset_hi"]) <= hi and (e["end_hi"] or e["end_lo"]) >= lo]
    rows, used = [], set()
    for r in refs:
        hits = [i for i, e in enumerate(eps)
                if (e["onset_lo"] or e["onset_hi"]) - 0.5 <= r["peak"] <= (e["end_hi"] or e["end_lo"]) + 0.5]
        used.update(hits)
        if len(hits) != 1:
            rows.append({"ref": r["id"], "status": "missed" if not hits else f"split_into_{len(hits)}"})
            continue
        e = eps[hits[0]]
        on_e, end_e = [e["onset_lo"], e["onset_hi"]], [e["end_lo"], e["end_hi"]]
        complete_end = not r.get("censored")
        rows.append({"ref": r["id"], "status": "matched",
                     "onset_overlap": overlaps(on_e, r["on"]),
                     "onset_mid_diff_d": None if mid(on_e) is None or mid(r["on"]) is None else round(mid(on_e) - mid(r["on"]), 3),
                     "end_overlap": overlaps(end_e, r["end"]) if complete_end else None,
                     "end_mid_diff_d": round(mid(end_e) - mid(r["end"]), 3)
                     if complete_end and mid(end_e) is not None and mid(r["end"]) is not None else None,
                     "onset_width_d": None if None in on_e else round(on_e[1] - on_e[0], 3),
                     "end_width_d": None if None in end_e else round(end_e[1] - end_e[0], 3)})
    matched = [r for r in rows if r["status"] == "matched"]
    diffs_on = [abs(r["onset_mid_diff_d"]) for r in matched if r["onset_mid_diff_d"] is not None]
    diffs_end = [abs(r["end_mid_diff_d"]) for r in matched if r["end_mid_diff_d"] is not None]
    return {"reference_events": len(refs), "episodes_in_window": len(eps), "matched": len(matched),
            "missed_or_split": [r for r in rows if r["status"] != "matched"],
            "extra_episodes": len(eps) - len(used),
            "onset_overlap": sum(bool(r["onset_overlap"]) for r in matched),
            "end_overlap": sum(bool(r["end_overlap"]) for r in matched if r["end_overlap"] is not None),
            "end_comparable": sum(r["end_overlap"] is not None for r in matched),
            "median_abs_onset_mid_diff_d": round(st.median(diffs_on), 3) if diffs_on else None,
            "max_abs_onset_mid_diff_d": max(diffs_on) if diffs_on else None,
            "median_abs_end_mid_diff_d": round(st.median(diffs_end), 3) if diffs_end else None,
            "max_abs_end_mid_diff_d": max(diffs_end) if diffs_end else None,
            "median_onset_width_d": st.median(r["onset_width_d"] for r in matched if r["onset_width_d"] is not None),
            "median_end_width_d": st.median(r["end_width_d"] for r in matched if r["end_width_d"] is not None),
            "events": rows}


def decade_profile(rows):
    episodes = x1_vote_episodes(rows)
    times = [v["t"] for v in visits(rows)]
    out = {}
    for k, e in enumerate(episodes):
        decade = 1890 + 10 * math.floor((e["peak_t"] - 2411368.5) / 3652.5)
        d = out.setdefault(decade, {"episodes": 0, "confirmed": 0, "gap_split": 0, "bounded": 0,
                                    "pairs_c1_4d": 0, "pairs_c1_7d": 0, "onset_w": [], "end_w": []})
        d["episodes"] += 1
        d["confirmed"] += e["confirmed_event"]
        d["gap_split"] += e["gap_split"]
        bounded = e["onset_lo"] is not None and e["end_hi"] is not None
        if bounded and e["confirmed_event"] and not e["gap_split"]:
            d["bounded"] += 1
            d["onset_w"].append(e["onset_hi"] - e["onset_lo"])
            d["end_w"].append(e["end_hi"] - e["end_lo"])
        nxt = episodes[k + 1] if k + 1 < len(episodes) else None
        if (nxt and bounded and e["confirmed_event"] and nxt["confirmed_event"] and nxt["onset_lo"] is not None
                and not e["gap_split"] and not nxt["gap_split"]):
            longest = longest_quiet_gap(times, e["end_hi"], nxt["onset_lo"])
            d["pairs_c1_4d"] += longest <= 4.0
            d["pairs_c1_7d"] += longest <= 7.0
    table = []
    for decade in sorted(out):
        d = out[decade]
        table.append({"decade": decade, "x1_episodes": d["episodes"], "confirmed": d["confirmed"],
                      "gap_split": d["gap_split"], "confirmed_bounded_unsplit": d["bounded"],
                      "median_onset_interval_d": round(st.median(d["onset_w"]), 2) if d["onset_w"] else "",
                      "median_end_interval_d": round(st.median(d["end_w"]), 2) if d["end_w"] else "",
                      "consecutive_pairs_max_gap_le_4d": d["pairs_c1_4d"],
                      "consecutive_pairs_max_gap_le_7d": d["pairs_c1_7d"]})
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, help="write the open-era decade table here")
    args = parser.parse_args()
    rows, _ = read_acquisition(ROOT / "data/raw/aavso_ss_cyg_1956_1959_20261107/native.xml")
    ref, blind = references()
    whole = (2435473.5, 2436569.5)
    year = (2435839.5, 2436204.5)
    result = {}
    for name, extractor in (("X1_vote", x1_vote_episodes), ("X2_median_hysteresis", x2_median_hysteresis)):
        episodes = extractor(rows)
        result[name] = {"vs_claude_adjudicated_1956_1958": score(episodes, ref, whole),
                        "vs_blind_1957": score(episodes, blind, year)}
    summary = {name: {ref_name: {k: v for k, v in s.items() if k != "events"} for ref_name, s in r.items()}
               for name, r in result.items()}
    print(json.dumps(summary, indent=2, default=str))
    paths = sorted((ROOT / "data/raw").glob("aavso_ss_cyg_*/native.xml"))
    combined, _ = combine_acquisitions(paths)
    table = decade_profile(combined)
    for row in table:
        print(row)
    if args.table:
        with open(args.table, "w", newline="") as h:
            writer = csv.DictWriter(h, fieldnames=list(table[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(table)


if __name__ == "__main__":
    main()
