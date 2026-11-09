# Bounded supporting checks for the independent review

These checks support the independent review of **BWBrook/dwarf-nova-memory**, commit **`f48f0e2c728739a97fb90fb795eddb54c98c2dc3`**, dated 9 November 2026. They are small arithmetic and synthetic demonstrations. They do not reproduce the full study, acquire observations, inspect any closed archive record, or determine the cause of the reported forecast gain.

## Contents

| File | Purpose | Local project checkout needed? |
|---|---|---|
| `aggregate_check.py` | Recalculate the primary aggregate mean/interval, exponentiated mean, leave-one-block-out means, and one fixed coarser grouping | No; optional original-file cross-check |
| `landmark_mixture_check.py` | Compare selected repository scoring/routing paths with independently calculated probabilities on synthetic inputs | **Yes**, exact selected source bytes |
| `endpoint_counterexample_check.py` | Independently enumerate and fit a synthetic positive endpoint-error counterexample | No; optional helper comparison after the independent fit |
| `censor_straddle.py` | Exhibit the production/reference treatment of an onset bracket that crosses a cutoff | **Yes**, exact selected source bytes |
| `_review_support.py` | Shared provenance, source-hash verification, explicit module loading, and output helpers | No |
| `public_block_aggregates.json` | Ten public counts/means plus the reported primary values for comparison | No |
| `source_provenance.json` | Fixed commit, original source SHA-256 values, bundled input hash, and original review-script hashes | No |
| `requirements.txt` | Versions used for the supplied outputs | No |
| `outputs/` | JSON results from the completed checks | No |

No original project modules, raw observations, observer identities, per-forecast records, or third-party texts are bundled. The synthetic checks were adapted from the review workspace's `verify_landmark_mixture.py`, `verify_endpoint_counterexample.py`, and `verify_censor_straddle.py`; their original SHA-256 values are recorded in the provenance file.

## Environment and commands

The included results were produced with Python **3.12.14**, NumPy **2.3.5**, and SciPy **1.17.0**. Dependencies are pinned in `requirements.txt`; use a suitable local Python environment. The scripts themselves install nothing and make no network requests.

Run from this `checks/` directory. Every command requires an explicit `--output`. Its parent directory must already exist. The included `outputs/` directory is ready to use; choose different filenames to preserve the supplied results.

Standalone checks:

```sh
python3 aggregate_check.py --output outputs/aggregate_rerun.json
python3 endpoint_counterexample_check.py --output outputs/endpoint_standalone_rerun.json
```

Checks against a local checkout of the reviewed source:

```sh
python3 landmark_mixture_check.py \
  --repo /path/to/reviewed/dwarf-nova-memory \
  --output outputs/landmark_rerun.json

python3 endpoint_counterexample_check.py \
  --repo /path/to/reviewed/dwarf-nova-memory \
  --output outputs/endpoint_with_repo_rerun.json

python3 aggregate_check.py \
  --repo /path/to/reviewed/dwarf-nova-memory \
  --output outputs/aggregate_with_repo_rerun.json

python3 censor_straddle.py \
  --repo /path/to/reviewed/dwarf-nova-memory \
  --output outputs/censor_straddle_rerun.json
```

`--repo` is required for the landmark and cutoff-straddling checks. The endpoint check completes its independent enumeration and fit **before** loading the optional project helper. The aggregate option verifies and compares the original public figure JSON; it imports no project code. A standalone rerun has the same numerical result but naturally lacks the optional source-verification fields.

### Read/write and source-pinning behavior

Each CLI writes only its specified JSON output, after its calculations/checks succeed, and prints a completion message to standard output. It disables Python bytecode writes. It does not create output directories, run repository pipelines, call archive clients, or invoke a project script's `main()` function. With `--repo`, output paths inside that checkout are rejected. Supplied check/input files cannot be overwritten as outputs.

