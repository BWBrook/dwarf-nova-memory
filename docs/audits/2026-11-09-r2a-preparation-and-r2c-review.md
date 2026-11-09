# R2a/c: completed preparation, corrected assumptions and precision limits

Codex, 9 November 2026, base `03f4cf8`. The amended preparation protocol is
`docs/protocols/r2-design-v1.md` (D036). Protocol/X5/power freeze `fe6dbf4`;
timing-model control freeze `f0049dd`; causal-feature freeze `956d33c`.
All batches below ran after their relevant source/configuration commits.

**R2a and R2c are complete. No new real-data R2b model fit, forecast gain or
duration–gap correlation was computed.** All actual observations read were
already opened SS Cyg rows before 2018. New-star work used dated catalogues and
primary literature, without observation-archive requests or coverage/count
queries. Product texts and PDFs stay unchanged. Original scientific sources,
parameters, protocol and execution receipts are preserved.

## Amendments needed before implementation

The [independent design review](2026-11-09-r2-design-review.md) accepts the
resolved-event inf/sup bound and the formal normalized CAR theorem. It corrects
their application:

- Containment also requires episode association, completeness, a crossing
  convention and a valid risk set (A0), plus measurement/aggregation assumptions
  (A1). Exact reports can defeat the proposed first-crossing bracket through
  recrossings or representative-visit aggregation. A one-magnitude error is
  not necessary.
- A censored survival contrast is not the unknown event's point-density
  contrast. `r2_scores.py` separates finite resolved-event bounds, fixed-C mixed
  density/survival bounds (including straddles), and the working interval/backoff
  score policy. Deterministic sample ordering does not prove CR1 coverage.
- The full CAR factorization (A2), not a first-detection narrative or a visit-rate
  comparison, is needed for the propriety claim. Contradiction counts cannot
  estimate failed-bracket probabilities without a measurement/association model.
- An observed faint clock removes numerical end-estimate reuse, but not
  cadence-dependent origin error or selection. An invented exact-report example
  with constant true duration and independent future gaps yields **+0.0539543
  nats** from bright span alone, with no estimated end anywhere. Parent
  Gauss–Legendre integration of independent density ratios reproduces the
  closed-form expectation within 5.76e−16. This counterexample is not real SS Cyg
  evidence; it invalidates DF's proposed status as a decisive mechanism test.

The original v0 remains intact. The interpretation specification now names
these limits. No automatic “E1 closed”, mechanistic retention-ratio gate or
unconditional “proper latent score” claim survives in v1.

## X5 gain-free report-window diagnostics

The additive X5 module preserves X4 candidates and fitted points. Corrected
decisive windows include limits, start after reported quiescence and use
conservative raw visit supports, with representative bounds retained separately.
Faint peaks have no substituted upper bound. Temporal overlaps, contested
epochs and decisive-faint recrossings have explicit eligibility flags.

| Whole opened record, confirmed episodes | Result |
|---|---:|
| Confirmed episodes | 845 |
| Finite onset-report windows | 818 |
| Eligible onset-report windows | 805 |
| No preceding decisive quiescence report | 4 |
| No decisive bright peak | 23 |
| Contested-epoch / rise-recrossing flags | 3 / 10 |
| Raw-support width, median / 90th percentile | 1.1495 / 4.6571 days |
| Fraction at most two days | 68.58% |
| Available old X4 point outside the new window | 77 |

The last row is geometric disagreement, not a truth-error estimate. The 818
available windows restore a feasible outcome comparison; they do not prove
latent containment. In particular the original X4 point estimates have not
been repaired or moved inside the new report windows.

Across selected windows the representative-time observer-visit rate is 7.122/day
in the preceding five days, 4.959/day including U and 4.336/day strictly inside.
These selection-conditioned summaries do not establish or reject CAR or identify
an alert policy. The near-threshold timing summary starts at selected Q and can
include earlier tail behaviour; it is not a verified alert-trigger time.

Opposite decisive reports from another observer within 0.5 day occur for
388/255,647 decisive visits (0.1518%). The selected clear plateau/quiescence
strata give 0/24,375 and 0/157,294. Genuine rapid changes, shared bias, selection
and errors around transitions prevent translating those rates into a global
error probability or an expected count of failed onset bounds.

