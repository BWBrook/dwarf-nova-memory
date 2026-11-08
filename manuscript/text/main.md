# Does the length of an outburst predict the wait for the next? A preregistered forecast test for SS Cygni

**Draft for review, 9 November 2026. Release and submission are Barry W. Brook's decisions.**
<div id="authors"></div>

## Abstract

Visual observers have recorded the outbursts of the dwarf nova SS Cygni almost continuously since
1896. Earlier analyses reported that longer outbursts tend to be followed by longer quiet intervals,
but those were in-sample correlations, and the best-known version partly reflected how cycles were
defined. We asked a narrower forecasting question. Once an outburst has ended, does its duration
improve a probabilistic forecast of the next onset, beyond what the recent quiet intervals already
say? We extracted outbursts from archived visual estimates with a threshold-crossing method qualified
on synthetic histories. We fitted lognormal forecast clocks to 1910–1959 only, froze them, published
the protocol with a DOI, and then scored forecasts issued at the end of each outburst from 1960 to
2017. Adding duration improved the log score by [0.0165]{.C01 .V001} nats per forecast (90% cluster
interval [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}; [441]{.C01 .V004} forecasts). The
predeclared criterion was met. The gain corresponds to a [1.7]{.C02}% higher geometric mean
likelihood of the observed outcomes. The evaluation was completed after a documented post-access
repair to the parser, for a missing-uncertainty token that no forecast uses []{.C05}. Two predeclared
secondary comparisons were inconclusive. One was the later segment, 1993–2017
([0.0057]{.C07}; [−0.0107]{.C07} to [0.0221]{.C07}). The other was a rule built on the 12-day
long/short outburst classes ([0.0025]{.C08}; [−0.0022]{.C08} to [0.0072]{.C08}). Exploratory fits
made after the result favour a long/short class indicator over continuous duration. They also
suggest that the class rule's weak score reflects how its class term was coded against the fixed
baseline. These fits supply no further confirmation. The result establishes incremental predictive
information in the completed outburst for one star, under one extraction and one timing baseline. It
does not establish physical memory, identify a mechanism, or carry over to other dwarf novae.

## 1. Introduction

Dwarf novae are close binaries in which a white dwarf accretes from a low-mass companion through a
disc. Every few weeks to months the disc brightens by several magnitudes for days to weeks and then
fades again. The disc instability model explains these outbursts as a limit cycle. Hydrogen
ionisation makes the disc thermally unstable, so it switches between a cool low-viscosity state that
stores mass and a hot high-viscosity state that drains it
[@lasota2001DiscInstabilityModel; @hameury2020ReviewDiscInstability]. Recurrence is quasi-periodic,
not periodic. Whether one outburst carries information about the next is therefore a question about
how much of the disc's state survives a cycle and can be read from the light curve.

SS Cygni is the natural test case. It is the brightest dwarf nova in the northern sky. Its light
curve, built from visual estimates archived by the American Association of Variable Star Observers
(AAVSO), runs almost unbroken from 1896. Bath and van Paradijs described SS Cyg as a relaxation
oscillator, with outburst energy related to the following waiting period
[@bath1983OutburstPeriodenergyRelations]. Cannizzo and Mattei then analysed 705 outbursts from 1896 to
1992 [@cannizzo1992LongtermBehaviorSS, hereafter CM92] []{.C40}. They showed that a correlation
between an outburst's duration and the "following cycle" largely reflects the cycle containing the
duration. They recommended the quiet interval instead.

On that footing CM92 reported the following correlations:

- duration with the following quiescence, r = [0.223]{.C40};
- duration with the preceding quiescence, [0.282]{.C40};
- successive durations, [−0.400]{.C40}, a strong alternation of long and short outbursts;
- durations split cleanly into two classes at about [12]{.C40} days.

They read the positive correlation between successive quiet intervals as a hint of secular
variation. Hempelmann and Kurths (1990, *Astronomy and Astrophysics* 232, 356) found short-range
dependence and possible long-range memory in a symbolic sequence of outburst widths. Searches for
low-dimensional chaos found no attractor [@cannizzo1988ChaosSSCygni]. Cannizzo's disc-instability
calculations tuned to SS Cyg reproduce the alternation [@cannizzo1993AccretionDiskLimit]. In those
calculations a long outburst drains more of the disc than a short one, and the depleted outer disc
tends to make the next outburst short. Moving averages of the real light curve also showed longer
recurrence times where long outbursts were relatively more common. The calculations reproduce that
relation through slow changes in disc parameters, not through changes in the mass-transfer rate.

