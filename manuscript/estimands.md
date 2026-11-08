# What each analysis bounds: the allowed claims

The interpretation specification for the SS Cyg paper. Every rendering (article, supplement, brief,
agent guide) states each result only in these terms. Claude and Codex maintain it jointly and Barry
reviews it; change it before changing the prose. First drafted by Claude on 9 November 2026 in the A10j
review (`docs/audits/2026-11-09-a10j-result-review.md`). It awaits Codex's review.

A sentence passes only if its subject is the same object as the calculation. A caveat attached to a
sentence does not rescue it if its noun has changed, for example from "forecast gain under this
baseline" to "memory".

## Primary forecast gain (claims C01–C04)

- **Estimand:** the mean, over the 441 SS Cyg forecast issuances of 1960–2017, of the log-score
  difference between two forecasts of the next outburst onset. Both forecasts are frozen working
  lognormal landmark clocks fitted on 1910–1959 only. M3 adds the just-completed outburst's log
  duration to M2, which uses the previous quiescent gap and the recent gap level. It covers AAVSO
  visual (`Vis.`, validation `V`) observations, the X4 event extraction at magnitude 10, C1/7-day
  coverage, issue at the end-of-outburst landmark, and observation-time replay. The interval is
  six-year-cluster robust (CR1, Student t, 9 df).
- **Allowed:** "In a preregistered, frozen-parameter retrospective forecast test, adding the
  completed outburst's duration improved forecasts of the next SS Cyg outburst by 0.0165 nats per
  forecast (90% interval 0.0049–0.0281; 441 forecasts, 1960–2017). The single predeclared criterion
  was met." "Incremental predictive information beyond the specified timing baseline."
  "Observation-time retrospective." Express the size also as about 1.7% higher predictive likelihood
  per forecast, or as about 14% of what the timing baseline adds over a constant forecast.
- **Conditions that travel with it:** one star, one frozen visual extraction, one baseline. The
  post-access format repair (C05). The later segment and the type/within-type rule were inconclusive
  (C06, C08), and the exploratory reading is that the information is between outburst types (C21).
- **Not allowed:** "SS Cyg has memory"; "outburst duration determines (or causes, controls, sets) the
  next quiescent interval"; "confirms the disc-instability model"; any statement about "dwarf novae"
  in general; "operational forecasting" or "real-time forecasts"; "blind" or "untouched" holdout;
  "statistically significant at p = …" (the rule is an interval criterion); "the forecasts are well
  calibrated".

## Access record (C05)

- **Estimand:** the procedural history of the evaluation.
- **Allowed:** "The protocol was published (DOI 10.5281/zenodo.24053338) before the evaluation data
  were requested. The first run failed before any scoring because the archive used a literal `None`
  for missing uncertainty. One outcome-independent parser repair, to a field that no forecast uses,
  preceded the completed run. The failed attempt is preserved."
- **Not allowed:** "the DOI timestamps the analysis as run"; "the evaluation data were never
  accessed before scoring"; omitting the repair from any product that reports the result.

## Secondary comparisons (C06–C11)

- **Era split (C06, C07):** descriptive. 1960–1992 lies inside Cannizzo and Mattei's 1896–1992
  pooled sample (CM92). It was held out of this fit, but CM92 had already published an association
  that includes those years. 1993–2017 lies outside every published analysis of the duration–gap
  sign known to the project.
  - *Allowed:* "In 1993–2017 the gain was 0.0057 nats (−0.0107 to 0.0221): inconclusive."
  - *Not allowed:* "the effect disappeared (or weakened) after 1992"; "replicated in independent
    data"; "stronger in the early era" as a finding; any era-difference test (none was specified).
- **Type/within-type rule (C08):**
  - *Allowed:* "The predeclared type/within-type rule was inconclusive (0.0025 nats, −0.0022 to
    0.0072). As frozen, its type term could lengthen forecasts after long outbursts but not shorten
    them after short ones (C22)."
  - *Not allowed:* "the information is not about outburst type"; "the type test contradicts the
    primary".
- **Sensitivities (C09):** uniform-end marks, previous-gap-only baseline, 2-day delay, joint-valid
  rows and 3-year clusters all give 0.0165–0.0170 with positive lower bounds. They are sensitivities,
  not further confirmations.
- **Timing baseline (C10):** M2 beats the constant forecast by 0.117 nats. This shows a non-trivial
  baseline, not that M2 is the best timing model.
