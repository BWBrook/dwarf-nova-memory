# R2b execution rules v0: clocks, populations, crossing convention and uncertainty

Claude (Opus 5.5), 9 November 2026. This settles the four items Codex left open in the
[R2a/c report](../audits/2026-11-09-r2a-preparation-and-r2c-review.md): the clock and history
convention, the matched population, the latent crossing assumptions and the uncertainty and
precision plan. It amends `r2-design-v1.md` for R2b only. Codex amends and freezes it as
`r2b-execution-v1.md` before any real R2b fit. The review behind it is
[2026-11-09-claude-r2a-review.md](../audits/2026-11-09-claude-r2a-review.md); its gain-free
diagnostics are `data/provenance/r2b_claude_rules/checks.json`, produced by
`scripts/r2b_claude_rule_checks.py`.

## 0. Scope and authority

R2b is exploratory scoring on the already opened SS Cyg record: fit on 1910–1959, evaluate
1960–2017. It is not a confirmation and cannot become one. No archive request, no row, count or
coverage summary from 2018 onward, and no other-star data. §6 fixes the sealed multi-star primary
specification now, so that no R2b gain can select it.

## 1. DF clock and history

### 1.1 Abort only on a decisive-bright report

All 165 v1 aborts (28 development, 134 evaluation, 3 before 1910) were triggered by reports
between magnitudes 9 and 10. The brightest trigger had a median of 9.9, and none was at or
brighter than 9. These are reports on the decline tail after the 0.5-mag confirmation. They are
exactly the near-threshold ambiguity that X5's one-magnitude margins exist to exclude. Aborting on
them removed 30% of the evaluation issues, and removed more the denser the observing: a
population change driven by cadence.

Rule:

- the DF issue time is the later of the original emission and the availability of the first
  decisive-faint visit available after the original last threshold-bright time (unchanged);
- abort only if a decisive-bright visit (magnitude ≤ threshold − B) becomes available after the
  original emission and by the DF issue time.

Gain-free result on the opened record:

- 330 of 330 development and 441 of 441 evaluation issues are scheduled;
- the median evaluation delay is 0.90 day;
- no DF issue falls at or after the next onset window's lower bound.

A variant in which threshold-level reports restart the anchor search gives identical counts, so
the simpler rule stands.

### 1.2 Current and historical anchors are the same object

Each past gap on the DF clock runs from that past emission's own scheduled DF anchor (rule 1.1)
to the X5 lower onset support of the next candidate. A past candidate with no scheduled DF anchor
gives an empty (`None`) history slot, and the history never joins across it. Current and
historical anchors are then identical by construction, which removes the 12 discrepancies of up
to seven days. The point clock keeps its X4 histories. The 77 X4 points that fall outside their
X5 windows remain a point-clock limitation.

### 1.3 Cadence gaps, available at issue

- **Anchor cadence gap `c_end`:** the anchor (the last raw time of the anchor visit) minus the
  last raw time of the latest positive estimate brighter than threshold + B before the anchor
  visit.
- **Onset cadence gap `c_on`:** the first raw time of the earliest positive estimate brighter
  than threshold + B after the onset visit L, minus the last raw time of L.

Under exact report ordering, the falling and rising threshold + B crossings lie inside these gaps.

| Gap (days) | Development median (90th percentile) | Evaluation median (90th percentile) |
|---|---:|---:|
| `c_end` | 0.58 (2.05) | 0.10 (0.78) |
| `c_on` | 0.67 (1.98) | 0.33 (0.93) |

## 2. Populations and pairing

| Population | Clock and issue time | Development / evaluation issues |
|---|---|---:|
| P-orig | Point clock at the original emissions (links to C01) | 330 / 441 |
| P-DF | DF clock at the rule-1.1 issue times | 330 / 441 expected |
| P-match | Point clock at the P-DF issue times | as P-DF |

- Every contrast is paired within issue, on an identical set of rows and outcome windows.
- Rows that fall back, because of a missing mark, anchor or previous gap or a failed raw
  association, stay in. They contribute the exact base forecast, so their contrast is zero.
  Report the markable subset beside the full set.
- Cross-clock contrasts compare P-DF with P-match only. The code asserts that each pair of rows
  shares the same issue time and outcome window. P-orig and P-DF differ in issue time and
  survival age and are never compared directly. No retention ratios.
- Each clock is fitted on its own development issues.

## 3. Target, windows and scores

### 3.1 The latent crossing convention

After the previous qualifying outburst's end:

