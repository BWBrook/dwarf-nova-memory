# R2 design, draft v0: observation target, endpoint discrimination, stronger baselines and a sealed multi-star test

Claude (Opus 5.5), 9 November 2026. **Draft for Codex to amend into a frozen v1. Nothing here is
frozen, and no score has been computed under it.** It builds on the A10n triage, D033, D034 and
my [R1 review](../audits/2026-11-09-claude-r1-review.md). Everything run on SS Cyg under this
design is exploratory, because 1910–2017 is already opened. The only fresh confirmation available
is the sealed multi-star test in §5, and opening any star's records is Barry's decision (G3).

## 1. Decisions proposed

1. **Target.** Forecast the latent time at which the star's visual light curve rises through a
   fixed threshold, followed by decisive brightening. Do not forecast the time of the first report.
2. **Observation contract as a ladder of assumptions,** each with its own score.
   - Under containment alone (A1), the latent point-score gain is **bounded** without any
     coarsening model.
   - Adding first-detection ignorability (A2) makes the hard decisive-bracket interval score
     proper.
   - The original working score and the point density remain as references.
3. **X5:** X4 with the lower onset clip corrected. It is the extractor for all new work and for the
   SS Cyg rescoring of outcomes.
4. **A decoupled forecast (DF)** that uses no estimated threshold crossing at the end of the
   outburst. It is the decisive test of the reviewer's endpoint and landmark explanation.
5. **The model ladder** B0 (M2), B1 (autoregressive with an evolving level) and B2 (state space),
   each with and without duration, on SS Cyg first.
6. **A sealed multi-star test,** with catalogue-only screening, development-only qualification
   and one opening per star. Its pooled primary is B2 + duration versus B2, scored with the X5
   interval score.
7. **Interpretation rules (§6)** fixed now, before any R2 score exists.

## 2. Observation target and contract

### 2.1 Target

$T$ is the first time after quiescence is re-established at which the star's visual brightness
rises through $m_{\rm thr}$ and then reaches $m_{\rm thr} - B$. For SS Cyg, $m_{\rm thr} = 10$ and
$B$ = `BAND` = 1 mag. $T$ is a property of the light curve. It is not the physical onset of the
disc instability, which precedes the optical rise by an amount that depends on whether the
outburst starts inside-out or outside-in. Excursions that never reach decisive brightness are not
outbursts under this definition.

### 2.2 Why the latent target and not the first report

The time of the first bright report is observable, and scoring it needs no coarsening assumption.
It folds the observing network into the outcome, though: cadence, season, era and alert behaviour.
These differ between stars and decades, and they plausibly correlate with outburst prominence,
since long, bright outbursts attract more observers. That makes it the worst target for a
multi-star test, and a direct channel for exactly the artefacts G1 must exclude. The scientific
claim is about the star, so the target should be too.

### 2.3 X5 decisive bracket

Per confirmed episode $k$ with predecessor $k-1$:

- $Q_k$, the **quiescence anchor**: the first decisive faint report after the predecessor's peak.
  A decisive faint report is a positive estimate, or a fainter-than limit, at or fainter than
  $m_{\rm thr} + B$.
- $U_k$: the first decisive bright report (an estimate at or brighter than $m_{\rm thr} - B$)
  after $Q_k$, at or before the peak.
- $L_k$: the last decisive faint report before $U_k$.
- The onset bracket is $(L_k, U_k]$. No posterior interval is involved, so there is no clipping
  and no envelope.

Episodes whose peak never reaches $m_{\rm thr} - B$ have no $U_k$. Scoring them needs a rule that
R2a must fix gain-free, either exclusion or $U_k$ = the peak report. My gain-free count (positive
estimates only, 1896–2017) finds a bracket for 818 of 845 confirmed episodes, with median width
1.16 d (R1 review). The end bracket is defined symmetrically: the last decisive bright report
after the peak, and the first decisive faint report after it.

Predictors (duration, previous gap, level) keep X4's point estimates in the SS Cyg rescoring, so
only the outcome observation changes. New stars use X5 for both, with point estimates inside the
X5 brackets.

### 2.4 Assumptions and scores

**A1, containment.** $T \in (L, U]$. It fails only if a visual estimate errs by at least $B$ in the
wrong direction near the crossing, or if a misidentified star is reported.

**A2, first-detection ignorability (coarsening at random).** Given the observed history, the
probability of the observed bracket does not depend on where $T$ lies inside it. The argument is
that before the first decisive bright report, no visual observer has seen the outburst. Visit times
inside $(L, U)$ are then set by schedules, weather, Moon, season and the observed history, which may
include anticipation from the known cycle. Two channels can break A2:

