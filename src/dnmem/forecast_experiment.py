"""Synthetic, chronological A10 development experiments; no archive access."""

from __future__ import annotations

from collections import Counter
import math
import random
from statistics import fmean, stdev

from .adaptive_effort import thin_adaptive
from .extract_x4 import x4_episodes
from .joint_benchmark import generate_observations
from .prefix_features import forecast_ledger, outcome_evidence
from .x4_benchmark import seed_for

ERAS = ("1910_1929", "1930_1949", "1950_1959")
CASES = ("null", "structured", "gross", "offset", "adaptive", "alternative")


def variant_spec(case, replicate):
    variants = [("prefix_point", "prefix", "point", "log_duration", 0),
                ("prefix_uniform_end", "prefix", "uniform_end", "log_duration", 0),
                ("retrospective_point", "retrospective", "point", "log_duration", 0),
                ("oracle_point", "oracle", "point", "log_duration", 0)]
    if case in ("null", "alternative") and replicate < 4:
        variants.extend([("prefix_type_within", "prefix", "point", "type_within", 0),
                         ("prefix_point_L2", "prefix", "point", "log_duration", 2),
                         ("prefix_uniform_end_L2", "prefix", "uniform_end", "log_duration", 2)])
    return variants


def source_strata(inputs):
    strata = {s["stratum"]: s for s in inputs["strata"] if s["stratum"] in ERAS}
    if set(strata) != set(ERAS):
        raise ValueError("missing open-era source strata")
    if any(s["start"] < 2418672.5 or s["stop"] > 2436934.0 for s in strata.values()):
        raise ValueError("source pattern outside the permitted open era")
    return strata


def crop_stratum(stratum, start, stop):
    if not stratum["start"] <= start < stop <= stratum["stop"]:
        raise ValueError("crop outside original source pattern")
    days = []
    for day in stratum["days"]:
        slots = [r for r in day["slots"] if start <= float(r["t"]) < stop]
        if slots:
            days.append({**day, "slots": slots})
    schedule = [r for r in stratum["schedule"] if start <= float(r["t"]) < stop]
    return {**stratum, "start": start, "stop": stop, "days": days, "schedule": schedule}


def observed_block(inputs, configuration, stratum, seed, case, offset_seed=None):
    process = case if case in ("structured", "alternative") else "null"
    actual_inputs = inputs
    if case == "offset":
        actual_inputs = {**inputs, "brightness_model": {
            who: {**p, "offset": p["offset"] + random.Random(
                seed_for(offset_seed, "persistent-observer", who)).gauss(0, .2)}
            for who, p in inputs["brightness_model"].items()}}
    rows, history, generator, cadence, contamination = generate_observations(
        actual_inputs, configuration, stratum, seed, process=process, gross=case == "gross")
    truth = [dict(e) for e in generator.truth_catalogue(history, 10.)
             if stratum["start"] <= e["onset"] and e["end"] < stratum["stop"]]
    metadata = {"cadence": {k: v for k, v in cadence.items() if k != "events"},
                "contamination": contamination, "case": case}
    return rows, truth, metadata