Before any project import, the relevant files are compared with the SHA-256 values in `source_provenance.json`. Missing or changed files produce a nonzero exit with an explicit error. No source is fetched, repaired, or silently substituted. The landmark check loads the verified `dnmem` package initializer, `ledger_forecast.py`, and `directional_forecast.py` by explicit local path. The optional endpoint comparison loads only the verified `scripts/a10d_design_calculations.py` and calls its calculation functions. The cutoff-straddling check verifies the package initializer, `extract.py`, `extract_x3.py`, `extract_x4.py`, `prefix_features.py`, and `prefix_reference.py` before explicitly importing that local chain; its synthetic visits and extracted episode are injected.

These checks pin **selected source bytes**, not every file in a checkout. No Git command is required, and matching these files does not certify the whole repository, its history, or its scientific conclusions. Floating-point optimization can vary slightly across platforms; the documented tolerances allow small numerical differences.

## 1. Public aggregate calculation

The input copies only `block`, `n`, and `mean_gain` from the ten public blocks in `manuscript/figure-data/fig2-gains.json`, plus the primary comparison's reported count, mean, and interval for verification. Provenance records the exact original file hash and commit. It contains no individual forecast scores.

For block counts `n_g`, means `m_g`, total `N`, and number of blocks `G`, the independent calculation is:

```text
mean = sum(n_g * m_g) / N
U_g = n_g * (m_g - mean)
CR1 variance = [G / (G - 1)] * sum(U_g^2) / N^2
90% interval = mean +/- t(.95, G - 1) * sqrt(CR1 variance)
```

For an intercept-only mean, these aggregate residual sums suffice for the stated cluster-robust arithmetic. With ten nonempty blocks the critical value has nine degrees of freedom. The two-sided 90% lower endpoint equals the one-sided 95% lower bound.

### Supplied result

- Count: **441**.
- Weighted mean gain: **0.0165335121774365** nats per forecast.
- CR1 standard error: **0.00632028483430624**.
- 90% t9 interval: **[0.00494771630959865, 0.0281193080452744]**.
- `exp(mean)`: **1.01667094707234**, a **1.66709470723404%** geometric bracket-mass increase.
- Leave-one-block-out mean range: **0.0132406166119419–0.0193900421035201**.
- Eight of the ten descriptive block means are positive.

The primary mean and endpoints reproduce the public reference to less than `1e-12` absolute difference.

### One exploratory coarser grouping

The script combines adjacent blocks exactly once: `(0,1), (2,3), (4,5), (6,7), (8,9)`. It does not search widths or offsets. These are nominal 12-year groups; the final group contains the shorter terminal block. Reapplying the same CR1 calculation with five groups and a t4 critical value gives **[0.00363014725437663, 0.0294368771004964]**, with the same weighted mean to rounding.

This is a **post-result review sensitivity**, not a predeclared analysis or a replacement primary. A positive lower bound under this grouping does not prove independence between groups or valid uncertainty under arbitrary slow dependence. Aggregate reproduction assumes the supplied block means/counts are correct and cannot audit event extraction or individual scores. The exponentiated mean is not forecast accuracy, explained variance, or a physical effect size.

## 2. Landmark mixture and routing calculation

This check uses one completely synthetic feature record and two synthetic outcomes: an onset interval and a right-censored time. It exercises M0, M2, and M3 with a point endpoint and with five equally weighted endpoint nodes. The independent calculation uses Python's `NormalDist` rather than the repository's vectorized log-probability implementation.

For uncertain endpoint node `e_j`, numerator `N_j`, and survival-to-issue probability `S_j`, the tested score is:

```text
log[sum_j N_j / sum_j S_j]
```

This mixes before conditioning on survival. It generally differs from the unweighted mean of the separately conditioned ratios `N_j / S_j`; that alternative is recorded for comparison. The check also verifies equal M2/M3 scores under the chosen missing-previous-gap, missing-landmark, invalid-duration, and zero-coefficient cases.

The supplied run completed **12 probability comparisons** and **four routing comparisons**. The maximum absolute log-score discrepancy was **4.44e-16**; all four routing contrasts were zero.

