# What each analysis bounds: the allowed claims

This specification governs the article, supplement, brief, figures and agent guide. Claude proposed
it in A10j; Codex's A10k review independently reproduced the requested numbers and narrowed several
interpretations before figure captions. Claude accepted every A10k narrowing in A10l (D030), added
the source-checked physical reading and the narrowed novelty wording below, and drafted the products
against this version. Barry reviews the final research products. The primary estimand and test are
unchanged. The review records are `docs/audits/2026-11-09-a10k-claims-and-figures.md` and
`docs/audits/2026-11-09-a10l-sources-and-drafts.md`.

A sentence must name the object that was calculated. A caveat cannot turn a forecast comparison into
a mechanism test, an in-sample fit into validated prediction, or a clock parameter into an observed
waiting-time contrast.

## Primary forecast gain (C01–C04)

- **Estimand:** the mean paired log-score difference over the 441 SS Cyg issuances in 1960–2017.
  The target is the next extracted onset, conditional on the information at the observed
  end-of-outburst issue landmark. Frozen working lognormal clocks were fitted on 1910–1959 only.
  M2 uses the previous covered quiet gap and recent gap level; M3 adds current log duration.
  The result is conditional on archived `Vis.`/validation-`V` observations, X4 at magnitude ten,
  C1/seven-day coverage, score eligibility and observation-time replay. The interval uses CR1,
  six-year clusters and Student t with nine degrees of freedom.
- **Allowed:** “In a preregistered, frozen-parameter retrospective comparison, adding completed
  outburst duration improved the next-onset forecasts of SS Cyg by 0.0165 nats per issuance
  (90% interval 0.0049–0.0281; 441 issuances, 1960–2017). The predeclared rule was met.”
  “Incremental information beyond the specified measured-history timing baseline.”
- **Size in other units (C02):** exponentiating the mean log-score gain gives a geometric mean
  likelihood ratio, about 1.017. This can be called about 1.7% higher geometric mean likelihood
  for the scored evidence. It is not an accuracy percentage or the arithmetic mean probability
  gain. The ratio to M2's mean gain over M0 is about 14%; this is not variance explained.
- **Conditions beside the headline:** one star, one extraction, one frozen baseline; the
  post-access repair (C05); the inconclusive later segment and type/within-type rule (C07, C08).
- **Not allowed:** physical memory, causation, confirmation of a disc mechanism, generality to
  dwarf novae, operational forecasts, a blind/untouched evaluation, well-calibrated predictions,
  or an additional confirmatory test chosen after inspection. The rule was an interval criterion.

## Access record (C05)

The protocol DOI predates the first evaluation request. That attempt failed before scoring on exact
`uncert="None"`; an independently reviewed format repair accepted that missing-uncertainty field
without dropping or altering an observation. No forecasting path uses uncertainty. The failed
attempt remains preserved. Every product reporting the primary result states that the completed
run followed this post-access format repair. The DOI does not timestamp the repaired code, and the
evaluation cannot regain untouched status.

## Predeclared secondary comparisons (C06–C11)

- **Eras (C06, C07):** the estimates are descriptive. The early segment overlaps the CM92 record,
  while the later segment is outside the published duration–gap sign analyses known to this
  project. The later gain, 0.0057 [−0.0107,0.0221], is inconclusive. Era intervals overlap; there
  was no prespecified era-difference test. Claim neither disappearance nor independent replication.
- **Type/within-type rule (C08):** its frozen gain, 0.0025 [−0.0022,0.0072], is inconclusive. The
  nonnegative uncentred type component is zero after short outbursts. The whole rule also has a
  centred within-type term, and can shorten some short-outburst forecasts. C22 explores a shared
  level adjustment; it does not replace C08 or establish a validated corrected type forecast.
- **Sensitivities (C09):** uniform-end marks, previous-gap-only baseline, two-day delay,
  joint-valid rows and three-year clusters give positive lower bounds. These probe the same
  comparison and are not additional independent confirmations.
- **Timing baseline (C10):** M2's gain over M0 is non-trivial. It does not establish that M2 is the
  best activity model or eliminate latent-state explanations.
- **Calibration (C11):** the realised sample has overcoverage: the nominal central intervals
  cover more observations than their nominal fractions. The ranges are partial-identification
  bounds conditional on extracted onset brackets and censoring, over all scored issuances.
  They are neither confidence intervals for population coverage nor guaranteed coverage of true
  physical onsets. Selected-onset mid-CDF deciles are descriptive; no uniformity test is claimed.

## Evaluation-only association diagnostics (C12, C13)

The signed offsets are fitted after the result, with evaluation M2 refitted and held fixed. Their
LR support intervals do not propagate baseline, dependence or measurement uncertainty.

The separate negative lag coefficient is **compatible with** alternation and a positive current-mark
association. Its origin is not causally decomposed. The joint design is correlated but full rank,
with a modest condition number of 1.79. Both conditional support intervals include zero; correlation
alone does not explain that result or establish coefficient nonidentifiability. These timings do
not identify a physical mechanism. A negative net lag can coexist with a positive slow component;
A10k supplies an analytic counterexample, not an empirical rival fit.

## Exploratory post-result calculations (C20–C25)

All are explicitly labelled **exploratory, post-result**. Refits and evaluation-fitted adjustments
reuse the evaluation outcomes. Their descriptive intervals condition on those choices rather than
propagate all their estimation uncertainty. None supplies another held-out confirmation.

