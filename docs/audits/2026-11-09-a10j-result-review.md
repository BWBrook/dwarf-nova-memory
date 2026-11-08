# A10j: review of the sealed SS Cyg result, and how the paper should frame it

**Subsequent review:** A10k independently reproduces these numbers but narrows the
interpretations of global recentering, class attribution, the whole class rule,
negative lag and the rounded SE margin. Read [the A10k review](2026-11-09-a10k-claims-and-figures.md)
and the current interpretation specification before quoting those passages.
The original review and aggregate results below are retained as history.

Claude, 9 November 2026, reviewing Codex's A10i result (`f05803c`, snapshot `9c98374`). Sections 3–6
are **exploratory and post-result**: every number in them was computed after the primary file
existed. None of it is a second confirmation, changes the frozen comparison, or bears on the closed
2018+ block. The numbers come from `scripts/a10j_postresult_review.py`, which writes aggregates only
to [the A10j summary](../../data/provenance/a10j_postresult_review/summary.json). The paper's
interpretation specification and claims ledger, seeded here, are
[`manuscript/estimands.md`](../../manuscript/estimands.md) and
[`manuscript/claims.csv`](../../manuscript/claims.csv). Claim IDs below refer to that ledger.

## Verdict

**I accept A10i.** The predeclared criterion is met. I recomputed the result by a separate route, and
it does not depend on any single six-year block. The post-access repair is outcome-independent and
honestly labelled. Codex's narrow reading is correct: incremental forecast information under this
extraction and baseline, not memory, mechanism or a general dwarf-nova result.

The exploratory analysis adds three things the paper needs:

1. **Most of the gain is within-era information.** About a fifth (0.0037 of 0.0165 nats) comes from
   the duration term partly correcting a level bias in the frozen baseline (C20).
2. **The information is carried by outburst type.** Long versus short explains the 1960–2017 data
   better than continuous log duration. Within-type duration adds nothing detectable (C21). The A01
   audit predicted this ("duration is a type label first") before any evaluation access.
3. **The type/within-type rule's weak score is a parameterisation interaction.** It is not evidence
   against a type effect (C08, C22). Codex and I both missed this before the freeze; section 4
   explains it.

## 1. Independent verification

| Check | Route | Result |
|---|---|---|
| Primary interval | My CR1 estimator on the 441 saved gains; the frozen interval module is not imported | Estimate, SE 0.0063203 and bounds [0.0049477, 0.028119] match `primary.json` to 1e-12 |
| Small-sample factor | CR0 without G/(G−1) | Lower bound 0.0055; the reported CR1 is the more conservative |
| Variants and eras | Same estimator on each saved score file | All six variants, M2−M0, both eras and three-year clusters reproduce A10i |
| Routes and outcomes | Recount from saved scores | 436 timing and 5 fallback rows; 435 interval and 6 right-censored outcomes; fallback gains exactly zero |
| Score recomputation | The independent checker's scalar score function | Maximum discrepancy 1.4e-13 against saved M2 and M3 scores |
| Refit machinery | Separate Nelder–Mead refit on 1910–1959 | Reproduces the frozen duration offset (0.04660) and the development LR (5.1935) exactly |

The score recomputation uses Codex's checker code, so it is not independent of the checker. The
interval, influence and refit computations are mine.

**Robustness (C25).**

- Eight of the ten six-year blocks are positive.
- Dropping any one block leaves a gain between 0.0132 and 0.0194.
- The criterion survives an SE up to 1.43 times the reported one. That margin matters because
  injected-effect interval containment in A10d was 85%, so the reported intervals run somewhat narrow.
- Per-issuance gains are heavy-tailed in both directions (54% positive; median 0.0078). The cluster
  SE carries that.

## 2. The repair and the access record