- a non-decisive near-threshold report that triggers alerts and follow-up;
- information from outside the visual stream, such as CCD observers or satellites.

Both shorten $U - T$ relative to the background rate.

**Scores, for a baseline B and a duration model D with predictive densities $f_B, f_D$ for $T$
conditioned on survival to issue:**

| Assumptions | Score per forecast | What it licenses |
|---|---|---|
| A1 only | Bounds: $\ell_i = \min_{t \in (L_i, U_i]} \log\frac{f_{D,i}(t)}{f_{B,i}(t)}$ and $u_i = \max_{t \in (L_i, U_i]} \log\frac{f_{D,i}(t)}{f_{B,i}(t)}$. Censored forecasts take the exact $\log S_D(c'_i) - \log S_B(c'_i)$, where $c'_i$ is the last decisive faint report at or before the cutoff | The latent point log-score gain (the score if each $T$ were known) lies in $[\bar\ell, \bar u]$. The CR1 lower limit on $\bar\ell$ is a conservative bound for it, with no coarsening model |
| A1 + A2 | Interval: $\log F_D(L_i, U_i] - \log F_B(L_i, U_i]$ | A proper score for the coarsened observation (see below) |
| References | Original working score (C01); saved-point density (C44) | Comparison with the frozen result |

*Propriety under A1 + A2.* Let the coarsening produce bracket $b$ with probability $c(b)$ whenever
$t \in b$, so that $\sum_b c(b)\,\mathbf 1\{t \in b\} = 1$ for every $t$. The expected score of a
forecast $F$ under truth $F_0$ is $\sum_b c(b)\, F_0(b) \log F(b)$. This is concave in $F$. Its
derivative with respect to $dF(s)$ at $F = F_0$ is $\sum_b c(b)\,\mathbf 1\{s \in b\} = 1$, the
same for every $s$, so $F_0$ is a global maximiser. Brackets need not form a partition. The
propriety is not strict: forecasts that agree on every bracket probability tie.

*Why the gain moves little between scores.* When a bracket of width $w$ is narrow against the
forecast scale $s$, the interval and point log-ratios differ by about $w \cdot \partial_t
\log(f_D/f_B)$. The two forecasts' slopes differ only through the small duration shift. The
bounds' half-range is the same quantity. R1's point-density sensitivity (−6.8% against the working
score) is consistent with this. R2b measures it directly.

### 2.5 Gain-free diagnostics (R2a, SS Cyg, before any R2 score)

- **A1 contradiction rate.** Among decisive reports more than 3 d from any bracket (clear
  quiescence or plateau), the share with an opposite decisive report from another observer within
  0.5 d. Report the expected number of failed brackets this implies. Also count decisive faint
  reports between $U_k$ and the peak.
- **A2 visit rates.** Visits per day inside $(L, U)$ against the 5 d before $L$. Then the interval
  from the first non-decisive bright report to $U$, against the background inter-visit interval.
  A short interval means alert-driven follow-up. Note that it affects the scores only at the
  sub-bracket scale.
- Bracket availability and widths by decade, plus the faint-peak rule.

## 3. The endpoint and landmark explanation (G1)

R1c shows that added iid end noise does not create a positive mean gain in the fixed simulator.
The reviewer's counterexample works differently. It uses the shared estimated end, through
measured duration and the issue age, together with landmark selection. Noise experiments cannot
exclude it. The test that can is a forecast in which the end estimate never appears.

**DF, the decoupled forecast (primary G1 test).**

- **Anchor:** the first decisive faint report after the peak, $E^{\rm dec}_k$. It is an observed
  time, by which the star is surely below threshold under A1, not an estimated crossing.
- **Age** at issue is $\tau - E^{\rm dec}_k$. The forecast targets $T - E^{\rm dec}_k$ under the
  same lognormal family, conditioned on survival to that age.
- **Duration:** the bright-phase length, from the first to the last decisive bright report in
  the episode. It shares no report with either threshold crossing.
- **Previous gap and level:** use the same decisive anchors, $L_k - E^{\rm dec}_{k-1}$.
- **Fitting:** baseline and duration refitted on 1910–1959, exactly as the primary was, with
  $\beta \ge 0$. Then evaluated on 1960–2017 with the X5 interval score and the A1 bounds.

The DF gain can fall short of the original's because bright-phase duration is a noisier measure of
the disc cycle. A positive DF gain cannot come from the shared end estimate, because there is none.

**Secondary G1 checks.**

- **Fluence:** integrated linear flux above quiescence over the episode, in threshold-flux-days,
  as a duration substitute in B0. An end shift of a day changes it by a few percent; it changes
  duration by about 10%. A disc-mass-depletion reading predicts that fluence carries at least
  comparable information. An endpoint artefact predicts that it carries less.
