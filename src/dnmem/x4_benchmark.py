"""Candidate-blind observation generation for the A04g experiment."""

import hashlib
import math
import random
from bisect import bisect_right
from collections import defaultdict

from dnmem.injection_observe import simulate_rows
from dnmem.injection_truth import LatentCoefficients


def seed_for(base, *labels):
    return int.from_bytes(hashlib.sha256("|".join(map(str, (base,) + labels)).encode()).digest()[:8], "big")


def history_for(inputs, parameters, task, base):
    family = task["family"]
    if family == "v3":
        from dnmem import injection_truth_v3 as generator
    elif family == "v2":
        from dnmem import injection_truth_v2 as generator
    elif family == "v1":
        from dnmem import injection_truth as generator
    else:
        raise ValueError("unknown waveform family")
    s = next(s for s in inputs["strata"] if s["stratum"] == task["stratum"])
    seed = seed_for(base, task["case"], family, task["stratum"], task["phase"], task["replicate"])
    process = "alternative" if task["case"] in ("structured", "alternative") else "null"
    kwargs = {"process": process}
    if task["case"] == "structured":
        kwargs["coefficients"] = LatentCoefficients(partial_duration_gap=0.0)
    if family != "v1":
        kwargs["shape_config"] = generator.ShapeConfig(**parameters[family]["shape_config"])
    history = generator.generate_events(inputs["durations"], inputs["gaps"], s["start"],
                                        s["stop"], seed_for(seed, "truth"), **kwargs)
    return s, seed, history, generator


def gross_errors(rows, truth, seed, fraction=0.0032):
    """Replace a fixed expected fraction of quiet observer-night visits in short clusters."""
    rng = random.Random(seed)
    intervals = sorted((float(e["onset"]) - 3, float(e["end"]) + 3) for e in truth)
    merged = []
    for lo, hi in intervals:
        if merged and lo <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(hi, merged[-1][1])
        else:
            merged.append((lo, hi))
    starts = [lo for lo, _ in merged]
    eligible = defaultdict(list)
    for i, row in enumerate(rows):
        t = float(row["JD"])
        previous = bisect_right(starts, t) - 1
        if previous >= 0 and t <= merged[previous][1]:
            continue
        who = (row.get("obsName") or "").strip().casefold() or row["by"]
        eligible[(who, math.floor(t))].append(i)
    keys = sorted(eligible)
    target = len(keys) * fraction
    budget = math.floor(target) + (rng.random() < target % 1)
    selected = set()
    clusters = []
    shuffled = list(keys)
    rng.shuffle(shuffled)
    for who, day in shuffled:
        if len(selected) >= budget:
            break
        if (who, day) in selected:
            continue
        length = rng.randint(1, 3)
        cluster = []
        for shift in range(length):
            key = who, day + shift
            if key not in eligible or key in selected or len(selected) >= budget:
                break
            selected.add(key)
            cluster.append(key)
        clusters.append(cluster)
    output = [dict(row) for row in rows]
    for cluster in clusters:
        magnitude = rng.uniform(8.5, 9.8)
        for key in cluster:
            for i in eligible[key]:
                output[i]["mag"] = str(round(magnitude, 2))
                output[i]["fainterThan"] = "0"
    return output, {"eligible_quiet_visits": len(keys), "contaminated_visits": len(selected),
                    "contaminated_rows": sum(len(eligible[k]) for k in selected),
                    "contamination_fraction": len(selected) / len(keys) if keys else None,
                    "clusters": len(clusters), "cluster_lengths": [len(c) for c in clusters]}


def observed_history(inputs, parameters, task, base):
    s, seed, history, generator = history_for(inputs, parameters, task, base)
    phase = task["phase"]
    if phase == "diverse":
        from dnmem.x4_cadence import diverse_state_schedule
        schedule, cadence = diverse_state_schedule(s["days"], history, s["start"], s["stop"],
                                                   seed_for(seed, "cadence"))
    elif phase == "legacy":
        from dnmem.x3_observation import state_compatible_schedule
        schedule, cadence = state_compatible_schedule(s["days"], history, s["start"], s["stop"])
    elif phase == "random":
        schedule = s["schedule"]
        cadence = {"no_match_fraction": 0.0, "borrowed_days": 0, "no_match_days": 0,
                   "observed_target_days": len(s["days"]),
                   "empty_days_preserved": math.ceil(s["stop"]) - math.floor(s["start"]) - len(s["days"]),
                   "boundary_rows_omitted": 0}
    else:
        raise ValueError("unknown cadence phase")
    family = task["family"]
    model = inputs["model"] if family == "v1" else inputs["brightness_model"]
    multiplier = 1.0 if family == "v1" else parameters[family]["noise_multiplier"]
    model = {who: {**p, "sigma": p["sigma"] * multiplier} for who, p in model.items()}
    if task["case"] == "offset":
        model = {who: {**p, "offset": p["offset"] + random.Random(
                    seed_for(seed, "persistent-offset", who)).gauss(0, .2)} for who, p in model.items()}
    magnitudes = generator.magnitudes_at(history, [float(row["JD"]) for row in schedule])
    rows = simulate_rows(schedule, magnitudes, model, seed_for(seed, "measurement"))
    contamination = {}
    if task["case"] == "gross":
        rows, contamination = gross_errors(rows, generator.truth_catalogue(history, 10.0),
                                           seed_for(seed, "gross-errors"))
    return rows, history, generator, s, seed, cadence, contamination
