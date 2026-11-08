"""Chronological directional-model trials; synthetic inputs only."""

from collections import Counter
import math

from .directional_forecast import fit_directional
from .oc_statistics import cluster_interval, reference_calibration
from .oc_streams import development_stream, reference_stream
from .prefix_features import forecast_ledger, outcome_evidence

VARIANTS = (("primary", "point", True, "log_duration", 0., False),
            ("joint_placebo", "point", True, "log_duration", 0., True),
            ("uniform_end", "uniform_end", True, "log_duration", 0., False),
            ("q_only", "point", False, "log_duration", 0., False),
            ("delay_2", "point", True, "log_duration", 2., False),
            ("type_within", "point", True, "type_within", 0., False))
COMPARISONS = ("gain_M3_M2", "gain_P3_M2", "gain_M3_P3", "gain_M2_M0")


def shifted_ledger(ledger, delay, stop):
    return [{**row, "issue_time": row["issue_time"]+delay, "latency": delay,
             "age_at_issue": row["age_at_issue"]+delay if row["age_at_issue"] is not None else None}
            for row in ledger if row["issue_time"]+delay < stop]


def scored(bundle, ledger, evidence):
    result = bundle.scores(ledger, evidence)
    for row in result:
        if row["M2"] is None:
            if any(row[model] is not None for model in ("M0", "M3", "P3")):
                raise ValueError("different model scoring populations")
            continue
        if not all(math.isfinite(row[model]) for model in ("M0", "M2", "M3", "P3")):
            raise ValueError("nonfinite forecast score")
        row["gain_M2_M0"] = row["M2"]-row["M0"]
    return [row for row in result if row["M2"] is not None]


def joint_valid(feature):
    return (feature.get("landmark_available") is True
            and feature.get("previous_gap_covered") is True
            and feature.get("duration") is not None and feature["duration"] > 0
            and feature.get("previous_duration") is not None and feature["previous_duration"] > 0)


def run_trial(inputs, configuration, case, replicate, base, *, references=True, force_references=False):
    rows, _truth, meta = development_stream(inputs, configuration, case, replicate, base)
    cutoff, stop, origin = meta["training_cutoff"], meta["stop"], meta["training_cutoff"]
    ledger = forecast_ledger(rows, stop=stop)
    lagged = shifted_ledger(ledger, 2., stop)
    ledgers = {0.: ledger, 2.: lagged}
    training = {delay: [f for f in group if f["issue_time"] < cutoff] for delay, group in ledgers.items()}
    testing = {delay: [f for f in group if f["issue_time"] >= cutoff] for delay, group in ledgers.items()}
    train_evidence = {delay: outcome_evidence(rows, group, stop=cutoff) for delay, group in training.items()}
    full_evidence = {delay: {e["emission_index"]: e for e in outcome_evidence(rows, group, stop=stop)}
                     for delay, group in ledgers.items()}
    test_evidence = {delay: [full_evidence[delay][f["emission_index"]] for f in group]
                     for delay, group in testing.items()}
    models, intervals, routes, output_scores = {}, {}, {}, []
    primary_bundle = None
    for name, endpoint, local, mark, delay, joint in VARIANTS:
        bundle = fit_directional(training[delay], train_evidence[delay], cutoff,
                                 endpoint_mode=endpoint, local_level=local,
                                 mark_mode=mark, joint_marks=joint)
        if name == "primary":
            primary_bundle = bundle
        part = scored(bundle, testing[delay], test_evidence[delay])
        if joint:
            ids = {f["emission_index"] for f in testing[delay] if joint_valid(f)}
            part = [row for row in part if row["emission_index"] in ids]
        if not part:
            raise ValueError("empty scored variant")
        intervals[name] = {str(years): {field: cluster_interval(part, field, origin, years)
                                      for field in COMPARISONS} for years in (3, 6)}
        routes[name] = {model: dict(Counter(row[model+"_route"] for row in part))
                        for model in ("M0", "M2", "M3", "P3")}
        output_scores.extend({"variant": name, **row} for row in part)
        models[name] = bundle.to_dict()

    secondary = fit_directional(testing[0.], test_evidence[0.], stop, directional=False)
    record = {"family": configuration["pair_id"], "case": case, "replicate": replicate,
              "stream_metadata": meta, "models": models, "intervals": intervals, "routes": routes,
              "secondary_evaluation_fit": secondary.to_dict(),
              "counts": {"training_issued": len(training[0.]), "evaluation_issued": len(testing[0.]),
                         "training_evidence": dict(Counter(e["kind"]+":"+e["reason"] for e in train_evidence[0.])),
                         "evaluation_evidence": dict(Counter(e["kind"]+":"+e["reason"] for e in test_evidence[0.]))}}
    if replicate == 0:
        record["audit_trace"] = {"ledger": {str(delay): {"training": training[delay], "evaluation": testing[delay]}
                                           for delay in (0., 2.)},
                                 "evidence": {str(delay): {"training": train_evidence[delay], "evaluation": test_evidence[delay]}
                                              for delay in (0., 2.)}}
    if references and configuration["pair_id"] == "v2-phase" and case in ("null", "alternative"):
        identity = primary_bundle.models["M3"].coefficients["beta"] == 0.
        reference_means = []
        reference_records = []
        if not identity or force_references:
            context = [row for row in rows if cutoff-400 < float(row["JD"]) <= cutoff]
            for reference in range(6):
                future, _, future_meta = reference_stream(inputs, configuration, case, replicate, base,
                                                           reference, context, meta)
                features = forecast_ledger(future, start=origin, stop=future_meta["stop"])
                outcomes = outcome_evidence(future, features, stop=future_meta["stop"])
                scores = scored(primary_bundle, features, outcomes)
                estimate = sum(row["gain_M3_M2"] for row in scores)/len(scores)
                reference_means.append(estimate)
                reference_records.append({"reference_id": reference, "estimate": estimate,
                                          "n": len(scores), "metadata": future_meta})
        record["reference_calibration"] = {
            str(years): reference_calibration(intervals["primary"][str(years)]["gain_M3_M2"],
                                               reference_means, identity) for years in (3, 6)}
        record["reference_replicas"] = reference_records
    return record, output_scores
