# R2b: observed clocks and stronger timing baselines

Codex, 9 November 2026, base `ced0413`. D039 amends Claude's R2b v0;
D040 resolves one coincident delayed issue before any actual fit. The first
source freeze is `939208e`; the execution freeze is `5fb69c6`, under
`docs/protocols/r2b-execution-v2.md`.

All actual work uses retained, already opened SS Cyg observations before 2018.
Training issues are 1910–1959; evaluation issues are 1960–2017. These are
post-result exploratory comparisons. They cannot become another confirmation.
No new archive request, other-star observation/count/coverage query, protected
2018+ observation, outside contact or manuscript release occurred. Product text
sources and PDFs are not rewritten.

## What changed before fitting

The [independent contract review](2026-11-09-r2b-pre-execution-review.md)
accepts the proposed last-upcrossing target but rejects three stronger claims:

- Exact report magnitudes and broad raw supports do not prove containment.
  A faint median visit can obscure a decisive bright report inside its support.
  Correct episode association, ordering and A0/A1 remain assumptions.
- The Fisher expansion is not a cadence ceiling. For an invented lognormal
  with median forty days, scale .4, issue age two days and a one-day additive
  anchor shift, independent integration gives KL .003247108449, exceeding
  the local quadratic .003120055091. A support shift can give infinite KL.
  Conditioning and older-history errors create additional omissions. The
  reported one-lag indices have no mechanism-exclusion interpretation.
- The observing-rate proxy uses a duration-dependent bright span. It is an
  observing-intensity sensitivity, not a validated negative control. Neither
  its positive gain nor a zero constrained coefficient identifies cadence.

H1–H3, model forms, bounds, starts, mark restrictions and score policies were
fixed before fitting. Timing models use all declared multistarts; their
statuses/objectives remain visible. A failed or disagreeing start is not
hidden behind a successful best fit. The constant/remaining fallbacks and
missing-mark routes remain common to both arms.

## Preserved preparation failure and unique issue convention

The first gain-free actual preparation at `939208e` stopped before creating
feature ledgers or fitting models: two original confirmations shared the same
delayed DF time and faint support. Independent reconstruction found one such
pair, in the evaluation period, among 828 original confirmations. The weaker
re-confirmation has eleven threshold-bright reports, none decisive bright.
This is a report/issuance pattern, not adjudication of physical outbursts.

D040 retains the earliest original representative only when issue, anchor,
raw-support start and availability match exactly. Later originals stay in the
audit as `coincident_pending_issue`; they are not extra forecasts. Other
ordering errors still raise. This rule was chosen using no fit or gain.
The alternative latest representative would replace the initial causal bright
phase with a short weak re-confirmation. A general supersession rule was not
introduced. Frozen C01 retains its original 441-issuance denominator.

The failed receipt is preserved alongside the original v1 protocol/source.
The v2 rehearsal reproduces v1's fitted synthetic parameter bytes exactly.

## Prepared populations and anchor provenance

| Period | P-orig | P-DF / P-match | DF anchor+gap+duration | Jointly markable clocks |
|---|---:|---:|---:|---:|
| 1910–1959 | 330 | 330 | 275 | 273 |
| 1960–2017 | 441 | 440 | 418 | 417 |

All 440 evaluation DF issues have an available model anchor; 328 development
issues do. Median DF issue delay is .10 day in development and .90 day in
evaluation. Two development rows use the exact common fallback.
These are scheduled populations, not yet a statement about outcome support.

The independent saved-vector checker verifies 147,696 invariants, all receipt
hashes, exact DF/P-match issue pairing and 815 comparable current-own anchors
with zero discrepancies. All 6,039 historical anchor links agree with earlier
scheduled anchors and availability. Ninety-one historical slots, including
eight measured gaps, refer to a past feature whose model clock fell back. They
match the immutable **scheduled observed anchor**, not an earlier usable model
clock. Current-prefix retrospective association can become available later.
Historical onsets/gap measurements are reconstructed at each current issue;
they are not claimed immutable operational measurements from earlier dates.

## Results