- **Coverage stratification:** the gain where both the current end bracket and the next onset
  bracket are at most 2 d wide, against the rest.
- **Synthetic sanity:** DF on the R1c null and structured histories. Its null gain should be near
  zero, like the original's.
- **Optional:** systematic, type-dependent end errors in the R1c harness, with long outbursts' ends
  shifted by $\delta \in \{0.5, 1, 2\}$ d. These are low priority once DF exists.

## 4. Stronger timing baselines

All baselines use timing only: quiet intervals, never durations or types. Duration enters as
$\beta\, z(\log d)$ with $\beta \ge 0$. Its centring and scale come from development data,
identical across rungs.

| Rung | Location of log quiet interval $k$ |
|---|---|
| B0 = M2 | $\alpha + b_q z(\log q_{k-1}) + b_L z(\bar L_6)$, the frozen benchmark |
| B1 | $\alpha + \phi_1 z(\log q_{k-1}) + \phi_2 z(\log q_{k-2}) + b_L z(L^{\lambda})$, where $L^{\lambda}$ is an exponentially weighted level with discount $\lambda$ fitted on development data. $q_{k-2}$ carries long/short alternation |
| B2 | Local level plus AR(1): $\log q_k = x_k + u_k$, $x_k = x_{k-1} + w_k$, $u_k = \phi u_{k-1} + e_k$. A Kalman filter treats uncovered intervals as missing, so state variance grows across gaps. The predictive variance includes the state uncertainty |

**Rules.**

- **Exact nesting.** Setting $\beta = 0$ reproduces the base forecast bit for bit, with identical
  routing when duration is missing. This is a required test.
- **Online use.** State updates use only intervals completed and available by the issue time.
- **Fitting order.** As in the primary: fit the base on development data, fit $\beta$ with the base
  fixed, then freeze. B2's variance ratio may be profiled on development data.
- **Reporting.** Report, on identical forecasts, the retained fraction
  $\rho_B = $ gain(B + D vs B) / gain(M3 vs M2), under the X5 interval score and the A1 bounds.

## 5. Sealed multi-star test (draft for the G3 decision)

**Hypothesis.** In ordinary U Gem-type dwarf novae, the measured length of a completed outburst
improves forecasts of the next onset beyond the strongest stable timing baseline. The direction is
fixed in advance ($\beta \ge 0$).

**Cohort, screened from catalogues and literature only** (GCVS, VSX classifications, published
cycle statistics; no AAVSO observation, count or coverage query):

- **Include:** type UGSS or an equivalent ordinary U Gem classification; northern or equatorial
  sky; a visual range spanning a threshold that visual observers routinely reach.
- **Exclude:** UGZ (standstills), UGSU and UGWZ (superoutbursts), and novalikes.
- **Candidates to verify:** U Gem, SS Aur, RU Peg, IP Peg, AR And, X Leo, TW Vir, plus any others the
  screen finds. U Gem and IP Peg eclipse, which is a qualification risk for spurious faint reports.
- **Exposure table:** published duration–interval analyses for each star and the years they used
  (for example Ak et al. 2002 for SS Cyg). Excluded stars stay in the screening record.

**Per-star constants, from the catalogue range before any access.**

- $m_{\rm thr}$ is the midpoint of the catalogue visual range, rounded to 0.5 mag. SS Cyg gives
  10.0.
- $B = \min(1.0, 0.25 \times \text{amplitude})$.
- X5 priors are rescaled by each star's catalogue rise and decline rates where published, and
  otherwise fixed at the SS Cyg values and qualified (Q4).

**Split and sealing.**

- Development is everything before 1990-01-01 (JD 2447892.5).
- Test runs from 1990-01-01 to 2025-12-31 (JD < 2461041.5).
- Each star's archive requests are date-bounded: development years first, test years once, after
  the freeze.
- Alternative for Codex and Barry: also reserve 2018–2025 for every star as a later replication.
  It costs about a fifth of the test years.

**Qualification on development years only.** A star failing any of these is dropped before its
test years are requested.

- **Q1:** an X5 onset bracket for at least 80% of confirmed episodes, and a median width of at most
  $\max(3\,\text{d},\ 0.1 \times$ the median quiet interval$)$.
- **Q2:** a decisive contradiction rate of at most 2%.
- **Q3:** at least 40 development forecasts with a covered previous gap and a scoreable outcome.
- **Q4:** synthetic recovery. On records with the star's development cadence (resampled visit
  times, SS Cyg-like light-curve shapes rescaled to the star), X5 brackets contain the true onset at
  least 95% of the time.

**Models.**

- Per-star B0–B2 parameters come from that star's development data.
- The duration coefficient is pooled across stars in standardised units, with star-specific centring
  and scale, fitted with the baselines fixed. Per-star $\beta$ is secondary.