All of this work describes associations within the record it analysed. None of it asks whether
the duration of a completed outburst improves forecasts of the next onset on data not used to
build the forecast. That question differs from the correlations. A forecast may use only information
available when it is issued. It must beat a baseline that already knows the recent rhythm of
quiet intervals. A proper scoring rule must reward it for the whole predictive distribution, not
for a point estimate [@gneiting2007StrictlyProperScoring]. Evaluation must also respect time order
[@burkner2020ApproximateLeavefutureoutCrossvalidation]. The only held-out timing forecast of a dwarf
nova we found is a machine-learning study of the Kepler light curve of V363 Lyr (Grigorievskiy et al.
2014, ITISE proceedings). It scored point forecasts of onset position on a single test outburst. A
search for short-term photometric precursors of SS Cyg outbursts found none
[@price2007SSCygniOutburst].

We report a preregistered, frozen-parameter test of one question. Does a forecast that knows the
completed outburst's duration assign higher probability to the next extracted onset than one that
knows only the recent quiet intervals? To our knowledge this is the first preregistered probabilistic
evaluation of dwarf-nova recurrence forecasts on held-out data, and the first test of whether the
completed outburst's duration adds forecast skill []{.C41}. Section 2 sets out the evidence and design, Section 3
the results, and Section 4 what they do and do not support. The supplement holds the definitions,
methods, sensitivities and the record of corrections made during review.

## 2. Evidence

### 2.1 Observations and outburst extraction

We used AAVSO International Database visual estimates of SS Cyg, keeping only rows in the `Vis.`
band with validation flag `V`. The 1960–2017 evaluation window contains [249,356]{.C15} such rows,
out of [500,479]{.C15} deduplicated archive rows []{.C15}. Earlier rows supplied the development fit
(1910–1959) and the causal history before 1960. Raw observations and observer identities are not
redistributed.

Outbursts were extracted by a threshold-crossing method, X4, at visual magnitude 10, CM92's
threshold (Supplement S2.1). For each candidate episode, X4 forms a posterior for the times at
which the brightening and fading curves cross the threshold. It includes a shared systematic error so
that the crossing intervals do not narrow artificially when many observers report. An episode is
confirmed by two observers, or by one observer on two nights well past the threshold with no
contradicting faint report. Before any real-star forecast was scored, X4 and a coverage rule, C1/7
d, were qualified on synthetic histories with realistic observer cadence. The coverage rule treats a
gap of more than seven days between visits as a loss of coverage. The qualification was conditional:
an unseen waveform family failed, and diagnostics at magnitude 9.5 failed in later eras. The
magnitude-10 extraction is therefore part of the estimand, not a neutral measurement.

### 2.2 Forecasts, outcomes and models

Each observation-time confirmation that an outburst has ended issues one forecast. Its predictors
come only from the 400 days of observations before that moment. A test with deliberately poisoned
future rows enforces this. The predictors are the following:

- **duration:** the completed outburst's onset-to-end time, from the prefix extraction;
- **previous gap:** the preceding quiet interval, if covered;
- **recent level:** the mean of up to six earlier covered log quiet intervals.

The outcome is the next extracted onset bracket. The bracket comes from the full record up to the
end of the block, and serves only for scoring. A forecast is right-censored at the earliest of
coverage loss, the next forecast's issue time, or the end of the block.

Each model is a lognormal clock for the quiet interval, conditioned on survival to the age at issue:

- **M0:** a constant;
- **M2:** M0 plus the standardised log previous gap and the recent level;
- **M3:** M2 plus $\beta$ times the standardised log duration, with $\beta$ constrained to be non-negative.

We fitted M2 on 1910–1959, then fitted $\beta$ with M2's parameters held fixed, and froze all parameters.
The development fit gave $\beta$ = [0.0466]{.C04} per standard deviation of log duration []{.C14}.
Forecasts without a covered previous gap use M0 for both models and contribute exactly zero to the
contrast.