D026 is sound. The literal `None` sits in an uncertainty field that no extraction, feature, routing
or score path reads. The repair accepts exactly that token and changes no row. It was frozen, tested,
rehearsed and authorised before continuation, and the failed attempt is preserved. "Frozen test after
a post-access format repair" is the right label. Every product must say so in the sentence that
reports the result, not only in the methods. The DOI timestamps the original protocol, not the repair
(C05).

## 3. Why the held-out gain is twice the development gain (exploratory)

The held-out gain (0.0165) is about twice the in-sample development gain (0.0079). Held-out skill
normally falls below in-sample, so this needs explaining before a referee asks.

**Outbursts and gaps are both shorter in 1960–2017.** The mean standardised log duration is −0.24 and
the mean previous gap is −0.25 SD against the 1910–1959 training values.

**The frozen M2 therefore over-predicts.** Its best single level correction on 1960–2017 is −0.047 in
log gap, so it forecasts gaps about 4.6% too long. Its previous-gap and recent-level slopes are too
weak to follow the shift.

**M3 corrects a little of that bias.** Because durations are shorter, β·x̄ shifts M3's forecasts down
by 0.011 on average. The gain splits as follows (C20):

| Part | Gain, nats/issuance | 90% cluster interval |
|---|---:|---:|
| Frozen M3 − M2 (the primary) | 0.0165 | [0.0049, 0.0281] |
| Level part: M2 shifted by β·x̄, minus M2 | 0.0037 | [0.0001, 0.0073] |
| Within-era part: M3 with the mark recentred on the evaluation mean, minus M2 | 0.0128 | [0.0036, 0.0221] |
| M3 − M2 when both receive M2's best evaluation level | 0.0124 | [0.0010, 0.0238] |

The two orderings of the decomposition agree to 1e-5. With a free level and the frozen M2 nuisance
parameters, the evaluation slope is 0.056 per training SD, against 0.047 frozen. The remaining
doubling therefore comes from a somewhat stronger within-era association plus the level part.

**What the level part means.** It is real predictive information: a forecaster using durations really
does better. It is also the signature of a slow common change in durations and gaps between the two
periods. That might be physical, a change in SS Cyg's activity, or measurement, a denser
post-1960 visual record changing what X4 extracts. Its lower bound is barely above zero.

**Paper wording.** "About a fifth of the gain reflects the duration term partly correcting a level
offset between periods. The rest is within-period information."

## 4. The information is outburst type (exploratory)

The A01 audit (7 November, before any evaluation access) said duration in SS Cyg is "a type label
first". CM92 split durations at 12 d and reported strong long/short alternation. I refitted three
offsets on top of the frozen M2 nuisance parameters, each with a free common level (C21):

| Data | Type only (long minus short) | Continuous log duration | Within-type, given type |
|---|---|---|---|
| 1910–1959 (in-sample) | contrast 0.093, LR 5.17 | LR 5.19 | LR 0.37 |
| 1960–2017 | contrast 0.129, LR 14.70 | LR 11.69 | LR 0.17 |
| 1960–1992 | contrast 0.163, LR 13.50 | LR 11.30 | LR 0.001 |
| 1993–2017 | contrast 0.078, LR 2.26 | LR 1.84 | LR 0.06 |

LRs are against the level-only model. In 1910–1959, type and continuous duration were equivalent. In
1960–2017, type fits better, and within-type duration adds nothing detectable. The gap after a long
outburst is about 14% longer than after a short one in 1960–2017, roughly five days on a typical
36-day gap. The figure was about 10% in 1910–1959. The frozen M3 implies 8.5% between the two
development type centres.

Type information is also robust to the shared end-time error that A10b–A10d worried about. A day of
end-time error moves continuous log duration, but rarely moves an outburst across 12 d. That the
signal lives in type is therefore modest further evidence against an endpoint artefact.

**Why the predeclared type/within-type rule scored only 0.0025.** The rule multiplies an *uncentred*
0/1 long indicator by β_type, while M2's intercept is held fixed: Codex's A10d amendment, which I
accepted. With a free intercept, centring is irrelevant. With a fixed one, the frozen rule can
lengthen forecasts after long outbursts but cannot shorten them after short ones.

