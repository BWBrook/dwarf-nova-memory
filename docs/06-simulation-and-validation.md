# Simulation and validation plan

**Status:** planned experiments, 5 November 2026. Numerical results from the repository demonstration are synthetic checks only. They are not estimates for real dwarf novae, a power analysis for the proposed dataset, or a validated physical accretion-disc simulation.

## 1. What the bundled code does and does not establish

The minimal implementation is deliberately an **oracle complete-event demonstration**: simulated outburst ends, durations and subsequent quiescent waits are known; a stationary lognormal renewal model and a marked alternative can be compared. Separate cadence exercises illustrate that some events can be missed. These pieces make the proposed information flow executable and expose useful failure modes.

They do not implement a joint likelihood for photometry and missed events, uncertain shared event boundaries, true end-confirmation landmarks, hierarchical population inference, or fitted latent-activity models M2/M3. Functions that evaluate simple interval or right-censor contributions are building blocks, not evidence that a complete censored-data fit exists.

An apparent gain by a marked model in a shared-state simulation is not automatically a false forecast result. The mark may really contain information about the hidden state. What would be false is interpreting that gain as proof that the previous outburst directly controls the next one.

## 2. Define success before running a large simulation campaign

There are four distinct validation questions:

| Question | Appropriate experiment |
|---|---|
| Is a calculation implemented correctly? | Analytic identities, limiting cases and an independently coded calculation |
| Can the estimator recover parameters under its own assumptions? | Simulation with known parameters; Bayesian SBC if a posterior sampler is implemented |
| Can the design distinguish competing scientific explanations? | Simulations outside the fitted model family, including observational failures |
| Does the method predict real later observations usefully? | Locked retrospective or prospective evaluation |

Passing an earlier row does not pass the later rows. Talts et al. (2018) describe simulation-based calibration for checking Bayesian computation. SBC should be added when the project actually fits a Bayesian model; it is not a substitute for testing misspecification or evaluating real forecasts.

For each experiment write a machine-readable configuration containing the generating process, observation policy, effect size, random seed, extractor version, training/evaluation split, fitting model and scoring rule. Generate distinct random streams for latent events, brightness noise and observing decisions. Keep truth files separate from the files supplied to the inference pipeline.

## 3. Generating mechanisms to distinguish

Use a small factorial design for screening before expanding the expensive cases.

| Scenario | Generating truth | What it tests |
|---|---|---|
| N0: independent renewal | Non-exponential gaps; independent completed marks | Whether a flexible renewal baseline avoids spurious claims caused by an inadequate Poisson null |
| N1: between-system heterogeneity | Different typical gaps and durations among stars, no within-star link | Whether pooling manufactures an individual memory relationship |
| L: shared slow state | State affects both duration and subsequent gap; direct mark coefficient is zero | Whether predictive gains are incorrectly interpreted as a direct mechanism |
| M: direct marked dependence | Gap depends on completed duration under a stationary regime | Recovery and predictive power for the operational target |
| LM: state plus marked dependence | Both mechanisms operate | Ability to retain mark information after adapting to timing history |
| C: changing regime | Abrupt or gradual changes without a fixed mark coefficient | Robustness to nonstationarity and inadequate state timescales |
| T: changing event mixture | Alternating or state-dependent short/long events | Whether a pooled relation merely tracks unmodelled event classes |
| B: shared boundary error | Independent true duration and gap, noisy common end time | False negative association caused by endpoint uncertainty |

Start with several systems, dozens of cycles each, and parameters spanning the pilot's measured ranges. The exact sample size and noise grid must be revised after data feasibility work; do not select a final design from simulated numbers that were never checked against actual coverage.

For marked effects use ratios of conditional median waiting times, for example 1.0, 1.1 and 1.2 when duration doubles, and corresponding negative effects. Under the log-duration AFT formulation, the generating slope is \(\log(r)/\log(2)\). Include more than one residual variance and more than one state persistence timescale. High-signal simulations alone are uninformative about feasibility.

For state-only scenarios, distinguish two nulls:

- **No incremental predictive information:** after the baseline's available history, the mark adds nothing. A claimed improvement is a statistical false positive.
- **No direct physical mark effect:** the mark can still reveal latent state and improve prediction. An improved forecast is legitimate, but direct physical attribution would be unsupported.

Do not estimate a single “false memory rate” that mixes these two definitions.

## 4. Pass truth through an observation process

The scientific experiment should eventually follow this order:

1. Generate true events, durations, marks and state histories.
2. Generate band-specific brightness trajectories and quiescent levels.
3. Generate observing opportunities and decisions, then noise, quality flags and limits.
4. Export only the ordinary observation format and provenance available to the real pipeline.
5. Apply the same deduplication, quality handling and event extraction as for real observations.
6. Construct every historical feature table as of its issue time.
7. Fit competing models, issue forecasts, and score their later evidence.
8. Compare event recovery and inference to hidden truth after all predictions are stored.

The observation experiment should cover:

- Regular and irregular cadence, scaled to the shortest events relevant to the primary sample.
- Seasonal gaps and interruptions, including intervals long enough to hide whole outbursts.
- Bright-state-triggered follow-up as well as scheduled observations independent of the simulated brightness.
- Detection depth that reaches quiescence versus depth that only detects outbursts.
- Filter changes, observer offsets, heteroscedastic errors, outliers and blended measurements.
- Missing onset/decline wings, uncertain thresholds and correlated endpoint errors.
- Duplicate observations appearing in more than one source archive.

Fixed real timestamps provide a conditional recovery test and preserve realistic seasons. Add a separate policy experiment in which observing probability depends on simulated brightness and recorded alerts. Freezing a schedule that was itself influenced by the actual star cannot prove that observation selection is harmless.

### Recoverability is a surface, not one percentage

Measure detection probability and endpoint error against duration, amplitude, phase within a season, cadence and limiting magnitude. Use realistic non-square light curves for the scientific recovery test, including examples different from the extractor's assumptions. Report recovered event count, false split/merge rate, missed-event rate, endpoint uncertainty coverage and bias in duration/fluence.

For a provisional tightly monitored sample, investigate whether a rule can achieve a missed-event fraction below about 5% across the relevant duration and brightness range. This is a **proposed pilot benchmark**, not a proven completeness claim. A rule that attains it only by excluding all short events changes the scientific sample. Report that tradeoff and include sensitivity to plausible residual missed events.

## 5. Tests worth retaining in a scientific codebase

Write tests for independent mathematical and scientific properties, rather than for exact copies of the implementation.

### Survival and event arithmetic

- Conditional survival satisfies \(S(a+h)/S(a)\), equals one at \(h=0\), and decreases appropriately with the future horizon.
- Interval probabilities agree with numerical integration in ordinary cases, approach density times width for narrow intervals, and remain numerically valid in the tails.
- Right-censor contributions are survival probabilities; no event is silently inserted at the censor time.
- When onset and end are known, \(C=D+Q\); the coupling null produces the expected direction of bias when \(C\) is regressed on \(D\).
- Shared end-time errors produce opposite errors in duration and subsequent quiescent time.
- Unobserved complete outbursts prevent adjacent detected events from being declared consecutive without supporting evidence.

### Forecast integrity

- Changing any data after a forecast's issue time leaves that forecast unchanged.
- A cycle crossing the training cutoff contributes only information available before the cutoff.
- State predictions use filtered histories, not states smoothed with later outcomes.
- Scaling constants and pooled hyperparameters do not use other systems' future observations.
- Changing a validation label cannot change model selection or preprocessing in a locked analysis.
- Repeated measurements or duplicated archive records do not artificially multiply event evidence.

### Calibration and stress tests

- Null cases with no incremental information do not systematically favour the more complex model under the planned evaluation procedure.
- Parameter or interval coverage is checked across simulated datasets, not just on the seed that generated an attractive example.
- Fitted effects and predictive scores are assessed when the generating distribution differs from the fitted distribution.
- The final analysis can return “data do not distinguish these explanations” without crashing or forcing a classification.

Implement the relevant tests as each feature becomes real. Do not label planned tests as passed simply because the demonstration tests pass.

## 6. Replication budget and decision criteria

Use approximately 50–100 replicates per screening cell to identify gross failures, then increase replication for the few scientific decisions that matter. Around 1,000 replicates give a Monte Carlo standard error of about 0.007 for an estimated false-positive probability of 0.05. This follows from \(\sqrt{p(1-p)/R}\); report Monte Carlo uncertainty rather than presenting simulation fractions as exact.

Before the final evaluation, choose a scientifically useful effect and a practical predictive-improvement target. A provisional feasibility target is at least 80% sensitivity to the agreed effect at the planned evidence criterion, while maintaining an acceptably low rate of claims under the **correctly defined** null. These are design choices, not mandatory universal thresholds. If power remains poor, reduce the question, extend the time series, improve measurement, or report a design/identifiability result. Do not compensate by pooling incompatible subclasses.

Inspect robustness to holding out each system, alternate plausible event thresholds, error inflation, additional missed events, and state timescales. Use the simulation to choose a small number of sensitivities before looking at the final observational results.

The first screening stage should run on a laptop. The user's larger CPU resources become useful for independent replicated simulation or model fits after the generative and observation models have been debugged. Parallelise whole replicates with deterministic seed allocation; retain configuration hashes and software versions. A large cluster does not resolve an unidentified model.

## 7. Deliverables from the simulation phase

The agents should produce:

1. A validated event-recovery surface for the selected observational regimes.
2. A comparison of competing fitted models under each generating scenario, including failed fits.
3. Calibration, effect-recovery and predictive-score diagnostics with Monte Carlo uncertainty.
4. A clearly stated range of effect sizes and state timescales the design can distinguish.
5. A list of observational and mechanistic ambiguities it cannot resolve.
6. A frozen choice of primary model comparison, forecast origins, score, sample rules and sensitivities for the observational evaluation.

## Source

Talts, S., Betancourt, M., Simpson, D., Vehtari, A. & Gelman, A. (2018). *Validating Bayesian Inference Algorithms with Simulation-Based Calibration*. [arXiv:1804.06788](https://arxiv.org/abs/1804.06788), bibliography key `Talts2018`. Checked 5 November 2026. The simulation scenarios and practical gates above are project proposals, not results reported by this source.