**All three headline contrasts are inconclusive.** H1 and H2 have positive
estimates, but both six- and twelve-year 90% intervals cross zero. H3 also
crosses zero: there is no clear paired evidence that incremental gains differ
between clocks. This does not erase the original C01 result or establish an
absent effect. No secondary replaces these frozen headlines.

| Contrast | Scored / scheduled | Gain (nats) | Six-year 90% interval | Twelve-year 90% interval |
|---|---:|---:|---|---|
| H1: original-issue point, B2 duration | 432 / 441 | +0.007535 | [-0.000821, +0.015891] | [-0.001444, +0.016515] |
| H2: observed clock, B2 duration | 431 / 440 | +0.004276 | [-0.000848, +0.009401] | [-0.002109, +0.010662] |
| H3: DF gain minus matched-point gain | 431 / 440 | -0.003076 | [-0.007844, +0.001692] | [-0.007846, +0.001694] |

Each delayed-clock analysis has 427 interval outcomes and four working censors;
nine scheduled outcomes are unsupported (eight flagged candidates and one
faint peak). P-orig has the same 427 interval outcomes and five working censors.
Training uses 306 supported outcomes from 330 issues: 291 intervals and fifteen
censors; twenty-four are excluded. Missing outcomes do not contribute empirical
zeros. Six-/twelve-year summaries use ten/five nonempty blocks.

H2's deterministic mixed sample envelope is [0.0009703, 0.0077535] on its 431
supported cases. Its positive lower mean is conditional on A0/A1 and genuine
survival through the selected cutoff. It is not a confidence limit, a
containment validation, or a general future latent-score claim. H3's
difference-of-marginal-bounds envelope spans zero.

### Secondary contrasts and baseline adequacy

| Clock | B0 duration gain | B1 duration gain | B2 duration gain |
|---|---:|---:|---:|
| Original point | +0.018432 | +0.021249 | +0.007535 |
| Observed DF | +0.008444 | +0.011042 | +0.004276 |
| Point at DF issue | +0.018138 | +0.020877 | +0.007353 |

The B0/B1 point-clock duration contrasts are positive under both blockings;
their DF contrasts are inconclusive. These are secondary comparisons, not an
alternative primary success. The smaller B2 gain does not identify a slow state.

B2 is the **preselected state-space comparator**, not the empirically strongest
baseline. All B2 timing starts converge, objective spreads are below the frozen
stability tolerance, and no B2 parameter is on a declared boundary. But its
development likelihood is lower than B0/B1, and descriptive evaluation baseline
means are also lower within every clock. On DF, mean base scores are −3.679437
(B0), −3.688352 (B1), and −3.696225 (B2), on identical supported cases. These
post-run mean aggregations were independently recounted; no statistical
dominance test or model selection is claimed. H1–H3 remain unchanged. Future
design review must address baseline adequacy explicitly rather than call B2
strongest or silently switch after seeing gains.

The B2 observing-rate sensitivity gains +0.003044 [0.001252, 0.004835] under
six-year blocking and [0.001255, 0.004832] under twelve-year blocking. Observing
intensity carries information under this working rule; its duration-dependent
span prevents attributing that information exclusively to cadence. DF-c gives
+0.004278, essentially the same point estimate as H2, but a single gap
covariate cannot eliminate all observation pathways. The DF flux-proxy gain
is +0.001716, with both intervals crossing zero.

Admitting available flagged windows yields DF B2 gain +0.004040 on 438 scored
issues, again with an interval crossing zero. The one-lag B2 index is available
on 419 issues (mean 0.009635, median 0.001089); it remains a local approximation,
not a bound to compare with H2.

DF B2 evaluation midpoint residual proxies have block ICC −0.021794, block-mean
lag-one ACF 0.228132 (nine pairs), and issuance lag-one ACF 0.011062. The
H2 gain block-mean lag-one ACF is 0.015481. These noisy, differently conditioned
diagnostics do not establish independent future star blocks or calibrate G2.
The predeclared planning-effect rule would use H2's estimate (about 0.00428),
below 0.010, with its large uncertainty. No new sample-size or power claim is
made here; R2d must carry that uncertainty into planning.

