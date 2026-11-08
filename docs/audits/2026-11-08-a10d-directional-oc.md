# A10d directional forecasting: synthetic calibration and development gate

Codex, 8 November 2026. Source freeze `8f5df44b950ec5781ba1e31e074e56976909a051`.

**Subsequent decision:** Barry has now explicitly accepted the finite-screen
option (D022). The initial hold reported below is resolved; the first real
development fit proceeds separately under the A10e protocol. The synthetic
results and their limits are unchanged.

## Result

The frozen 360-trial grid completes without failures and passes the
prespecified **observed-rate and joint-MC calibration screen**. An independent
calculator reconciles all 360 primary intervals, all 80 reference-calibration
records and the aggregate decisions against 823,070 variant score rows.
Recomputing 22,980 representative scores from serialized forecasts gives a
maximum difference of 1.14e-13, with no population or routing discrepancies.

This does **not** certify that the population false-positive rate is ≤5%.
The gate-policy clarification raised before outcomes remains unanswered, so
D021 keeps the first real development fit closed. No real duration–following-
gap computation or 1960+ access occurs in this tranche. D018 remains held-out
forecast gain, with the coefficient secondary.

### Primary six-year results

| Synthetic case | Trials | Mean M3−M2, nats/issuance | Confirmations |
|---|---:|---:|---:|
| v2 independent null | 40 | −0.00044 | 0/40 |
| v2 structured null | 40 | −0.00185 | 1/40 |
| v2 gross reports | 40 | +0.00046 | 2/40 |
| v2 persistent offsets | 40 | −0.00042 | 0/40 |
| v2 adaptive effort | 40 | −0.00082 | 0/40 |
| v2 shared state, φ=.90 | 40 | +0.00191 | 6/40 |
| v2 shared state, φ=.98 | 40 | +0.00499 | 7/40 |
| v2 injected effect | 40 | +0.00452 | 11/40 |
| v4 independent null | 20 | −0.00092 | 0/20 |
| v4 injected effect | 20 | +0.00151 | 6/20 |

Every gated null meets the fixed cap of 2/40 or 1/20. The worst observed
rate, gross reports at 2/40, has a two-sided exact 95% interval of 0.6–16.9%
and a one-sided upper bound of 14.9%. Even 0/40 has a one-sided upper bound
of 7.2%. These are finite screens, not five-percent size certificates; the
plug-in MC SE of zero at 0 rejections must not be read as zero uncertainty.

The injected-effect power is **27.5%** (MC SE 7.1 percentage points; exact
95% interval 14.6–43.9%), with 390.9 scored forecasts per evaluation history
on average. The v4 sensitivity gives 30%, with much wider MC uncertainty.
This replaces the Gaussian power projection for this fitted forecast system;
it is conditional on the simulated effect and observation process, not a
power guarantee for SS Cyg. Gain is positive in 31/40 histories, but only
11/40 confirm. The median 90% interval half-width is 0.00975 nats per
issuance. A non-confirmation cannot establish an absent effect.

### Reference calibration

Six-year joint-MC containment is 37/40 under the null and 34/40 under the
alternative; among nonzero offsets it is 24/27 and 31/37. The predeclared
lower-tail tests against .90 give p=.777/.206 overall and .515/.160 for
interior fits, so no screen rejects. The alternative's point containment is
85% overall and 83.8% among interior fits: nominal conditional coverage is
not established. The finite six-replica references are estimates, not exact
truth. All 16 analytic-zero and 64 nonzero reference records are retained.

Three-year sensitivity containment is 36/40 and 35/40 overall. Six-year
clusters remain primary as frozen before the outcomes; no interval method
is selected using these results. All 480 variant/comparison summaries,
coefficient distributions, evidence counts, MC SEs and exact binomial
intervals are in `data/simulations/a10d_20261108/`.

### What the state cases show

A current mark can win even when no direct memory term exists. In the
joint-valid comparison, current versus lagged duration confirms in 3/40
(φ=.90) and 6/40 (φ=.98) pure-state histories. At φ=.98, M3−M2 mean gain is
larger than the injected-effect mean. Thus even separating M3 from P3 cannot
identify a direct physical mechanism. The primary claim remains incremental
forecast information beyond the specified measured timing baseline.

## Changes and independent checks

M2 fits previous log gap plus six-gap local history. M3/P3 fit nonnegative
mark offsets with M2 frozen, preserving literal fallback and exact zero
nesting. This amended training objective avoids fitting one likelihood and
deploying another for missing marks. The independent prefix implementation
adds the same v3 covariates without calling candidate feature code.

The nonnegative coefficient does not universally exclude positive endpoint
artefacts after survival selection. The exact counterexample retained in
`data/provenance/a10d_design_calculations.json` has constant true duration,
a positive fixed-baseline offset, and positive conditional forecast gain.
It is a counterexample to a general claim, not an estimate of SS Cyg bias.
Similarly, a more recent duration can beat its lagged value under a shared
slow state: the lagged-duration comparator does not identify direct memory.

