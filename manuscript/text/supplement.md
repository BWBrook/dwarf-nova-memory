# Supplement: methods, sensitivities and correction record

**Second draft for review, 10 November 2026. No release or new data access is authorised.**
<div id="authors"></div>

\renewcommand{\thefigure}{S\arabic{figure}}

This supplement distinguishes the frozen original comparison, the exploratory observation and
clock reassessment, synthetic precision planning, and the prospectively frozen transfer screen.
Every quoted number is linked to the claims
ledger, `manuscript/claims.csv`. The interpretation specification, `manuscript/estimands.md`,
states what each analysis bounds and which phrasings are not allowed. Section and decision labels
(A04, A10, D018 and so on) refer to the project record in `docs/` and `coordination/decisions.md`.

## S1. Definitions, readings and units

| Term | Meaning |
|---|---|
| Issuance | One forecast, issued when the observation-time rule first confirms that an outburst has ended |
| Duration | Onset-to-end time of the completed outburst, from X4 run on the 400 days before issue |
| Quiet gap | End of one outburst to onset of the next; fitted-end and observed-anchor proxies are distinguished in S2.8 |
| Previous-gap predictor, $q$ | Standardised log of the preceding quiet gap, used only if covered (no visit gap over seven days) |
| Recent-level predictor, $L$ | Standardised mean of up to six earlier covered log quiet gaps; zero after standardisation if none |
| Fitted onset interval | X4's retrospective crossing summary; working scoring evidence, not a known physical bracket |
| Right censoring | The forecast ends at coverage loss, the next issuance, or the block end before an onset is established |
| Working interval score | Log forecast mass for the fitted onset interval, or log survival to a selected cutoff, conditioned on issue; a proper latent-onset likelihood is unestablished |
| Paired gain | M3's log score minus M2's for the same issuance |
| Geometric mean likelihood ratio | exp(mean paired gain); a [1.7]{.C02}% increase for the primary |
| Working clock scale | The median of the untruncated lognormal clock; ratios of scales are model quantities, not observed mean waits |
| Partial-identification bounds | The smallest and largest coverage consistent with bracketed or censored outcomes |

Times are Julian Dates as returned by the archive, without conversion. Durations and gaps are in
days. Log durations are standardised by the frozen development centre and scale.

## S2. Methods

### S2.1 Observations and extraction

Rows were requested in bounded annual windows, ending strictly before 2018. Responses near the
50,000-row service cap were bisected, and every response was hashed on receipt before parsing. The
analysis uses rows in the `Vis.` band with validation flag `V`. The 1960–2017 evaluation window
contains [63]{.C15} validated leaf responses. These hold [500,479]{.C15} rows after removing
[81]{.C15} duplicate identifiers, of which [249,356]{.C15} meet the analysis selector[]{.C15}.

X4 (`src/dnmem/extract_x4.py`, definition `a04f-x4-v1`) groups observer visits into candidate
episodes brighter than visual magnitude 10. For each episode it forms normalised slope-mixture summaries for the
brightening and fading threshold crossings, using nearby estimates plus a shared 0.05-mag
systematic level-error allowance. Plug-in noise, slope weighting and clipping do not establish
a calibrated posterior or known containment of physical onset. The allowance prevents unlimited
shrinkage as estimates accumulate; it was chosen on development simulations, not measured as
the true shared observer error. An episode is
confirmed by bright reports from two distinct observers, or from one observer on at least two
nights with a margin past the threshold and no contradicting faint report. The observation-time
confirmation rule arms only on bright evidence at least 0.5 mag past the threshold. Reports
closer to the threshold cannot arm it; noisy reports that cross the margin can still do so.

Three earlier extractors, X1 to X3, failed qualification. X4 passed a synthetic screen at magnitude
10 on the qualified phase-aligned cadence family, and the C1/7 d coverage rule was selected there.
The unseen waveform family failed benchmark qualification before X4 recovery was scored;
X4 recovery on that family was not tested. Magnitude-9.5 diagnostics failed in later eras. Those
failures are retained (A04e–A04i). The evaluation is therefore conditional on the magnitude-10
X4 extraction.

### S2.2 Issuance and predictors

Each observation-time end confirmation issues one forecast at its emission time. A two-day reporting
delay is a sensitivity. Every emission is kept, including false and repeat emissions. Predictors come
from X4 run on the rows in the 400 days up to the emission and on nothing else. A unit test inserts
poisoned rows after the emission and checks that no ledger field changes. The current episode is
the last prefix episode whose end bracket reaches the emission's bright evidence. A duration of zero
or less makes the mark unavailable; nothing is clipped. The previous gap requires the previous
episode to begin more than 30 days inside the window.

### S2.3 Outcomes and censoring

The original outcome is the next onset summary found by retrospective X4 up to an explicit cutoff. An onset
bracket that straddles issue does not establish survival, and that forecast is excluded under the
frozen rule. Here none were excluded. A forecast is scored on the onset interval if the interval is
established before the first of these events:

- coverage loss, the first visit gap longer than seven days after issue;
- supersession by the next issuance;
- the end of the block.

Otherwise the forecast is right-censored at the earliest of these events.

### S2.4 Models and working scores

Each model is a lognormal clock for the quiet gap $Q$ after a fitted end anchor $e$, with log-location
$\mu$ and log-standard deviation $\sigma$:

- M0: $\mu = \alpha$;
- M2: $\mu = \alpha + \gamma_1 q + \gamma_2 L$;
- M3: $\mu = \alpha + \gamma_1 q + \gamma_2 L + \beta x$, with $\beta \ge 0$.

Here $q = (\log Q_{\mathrm{prev}} - c_q)/s_q$. If $\ell$ is the mean of up to six earlier covered
log quiet gaps, $L = (\ell - c_L)/s_L$; set $L = 0$ if none are available. The centres and scales
are frozen development means and standard deviations. Likewise, $x$ is the standardised log
duration. At issue age $a$, an onset bracket $(l, u]$ scores
$\log P(l - e < Q \le u - e) - \log S(a)$. A censoring time $c$ scores $\log S(c - e) - \log S(a)$,
where $S$ is the survival function. Forecasts without a covered previous gap use M0 in both
models, and forecasts without an available fitted end use a common remaining-wait forecast. Both contribute
exactly zero to the contrast.