## Verification and limits

The bounded raw-report rehearsal generates seventy synthetic episodes, spanning
training and evaluation across the 1960 split; it does not reproduce the full
58-year evaluation calendar or validate an astronomical DGP. Independent direct
Gaussian conditioning replaces the B2 recursion; scalar SciPy probabilities
replace candidate scoring. The v2 rehearsal checks fourteen models, 2,072
base/marked scores, seventy development-objective components, mixed extrema,
H3, routes/identities and six-/twelve-year aggregation. Maximum score error is
1.07e-13; maximum objective error is 9.95e-14.

The actual independent reconstruction passes all fourteen models, 24,348
base/marked working scores (including flagged sensitivities), seventy
training-objective components, fixed-C extrema, H1–H3 and both block summaries.
Maximum score error is 5.47e-13; objective error 9.09e-13; prediction error
4.00e-15; bound error 3.55e-15. It verifies 12,328 zero counterfactuals and
358 saved exact identities. All six development-ledger hashes and the local
parameter lock agree. These counts are numerical checks, not extra unit tests.
All 516 unit tests pass locally and on the source-freeze CI matrix.

The actual pipeline writes all model parameters and a local immutable
`parameter-lock.json` before evaluation scores, and verifies their bytes later.
The lock records execution order and hashes; it is not an independent external
timestamp or a new preregistration. Every individual feature/evidence/score
table remains ignored and unreleased. Aggregate evidence, source identities
and reproduction commands are in `data/provenance/r2b_20261109/`.

Numerical agreement does not establish global optimizer optimality, parameter
identifiability, measurement calibration, CAR, completeness or latent containment.
Working selected-observation cutoffs are not independent administrative censors.
The deterministic mixed bounds and working interval/backoff score remain
different objects. Unsupported outcomes are excluded equally from empirical
score comparisons; known identity zeros are reported separately.

Six-/twelve-year intervals are exploratory dependence sensitivities, not
validated coverage. Midpoint log-residual ICC/ACF are measurement/selection-
conditioned proxies, not latent error correlations. Eighteen-year or whole-star
clustering needs a prospective uncertainty/stress envelope before G3; a
simulation at a single estimated dependence value cannot certify coverage.
The catalogue nominees remain unqualified, and G2 remains open.

## Reproduction and next review

Use the project Python environment and new output directories:

```sh
.venv/bin/python scripts/r2b_execute.py --mode rehearsal --freeze-commit 5fb69c6 --output outputs/r2b_rehearsal_reproduction
.venv/bin/python scripts/check_r2b_execution.py --run outputs/r2b_rehearsal_reproduction --output outputs/r2b_rehearsal_check
.venv/bin/python scripts/r2b_feature_preparation.py --freeze-commit 5fb69c6 --output outputs/r2b_feature_reproduction
.venv/bin/python scripts/check_r2b_features.py --features outputs/r2b_feature_reproduction --output outputs/r2b_feature_check
.venv/bin/python scripts/r2b_execute.py --mode real --freeze-commit 5fb69c6 --features outputs/r2b_feature_reproduction --output outputs/r2b_real_reproduction
.venv/bin/python scripts/check_r2b_execution.py --run outputs/r2b_real_reproduction --allow-real --output outputs/r2b_real_check
```

The actual-data commands require the retained acquisition/cache; no download
or protected-period access is implicit. Claude should independently review
the results, remaining measurement assumptions, development stability and the
R2d precision/dependence design before any G3a request or product rewrite.

New claims C53–C60 remain provisional pending Claude review. The numerical
audit is independent; scientific interpretation and future design still need
that review. No model or primary contrast was selected by these gains.

A separate semantic review checked the report, README, D041 and C53–C60 against
the aggregate evidence and v2 rules. It found no numeric/denominator, CI/bounds,
mechanism or strongest-baseline conflation. Its requested C54 wording correction
was applied: historical anchors are scheduled observations whose source emission
may have used a fallback model, rather than anchors supplied by that fallback.
