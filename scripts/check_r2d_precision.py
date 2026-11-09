"""Independent saved-trial aggregation and representative vector audit for R2d."""

import argparse
from collections import Counter
import difflib
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.stats import binom, norm, t as student_t

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_interval(k, n):
    if not n:
        return None
    lower = brentq(lambda p: binom.sf(k - 1, n, p) - .025, 0., 1., xtol=1e-14) if k else 0.
    upper = brentq(lambda p: binom.cdf(k, n, p) - .025, 0., 1., xtol=1e-14) if k < n else 1.
    return [float(lower), float(upper)]


@lru_cache(maxsize=None)
def _weights_cached(counts):
    counts = np.asarray(counts, dtype=float)
    if len(counts) < 3 or np.any(counts <= 0):
        raise ValueError("infeasible normalized forty-percent cap")
    scale = brentq(lambda k: np.minimum(.4, k * counts).sum() - 1., 0., 1. / counts.min(), xtol=1e-15)
    return np.minimum(.4, scale * counts)


def weights(counts):
    return _weights_cached(tuple(float(n) for n in counts))


def interval(values, stars, epochs, clustering):
    groups, row_weights = {}, np.zeros(len(values))
    counts = [sum(stars == s) for s in range(int(stars.max()) + 1)]
    capped = weights(counts)
    for i, (value, star, epoch) in enumerate(zip(values, stars, epochs)):
        row_weights[i] = capped[star] / counts[star]
        key = (int(star), int(epoch >= 3)) if clustering == "halves" else int(star)
        groups.setdefault(key, []).append(i)
    mean = float(sum(float(value) * weight for value, weight in zip(values, row_weights)))
    totals = [sum(row_weights[i] * (values[i] - mean) for i in indices) for indices in groups.values()]
    g = len(groups)
    se = math.sqrt(g / (g - 1) * sum(total * total for total in totals))
    critical = float(student_t.ppf(.95, g - 1))
    return dict(estimate=mean, se=se, lower90=mean - critical * se, upper90=mean + critical * se,
                statistic=mean / se if se else None, reject_one_sided=bool(mean > critical * se),
                clusters=g, df=g - 1, maximum_star_weight=float(capped.max()))