M2 was fitted on timing-eligible 1910–1959 rows and frozen. The duration offset was then fitted on
rows with a valid mark, with M2 held fixed, so that $\beta = 0$ reproduces M2 exactly (D021).
Frozen values (C04): $\beta$ = [0.046597]{.C04} per standard deviation of log duration; previous-gap
slope [0.078016]{.C04}; recent-level slope [0.051336]{.C04}; $\sigma$ = [0.34636]{.C04}. The
parameter file's SHA-256 begins `ce4ef8d5`.

The constraint $\beta \ge 0$ and matched routing respond to a measurement coupling. The duration
and the following gap share the estimated end time, so end-time error couples them. In earlier
synthetic work that coupling pushed fitted null coefficients negative (D020). Codex then showed
that a nonnegative bound is a restriction of direction, not a theorem about the sign of the error.
An exact construction with constant true duration can yield positive information (D021). Endpoint
coupling therefore remains a stated limit. The uniform-end and two-day-delay sensitivities probe
it only partly.

### S2.5 Primary statistic and inference

The statistic is the mean paired gain over all score-eligible issuances with issue times in
JD 2436934.5 to 2458119.5. The standard error is cluster-robust, over consecutive clusters of
$6 \times 365.25$ days anchored at the window start, with the factor $G/(G-1)$ for $G$ nonempty clusters.
Inference uses Student's t with $G - 1$ degrees of freedom. The result counts as confirmed if the
one-sided 95% lower bound exceeds zero. The cluster length was chosen before any operating
characteristics were seen (D021). There is one confirmatory statistic. No subset, era, variant or
interval width may replace it.

### S2.6 Operating characteristics

Before the development fit, a finite synthetic screen checked the design (A10d). At an effect sized
to CM92's published correlations, [11]{.C30} of [40]{.C30} simulated evaluations confirmed, with exact
interval [0.146]{.C30} to [0.439]{.C30}[]{.C30}. Pooled no-effect histories gave [3]{.C31}
confirmations in [220]{.C31}. These histories share random streams, so the count is a finite
screen, not an independent error rate or a certified size. The reference injected effect gave a
mean gain of [0.0045]{.C33} nats[]{.C33}. Barry accepted the finite screen before the first real
fit (D022).

### S2.7 Access, execution and repair

| Stage (8 November 2026, UTC) | Time |
|---|---|
| Protocol published (DOI 10.5281/zenodo.24053338) | 12:34:47 |
| First attempt began; failed before any ledger or score | 12:38:28; 12:39:51 |
| Repaired acquisition began | 12:51:18 |
| Candidate and reference ledger concordance passed | 13:06:58.627 |
| Primary result written | 13:06:58.641 |

The first attempt failed when the archive's literal `uncert="None"` token for missing uncertainty
reached a strict parser. Uncertainty enters no extraction, feature, evidence, routing or score path.
The repair accepts that exact token without changing or dropping any row. Synthetic invariance
tests, independent review, the full test suite, a new full rehearsal and supported-platform CI
passed before continuation (D026). All 26 original forecasting source files, the parameter bytes
and the protocol bytes are unchanged. The repair freeze is `5e39aeb` and the execution commit
`d7151e0`. No person or agent inspected real scores, outcomes, counts or coverage summaries before
the primary file existed[]{.C05}.

Two independent ledger and evidence implementations had to agree exactly at both delays before any
score. A separate checker reproduced all 2,641 variant score rows, with a maximum discrepancy of
order $10^{-13}$, and the primary interval[]{.C01}. Claude recomputed the interval by a separate
route[]{.C01}. The primary population and routing are in C03.


### S2.8 Observation contract, censor repair and redesigned clocks

The original probability calculation is reproducible, but the fitted interval is not itself a
known latent-onset set. The R1 contract audit found that clipping may return an envelope when
fitted and report intervals conflict, rather than always nesting the former inside the latter.
Its crossing kernel also contains a slope-dependent weighting. Normalising that kernel does
not prove a generative likelihood for the selected reports. Forecast comparisons using it must
therefore be named working scores.

R1 separately audited the first eligible confirmed candidate, including candidates that never
issued forecasts. A future rule was needed when a fitted interval straddles a selected stopping
cutoff: if issue < L < C < U, version v4 uses the working lower-edge backoff while retaining C
and its administrative reason. The original sources and scores are preserved. This repair fixes
an internal working-set convention; it does not convert statistical bounds into known survival
of a physical onset. The actual original ledger has no affected straddle[]{.C43}.

The corrected X5 construction searches for decisive faintness after the previous peak before
selecting the subsequent decisive-bright rise. It keeps raw time supports and explicit flags.
The latent target proposed for R2 is the last upward threshold crossing before decisive
brightness. Three premises remain distinct:

- **A0:** correct association, relevant-event completeness and a valid risk set;
- **A1:** containment of the latent crossing in a resolved report window, or genuine survival
  through a censoring cutoff;
- **A2:** a complete normalised coarsening-at-random observation kernel for the selected data.

Under the relevant premises, the report likelihood can factor into a model-independent
observation term and the forecast probability of its compatible onset set. Visit timing alone
does not establish that factorisation. Median aggregation can hide a decisive raw report,
so exact raw magnitudes and broad time supports do not by themselves establish witness ordering.
A margin past threshold is not proof of A0, A1 or A2.

R2b retained the working interval/backoff score and reported a separate deterministic sensitivity.
At the realised stopping cutoff C, its mixed functional uses the point-density contrast for a
latent onset before C and the survival contrast at C otherwise. Infima and suprema over the
compatible report set give conditional sample bounds. They require A0/A1 and genuine survival
where used, are not confidence limits, and do not bound an unknown censored latent-density score.
Coverage loss and supersession are selected cutoffs, not independent administrative censoring.