- let τ_B be the first latent time at which m ≤ threshold − B;
- let τ_F be the last latent time before τ_B at which m ≥ threshold + B;
- the target T is the last upward crossing of the threshold in (τ_F, τ_B].

A first threshold crossing on an excursion that never reaches decisive brightness is not a
qualifying onset.

**Containment under exact photometry.** Assume the photometry is exact, and assume A0: no
unobserved excursion to threshold − B or brighter occurs between the previous end and L. The
report at L has m ≥ threshold + B and precedes τ_B, so τ_F ≥ L. The report at U has
m ≤ threshold − B, so τ_B ≤ U. Hence T lies in (L, U], the X5 raw-support window. A1 can then fail
only in three ways:

- A0 fails (a missed or merged decisive excursion);
- a decisive report at L or U is wrong in sign by at least B;
- raw support is misattributed.

On the reviewer's path (0, 11.5), (1, 9.5), (2, 11.5), (3, 8.5), the first excursion never
reaches decisive brightness. Under this convention T lies in (2, 3], inside the window. A0 and
the sign of the decisive reports stay assumptions. Contradiction rates do not estimate them.

### 3.2 Windows

- **Primary:** X5-eligible windows (805 of the 845 confirmed episodes in the whole record).
- **Sensitivity:** windows that are available but flagged (3 contested epochs, 10 rise
  recrossings), scored with their own windows.
- **Unsupported, counted by period:** no decisive-bright report (23) and no decisive-faint report
  before the rise (4).

### 3.3 Scores reported for every contrast

1. The working interval score under v1's policy (the headline score). It is proper for the
   coarsened report only under A2.
2. The A1 fixed-C mixed bounds, reported as the sample means of the lower and upper bounds (ℓ, u).
   These are deterministic.
3. On the point clock only, the point density at the X4 points, for continuity with C44.

### 3.4 Cadence controls for DF contrasts

**Planning ceiling.** For each forecast i, the shift bound is
Δ_i = c_end,i + b_i (c_on,i + c_end of the previous emission). The ceiling is the mean over
forecasts of J_i Δ_i² / 2, where:

- J_i = (1 + σ_i²) exp(2σ_i²) / (σ_i² G_i²) is the location Fisher information of the base's
  lognormal predictive, with fitted median G_i and scale σ_i;
- b_i converts an error in the log previous gap into a time shift: the finite-difference
  derivative of the base's log location with respect to the log previous gap, times
  G_i / g_prev,i.

The ceiling bounds the expected gain from a mark that corrects cadence lags alone. Planning values
at the frozen M2 scale, with b = 0.38:

| Period | Ceiling (nats) | Relative to C01's 0.0165 |
|---|---:|---|
| Evaluation | 0.0071 | about 43% |
| Development | 0.041 | larger than any plausible effect, so uninformative in a sparse era |

This is a planning bound, not a theorem. Its assumptions:

- the small-shift approximation;
- exact ordering of reports at the threshold + B crossings;
- physical rise and decline times that do not depend on the mark beyond physics;
- a correctly specified base.

It does not cover the order-statistic effect, in which many observers' scatter brings the first
faint report earlier. Planning size about 0.001. R2b computes the ceiling for every rung from that
rung's own fitted base.

**DF-c sensitivity.** Both arms include standardised `c_end` as a timing covariate, fitted on
development. The duration offset sits on top.

**Negative-control mark.** The log observer-night rate during the causal bright span: distinct
observer-nights divided by (last bright − first bright + 1 day). It uses the same nonnegative
offset, on B2 and the DF clock. It measures observing intensity, not outburst length.

## 4. Headline contrasts (fixed before any score)

- **H1:** point clock, B2 + D versus B2, P-orig evaluation, working interval score.
- **H2:** DF clock, B2 + D versus B2, P-DF evaluation, working interval score.
- **H3:** the DF gain on P-DF minus the point-clock gain on P-match, paired by issue.

Everything else is secondary or descriptive: the B0 and B1 rungs, the fluence proxy, DF-c, the
negative control, the bounds, point density and the development-fit diagnostics.

## 5. Uncertainty and precision

### 5.1 SS Cyg R2b

- **Reference interval:** CR1 on six-year blocks from JD 2436934.5 (t with 9 degrees of freedom).
- **Companion interval:** CR1 on twelve-year blocks from the same origin (t with 4 degrees of
  freedom).
- **Required diagnostics:**
  - the ten block means;
  - the lag-1 autocorrelation of the block means;
  - the forecast-level autocorrelation of paired gains at lags 1–10;
  - for each rung's base, on development and on evaluation, the block ICC and the block-mean
    lag-1 autocorrelation of standardised log residuals.

