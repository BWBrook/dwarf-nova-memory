"""Independent R1d/e illustration and finite-simulation aggregate calculations.

Offline, from the previously opened frozen real run and retained synthetic
history records. No model fit, extraction, archive call, or protected-block
inspection. All emitted data are aggregate or the already public illustration.
"""

from __future__ import annotations

import argparse
from bisect import bisect_left
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist, fmean, median, quantiles, stdev
import subprocess

from scipy.stats import spearmanr, t as student_t

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 2436934.5
STOP = 2458119.5
WIDTH = 6 * 365.25
SELECTOR = "first 1960 issuance with extracted onset after JD2436934.5; minimum issue time, then emission index"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value) -> str:
    payload = json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def load_verified(path: Path, expected: str):
    if digest(path) != expected:
        raise ValueError(f"retained hash mismatch: {path.relative_to(ROOT)}")
    return json.loads(path.read_text())


def cdf_binomial(count: int, trials: int, probability: float) -> float:
    return math.fsum(math.comb(trials, k) * probability ** k * (1 - probability) ** (trials - k)
                     for k in range(count + 1))


def solve_decreasing(function, target: float) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if function(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def binomial_interval(successes: int, trials: int) -> dict:
    if not 0 <= successes <= trials or trials < 1:
        raise ValueError("invalid binomial count")
    rate = successes / trials
    return {
        "successes": successes, "trials": trials, "rate": rate,
        "rate_mc_se": math.sqrt(rate * (1 - rate) / trials),
        "exact_lower95": solve_decreasing(lambda p: cdf_binomial(successes - 1, trials, p), .975) if successes else 0.0,
        "exact_upper95": solve_decreasing(lambda p: cdf_binomial(successes, trials, p), .025) if successes < trials else 1.0,
        "one_sided_upper95": solve_decreasing(lambda p: cdf_binomial(successes, trials, p), .05) if successes < trials else 1.0,
    }


def compare(saved, calculated, context: str, failures: list, tolerance: float = 1e-12) -> None:
    if isinstance(calculated, (float, int)) and not isinstance(calculated, bool):
        equal = saved is not None and abs(float(saved) - calculated) <= tolerance
    else:
        equal = saved == calculated
    if not equal:
        failures.append({"context": context, "saved": saved, "calculated": calculated})


def interpolated(x: list[float], y: list[float], target: float) -> float:
    index = bisect_left(x, target)
    if index == 0:
        return y[0]
    if index == len(x):
        raise ValueError("interpolation outside the saved grid")
    fraction = (target - x[index - 1]) / (x[index] - x[index - 1])
    return y[index - 1] + fraction * (y[index] - y[index - 1])


def lognormal_survival(time: float, location: float, sigma: float) -> float:
    return 1.0 if time <= 0 else .5 * math.erfc((math.log(time) - location) / (sigma * math.sqrt(2)))


def remaining_cdf(wait: float, age: float, location: float, sigma: float) -> float:
    return 1 - lognormal_survival(age + wait, location, sigma) / lognormal_survival(age, location, sigma)


def remaining_median(age: float, location: float, sigma: float) -> float:
    tail_probability = .5 * lognormal_survival(age, location, sigma)
    quantile = NormalDist().inv_cdf(1 - tail_probability)
    return math.exp(location + sigma * quantile) - age


def figure_example(ledger: list[dict], evidence: list[dict], parameters: dict, public: dict,
                   failures: list) -> dict:
    eligible = [feature for feature in ledger if ORIGIN <= feature["issue_time"] < ORIGIN + 366
                and feature.get("onset_t") is not None and feature["onset_t"] > ORIGIN]
    chosen = min(eligible, key=lambda feature: (feature["issue_time"], feature["emission_index"]))
    outcome = next(e for e in evidence if e["emission_index"] == chosen["emission_index"])
    if not chosen["previous_gap_covered"] or chosen["previous_gap"] <= 0 or outcome["kind"] != "interval":
        raise ValueError("the preserved date selector no longer supports its illustration")
    feature_sha, outcome_sha = canonical_digest(chosen), canonical_digest(outcome)
    compare(public["illustration"]["selector"], SELECTOR, "figure selector", failures)
    compare(public["illustration"]["source_feature_sha256"], feature_sha, "figure selected feature", failures)
    compare(public["illustration"]["source_outcome_sha256"], outcome_sha, "figure selected outcome", failures)
    model_inputs = {"previous_gap": math.log(chosen["previous_gap"]),
                    "earlier_level": fmean(chosen["earlier_gaps"]) if chosen["earlier_gaps"] else None}
    age = chosen["issue_time"] - chosen["end_t"]
    curves = public["conditional_remaining_wait_cdf"]
    grid = curves["days_from_issue"]
    models = {}
    for name in ("M2", "M3"):
        model = parameters["primary"]["models"][name]
        location = model["intercept"]
        for term in ("previous_gap", "earlier_level"):
            raw = model_inputs[term] if model_inputs[term] is not None else model["centers"][term]
            location += model["coefficients"][term] * (raw - model["centers"][term]) / model["scales"][term]
        if name == "M3":
            duration = chosen["end_t"] - chosen["onset_t"]
            location += model["coefficients"]["beta"] * (math.log(duration) - model["centers"]["mark"]) / model["scales"]["mark"]
        sigma = model["sigma"]
        recalculated = [remaining_cdf(wait, age, location, sigma) for wait in grid]
        maximum_error = max(abs(a - b) for a, b in zip(recalculated, curves["models"][name]))
        compare(maximum_error, 0.0, f"figure {name} entire grid", failures, 1e-13)
        analytic = remaining_median(age, location, sigma)
        grid_median = interpolated(curves["models"][name], grid, .5)
        probability = remaining_cdf(30.0, age, location, sigma)
        models[name] = {"conditional_median_remaining_wait_days": analytic,
                        "public_grid_interpolated_median_days": grid_median,
                        "grid_median_minus_analytic_days": grid_median - analytic,
                        "probability_onset_within_30_days": probability,
                        "public_grid_probability_within_30_days": interpolated(grid, curves["models"][name], 30.0),
                        "max_absolute_public_grid_cdf_error": maximum_error}
    return {"selector": SELECTOR, "selected_feature_sha256": feature_sha, "selected_outcome_sha256": outcome_sha,
            "models": models,
            "median_change_days_M3_minus_M2": models["M3"]["conditional_median_remaining_wait_days"] - models["M2"]["conditional_median_remaining_wait_days"],
            "probability_change_percentage_points_M3_minus_M2": 100 * (models["M3"]["probability_onset_within_30_days"] - models["M2"]["probability_onset_within_30_days"]),
            "interpretation": "One observation-time-selected illustration, using the prefix point end/duration and conditioning once on survival to issue; not an average effect or utility estimate; not the endpoint-integrated scoring rule."}


def real_interval(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    values = [row["gain"] for row in rows]
    average = fmean(values)
    for row in rows:
        groups[math.floor((row["issue_time"] - ORIGIN) / WIDTH)].append(row["gain"])
    count, clusters = len(rows), len(groups)
    score_sums = [math.fsum(value - average for value in group) for group in groups.values()]
    standard_error = math.sqrt(clusters * math.fsum(value * value for value in score_sums) / ((clusters - 1) * count ** 2))
    radius = float(student_t.ppf(.95, clusters - 1)) * standard_error
    return {"n": count, "blocks": clusters, "mean": average, "lower90": average - radius, "upper90": average + radius}


def check_a10n(ledger: list[dict], evidence: list[dict], scores: list[dict], saved: dict,
               settings: list[dict], failures: list) -> dict:
    by_id = {row["emission_index"]: row for row in scores}
    real = [{"width": f["end_hi"] - f["end_lo"], "gain": by_id[f["emission_index"]]["gain_M3_M2"],
             "issue_time": f["issue_time"]} for f in ledger]
    changed = sum(math.floor((row["issue_time"] - ORIGIN) / WIDTH) !=
                  math.floor((row["issue_time"] - 2436934.0) / WIDTH) for row in real)
    widths = [row["width"] for row in real]
    med, cuts = median(widths), quantiles(widths, n=3)
    split = {"all": real_interval(real),
             "end_bracket_width_days": {"median": med, "tercile_cuts": cuts, "min": min(widths), "max": max(widths)},
             "narrow_half": real_interval([row for row in real if row["width"] <= med]),
             "wide_half": real_interval([row for row in real if row["width"] > med]),
             "terciles": [real_interval([row for row in real if lo < row["width"] <= hi])
                          for lo, hi in zip([-math.inf, *cuts], [*cuts, math.inf])]}
    rho, probability = spearmanr(widths, [row["gain"] for row in real])
    split["spearman_width_gain"] = {"rho": float(rho), "p": float(probability)}
    for section in ("all", "narrow_half", "wide_half", "spearman_width_gain"):
        for field, calculated in split[section].items():
            compare(saved["end_width_split"][section][field], calculated, f"A10n {section} {field}", failures)
    for index, item in enumerate(split["terciles"]):
        for field, calculated in item.items():
            compare(saved["end_width_split"]["terciles"][index][field], calculated, f"A10n third {index} {field}", failures)
    for field, calculated in split["end_bracket_width_days"].items():
        if isinstance(calculated, list):
            for index, value in enumerate(calculated):
                compare(saved["end_width_split"]["end_bracket_width_days"][field][index], value, f"A10n {field} {index}", failures)
        else:
            compare(saved["end_width_split"]["end_bracket_width_days"][field], calculated, f"A10n {field}", failures)
    censored_ids = {e["emission_index"] for e in evidence if e["kind"] == "right_censored"}
    censored_sum = math.fsum(by_id[index]["gain_M3_M2"] for index in censored_ids)
    all_sum = math.fsum(row["gain"] for row in real)
    censor = {"censored": len(censored_ids), "censored_total_contribution": censored_sum,
              "mean_all": all_sum / len(real), "mean_excluding_censored": (all_sum - censored_sum) / (len(real) - len(censored_ids))}
    for field, calculated in censor.items():
        compare(saved["censor_audit"][field], calculated, f"A10n censor {field}", failures)
    calculated_settings = {(setting["family"], setting["case"]): setting for setting in settings}
    for old in saved["simulated_gain_M3_M2"]:
        fresh = calculated_settings[(old["family"], old["case"])]
        for old_key, new_key in (("mean_gain", "mean_gain"), ("mc_se", "mean_gain_mc_se"), ("trial_sd", "trial_sd")):
            compare(old[old_key], fresh[new_key], f"A10n {old['family']} {old['case']} {old_key}", failures)
        compare(old["confirmations"], f"{fresh['confirmation']['successes']}/{fresh['confirmation']['trials']}", "A10n confirmations", failures)
    return {"correct_real_six_year_origin_jd": ORIGIN, "a10n_script_origin_jd": 2436934.0,
            "issuances_with_changed_block_assignment": changed, "end_width_split": split,
            "censor_sensitivity": censor, "all_numerical_a10n_aggregates_match": not any(str(f["context"]).startswith("A10n") for f in failures),
            "censor_candidate_relations": "Not re-inferred from next emission here; the separate R1a audit verifies actual frozen candidates."}


def recompute_reference(result: dict, years: str, failures: list, context: str) -> dict:
    interval = result["intervals"]["primary"][years]["gain_M3_M2"]
    saved = result["reference_calibration"][years]
    beta = result["models"]["primary"]["models"]["M3"]["coefficients"]["beta"]
    replicas = result["reference_replicas"]
    if beta == 0:
        if interval["estimate"] != 0 or interval["se"] != 0 or replicas:
            raise ValueError("nonidentity values in a zero-beta reference history")
        for field, calculated in (("interior", False), ("joint_mc_covers_zero", True),
                                  ("reference_mean", 0.0), ("reference_se", 0.0),
                                  ("reference_means", []), ("naive_reference_contained", True),
                                  ("method", "analytic_zero_identity")):
            compare(saved.get(field), calculated, f"{context} identity {field}", failures)
        return {"interior": False, "covered": True, "reference_mean": 0.0}
    means = [replica["estimate"] for replica in replicas]
    if len(means) != 6:
        raise ValueError("six matched reference means required")
    reference_mean, reference_se = fmean(means), stdev(means) / math.sqrt(6)
    v, u = interval["se"] ** 2, reference_se ** 2
    degrees = (v + u) ** 2 / (v ** 2 / (interval["blocks"] - 1) + u ** 2 / 5)
    radius = float(student_t.ppf(.95, degrees)) * math.sqrt(v + u)
    difference = interval["estimate"] - reference_mean
    covered = abs(difference) <= radius
    for field, calculated in (("reference_mean", reference_mean), ("reference_se", reference_se),
                              ("joint_mc_df", degrees), ("difference", difference),
                              ("joint_mc_lower", difference - radius), ("joint_mc_upper", difference + radius),
                              ("joint_mc_covers_zero", covered), ("interior", True),
                              ("naive_reference_contained", interval["lower"] <= reference_mean <= interval["upper"])):
        compare(saved.get(field), calculated, f"{context} {field}", failures)
    for a, b in zip(saved["reference_means"], means):
        compare(a, b, f"{context} replica estimate", failures)
    return {"interior": True, "covered": covered, "reference_mean": reference_mean}


def simulation_tables(records: list[dict], public_csv: Path, public_report: dict, real_gain: float,
                      failures: list) -> tuple[list[dict], list[dict], list[dict]]:
    groups = defaultdict(list)
    for record in records:
        if not record["success"]:
            raise ValueError("failed retained simulation history")
        groups[tuple(record["task"][:2])].append(record["result"])
    with public_csv.open() as handle:
        committed = {(r["family"], r["case"], r["variant"], int(r["cluster_years"]), r["comparison"]): r
                     for r in csv.DictReader(handle)}
    all_rows, settings = [], []
    for (family, case), histories in sorted(groups.items()):
        for variant, intervals in histories[0]["intervals"].items():
            for years, comparisons in intervals.items():
                for comparison in comparisons:
                    values = [history["intervals"][variant][years][comparison] for history in histories]
                    estimates = [value["estimate"] for value in values]
                    confirmations = [value["estimate"] - float(student_t.ppf(.95, value["blocks"] - 1)) * value["se"] > 0
                                     for value in values]
                    for value, recomputed in zip(values, confirmations):
                        compare(value["confirmed"], recomputed, "simulation retained confirmation flag", failures)
                    uncertainty = binomial_interval(sum(confirmations), len(values))
                    row = {"family": family, "case": case, "variant": variant, "cluster_years": int(years),
                           "comparison": comparison, "mean_gain": fmean(estimates), "trial_sd": stdev(estimates),
                           "mean_gain_mc_se": stdev(estimates) / math.sqrt(len(estimates)),
                           "mean_n": fmean(value["n"] for value in values), **uncertainty}
                    old = committed[(family, case, variant, int(years), comparison)]
                    for field in ("mean_gain", "trial_sd", "mean_n", "successes", "trials", "rate",
                                  "exact_lower95", "exact_upper95", "one_sided_upper95"):
                        compare(old[field], row[field], f"A10d {family} {case} {variant} {years} {comparison} {field}", failures)
                    compare(old["mc_se"], row["rate_mc_se"], "A10d binomial rate MCSE", failures)
                    all_rows.append(row)
                    if (variant, years, comparison) == ("primary", "6", "gain_M3_M2"):
                        settings.append({"family": family, "case": case, "mean_gain": row["mean_gain"],
                                         "trial_sd": row["trial_sd"], "mean_gain_mc_se": row["mean_gain_mc_se"],
                                         "confirmation": uncertainty, "minimum_individual_history_mean_gain": min(estimates),
                                         "maximum_individual_history_mean_gain": max(estimates),
                                         "histories_at_or_above_real_mean_gain": sum(value >= real_gain for value in estimates),
                                         "real_mean_gain_minus_scenario_mean": real_gain - fmean(estimates)})
    if len(all_rows) != len(committed):
        raise ValueError("incomplete comparison reconstruction")
    coverage = []
    for case in ("null", "alternative"):
        for years in ("3", "6"):
            entries = [recompute_reference(history, years, failures, f"reference {case} {years}")
                       for history in groups[("v2-phase", case)]]
            interior = [entry for entry in entries if entry["interior"]]
            item = {"case": case, "cluster_years": int(years),
                    "overall": binomial_interval(sum(entry["covered"] for entry in entries), len(entries)),
                    "interior": binomial_interval(sum(entry["covered"] for entry in interior), len(interior))}
            item["undercoverage_p"] = cdf_binomial(item["overall"]["successes"], len(entries), .9)
            item["interior_undercoverage_p"] = cdf_binomial(item["interior"]["successes"], len(interior), .9)
            old = next(row for row in public_report["calibration"] if row["case"] == case and row["cluster_years"] == int(years))
            for subset in ("overall", "interior"):
                for field, value in item[subset].items():
                    compare(old[subset]["mc_se" if field == "rate_mc_se" else field], value, f"A10d reference {case} {years} {subset} {field}", failures)
            for field in ("undercoverage_p", "interior_undercoverage_p"):
                compare(old[field], item[field], f"A10d reference {case} {years} {field}", failures)
            coverage.append(item)
    return settings, all_rows, coverage


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/a10h_live_repair_5e39aeb")
    parser.add_argument("--simulations", type=Path, default=ROOT / "outputs/a10d_run_8f5df44/a10d_oc")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/r1_example_simulation_table")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    failures = []
    run_receipt_path = ROOT / "data/provenance/a10i_evaluation_1960_2017/run-receipt.json"
    run_public = json.loads(run_receipt_path.read_text())
    receipt = load_verified(args.run / "receipt.json", run_public["original_run_receipt_sha256"])
    inputs = {}
    for filename in ("ledger-0.0.json", "evidence-0.0.json", "frozen_parameters.json", "primary-scores.json"):
        path = args.run / filename
        inputs[filename] = load_verified(path, receipt["files_sha256"][filename])
    ledger, scores = inputs["ledger-0.0.json"], inputs["primary-scores.json"]
    if any(not ORIGIN <= row["issue_time"] < STOP for row in ledger + scores):
        raise ValueError("record outside the already opened real interval")
    sim_receipt_path = ROOT / "data/simulations/a10d_20261108/run-receipt.json"
    simulation_receipt = load_verified(args.simulations / "receipt.json", digest(sim_receipt_path))
    records = load_verified(args.simulations / "records.json", simulation_receipt["records_sha256"])
    if simulation_receipt["status"] != "completed" or len(records) != 360 or len({tuple(row["task"]) for row in records}) != 360:
        raise ValueError("not the complete fixed simulation grid")
    simulation_config = json.loads((ROOT / "configs/a10d_oc.json").read_text())
    expected = {(family, case, replicate) for family, specification in simulation_config["families"].items()
                for case in specification["cases"] for replicate in range(specification["replicates"])}
    if {tuple(row["task"]) for row in records} != expected:
        raise ValueError("retained simulation task grid differs")
    public_csv = ROOT / "data/simulations/a10d_20261108/comparisons.csv"
    simulation_report = ROOT / "data/simulations/a10d_20261108/report.json"
    figure_data = ROOT / "manuscript/figure-data/fig1-illustration.json"
    triage = ROOT / "data/provenance/a10n_triage/checks.json"
    real_gain = fmean(row["gain_M3_M2"] for row in scores)
    settings, comparisons, coverage = simulation_tables(records, public_csv, json.loads(simulation_report.read_text()), real_gain, failures)
    example = figure_example(ledger, inputs["evidence-0.0.json"], inputs["frozen_parameters.json"], json.loads(figure_data.read_text()), failures)
    a10n = check_a10n(ledger, inputs["evidence-0.0.json"], scores, json.loads(triage.read_text()), settings, failures)
    paths = [Path(__file__), run_receipt_path, args.run / "receipt.json", sim_receipt_path,
             args.simulations / "receipt.json", args.simulations / "records.json", public_csv,
             simulation_report, figure_data, triage, ROOT / "configs/a10d_oc.json"]
    paths.extend(args.run / name for name in inputs)
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "scope": "Independent offline R1d/e post-result calculations; no fits, archive calls, new real inputs, or new confirmation",
              "input_sha256": {str(path.relative_to(ROOT)): digest(path) for path in paths},
              "figure1": example, "settings_primary_six_year": settings, "reference_coverage": coverage,
              "all_simulation_comparison_rows_recomputed": len(comparisons), "histories_recomputed": len(records),
              "original_frozen_real_mean_gain": real_gain,
              "real_mean_exceeds_every_scenario_mean": all(real_gain > row["mean_gain"] for row in settings),
              "real_mean_exceeds_every_individual_history_mean": all(real_gain > row["maximum_individual_history_mean_gain"] for row in settings),
              "individual_histories_at_or_above_real_mean": sum(row["histories_at_or_above_real_mean_gain"] for row in settings),
              "a10n_verification": a10n,
              "limits": ["Simulation means and MCSE describe the frozen finite generator and observation/extraction process, not a population of real dwarf novae.",
                         "Exact binomial intervals cover simulation-history confirmation probabilities under independent histories; observed rates do not certify a true 5% error rate.",
                         "Reference coverage is a joint-Monte-Carlo screen using six finite matched replicas, not coverage against known exact conditional truth.",
                         "Serialized history estimates and replica estimates are reaggregated; synthetic scoring streams are not rescored in this bounded check.",
                         "The date-selected Figure1 illustration supplies no average forecast shift or observing-decision utility."]}
    (args.output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    with (args.output / "all-comparisons.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    table = ["| Family | Setting | Mean gain | MCSE of mean | Confirmations | Exact 95% rate interval | Maximum history mean |",
             "|---|---|---:|---:|---:|---|---:|"]
    for row in settings:
        c = row["confirmation"]
        table.append(f"| {row['family']} | {row['case']} | {row['mean_gain']:.8f} | {row['mean_gain_mc_se']:.8f} | "
                     f"{c['successes']}/{c['trials']} | [{c['exact_lower95']:.4f}, {c['exact_upper95']:.4f}] | {row['maximum_individual_history_mean_gain']:.8f} |")
    (args.output / "report.md").write_text(
        "# R1d/e: illustrative forecasts and finite simulation evidence\n\n"
        "The original date selector and feature/outcome hashes reproduce. At the prefix point end, "
        f"the conditional median remaining wait is {example['models']['M2']['conditional_median_remaining_wait_days']:.4f} d for M2 and "
        f"{example['models']['M3']['conditional_median_remaining_wait_days']:.4f} d for M3. Probability of onset within 30 d is "
        f"{100*example['models']['M2']['probability_onset_within_30_days']:.4f}% and "
        f"{100*example['models']['M3']['probability_onset_within_30_days']:.4f}%. "
        "These are one selected illustration, not an average effect, endpoint-integrated forecast, or utility result.\n\n"
        + "\n".join(table) + "\n\n"
        "The real mean exceeds every scenario mean but does not exceed every individual synthetic-history mean. "
        "Scenario averages and maxima answer different questions. Confirmation-rate intervals are two-sided exact "
        "95% Clopper–Pearson intervals, independently inverted from binomial tails; the MCSE column is for the mean gain, "
        "not for the confirmation rate.\n\n"
        "Six-year reference coverage: null overall 37/40, interior 24/27; alternative overall 34/40, interior 31/37. "
        "Overall counts include exact-zero identity histories. Joint-Monte-Carlo coverage uses six finite matched references, "
        "not known exact expected gains. These screens do not certify a true 5% error rate or a population coverage guarantee.\n\n"
        f"All {len(comparisons)} committed comparison rows and A10n's numerical aggregates reproduce within tolerance. "
        f"The proper real six-year block origin is JD {ORIGIN}; replacing A10n's JD 2436934.0 origin changes "
        f"{a10n['issuances_with_changed_block_assignment']} of {len(ledger)} assignments in this record. "
        "This check uses the proper origin throughout.\n\n"
        f"Status: {result['status']}; {len(failures)} discrepancies. Inputs are receipt-verified and hashed in summary.json. "
        "No real per-issuance table, model refit, raw observations, new star data or protected-block information is emitted.\n")
    print(json.dumps({"status": result["status"], "failures": len(failures), "settings": len(settings),
                      "comparisons": len(comparisons), "output": str(args.output)}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