The DF observed clock anchors the current forecast to the first decisive faint report and
uses the decisive-bright span as its mark. A delayed issue waits for report availability; a new
decisive bright report can abort it. The same scheduled observed-anchor convention defines
historical gaps. Prefix extraction reconstructs history at each issue; it is not an immutable
catalogue of measurements available under unknown historical upload dates. End interpolation
is absent from this clock, but report lag, shared observations and selection remain. An invented
cadence construction yields a positive duration-mark gain without physical duration information;
it is a counterexample, not an estimate for SS Cyg[]{.C48}.

B0 uses previous-gap and older-history covariates, B1 discounted history and B2 a windowed
state-space level. Every marked rule adds a development-fitted nonnegative term to its own
fixed base and preserves missing-history/mark fallbacks. These models are new windowed
comparators, not the original M2. The original-issue, DF-issue and matched point-clock populations
are kept distinct. Exact coincident DF clocks share the earliest original representative;
later originals remain in the audit. Unsupported outcomes stay unsupported and are not filled
with empirical zero gains. The execution freeze is 5fb69c6.

### S2.9 Sequential precision experiments and distinct nulls

R2d simulated the learning and availability algorithm in Gaussian point log gaps. Development
fits, guarded marks, delayed outcome labels and rolling level updates were rebuilt in each trial.
Mark noise, missingness, small development samples, unequal star weights, opposing slopes,
shared trends/states and dependence were stressed jointly. Star weights were capped; both
star-half and whole-star CR1/t procedures were reported, with whole-star score sign flips as a
symmetry-qualified sensitivity. Six equal-count epochs were grouped into halves: these are
not actual calendar eighteen-year clusters. No method was selected from the results.
The positive-effect cells use a nominal individual latent-oracle gain of [0.004]{.C65} nats
before mark noise, centring and development learning; achieved frozen gains can be much smaller.
This is a synthetic input, not C01 or an effect inferred from the archive.[]{.C69}

The two statistics ask different questions. In an invented unit-variance Gaussian model with
standardised mark x, true coefficient beta and frozen forecast shift b*x,

$$E[U_0]=\beta,\qquad E[\Delta s]=b\beta-b^2/2.$$

Thus a positive coefficient-score moment can accompany negative gain by the actual forecast.
With beta=[0.05]{.C66} and b=[0.20]{.C66}, expected gain is [−0.010]{.C66} nats.
Mark centring, variance centring and nuisance orthogonalisation are different operations; the
tested score moment is not asserted to be an efficient or model-free information test.

Strict predictive-null controls used the generator's true conditional mean and innovation
variance. No-direct-effect histories with estimated bases or shared states can still contain
real incremental predictive information. Their rejection rates are specificity/learning
diagnostics, not universally false positives. Known means give realised-path predictable
gain and score targets; these are not unconditional long-run KL. Gain-interval coverage was
reported with and without exact-zero-offset fits.

The grid fixed [35]{.C65} cases with [2,000]{.C65} deterministic trial seeds each. A separate
six-star grid fixed [eight]{.C69} cases and [16,000]{.C69 .V068} total trials. Exact binomial intervals
describe per-cell Monte Carlo uncertainty, not uncertainty about the astronomical process.
An observed at-most-five-percent screen does not certify nominal size; neither pooling different
null cases nor agreement of same-sample Taylor ratios certifies every full null. Few stars
also limit exact sign flips: with four, the minimum one-sided p is [0.0625]{.C66}.

The proposed association-then-gain fixed sequence retains distinct claims. Strong familywise
control requires stage one valid under its association null and stage two valid whenever
frozen forecast gain is nonpositive, including real association with an oversized trained
coefficient. Independence of the stages is unnecessary. Empirical nesting of rejections in
the retained grids is not a theorem or a future power guarantee[]{.C67}.

### S2.10 Gain-free early-record transfer qualification

G3a fixed its protocol and implementation in Git at d827313 before any candidate record was
requested. The authorised split is native JD < 2447892.5, with the inclusive provider endpoint
strictly below it. Exact names were resolved under the same date restriction; pagination,
cap subdivision, identity, row-window and duplicate checks preceded analysis. Every raw response
was retained and hashed. Only native Vis./V reports entered qualification; limits remained
limits and missing uncertainties remained missing.

The candidate set was SS Aur, RU Peg, AR And, X Leo, TW Vir, UU Aql, CH UMa and DX And, with
U Gem and IP Peg as eclipse holds. Thresholds were catalogue proposals, not fitted visual
calibrations. A common decisive margin was frozen before access. All candidates needed:

- at least [40]{.C68 .V036} timing-supported, positive-mark DF issuances with an eligible onset window
  or positive-exposure working censor;
- at least [70]{.C68 .V037}% eligible onset windows among confirmed episodes;
- stable nondegenerate unmarked B0 fits at every declared start;
- no operational long-bright-run failure;
- for the holds, an additional frozen eclipse feasibility guard.

Zero-exposure survival terms did not count. B0 convergence used marks stripped and fitted no
duration offset. The morphology rule flags a supported threshold-bright run lasting at least
sixty days, or repeated forty-day runs, with minimum night/observer support and no long internal
observing hole. It is an operational exclusion, not a subtype classifier. The qualifying set
was written before any pooled mark fit; it is empty, so no such fit followed.

The holds used two derived observer/JD-night streams: median versus brightest positive estimate,
with the strongest numerical bound for all-limit nights. A night is released at its fixed end,
not its retrospectively last report. Two-night faint confirmation delays the issue. Both streams
must pass ordinary qualification and agree on episode/window/mark and supported-count metrics.
A fixed synthetic dip envelope on the same early timestamps is an additional conditional test.
Its no-eclipse baseline must first recover enough events with adequate timing accuracy; neither
hold passed this baseline, so no eclipse-profile outcome was evaluated. This is not evidence
that eclipses caused failure or were removed.

Last-decade supported issuance rates were extrapolated to proposed test horizons solely for
planning. G3a required a sufficiently large qualifying cohort and projected yield before a
G3b request; neither requirement was met. Candidate test data and SS Cyg 2018 onward remain
closed. G3a measured transfer feasibility, not duration effects in other stars.

