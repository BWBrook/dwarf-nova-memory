#!/usr/bin/env python3
"""Build an A04 annotation from adjudication decisions and the native export.

Decisions name which mechanical candidates form each event and which rows the
annotator overruled; brackets, envelopes, confirmations and gaps are computed.
"""

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem.aavso import read_native_payload
from dnmem.brackets import DEFINITION_VERSION, MISS_GAP_DAYS, candidate_runs, observer, row_class

FIELDS = ["target_id", "event_id", "definition_version", "annotator", "candidates", "overruled_obsids",
          "onset_earliest_jd", "onset_earliest_obsid", "onset_latest_jd", "onset_latest_obsid",
          "onset_envelope_end_jd", "left_censored", "onset_detected_jd",
          "end_earliest_jd", "end_earliest_obsid", "end_latest_jd", "end_latest_obsid",
          "end_envelope_start_jd", "right_censored", "end_confirmed_jd",
          "duration_min_d", "duration_max_d", "duration_min_envelope_d",
          "gap_next_min_d", "gap_next_max_d", "gap_next_max_envelope_d",
          "longest_quiet_gap_d", "consecutive_with_next", "missed_event_possible",
          "peak_mag", "peak_jd", "n_bright", "n_bright_observers", "n_interleaved_faint",
          "type_cm92_v1", "type_cm92_envelope", "event_class", "t_flag_effect", "code_flags", "notes"]
UNDOCUMENTED_CODES = {"N", "Q", "X"}


def jd(row):
    return float(row["JD"])


def candidate_numbers(text):
    numbers = []
    for part in text.split():
        a, _, b = part.partition("-")
        numbers.extend(range(int(a), int(b or a) + 1))
    return numbers


def kind(d_min, d_max):
    if d_min >= 12.0:
        return "long"
    if d_max is not None and d_max < 12.0:
        return "short"
    return "ambiguous"


def second_observer(rows):
    first = observer(rows[0])
    return next((row for row in rows[1:] if observer(row) != first), None)