- The primary comparator is B2. If the SS Cyg ladder (R2b) shows B2 to be unstable or dominated,
  it is the strongest stable rung instead, fixed before G3.

**Primary statistic.**

- The forecast-weighted mean of the paired X5 interval-score gain (B2 + D − B2) over all test
  forecasts of qualified stars.
- No star contributes more than 40% of the weight; beyond that its forecasts are downweighted.
- CR1 clusters are star × six-year block. Confirmation is a lower 90% limit above zero (one-sided
  5%).
- **Secondaries:** the star-balanced mean, per-star gains, the ladder, DF and the A1 bounds. All are
  descriptive. There is one primary, so no multiplicity correction applies.

**Precision (G2).**

- From C01, the per-forecast gain SD including clustering is about
  $0.0063203 \times \sqrt{441} \approx 0.133$.
- At 80% power and one-sided 5%, SS Cyg-like variability needs about 400 test forecasts to detect
  0.0165, about 1,100 for 0.010 and about 1,700 for 0.008.
- C01 passed a significance filter, so the true SS Cyg effect is plausibly below its estimate.
  Design for a minimum detectable effect of 0.010.
- R2c turns this into a simulation, with no star data:
  - literature cycle statistics and synthetic cadences;
  - X5 extraction;
  - effects scaled from SS Cyg, with gain SD scaling with $\beta$.

**Later option (not in R2):** prospective public forecasts for the cohort, posted in the repository
before the outbursts occur and scored as they arrive. That is the strongest confirmation there is,
and it fits the living-paper model. For SS Cyg it would need 2018+ history, so it is Barry's call.

## 6. Interpretation rules, fixed before any R2 score

These apply to the SS Cyg exploratory analyses (R2b). Ratios compare point estimates on identical
forecasts with the original M3 − M2 working gain on those forecasts.

| Result | Reading |
|---|---|
| X5 interval gain: lower 90% > 0, **and** $\bar\ell > 0$ | The duration effect holds for the latent threshold onset under A1 (bounds) and A1 + A2 (interval). E1 is closed for SS Cyg, as an exploratory finding |
| Interval lower 90% > 0, but $\bar\ell \le 0$ | The result depends on A2. Products state it as conditional on first-detection ignorability |
| Interval 90% interval includes 0 | The working-score result does not transfer to a proper latent score. Reframe before any expansion |
| DF ratio ≥ 0.5 | The shared end estimate cannot be the sole source. G1 passes |
| 0 < DF ratio < 0.5 | Partial or indeterminate. G1 is open; multi-star DF becomes a co-primary secondary |
| DF ratio ≤ 0 | Endpoint or landmark information is the leading explanation. G1 fails; measurement becomes the paper's centre |
| $\rho_{B2} \ge 0.5$ | Duration carries information beyond an evolving timing state |
| $\rho_{B2} \le 0.25$ and its interval includes 0 | Duration acts mainly as a state indicator. The multi-star hypothesis is restated, with B0 as comparator, and that is still a result worth testing |

**Go to G3** when E1 closes or is conditional on A2, G1 passes or is open, and G2's minimum
detectable effect is at most 0.010. Otherwise, the paper is a bounded SS Cyg study with corrected
claims and the measurement findings.

## 7. Work plan

| Step | Owner | Content | Data |
|---|---|---|---|
| R2a | Codex | X5 with fainter-than limits and the faint-peak rule, plus tests; §2.5 diagnostics; DF features, fluence, B1 and B2 with exact-nesting tests; freeze the R2b protocol with §6 | SS Cyg 1896–2017, gain-free |
| R2b | Codex runs, Claude reviews | §2.4 scores, §3 DF and its secondaries, §4 ladder; fit 1910–1959, evaluate 1960–2017 | SS Cyg, exploratory |
| R2c | Codex (parallel with R2a) | Cohort screen and exposure table; per-star constants; G2 power simulation | Catalogues and literature only |
| R2d | Claude | Integrate; go/no-go; sealed protocol v1; one G3 question to Barry with a recommendation | none |

Manuscript products stay paused. Once the contract is agreed, `estimands.md` gets A1/A2 and their
allowed phrasings, before any prose changes.

## 8. Decisions that belong to Barry (none needed now)

- **G3:** date-bounded development-year requests for screened stars, then one test-year opening per
  qualified star, on the frozen v1 protocol.
- Whether SS Cyg 2018–2025 joins the test as one more sealed series.
- Whether to invite a dwarf-nova specialist to review the cohort and the physical predictions
  before G3. I recommend it.
- Later: prospective public forecasts, byline (AAS does not allow AI authors) and venue.