### 2.3 The primary test and the access record

The single confirmatory statistic is the mean paired log-score gain of M3 over M2 across all
score-eligible 1960–2017 issuances, including the fallback zeros. Its uncertainty comes from
consecutive six-year calendar clusters, a small-sample-corrected cluster-robust standard error and
Student's t with nine degrees of freedom. The result counts as confirmed if the one-sided 95% lower
bound exceeds zero. The protocol named the era split, the long/short class rule, several sensitivity
variants and calibration diagnostics as secondary analyses that cannot replace the primary.

The protocol was published with a DOI, 10.5281/zenodo.24053338, minutes before the first request
for evaluation data. That first attempt stopped before any ledger or score was computed. The
archive returns an uncertainty field as the literal token `None` for missing values, which the
parser rejected. The uncertainty field enters no extraction, feature, routing or score. An
independently reviewed repair accepted that exact token without altering or dropping any
observation. Synthetic invariance tests, the full test suite and a new rehearsal passed before the
run continued. No magnitude, outcome, count or score informed the repair. The failed attempt is
preserved. The evaluation therefore cannot be described as untouched, and the DOI timestamps the
original protocol, not the repair []{.C05}. Data from 2018 onward remain closed.

**Table 1.** Pivotal inputs, what each shows directly, and what a stronger claim would also need.

| Input | Shows directly | Used for | A stronger claim would need |
|---|---|---|---|
| AAVSO visual estimates, 1910–2017 | Brightness reports by many observers | All events, predictors and outcomes | Independent photometry or a second extraction |
| X4 extraction at magnitude 10, C1/7 d | Onset and end brackets, coverage | Durations, gaps, outcome brackets | Qualification on unseen waveforms and other thresholds |
| Frozen M0, M2, M3 (1910–1959 fit) | Forecast distributions | The scored comparison | Comparison with stronger latent-state baselines |
| Protocol DOI and access record | Order of publication and data access | Status of the test | A fully untouched evaluation, now impossible for 1960–2017 |
| CM92 Table 4 | Published in-sample correlations, 1896–1992 | Prior direction and expected size | Not applicable: prior art, not evidence for the result |

## 3. Results

### 3.1 The primary comparison

The predeclared criterion was met (Fig. 2). Across [441]{.C01 .V004} issuances, adding the completed
outburst's duration raised the mean log score by [0.0165]{.C01 .V001} nats per issuance, with 90%
cluster interval [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}. Exponentiated, this is a [1.7]{.C02}%
higher geometric mean likelihood of the scored outcomes. It is neither an accuracy percentage nor
an arithmetic probability gain. Timing models were used on [436]{.C03} issuances and the shared
fallback on [5]{.C03}. The outcomes comprised [435]{.C03} onset brackets and [6]{.C03}
right-censored cases. The baseline itself is not trivial: M2 beat the constant M0 by
[0.117]{.C10} nats per issuance ([0.066]{.C10} to [0.167]{.C10}). The duration gain is about
[14]{.C02}% of that baseline gain, a ratio that should not be read as variance explained.

[8]{.C25} of the ten blocks have positive means (Fig. 2A). Leaving out any one block gives means
between [0.0132]{.C25} and [0.0194]{.C25}. With the estimate and critical value held fixed, the
decision would fail only if the standard error were inflated by a factor of [1.427]{.C25} or
more []{.C25}. Every protocol sensitivity kept a positive lower bound. That includes uniform end
uncertainty ([0.0166]{.C09}, lower bound [0.0045]{.C09}), the previous-gap-only baseline
([0.0170]{.C09}, [0.0054]{.C09}), a two-day issue delay ([0.0165]{.C09}, [0.0049]{.C09}), the
joint-valid rows ([0.0167]{.C09}, [0.0049]{.C09}) and three-year clusters (lower bound
[0.0059]{.C09}). These probe the same comparison and are not further confirmations.

Fig. 1 shows one forecast, selected by observation time rather than by score. It illustrates the
information available at issue.

### 3.2 Predeclared qualifications

