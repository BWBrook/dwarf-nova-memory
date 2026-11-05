# Research brief

**Working title:** *Forecasting dwarf-nova recurrence: the incremental information
in completed outbursts under changing activity and incomplete observation.*

**Status:** proposed framework, 5 November 2026. The initial literature review is
not an exhaustive novelty assessment. All thresholds below are planning choices,
not established empirical properties or a preregistered protocol.

## 1. The central question

For a defined group of well-observed ordinary dwarf novae, does the duration or
other information in a completed outburst improve the probability forecast for
the next outburst, beyond a star-specific recurrence distribution and models
that allow the system's activity to change through time?

The first estimand is **incremental forecast performance**, evaluated on later
observations under a declared observation and event-inference protocol. A second,
more ambitious question is whether competing physical explanations can be
distinguished. These are different questions. Predictive value may arise because
the previous outburst is a useful indicator of an underlying state, even if it
does not itself influence the next event.

This matches the scientific lead's strengths in time series, imperfect
observation, simulation and prediction assessment. It requires learning the
physics of a bounded source class rather than solving disc magnetohydrodynamics.

## 2. Why the framing has changed from the initial idea

The general existence of outburst correlations or “memory” is not a novel
hypothesis. The literature includes historical single-system serial-dependence
studies and multi-system studies of light-curve properties. A reproduction and
extension must acknowledge those directly; see the evidence-linked review in
`02-literature-review.md`.

Two distinct 2016 catalogues also need to stay distinct: Coppejans et al.'s CRTS
outburst catalogue contains system-level summary information for 722 dwarf
novae; Otulakowska-Hypka, Olech and Patterson compiled a different set of
outburst properties and correlations. Neither title alone promises a clean,
complete, event-by-event history for the present forecasting task.