Pre-freeze review caught a slow renewal-clock defect and repaired it with
an exact following-gap chronology regression. The initial slow development
outputs are superseded. Receipt binding now hashes/parses the same bytes,
validates stage/namespace/source/input contracts, and checks the concordance
receipt and records unchanged at completion. A second bounded independent
review verified both repairs in the freeze.

The 296-test suite and repository validator pass locally and on the target.
CI is green on the freeze. Fresh production concordance matches exactly on
100 histories at both delays (15.91 seconds). Development score checks on
6,934 rows agree to less than 8e-14, with the pre-fix slow rows superseded.
The corrected three-history smoke passes in 235.82 seconds. All 6,766
corrected smoke scores independently agree within 1.1e-13, including the
protocol exclusion of ambiguous-survival evidence. The forced six-reference
smoke passes in 501.20 seconds. Production numerical/aggregate checks are
reported above. The completed grid takes 2,179.24 seconds with 48 workers
and numerical-library threads fixed at one.
The reporting checkout passes 299 tests, including regressions for the
independent calculators, and the repository validator. Temporary compute
resources have returned to their standing allocation; the archive is intact.

## Inference and scope

The six-year cluster width was chosen before OC outcomes; three-year
results remain a sensitivity. Exact-zero fits cannot confirm. The null and
alternative references use six independent matched 58-year records with
finite-reference uncertainty propagated; these are joint Monte Carlo checks,
not coverage against exact conditional truth. Overall and interior-fit
coverage are reported separately.

All waveform/cadence inputs retain the pre-1960 frozen benchmark anchor.
V4 is an unqualified waveform sensitivity. Slow-state cases describe what
positive predictive skill can mean, and are not false-positive gates for a
forecast-information claim. Every other null, including v4, is screened.

The observed ≤5% screen and a formal upper-bound certificate are both
computed. Counts of 40/20 cannot certify a true ≤5% rate even at zero
rejections. Barry's interpretation question was raised before outcomes;
no automatic real-fit action is part of the runner.

The chronological information set uses observation times. The archive does
not supply historical publication availability dates, so any eventual real
evaluation is observational-time retrospective, not an operational replay.
The fitted timing baseline is q plus local gap history, not an identified
physical state model. This tranche does not infer missed events or fit a
physical disc model.

“Per issuance” refers to every score-eligible issuance, retaining literal
fallback zeros. The pre-existing truth-free evidence rule marks ambiguous
survival as excluded: those issuances remain in the ledger and evidence
counts but cannot enter this conditional-survival score. No exclusion is
based on duration sign, gain or simulated truth. The compact report preserves
issued counts, scored counts and evidence-reason totals separately.

Independent calculator development also caught checker errors in excluded-
evidence populations, exact-zero routing and one-sided binomial inversion.
The corrected score calculations and reference algebra were verified against
completed synthetic fixtures; all 62 binomial upper bounds at n=20/40 were
checked against base R quantiles to less than 3e-16. These corrections do not
change the frozen forecaster or the prespecified OC calculations.

## Reproduction and retained evidence

Generate in an isolated clean checkout of `8f5df44b950ec5781ba1e31e074e56976909a051`,
using the locked analysis environment and the retained anonymous cache
identified by `configs/a04i_inputs.json`. No native observations need to be
opened to repeat the synthetic run. Use a fresh output directory each time:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
uv run --frozen --extra analysis python scripts/a10d_pipeline.py concordance --freeze-commit 8f5df44b950ec5781ba1e31e074e56976909a051 --output outputs/a10d_concordance --workers 24
uv run --frozen --extra analysis python scripts/a10d_pipeline.py oc --freeze-commit 8f5df44b950ec5781ba1e31e074e56976909a051 --concordance outputs/a10d_concordance/receipt.json --output outputs/a10d_oc --workers 48
```

The reporting checkout contains the corrected independent calculators. Point
them at the completed or restored OC directory:

```bash
python scripts/check_a10d_aggregate.py --directory outputs/a10d_run_8f5df44/a10d_oc --output outputs/a10d_aggregate_check.json
python scripts/report_a10d.py --directory outputs/a10d_run_8f5df44/a10d_oc --output outputs/a10d_public_report
```

[The compact report](../../data/simulations/a10d_20261108/report.json),
[all comparisons](../../data/simulations/a10d_20261108/comparisons.csv),
[generation receipt](../../data/simulations/a10d_20261108/run-receipt.json),
and [independent audit summary](../../data/provenance/a10d_audit_checks.json)
are committed. The latter binds the corrected calculator bytes by SHA-256.
The full regenerable payload and audit sources stay outside Git in archive
`a10d-20261108-8f5df44`: 757 files, 605,168,799 bytes. Its inventory SHA-256 is
`b9adb18748225e81cd679362f8f0ee3d0ea595503554e085544b91e8e00f4c4d`.
No model or inferential rule was tuned after the production outcomes.