The two era segments differ in estimate but not decisively (Fig. 2B). The segment 1960–1992 gave
[0.0240]{.C06} ([0.0091]{.C06} to [0.0389]{.C06}; [261]{.C06} issuances). These years were held
out of the fit, but they overlap the record behind CM92's published association []{.C06}. The
segment 1993–2017, outside the published sign analyses we know of, gave [0.0057]{.C07}
([−0.0107]{.C07} to [0.0221]{.C07}; [180]{.C07} issuances). That is inconclusive. The intervals
overlap, no era-difference test was specified, and the result is not evidence that the gain
disappeared.

The predeclared class rule used a 12-day long/short indicator plus a within-class duration term.
It gained [0.0025]{.C08} ([−0.0022]{.C08} to [0.0072]{.C08}), also inconclusive. Section 3.4
examines why.

Calibration is a separate question from relative skill. The realised sample overcovers (Fig. 3).
M3's nominal 50% central intervals contained between [0.55]{.C11} and [0.62]{.C11} of outcomes.
Its nominal 90% intervals contained between [0.92]{.C11} and [0.98]{.C11}. These are
partial-identification bounds given the extracted brackets and censoring, not confidence intervals
for a population coverage rate. The positive paired gain does not imply sharply calibrated
operational forecasts.

### 3.3 Why the held-out gain exceeds the development expectation

The development fit was in-sample and modest: a likelihood-ratio statistic of [5.19]{.C14} against
M2 []{.C14}. In the operating-characteristic simulations, the reference injected effect gave a mean
gain of [0.0045]{.C33} nats, and at the published-size effect [11]{.C30} of 40 simulated evaluations
confirmed []{.C30}. The realised gain is larger than this model-specific reference. The reference
carries Monte Carlo uncertainty and was not a target, so this is not a claim that the effect exceeds
a known physical size.

A post-result decomposition, exploratory and conditional on evaluation-fitted adjustments, finds
part of the reason. Evaluation-era durations and gaps are both shorter than in 1910–1959. The best
common log-location shift for M2 is [−0.0468]{.C20}. That shift reduces the untruncated clock scale
by about 4.6%; it is not an estimate of bias in the remaining-wait forecasts. Because mean
standardised log duration is negative in the evaluation era, the duration term partly supplies this
level correction. That accounts for [0.0037]{.C20} nats ([0.0001]{.C20} to [0.0073]{.C20}). After
the duration is recentred at its evaluation mean, the score contrast is [0.0128]{.C20}
([0.0036]{.C20} to [0.0221]{.C20}) []{.C20}. A single global mean does not remove drift within the
period, and the two parts are a descriptive, approximately additive split, not a causal partition.

### 3.4 Exploratory: long/short class and alternation

All results in this subsection were computed after the primary result, using the evaluation
outcomes, and are labelled exploratory (Fig. 4). With M2's historical parameters fixed and a free
common level, a long/short indicator alone reaches a likelihood-ratio statistic of
[14.7]{.C21 .V005} against the level-only model. Continuous log duration reaches
[11.7]{.C21 .V006}. These equal-dimensional models are not nested. Adding linear within-class
duration to the indicator changes the statistic by [0.17]{.C21 .V007}. The fit therefore favours a
parsimonious class reading. It is not a test showing that duration within a class adds nothing. In
the development years the two forms fit about equally well []{.C21}. The fitted class contrast
corresponds to a [14]{.C21 .V008}% larger untruncated clock scale after long outbursts, conditional
on the other covariates. This is a model-scale ratio, not an observed difference in mean waiting
times. Era-specific refits give larger class contrasts in 1960–1992 than in 1993–2017 []{.C23},
without an era-change test.

The predeclared class rule coded the class as an uncentred 0/1 indicator with a non-negative
coefficient, added to a baseline whose level was fixed. The class component could therefore only
lengthen forecasts after long outbursts, never shorten them after short ones. The rule's centred
within-class term could still shorten some short-outburst forecasts []{.C08}. When both rules
receive M2's evaluation-fitted common level, the frozen class rule gains about [0.009]{.C22} nats
([0.0041]{.C22} to [0.0140]{.C22}) []{.C22}. That shows sensitivity to coding and baseline
calibration. It neither rescues the original inconclusive result nor validates a corrected rule.
The lesson for future protocols is that indicator coding and intercept freedom must be specified
together.