## Causal observed-clock preparation changes the population

DF waits for the selected one-magnitude-faint visit to close; it never borrows
a future anchor at the old issue. A renewed threshold-bright report aborts the
pending issue. DF uses only closed visits, raw candidate association and raw
observer counts, with no interpolated end or fitted single-observer confirmation.
Poisoning all fitted boundary fields leaves DF fields unchanged in synthetic
tests. Already-issued features are invariant to arbitrary later reports.

| Actual-issue period | Original point issues | Matched DF and point issues | DF anchor+gap+mark | Both clocks anchor+gap+mark |
|---|---:|---:|---:|---:|
| 1910–1959 | 330 | 302 | 251 | 249 |
| 1960–2017 | 441 | 307 | 292 | 291 |

There are 828 original and 663 matched issues across the whole opened record.
The scheduling rule aborts 165 pending issues, including 28/330 original
development issues and **134/441** original evaluation issues. These are bright-
report triggers, not identified physical outbursts. This change cannot be
hidden inside a comparison with the original 441-forecast mean.

Median delay is 0.256 day overall, zero in development and 0.720 day in evaluation;
413/663 issued DF forecasts are delayed. Current scheduled anchors (after the
last causal bright report) and historical X5 first-postpeak faint anchors differ
in 12/651 comparable cases, including seven development and five evaluation
cases, by up to seven days. This is a declared working-clock asymmetry, not a
validated renewal-gap definition. The R2b execution review must predeclare
whether to harmonize those clocks or retain and label the sensitivity.

The limited `flux_proxy` uses positive closed observer visits, balanced by
observer-night and night, and integrates threshold-excess flux only between
observed bright-span points. It is not complete outburst/quiescent-subtracted
fluence, bolometric energy or disc mass. Missing support and gaps over seven
days give explicit unavailable statuses. It is available for 287 development
and 303 evaluation DF issues; the matched point/DF proxy dictionaries are
identical. The DF anchor+gap+proxy intersection is 250 and 292, respectively.

All histories retain consecutive candidate-gap placeholders and never join
across unconfirmed/uncovered candidates. As-of-current-issue values are not
claimed to be the exact values available at earlier historical dates. The
parent validated all 828/663/663 feature records against the model input schema
without evaluating a real forecast distribution. No raw event or per-issuance
table is published.

## B0/B1/B2 implementation and synthetic controls

`r2_models.py` implements the newly fitted B0 timing form, B1 two-lag/EWMA
profiles and a windowed two-state B2 filter. B2 propagates predictive covariance
and missing steps; duration never alters its timing-state updates. All rungs
use the same stricter history and common missing-clock/gap fallbacks. Positive
mark offsets hold timing parameters and variances fixed. Zero offsets and
missing marks return the base exactly. This is not the original frozen M2.

The independent pre-run review caught and fixed semantic availability guards:
NaN timestamps and outcome support later than declared availability are now
rejected before optimization. B1 lambda zero duplicates the second-lag column;
every profile reports design rank rather than implying identified coefficients.
All-censored timing training fails explicitly. Optimizer success is not a
calibration or parameter-identifiability certificate.

All nine frozen control histories complete, with 120 development and 120 later
forecasts each. Three stationary controls give zero mean duration gain for all
rungs. Three drifting controls give zero for B0/B1 and −0.000110 for B2.
Direct-duration controls give mean gains +0.02434, +0.02796 and +0.03140 for
B0/B1/B2. Three histories per setting are implementation checks, not an
operating-characteristic screen or evidence that a rung dominates in SS Cyg.

An independent checker replaces B2's recursion with joint Gaussian conditioning
and independently reconstructs B0/B1 covariates and SciPy density/survival scores:
6,480 evaluation scores agree within 2.49e−14; 3,240 paired gains within
4.89e−15; 14,661 mixed training-score terms reproduce objectives within 1.71e−12.
There are 3,240 zero-counterfactual checks and 2,220 exactly equal saved
zero/missing pairs. It does not prove optimizer global optimality or physical
calibration. Source book identity/hash is recorded; no copyrighted PDF/text is
redistributed.

## R2c: cohort proposals and precision remain conditional