## S3. Results and sensitivities

### S3.1 Primary, eras, class rule and sensitivities

**Table S1.** Frozen comparisons, mean paired working-score gain (nats per issuance) and 90% cluster
interval. Only the first row is confirmatory.

| Comparison | Issuances | Gain | Interval |
|---|---:|---:|---|
| Primary, M3 − M2, 1960–2017 | [441]{.C01 .V004} | [0.0165]{.C01 .V001} | [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003} |
| Segment 1960–1992 | [261]{.C06} | [0.0240]{.C06} | [0.0091]{.C06} to [0.0389]{.C06} |
| Segment 1993–2017 | [180]{.C07} | [0.0057]{.C07} | [−0.0107]{.C07} to [0.0221]{.C07} |
| 12-day class and within-class rule | 441 | [0.0025]{.C08} | [−0.0022]{.C08} to [0.0072]{.C08} |
| Uniform-end marks | 441 | [0.0166]{.C09} | lower [0.0044]{.C09} |
| Previous-gap-only baseline | 441 | [0.0170]{.C09} | lower [0.0054]{.C09} |
| Two-day issue delay | 441 | [0.0165]{.C09} | lower [0.0049]{.C09} |
| Joint-valid rows | 436 | [0.0167]{.C09} | lower [0.0049]{.C09} |
| Three-year clusters | 441 | as primary | lower [0.0059]{.C09} |
| Baseline M2 − M0 | 441 | [0.1168]{.C10} | [0.0663]{.C10} to [0.1672]{.C10} |

The primary interval uses ten nonempty blocks and nine degrees of freedom[]{.C01}. Eight have positive means. Leave-one-block-out means span [0.0132]{.C25} to
[0.0194]{.C25}, and [0.5397]{.C25} of individual issuance gains are positive. Holding the estimate,
critical value and blocks fixed, the strict failure boundary is approximately
[1.42705]{.C25} times the reported standard error. A 42% inflation passes and an exact 43%
fails. None of these checks validates the cluster dependence assumption.

The frozen P3 placebo equals M2, because its development lag coefficient sat at its bound of zero.
The planned memory placebo therefore carries no information.

### S3.2 Calibration

M3's nominal 50% central intervals covered between [0.546]{.C11} and [0.617]{.C11} of outcomes;
its nominal 90% intervals between [0.923]{.C11} and [0.980]{.C11}[]{.C11}. Each range runs from
definitely covered to possibly covered, given the extracted brackets and censoring, over all scored
issuances. These are realised-sample bounds, not confidence intervals for a population rate, and
they show overcoverage. Mid-CDF deciles of resolved onsets are descriptive; no uniformity test is
claimed.

### S3.3 Evaluation-only offsets

Duration offsets were fitted to the evaluation outcomes with an evaluation-refitted M2 held fixed.
The support intervals use a likelihood-ratio cutoff of 3.841, with no dependence or measurement
calibration.

| Offset | Estimate | Conditional support |
|---|---:|---|
| Current duration, separate | [0.04209]{.C12} | [0.01574]{.C12} to [0.06845]{.C12} |
| Previous duration, separate | [−0.03836]{.C12} | [−0.06489]{.C12} to [−0.01184]{.C12} |
| Current duration, joint | [0.03045]{.C13} | [−0.00063]{.C13} to [0.06152]{.C13} |
| Previous duration, joint | [−0.02213]{.C13} | [−0.05340]{.C13} to [0.00913]{.C13} |

The joint design is correlated but has full rank, with condition number [1.79]{.C13}[]{.C13}. Both
joint support intervals include zero. Correlation alone neither explains that nor makes the
coefficients nonidentifiable.

### S3.4 A slow component can hide behind negative lag signs

Negative lag signs alone cannot exclude a dominant slow driver (A10k). Take independent
unit-variance AR(1) components $S$ and $A$, with persistence 0.95 and −0.9, and set log duration
$= 0.175S + 0.350A$ and log gap $= 0.300S + 0.001A$. The lag-one duration correlation is then about
−0.53, and the lag coefficient conditional on the preceding gap is negative. Yet $S$ dominates gap
variation and the current conditional covariance. This construction is a logical counterexample, not
fitted to SS Cyg and not a rival empirical result.

### S3.5 Exploratory post-result calculations

Everything in this subsection reuses the evaluation outcomes. Each interval conditions on the fitted
adjustment it describes. None supplies a further held-out confirmation.

- **Level shift and recentring (C20).** The best common M2 log-location shift is [−0.04679]{.C20}.
  It reduces the original untruncated clock scale by about 4.57%. The frozen duration term implies a
  level shift of [−0.01108]{.C20}, because the evaluation mean standardised log duration is
  [−0.2379]{.C20}. Shifting M2 by that implied amount accounts for [0.00370]{.C20} nats
  ([0.00013]{.C20} to [0.00726]{.C20}). The contrast after recentring the duration at its evaluation
  mean is [0.01283]{.C20} ([0.00359]{.C20} to [0.02206]{.C20}). With both models at the best M2
  level, the gain is [0.01239]{.C20} ([0.00098]{.C20} to [0.02381]{.C20}). The two orderings of the
  split differ by about 0.000012 nats.
- **Class versus continuous duration (C21).** With M2's historical parameters fixed and a free
  common level, the evaluation likelihood-ratio comparisons are as follows:
  - class versus level only, [14.7]{.C21 .V005};
  - continuous log duration versus level only, [11.7]{.C21 .V006};
  - within-class duration added to class, [0.17]{.C21 .V007}.

  The class contrast corresponds to a [14]{.C21 .V008}% larger untruncated working-clock scale after
  long outbursts. In 1910–1959 the class and continuous fits were similar, with a smaller contrast[]{.C21}.
- **Shared level for the class rule (C22).** The frozen class-plus-within rule's mean offset is
  [0.01728]{.C22}. Giving both rules M2's evaluation-fitted level yields a gain of [0.00905]{.C22}
  ([0.00409]{.C22} to [0.01401]{.C22}). For 1993–2017 alone it yields [0.00761]{.C22}
  ([−0.00631]{.C22} to [0.02153]{.C22}). The uncentred type component cannot shorten short-outburst
  forecasts, but the full frozen rule does shorten [181]{.C22} of [245]{.C22} of them through its within-class term.