Sources: [Coppejans et al. 2016](https://doi.org/10.1093/mnras/stv2921);
[Otulakowska-Hypka et al. 2016](https://doi.org/10.1093/mnras/stw1120).

The candidate opening is the combination of:

1. Chronological prediction with only information available at each issue time.
2. Fair nonstationary as well as stationary recurrence baselines.
3. Explicit observing windows, boundary uncertainty and missing-event sensitivity.
4. Within-star estimation with calibrated uncertainty and a clear population scope.
5. A reproducible benchmark that reports calibrated gains and failures, rather
   than a long list of in-sample correlations.

This combination remains a **novelty candidate**. The agents must test it against
the closest papers before proceeding to a paper-scale analysis.

## 3. Operational definitions

For event i, let s_i be onset, e_i the operational end and D_i=e_i−s_i its
duration. Define Q_i=s_(i+1)−e_i as the following quiescent interval. The full
onset-to-onset cycle is C_i=D_i+Q_i.

The primary target is the distribution of Q_i, or its remaining duration at an
actual forecast issue time. D_i is the initial primary completed-outburst mark.
Band-specific relative fluence, peak excess and rise/decline shape are ancillary
features to add only if their uncertainty and coverage support doing so.

Forecasts begin when the end has been *observationally confirmed*, not when a
later reconstruction says the end occurred. If a days of verified quiescence
have already elapsed, forecast the remaining wait conditional on survival to a.
An unobserved interval is not verified survival. Details belong in the full
statistical design, including uncertain e_i and interrupted observation windows.

Duration and C_i are algebraically coupled. Even Q_i shares an uncertain end
boundary with D_i: an end error δ gives D_hat=D+δ and Q_hat=Q−δ. This motivates
joint endpoint treatment and deliberate error-injection tests.

## 4. Hypotheses and interpretable outcomes

| Label | Hypothesis | What would support it | What would not establish it |
|---|---|---|---|
| H1: predictive information | A completed outburst contributes useful information about the next one | Better out-of-time proper scores and calibrated intervals against appropriate baselines | An in-sample correlation or improved fit alone |
| H2: changing activity | Longer-term activity explains part of apparent dependence | Timing-state models improve forecasts and account for patterns across cycles | A hidden-state model fitting well without recovery checks |
| H3: robustness to observation | The inferred gain survives realistic observing and boundary errors | Consistency across observation designs and injection experiments | Merely conditioning on timestamps that were triggered by an outburst |
| H4: heterogeneity | Predictive value varies among systems or epochs | Identifiable within-star differences with uncertainty and independent evaluation | Pooling thousands of points and ignoring a small number of stars |
| H5: structural mechanism, later extension | Some dependence remains beyond a specified shared-state mechanism | Identifiable joint mark–state comparisons and independent physical evidence | A nonzero regression coefficient or predictive gain by itself |

The sign of the completed-duration effect is not fixed in advance. A larger
outburst could be associated with different replenishment conditions, residual
disc structure, or mass supply. A statistical sign cannot uniquely adjudicate
these. The review of the disc instability model provides the physical context,
not a universal signed prediction for every dwarf-nova subtype.

Source: [Hameury 2020](https://arxiv.org/abs/1910.01852).

## 5. Deliberately bounded first paper

Start with ordinary hydrogen-rich, predominantly nonmagnetic dwarf novae showing
frequent normal outbursts. Use a handful of benchmarks for feasibility, then a
conditionally larger cohort only if observational quality and effective sample
size justify it. The candidate table is an audit queue, not a final sample.

Treat SU UMa supercycles, WZ Sge rare events, Z Cam standstills, magnetic systems
and helium accretors as separate strata or follow-up projects. SS Cyg itself
must be checked for known unusual episodes; familiar names do not guarantee
stationarity. The target plan records these distinctions.

The first submission should deliver a carefully qualified event/forecast
benchmark, a comparison of modest models, and a clear answer about achievable
prediction. It need not introduce a new disc simulation or an automated survey
of every known dwarf nova. Archive metadata and unglamorous auditing are central
parts of the contribution.

## 6. Model ladder

| Model | Main information | Purpose |
|---|---|---|
| M0 | Star-specific renewal waiting-time distribution | Establish a meaningful baseline; “no cross-cycle memory” is not the same as Poisson |
| M1 | M0 plus completed-outburst mark | Estimate incremental prediction relative to stationary recurrence |
| M2 | Past timing and a changing activity state | Challenge mark effects with a nonstationary explanation |
| M3 | Changing activity plus completed mark | Test additional information beyond the timing-state baseline |

M0 should be flexible enough that a poor choice of gap distribution does not
manufacture a result. M2 may begin with a modest rolling/past-only baseline and
advance to latent-state inference when the data and simulations support it.
M3 versus M2 is a predictive comparison; a joint mark–state model is needed for
stronger structural interpretation. Avoid an unrestricted model search before
choosing an untouched evaluation period.

## 7. Deliverables and possible endings

**First checkpoint:** archived queries and hashed data; identity/time/filter
audit; six provisional benchmark dossiers; a manually reviewed event sample;
one historical reproduction; an explicit decision to proceed or narrow.

**If prediction improves:** report the magnitude and uncertainty of the gain,
where calibration holds, which stars/epochs contribute, and which alternatives
remain observationally indistinguishable.

**If prediction does not improve:** use simulations to distinguish a useful
upper bound from insufficient information. A null conclusion is publishable
only if the question, detectable effect range and comparison are worthwhile.

**If observation quality dominates:** a smaller methodological/benchmark study
may be defensible; otherwise stop and move to another candidate. The project
should be allowed to fail early rather than manufacture an astrophysical claim.

## 8. First-hour handoff

Run the seed checks, read the evidence register, then ask Claude to audit the
physical framing and nearest precedents while Codex audits the code and acquires
one authentic light curve through a documented route. Reverse the reviewer and
implementer roles for the next milestone. Neither agent's agreement substitutes
for reproducible evidence or expert astronomical interpretation.