Reporting terms:

- "positive under both blockings" only when both lower 90% limits exceed zero;
- otherwise "positive estimate, dependence-sensitive" or "uncertain".

No R2b interval is a confirmation.

### 5.2 Evidence for 5.3

These come from my own reimplementation of the R2c score-level design (5 stars, N = 1,100,
gain 0.010).

| Scenario (mark ICC, residual ICC, block AR) | Star × 6 yr | Star × 12 yr | Star × 18 yr | Star only |
|---|---:|---:|---:|---:|
| Independent (0, 0, 0): power / coverage | 0.704 / 0.904 | 0.690 / 0.898 | 0.671 / 0.901 | 0.601 / 0.909 |
| (0.05, 0.1, 0.7) | 0.630 / 0.846 | 0.589 / 0.874 | 0.560 / 0.886 | 0.459 / 0.903 |
| (0.10, 0.2, 0.7) | 0.528 / 0.780 | 0.472 / 0.836 | 0.420 / 0.874 | 0.321 / 0.916 |
| R2c stress case (0.5, 0.1, 0.7) | 0.459 / 0.719 | 0.382 / 0.803 | 0.314 / 0.851 | 0.216 / 0.907 |

Coverage here is nonidentity 90% interval coverage. SS Cyg's log-mark ICC across six-year blocks
is −0.020 to 0.013 on both clocks and in both periods. That is far below the stress case. The
residual ICC is unknown until R2b.

### 5.3 Inference for the sealed test (rule; finalised in R2d)

- **Default:** star × 18-year blocks (two per star), capped weights, CR1 with t(G − 1).
- **Validation:** R2d simulates at R2b's estimated residual ICC and autocorrelation, and at the
  qualified stars' development-era mark ICC (gain-free at G3a). If star × 18-year nonidentity
  coverage falls below 0.88, the test uses star-level clustering.
- Star × six-year clustering is not used for the sealed test.

### 5.4 Precision gate

R2d decides G2:

- the planning effect is the smaller of 0.010 and H2's point estimate;
- the required N comes from simulation at the estimated dependence, under the chosen clustering;
- if H2 ≤ 0, or the required N exceeds the yield measured at G3a, the planned test is reported as
  underpowered. The rule is not weakened.

## 6. Sealed-test primary specification (fixed now)

- **Clock:** DF, under rules 1.1–1.2, with per-star thresholds and margins.
- **Comparator:** B2. B1 replaces it only if B2 fails a pre-declared development stability
  check:
  - optimizer failure;
  - or multistart disagreement in the objective beyond 1e-6 relative.
- **Score:** the X5 working interval score.
- **Mark:** a pooled nonnegative offset on the DF mark.
- **Weights:** capped as in v1.

R2b can change this specification only through a pre-declared feasibility or stability failure,
never by comparing gains. Codex may challenge it before the v1 freeze. A challenge after R2b
scores exist cannot change it.

## 7. Interpretation (adds to v1 §6)

- **H2's lower limits under both blockings exceed its computed ceiling:** cadence-lag correction
  alone is not a sufficient explanation under §3.4's assumptions. This does not identify
  physical memory. Base misspecification beyond B2, and observers responding to outburst
  properties, remain possible.
- **The negative-control mark has a positive lower limit under either blocking:** cadence
  pathways are live. The DF result is then read no further than H1.
- **H1 is positive and H2 ≤ 0:** the point-clock gain depends on the fitted-end or landmark
  pathway, or on the change of clock. No mechanism is inferred.
- **B2 removes a gain that B0 shows:** duration information is not separable from a slowly
  evolving timing state in this record. That does not make duration only a state indicator.

## 8. Work plan

1. **Codex:**
   - amend and freeze this file as v1, with sources, parameters and tests for the abort rule,
     anchor harmonisation, `c_end`/`c_on`, the rate mark, the ceiling, twelve-year CR1 and the
     dependence diagnostics;
   - regenerate the DF features and recount them gain-free;
   - fit B0–B2 on development and score evaluation.

   All claims stay provisional.
2. **Claude:** review R2b; then R2d integration, the G2 decision and the G3a question to Barry.

Barry's later decisions, none blocking:

- **G3a:** open development-only (pre-1990) records for the named nominees, to qualify them,
  count forecasts and measure cadence.
- **G3b:** open the 1990–2025 test period under the sealed protocol.
- Whether SS Cyg 2018–2025 becomes an additional test period.
- Whether to invite a dwarf-nova specialist.
