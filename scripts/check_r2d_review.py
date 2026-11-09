"""Independent C61-C64 audit from retained R2b forecasts, without candidate imports."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import lognorm, norm, t as student_t, truncnorm

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 2436934.5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def distribution(anchor, issue, mu, sigma, kind, lower=None, upper=None, censor=None):
    age = issue - anchor
    a = (math.log(age) - mu) / sigma if age > 0 else -np.inf
    normalizer = norm.logsf(a)
    if kind == "interval":
        lo, hi = (math.log(lower - anchor) - mu) / sigma, (math.log(upper - anchor) - mu) / sigma
        if lo > 0:
            large, small = norm.logsf(lo), norm.logsf(hi)
        else:
            large, small = norm.logcdf(hi), norm.logcdf(lo)
        score = large + np.log(-np.expm1(small - large)) - normalizer
    else:
        lo, hi = ((math.log(censor - anchor) - mu) / sigma if censor > anchor else -np.inf), np.inf
        score = norm.logsf(lo) - normalizer
    event_mean, event_variance = truncnorm.stats(lo, hi, moments="mv")
    age_mean, age_variance = truncnorm.stats(a, np.inf, moments="mv")
    derivative = (float(event_mean) - float(age_mean)) / sigma
    information = (float(age_variance) - float(event_variance)) / sigma ** 2
    return float(score), derivative, information


def statistics(values, issues, years=6):
    values = np.asarray(values, dtype=float)
    groups = np.floor((np.asarray(issues) - ORIGIN) / (365.25 * years)).astype(int)
    keys = np.unique(groups)
    sums = np.asarray([values[groups == key].sum() for key in keys])
    counts = np.asarray([(groups == key).sum() for key in keys])
    n, g, total = len(values), len(keys), values.sum()
    centered_variance = g / (g - 1) * np.square(sums - total * counts / n).sum()
    raw_variance = g / (g - 1) * np.square(sums).sum()
    mean, se = total / n, math.sqrt(centered_variance) / n
    q = student_t.ppf(.95, g - 1)
    return dict(mean=float(mean), se=float(se), t=float(mean / se) if se else None,
                lower90=float(mean - q * se), upper90=float(mean + q * se), blocks=int(g),
                centered_score=float(total / math.sqrt(centered_variance)) if centered_variance else None,
                uncentered_score=float(total / math.sqrt(raw_variance)) if raw_variance else None,
                independent_score=float(total / math.sqrt(np.square(values).sum())))


def predict_timing(feature, timing):
    anchor, issue = feature.get("clock_anchor"), feature["issue_time"]
    if anchor is None:
        return issue, timing["remaining"][0], timing["remaining"][1], "R0"
    previous = feature.get("previous_gap")
    if previous is None or feature.get("previous_gap_covered") is not True:
        return anchor, timing["constant"][0], timing["constant"][1], "constant"
    history = [item["log_gap"] for item in feature["gap_history"]]
    if timing["rung"] == "B2":
        mu, phi, log_level, log_ar = timing["parameters"]
        n = len(history)
        indices = [i for i, value in enumerate(history) if value is not None]
        level, ar = math.exp(2 * log_level), math.exp(2 * log_ar) / (1 - phi ** 2)
        covariance = np.asarray([[1 + min(i + 1, j + 1) * level + ar * phi ** abs(i - j)
                                  for j in range(n + 1)] for i in range(n + 1)])
        loc, variance = mu, covariance[n, n]
        if indices:
            cross = covariance[n, indices]
            observed = covariance[np.ix_(indices, indices)]
            loc += cross @ np.linalg.solve(observed, np.asarray([history[i] for i in indices]) - mu)
            variance -= cross @ np.linalg.solve(observed, cross)
        return anchor, float(loc), math.sqrt(float(variance)), "B2"
    older = history[:-1]
    if timing["rung"] == "B0":
        measured = [value for value in older if value is not None]
        raw = [history[-1], float(np.mean(measured)) if measured else None]
    else:
        discount = timing["discount"]
        weighted = [(value, discount ** i) for i, value in enumerate(reversed(older)) if value is not None]
        denominator = sum(weight for _, weight in weighted)
        raw = [history[-1], older[-1] if older else None,
               sum(value * weight for value, weight in weighted) / denominator if denominator else None]
    x = [1.] + [0. if value is None else (value - transform[0]) / transform[1]
                 for value, transform in zip(raw, timing["transform"])]
    return anchor, float(np.dot(x, timing["parameters"][:-1])), math.exp(timing["parameters"][-1]), timing["rung"]


def mark(feature, marker):
    if marker in ("duration", "cadence"):
        value = feature.get("mark")
    elif marker == "rate":
        value = feature["observer_rate"]["value_per_day"]
    else:
        value = feature["flux_proxy"]["value_threshold_flux_days"]
    return float(value) if value is not None and value > 0 else None


def outcome(signature):
    if signature["kind"] == "right_censored":
        return dict(kind="right_censored", censor=signature["censor_at"])
    return dict(kind="interval", lower=signature["onset_lo"], upper=signature["onset_hi"])


def recalc(rows, shifts, marks):
    values, derivatives, information = [], [], []
    for row, shift, z in zip(rows, shifts, marks):
        base, u, j = distribution(row["anchor"], row["issue"], row["mu"] + shift,
                                   row["sigma"], **row["outcome"])
        enriched = distribution(row["anchor"], row["issue"], row["mu"] + shift + row["beta"] * z,
                                row["sigma"], **row["outcome"])[0]
        values.append((enriched - base, base))
        derivatives.append(u)
        information.append(j)
    return values, np.asarray(derivatives), np.asarray(information)


def adaptive_shifts(rows, availability=None, k=20, numerical_information=False):
    infos = np.asarray([r["finite_information"] if numerical_information else r["info"] for r in rows])
    times = np.asarray(availability if availability is not None else [r["resolved"] for r in rows])
    shifts, memberships = [], []
    for row in rows:
        selected = np.flatnonzero(times <= row["issue"])
        selected = selected[np.argsort(times[selected], kind="stable")][-k:]
        denominator = infos[selected].sum()
        shifts.append(float(sum(rows[i]["u"] for i in selected) / denominator) if len(selected) and denominator > 0 else 0.)
        memberships.append(selected.tolist())
    return np.asarray(shifts), memberships


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/r2b_real_5fb69c6")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    inputs, comparisons, failures = {}, {}, []
    max_errors = Counter()

    def load(path):
        inputs[str(path.relative_to(ROOT))] = sha(path)
        return json.loads(path.read_text())

    def compare(actual, expected, category, label, tolerance=2e-8):
        error = abs(float(actual) - float(expected))
        max_errors[category] = max(max_errors[category], error)
        if not math.isfinite(error) or error > tolerance:
            failures.append(dict(label=label, actual=actual, expected=expected, absolute_error=error))

    reference = load(ROOT / "data/provenance/r2b_claude_review/checks.json")
    receipt = load(args.run / "receipt.json")
    if receipt["status"] != "completed" or receipt["mode"] != "real":
        raise ValueError("requires completed actual retained run")
    for name, expected in receipt["output_sha256"].items():
        if sha(args.run / name) != expected:
            raise ValueError("saved R2b output differs: " + name)
    params = load(args.run / "parameters-unreleased.json")
    periods = {c: {p: load(args.run / f"{c}-{p}-features-unreleased.json")
                   for p in ("development", "evaluation")} for c in params}
    evidence = {c: {p: load(args.run / f"{c}-{p}-evidence-unreleased.json")
                    for p in ("development", "evaluation")} for c in params}
    rows_by_model, availability_checks, development = {}, {}, {}
    for clock, models in params.items():
        features = {f["emission_index"]: f for f in periods[clock]["evaluation"]}
        evidence_by_id = {e["emission_index"]: e for e in evidence[clock]["evaluation"]}
        for model, parameter in models.items():
            rows = []
            saved = load(args.run / f"{clock}-{model}-scores-unreleased.json")
            marker = model.split(".")[1]
            for item in saved:
                if item["status"] != "scored":
                    continue
                feature = features[item["emission_index"]]
                clock_data = item["base_clock"]
                signature = item["outcome_signature"]
                target = outcome(signature)
                score, u, info = distribution(clock_data["anchor"], clock_data["issue"], clock_data["mu"], clock_data["sigma"], **target)
                marked = item["marked_clock"]
                marked_score = distribution(marked["anchor"], marked["issue"], marked["mu"], marked["sigma"], **target)[0]
                compare(score, item["baseline_score"], "score", f"{clock}/{model}/base", 1e-10)
                compare(marked_score, item["marked_score"], "score", f"{clock}/{model}/marked", 1e-10)
                raw = mark(feature, marker)
                usable = item["base_route"] in ("B0", "B1", "B2") and raw is not None
                z = (math.log(raw) - parameter["mark_center"]) / parameter["mark_scale"] if usable else 0.
                h = 1e-4
                up = distribution(clock_data["anchor"], clock_data["issue"], clock_data["mu"] + h, clock_data["sigma"], **target)[1]
                down = distribution(clock_data["anchor"], clock_data["issue"], clock_data["mu"] - h, clock_data["sigma"], **target)[1]
                resolved = target["upper"] if target["kind"] == "interval" else target["censor"]
                ev = evidence_by_id[item["emission_index"]]
                row = dict(emission_index=item["emission_index"], anchor=clock_data["anchor"], issue=item["issue_time"],
                           mu=clock_data["mu"], sigma=clock_data["sigma"], outcome=target, base=score,
                           gain=marked_score - score, u=u, info=info, finite_information=-(up - down) / (2 * h),
                           z=z, has_mark=usable, beta=parameter["beta"], resolved=resolved,
                           reason=ev["reason"], signature=signature)
                rows.append(row)
                compare(info, row["finite_information"], "observed_information", f"{clock}/{model}/information", 5e-6)
            rows_by_model[(clock, model)] = rows
            issues = [r["issue"] for r in rows]
            zs, us = np.asarray([r["z"] for r in rows]), np.asarray([r["u"] for r in rows])
            contrib = zs * us
            raw = statistics([r["gain"] for r in rows], issues)
            raw_score = statistics(contrib, issues)
            information = sum(r["z"] ** 2 * r["info"] for r in rows)
            beta_eval = contrib.sum() / information
            history = [(f["issue_time"], (math.log(v) - parameter["mark_center"]) / parameter["mark_scale"])
                       for f in periods[clock]["development"] + periods[clock]["evaluation"]
                       if (v := mark(f, marker)) is not None]
            zc = []
            for row in rows:
                prior = [value for time, value in history if time < row["issue"]][-10:]
                zc.append(row["z"] - np.mean(prior) if prior and row["has_mark"] else 0.)
            shifts, membership = adaptive_shifts(rows, numerical_information=True)
            values, new_u, _ = recalc(rows, shifts, zc)
            guarded_gain = statistics([g for g, _ in values], issues)
            guarded_gain12 = statistics([g for g, _ in values], issues, 12)
            guarded_score = statistics(np.asarray(zc) * new_u, issues)
            guarded_score12 = statistics(np.asarray(zc) * new_u, issues, 12)
            grouping = np.floor((np.asarray(issues) - ORIGIN) / (6 * 365.25)).astype(int)
            means = {g: float(np.mean([r["z"] for group, r in zip(grouping, rows) if r["has_mark"] and group == g]))
                     for g in np.unique(grouping)}
            between = sum(means[g] * r["u"] for g, r in zip(grouping, rows) if r["has_mark"]) / contrib.sum()
            deff = (raw_score["independent_score"] / raw_score["centered_score"]) ** 2
            deff_guard = (guarded_score["independent_score"] / guarded_score["centered_score"]) ** 2
            predicted = beta_eval / (beta_eval - parameter["beta"] / 2)
            result = dict(scored=len(rows), mean_mark_z=float(np.mean([r["z"] for r in rows if r["has_mark"]])),
                          raw_gain=raw, raw_score=raw_score, beta_eval=float(beta_eval),
                          between_share=float(between), predicted_ratio=float(predicted),
                          observed_ratio=raw_score["centered_score"] / raw["t"], raw_deff=deff, guarded_deff=deff_guard,
                          guarded_gain=guarded_gain, guarded_gain12=guarded_gain12,
                          guarded_score=guarded_score, guarded_score12=guarded_score12)
            ref = reference["contrasts"][clock + ":" + model]
            for key, value in [("mean_mark_z_evaluation",result["mean_mark_z"]),
                               ("between_block_share_of_statistic",between),
                               ("evaluation_one_step_beta",beta_eval),
                               ("predicted_score_to_gain_ratio",predicted),
                               ("design_effect_centred_six_raw",deff),
                               ("design_effect_centred_six_guarded",deff_guard)]:
                if key in ref:
                    compare(value,ref[key],"review_aggregates",clock+":"+model+":"+key,5e-6)
            for actual,key in [(guarded_gain["mean"],"gain_six"),(guarded_gain12["mean"],"gain_twelve")]:
                compare(actual,ref["drift_guarded"][key]["mean"],"guarded_gain",clock+":"+model+":"+key,1e-8)
            for value,key in [(guarded_score["centered_score"],"score_centred_six"),
                              (guarded_score12["centered_score"],"score_centred_twelve")]:
                compare(value,ref["drift_guarded"][key],"guarded_score",clock+":"+model+":"+key,5e-6)
            for value,key in [(guarded_gain["t"],"gain_six"),(guarded_gain12["t"],"gain_twelve")]:
                compare(value,ref["drift_guarded"][key]["t"],"guarded_t",clock+":"+model+":"+key,5e-6)
            comparisons[clock+":"+model] = result
            closure = [r["resolved"] + (.15 if r["outcome"]["kind"] == "interval" else 7. if r["reason"].startswith("coverage:") else 0.) for r in rows]
            delayed, membership_delayed = adaptive_shifts(rows, closure, numerical_information=True)
            delayed_values, delayed_u, _ = recalc(rows, delayed, zc)
            availability_checks[clock+":"+model] = dict(
                update_sets_changed=sum(a != b for a,b in zip(membership,membership_delayed)),
                maximum_location_shift_difference=float(np.max(np.abs(shifts-delayed))),
                closure_delayed_gain=statistics([g for g,_ in delayed_values],issues),
                qualification="0.15d added conservatively to every interval; coverage censor recognized after seven days; not a reconstructed full outcome-availability ledger")
    eras = {}
    for clock in ("df", "point_at_df"):
        for period, feats in periods[clock].items():
            groups = {}
            for f in feats:
                if f.get("previous_gap") is not None and f.get("previous_gap_covered") is True:
                    key=math.floor((f["issue_time"]-ORIGIN)/(12*365.25))
                    groups.setdefault(key,[]).append(math.log(f["previous_gap"]))
            eras[clock+":"+period] = {str(k):dict(n=len(v),geometric_mean_gap=math.exp(float(np.mean(v)))) for k,v in groups.items()}
            for row in reference["era_levels_twelve_year"][clock+":"+period]["blocks"]:
                compare(eras[clock+":"+period][str(row['block'])]["geometric_mean_gap"],row["geometric_mean_gap_days"],"era_gap",clock+":"+period,1e-10)
    for clock in params:
        feats=periods[clock]["development"]
        evs={e['emission_index']:e for e in evidence[clock]['development']}
        for rung in ("B0","B1","B2"):
            parameter=params[clock][rung+'.duration']; rows=[]
            for f in feats:
                ev=evs[f['emission_index']]
                if ev['kind']=='excluded' or f.get('clock_anchor') is None:continue
                anchor,mu,sigma,route=predict_timing(f,parameter['timing'])
                if route!=rung:continue
                target=dict(kind='interval',lower=ev['onset_lo'],upper=ev['onset_hi']) if ev['kind']=='interval' else dict(kind='right_censored',censor=ev['censor_at'])
                score,u,info=distribution(anchor,f['issue_time'],mu,sigma,**target)
                h=1e-4
                ip=distribution(anchor,f['issue_time'],mu+h,sigma,**target)[1]
                im=distribution(anchor,f['issue_time'],mu-h,sigma,**target)[1]
                rows.append(dict(anchor=anchor,issue=f['issue_time'],mu=mu,sigma=sigma,outcome=target,u=u,info=info,finite_information=-(ip-im)/(2*h),resolved=target.get('upper',target.get('censor')),beta=0.))
            shifts,_=adaptive_shifts(rows,numerical_information=True)
            before=-sum(distribution(r['anchor'],r['issue'],r['mu'],r['sigma'],**r['outcome'])[0] for r in rows)
            after=-sum(distribution(r['anchor'],r['issue'],r['mu']+shift,r['sigma'],**r['outcome'])[0] for r,shift in zip(rows,shifts))
            key=clock+':'+rung;development[key]=dict(timing_rows=len(rows),nll=before,recalibrated_nll=after)
            compare(before,reference['development'][key]['nll'],'development_nll',key,1e-8)
            compare(after,reference['development'][key]['nll_causal_recalibrated_k20'],'development_recalibration',key,1e-5)
    duration=[v for k,v in comparisons.items() if k.endswith('.duration')]
    summary=dict(scope="independent scalar truncated-normal moment and joint Gaussian covariance audit; no candidate/Claude imports or new fits",status="failed" if failures else "passed",failures=failures,maximum_absolute_errors=dict(max_errors),models_checked=len(comparisons),comparisons=comparisons,era_levels=eras,development=development,availability_sensitivity=availability_checks,
                 efficiency_ranges=dict(predicted_ratio=[min(v['predicted_ratio'] for v in duration),max(v['predicted_ratio'] for v in duration)],max_ratio_discrepancy=max(abs(v['predicted_ratio']-v['observed_ratio']) for v in duration),raw_deff=[min(v['raw_deff'] for v in duration),max(v['raw_deff'] for v in duration)],guarded_deff=[min(v['guarded_deff'] for v in duration),max(v['guarded_deff'] for v in duration)]),input_sha256=inputs,checker_sha256=sha(__file__),limits=["Post-result diagnostics; no C01 decomposition was performed.","Closure-delay sensitivity does not reconstruct candidate confirmation/association availability.","Score test targets a working coefficient moment; it is not the finite development-fitted forecast-gain null.","Score/gain ratio agreement uses the same evaluation score and curvature and is a Taylor-identity check, not independent power validation."])
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(dict(status=summary['status'],models_checked=summary['models_checked'],maximum_absolute_errors=summary['maximum_absolute_errors'],failures=failures)))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