def concordance_stream(inputs, configurations, index, base):
    family = "v2-phase" if index < 80 else "v4-phase"
    case = CASES[index % len(CASES)]
    era = ERAS[(index // len(CASES)) % 3]
    source = source_strata(inputs)[era]
    width = 3 * 365.25
    windows = max(1, int((source["stop"] - source["start"]) // width))
    window = (index // 18) % windows
    start = source["start"] + window * width
    stop = min(start + width, source["stop"])
    crop = crop_stratum(source, start, stop)
    seed = seed_for(base, "concordance", index, family, case, era)
    rows, _, metadata = observed_block(inputs, configurations[family], crop, seed, case, seed)
    if case == "adaptive":
        rows, metadata["adaptive"] = thin_adaptive(rows, seed_for(seed, "adaptive"))
    return rows, {"index": index, "family": family, "case": case, "era": era,
                  "start": start, "stop": stop, "seed": seed, **metadata}


def chronological_stream(inputs, configuration, case, replicate, base):
    """Replay open-era sampling patterns on an explicitly artificial timeline.

    Three source strata give about 50 development years, followed by 58
    evaluation years. Integer shifts preserve the native-JD night bins.
    Thirty-day seams force coverage censoring between independent blocks.
    """
    strata = source_strata(inputs)
    blocks = [strata[e] for e in ERAS] * 2
    first = strata[ERAS[0]]
    blocks += [crop_stratum(first, first["start"], first["start"] + 8 * 365.25)]
    rows, truth, metadata = [], [], []
    cursor, train_cutoff = 1000.5, None
    process_label = case if case in ("structured", "alternative") else "null"
    offset_seed = seed_for(base, configuration["pair_id"], replicate, "observer-offsets")
    for index, source in enumerate(blocks):
        seed = seed_for(base, configuration["pair_id"], process_label, replicate, "block", index)
        observed, events, info = observed_block(inputs, configuration, source, seed, case, offset_seed)
        shift = cursor - source["start"]
        if abs(shift - round(shift)) > 1e-7:
            raise ValueError("translation must preserve native-JD night bins")
        shift = int(round(shift))
        for r in observed:
            rows.append({**r, "JD": str(float(r["JD"]) + shift),
                         "obsID": f"synthetic-block-{index}-{r.get('obsID', '')}"})
        for e in events:
            truth.append({**e, "id": f"block-{index}-{e['id']}", "block": index,
                          **{k: e[k] + shift for k in ("onset", "end", "peak_t")}})
        end = source["stop"] + shift
        metadata.append({"block": index, "source_era": source["stratum"], "seed": seed,
                         "source_start": source["start"], "source_stop": source["stop"],
                         "synthetic_start": cursor, "synthetic_stop": end, **info})
        if index == 2:
            train_cutoff = end
        cursor = math.ceil(end + 30 - .5) + .5
    adaptive = None
    if case == "adaptive":
        rows, adaptive = thin_adaptive(rows, seed_for(base, replicate, configuration["pair_id"], "adaptive"))
    rows.sort(key=lambda r: float(r["JD"]))
    truth.sort(key=lambda e: e["onset"])
    return rows, truth, {"training_cutoff": train_cutoff, "stop": metadata[-1]["synthetic_stop"],
                         "blocks": metadata, "adaptive": adaptive,
                         "time_basis": "artificial relative days; integer translations of pre1960 patterns"}


def predictor_views(rows, ledger, truth):
    """Diagnostic oracle/retrospective views; production features remain prefix."""
    episodes = x4_episodes(rows, 10.)
    retrospective, oracle = [], []
    counts = Counter()
    for f in ledger:
        r = dict(f)
        since = f["bright_first_at"] - 1.15
        current = next((i for i in range(len(episodes)-1, -1, -1)
                        if (episodes[i]["onset_lo"] if episodes[i]["onset_lo"] is not None
                            else episodes[i]["peak_t"]) <= f["bright_first_at"]+1.15 and
                        (episodes[i]["end_hi"] if episodes[i]["end_hi"] is not None
                         else episodes[i]["peak_t"]) >= since), None)
        if current is not None:
            e = episodes[current]
            for k in ("onset_t", "onset_lo", "onset_hi", "end_t", "end_lo", "end_hi"):
                r[k] = e[k]
            if r["onset_t"] is not None and r["end_t"] is not None:
                r["duration"] = r["end_t"] - r["onset_t"]
                r["age_at_issue"] = r["issue_time"] - r["end_t"]
            else:
                r.update(duration=None, age_at_issue=None)
            r["landmark_available"] = r["end_t"] is not None and r["end_t"] <= r["issue_time"]
            counts["retrospective_matched"] += 1
        else:
            r.update(landmark_available=False, duration=None, onset_t=None, end_t=None,
                     end_lo=None, end_hi=None)
            counts["retrospective_unmatched"] += 1
        retrospective.append(r)
        o = dict(f)
        matches = [i for i, e in enumerate(truth)
                   if e["onset"] <= f["bright_first_at"] <= e["end"] and e["end"] <= f["issue_time"]]
        if len(matches) != 1:
            o.update(landmark_available=False, duration=None, onset_t=None, end_t=None,
                     end_lo=None, end_hi=None, previous_gap=None, previous_gap_covered=False)
            counts["oracle_unknown_or_uncompleted"] += 1
        else:
            i = matches[0]
            e = truth[i]
            previous = truth[i-1] if i else None
            gap = e["onset"] - previous["end"] if previous and previous["block"] == e["block"] else None
            o.update(landmark_available=True, onset_t=e["onset"], onset_lo=e["onset"], onset_hi=e["onset"],
                     end_t=e["end"], end_lo=e["end"], end_hi=e["end"], duration=e["end"]-e["onset"],
                     age_at_issue=f["issue_time"]-e["end"], previous_gap=gap,
                     previous_gap_covered=gap is not None and gap > 0)
            counts["oracle_completed_unique"] += 1
        oracle.append(o)
    return {"prefix": ledger, "retrospective": retrospective, "oracle": oracle}, dict(counts)


def block_interval(rows, field, width=3*365.25):
    from scipy.stats import t
    if not rows:
        return {"n": 0, "estimate": None, "lower": None, "upper": None}
    origin = min(r["issue_time"] for r in rows)
    blocks = {}
    for r in rows:
        block = math.floor((r["issue_time"]-origin)/width)
        blocks.setdefault(block, []).append(r[field])
    mean = fmean(r[field] for r in rows)
    totals = [(sum(v), len(v)) for v in blocks.values()]
    b = len(totals)
    se = (stdev(s-mean*n for s, n in totals) / math.sqrt(b) / fmean(n for _, n in totals)
          if b > 1 else None)
    radius = float(t.ppf(.975, b-1))*se if se is not None else None
    return {"n": len(rows), "blocks": b, "estimate": mean, "se": se,
            "lower": mean-radius if radius is not None else None,
            "upper": mean+radius if radius is not None else None,
            "scope": "three-year cluster interval diagnostic; not a calibrated confirmatory test"}


def score_trial(inputs, configuration, case, replicate, base):
    from .ledger_forecast import fit_models
    rows, truth, metadata = chronological_stream(inputs, configuration, case, replicate, base)
    cutoff, stop = metadata["training_cutoff"], metadata["stop"]
    ledger = forecast_ledger(rows, stop=stop)
    training = [f for f in ledger if f["issue_time"] < cutoff]
    train_evidence = outcome_evidence(rows, training, stop=cutoff)
    evidence = outcome_evidence(rows, ledger, stop=stop)
    by_index = {e["emission_index"]: e for e in evidence}
    train_views, _ = predictor_views([r for r in rows if float(r["JD"]) <= cutoff], training,
                                    [e for e in truth if e["end"] <= cutoff])
    eval_ledger = [f for f in ledger if f["issue_time"] >= cutoff]
    eval_views, mapping_counts = predictor_views(rows, eval_ledger, truth)
    variants = variant_spec(case, replicate)
    if case in ("null", "alternative") and replicate < 4:
        late = [{**f, "issue_time": f["issue_time"]+2, "latency": 2.,
                 "age_at_issue": f["age_at_issue"]+2 if f["age_at_issue"] is not None else None}
                for f in ledger if f["issue_time"]+2 < stop]
        late_train = [f for f in late if f["issue_time"] < cutoff]
        late_train_evidence = outcome_evidence(rows, late_train, stop=cutoff)
        late_eval = [f for f in late if f["issue_time"] >= cutoff]
        late_by_index = {e["emission_index"]: e for e in outcome_evidence(rows, late, stop=stop)}
    results, models, routes, score_rows = {}, {}, {}, []
    for name, view, endpoint_mode, mark_mode, latency in variants:
        fit_ledger = late_train if latency else train_views[view]
        fit_evidence = late_train_evidence if latency else train_evidence
        testing = late_eval if latency else eval_views[view]
        targets = late_by_index if latency else by_index
        bundle = fit_models(fit_ledger, fit_evidence, cutoff,
                            endpoint_mode=endpoint_mode, mark_mode=mark_mode)
        part = []
        route_counts = {m: Counter() for m in ("M0", "M1", "M2", "M3")}
        for f in testing:
            e = targets[f["emission_index"]]
            scores = {m: bundle.score(f, e, m) for m in ("M0", "M1", "M2", "M3")}
            if any(s is None for s in scores.values()):
                if not all(s is None for s in scores.values()):
                    raise ValueError("models scored different issuance sets")
                continue
            if not all(math.isfinite(s) for s in scores.values()):
                raise ValueError("nonfinite predictive score")
            routing = {m: bundle.route(f, m) for m in scores}
            for m, actual in routing.items():
                route_counts[m][actual] += 1
            record = {"variant": name, "emission_index": f["emission_index"],
                      "issue_time": f["issue_time"], "kind": e["kind"], "reason": e["reason"],
                      **scores, **{f"route_{m}": actual for m, actual in routing.items()},
                      "gain_M1_M0": scores["M1"]-scores["M0"],
                      "gain_M2_M0": scores["M2"]-scores["M0"],
                      "gain_M3_M2": scores["M3"]-scores["M2"]}
            part.append(record)
        if not part:
            raise ValueError("no scored evaluation issuances")
        results[name] = {k: block_interval(part, k) for k in ("gain_M1_M0", "gain_M2_M0", "gain_M3_M2")}
        models[name] = bundle.to_dict()
        routes[name] = {m: dict(count) for m, count in route_counts.items()}
        score_rows.extend(part)
    counts = {"training_issued": len(training), "evaluation_issued": len(eval_ledger),
              "training_evidence": dict(Counter(e["kind"]+":"+e["reason"] for e in train_evidence)),
              "evaluation_evidence": dict(Counter(by_index[f["emission_index"]]["kind"]+":"+
                                            by_index[f["emission_index"]]["reason"] for f in eval_ledger))}
    ledger_trace = {view: {"training": train_views[view], "evaluation": eval_views[view]}
                    for view in train_views}
    evidence_trace = {"0": {"training": train_evidence,
                             "evaluation": [by_index[f["emission_index"]] for f in eval_ledger]}}
    if case in ("null", "alternative") and replicate < 4:
        ledger_trace["prefix_L2"] = {"training": late_train, "evaluation": late_eval}
        evidence_trace["2"] = {"training": late_train_evidence,
                               "evaluation": [late_by_index[f["emission_index"]] for f in late_eval]}
    return {"case": case, "family": configuration["pair_id"], "replicate": replicate,
            "counts": counts, "diagnostic_mapping_counts": mapping_counts, "results": results,
            "models": models, "evaluation_routes": routes,
            "stream_metadata": metadata, "ledger_trace": ledger_trace,
            "evidence_trace": evidence_trace}, score_rows
