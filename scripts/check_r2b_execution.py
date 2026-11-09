"""Independent R2b audit: direct Gaussian conditioning, no dnmem imports."""

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

import numpy as np
from scipy.stats import lognorm, t as student_t

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-9
ORIGIN = date(1960, 1, 1).toordinal() + 1721424.5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-real", action="store_true")
    args = parser.parse_args()
    run, out = args.run.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    failures, inputs, errors = [], {}, Counter()
    counts, routes, training_kinds = Counter(), Counter(), Counter()

    def require(ok, message):
        if not ok:
            failures.append(message)

    def compare(actual, expected, label, category):
        if actual is None or expected is None:
            require(actual is None and expected is None, label + ": missingness differs")
        else:
            error = abs(float(actual) - float(expected))
            errors[category] = max(errors[category], error)
            require(math.isfinite(error) and error <= TOL, label + ": numerical difference " + str(error))
            counts[category + "_checks"] += 1

    def read(path):
        raw = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    def indexed(rows, label):
        result = {row["emission_index"]: row for row in rows}
        require(len(result) == len(rows), label + ": duplicate IDs")
        return result

    def previous(row):
        return (row.get("previous_gap_covered") is True and row.get("previous_gap") is not None
                and math.isfinite(row["previous_gap"]) and row["previous_gap"] > 0)

    def history(row):
        require(math.isfinite(row["available_at"]) and row["available_at"] <= row["issue_time"], "future/nonfinite feature")
        values = []
        for item in row["gap_history"]:
            require(math.isfinite(item["available_at"]) and item["available_at"] <= row["issue_time"], "future/nonfinite history")
            value = item["log_gap"]
            require(value is None or math.isfinite(value), "nonfinite gap")
            values.append(value)
        if previous(row):
            require(bool(values) and values[-1] is not None, "usable previous gap lacks history")
            if values and values[-1] is not None:
                compare(math.log(row["previous_gap"]), values[-1], "previous gap identity", "feature")
        else:
            require(not values or values[-1] is None, "missing previous gap has measured final slot")
        return values

    def raw_covariates(row, rung, discount):
        values = history(row)
        older = values[:-1]
        if rung == "B0":
            valid = [value for value in older if value is not None]
            return [values[-1], statistics.fmean(valid) if valid else None]
        weighted = [(value, discount ** lag) for lag, value in enumerate(reversed(older)) if value is not None]
        total = math.fsum(weight for _, weight in weighted)
        return [values[-1], older[-1] if older else None,
                math.fsum(value * weight for value, weight in weighted) / total if total else None]

    def standard(values):
        if not values:
            return [0., 1., True]
        center, sd = statistics.fmean(values), statistics.pstdev(values)
        return [center, 1. if sd <= 1e-10 else sd, sd <= 1e-10]

    def transform(rows, rung, discount):
        raw = [raw_covariates(row, rung, discount) for row in rows]
        return [standard([item[j] for item in raw if item[j] is not None]) for j in range(len(raw[0]))]

    def covariance_prediction(values, theta):
        mu, phi, log_level, log_ar = theta
        level_var, ar_var = math.exp(2 * log_level), math.exp(2 * log_ar)
        def covariance(i, j):
            return 1. + min(i, j) * level_var + ar_var * phi ** abs(i - j) / (1 - phi ** 2)
        observed = [i + 1 for i, value in enumerate(values) if value is not None]
        target = len(values) + 1
        if not observed:
            return mu, math.sqrt(covariance(target, target))
        matrix = np.array([[covariance(i, j) for j in observed] for i in observed])
        cross = np.array([covariance(target, i) for i in observed])
        residual = np.array([values[i - 1] - mu for i in observed])
        weights = np.linalg.solve(matrix, cross)
        prediction = mu + float(weights @ residual)
        variance = covariance(target, target) - float(cross @ weights)
        if variance <= 0:
            raise ValueError("nonpositive independent Gaussian variance")
        return prediction, math.sqrt(variance)

    def cadence(row):
        record = row.get("cadence_end", {})
        value = record.get("value_days")
        if value is not None:
            require(math.isfinite(value) and value >= 0 and math.isfinite(record["available_at"])
                    and record["available_at"] <= row["issue_time"], "future/invalid cadence")
        return value

    def mark(row, marker):
        if marker == "duration":
            value, available = row.get("mark"), row["available_at"]
        elif marker == "rate":
            value, available = row["observer_rate"]["value_per_day"], row["observer_rate"]["available_at"]
        else:
            value, available = row["flux_proxy"]["value_threshold_flux_days"], row["flux_proxy"]["available_at"]
        if value is not None:
            require(math.isfinite(value) and math.isfinite(available) and available <= row["issue_time"], "future/invalid mark")
        return value if value is not None and value > 0 else None

    def prediction(row, model, enriched=False):
        timing = model["timing"]
        values = history(row)
        issue, anchor = row["issue_time"], row["clock_anchor"]
        if anchor is None:
            return (issue, issue, *timing["remaining"]), "R0"
        require(anchor <= issue, "anchor after issue")
        if not previous(row):
            return (anchor, issue, *timing["constant"]), "constant"
        rung, theta = timing["rung"], timing["parameters"]
        if rung == "B2":
            location, sigma = covariance_prediction(values, theta)
        else:
            raw = raw_covariates(row, rung, timing["discount"])
            z = [0. if value is None else (value - center) / scale
                 for value, (center, scale, _) in zip(raw, timing["transform"])]
            location = theta[0] + math.fsum(a * b for a, b in zip(theta[1:-1], z))
            sigma = math.exp(theta[-1])
        if model["cadence_transform"] is not None:
            value = cadence(row)
            center, scale, _ = model["cadence_transform"]
            location += model["cadence_beta"] * ((value - center) / scale if value is not None else 0.)
        route = rung
        value = mark(row, model["marker"]) if enriched and model["beta"] != 0 else None
        if value is not None:
            location += model["beta"] * (math.log(value) - model["mark_center"]) / model["mark_scale"]
            route += "+" + model["marker"]
        return (anchor, issue, location, sigma), route

    def score(clock, ev):
        anchor, issue, mu, sigma = clock
        kwargs = dict(s=sigma, scale=math.exp(mu))
        denominator = float(lognorm.logsf(issue - anchor, **kwargs))
        if ev["kind"] == "interval":
            lo, hi = ev["onset_lo"] - anchor, ev["onset_hi"] - anchor
            if math.log(lo) >= mu:
                mass = float(lognorm.sf(lo, **kwargs) - lognorm.sf(hi, **kwargs))
            else:
                mass = float(lognorm.cdf(hi, **kwargs) - lognorm.cdf(lo, **kwargs))
            if not mass > 0:
                raise ValueError("independent interval probability unresolved")
            numerator = math.log(mass)
        elif ev["kind"] == "right_censored":
            numerator = float(lognorm.logsf(ev["censor_at"] - anchor, **kwargs))
        elif ev["kind"] == "point":
            numerator = float(lognorm.logpdf(ev["onset_t"] - anchor, **kwargs))
        else:
            raise ValueError("unsupported independent score")
        answer = numerator - denominator
        require(math.isfinite(answer), "nonfinite independent score")
        return answer

    def mixed_bounds(base, marked, ev):
        def survival(cutoff):
            outcome = dict(kind="right_censored", censor_at=cutoff)
            return score(marked, outcome) - score(base, outcome)
        lo, hi, cutoff = ev.get("onset_lo"), ev.get("onset_hi"), ev["fixed_cutoff"]
        if lo is None or hi is None or lo >= cutoff:
            value = survival(cutoff)
            return value, value
        end = min(hi, cutoff)
        times = [lo, end]
        inv_b, inv_m = 1 / base[3] ** 2, 1 / marked[3] ** 2
        quadratic = .5 * (inv_b - inv_m)
        if quadratic:
            vertex = -(marked[2] * inv_m - base[2] * inv_b) / (2 * quadratic)
            if math.log(lo - base[0]) < vertex < math.log(end - base[0]):
                times.append(base[0] + math.exp(vertex))
        values = [score(marked, dict(kind="point", onset_t=time)) - score(base, dict(kind="point", onset_t=time)) for time in times]
        if hi > cutoff:
            values.append(survival(cutoff))
        return min(values), max(values)

    def acf(values, maximum):
        available = [value for value in values if value is not None]
        center = statistics.fmean(available) if available else None
        denominator = math.fsum((value - center) ** 2 for value in available) if available else 0.
        rows = []
        for lag in range(1, maximum + 1):
            pairs = [(values[i], values[i + lag]) for i in range(max(0, len(values) - lag))
                     if values[i] is not None and values[i + lag] is not None]
            rows.append(dict(lag=lag, pairs=len(pairs), acf=math.fsum((a - center) * (b - center) for a, b in pairs) / denominator if denominator and pairs else None))
        return rows

    def calendar(rows, field, years):
        groups = {}
        for row in rows:
            if row.get(field) is not None:
                key = math.floor((row["issue_time"] - ORIGIN) / (years * 365.25))
                groups.setdefault(key, []).append(row[field])
        values = [value for group in groups.values() for value in group]
        n, g = len(values), len(groups)
        estimate = statistics.fmean(values) if values else None
        result = dict(n=n, issued=len(rows), missing=len(rows) - n, blocks=g, df=g - 1 if g else None,
                      estimate=estimate, se=None, lower=None, upper=None,
                      block_means=[dict(block=k, n=len(v), weight=float(len(v)), mean=statistics.fmean(v)) for k, v in sorted(groups.items())])
        if g >= 2:
            se = math.sqrt(g / (g - 1) * math.fsum(math.fsum(value - estimate for value in group) ** 2 for group in groups.values()) / n ** 2)
            radius = float(student_t.ppf(.95, g - 1)) * se
            result.update(se=se, lower=estimate - radius, upper=estimate + radius)
        return result

    def check_aggregate(rows, saved, field, label):
        for years, name in [(6, "six_year"), (12, "twelve_year")]:
            expected, actual = calendar(rows, field, years), saved[name]
            for key in ("n", "issued", "missing", "blocks", "df"):
                require(actual[key] == expected[key], label + ": cluster count " + key)
            for key in ("estimate", "se", "lower", "upper"):
                compare(actual[key], expected[key], label + ": " + key, "aggregate")
            require([r["block"] for r in actual["block_means"]] == [r["block"] for r in expected["block_means"]], label + ": block IDs")
            for a, b in zip(actual["block_means"], expected["block_means"]):
                require(a["n"] == b["n"], label + ": block population")
                compare(a["mean"], b["mean"], label + ": block mean", "aggregate")
        for a, b in zip(saved["forecast_acf"]["lags"], acf([row.get(field) for row in rows], 10)):
            require(a["pairs"] == b["pairs"], label + ": ACF pair count")
            compare(a["acf"], b["acf"], label + ": ACF", "aggregate")

    def check_summary(rows, saved, label):
        for field, key in [("gain", "working"), ("known_contrast", "algebraically_known_contrasts"), ("point_gain", "point_sensitivity")]:
            check_aggregate(rows, saved[key], field, label + ":" + field)
        bounded = [r for r in rows if r["bounds_lower"] is not None]
        require(saved["deterministic_bounds"]["n"] == len(bounded), label + ": bounds population")
        for key, field in [("lower_mean", "bounds_lower"), ("upper_mean", "bounds_upper")]:
            compare(saved["deterministic_bounds"][key], statistics.fmean(r[field] for r in bounded) if bounded else None, label + ": " + key, "aggregate")
        for field, key, default in [("base_route", "base_routes", "paired"),
                                     ("marked_route", "marked_routes", "paired"),
                                     ("reason", "reasons", "paired")]:
            require(saved[key] == dict(Counter(row.get(field, default) for row in rows)), label + ": " + key)
        require(saved["supported_identities"] == sum(row.get("identical_forecasts", False) and row["gain"] is not None for row in rows), label + ": supported identity count")
        require(saved["unsupported_identities"] == sum(row.get("identical_forecasts", False) and row["gain"] is None for row in rows), label + ": unsupported identity count")

    report = {}
    try:
        receipt = read(run / "receipt.json")
        if receipt["mode"] == "real" and not args.allow_real:
            raise ValueError("real run requires explicit --allow-real after its path is authorized")
        require(receipt["status"] == "completed", "run did not complete")
        for name, expected in receipt["output_sha256"].items():
            require(hashlib.sha256((run / name).read_bytes()).hexdigest() == expected, "output receipt hash: " + name)
        for name, expected in receipt["source_sha256"].items():
            raw = subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":" + name], cwd=ROOT)
            require(hashlib.sha256(raw).hexdigest() == expected, "historical source hash: " + name)
        models, summary = read(run / "parameters-unreleased.json"), read(run / "summary.json")
        parameter_hash = hashlib.sha256((run / "parameters-unreleased.json").read_bytes()).hexdigest()
        require(parameter_hash == receipt["parameters_sha256"] == summary["parameters_sha256"], "parameter lock hash differs")
        config = json.loads(subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":configs/r2b_execution.json"], cwd=ROOT))
        require(config["training_stop"] == ORIGIN and config["evaluation_stop"] == date(2018, 1, 1).toordinal() + 1721424.5, "period differs")
        expected_scores = {}
        for clock, own in models.items():
            features, evidence = {}, {}
            for period in ("development", "evaluation"):
                features[period] = read(run / f"{clock}-{period}-features-unreleased.json")
                evidence[period] = read(run / f"{clock}-{period}-evidence-unreleased.json")
                require(indexed(features[period], clock).keys() == indexed(evidence[period], clock).keys(), "feature/evidence population differs")
                for row in features[period]:
                    history(row)
                    lo = config["training_start"] if period == "development" else config["training_stop"]
                    hi = config["training_stop"] if period == "development" else config["evaluation_stop"]
                    require(lo <= row["issue_time"] < hi, "feature outside declared period")
                for ev in evidence[period]:
                    cutoff = config["training_stop"] if period == "development" else config["evaluation_stop"]
                    require(ev["computed_as_of"] <= cutoff and ev["evidence_available_at"] <= cutoff, "future evidence")
                    for key in ("onset_hi", "onset_t", "censor_at"):
                        require(ev.get(key) is None or ev[key] <= cutoff, "future outcome support")
                    support = ev.get("onset_hi") if ev["kind"] == "interval" else ev.get("censor_at") if ev["kind"] == "right_censored" else None
                    require(support is None or support <= min(ev["computed_as_of"], ev["evidence_available_at"]), "outcome precedes declared availability")
                require(summary["populations"][clock][period]["issues"] == len(features[period]), "summary issue count")
                require(summary["populations"][clock][period]["outcomes"] == dict(Counter(ev["kind"] for ev in evidence[period])), "summary outcome counts")
            training_by_id = indexed(features["development"], clock)
            pairs = [(training_by_id[ev["emission_index"]], ev) for ev in evidence["development"] if ev["kind"] != "excluded"]
            anchored = [(r, e) for r, e in pairs if r["clock_anchor"] is not None]
            timed = [(r, e) for r, e in anchored if previous(r)]
            eval_by_id = indexed(features["evaluation"], clock)
            for name, model in own.items():
                label = clock + ":" + name
                timing, meta = model["timing"], model["metadata"]
                rung = timing["rung"]
                require(meta["training_cutoff"] == config["training_stop"] and meta["training_rows"] == len(pairs) and meta["timing_rows"] == len(timed), label + ": training metadata")
                require(timing["beta"] == 0., label + ": nested TimingRule unexpectedly marked")
                if rung != "B2":
                    expected_transform = transform([r for r, _ in timed], rung, timing["discount"])
                    for a, b in zip(timing["transform"], expected_transform):
                        compare(a[0], b[0], label + ": transform center", "transform")
                        compare(a[1], b[1], label + ": transform scale", "transform")
                        require(a[2] == b[2], label + ": transform fixed flag")
                if model["cadence_transform"] is not None:
                    expected = standard([cadence(r) for r, _ in timed if cadence(r) is not None])
                    for a, b in zip(model["cadence_transform"][:2], expected[:2]):
                        compare(a, b, label + ": cadence transform", "transform")
                    require(model["cadence_transform"][2] == expected[2], label + ": cadence fixed flag")
                marked = [(r, e) for r, e in timed if mark(r, model["marker"]) is not None]
                expected = standard([math.log(mark(r, model["marker"])) for r, _ in marked])
                compare(model["mark_center"], expected[0], label + ": mark center", "transform")
                compare(model["mark_scale"], expected[1], label + ": mark scale", "transform")
                for key, group, remaining in [("remaining_fit", pairs, True), ("constant_fit", anchored, False)]:
                    obj = -math.fsum(score((r["issue_time"] if remaining else r["clock_anchor"], r["issue_time"], *timing["remaining" if remaining else "constant"]), e) for r, e in group)
                    compare(meta[key]["objective"], obj, label + ": " + key, "objective")
                    training_kinds.update(e["kind"] for _, e in group)
                total = -math.fsum(score(prediction(r, model)[0], e) for r, e in timed)
                compare(meta["base_fit"]["objective"], total, label + ": base objective", "objective")
                training_kinds.update(e["kind"] for _, e in timed)
                if meta["offset_fit"]["status"] == "optimized":
                    plain = -math.fsum(score(prediction(r, model)[0], e) for r, e in marked)
                    enriched = -math.fsum(score(prediction(r, model, True)[0], e) for r, e in marked)
                    compare(meta["offset_fit"]["objective"], enriched, label + ": offset objective", "objective")
                    compare(meta["offset_fit"]["zero_objective"], plain, label + ": zero objective", "objective")
                    training_kinds.update(e["kind"] for _, e in marked for _ in range(2))
                attempts = meta["base_fit"]["attempts"]
                good = [a for a in attempts if a["successful"]]
                spread = max(a["objective"] for a in good) - min(a["objective"] for a in good)
                require(meta["base_fit"]["stable"] == (len(good) == len(attempts) and len(good) >= 2 and spread <= meta["base_fit"]["stability_tolerance"]), label + ": stability status")
                for flagged in (False, True):
                    suffix = "flagged-scores" if flagged else "scores"
                    saved = read(run / f"{clock}-{name}-{suffix}-unreleased.json")
                    require(indexed(saved, label).keys() == eval_by_id.keys(), label + ": score population")
                    expected = []
                    for actual in saved:
                        row = eval_by_id[actual["emission_index"]]
                        ev = actual["outcome_signature"]
                        require(actual["issue_time"] == row["issue_time"] == ev["issue_time"], label + ": issue mismatch")
                        if not flagged:
                            original_ev = indexed(evidence["evaluation"], clock)[actual["emission_index"]]
                            require(all(original_ev.get(k) == v for k, v in ev.items()), label + ": saved outcome signature")
                        base, base_route = prediction(row, model)
                        enriched, mark_route = prediction(row, model, True)
                        for prefix, value in [("base", base), ("marked", enriched)]:
                            for k, v in zip(("anchor", "issue", "mu", "sigma"), value):
                                compare(actual[prefix + "_clock"][k], v, label + ": clock " + k, "prediction")
                        require(actual["base_route"] == base_route and actual["marked_route"] == mark_route, label + ": route mismatch")
                        identity = base == enriched
                        require(actual["identical_forecasts"] == identity, label + ": identity mismatch")
                        routes[clock + ":" + mark_route] += 1
                        counts["zero_counterfactuals"] += 1
                        require(prediction(row, {**model, "beta": 0.}, True) == prediction(row, {**model, "beta": 0.}, False), label + ": zero nesting")
                        result = dict(issue_time=row["issue_time"], emission_index=row["emission_index"], gain=None,
                                      known_contrast=0. if identity else None, bounds_lower=None, bounds_upper=None,
                                      point_gain=None, outcome_signature=ev, identical_forecasts=identity,
                                      base_route=base_route, marked_route=mark_route, reason=ev["reason"],
                                      status="excluded", point_status="unavailable")
                        if ev["kind"] != "excluded":
                            if ev["kind"] == "interval":
                                require(ev["onset_hi"] <= ev["fixed_cutoff"] and row["issue_time"] < ev["onset_lo"], label + ": interval routing")
                            elif ev.get("onset_hi") is not None:
                                expected_censor = ev["onset_lo"] if ev["onset_lo"] < ev["fixed_cutoff"] < ev["onset_hi"] else ev["fixed_cutoff"]
                                require(ev["censor_at"] == expected_censor, label + ": censor routing")
                            plain, augmented = score(base, ev), score(enriched, ev)
                            lo, hi = mixed_bounds(base, enriched, ev)
                            result.update(gain=augmented - plain, known_contrast=augmented - plain, bounds_lower=lo, bounds_upper=hi, status="scored")
                            compare(actual["baseline_score"], plain, label + ": base score", "score")
                            compare(actual["marked_score"], augmented, label + ": marked score", "score")
                            if row.get("clock") != "point":
                                result["point_status"] = "not_a_point_clock_sensitivity"
                            else:
                                if ev["kind"] == "right_censored":
                                    result["point_gain"] = result["gain"]
                                    result["point_status"] = "same_working_censor_survival"
                                elif ev.get("onset_t") is not None and base[1] < ev["onset_t"] <= ev["fixed_cutoff"]:
                                    point = dict(kind="point", onset_t=ev["onset_t"])
                                    result["point_gain"] = score(enriched, point) - score(base, point)
                                    result["point_status"] = "saved_X4_point_density"
                                else:
                                    result["point_status"] = "saved_X4_point_missing_or_outside_issue_cutoff"
                        require(actual["status"] == result["status"] and actual["reason"] == result["reason"]
                                and actual["point_status"] == result["point_status"], label + ": score status/reason")
                        for key in ("gain", "known_contrast", "bounds_lower", "bounds_upper", "point_gain"):
                            compare(actual[key], result[key], label + ": " + key, "bound" if key.startswith("bounds") else "contrast")
                        if identity:
                            require(actual["known_contrast"] == 0., label + ": saved exact identity")
                            counts["saved_exact_identities"] += 1
                        expected.append(result)
                    saved_summary = summary["comparisons"][clock][name]
                    check_summary(expected, saved_summary["including_flagged_windows"] if flagged else saved_summary, label + (":flagged" if flagged else ""))
                    if not flagged:
                        expected_scores[(clock, name)] = expected
        check_summary(expected_scores[("point_original", "B2.duration")], summary["headline"]["H1"], "H1")
        check_summary(expected_scores[("df", "B2.duration")], summary["headline"]["H2"], "H2")
        left = indexed(expected_scores[("df", "B2.duration")], "DF")
        right = indexed(expected_scores[("point_at_df", "B2.duration")], "point match")
        require(left.keys() == right.keys(), "H3 populations differ")
        saved_pair = read(run / "H3-paired-scores-unreleased.json")
        pair = []
        for actual in saved_pair:
            a, b = left[actual["emission_index"]], right[actual["emission_index"]]
            require(a["outcome_signature"] == b["outcome_signature"], "H3 outcomes differ")
            result = dict(issue_time=a["issue_time"], point_gain=None,
                          status="scored" if a["gain"] is not None and b["gain"] is not None else "excluded")
            for field in ("gain", "known_contrast"):
                result[field] = a[field] - b[field] if a[field] is not None and b[field] is not None else None
            result["bounds_lower"] = a["bounds_lower"] - b["bounds_upper"] if a["bounds_lower"] is not None and b["bounds_upper"] is not None else None
            result["bounds_upper"] = a["bounds_upper"] - b["bounds_lower"] if a["bounds_upper"] is not None and b["bounds_lower"] is not None else None
            for key in ("gain", "known_contrast", "bounds_lower", "bounds_upper"):
                compare(actual[key], result[key], "H3 " + key, "H3")
            pair.append(result)
        check_summary(pair, summary["headline"]["H3"], "H3")
        counts["models_checked"] = sum(map(len, models.values()))
        counts["H3_rows"] = len(pair)
        report.update(mode=receipt["mode"], source_freeze=receipt["freeze_commit"], parameters_sha256=parameter_hash,
                      parameter_file_mtime_before_score_files=all((run / "parameters-unreleased.json").stat().st_mtime <= p.stat().st_mtime for p in run.glob("*-scores-unreleased.json")))
    except Exception as exc:
        failures.append(type(exc).__name__ + ": " + str(exc))
    for name, expected in inputs.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "inspected input changed: " + name)
    report.update(status="failed" if failures else "passed", absolute_tolerance=TOL, counts=dict(counts),
                  maximum_absolute_errors=dict(errors), routing_counts=dict(routes), training_score_terms_by_kind=dict(training_kinds),
                  failures=failures, input_sha256=inputs, checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  derivation="direct joint Gaussian covariance; independent covariates/cadence/marks; SciPy lognormal scores; scalar mixed extrema; CR1/t",
                  limits=["No candidate functions imported, optimizer run, new simulation or raw archive accessed.",
                          "Saved feature/evidence association is checked for consistency, not independently re-extracted from photometry.",
                          "Numerical agreement does not certify optimizer global optimality, calibration, CAR or latent containment.",
                          "Parameter hash and frozen execution order agree; final receipt alone is not an independent historical timestamp of its intermediate stage.",
                          "Filesystem mtime is descriptive provenance only; copies can change it."])
    (out / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    (out / "report.md").write_text("# Independent R2b execution audit\n\n" + json.dumps({k: report[k] for k in ("status", "absolute_tolerance", "counts", "maximum_absolute_errors", "failures")}, indent=2) + "\n\nNo candidate functions imported. Direct Gaussian conditioning replaces the state recursion. See summary.json for hashes and limits.\n")
    print(json.dumps({k: report[k] for k in ("status", "counts", "maximum_absolute_errors", "failures")}))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