The [R2c report](2026-11-09-r2c-cohort-power.md) supplies sixteen screened
nomination/control/exclusion rows from identified 2006/2015 catalogues and
primary literature. The ordinary development-feasibility queue is SS Aur,
RU Peg, AR And, X Leo, TW Vir, UU Aql, CH UMa and DX And. U Gem/IP Peg are held
for eclipse/subtype review. These are nominees, not eight eligible stars.
Thresholds are source-specific catalogue proposals, not calibrated visual
extraction constants. SS Cyg's midpoint ten is defensible with the named range;
an eclipse-contaminated or photographic range cannot silently be substituted.

The proposed 1990–2025 test spans 36 calendar years, not 35. Published studies
already expose parts of those years; the exposure ledger prevents a future
claim of complete outcome ignorance. Ak2002's parsed primary text was read but
the raw download timed out, and some exact study spans remain unresolved.

All 35 frozen score-level scenarios (2,000 replicates each) complete once.
At nominal individual-oracle gain 0.010 and N=1,100, the fitted rule achieves
mean gain about 0.00903 and power **0.711 [0.691,0.731]**. At N=1,600 power is
0.8005 [0.7823,0.8178]; N=2,200 gives 0.863. These exact binomial intervals
describe Monte Carlo uncertainty, not assurance of real-world power.
Within-block dependence reduces N=1,100 fitted power to 0.3945. Serial-block
dependence yields 0.450 power but only 0.7265 nonidentity 90% interval coverage.
Identity-zero fits inflate overall coverage. Consequently G2 is **not
established**, and star-by-block CR1 cannot simply be carried into the sealed
test as a validated uncertainty procedure.

The parent independently streamed all 70,000 saved trials and reproduces all
70 scenario/rule count, coverage and identity rows; maximum mean discrepancy
is 3.13e−17. This verifies aggregation, not the realism of the DGP. The study
does not implement X5, photometry, missing events, qualification, censoring,
state-filter learning or estimated variance. No scoreable archive count was
measured. Eight nominees and 1,100 hypothetical forecasts do not establish a
powered cohort or authorize G3.

## Reproduction and next review

Aggregate evidence is in `data/provenance/r2a_preparation/`,
`data/provenance/r2_design_audit/` and `data/provenance/r2c_catalogue_power/`.
Raw retained observations, per-issue ledgers, papers/catalogue responses and
full simulation streams stay ignored. Each runner refuses occupied output
directories and binds its relevant committed sources/configuration.

```sh
.venv/bin/python scripts/r2a_observation_diagnostics.py --freeze-commit fe6dbf4 --output outputs/r2_x5_reproduction
.venv/bin/python scripts/r2a_feature_preparation.py --freeze-commit 956d33c --output outputs/r2_features_reproduction
.venv/bin/python scripts/check_r2a_feature_counts.py --features outputs/r2_features_reproduction --output outputs/r2_population_recount.json
.venv/bin/python scripts/r2a_model_controls.py --freeze-commit f0049dd --output outputs/r2_models_reproduction
.venv/bin/python scripts/check_r2a_model_controls.py --run outputs/r2_models_reproduction --output outputs/r2_model_scalar_check
.venv/bin/python scripts/r2c_power.py --freeze-commit fe6dbf4 --output outputs/r2_power_reproduction
.venv/bin/python scripts/r2_design_counterexamples.py --output outputs/r2_math_reproduction
```

Claude's R2d review should settle the clock/history convention, matched real
R2b population, latent association/recrossing assumptions and inference/precision
plan before the real exploratory scoring freeze. Future G3 must name the actual
cohort and development-only qualification, not infer them from catalogues.
No new decision or archive opening is requested from Barry at this stage.

Claims C47–C52 record these new results as provisional pending Claude's review.
The independent delegates changed the design's interpretation and exposed
availability guards before execution; their numerical checks and the parent's
recounts are retained separately from the candidate implementations.

Local verification: all 465 unit tests pass, along with the structural validator,
claims/product checks (zero errors) and numerical seed reproduction. All 26
qualified original forecasting sources and the parameter hash still match their
receipts. Product text sources and all three PDF bytes match `03f4cf8`. No new
PDF render was needed because those products were not edited. These checks do
not turn the synthetic controls into scientific calibration.