def reconstruct_star(history, case):
    y, issue, available, mark = [np.asarray(history[key], dtype=float) for key in
                                 ("y", "issue", "outcome_available_at", "mark")]
    n, ndev = len(y), int(history["development_n"])
    raw = np.full((n, 2), np.nan)
    for i in range(n):
        if i and available[i - 1] <= issue[i]:
            raw[i, 0] = y[i - 1]
        older = [y[j] for j in range(max(0, i - 6), i - 1) if available[j] <= issue[i]]
        if older:
            raw[i, 1] = np.mean(older)
    train = (np.arange(n) < ndev) & (available <= issue[ndev])
    timed = train & np.isfinite(raw[:, 0])
    transform = []
    for j in range(2):
        column = raw[timed, j]; column = column[np.isfinite(column)]
        center = float(column.mean()) if len(column) else 0.
        scale = float(column.std()) if len(column) else 1.
        transform.append((center, scale if scale > 1e-10 else 1.))
    x = np.column_stack([np.ones(n)] + [np.where(np.isfinite(raw[:, j]), (raw[:, j] - m) / sd, 0.)
                                      for j, (m, sd) in enumerate(transform)])
    beta = np.linalg.lstsq(x[timed], y[timed], rcond=None)[0]
    raw_mean = np.where(np.isfinite(raw[:, 0]), x @ beta, y[train].mean())
    variance = min(4., max(.0009, float(np.mean((y[timed] - raw_mean[timed]) ** 2))))
    if case.get("oracle_base", False):
        raw_mean = np.asarray(history["true_mean_without_direct_mark"], dtype=float)
        variances = np.asarray(history["innovation_variance"], dtype=float)
    else:
        variances = np.full(n, variance)
    correction = np.zeros(n)
    for i in range(n):
        prior = [j for j in range(i) if available[j] <= issue[i]][-int(case.get("level_window", 20)):]
        if prior and case.get("recalibrate", True) and not case.get("oracle_base", False):
            correction[i] = float(np.mean(y[prior] - raw_mean[prior]))
    observed_training = mark[:ndev][np.isfinite(mark[:ndev])]
    center = float(observed_training.mean()) if len(observed_training) else 0.
    scale = float(observed_training.std()) if len(observed_training) else 1.
    fixed = len(observed_training) < 2 or scale <= 1e-10
    if fixed:
        scale = 1.
    normalized = (mark - center) / scale
    z, usable = np.zeros(n), np.zeros(n, dtype=bool)
    for i in range(n):
        prior = [j for j in range(i) if np.isfinite(mark[j])][-int(case.get("mark_window", 10)):]
        valid = np.isfinite(mark[i]) and not fixed and np.isfinite(raw[i, 0])
        if case.get("guard_marks", True):
            valid = valid and len(prior) >= int(case.get("minimum_marks", 3))
        if valid:
            z[i] = normalized[i] - float(np.mean(normalized[prior])) if case.get("guard_marks", True) else normalized[i]
            usable[i] = True
    return dict(history=history, raw_mean=raw_mean, baseline_mean=raw_mean + correction,
                variance=variances, z=z, mark_usable=usable, training=train, timed_training=timed,
                level_shift=correction, coefficient=beta, transforms=transform,
                mark_center=center, mark_scale=scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/r2d_precision_67c45ab")
    parser.add_argument("--vectors", type=Path, default=ROOT / "outputs/r2d_precision_vector_audit")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wait-seconds", type=float, default=1800.)
    args = parser.parse_args()
    deadline = time.monotonic() + args.wait_seconds
    while not (args.run / "receipt.json").exists() or not (args.run / "summary.json").exists():
        if time.monotonic() >= deadline:
            raise TimeoutError("precision run is unfinished; no audit output created")
        time.sleep(5.)
    args.output.mkdir(parents=True, exist_ok=False)
    failures, counts, errors, input_hashes = [], Counter(), Counter(), {}

    def require(ok, label):
        counts["logical_checks"] += 1
        if not ok:
            failures.append(label)

    def equal(actual, expected, label, category="aggregate", tolerance=1e-10):
        if isinstance(actual, (list, tuple)) or isinstance(expected, (list, tuple)):
            require(len(actual) == len(expected), label + ": length")
            for i, (a, b) in enumerate(zip(actual, expected)):
                equal(a, b, label + f"[{i}]", category, tolerance)
        elif actual is None or expected is None:
            require(actual is None and expected is None, label + ": missingness")
        elif isinstance(actual, (bool, str)) or isinstance(expected, (bool, str)):
            require(actual == expected, label + ": identity")
        else:
            error = abs(float(actual) - float(expected)); errors[category] = max(errors[category], error)
            require(math.isfinite(error) and error <= tolerance, label + ": numerical difference " + str(error))

    def load(path):
        input_hashes[str(path.relative_to(ROOT))] = sha(path)
        return json.loads(path.read_text())

    receipt = load(args.run / "receipt.json")
    summary = load(args.run / "summary.json")
    equal(sha(args.run / "summary.json"), receipt["summary_sha256"], "summary hash")
    frozen_sources, checkout_hashes, checkout_drift = {}, {}, []
    for name, digest in receipt["source_sha256"].items():
        frozen = subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":" + name], cwd=ROOT)
        equal(hashlib.sha256(frozen).hexdigest(), digest, "frozen source " + name)
        frozen_sources[name] = frozen
        current = (ROOT / name).read_bytes() if (ROOT / name).exists() else None
        checkout_hashes[name] = hashlib.sha256(current).hexdigest() if current is not None else None
        if current is not None:
            input_hashes[name] = checkout_hashes[name]
        if checkout_hashes[name] != digest:
            test_only = name.startswith("tests/")
            deviation = dict(path=name, classification="test-only" if test_only else "functional-blocking",
                             frozen_sha256=digest, current_sha256=checkout_hashes[name])
            if test_only and current is not None:
                deviation["diff"] = ''.join(difflib.unified_diff(frozen.decode().splitlines(keepends=True),
                                                               current.decode().splitlines(keepends=True),
                                                               fromfile="freeze/" + name, tofile="checkout/" + name))
            checkout_drift.append(deviation)
            require(test_only, "current functional source differs from recorded freeze: " + name)
    design = json.loads(frozen_sources["data/provenance/r2d_precision/design.json"])
    expected_cases = {c["id"]: c for c in design["cases"]}
    published = {c["case"]: c for c in summary["cases"]}
    require(len(expected_cases) == len(design["cases"]) == 35, "thirty-five unique configured cases")
    require(set(expected_cases) == set(published) and len(summary["cases"]) == 35, "complete unique summary case set")
    require(len(list(args.run.glob("*-trials.jsonl"))) == len(expected_cases), "complete JSONL file set")
    reps = design["replicates_per_case"]
    require(reps == 2000, "two thousand replicates per case")
    all_seeds, representative_records, aggregates = set(), {}, []
    critical_cache = {}
    for case_id, case in expected_cases.items():
        path = args.run / (case_id + "-trials.jsonl")
        hashed = sha(path);input_hashes[str(path.relative_to(ROOT))] = hashed
        equal(hashed, published[case_id]["trials_sha256"], case_id + " file hash")
        counters, sums, seen = Counter(), Counter(), set()
        with path.open() as stream:
            for line in stream:
                record = json.loads(line);rep = record["replicate"]
                require(record["case"] == case_id and rep not in seen and 0 <= rep < reps, case_id + " replicate identity")
                seen.add(rep)
                seed = int.from_bytes(hashlib.sha256(f"{design['namespace']}|{case_id}|{rep}".encode()).digest()[:8], "big")
                require(record["seed"] == seed and seed not in all_seeds, case_id + " seed uniqueness")
                all_seeds.add(seed);counters["attempted"] += 1
                if record["status"] != "passed":
                    counters["failures"] += 1
                    continue
                counters["completed"] += 1
                if rep == 0:
                    representative_records[case_id] = record
                equal(record["test_forecasts"], case["test_forecasts"], case_id + " forecast count")
                require(len(record["star_counts"]) == record["stars"] == case["stars"]
                        and sum(record["star_counts"]) == case["test_forecasts"], case_id + " star allocation")
                w = weights(record["star_counts"])
                require(record["scientific_null_class"] == case["null_class"], case_id + " null label")
                beta, info = record["beta_hat"], record["mean_mark_information"]
                require(math.isfinite(beta) and beta >= 0 and math.isfinite(info) and info >= 0, case_id + " offset/information")
                require(record["gain_identity"] == (beta == 0 or info == 0), case_id + " exact identity classification")
                equal(record["conditional_expected_gain"], beta * record["conditional_expected_score"] - .5 * beta * beta * info,
                      case_id + " predictable target identity", "trial_algebra")
                equal(record["conditional_local_signal_projection"], record["conditional_expected_score"] / info if info > 0 else None,
                      case_id + " local projection", "trial_algebra")
                profile = np.asarray(case.get("effect_profile", np.ones(case["stars"])), dtype=float)
                equal(record["nominal_direct_oracle_gain"], case["nominal_oracle_gain"] * float(np.dot(w, profile ** 2)),
                      case_id + " nominal individual oracle signal", "trial_algebra")
                require(record["direct_effect_zero"] == (case["nominal_oracle_gain"] == 0 or np.all(profile == 0)),
                        case_id + " direct-effect classification")
                counters["identity_count"] += record["gain_identity"]
                counters["positive_score_negative_gain_count"] += record["conditional_expected_score"] > 0 and record["conditional_expected_gain"] < 0
                for name, field in [("mean_beta", "beta_hat"), ("mean_predictable_gain", "conditional_expected_gain"),
                                    ("mean_predictable_score", "conditional_expected_score"), ("mean_supported_marks", "markable_evaluation"),
                                    ("mean_nominal_individual_oracle_gain", "nominal_direct_oracle_gain")]:
                    sums[name] += record[field]
                for clustering in ("halves", "star"):
                    gain = record["methods"][clustering]["gain"]
                    score = record["methods"][clustering]["score"]
                    equal(gain["estimate"], beta * score["estimate"] - .5 * beta * beta * info,
                          case_id + " realized Gaussian gain identity", "trial_algebra")
                    equal(gain["estimate"], record["methods"]["star"]["gain"]["estimate"], case_id + " gain clustering invariance", "trial_algebra")
                    for statistic in ("gain", "score"):
                        method = record["methods"][clustering][statistic]
                        name = clustering + "-" + statistic
                        g = case["stars"] * (2 if clustering == "halves" else 1)
                        require(method["clusters"] == g and method["df"] == g - 1, case_id + " cluster degrees")
                        if g not in critical_cache:
                            critical_cache[g] = float(student_t.ppf(.95, g - 1))
                        q = critical_cache[g]
                        estimate, se = method["estimate"], method["se"]
                        require(math.isfinite(estimate) and math.isfinite(se) and se >= 0, case_id + " finite statistic")
                        equal(method["lower90"], estimate - q * se, case_id + " lower limit", "trial_interval")
                        equal(method["upper90"], estimate + q * se, case_id + " upper limit", "trial_interval")
                        equal(method["statistic"], estimate / se if se else None, case_id + " t statistic", "trial_interval")
                        equal(method["maximum_star_weight"], float(w.max()), case_id + " weight cap", "trial_interval")
                        require(method["zero_variance"] == (se == 0), case_id + " zero-variance label")
                        rejected = estimate > q * se
                        require(method["reject_one_sided"] == rejected, case_id + " rejection flag")
                        counters[name + ":rejections"] += rejected
                        counters[name + ":reject_with_negative_predictable_gain"] += rejected and record["conditional_expected_gain"] < 0
                        sums[name + ":estimate"] += estimate
                        if statistic == "gain":
                            covered = method["lower90"] <= record["conditional_expected_gain"] <= method["upper90"]
                            require(method["covers_conditional_expected_gain"] == covered, case_id + " gain coverage flag")
                            counters[name + ":covered"] += covered
                            if not record["gain_identity"]:
                                counters[name + ":nonidentity_count"] += 1
                                counters[name + ":nonidentity_covered"] += covered
                            if record["gain_identity"]:
                                equal(estimate, 0., case_id + " exact identity estimate", "trial_algebra")
                                equal(se, 0., case_id + " exact identity uncertainty", "trial_algebra")
                                equal(record["conditional_expected_gain"], 0., case_id + " exact identity target", "trial_algebra")
                sf = record["score_sign_flip"];patterns = 2 ** case["stars"]
                equal(sf["minimum_p"], 1 / patterns, case_id + " sign-flip minimum p")
                require(1 / patterns <= sf["p"] <= 1 and abs(sf["p"] * patterns - round(sf["p"] * patterns)) < 1e-10,
                        case_id + " sign-flip granularity")
                require(sf["reject_one_sided"] == (sf["p"] <= .05), case_id + " sign-flip rejection")
                counters["star-score-sign-flip:rejections"] += sf["p"] <= .05
        require(seen == set(range(reps)), case_id + " full replicate set")
        require(counters["failures"] == 0, case_id + " zero trial failures")
        n = counters["completed"];expected = published[case_id]
        for field in ("attempted", "completed", "failures", "identity_count", "positive_score_negative_gain_count"):
            equal(counters[field], expected[field], case_id + ":" + field)
        require(expected["settings"] == case, case_id + " configured settings")
        for field in ("mean_beta", "mean_predictable_gain", "mean_predictable_score", "mean_supported_marks", "mean_nominal_individual_oracle_gain"):
            equal(sums[field] / n, expected[field], case_id + ":" + field)
        reconstructed_methods = {}
        for name, method in expected["methods"].items():
            k = counters[name + ":rejections"]
            reconstructed = dict(rejections=k, rate=k / n, exact_mc95=exact_interval(k, n))
            if name != "star-score-sign-flip":
                reconstructed.update(mean_estimate=sums[name + ":estimate"] / n,
                    reject_with_negative_predictable_gain=counters[name + ":reject_with_negative_predictable_gain"])
            if name.endswith("gain"):
                covered, ni, nic = (counters[name + ":" + field] for field in ("covered", "nonidentity_count", "nonidentity_covered"))
                reconstructed.update(covered=covered, coverage=covered / n, coverage_mc95=exact_interval(covered, n),
                                     nonidentity_count=ni, nonidentity_covered=nic,
                                     nonidentity_coverage=nic / ni if ni else None,
                                     nonidentity_coverage_mc95=exact_interval(nic, ni))
            else:
                if name == "star-score-sign-flip":
                    reconstructed["minimum_p"] = 2. ** (-case["stars"])
            for field, value in reconstructed.items():
                equal(value, method[field], case_id + ":" + name + ":" + field, "mc_interval" if "mc95" in field else "aggregate")
            reconstructed_methods[name] = reconstructed
        aggregates.append(dict(case=case_id, completed=n, identity_count=counters["identity_count"],
                               mean_predictable_gain=sums["mean_predictable_gain"] / n,
                               mean_predictable_score=sums["mean_predictable_score"] / n, methods=reconstructed_methods))
        counts["trial_rows"] += counters["attempted"]
    require(counts["trial_rows"] == receipt["attempted"] == 70000, "seventy thousand attempted trials")
    require(receipt["failures"] == 0 and len(all_seeds) == 70000, "zero failures and globally unique seeds")
    representatives = []
    for path in sorted(args.vectors.glob("*.json")):
        snapshot = load(path);case = snapshot["case"];case_id=case["id"]
        require(case == expected_cases[case_id] and snapshot["replicate"] == 0, "representative configuration")
        saved = representative_records[case_id]
        require(snapshot["seed"] == saved["seed"], "representative existing seed")
        for field, value in snapshot["result"].items():
            if isinstance(value, (int, float, bool, str)) or value is None:
                equal(value, saved[field], case_id + ":rerun:" + field, "representative")
        fitted = [reconstruct_star(s["history"], case) for s in snapshot["vectors"]["fitted"]]
        training_counts = np.asarray([sum(s["training"] & s["mark_usable"]) for s in fitted])
        active = training_counts > 0
        numerator = denominator = 0.
        if active.sum() >= 3:
            training_weights = weights(training_counts[active])
            for s, count, weight in zip([s for s,a in zip(fitted,active) if a], training_counts[active], training_weights):
                mask = s["training"] & s["mark_usable"]
                z, residual, variance = s["z"][mask], np.asarray(s["history"]["y"])[mask] - s["baseline_mean"][mask], s["variance"][mask]
                numerator += weight / count * float(np.sum(z * residual / variance))
                denominator += weight / count * float(np.sum(z * z / variance))
        beta = max(0., numerator / denominator) if denominator > 0 else 0.
        equal(beta, saved["beta_hat"], case_id + " reconstructed beta", "representative")
        vectors = {k:[] for k in ("gain", "score", "expected_gain", "expected_score", "star", "epoch", "shift", "information")}
        for i, (fit, stored) in enumerate(zip(fitted, snapshot["vectors"]["fitted"])):
            for key in ("raw_mean", "baseline_mean", "variance", "z", "mark_usable", "training", "timed_training", "level_shift"):
                equal(np.asarray(fit[key]).tolist(), stored[key], case_id + ":fitted:" + key, "representative", 1e-9)
            first = int(fit["history"]["development_n"])
            y, truth = np.asarray(fit["history"]["y"])[first:], np.asarray(fit["history"]["true_mean"])[first:]
            mu, variance, z = fit["baseline_mean"][first:], fit["variance"][first:], fit["z"][first:]
            shift = beta * z
            gain = norm.logpdf(y, loc=mu + shift, scale=np.sqrt(variance)) - norm.logpdf(y, loc=mu, scale=np.sqrt(variance))
            vals=dict(gain=gain, score=z*(y-mu)/variance,
                      expected_gain=shift*(truth-mu)/variance-.5*shift**2/variance,
                      expected_score=z*(truth-mu)/variance, star=np.full(len(y),i,dtype=int),
                      epoch=np.asarray(fit["history"]["epoch"])[first:], shift=shift, information=z*z/variance)
            for key,value in vals.items():vectors[key].extend(value.tolist())
        vectors={k:np.asarray(v) for k,v in vectors.items()}
        for key in snapshot["vectors"]:
            if key not in ("beta","fitted"):
                equal(vectors[key].tolist(),snapshot["vectors"][key],case_id+":vector:"+key,"representative",1e-9)
        stars, epochs=vectors['star'].astype(int),vectors['epoch'].astype(int)
        allocation=np.bincount(stars);row_weights=weights(allocation)[stars]/allocation[stars]
        for field,key in [('conditional_expected_gain','expected_gain'),('conditional_expected_score','expected_score'),('mean_mark_information','information')]:
            equal(float(np.dot(row_weights,vectors[key])),saved[field],case_id+":"+field,"representative",1e-9)
        for clustering in ('halves','star'):
            for statistic in ('gain','score'):
                actual=interval(vectors[statistic],stars,epochs,clustering)
                expected=saved['methods'][clustering][statistic]
                for field,value in actual.items():equal(value,expected[field],case_id+':CR1:'+clustering+':'+statistic+':'+field,'representative',1e-9)
        contributions=[sum(vectors['score'][stars==s]*row_weights[stars==s]) for s in range(case['stars'])]
        observed=sum(contributions)
        p=sum(sum(a*b for a,b in zip(sign,contributions))>=observed-1e-12 for sign in itertools.product((-1.,1.),repeat=case['stars']))/(2**case['stars'])
        equal(p,saved['score_sign_flip']['p'],case_id+':sign-flip','representative')
        representatives.append(dict(case=case_id,replicate=0,seed=saved['seed'],forecasts=len(stars),sign_flip_p=p))
    require(len(representatives)==4,"four existing-seed representative vector snapshots")
    for name, expected in input_hashes.items():
        require(sha(ROOT/name)==expected,"input remained unchanged: "+name)
    report=dict(status='failed' if failures else 'passed',scope='independent saved-JSONL aggregation and four exact-seed vector reconstructions; no candidate/runner imports or new grid',
                counts=dict(counts),unique_seeds=len(all_seeds),cases_checked=len(aggregates),representatives=representatives,
                maximum_absolute_errors=dict(errors),failures=failures,input_sha256=input_hashes,checker_sha256=sha(__file__),
                freeze_commit=receipt['freeze_commit'],frozen_source_sha256=receipt['source_sha256'],
                current_checkout_source_sha256=checkout_hashes,current_checkout_drift=checkout_drift,
                aggregates=aggregates,limits=['Full-grid SEs are checked from saved estimate/SE/cluster metadata; raw vector CR1 is independently rebuilt for four representative trials only.',
                    'Representative raw generator histories come from same-seed candidate reruns; the RNG/DGP itself is not independently regenerated.',
                    'Exact Monte Carlo intervals are inverted binomial tails and are per-cell, not simultaneous guarantees.',
                    'Predictable target is conditional on the realized generator path and frozen forecasts, not unconditional long-run KL or actual astronomical forecast gain.'])
    (args.output/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    (args.output/'report.md').write_text('# Independent R2d precision audit\n\n'+json.dumps({k:report[k] for k in ('status','cases_checked','unique_seeds','counts','representatives','maximum_absolute_errors','failures','current_checkout_drift')},indent=2)+'\n\n'+ '\n'.join('- '+s for s in report['limits'])+'\n')
    audit_receipt = dict(status=report['status'], freeze_commit=receipt['freeze_commit'],
                         checker_sha256=sha(__file__), input_sha256=input_hashes,
                         frozen_source_sha256=receipt['source_sha256'],
                         current_checkout_source_sha256=checkout_hashes,current_checkout_drift=checkout_drift,
                         summary_sha256=sha(args.output/'summary.json'),
                         report_sha256=sha(args.output/'report.md'),
                         python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                         independent_methods='binomial tail inversion; capped-weight root; OLS history reconstruction; Gaussian logpdf differences; direct CR1 residual sums; exhaustive sign flips',
                         no_candidate_or_runner_imports=True, new_monte_carlo_trials=0)
    (args.output/'receipt.json').write_text(json.dumps(audit_receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('status','cases_checked','unique_seeds','counts','maximum_absolute_errors','failures')}))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
