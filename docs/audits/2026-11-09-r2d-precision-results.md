# R2d: arithmetic accepted, robust multi-star precision not established

Codex, 9 November 2026. Base `6a94c9d`; source/configuration freeze
[`67c45ab`](https://github.com/BWBrook/dwarf-nova-memory/commit/67c45ab218e5fe089b49e5178cf53c8c0c638681).
Decision D043; protocol [R2d v1](../protocols/r2d-sealed-design-v1.md).
No new archives or observational fits. All paper products remain paused.

## Independent review of C61–C64

A bounded delegate reconstructed conditional interval/survival probabilities,
truncated-normal score moments and direct joint-Gaussian development predictions
from retained R2b forecasts, without importing either the candidate or Claude's
checker. Fourteen models match; largest guarded-gain discrepancy 6.15e-15,
score-statistic discrepancy 7.81e-12 and development-NLL discrepancy 7.96e-13.
[Summary](../../data/provenance/r2d_review_audit/summary.json) and
[receipt](../../data/provenance/r2d_review_audit/receipt.json) record inputs,
source hashes and limits. Parent checked the key interpretations and numerical
summaries. C61–C64 now support the arithmetic with these amendments:

- **C61:** B2 has lower development likelihood and held-out baseline means.
  This is not a prespecified adequacy rejection or a unique diagnosis of the
  physical gap process. Covered measured gaps show a level shift; its physical
  versus observational origin is unresolved.
- **C62:** changing the base and mark together attenuates several gains. This
  does not uniquely allocate gain to an era effect, and no fraction of C01 was
  measured. C01 remains its frozen working-score result.
- **C63:** the guarded observing-rate estimate remains positive and inconclusive.
  Significance labels do not test a difference between predictors. Contrary to
  the previous ledger limitation, point-original B0's duration interval is
  positive under both blockings; DF B0/B2 remain inconclusive.
- **C64:** the local ratio arithmetic reproduces, but the same evaluation score
  and curvature enter both sides. Agreement is a Taylor check, not independent
  prospective power evidence or a universal efficiency theorem.

The historical guards kept unguarded development beta, used evaluation-only
recalibration and final saved labels at proxy resolution times. Simple .15-day
closure and seven-day censor-recognition delays change no update sets here;
they do not reconstruct confirmation/association/flag availability. Those
diagnostics are not an executed replay of the new R2d rule.

## What changed before running

An independent methodological delegate read v0, primary methodological sources,
and the new helper/runner/configuration. The
[design review](2026-11-09-r2d-design-review.md) and five reproducible invented-
number checks establish three distinctions:

1. A positive score moment can coexist with negative gain of the frozen
   development-trained forecast. Forecast gain remains the default claim under
   D018; a switch to association needs an explicit scientific choice.
2. Rolling mark and level corrections leave aligned trends and can introduce
   score dependence. They do not exclude slow shared causes.
3. Whole-star sign flips have minimum p = 2^-S; three/four stars cannot reject
   at 5%. Mean per-star oracle KL with opposing signs is not pooled signal.

A third delegate built the additive Gaussian point-log-gap helper and focused
tests without real-data inputs or Monte Carlo grid outcomes. The parent built
the runner and fixed grid, reviewed the helper, and froze them before execution.
The independent review saw both the real-data summary and new implementation;
its independence rests on separate derivations/checks, not withheld project
conclusions. No claim of blind design is made.

## Precision screen

All **35 cases × 2,000 trials = 70,000** completed, with zero failed fits,
from deterministic individual seeds. Four local M4 workers took 107 seconds.
Full synthetic trial lines remain ignored under `outputs/r2d_precision_67c45ab/`;
the [aggregate](../../data/provenance/r2d_precision/summary.json),
[receipt](../../data/provenance/r2d_precision/receipt.json) and fixed
[design](../../data/provenance/r2d_precision/design.json) are public.
No method was selected or tuned on these outcomes.

The following are **whole-star CR1/t** rejection frequencies under positive
direct effects; 95% intervals quantify Monte Carlo uncertainty in each frequency.
They do not cover uncertainty about the real astronomical process.

| Case | Test forecasts | Forecast-gain rejection | Score-moment rejection |
|---|---:|---:|---:|
| Four stars, clean | 1,100 | 28.1% [26.1, 30.1] | 65.6% [63.5, 67.7] |
| Eight stars, clean | 1,100 | 36.7% [34.5, 38.8] | 81.8% [80.0, 83.5] |
| Eight stars, clean | 2,000 | 51.0% [48.8, 53.2] | 94.9% [93.8, 95.8] |
| Eight stars, imbalanced/heterogeneous/history-correlated marks | 1,100 | 28.8% [26.8, 30.8] | 54.8% [52.6, 57.0] |
| Eight stars, persistent/small development/missing marks | 1,100 | 24.3% [22.4, 26.2] | 63.6% [61.4, 65.7] |
| Eight stars, common states/noisy marks/delayed labels | 1,100 | 12.5% [11.0, 14.0] | 38.7% [36.6, 40.9] |

The clean eight-star score cell narrowly clears an 80% lower Monte Carlo bound
(unrounded 0.800378). The stress cases do not. No tested core forecast-gain cell
reaches 80%, even with 2,000 forecasts. The .004 nominal individual latent oracle
signal is reduced by learning and guards: the eight-star clean 1,100 case has
mean predictable frozen-rule gain .003397, versus .000313 in the delayed/noisy
case. These are path-average generator targets, not long-run population KL.
Counts in the table are total test issuances, not guaranteed mark-supported
forecasts. The persistent and delayed eight-star cases average 880 and 654
mark-supported forecasts respectively; no additional draws compensate for those
losses. The imbalanced case retains all 1,100 but changes effect heterogeneity
and weighting (mean individual nominal oracle gain .00523). These cells do not
estimate power at an identical achieved effect or identical supported count.

**Null and coverage screens.** Under the four strict oracle predictive nulls,
whole-star forecast-gain rejection is 0.75–1.00%; score rejection is 4.65–5.55%.
For the 5.55% score cell the exact Monte Carlo interval is [4.59, 6.65]%, which
includes 5%. Nevertheless it misses the frozen observed-rate ≤5% screen.
Neither half-cluster nor sign-flip score procedures pass that point-rate screen
across all strict-null cells either. This is not proof of an anti-conservative
true rate, and no procedure is certified at 5%.

Across all cases, whole-star nominal 90% gain coverage conditional on nonzero
offset ranges 88.9–98.6%; corresponding half-cluster coverage ranges 88.7–97.0%.
Exact Monte Carlo intervals and identity counts are reported per case. Coverage
is of a **realized-path predictable gain average** under the generator, not a
general interval for astronomical population gain. Exact-zero fitted offsets
are reported separately rather than inflating the nonidentity coverage claim.

Estimated-base/no-direct-effect cells are not automatically predictive nulls:
a proxy can genuinely improve an estimated or misspecified base. For example,
the imbalanced/history-correlated-mark no-direct-effect case gives score
rejections of 7.2–7.7% under whole-star CR1. This diagnoses the limitations of
the working moment/comparator, not a universal physical-memory false-positive
rate. It motivates neither relabeling those cells nor dropping them.

## Why changing the statistic changes the claim

With an effect four times stronger in development than evaluation, the score
test rejects in **74.85%** of five-star trials, while mean realized gain is
**−.02858 nats** and the frozen gain test rejects in .05%. Every trial's
predictable score expectation is positive and predictable gain negative.
That is direct evidence against reading association power as confirmation of
this trained forecast's improvement. It does not invalidate the score moment
as a test of its own working association.

The slow shared-state case has **no direct mark effect**, yet mean gain is
+.002575 nats and whole-star gain/score rejection frequencies are 30.5%/66.45%.
This is genuine incremental prediction over the specified imperfect base;
it demonstrates the continuing lack of physical specificity after the guards.
The shared-trend and joint-shift cells are also retained, whatever their
aggregate sign. All are exploratory synthetic counterexamples, not inferred
causes of SS Cyg's result.

## Verification and next decision

Independent aggregation and four same-seed vector reconstructions are recorded
in `data/provenance/r2d_precision/independent-check.json`. The vector
audit is a numerical reconstruction of retained synthetic seeds, not a second
precision study. It checks Gaussian densities, generator predictable targets,
weights and cluster/sign-flip arithmetic without importing the candidate.

Preservation checks find no changes to the original 26 forecasting sources,
original parameters, R2b sources/outputs or manuscript product text; hashes are
in [preservation.json](../../data/provenance/r2d_review_audit/preservation.json).
Only interpretation/claims/status records, additive synthetic tools and small
aggregate evidence changed. No new-star yield or coverage was measured.

**CI-only amendment:** the original source-freeze CI run
[42614727569](https://github.com/BWBrook/dwarf-nova-memory/actions/runs/42614727569)
failed one new permutation test on Python 3.11: exact dictionary equality
compared 1.4999999999999998 with 1.5. Commit `3e195a5` changes floating fields
to a 1e-12 assertion tolerance, keeping discrete fields exact. It changes only
that test, after the grid; helper, runner, configuration, protocol and outcomes
remain byte-identical. The independent audit records the test-only checkout
drift against the original frozen receipt. Reproduction below uses the equivalent
test-repaired freeze; the original `67c45ab` checkout remains available unchanged.
The final claims check also exposed a numeric-token bug: a hexadecimal checksum
beginning `71e959…` was parsed as an enormous exponent, overflowing Decimal and
potentially supplying spurious numeric evidence. `tools/claims.py` now requires
an ending word boundary; a focused regression retains decimal/exponent/comma
numbers and rejects the checksum. Existing product bindings still pass.

**R2d does not establish a robust required N.** Increasing N alone cannot cure
inadequate development learning, a weak comparison, too few stars, or a change
in the claim. The point-Gaussian screen omits extraction, window scoring,
endogenous observing and actual calendar yield. Do not promote its clean-cell
power to an observational design guarantee.

Claude should independently review these findings and settle what a new-star
study can claim before bringing Barry a concrete G3a early-record feasibility
proposal. That opening could be useful without promising 80% power: it would
measure eligibility and development support under a frozen acceptance rule.
Any test-period opening remains a separate decision. Products stay paused.

Reproduction:

```sh
.venv/bin/python scripts/check_r2d_review.py --output outputs/r2d_review_reproduction
.venv/bin/python scripts/r2d_design_checks.py --output outputs/r2d_design_reproduction
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python scripts/r2d_precision.py --freeze-commit 3e195a5 --workers 4 --output outputs/r2d_precision_reproduction
```

Keep every existing output directory; reproduction commands require a fresh path.