Alternation is strong in the forecast record. The lag-one correlation of log duration is
[−0.52]{.C24}. A long outburst followed a long one in [0.15]{.C24} of pairs and followed a short one
in [0.66]{.C24} []{.C24}. Fitted separately on the evaluation data, with evaluation M2 refitted and
fixed, the current duration offset is positive ([0.042]{.C12}) and the previous outburst's is
negative ([−0.038]{.C12}) []{.C12}. Fitted jointly, both conditional support intervals include zero
[]{.C13}. The negative previous-duration coefficient is compatible with alternation combined with
a positive current association. Its causes have not been separated.

## 4. Discussion

### 4.1 What follows

For SS Cyg, the completed outburst carries usable information about when the next will begin. That
information goes beyond the recent quiet intervals that a timing-only forecaster already knows, and
it survived a frozen, preregistered test on 58 years of held-out record. CM92's in-sample
association thus has a forecast counterpart. The effect is small. A [1.7]{.C02}% geometric
likelihood gain would matter little to an observer planning a night at the telescope. It matters
more as a measured constraint on how much of the disc's state is visible in one outburst's length.

Two physical readings fit the result and we cannot separate them. In the cycle-to-cycle reading, a
long outburst drains more of the disc, and the drained disc both alternates the next outburst's type
and alters the interval before it. Cannizzo's model provides the first half of this account; we did
not find in it a reported contrast in quiescence after long versus short outbursts
[@cannizzo1993AccretionDiskLimit]. In the slow-state reading, duration acts as a proxy for a slowly
varying disc or transfer state that the recent-gap level does not fully capture. The observed
covariation of recurrence time with the long-to-short ratio points this way. The negative
previous-duration coefficient is compatible with alternation, but a negative net lag does not
exclude a dominant slow component coexisting with a stronger alternating one (Supplement S3.4).
Neither reading is a mechanism test, and the word "memory" should not be applied to the result
without a model that distinguishes them.

The weaker later segment is the most important open qualification. Its estimate is a quarter of the
earlier segment's, and the exploratory class contrast is smaller there too. The record gives no
basis for choosing between real change, a change in observing that alters extraction, and
sampling variation in 180 forecasts. The design did not specify an era test, so we do not claim one.

Measurement limits remain. The duration and the following gap share the estimated end time, so
end-time error couples them. The coefficient bound and matched routing were designed against the
negative coupling seen in simulations. An exact construction shows the coupling can also produce
positive information (Supplement S2.4). The uniform-end and delayed-issue sensitivities kept
positive lower bounds, which probes this route without excluding it. Informative observing, missed
outbursts and incomplete propagation of measurement error are further limits.

The study also carries lessons about method. The cycle convention that misled earlier work (CM92) has
a forecasting analogue. Any predictor computed from data after the issue time contaminates the
score, so we enforced observation-time features with poisoned-row tests. A component restriction in
a frozen model can silently cripple a secondary hypothesis, as the class rule showed. A post-access
format failure, however innocent, permanently changes what a test can be called. Recording it
openly is the only remedy.

### 4.2 Which conclusions depend on which assumptions

**Table 2.** Dependence of each main conclusion on its assumptions.

| Conclusion | Rests on | Fails if |
|---|---|---|
| Duration adds forecast information for SS Cyg, 1960–2017 | Frozen parameters; observation-time features; six-year clusters capture dependence | Look-ahead leakage is found; end-time coupling generates the gain; dependence spans much longer than six years, inflating the SE by a factor of [1.427]{.C25} or more |
| The gain is not a level artefact alone | Global recentring as a descriptive split | Within-period drift explains the recentred contrast (untested) |
| The information is mainly long/short class | Exploratory in-sample likelihoods | A held-out class test, properly coded, fails |
| The 1993–2017 segment does not show disappearance | Overlapping intervals; low power | A prespecified era test, or new data, shows a reliable decline |
| The extraction measures onsets well enough | X4 qualification at magnitude 10, C1/7 d | Real waveforms or cadence differ from the qualified families in ways that bias durations |

### 4.3 What would sharpen the answer

Four kinds of evidence would most improve these inferences.