- **Era refits (C23).** The class contrast is [0.16323]{.C23} (statistic [13.504]{.C23}) in
  1960–1992 and [0.07828]{.C23} ([2.262]{.C23}) in 1993–2017. These are descriptive; there is no
  test of change.
- **Alternation (C24).** Across forecast-record pairs, the lag-one correlation of log duration is
  [−0.5233]{.C24} in the evaluation years and [−0.4006]{.C24} in the development years. A long
  outburst followed a long one in [0.1495]{.C24} of pairs and a short one in [0.6640]{.C24}. The
  pairs include one repeat-flagged record and are not a catalogue of unique consecutive outbursts.

### S3.6 Development fit

In 1910–1959 the duration offset was [0.0466]{.C14} per standard deviation, with likelihood-ratio
statistic [5.1935]{.C14} against M2[]{.C14}. This fit is in-sample and overlaps CM92's record, so it
is not evidence for the claim.

### S3.7 Prior art checked against the source

Claude re-read CM92's Table 4 and its Fig. 5 subscript conventions on the original scan
[@cannizzo1992LongtermBehaviorSS] []{.C40}.
For [705]{.C40} outbursts (1896–1992), the correlations are:

- duration with the following quiescence, [0.223]{.C40};
- duration with the preceding quiescence, [0.282]{.C40};
- successive durations, [−0.400]{.C40}.

Durations split at [12]{.C40} days, with [401]{.C40} shorter and [304]{.C40} longer. The correlation of duration
with the following onset-to-onset cycle is [0.475]{.C40}, against [0.145]{.C40} with the preceding cycle. For
end-to-end cycles the pattern reverses, at [0.093]{.C40} and [0.521]{.C40}. The famous relation is therefore
largely a consequence of the cycle definition, which already contains the duration; CM92 showed
that cycle definitions matter.

### S3.8 Bounded independent novelty check

An independent search in A10m found no prior preregistered probabilistic held-out recurrence
evaluation, or explicit held-out comparison of duration beyond a timing-history baseline, among
the studies located and checked. This supports a bounded "to our knowledge" statement, not proof
of universal priority. The exact queries and source receipts are in
`data/provenance/a10m_novelty/`; the appraisal is
`docs/audits/2026-11-09-a10m-novelty-review.md`.

