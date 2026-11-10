"""Independent C67 recount and fixed-sequence logic; retained synthetic trials only."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom, t as student_t

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def proportion(k, n):
    lo = brentq(lambda p: binom.sf(k - 1, n, p) - .025, 0., 1., xtol=1e-14) if k else 0.
    hi = brentq(lambda p: binom.cdf(k, n, p) - .025, 0., 1., xtol=1e-14) if k < n else 1.
    return dict(k=int(k), n=int(n), rate=k / n, binomial_mc95=[lo, hi])


def gaussian_counterexample():
    information = np.repeat([.1, .1, .1, 20.], 6)
    wanted_gain = np.repeat([.09, .10, .11, .10], 6)
    z = np.sqrt(information)
    score = wanted_gain + .5 * information
    outcome = score / z
    gain = z * outcome - .5 * z * z
    stars, epochs = np.repeat(np.arange(4), 6), np.tile(np.arange(6), 4)
    methods = {}
    for clustering in ("star", "halves"):
        group = stars if clustering == "star" else stars * 2 + (epochs >= 3)
        groups = sorted(set(group.tolist()))
        methods[clustering] = {}
        for name, values in (("gain", gain), ("score", score)):
            mean = float(np.mean(values))
            cluster_totals = [float(np.sum((values - mean)[group == g]) / len(values)) for g in groups]
            se = math.sqrt(len(groups) / (len(groups) - 1) * sum(x * x for x in cluster_totals))
            critical = float(student_t.ppf(.95, len(groups) - 1))
            methods[clustering][name] = dict(estimate=mean, se=se, statistic=mean / se,
                                           critical=critical, reject=mean > critical * se)
    return dict(scope="invented Gaussian row-level algebra, not a new grid or an admitted generator history",
                beta=1., variance=1., equal_star_weights=.25, rows_per_star=6,
                information_by_star=[.1, .1, .1, 20.], gain_by_star=[.09, .10, .11, .10],
                gaussian_identity_max_error=float(np.max(np.abs(gain - wanted_gain))), methods=methods)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "outputs/r2d_precision_67c45ab")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/g3a_sequence_audit")
    parser.add_argument("--evidence", type=Path, default=ROOT / "data/provenance/g3a_preparation/sequence-check.json")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    failures, input_hashes, source_drift, cases = [], {}, [], {}

    def check(ok, label):
        if not ok:
            failures.append(label)

    def load(path):
        input_hashes[str(path.relative_to(ROOT))] = sha(path)
        return json.loads(path.read_text())

    receipt, summary = load(args.run / "receipt.json"), load(args.run / "summary.json")
    public_summary = ROOT / "data/provenance/r2d_precision/summary.json"
    public_receipt = ROOT / "data/provenance/r2d_precision/receipt.json"
    claude = load(ROOT / "data/provenance/r2d_claude_review/checks.json")
    check(sha(args.run / "summary.json") == receipt["summary_sha256"], "saved summary receipt hash")
    for saved, public in ((args.run / "summary.json", public_summary), (args.run / "receipt.json", public_receipt)):
        input_hashes[str(public.relative_to(ROOT))] = sha(public)
        check(sha(saved) == sha(public), "retained/public bytes: " + public.name)
    frozen_sources = {}
    for name, digest in receipt["source_sha256"].items():
        frozen = subprocess.check_output(["git", "show", receipt["freeze_commit"] + ":" + name], cwd=ROOT)
        check(hashlib.sha256(frozen).hexdigest() == digest, "frozen source hash: " + name)
        frozen_sources[name] = frozen
        current_hash = sha(ROOT / name) if (ROOT / name).exists() else None
        if current_hash != digest:
            source_drift.append(dict(path=name, frozen_sha256=digest, current_sha256=current_hash,
                                     test_only=name.startswith("tests/")))
            check(name.startswith("tests/"), "functional source drift: " + name)
    design = json.loads(frozen_sources["data/provenance/r2d_precision/design.json"])
    configured = {c["id"]: c for c in design["cases"]}
    published = {c["case"]: c for c in summary["cases"]}
    check(len(configured) == len(published) == 35 and set(configured) == set(published), "35 configured cases")
    all_seeds, total, failed = set(), 0, 0
    pooled = {cl: Counter() for cl in ("star", "halves")}
    strict_cases = []
    for name, config in configured.items():
        path = args.run / (name + "-trials.jsonl")
        input_hashes[str(path.relative_to(ROOT))] = sha(path)
        check(sha(path) == published[name]["trials_sha256"], name + " trial bytes")
        tally, seen = {cl: Counter() for cl in ("star", "halves")}, set()
        targets, n = Counter(), 0
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                rep = row["replicate"]
                check(row["case"] == name and rep not in seen, name + " unique replicate")
                seen.add(rep)
                expected_seed = int.from_bytes(hashlib.sha256(f"{design['namespace']}|{name}|{rep}".encode()).digest()[:8], "big")
                check(row["seed"] == expected_seed and expected_seed not in all_seeds, name + " unique seed")
                all_seeds.add(expected_seed)
                total += 1
                if row["status"] != "passed":
                    failed += 1
                    continue
                n += 1
                targets["positive_score_nonpositive_gain"] += row["conditional_expected_score"] > 0 and row["conditional_expected_gain"] <= 0
                targets["sum_predictable_score"] += row["conditional_expected_score"]
                targets["sum_predictable_gain"] += row["conditional_expected_gain"]
                for cl in tally:
                    flags = {}
                    for stat in ("score", "gain"):
                        method = row["methods"][cl][stat]
                        groups = config["stars"] * (2 if cl == "halves" else 1)
                        threshold = float(student_t.ppf(.95, groups - 1))
                        check(method["df"] == groups - 1 and method["clusters"] == groups, name + " cluster metadata")
                        flags[stat] = method["estimate"] > threshold * method["se"]
                        check(flags[stat] == method["reject_one_sided"], name + " numeric rejection flag")
                        tally[cl][stat] += flags[stat]
                    tally[cl]["both"] += flags["score"] and flags["gain"]
                    tally[cl]["gain_without_score"] += flags["gain"] and not flags["score"]
                    tally[cl]["score_without_gain"] += flags["score"] and not flags["gain"]
                    tally[cl]["neither"] += not flags["score"] and not flags["gain"]
        check(seen == set(range(2000)) and n == 2000, name + " full successful replicate set")
        result = dict(n=n, settings=config, methods={}, targets=dict(
                      mean_predictable_gain=targets["sum_predictable_gain"] / n,
                      mean_predictable_score=targets["sum_predictable_score"] / n,
                      positive_score_nonpositive_gain=targets["positive_score_nonpositive_gain"]))
        for cl, counts in tally.items():
            result["methods"][cl] = {key: proportion(counts[key], n) for key in
                                      ("gain", "score", "both", "gain_without_score", "score_without_gain", "neither")}
            for stat in ("gain", "score"):
                check(counts[stat] == published[name]["methods"][cl + "-" + stat]["rejections"], name + " summary recount")
            for key in ("gain", "score", "both", "gain_without_score"):
                check(counts[key] == claude["cases"][name][cl][key]["k"], name + " Claude independent recount")
            if config["null_class"] == "strict_oracle_predictive_null":
                pooled[cl].update(counts)
                pooled[cl]["n"] += n
        if config["null_class"] == "strict_oracle_predictive_null":
            strict_cases.append(name)
        cases[name] = result
    check(total == len(all_seeds) == 70000 and failed == receipt["failures"] == 0, "70,000 unique successful trials")
    check(len(strict_cases) == 4, "four strict-oracle cells")
    pooled_report = {cl: {key: proportion(counts[key], counts["n"]) for key in
                          ("gain", "score", "both", "gain_without_score")} for cl, counts in pooled.items()}
    check(pooled["star"]["score"] == 397 and pooled["star"]["n"] == 8000, "C67 strict-null 397/8000")
    check(cases["core-s8-n1100-effect"]["methods"]["star"]["gain"]["k"] ==
          cases["core-s8-n1100-effect"]["methods"]["star"]["both"]["k"] == 733, "C67 clean joint 733/2000")
    joint_absence = {cl: proportion(sum(c["methods"][cl]["gain_without_score"]["k"] for c in cases.values()), total)
                     for cl in ("star", "halves")}
    check(all(x["k"] == 0 for x in joint_absence.values()), "C67 empirical gain subset in both clusterings")
    probability = .95 ** 2000
    pmf = [probability]
    for k in range(100):
        probability *= (2000 - k) / (k + 1) * .05 / .95
        pmf.append(probability)
    fail_one = 1 - math.fsum(pmf)
    fail_four = 1 - (1 - fail_one) ** 4
    check(abs(fail_one - claude["per_cell_screen_note"]["exact_5pct_test_fails_observed_le_5pct_in_2000_trials"]) < 1e-12, "binomial per-cell screen arithmetic")
    check(abs(fail_four - claude["per_cell_screen_note"]["four_independent_cells_any_fail"]) < 1e-12, "four-independent-cell arithmetic")
    counterexample = gaussian_counterexample()
    check(all(m["gain"]["reject"] and not m["score"]["reject"] for m in counterexample["methods"].values()), "gain-subset algebra counterexample")
    for name, digest in input_hashes.items():
        check(sha(ROOT / name) == digest, "input stability: " + name)
    report = dict(status="failed" if failures else "passed", scope="independent retained synthetic-trial recount, not new simulations or observations",
                  failures=failures, trials=total, cases=cases, unique_seeds=len(all_seeds), failed_trials=failed,
                  strict_null_cases=strict_cases, pooled_strict_oracle=pooled_report,
                  all_trials_gain_without_score=joint_absence,
                  exact_5pct_screen=dict(fail_one_of_2000=fail_one, fail_any_of_four_independent_cells=fail_four,
                                        calculation="finite binomial PMF recurrence, counts zero through100"),
                  counterexample=counterexample, current_checkout_drift=source_drift,
                  freeze_commit=receipt["freeze_commit"], input_sha256=input_hashes, checker_sha256=sha(__file__),
                  fixed_sequence=dict(alpha=.05, association_null="theta_score <= 0", forecast_gain_null="theta_gain <= 0",
                    association_rejection="R1={p1<=alpha}", gain_rejection="R1 intersect R2, R2={p2<=alpha}",
                    cases=[dict(association_null=True,gain_null=True,FWER="P(R1)<=alpha if stage1 has level alpha"),
                           dict(association_null=True,gain_null=False,FWER="P(R1)<=alpha if stage1 has level alpha; may be logically absent in some models"),
                           dict(association_null=False,gain_null=True,FWER="P(R1 intersect R2)<=P(R2)<=alpha if stage2 is valid over this partial null"),
                           dict(association_null=False,gain_null=False,FWER="0; neither rejection is a false claim")],
                    assumptions=["Order, both claims, cohort, transformations, weights and tests fixed before sealed scoring.",
                                 "Each marginal test is level alpha under its own entire null, including nuisance and partial-null configurations; stage2 need not be conditionally level alpha given stage1 rejection.",
                                 "No independence between the two tests is required by the fixed-sequence proof.",
                                 "Fixed development rules and availability must be respected; selection needs its own validity justification.",
                                 "CR1/t finite-few-star level is not proved by the fixed-sequence theorem or certified by this simulation."],
                    conclusion="Strong FWER is at most alpha under those conditions; it does not generally equal the pooled score size. In the retained grid the sequence has exactly the stand-alone gain rejection counts; future power equality is unproved."),
                  pooling_limits=["397/8000 is an equally weighted descriptive average of four oracle cases, not a maximum over cases or an observational guarantee.",
                                  "The quoted exact binomial interval assumes a common Bernoulli rejection probability. Distinct cell probabilities need not share it; report per-cell intervals too.",
                                  "A per-cell screen failure probability of .473 and four-cell probability .923 assume an exactly5% procedure and independent repeated trials/cells; they do not excuse a systematic size error.",
                                  "Zero observed gain-without-score cases does not prove impossibility or zero future probability; the Gaussian counterexample rules out the proposed general algebraic implication."])
    output = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (args.output / "summary.json").write_text(output)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    if args.evidence.exists():
        raise FileExistsError(args.evidence)
    args.evidence.write_text(output)
    audit_receipt = dict(freeze_commit=receipt["freeze_commit"], checker_sha256=sha(__file__),
                         summary_sha256=sha(args.output / "summary.json"), evidence_sha256=sha(args.evidence),
                         input_sha256=input_hashes, no_new_grid=True, no_observations=True)
    (args.output / "receipt.json").write_text(json.dumps(audit_receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(status=report["status"], trials=total, failures=failures,
                          gain_without_score={cl:v["k"] for cl,v in joint_absence.items()},
                          pooled_star_score=pooled_report["star"]["score"], screen_fail_one=fail_one,screen_fail_four=fail_four)))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