- **A new frozen protocol for the closed data.** At the earlier issuance rate, the 2018-onward SS Cyg
  record would hold roughly 65 forecasts, a planning assumption and not a count. That is too few to
  test this effect alone. It should enter a new frozen protocol as one stratum
  of a multi-star test. That test should use a class rule whose indicator coding and intercept
  freedom are defined together, and treat the anomalous 2021 SS Cyg event
  [@kimura2021NatureAnomalousEvent] as a declared stress case.
- **Other long-record dwarf novae.** U Gem-type systems with long, well-sampled histories could test
  whether the result generalises. Their extraction must be qualified first.
- **An independent extraction for recent decades.** Photoelectric, CCD and space photometry would
  separate observing changes from physical change in the later segment.
- **Stronger timing baselines.** Latent-state models of the quiet-interval sequence would test
  whether duration remains informative once a slowly varying state is modelled explicitly.

## 5. Conclusions

The completed outburst's duration improved frozen probabilistic forecasts of SS Cyg's next onset
over a timing-only baseline, by [0.0165]{.C01 .V001} nats per forecast across [441]{.C01 .V004}
held-out forecasts from 1960 to 2017. The preregistered criterion was met after a documented
post-access parser repair. The gain was smaller and inconclusive in 1993–2017, and the predeclared
long/short class rule was inconclusive. Exploratory fits favour a class reading, while CM92 had
already reported the association, the alternation and the split. The result is a forecast fact
about one star under one extraction. Whether it reflects cycle-to-cycle disc depletion or a slowly
varying state, and whether it holds for other dwarf novae, remain open.

## Methods in brief

- **Definitions, readings and units:** Supplement S1.
- **Extraction, coverage, issuance, outcome and censoring rules, models, fitting, scoring and
  interval construction:** S2.
- **Sensitivities, calibration, development comparison, exploratory calculations and the slow-driver
  counterexample:** S3.
- **Corrections made during review:** S4.
- **Reproduction commands and the evidence map:** S5.

The claims ledger (`manuscript/claims.csv`) gives every quoted number with its evidence file, its
verifying commit, a reproduction command and its limits.

## Roles of AI systems and humans

This work was conducted by AI systems with a human scientific lead, and the record is public.

- **Barry W. Brook** (University of Tasmania) set the scientific direction and the data boundaries.
  He chose to publish the protocol on Zenodo before opening the evaluation data, and keeps the
  2018-onward record closed. He reviews the final products and decides on release and submission.
- **GPT-6 Pro** (OpenAI, through ChatGPT) produced the seed ideation and the first framework.
- **Claude Opus 5.5** (Anthropic, through Claude Code) did the following:
  - wrote the novelty and physical-framing audit;
  - developed and diagnosed the extraction methods, and wrote the X4 extractor and the first
    observation-time feature code;
  - proposed or reviewed each protocol;
  - reviewed the sealed result and ran the post-result exploratory analyses (A10j);
  - re-read the primary sources;
  - drafted this article, the supplement, the brief and the agent guide.

  A separate Claude Sonnet subagent refreshed the novelty search.
- **GPT-6 Codex** (OpenAI, through Codex) did the following:
  - implemented the forecasting, scoring, simulation and sealed-evaluation code;
  - executed the sealed evaluation and the format repair;
  - wrote the independent numerical audits of the result and the exploratory claims (A10k), which
    narrowed several of Claude's interpretations;
  - built the figures and the document toolchain.

Model names are the labels the systems reported on the project's correspondence board. Agreement
between models is not treated as independent validation. Independence rests on separately
implemented computational routes, which the audit records name. The human–AI correspondence is
published with the repository.

## Data and code

The repository <https://github.com/BWBrook/dwarf-nova-memory> holds the protocols, code, frozen
parameters, aggregate evidence, figures, claims ledger and the full access record. Code is MIT
licensed; text, figures and derived data are CC BY-SA 4.0. The evaluation protocol is archived at
<https://doi.org/10.5281/zenodo.24053338>.

AAVSO observations are available from the AAVSO International Database (<https://www.aavso.org>).
We do not redistribute raw observations, observer identities, event catalogues or per-forecast
scores. The supplement (S5) gives the commands that reproduce every reported number from the
retained run without new archive requests.

We thank the AAVSO observers whose century of visual estimates made this test possible.

## References