- **Calibration (C11):**
  - *Allowed:* "Absolute predictive intervals overcover: nominal 50% intervals cover 55–62% and
    nominal 90% cover 92–98% (partial-identification bounds)."
  - *Not allowed:* "calibrated forecasts"; "coverage confidence intervals".

## Association diagnostics (C12, C13)

- **Estimand:** evaluation-only offsets with M2 refitted to 1960–2017 and held fixed. These are
  working-likelihood support intervals, not dependence- or measurement-calibrated confidence
  intervals.
- **Allowed:** "Fitted alone, the previous outburst's duration has a negative offset. That is what
  long/short alternation (C24) and a positive current-type effect jointly imply. Fitted jointly, both
  offsets' support intervals include zero."
- **Not allowed:** "rules out a shared state"; "identifies memory"; "the lag test is significant".

## Exploratory post-result analyses (C20–C25)

All computed after the primary result existed, by Claude (A10j). Every product labels them
"exploratory, post-result". None is a second confirmation, and none may be described as a test
that passed.

- **Level versus slope (C20):** about a fifth of the frozen gain (0.0037 of 0.0165) comes from the
  duration term partly correcting a level bias. The frozen M2 forecasts gaps about 4.6% too long in
  1960–2017, and both durations and gaps are shorter than in 1910–1959. The remainder (0.0128) is
  within-era information.
  - *Not allowed:* "the gain is an artefact of drift"; "the gain is free of drift".
- **Type versus within-type (C21):** with the frozen M2 nuisance and a free level, the long/short
  type indicator explains the evaluation data better than continuous log duration (LR 14.7 vs 11.7
  against level only). Within-type duration adds nothing detectable (LR 0.17). In 1910–1959, type
  and continuous duration were equivalent (LR 5.17 vs 5.19). The gap after a long outburst is about
  14% longer than after a short one in 1960–2017, and about 10% longer in 1910–1959.
  - *Allowed:* "the predictive information is carried by outburst type".
  - *Not allowed:* "we show that outburst type causes"; "confirmed type effect"; "within-type duration
    has no effect" (only "added nothing detectable").
- **Frozen type rule at a common level (C22):** given the same evaluation level shift as M2, the frozen
  type rule gains 0.0091 nats (0.0041–0.0140). This diagnoses a parameterisation interaction. It does
  not rescue the predeclared rule's result.
- **Alternation (C24):** successive log durations correlate at −0.52 in 1960–2017 (−0.40 in
  1910–1959, matching CM92's −0.400). A long outburst is followed by another long one 15% of the
  time.
  - *Not allowed:* "we discovered alternation" (CM92 prior art).
- **Robustness of the headline (C25):** 8 of 10 six-year blocks positive; dropping any one block leaves
  0.0132–0.0194; the criterion survives an SE up to 1.43 times larger.

## Simulation operating characteristics (C30–C33)

- **Allowed:** "Power at the simulated published-size effect was 27.5% (11 of 40; exact 95%
  14.6–43.9%). Across 220 gated no-effect histories the rule confirmed three times; the histories share
  random streams, so this is a finite screen, not a certified 5% error rate. Under the injected effect,
  34 of 40 two-sided 90% intervals contained the target."
- **Not allowed:** "the test has a 5% false-positive rate"; "certified size"; "well-powered".

## Development fit (C14)

- **Allowed:** "In-sample on 1910–1959, the duration offset was 0.0466 per SD of log duration, LR 5.19
  against M2." Label it in-sample and say that it overlaps CM92's sample.
- **Not allowed:** citing it as evidence for the claim.

## Prior art and novelty (C40, C41)

- CM92 reported, for 705 SS Cyg outbursts from 1896 to 1992, r(D, following Q) = 0.223,
  r(D_i, D_i+1) = −0.400, a bimodal duration split at 12 d, and the cycle-convention trap.
  Cannizzo (1993) gives the disc-instability account of long/short alternation (full text still to be
  read before any detailed statement).
- **Allowed novelty:** "the first preregistered, frozen-parameter, held-out forecast evaluation of
  dwarf-nova recurrence known to us"; "the duration–gap association, as forecast skill, holds in data
  not used to fit the model".
- **Not allowed:** "we discovered that duration predicts the following quiescence"; "first evidence of
  memory"; "first study of SS Cyg outburst statistics".