This supports a limited implementation claim: the selected scoring paths agree with the independently written working-probability formula for the fixture. It does **not** establish that the endpoint distribution is correct, that the outcome brackets are true supports, that the score is proper for physical onsets, that all extraction uncertainty is propagated, or that any real-star result is reproduced.

## 3. Endpoint-error counterexample

The standalone check enumerates exact synthetic probabilities with `Fraction` and fits an independently written conditional lognormal likelihood. True duration is always 10. True issue age takes values 2 or 8, and endpoint error takes values 0 or 6, independently and equiprobably. The true gap is 5 with probability 0.9 or 20 with probability 0.1. Retention requires nonnegative observed issue age and survival to the true issue age.

Among retained states with observed age 2, observed duration 10 has mean remaining wait **4.5**, while observed duration 16 has mean remaining wait **12**. The high-duration group's conditional probability is exactly **1/11**. Because these two groups' remaining-wait supports are disjoint at that observed age, the conditional mutual information is **0.304636097349238** nats, despite constant true duration.

The independent numerical calculation uses a nine-start Powell baseline fit and then estimates a nonnegative duration offset with that baseline fixed. Its narrow synthetic event intervals have width 0.02. The supplied result is:

- Duration coefficient: **0.242535990960438** per standard deviation of observed log duration.
- Fixed-baseline mean score gain: **0.0837449590052826** nats per retained synthetic anchor.
- All nine baseline optimization starts succeeded.

The optional project-helper comparison is performed only after that independent fit. It agrees to **3.97e-8** in the coefficient and **6.38e-8** in the gain. Checked tolerances are `1e-12` for the mutual information, `1e-4` for the coefficient, and `1e-7` for the gain. The helper uses a separate vectorized likelihood/optimizer route; its file-writing entry point is not called.

This is an **existence demonstration**, not an estimate of SS Cyg's measurement bias and not evidence that endpoint error explains the actual result. It establishes that a nonnegative duration coefficient does not universally eliminate predictive information induced by endpoint error plus landmark selection. There are no random draws and no archive inputs.

## 4. Bracket straddling a censor cutoff

This check injects synthetic visit summaries and a synthetic extracted episode into both `prefix_features.outcome_evidence` and `prefix_reference.outcome_evidence`. It isolates the outcome-routing contract, rather than requiring photometry or running an extraction on real observations.

The focal case has issue time **10**, onset bracket **(18, 22]**, and censor cutoff **20**. Both implementations classify it as **right-censored at 20**, discard the onset endpoints in the returned evidence, and mark survival as unambiguous. The branch is reproduced both when the cutoff arises from a coverage gap and when the forecast is superseded.

The logical witness is an onset at **19**: it lies inside the input bracket but precedes the censor cutoff. Even if the bracket were a certain support interval, its membership alone would therefore not establish survival through 20. An onset before the cutoff can coexist with the stated interval evidence. Production/reference agreement does not settle the validity of that shared contract.

Controls show that a bracket wholly before the cutoff, **(16, 18]**, is interval evidence; a wholly later bracket, **(22, 24]**, is censored at 20; and a bracket straddling issue, **(9, 11]**, is excluded as ambiguous survival. Across four scenarios, two stop reasons, and two implementations, **16 calls** reproduce the reviewed behavior.

This is an implementation-level synthetic witness. It does **not** establish that this branch occurred in the empirical evaluation, how often it occurred, or whether correcting it would change the reported result. No real observations, empirical event counts, or scores are read.

## Supplied execution record

All five following modes completed successfully on 9 November 2026:

- Aggregate check with optional verification against the original public figure file: `outputs/aggregate_check.json`.
- Landmark check with verified selected project modules: `outputs/landmark_mixture_check.json`.
- Independent endpoint check without any repository argument: `outputs/endpoint_counterexample_standalone.json`.
- Endpoint check with the optional verified helper comparison: `outputs/endpoint_counterexample_with_repo.json`.
- Cutoff-straddling branch check with both verified implementations: `outputs/censor_straddle.json`.

The JSON results include the runtime versions, source/input hashes where applicable, calculation details, and scope limitations. None is a new astronomical result or a substitute for the review's scientific judgment.