The closest precedent, [Grigorievskiy et al. (2014)](https://research.cs.aalto.fi/aml/Publications/Publication216.pdf),
uses chronological training, validation and test sets, with one test outburst of V363 Lyr. It
scores point-onset errors; no preregistration or scored predictive onset distribution is reported.
No explicit duration-addition comparison against a common timing baseline is reported. Repeated
random fits do not make the evaluated forecast a probability distribution. The independent
search included an OpenAlex citing-title screen and primary-source checks of this study and
@price2007SSCygniOutburst. ADS access failed; observer/non-English coverage is incomplete, and some
full texts, including Tsuranova et al. (2026), remain inaccessible. Their unverified methods are
not treated as exclusions. []{.C41}


### S3.9 R1 rescoring and endpoint-error diagnostics

The censor audit's future repair changed [zero]{.C43} original outcomes. Deleting all
[six]{.C43} censored issuances gives [0.01678]{.C43} nats on the remainder, a descriptive deletion
sensitivity rather than a bound on every observation-model correction. The date-selected
Figure 1 example has model median remaining waits [27.5749]{.C42} and [26.7726]{.C42} days and
probabilities within thirty days [0.576727]{.C42} and [0.602765]{.C42}. It does not estimate
mean observational utility.

Saved-point density scoring gained [0.015404]{.C44} nats ([0.003443]{.C44} to [0.027365]{.C44})
on [441]{.C44} issuances. Its points are fitted summaries. Original report clips were missing
for [434]{.C45} associations. Only [11]{.C45} contrasts, including [five]{.C45} exact fallback
zeros, supported the proposed report-interval/kernel sensitivity. That selected subset is not a
full-population replication. The later X5 repair supplied [818]{.C47} available and [805]{.C47}
eligible windows among [845]{.C47} confirmed episodes, with median width [1.1495]{.C47} days;
it did not retroactively alter the frozen result.

The endpoint-dose study used [80]{.C46} histories under null and gap-dependent scenarios.
Independent Gaussian errors were added to fitted ends after extraction, while issue and onset
times stayed fixed. Every tested all-issued scenario/dose mean was nonpositive[]{.C46}.
Large doses disabled landmarks and increased exact common fallbacks, so zero gain did not
certify latent measurement validity. Truth-anchor comparisons selected completed,
still-quiescent matched emissions. Systematic/state-dependent errors, regenerated observing
behaviour and unseen waveforms were not covered. One floating-point concordance failure and
its separately frozen same-seed recovery remain in the execution record; no scientific
predictor or gain was tuned from that failure.

### S3.10 R2b report-window and clock contrasts

**Table S2.** Exploratory R2b headline contrasts. Every six- and twelve-year interval crosses
zero. These intervals describe the stated working-score populations; they do not validate
physical onset containment, coarsening at random or prospective coverage.

<!-- BEGIN GENERATED r2b -->
| Exploratory contrast | Scored issuances | Mean gain, nats | Six-year 90% interval | Twelve-year 90% interval |
|---|---:|---:|---|---|
| H1: fitted-end clock, B2 duration | [432]{.C55 .V012} | [0.0075]{.C55 .V009} | [−0.0008]{.C55 .V010} to [0.0159]{.C55 .V011} | [−0.0014]{.C55 .V021} to [0.0165]{.C55 .V022} |
| H2: observed clock, B2 bright span | [431]{.C55 .V016} | [0.0043]{.C55 .V013} | [−0.0008]{.C55 .V014} to [0.0094]{.C55 .V015} | [−0.0021]{.C55 .V023} to [0.0107]{.C55 .V024} |
| H3: observed-clock gain minus matched fitted-end gain | [431]{.C55 .V020} | [−0.0031]{.C55 .V017} | [−0.0078]{.C55 .V018} to [0.0017]{.C55 .V019} | [−0.0078]{.C55 .V025} to [0.0017]{.C55 .V026} |
<!-- END GENERATED r2b -->

Original evaluation issues numbered [441]{.C54}; the unique delayed-clock schedule numbered
[440]{.C54}. Those are not the scored denominators. Missing windows, candidate obstacles and
invalid risk sets stayed explicit; they were not skipped to credit a later event. H3 is a
paired difference between incremental working gains, not a causal measurement-error effect.

The fixed-C mixed sample envelope for H2 runs from [0.0009703]{.C57} to [0.0077535]{.C57}.
Its positive lower mean is conditional on the report/risk-set and survival premises. It is not
a positive confidence limit or proof of latent forecast improvement. The observing-rate proxy
gained [0.0030]{.C56} under the working rule, but its duration-dependent span prevents treating
it as a validated cadence negative control. A one-lag anchor-shift Fisher index is only local:
independent exact integration exceeds its quadratic approximation in an invented example[]{.C53}.
It cannot serve as an upper bound ruling out cadence. Midpoint residual and block-dependence
proxies are likewise selected, noisy diagnostics rather than validated future-star covariance.

All actual model scores were reconstructed by separate numerical routes[]{.C58}. That
agreement establishes implementation concordance, not parameter identifiability, measurement
calibration or the observation premises.

### S3.11 Baseline adequacy and post-result rolling guards

On the DF development population, negative log likelihood was [830.19]{.C61} for B0,
[827.24]{.C61} for B1 and [849.28]{.C61} for B2. B2 was preselected, not empirically strongest.
Its lower fit motivates review of its particular windowed state implementation; it does not
uniquely establish the physical recurrence process. Measured geometric mean gaps in the first
evaluation blocks were shorter than the development-block range, without resolving physical
versus observational causes[]{.C61}.

Historical guards subtracted the preceding ten marks and used rolling recalibration from
preceding available evaluation outcomes. They retained the unguarded development coefficient,
used evaluation-only history and final saved labels at proxy resolution times. Simple closure
and coverage-recognition delays left update sets unchanged in SS Cyg, but complete confirmation,
recrossing and eligibility availability was not reconstructed.

The point-original B0 duration gain changed from [0.0184]{.C62} to [0.0132]{.C62}. The rate
gain changed from [0.00304]{.C62} to [0.00142]{.C62}; the guarded estimate remained positive
and inconclusive. Guarded DF B0/B2 duration intervals also crossed zero, while point-B0 retained
positive lower limits under both blockings[]{.C63}. Changing base and mark together creates an
ordering-dependent descriptive sensitivity, not a causal allocation or a measured fraction
of C01. Different significance labels do not establish a predictor difference.

Sequential trend counterexamples show that rolling guards can leave positive score moments
and even genuine gain over a lagging base without a direct physical mark effect[]{.C66}.
The same-sample score/gain Taylor ratios reproduce[]{.C64}, but shared scores and curvature
enter both sides. They are not independent prospective power evidence.

### S3.12 Multi-star precision and sequence diagnostics

**Table S3.** Whole-star rejection frequencies at a nominal individual latent-oracle gain of
[0.004]{.C65} nats, before noise, centring and learning. The issuance counts are nominal; stressed cases lose usable mark support. Percentages
concern each complete generator/learning process, not a common supported sample size or achieved gain.

<!-- BEGIN GENERATED precision -->
| Stars and condition | Nominal evaluation issuances | Score-moment rejection | Frozen-gain rejection |
|---|---:|---:|---:|
| Eight, clean | [1,100]{.C65} | [81.8]{.C65}% | [36.7]{.C65}% |
| Eight, persistent / small development / missing marks | [1,100]{.C65} | [63.6]{.C65}% | — |
| Eight, noisy / delayed / common state | [1,100]{.C65} | [38.7]{.C65}% | — |
| Six, clean | [1,100]{.C69 .V066} | [76.8]{.C69 .V058}% | [33.1]{.C69 .V059}% |
| Six, clean | [2,000]{.C69 .V067} | [94.6]{.C69 .V060}% | [48.8]{.C69 .V061}% |
| Six, persistent / small development / missing marks | [1,100]{.C69 .V066} | [59.4]{.C69 .V062}% | [21.3]{.C69 .V063}% |
| Six, noisy / delayed / common state | [1,100]{.C69 .V066} | [36.2]{.C69 .V064}% | [10.3]{.C69 .V065}% |
<!-- END GENERATED precision -->

All [70,000]{.C65} original-grid and [16,000]{.C69 .V068} supplemental trials completed without
failed fits. Neither grid establishes a robust sample size across its stressed envelope.
The six-star supplement has estimated-base no-direct-effect cells, not separate six-star
strict-oracle controls.

Gain never rejected without the score test in either retained grid[]{.C67}[]{.C69}. Independent
Gaussian arithmetic disproves general nesting, so this is not a prospective power identity.
The pooled original strict-oracle score rate was [397]{.C67}/[8,000]{.C67}; pooling does not
certify every scenario or the partial null of real association with nonpositive gain. An exactly
five-percent procedure can fail an observed-at-most-five-percent Monte Carlo screen frequently;
the frozen screen is retained as the finite rule it was, with uncertainty, not reinterpreted
as proof of miscalibration or replaced by a pooled pass.

### S3.13 Transfer qualification, attrition and the SS Aur flag

**Table S4.** Frozen G3a qualification. Hold-star counts use the median derived-night stream
with delayed confirmations, not the ordinary raw-report diagnostic.

<!-- BEGIN GENERATED qualification -->
| Candidate | Supported development issuances | Eligible onset windows | Main failed conditions |
|---|---:|---:|---|
| SS Aur | [110]{.C68 .V038} | [79.6]{.C68 .V039}% | Operational morphology |
| RU Peg | [23]{.C68 .V040} | [63.5]{.C68 .V041}% | Count, windows |
| AR And | [7]{.C68 .V042} | [31.4]{.C68 .V043}% | Count, windows, base information/fit |
| X Leo | [35]{.C68 .V044} | [44.0]{.C68 .V045}% | Count, windows |
| TW Vir | [0]{.C68 .V046} | [11.6]{.C68 .V047}% | Count, windows, base information/fit |
| UU Aql | [15]{.C68 .V048} | [80.8]{.C68 .V049}% | Count |
| CH UMa | [0]{.C68 .V050} | [70.4]{.C68 .V051}% | Count, base information/fit |
| DX And | [0]{.C68 .V052} | [70.8]{.C68 .V053}% | Count, base information/fit |
| U Gem, hold | [27]{.C68 .V054} | [90.6]{.C68 .V055}% | Count, eclipse guard inconclusive |
| IP Peg, hold | [0]{.C68 .V056} | [66.7]{.C68 .V057}% | Count, windows, base information/fit, eclipse guard inconclusive |
<!-- END GENERATED qualification -->

Across frozen streams there were [217]{.C68 .V033} supported development issuances. The frozen
1980s streams supplied [102]{.C68 .V034} supported issuances; all candidates ignoring gates project
[367.2]{.C68 .V035} over 36 years if that rate persists. No actual test count was opened.

The independent ordinary raw-report diagnostic must remain separate. It gave [105]{.C70}
supported 1980s issuances against [485]{.C70} confirmed episode peaks, compared with SS Cyg's
[67]{.C70}/[73]{.C70}. The ratios count issues and peaks by different time landmarks and are
not paired recovery probabilities. In this raw diagnostic, [822]{.C70} clock-available
development issuances fell to [280]{.C70} with a covered previous gap and [274]{.C70} after
requiring a mark. Outcome support reduced the corresponding covered-gap unmarked/marked totals to
[225]{.C70}/[221]{.C70}. Missing covered history was the largest counted loss; the causes
include observing holes, window eligibility and candidate association, not a unique depth effect.

Deleting history and mark gates in the raw diagnostic gave [201]{.C70} 1980s opportunities
and at most [five]{.C70} stars with forty development opportunities. At that assumed rate the
[36]{.C70}-year projection is [723.6]{.C70}. This does not meet the proposal, and it is not the
frozen hold-stream result or an impossibility bound for other models. We omit speculative later
split projections because they do not measure later observing coverage.

Whole-pre-1990 median fade-confirmation delays were longer in candidates than the SS Cyg
reference[]{.C70}. These measure the closure of the last threshold-bright visit to the last raw support time
of the first selected decisive-faint visit, not true-end timing errors. They do not justify allocating the forecast loss to
photometric precision.

The SS Aur flag spans [100.97]{.C71} days. Separate native parsing and graph reconstruction
found [258]{.C71} votes, including [252]{.C71} positive visit medians; their magnitude quantiles
were [12.5]{.C71}, [13.2]{.C71} and [13.7]{.C71}. The exact nondecisive threshold-bright band,
$12.5<m\le13.5$, contains [176]{.C71}/[252]{.C71}. Its decisive-bright nights form
[four]{.C71} separated groups, with [one]{.C71}, [seven]{.C71}, [three]{.C71} and [five]{.C71}
nights. This is not an independently annotated physical-outburst count. The record-wide
[14.5]{.C71}-mag median is selected from reports fainter than threshold and pools other years
and observers. No sequence change, observer offset, intrinsic brightening, contamination or
subtype is adjudicated. Removing this morphology failure would still not create the required
cohort under the unchanged count gates.

The expansion stops for this paper. Preserving the empty qualifying set and untouched test
records records what the chosen transfer failed to support. It does not establish absent
duration information in other stars or the impossibility of a materially different analysis.

## S4. Analyses superseded during review

Each entry records what was replaced, who found the problem, and where the record is.

| Earlier analysis or statement | Problem and finder | Replacement | Record |
|---|---|---|---|
| Duration predicts the following onset-to-onset cycle | Shared term with the cycle (CM92); confirmed in the A01 audit | Quiet-gap target only | A01 memo |
| Extractors X1, X2, X3 | Failed synthetic qualification (Codex and Claude reviews) | X4, qualified at magnitude 10 only | A04e–A04i |
| Unrestricted duration coefficient on all routes | End-time coupling and route mixing (Claude, D020) | $\beta \ge 0$, matched routing, local gap level | D020, D021 |
| Joint refit of M3 with M2 | Training loss not matched to deployment (Codex, D021) | Mark offsets fitted with M2 fixed | D021 |
| Candidate-authority concordance rule | Allowed mismatch deletion (Codex, D024) | Exact two-implementation concordance or abort | D024 |
| Strict parser for the uncertainty field | Failed on `None` after access (execution) | Exact-token repair, reviewed and rehearsed | D026 |

**Interpretation corrections checked in A10k.** Codex's independent audit narrowed several readings
from Claude's A10j review before the products were drafted. Claude accepted all of them (D030).

| Earlier reading | Corrected scope | Evidence |
|---|---|---|
| Global recentering isolates drift-free information | It defines an approximately additive descriptive score contrast; within-period drift remains possible |[]{.C20} |
| All predictive information is in outburst type | A class indicator has greater in-sample likelihood; within-class equivalence was not tested |[]{.C21} |
| The entire frozen class rule cannot shorten short-event forecasts | That restriction concerns its type component; the within-class component can shorten them |[]{.C08}[]{.C22} |
| Negative lag excludes a dominant slow driver | Alternation and a slow component can coexist; no mechanism allocation follows |[]{.C12}[]{.C13}[]{.C24} |
| A rounded SE boundary is a safe inclusive margin | The decision is strict; the rescaling boundary is exclusive and does not validate dependence |[]{.C25} |
| Frozen M2 forecasts are 4.6% too long | The best level shift reduces the untruncated clock scale by 4.57%; that is not a remaining-wait bias |[]{.C20} |
| The gap after a long outburst is about five days longer | A 14% clock-scale ratio; days need an explicitly chosen reference scale |[]{.C21} |

The original exploratory numbers are retained. These corrections do not alter the frozen primary
comparison, its outcomes or the predeclared class-rule result.

**Novelty wording narrowed in A10l.** The draft framing called this the first preregistered held-out
forecast test of dwarf-nova recurrence. The refreshed search found a held-out point-forecast study
of V363 Lyr by Grigorievskiy and colleagues, in the 2014 ITISE proceedings (pp. 520–531), with a single test
outburst. The claim now specifies preregistered, probabilistic and duration-based[]{.C41}.

**Draft corrections in A10m.** Semantic review corrected an overstatement of complete flare
recovery, distinguished an unseen-waveform qualification failure from unperformed X4 recovery,
defined the standardised timing predictors, and gave the within-class likelihood statistic its
proper class-model reference. The article's assumptions table now states calculated results and
current limits rather than attributing information exclusively to class or physical disc state.
The uniform-end lower bound is rounded directly from the full-precision evidence, and the SE
failure boundary is explicitly approximate when printed. Reproduction commands preserve committed
evidence and state their retained-input dependencies. The primary comparison is unchanged.


**Observation, baseline and transfer corrections after external review.**

| Earlier reading or implementation | Reviewed replacement | Evidence |
|---|---|---|
| X4's fitted interval is a hard observing bracket or calibrated posterior | Working crossing summary; proper latent-onset observation likelihood remains unestablished | R1 contract audit |
| The censor rule handles every interval straddle | Separately versioned lower-edge backoff; zero original outcomes changed |[]{.C43} |
| Two-sided report rescoring is available for the original full population | Missing lower clips prevent that; corrected X5 is a new construction |[]{.C45}[]{.C47} |
| An observed clock eliminates endpoint/cadence mechanisms | It removes one literal fitted end but retains report lags, selection and shared observations |[]{.C48}[]{.C53} |
| B2 is the strongest activity comparator | It was preselected; development and descriptive held-out fit were weaker |[]{.C60}[]{.C61} |
| Guards identify an era component of C01 or remove all slow covariation | They change both rules and leave other trends; no causal share of C01 was measured |[]{.C62}[]{.C63} |
| Positive score detection confirms trained forecast gain | Distinct full nulls; overshoot counterexamples and no universal sequence nesting |[]{.C66}[]{.C67} |
| Candidate/reference ratios are paired cycle-conversion probabilities | Issuance/peak descriptive rates; ordinary and derived hold streams are separate |[]{.C70} |
| SS Aur's flag establishes four outbursts or photometric contamination | Four report-night clusters and threshold-proximate medians, with no cause adjudicated |[]{.C71} |
| Frozen transfer failure excludes every later model or data source | Failure of the specified screen; stopping expansion is a scope judgment |[]{.C68}[]{.C70} |

None of these reviews retunes or overwrites the original comparison. The failed protocols,
source freezes, bounded access receipts and negative/inconclusive results remain in the record.

## S5. Reproduction and navigation

From the repository root, without new archive requests:

These public-only checks use the committed aggregates and figure assets:

```sh
python3 manuscript/figures.py --check
make -C manuscript check
make -C manuscript
```

Recomputing scores and exploratory fits requires the retained inputs outside Git. The saved-score
checker needs the completed evaluation run. The three subsequent analyses also need the retained
1910–1959 development inputs. Outputs below go to scratch paths; committed evidence is preserved.

```sh
python3 scripts/check_a10g_evaluation.py \
  --directory outputs/a10h_live_repair_5e39aeb \
  --output outputs/a10m_reproduction/score_audit.json
uv run --frozen --extra analysis \
  python scripts/a10j_postresult_review.py \
  --output outputs/a10m_reproduction/a10j_summary.json
uv run --frozen --extra analysis \
  python scripts/a10k_exploratory_audit.py
uv run --frozen --extra analysis \
  python scripts/a10k_secondary_audit.py
```

The retained run includes raw archive replies, observer identities and per-issuance scores. Its
archive SHA-256 and manifest are in `data/provenance/a10i_evaluation_1960_2017/archive.json`.
The committed aggregates support the ledger values, but do not replace these inputs for a full
recomputation. The published protocol is at <https://doi.org/10.5281/zenodo.24053338>.


The observation/transfer reviews use the same retained early records and saved outputs.
These commands write new audit outputs and do not download data:

~~~sh
uv run --frozen --extra analysis python scripts/r1_observation_scores.py \
  --freeze-commit 0594146 --output outputs/paper_reproduction/r1_scores
uv run --frozen --extra analysis python scripts/check_r2b_execution.py \
  --run outputs/r2b_real_5fb69c6 --allow-real --output outputs/paper_reproduction/r2b_check
uv run --frozen --extra analysis python scripts/check_r2d_review.py \
  --output outputs/paper_reproduction/r2d_review
uv run --frozen --extra analysis python scripts/check_g3a_execution.py \
  --output outputs/paper_reproduction/g3a_check
uv run --frozen --extra analysis python scripts/check_ss_aur_flag.py \
  --output outputs/paper_reproduction/ss_aur_flag
~~~

The endpoint-dose and precision-grid regeneration commands, individual deterministic seeds,
source locks and recovery receipts are in the R1, R2d and G3a audit/protocol files. Full
regeneration is distinct from recounting saved trials and is unnecessary for rebuilding the
paper. Public evidence resides in data/provenance/r1_20261109, r2b_20261109,
r2d_precision, g3a_preparation, g3a_20261110 and g3a_review_independent. These aggregates
do not replace native inputs for an independent full measurement reconstruction. No command
in this guide authorises a new candidate test-period request or SS Cyg 2018+ access.

Navigation:

- `manuscript/claims.csv`: every claim, with its status, evidence, commit, reproduction command and
  limits.
- `manuscript/estimands.md`: allowed and forbidden readings.
- `coordination/decisions.md`: D013–D047.
- `docs/audits/`: every review, including A10i (the result), A10j (Claude's review), A10k (Codex's
  audit) and A10l (sources and drafts).
- `docs/outcome-access-ledger.md`: who saw which outcomes, and when.
- `manuscript/text/for-agents.md`: the agent guide.

## References