- In development this cost about 40% of the in-sample type information: gain 0.0048 against 0.0079.
- In 1960–2017, M2 already forecasts too long, and the frozen rule's mean offset is +0.017, the wrong
  direction.
- Give both models M2's best evaluation level, and the frozen type rule gains 0.0091 [0.0041, 0.0140].
  That interval is narrower than the primary's. It holds better in 1993–2017 (0.0076) than the frozen
  log-duration model (0.0015) (C22).

So the A10i sentence "the primary does not establish a within-outburst-type effect" is correct, and
the exploratory evidence sharpens it: there is no detectable within-type effect. The type/within-type
secondary must not be read as weakening the primary. As frozen, it was not a fair representation of
a type effect.

I specified the type/within-type family in A01 and accepted the fixed-M2 amendment in A10f without
seeing their interaction. That belongs in the supplement's audit trail and as a trap in the agent
guide. Any future indicator mark must be centred at its training mean.

## 5. The lagged mark and alternation

Successive log durations correlate at −0.52 in 1960–2017 and −0.40 in 1910–1959. CM92 reported
−0.400 for 1896–1992. A long outburst is followed by another long one only 15% of the time,
against 66% after a short one (C24).

Given a positive current-type effect, alternation alone implies a negative separate lagged offset.
That is what S1 shows (−0.038, C12). The joint fit's condition number of 1.79 corresponds to the 0.52
correlation, which is why both joint support intervals include zero (C13).

A slow shared state of the kind simulated in A10c–A10f predicts a positive lagged offset. The
evaluation data show none, consistent with the development-stage reading. That disfavours a slow
multi-cycle driver as the main source. It does not identify memory: a driver that decorrelates within
a cycle, or the disc's own state, looks the same.

Physically, Cannizzo (1993) accounts for alternation in the disc-instability model through mass stored
in the outer disc. A depleted disc after a long outburst taking longer to refill is the natural reading
of "longer gap after long". The paper may say this only after one of us has read Cannizzo (1993) and
CM92 in full and checked what they predict and report.

## 6. The era split

1960–1992 gives 0.024 [0.009, 0.039]. 1993–2017 gives 0.0057 [−0.0107, 0.0221], about a quarter of the
early value. No era test was specified. An approximate post hoc z for the difference is 1.7, which
neither establishes nor excludes a change.

The 1993–2017 segment alone had little chance. Its SE (0.0077) exceeds the overall SE, and with four
degrees of freedom even the full-period estimate would sit at its threshold. Exploratory pieces point
in both directions:

- the type contrast is smaller in 1993–2017 (0.078 against 0.163);
- the frozen M2 is nearly unbiased there, so the level part is small;
- a common-level type rule holds up better there than the frozen log-duration model.

**Paper wording.** "The segment outside every published analysis of the sign, 1993–2017, is
inconclusive on its own." Say neither that the effect "faded" nor that it "replicated".

## 7. Framing the paper

**Headline (confirmatory).** In a preregistered, frozen-parameter retrospective test, adding the
completed outburst's duration improved forecasts of SS Cyg's next outburst. The gain was 0.0165 nats
per forecast (90% interval 0.0049–0.0281), over 441 forecasts in 1960–2017. That is about 1.7% higher
predictive likelihood per forecast, and about 14% of what the timing baseline adds over a constant
forecast. The completed run followed one outcome-independent parser repair.

**Second sentence (exploratory, labelled).** Post-result analysis indicates that the information is
carried by whether the outburst was long or short, with no detectable within-type contribution.

**What is new.**

- The first preregistered, held-out forecast evaluation of dwarf-nova recurrence known to us (C41).
- The forecast skill of the CM92 association, in data not used to fit the model.
- A transparent sealed-access record: DOI before access, preserved failure, repair receipt.
- A published human–AI correspondence record.

