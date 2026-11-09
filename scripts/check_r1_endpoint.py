"""Independently audit completed R1c serialized histories without refitting.

    python scripts/check_r1_endpoint.py --run outputs/r1c_frozen_0594146 \
        --output outputs/r1_endpoint_independent_cli_check

The output path must not exist. The first history is null000; a second history
is selected only to exercise a positive fitted duration coefficient.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "outputs/a10d_run_8f5df44/a10d_oc"
TOL = 1e-9
INSPECTED = {}
FAILURES = Counter()
UNDERFLOW = Counter()


def read(path):
    payload = path.read_bytes()
    INSPECTED[path_label(path)] = hashlib.sha256(payload).hexdigest()
    return payload


def path_label(path):
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def load(path):
    return json.loads(read(path))


def lines(path):
    return [json.loads(line) for line in read(path).splitlines()]


def require(condition, message):
    if not condition:
        FAILURES[message] += 1


def sf_log(time, location, sigma, label):
    if time <= 0:
        return 0.0
    probability = .5 * math.erfc((math.log(time) - location) / (sigma * math.sqrt(2)))
    if probability == 0.0:
        UNDERFLOW[label] += 1
        raise ArithmeticError("scalar erfc tail underflow")
    return math.log(probability)


def route(feature, bundle, requested):
    if feature.get("landmark_available") is False or feature.get("end_t") is None:
        return "R0"
    require(feature["end_t"] <= feature["issue_time"] + 1e-10, "known end after issue")
    if requested == "M0":
        return "M0"
    previous = feature.get("previous_gap")
    if feature.get("previous_gap_covered") is not True or previous is None or previous <= 0:
        return "M0"
    if requested == "M2":
        return "M2"
    mark = bundle["models"][requested]
    if mark["coefficients"]["beta"] == 0.0:
        return "M2"
    duration = (feature["end_t"] - feature["onset_t"] if feature.get("onset_t") is not None else feature.get("duration")) if requested == "M3" else feature.get("previous_duration")
    return requested if duration is not None and duration > 0 else "M2"


def scalar_score(feature, evidence, bundle, requested, label):
    selected = route(feature, bundle, requested)
    if selected == "R0":
        model = bundle["r0"]
        end = feature["issue_time"]
        location = model["intercept"]
    else:
        model = bundle["models"][selected]
        end = feature["end_t"]
        location = model["intercept"]
        if selected in ("M2", "M3", "P3"):
            baseline = bundle["models"]["M2"]
            location = baseline["intercept"]
            previous = (math.log(feature["previous_gap"]) - baseline["centers"]["previous_gap"]) / baseline["scales"]["previous_gap"]
            earlier = feature.get("earlier_gaps") or []
            level = (statistics.fmean(earlier) - baseline["centers"]["earlier_level"]) / baseline["scales"]["earlier_level"] if earlier else 0.0
            location += baseline["coefficients"]["previous_gap"] * previous
            if bundle["local_level"]:
                location += baseline["coefficients"]["earlier_level"] * level
            if selected in ("M3", "P3"):
                duration = (end - feature["onset_t"] if feature.get("onset_t") is not None else feature["duration"]) if selected == "M3" else feature["previous_duration"]
                location += model["coefficients"]["beta"] * (math.log(duration) - model["centers"]["mark"]) / model["scales"]["mark"]
    sigma, issue = model["sigma"], feature["issue_time"]
    age = issue - end
    require(age >= 0, "negative conditional age")
    denominator = sf_log(age, location, sigma, label)
    if evidence["kind"] == "point":
        wait = evidence["onset_t"] - end
        require(evidence["onset_t"] > issue and wait > 0, "point not after issue")
        z = (math.log(wait) - location) / sigma
        numerator = -.5 * z * z - math.log(wait * sigma) - .5 * math.log(2 * math.pi)
    elif evidence["kind"] == "right_censored":
        require(evidence["censor_at"] >= issue, "censor before issue")
        numerator = sf_log(evidence["censor_at"] - end, location, sigma, label)
    elif evidence["kind"] == "interval":
        lower, upper = evidence["onset_lo"] - end, evidence["onset_hi"] - end
        require(lower >= age - 1e-10 and upper > lower, "invalid legacy interval support")
        lower_log = sf_log(lower, location, sigma, label)
        upper_log = sf_log(upper, location, sigma, label)
        mass_ratio = -math.expm1(upper_log - lower_log)
        if mass_ratio <= 0:
            UNDERFLOW[label + " interval mass cancellation"] += 1
            raise ArithmeticError("scalar interval mass cancellation")
        numerator = lower_log + math.log(mass_ratio)
    else:
        raise ValueError("unexpected truth evidence")
    return numerator - denominator, selected


def index(rows, label):
    found = {row["emission_index"]: row for row in rows}
    require(len(found) == len(rows), label + " duplicate IDs")
    return found


def expected_anchors(features, truth, metadata):
    used, anchors = set(), {}
    for feature in sorted(features.values(), key=lambda f: f["issue_time"]):
        issue = feature["issue_time"]
        block = next((b for b in metadata["blocks"] if b["synthetic_start"] <= issue < b["synthetic_stop"]), None)
        if block is None:
            continue
        block_truth = [event for event in truth if event["block"] == block["block"]]
        matches = [event for event in block_truth if event["onset"] <= feature["bright_first_at"] <= event["end"]]
        if len(matches) != 1:
            continue
        event = matches[0]
        repeated = event["id"] in used
        used.add(event["id"])
        completed = event["end"] <= issue
        intervening = any(event["end"] < e["onset"] <= issue for e in block_truth)
        active = any(e["id"] != event["id"] and e["onset"] <= issue <= e["end"] for e in block_truth)
        if not repeated and completed and not intervening and not active:
            anchors[feature["emission_index"]] = event["id"]
    return anchors


def audit(case, replicate, old_receipt, run):
    name = f"{case}-{replicate:03d}"
    complete = load(run / f"{name}-complete.json")
    record = load(run / f"{name}-record.json")
    evidence = load(run / f"{name}-evidence.json")
    feature_rows = lines(run / f"{name}-features.jsonl")
    score_rows = lines(run / f"{name}-scores.jsonl")
    require(all(complete[key] == value for key, value in record.items()), name + " completion marker mismatch")
    features = {}
    for dose in (0.0, 1.0, 2.0, 4.0, 6.0):
        features[dose] = index([row["feature"] for row in feature_rows if row["sigma"] == dose], name + " feature")
    for group in features.values():
        require(set(group) == set(features[0.0]), name + " dose feature population changed")
        require(all(group[key]["issue_time"] == features[0.0][key]["issue_time"] for key in group), name + " dose issue times changed")
    anchors = expected_anchors(features[0.0], evidence["truth"], record["meta"])
    saved_anchors = {row["emission_index"]: row["truth_id"] for row in record["classifications"] if row["classification"] == "fixed_anchor"}
    require(anchors == saved_anchors, name + " independently derived anchors mismatch")
    cutoff = record["meta"]["training_cutoff"]
    test_ids = {key for key, feature in features[0.0].items() if feature["issue_time"] >= cutoff}
    anchor_ids = set(anchors) & test_ids
    truths = index(evidence["evaluation_truth"], name + " evaluation truth")
    require(set(truths) == anchor_ids, name + " truth anchor population mismatch")
    require(len(evidence["training_truth"]) == len(anchors) - len(anchor_ids), name + " training truth anchor count mismatch")
    extracted = index(evidence["evaluation_extracted"], name + " extracted evidence")
    truth_by_id = {event["id"]: event for event in evidence["truth"]}
    cutoff_checked, cutoff_unavailable = 0, 0
    for key, outcome in truths.items():
        current = truth_by_id[anchors[key]]
        successors = [event for event in evidence["truth"] if event["block"] == current["block"] and event["onset"] > current["end"]]
        successor = min(successors, key=lambda event: event["onset"]) if successors else None
        require(outcome["truth_id"] == (successor["id"] if successor else None), name + " next true event mismatch")
        require(successor is None or successor["onset"] > outcome["issue_time"], name + " true risk set not quiescent")
        stop = extracted[key].get("stopping_cutoff")
        if stop is not None:
            block = next(b for b in record["meta"]["blocks"] if b["synthetic_start"] <= outcome["issue_time"] < b["synthetic_stop"])
            stop = min(stop, block["synthetic_stop"])
            expected_kind = "point" if successor is not None and successor["onset"] <= stop else "right_censored"
            require(outcome["kind"] == expected_kind, name + " truth classification versus administrative cutoff mismatch")
            if expected_kind == "right_censored":
                require(outcome["censor_at"] == stop, name + " true administrative censor mismatch")
            cutoff_checked += 1
        else:
            cutoff_unavailable += 1
        if outcome["kind"] == "point":
            require(successor is not None and outcome["onset_t"] == successor["onset"], name + " exact point target mismatch")
    groups = []
    for dose in (0.0, 1.0, 2.0, 4.0, 6.0):
        groups.append(("fixed_anchor_truth", dose, features[dose], record["sigmas"][str(dose)]["model"]))
    oracle = index([feature for feature in evidence["oracle_features"] if feature["issue_time"] >= cutoff], name + " oracle features")
    require(set(oracle) == anchor_ids, name + " oracle anchor population mismatch")
    groups.append(("composite_oracle_truth", 0.0, oracle, record["oracle"]["model"]))
    numerical = []
    truth_results = {}
    for branch, dose, available, model in groups:
        label = f"{name} {branch} {dose}"
        require(model["endpoint_mode"] == "point" and model["mark_mode"] == "log_duration", label + " unsupported prediction contract")
        saved = index([row for row in score_rows if row["route"] == branch and row["sigma"] == dose], label)
        require(set(saved) == anchor_ids, label + " score anchor population mismatch")
        errors = {"M2": [], "M3": []}
        routes = {"M2": Counter(), "M3": Counter()}
        computed_gains = {}
        for key in anchor_ids:
            computed = {}
            for requested in ("M2", "M3"):
                try:
                    value, selected = scalar_score(available[key], truths[key], model, requested, label)
                except ArithmeticError:
                    FAILURES[label + " erfc underflow"] += 1
                    continue
                require(selected == saved[key][requested + "_route"], label + " " + requested + " route mismatch")
                require(saved[key]["kind"] == truths[key]["kind"] and saved[key]["reason"] == truths[key]["reason"], label + " outcome label mismatch")
                error = abs(value - saved[key][requested])
                errors[requested].append(error)
                routes[requested][selected] += 1
                require(error <= TOL, label + " " + requested + " score discrepancy")
                computed[requested] = value
            if len(computed) == 2:
                computed_gains[key] = computed["M3"] - computed["M2"]
                require(abs(computed_gains[key] - saved[key]["gain_M3_M2"]) <= TOL, label + " gain discrepancy")
        truth_results[(branch, dose)] = computed_gains
        numerical.append({"branch": branch, "dose_days": dose, "rows": len(saved),
                          "evidence_kinds": dict(Counter(truths[key]["kind"] for key in saved)),
                          "M3_beta": model["models"]["M3"]["coefficients"]["beta"],
                          "maximum_absolute_error": {key: max(value, default=None) for key, value in errors.items()},
                          "route_counts": {key: dict(value) for key, value in routes.items()}})
    shared_subsets = []
    previous_shared = None
    for dose in (0.0, 1.0, 2.0, 4.0, 6.0):
        extracted_scores = index([row for row in score_rows if row["route"] == "all_issued_extracted" and row["sigma"] == dose], name + " extracted scores")
        require(set(extracted_scores) == test_ids, name + " all-issued extracted population mismatch")
        shared = {key for key in anchor_ids if extracted_scores[key]["gain_M3_M2"] is not None}
        missing = anchor_ids - shared
        summary = record["sigmas"][str(dose)]
        require(set(summary["extracted_unscoreable_anchor_ids"]) == missing, name + " unscoreable anchor list mismatch")
        require(summary["fixed_anchor_extracted"]["n"] == len(shared), name + " fixed extracted n mismatch")
        require(summary["fixed_anchor_extracted"]["excluded"] == len(missing), name + " fixed extracted exclusions mismatch")
        require(summary["fixed_anchor_truth"]["n"] == len(anchor_ids), name + " truth n mismatch")
        require(summary["extracted_scoreable_anchor_truth"]["n"] == len(shared), name + " shared truth n mismatch")
        if shared and shared <= set(truth_results[("fixed_anchor_truth", dose)]):
            expected_mean = statistics.fmean(truth_results[("fixed_anchor_truth", dose)][key] for key in shared)
            require(abs(summary["extracted_scoreable_anchor_truth"]["gain_M3_M2"]["mean"] - expected_mean) <= TOL, name + " shared truth mean mismatch")
            expected_extracted = statistics.fmean(extracted_scores[key]["gain_M3_M2"] for key in shared)
            require(abs(summary["fixed_anchor_extracted"]["gain_M3_M2"]["mean"] - expected_extracted) <= TOL, name + " shared extracted mean mismatch")
        elif shared:
            FAILURES[name + " shared truth mean unavailable after scalar numerical failure"] += 1
        if previous_shared is not None:
            require(shared == previous_shared, name + " extracted scored anchor subset changed across dose")
        previous_shared = shared
        shared_subsets.append({"dose_days": dose, "all_fixed_anchors": len(anchor_ids), "shared_scored_anchors": len(shared), "extracted_excluded_anchors": len(missing)})
    old_name = f"v2-phase-{case}-{replicate:03d}"
    for suffix in (".json", "-scores.jsonl"):
        path = OLD / (old_name + suffix)
        require(hashlib.sha256(read(path)).hexdigest() == old_receipt["files_sha256"][path.name], name + " retained source output hash mismatch")
    old = load(OLD / (old_name + ".json"))["result"]
    old_scores = index([row for row in lines(OLD / (old_name + "-scores.jsonl")) if row["variant"] == "primary"], name + " retained primary scores")
    new_scores = index([row for row in score_rows if row["route"] == "legacy_v3_extracted" and row["M2"] is not None], name + " legacy replay scores")
    require(set(old_scores) == set(new_scores), name + " legacy replay scored population mismatch")
    legacy_errors = []
    refit_exceedances = 0
    replay_errors = []
    old_evidence = index(evidence["evaluation_legacy_v3"], name + " legacy evidence")
    for key in set(old_scores) & set(new_scores):
        for requested in ("M0", "M2", "M3", "P3"):
            require(old_scores[key][requested + "_route"] == new_scores[key][requested + "_route"], name + " legacy route mismatch")
            error = abs(old_scores[key][requested] - new_scores[key][requested])
            legacy_errors.append(error)
            refit_exceedances += error > TOL
            try:
                scalar, replay_route = scalar_score(features[0.0][key], old_evidence[key], old["models"]["primary"], requested, name + " retained parameter replay")
                require(replay_route == old_scores[key][requested + "_route"], name + " retained-parameter scalar replay route mismatch")
                replay_error = abs(scalar - old_scores[key][requested])
                replay_errors.append(replay_error)
                require(replay_error <= TOL, name + " retained-parameter scalar replay score discrepancy")
            except ArithmeticError:
                FAILURES[name + " retained-parameter scalar replay tail underflow"] += 1
        for field in ("issue_time", "kind", "reason"):
            require(old_scores[key][field] == new_scores[key][field], name + " legacy outcome/issue mismatch")
    trace_checked = False
    if "audit_trace" in old:
        trace_checked = True
        old_features = old["audit_trace"]["ledger"]["0.0"]
        old_by_id = index(old_features["training"] + old_features["evaluation"], name + " retained ledger trace")
        require(set(old_by_id) == set(features[0.0]), name + " legacy ledger population mismatch")
        for key in old_by_id:
            stripped = {field: value for field, value in features[0.0][key].items() if not field.startswith("r1_")}
            require(stripped == old_by_id[key], name + " sigma-zero feature differs from retained trace")
        for period in ("training", "evaluation"):
            require(evidence[period + "_legacy_v3"] == old["audit_trace"]["evidence"]["0.0"][period], name + " legacy evidence differs from retained trace")
    return {"case": case, "replicate": replicate, "independently_rederived_fixed_anchors": len(anchors),
            "evaluation_fixed_anchors": len(anchor_ids), "truth_routing_and_scalar_scores": numerical,
            "shared_subsets": shared_subsets,
            "truth_administrative_cutoff_checks": {"checked_from_retained_v4_stopping_cutoff": cutoff_checked,
                                                   "unavailable_because_extracted_evidence_excluded": cutoff_unavailable},
            "legacy_replay": {"scored_population": len(new_scores), "retained_trace_available_and_checked": trace_checked,
                              "all_routes_and_individual_scores_checked": True,
                              "retained_parameter_scalar_replay_maximum_absolute_error": max(replay_errors, default=None),
                              "new_refit_vs_retained_maximum_absolute_score_difference": max(legacy_errors, default=None),
                              "new_refit_vs_retained_model_scores_above_tolerance": refit_exceedances,
                              "interpretation": "The independently optimized legacy comparator is a refit, not the retained parameter replay. Its absolute-score differences are retained explicitly; the frozen-parameter replay is checked separately at unchanged 1e-9 tolerance."},
            "limitation": "No raw visit stream is retained in these files. Truth-cutoff checks use separately retained administrative stopping metadata where available; they do not independently reconstruct coverage from observations."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="Completed-history R1c output directory")
    parser.add_argument("--output", type=Path, required=True, help="New aggregate audit directory; must not exist")
    args = parser.parse_args(argv)
    run = args.run.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error("output path already exists; choose a new directory to preserve audit evidence")
    if not (run / "receipt.json").is_file():
        parser.error("run directory has no receipt.json")
    output.mkdir(parents=True, exist_ok=False)
    receipt = load(run / "receipt.json")
    old_receipt = load(OLD / "receipt.json")
    require(read(OLD / "receipt.json") == read(ROOT / "data/simulations/a10d_20261108/run-receipt.json"), "original simulation receipt differs from committed receipt")
    selected, inspected_parameters = None, []
    for case in ("null", "structured"):
        for replicate in range(40):
            path = run / f"{case}-{replicate:03d}-complete.json"
            if not path.exists():
                continue
            complete = load(path)
            inspected_parameters.append({"case": case, "replicate": replicate})
            positive = any(row["model"]["models"]["M3"]["coefficients"]["beta"] > 0 for row in complete["sigmas"].values())
            positive = positive or complete["oracle"]["model"]["models"]["M3"]["coefficients"]["beta"] > 0
            if positive:
                selected = (case, replicate)
                break
        if selected:
            break
    require(selected is not None, "no completed positive-beta branch available")
    tasks = [("null", 0)] + ([selected] if selected and selected != ("null", 0) else [])
    results = [audit(case, replicate, old_receipt, run) for case, replicate in tasks]
    prior_first_pass = []
    for filename in ("first-pass-summary.json", "first-pass-report.md"):
        path = ROOT / "outputs/r1_endpoint_independent_check" / filename
        if path.is_file():
            read(path)
            prior_first_pass.append(path_label(path))
    INSPECTED[str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for name, expected in list(INSPECTED.items()):
        if name == path_label(run / "receipt.json"):
            continue
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "inspected file changed during audit")
    refit_differences = sum(r["legacy_replay"]["new_refit_vs_retained_model_scores_above_tolerance"] for r in results)
    result = {"status": "failed" if FAILURES else "passed_with_refit_differences" if refit_differences else "passed", "absolute_tolerance": TOL,
              "failures": dict(FAILURES), "scalar_erfc_tail_underflows": dict(UNDERFLOW),
              "prior_private_first_pass_evidence": prior_first_pass,
              "refit_replay_distinction": "A prior scratch check asserted new-refit scores equal retained scores at 1e-9 and failed. Its private evidence remains untouched. This audit separates refit differences from frozen-parameter replay without changing tolerance.",
              "score_calculation": "Scalar erfc normal survival and closed-form lognormal density; independently rebuilt routes and frozen covariate transforms; no candidate scoring functions imported.",
              "selection": {"mandatory_history": "null000", "additional_history": {"case": selected[0], "replicate": selected[1]} if selected else None,
                            "rule": "First available completed history in null000..039 then structured000..039 order with positive M3 beta in any measured dose or composite oracle; parameter branch coverage only, no score-based or inferential selection.",
                            "completion_metadata_inspected_in_order": inspected_parameters},
              "batch_receipt_at_read_status": receipt["status"], "freeze_commit": receipt["freeze_commit"],
              "histories": results, "input_sha256": INSPECTED,
              "limitations": ["The positive-beta history is selected for numerical branch coverage only, without an inferential comparison or selected scientific result.",
                              "Verification is limited to the audited completed histories listed here, irrespective of the batch receipt status at read; no overall grid result or operating characteristic is certified.",
                              "No fitting, simulation, source changes, or new observation access was performed."]}
    (output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    rows = []
    for history in results:
        maximum = max((error for row in history["truth_routing_and_scalar_scores"]
                       for model in ("M2", "M3") if (error := row["maximum_absolute_error"][model]) is not None), default=None)
        shown = ["unavailable" if value is None else f"{value:.3g}" for value in
                 (maximum, history["legacy_replay"]["retained_parameter_scalar_replay_maximum_absolute_error"],
                  history["legacy_replay"]["new_refit_vs_retained_maximum_absolute_score_difference"])]
        rows.append(f"| {history['case']}{history['replicate']:03d} | {history['evaluation_fixed_anchors']} | " + " | ".join(shown) + " |")
    (output / "report.md").write_text("# Independent scalar R1c score check\n\n"
        f"Status: {result['status']}; tolerance {TOL:g}; failures {sum(FAILURES.values())}; erfc underflows {sum(UNDERFLOW.values())}.\n\n"
        f"Batch receipt status at read: {receipt['status']}. Verification covers only the histories listed below.\n\n"
        "| History | Evaluation fixed anchors per dose | Maximum truth-score error | Maximum retained-parameter replay error | Maximum new-refit difference |\n"
        "|---|---:|---:|---:|---:|\n" + "\n".join(rows) + "\n\n"
        "All five measured doses and the composite oracle were checked using scalar normal survival/lognormal density, "
        "with routes and covariate transforms reconstructed from serialized parameters. Anchor sets, original issue times "
        "and exact extracted/truth common subsets were checked across doses. Legacy primary populations, routes and "
        "individual scores were compared with receipt-verified retained A10d streams; null000 also supplies an exact "
        "original ledger/evidence trace.\n\n"
        "The new legacy-v3 refits differ from retained absolute scores above the requested 1e-9 tolerance. "
        "That first-pass failure is preserved. Frozen-parameter replay is a separate calculation; no tolerance was relaxed. "
        "The final status distinguishes these refit differences from failures of numerical replay.\n\n"
        "The additional history was selected solely as the first completed positive-beta parameter "
        "branch in the declared seed order. Its audited coefficient values are retained in summary.json. This is numerical coverage, "
        "not an inferential comparison or selected scientific result.\n\n"
        "Truth risk sets/next-event identities were rederived from retained truth and sigma-zero features. "
        "Administrative cutoffs were checked against retained v4 stopping metadata where available. No raw visit "
        "stream is retained in these files, so coverage cutoffs were not reconstructed independently from observations. "
        "No fit, new simulation or source edit was made by this check. Input hashes are in summary.json.\n")
    print(json.dumps({"status": result["status"], "failures": dict(FAILURES), "underflows": dict(UNDERFLOW), "histories": tasks}))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