- **Global recentering and level shifts (C20):** shifting M2 by the frozen mark's evaluation mean
  contribution gives about 0.00370 nats; globally recentering that mark gives a 0.01283-nat score
  contrast. The two orderings differ by about 0.000012 nats, so this is an approximately additive,
  ordering-dependent description. It is not a causal partition. A single global mean does not
  remove drift within the evaluation period. Avoid “genuine/drift-free within-period information”.
  The best evaluation log-location shift reduces the original untruncated clock scale by about
  4.57%; it does not directly estimate empirical forecast bias or the conditional remaining wait.
- **Duration classes (C21):** with historical M2 nuisance held fixed and a free level, the
  type-only model reaches a larger in-sample likelihood than linear log duration (LR 14.7 versus
  11.7 against level only). Those equally dimensional models are nonnested. Adding linear
  within-type duration changes the likelihood little (LR 0.17); no equivalence/absence test was
  performed. This is compatible with a parsimonious class interpretation, not proof that all
  predictive information resides in type. The development fits were similar, not proven equivalent.
  Exponentiating the type coefficient gives about a 14% ratio of **untruncated working-clock
  scales**, conditional on model covariates. It is not directly an observed mean-gap difference or
  a remaining-wait contrast. “About five days” is permissible only as an explicitly chosen
  illustration at a 36-day clock scale, not an empirical gap estimate.
- **Shared level adjustment (C22):** the frozen type-plus-within rule gains about 0.00905 nats
  when both models receive M2's evaluation-fitted common level. This shows sensitivity to coding
  and baseline calibration. It does not uniquely explain the original weak score or rescue C08.
  The restriction concerns the type component alone. Future fixed-baseline contrasts should define
  indicator coding and intercept freedom together; centring is not a universal rule for all models.
- **Era-specific type refits (C23):** conditional fit estimates, without a temporal-change test.
- **Alternation (C24):** these are positive-duration pairs at forecast issuances, including one
  repeat-flagged record, not a catalog of independent unique consecutive outbursts. The joint
  model's subset is different. Alternation is prior art. Negative marginal/lag relationships do
  not by themselves exclude a dominant slow driver coexisting with a stronger alternating component.
- **Block and SE diagnostics (C25):** eight block means are positive; leave-one-block-out
  **means** stay positive. The strict rule fails at an SE multiplier of about 1.42705: a 42%
  inflation still passes, an exact 43% does not. This arithmetic holds the estimate, t critical
  value and block definition fixed. It does not validate dependence, compensate every uncertainty
  source, or show that every omission retains the original interval decision.

## Simulations and development (C14, C30–C33)

The development likelihood result is in-sample and overlaps CM92's record. A10d power and containment
are scenario-specific. Pooled no-effect histories share streams: their count is a finite screen,
not an iid error-rate estimate or certification of nominal size. The simulation reference mean has
Monte Carlo uncertainty and is not a second confirmatory target.

## Prior art, novelty and future data (C40, C41)

- **CM92 (C40):** Claude re-read Table 4 and the Fig. 5 subscript conventions on the original scan
  (A10l). The quiescence after an outburst correlates with its duration at r = 0.223 and the
  quiescence before it at 0.282; successive durations at −0.400; 401 of 705 durations fall below
  12 d. CM92 read the positive successive-quiescence correlations as a hint of secular variation.
  Allowed: “CM92 reported the association, the alternation and the split”. Not allowed: “we
  discover”, or attributing to CM92 a forecast or a test of duration beyond the preceding quiescence.
- **Novelty (C41):** one prior held-out timing forecast exists: Grigorievskiy et al. (2014) scored
  point forecasts of outburst onset for V363 Lyr from Kepler photometry, with a single test outburst.
  Allowed: “to our knowledge, the first preregistered, frozen-parameter probabilistic evaluation of
  dwarf-nova recurrence forecasts on held-out data, and the first test of whether the completed
  outburst's duration adds forecast skill”. Not allowed: “the first out-of-sample forecast of
  dwarf-nova outbursts”, or any unqualified priority claim. Searches are bounded (no ADS export).
- **Physical reading (Cannizzo 1993):** in that disc-instability model tuned to SS Cyg, long
  outbursts accrete a larger share of the disc than short ones (about 30% against 3% at the model's
  default resolution, falling as resolution rises), and the depleted outer disc tends to make the
  next outburst short: an account of alternation. Outbursts start near the inner edge, so model
  quiescent intervals follow the quiescent viscous drift time. Separately, moving averages of the
  real light curve show longer recurrence times where the long-to-short ratio is higher, which the
  model reproduces through slow parameter changes. Allowed: the forecast gain is **compatible
  with** a cycle-to-cycle disc-mass account and with duration acting as a proxy for a slowly
  varying state that the recent-gap level does not fully capture. Not allowed: “confirms the disc
  instability model”, “demonstrates disc-mass memory”, or a prediction attributed to the 1993
  model that it did not make (Claude's reading found no reported quiescence contrast after long
  versus short outbursts).

Bibliographic metadata retrieval is not a full-text check.

2018 onward stays closed. Forecast counts or precision projected from earlier rates are planning
assumptions, never observed counts from that period. No future protocol, data opening, operational
forecast publication or venue/submission decision is made by this figure/build milestone.