The methodological contribution is portable to other variable-star questions.

**What is not new (C40).** The duration–gap correlation, alternation, the 12 d split and the
cycle-convention trap are all CM92 or earlier.

**Title.** The scaffold uses: "Does the length of an outburst predict the wait for the next? A
preregistered 58-year forecast test for SS Cygni". A type-led title would put an exploratory finding
first, so I recommend against it.

**The three products.**

- **Article:** observational methods with a forecasting core. Pivotal-records table: the AAVSO
  visual record, the X4 extraction, CM92 Table 4 and the protocol DOI. Assumption table:
  - cluster independence at six years;
  - observation-time replay;
  - X4 at magnitude 10 with C1/7-day coverage;
  - working lognormal clock;
  - visual-only selection.
- **Brief:** "Knowing whether SS Cygni's last outburst was long or short shifts the forecast of its
  next one by a few days, and that held up in 58 years of data the model had never seen." The finding
  that limits it: "one star; the later 25 years alone are inconclusive."
- **Agent guide:** the provenance map from receipts to `primary.json`. Traps:
  - the uncentred type rule;
  - "doubling" read as overfitting;
  - era overreading;
  - S1 support read as confidence intervals;
  - the DOI read as covering the repair.

**Figures.**

1. A stretch of SS Cyg light curve with extracted onsets and ends, and one issued forecast distribution.
2. Per-block gains with the overall and era intervals, as a forest plot. This is the figure the headline
   needs.
3. M2 calibration and coverage bounds.
4. Exploratory: forecast quantiles after long and after short outbursts against outcomes.

The brief takes figure 2 or 4, redrawn large.

**Venue** is Barry's decision. My recommendation is MNRAS, with an arXiv astro-ph.SR preprint at
snapshot time. The audience is the variable-star and accretion community, and MNRAS takes
observational-methods papers of this length. RNAAS is too short for the access record. PASP suits the
method but reaches fewer accretion physicists.

## 8. The 2018+ block

Keep it closed. SS Cyg has had about 65 forecastable outbursts since 2018 (7.6 a year). That is too
few for a useful confirmation on its own: the SE would be roughly 2.5 times the 1960–2017 SE. Its best
use is as one stratum of a multi-star frozen protocol (A05). A pre-registered, centred type rule
would be the natural primary there, because section 4 is exactly the kind of post-result insight that
must be confirmed on new data. A prospective arm publishing live SS Cyg forecasts would be the first
genuinely operational test. It is outward-facing, so it is Barry's decision.

## 9. Next work and owners

| Item | Owner |
|---|---|
| Independently check C20–C25 (exploratory) and C11–C13 (rechecked secondaries). Promote to `supported` or correct | Codex |
| Review `manuscript/estimands.md`. Disagreements go there before any prose | Codex |
| Read CM92 and Cannizzo (1993) in full, and refresh the novelty search (C40, C41) | Claude |
| Draft article, supplement, agent guide and brief from the ledger | Claude, after the estimands are agreed |
| Figures script with hashes; makedoc build; DOI list; author metadata; AI-roles record from board model fields | Codex |
| Venue, authorship, preprint and release decisions; observer-credit and terms review | Barry |

## 10. Checks run

- `scripts/a10j_postresult_review.py` reran end to end (about 1 s). It reports
  `matches_committed_primary: true` and a maximum score recomputation error of 1.4e-13. Input hashes
  are recorded in its output.
- `python3 tools/claims.py check manuscript/claims.csv`: every ledger value is found in its evidence.
  Citation warnings are expected until products are drafted.
- Validator, the 344 tests and a staged gitleaks scan, all before the push.
- I read the saved evaluation scores, ledger, evidence and parameters, and the 1910–1959 development
  outputs. I requested no archive data. Nothing from 2018 onward was touched.
