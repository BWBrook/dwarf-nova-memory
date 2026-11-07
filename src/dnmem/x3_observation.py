"""Outburst-brightness calibration and availability-preserving cadence stress."""

from bisect import bisect_left, bisect_right
from collections import defaultdict
import math
from statistics import median

from .injection_observe import prepare_schedule


def calibrate_brightness(rows, base_model):
    selected = [r for r in rows if r["band"] == "Vis." and r["val"] == "V"]
    schedule = prepare_schedule(rows)
    bins = defaultdict(lambda: defaultdict(list))
    for raw, slot in zip(selected, schedule):
        if raw["fainterThan"] == "0":
            bins[math.floor(float(raw["JD"]))][slot["observer_id"]].append(float(raw["mag"]))
    residuals = defaultdict(list)
    accepted = 0
    for own in bins.values():
        values = {who: median(mags) for who, mags in own.items()}
        if len(values) < 2 or not 8.5 <= median(values.values()) <= 10.5:
            continue
        accepted += 1
        for who, value in values.items():
            residuals[who].append(value - median(v for peer, v in values.items() if peer != who))
    model = {who: dict(params) for who, params in base_model.items()}
    for who, errors in residuals.items():
        centre = median(errors)
        sigma = max(.1, 1.4826 * median(abs(e - centre) for e in errors))
        weight = len(errors) / (len(errors) + 10)
        model[who]["offset"] = weight * centre
        model[who]["sigma"] = math.sqrt(weight * sigma**2 + (1-weight) * base_model[who]["sigma"]**2)
        model[who]["outburst_residual_n"] = len(errors)
    return model, {"outburst_bins": accepted, "observers_with_outburst_residuals": len(residuals),
                   "median_observer_sigma": median(p["sigma"] for p in model.values()),
                   "scope": "leave-observer-out residuals at observer-bin median brightness 8.5–10.5; no real duration-gap statistic"}


def labelled_days(rows):
    selected = [r for r in rows if r["band"] == "Vis." and r["val"] == "V"]
    schedule = prepare_schedule(rows)
    days = defaultdict(list)
    votes = defaultdict(lambda: defaultdict(list))
    for raw, slot in zip(selected, schedule):
        day = math.floor(float(slot["JD"]))
        days[day].append(slot)
        if raw["fainterThan"] == "0":
            votes[day][slot["observer_id"]].append((float(raw["mag"]), False))
        elif float(raw["mag"]) >= 10:
            votes[day][slot["observer_id"]].append((math.inf, True))
    result = []
    for day, slots in sorted(days.items()):
        values = [median([value for value, limit in v if not limit])
                  if any(not limit for _, limit in v) else math.inf for v in votes[day].values()]
        bright = sum(v <= 10 for v in values)
        label = "unknown" if not values else "B" if 2*bright > len(values) else "F" if 2*bright < len(values) else "mixed"
        result.append({"day": day, "state": label, "slots": slots})
    return result


def state_compatible_schedule(days, history, start, stop):
    table = {int(d["day"]): d for d in days}
    by_state = {state: sorted(day for day, d in table.items() if d["state"] == state) for state in ("B", "F")}
    result = []
    changed = unmatched = 0
    dropped = 0
    for day, original in sorted(table.items()):
        representative = median(float(r["JD"]) for r in original["slots"])
        wanted = "B" if history.evaluate([representative])[0] <= 10 else "F"
        donors = by_state[wanted]
        available = donors[bisect_left(donors, day-15):bisect_right(donors, day+15)]
        if available:
            donor = min(available, key=lambda other: (abs(other-day), other))
        else:
            donor = day
            unmatched += 1
        changed += donor != day
        for slot in table[donor]["slots"]:
            t = day + float(slot["JD"]) - donor
            if start <= t < stop:
                result.append({**slot, "JD": t, "t": t})
            else:
                dropped += 1
    result.sort(key=lambda r: (float(r["JD"]), r["observer_id"]))
    calendar_days = math.ceil(stop) - math.floor(start)
    summary = {"observed_target_days": len(table), "borrowed_days": changed,
               "no_match_days": unmatched, "no_match_fraction": unmatched/len(table) if table else 1.0,
               "empty_days_preserved": calendar_days - len(table), "boundary_rows_omitted": dropped,
               "scope": "availability-preserving state-compatible cadence stress; unknown/empty days are not quiescent labels"}
    return result, summary