def build(rows, decisions, annotator):
    runs = candidate_runs(rows)
    overruled = {obs for d in decisions for obs in d["overruled_obsids"].split()}
    grouped = {k for d in decisions for k in candidate_numbers(d["candidates"])}
    for k, run in enumerate(runs, start=1):
        if k not in grouped and not {run["onset_latest"]["obsID"], run["end_earliest"]["obsID"]} <= overruled:
            raise ValueError(f"candidate {k} is neither assigned to an event nor overruled")
    usable = sorted((r for r in rows if r["val"] == "V" and r["obsID"] not in overruled),
                    key=lambda r: (jd(r), r["obsID"]))
    info = [r for r in usable if row_class(r) != "N"]
    index = {r["obsID"]: i for i, r in enumerate(info)}
    flagged = [r for r in rows if r["val"] == "T"]
    events = []
    for d in decisions:
        group = [runs[k - 1] for k in candidate_numbers(d["candidates"])]
        bright = [r for run in group for r in (run["onset_latest"], run["end_earliest"])
                  if r["obsID"] not in overruled]
        i0 = min(index[r["obsID"]] for r in bright)
        i1 = max(index[r["obsID"]] for r in bright)
        span = info[i0:i1 + 1]
        b_rows = [r for r in span if row_class(r) == "B"]
        peak = min(b_rows, key=lambda r: (float(r["mag"]), jd(r)))
        p = span.index(peak)
        rise_f = [r for r in span[:p] if row_class(r) == "F"]
        fall_f = [r for r in span[p:] if row_class(r) == "F"]
        before = info[i0 - 1] if i0 > 0 else None
        after = info[i1 + 1] if i1 + 1 < len(info) else None
        confirm, seen = None, set()
        for r in info[i1 + 1:]:
            if row_class(r) == "B":
                break
            seen.add(observer(r))
            if len(seen) == 2:
                confirm = r
                break
        detected = second_observer(b_rows)
        events.append({"d": d, "span": span, "before": before, "first": info[i0], "last": info[i1],
                       "after": after, "peak": peak, "b_rows": b_rows,
                       "env_on": max([jd(info[i0])] + [jd(r) for r in rise_f]),
                       "env_end": min([jd(info[i1])] + [jd(r) for r in fall_f]),
                       "n_interleaved": len(rise_f) + len(fall_f), "detected": detected, "confirm": confirm,
                       "i0": i0, "i1": i1})
    confirmed_spans = [jd(e["after"]) - jd(e["before"]) for e in events
                       if e["before"] and e["after"] and e["d"]["event_class"] != "unconfirmed"]
    shortest_span = min(confirmed_spans)
    out = []
    for k, e in enumerate(events):
        nxt = events[k + 1] if k + 1 < len(events) else None
        on_lo, on_hi = e["before"], e["first"]
        end_lo, end_hi = e["last"], e["after"]
        d_min = jd(end_lo) - jd(on_hi)
        d_max = jd(end_hi) - jd(on_lo) if on_lo and end_hi else None
        d_min_env = e["env_end"] - e["env_on"]
        gap = {}
        if nxt is not None and end_hi and nxt["before"]:
            gap = {"gap_next_min_d": jd(nxt["before"]) - jd(end_hi),
                   "gap_next_max_d": jd(nxt["first"]) - jd(end_lo),
                   "gap_next_max_envelope_d": nxt["env_on"] - e["env_end"]}
            quiet = [jd(r) for r in info[e["i1"] + 1:nxt["i0"]]]
            longest = max(b - a for a, b in zip(quiet, quiet[1:])) if len(quiet) > 1 else 0.0
            gap.update({"longest_quiet_gap_d": longest,
                        "consecutive_with_next": "verified" if longest <= MISS_GAP_DAYS else "unverified",
                        "missed_event_possible": "possible" if longest >= shortest_span else "no"})
        effects = []
        for label, lo, hi, lo_name, hi_name in (("onset", on_lo, on_hi, "onset_earliest", "onset_latest"),
                                                ("end", end_lo, end_hi, "end_earliest", "end_latest")):
            if lo is None or hi is None:
                continue
            for r in flagged:
                if jd(lo) < jd(r) < jd(hi) and row_class(r) != "N":
                    moved = (hi_name if row_class(r) == "B" else lo_name) if label == "onset" else \
                            (lo_name if row_class(r) == "B" else hi_name)
                    effects.append(f"{label}: T {row_class(r)} {r['obsID']} would move {moved} to {r['JD']}")
        if nxt is not None and end_hi and nxt["before"]:
            spurious = [r for r in flagged if jd(end_hi) < jd(r) < jd(nxt["before"]) and row_class(r) == "B"]
            if spurious:
                effects.append(f"{len(spurious)} T B rows in following quiescence would form spurious runs")
        codes = sorted({f"{name}:{r['comCode']}" for name, r in (("onset_earliest", on_lo), ("onset_latest", on_hi),
                                                                ("end_earliest", end_lo), ("end_latest", end_hi))
                        if r is not None and set(r["comCode"]) & UNDOCUMENTED_CODES})
        r3 = lambda x: "" if x is None else f"{x:.3f}"
        out.append({
            "target_id": "ss_cyg", "event_id": e["d"]["event_id"], "definition_version": DEFINITION_VERSION,
            "annotator": annotator, "candidates": e["d"]["candidates"], "overruled_obsids": e["d"]["overruled_obsids"],
            "onset_earliest_jd": on_lo["JD"] if on_lo else "", "onset_earliest_obsid": on_lo["obsID"] if on_lo else "",
            "onset_latest_jd": on_hi["JD"], "onset_latest_obsid": on_hi["obsID"],
            "onset_envelope_end_jd": r3(e["env_on"]), "left_censored": on_lo is None,
            "onset_detected_jd": e["detected"]["JD"] if e["detected"] else "",
            "end_earliest_jd": end_lo["JD"], "end_earliest_obsid": end_lo["obsID"],
            "end_latest_jd": end_hi["JD"] if end_hi else "", "end_latest_obsid": end_hi["obsID"] if end_hi else "",
            "end_envelope_start_jd": r3(e["env_end"]), "right_censored": end_hi is None,
            "end_confirmed_jd": e["confirm"]["JD"] if e["confirm"] else "",
            "duration_min_d": r3(d_min), "duration_max_d": r3(d_max), "duration_min_envelope_d": r3(d_min_env),
            "gap_next_min_d": r3(gap.get("gap_next_min_d")), "gap_next_max_d": r3(gap.get("gap_next_max_d")),
            "gap_next_max_envelope_d": r3(gap.get("gap_next_max_envelope_d")),
            "longest_quiet_gap_d": r3(gap.get("longest_quiet_gap_d")),
            "consecutive_with_next": gap.get("consecutive_with_next", ""),
            "missed_event_possible": gap.get("missed_event_possible", ""),
            "peak_mag": e["peak"]["mag"], "peak_jd": e["peak"]["JD"], "n_bright": len(e["b_rows"]),
            "n_bright_observers": len({observer(r) for r in e["b_rows"]}), "n_interleaved_faint": e["n_interleaved"],
            "type_cm92_v1": kind(d_min, d_max), "type_cm92_envelope": kind(d_min_env, d_max),
            "event_class": e["d"]["event_class"], "t_flag_effect": "; ".join(effects),
            "code_flags": " ".join(codes), "notes": e["d"]["notes"]})
    return out, shortest_span


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_xml", type=Path)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("--annotator", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, _ = read_native_payload(args.native_xml)
    with open(args.decisions, newline="") as handle:
        decisions = list(csv.DictReader(handle))
    out, shortest = build(rows, decisions, args.annotator)
    with open(args.output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)
    print(f"{len(out)} events; shortest confirmed faint-to-faint span {shortest:.2f} d")


if __name__ == "__main__":
    main()
