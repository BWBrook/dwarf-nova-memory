# A10a: the A04i restrictions, prefix-causal predictors and achievable precision

Claude (Opus 5.5), 8 November 2026. Base `03cfd82`. This answers Codex's A04i
handoff: review the magnitude-10 restriction and the known-waveform limit, then
specify A10's prefix-causal predictor construction. It uses pre-1960 rows and
synthetic histories on new seeds (`a10-claude-*`). No 1960+ data were touched.
No real duration–gap association was computed: the real-data diagnostics below
concern boundaries, lags and evidence status only. X4 is unchanged.

## Verdict

- **Accept A04i as a conditional retrospective qualification at 10.0, C1/7 d.**
  Codex's limits are stated correctly.
- **The magnitude-10 restriction is structural, not a v2 quirk.** X4 arms and
  confirms only on votes 0.5 mag brighter than the threshold.
  - At 9.5 that margin falls inside the peak distribution of short outbursts:
    13–15% of v2 outbursts peak fainter than 9.0, and so do 6–8% of real
    1910–1959 outbursts.
  - At 10.0 the corresponding shares are 0.4% (v2) and 1–2% (real).
  - A10 should use 10.0 as primary, 10.5 as a flagged sensitivity, and drop 9.5.
- **The known-waveform limit mainly costs power, not validity of a null test.**
  In the A10 design, forecasts are anchored at issue time, baselines condition
  on age, and outcomes come from later observations. Under the null,
  boundary-shape errors can then dilute the mark but cannot manufacture skill.
  The residual channels are small and already bounded by A04i. The limit
  matters for the coefficient's physical scale and for threshold claims.
- **Prefix-causal predictors are specified, implemented and tested**
  ([protocol](../protocols/a10-prefix-causal-predictors-v1.md),
  `src/dnmem/prefix_features.py`, 8 tests).
  - On real 1910–1959 data, causality costs almost nothing: the prefix
    duration differs from the retrospective one by 0.05 d on average.
  - A truth-free live-forecast rule handles repeat and false emissions.
- **Precision is the binding constraint.**
  - At the expected effect (partial r ≈ 0.12) and about 390 evaluation
    forecasts, the paired forecast gain is positive with probability 0.83.
  - Its one-sided test has only 32% power; a slope test on the same block has
    77%.
  - The confirmatory estimand needs Barry's decision with that known (§4).

## 1. Why the magnitude-10 restriction is structural

X4 arms its causal rule on votes at least `ARM_MARGIN` = 0.5 mag brighter than
the threshold. Its single-observer confirmation needs one vote at least
`CONFIRM_MARGIN` = 0.5 mag brighter. Both margins move with the threshold. An
outburst whose peak lies within 0.5 mag of the threshold can only arm through
observer noise.

| Share of outbursts peaking within 0.5 mag of the threshold | 9.5 | 10.0 | 10.5 |
|---|---:|---:|---:|
| v2 truth, 30 histories per era (true peak) | 13.4–14.8% | 0.4–0.5% | 0% |
| Real 1910–1959, measured core level (288 episodes) | 8.3% | 1.0% | — |
| Real 1910–1959, brightest observer-visit median (344 episodes) | 5.8% | 1.7% | — |

The A04i X4 C1 results follow the same pattern:

| Threshold | Onset coverage, 1930–1959 | Missing first signals | False confirmed /yr | Unsafe /yr |
|---|---:|---:|---:|---:|
| 9.5 | 88.5–89.4% | 4.9–5.7% | 0.049–0.057 | ≤0.009 |
| 10.0 | 92.8–93.3% | 1.3–1.6% | ≤0.008 | ≤0.015 |
| 10.5 | 90.1–92.0% | 2.8–3.0% | 0.011–0.017 | 0.081–0.091 |

At 9.5 the losses come from the bright end. Some faint-peaking outbursts never
produce an arming vote, and others cross near turnover, where the crossing is
poorly defined. v2 overstates the faint-peak share relative to the real record,
roughly twofold, partly through its fixed 5% low-amplitude tail. The real
share at 9.5 is still large enough to break the 5% missing-signal limit. At
10.5 the losses come from the faint end: decline tails and quiescent scatter
re-arm the causal rule more often.

10.0 is where the margins sit clear of both tails, which is why it qualifies.
Real data have somewhat more faint-peak outbursts at 10.0 than v2 (1–2% against
0.4%). At most, that would add a fraction of a percent to the missing-signal
rate, against a 5% limit.

For A10 this means:

- **Primary threshold 10.0.**
- **10.5 as a flagged sensitivity.** Its primary cells pass, its
  injected-effect bias is inconclusive, and unsafe signals are 0.09/yr.
- **No 9.5 analysis.** Retuning the margins would need a new candidate and
  fresh validation. That would buy a sensitivity analysis, not the primary
  result, so I do not propose it.
- **Threshold changes alter the population.** Because amplitude and duration
  are coupled (Spearman −0.65), a brighter threshold selects against short,
  faint outbursts. A threshold sensitivity is therefore partly a population
  sensitivity, and must be reported as one.

## 2. What the known-waveform limit does and does not threaten

I developed X4 on v2. A04i used fresh seeds and an independently built phase
cadence, but the same waveform family. The two source-blind waveforms (v3 and
v4) failed realism, so no realistic unseen waveform exists to test against.
What matters is which A10 conclusions could be wrong if real outbursts differ
from v2 in ways X4 is sensitive to.

**A null forecast comparison is protected by construction.** In the protocol,
a forecast is issued at the observable time τ. Every model conditions on
survival to the prefix age a = τ − ê, and the outcome is the next onset,
measured from observations after τ. Suppose the following wait Q is
independent of the current outburst. Then a duration estimate D̂ is linked to
the remaining wait only through the end error ε (a_true = a + ε). Whatever X4's
bias with respect to shape, the induced association is about
−Var(ε)/(sd D̂ · sd Q). With ε of about 0.5 d, sd D̂ of about 3 d and sd Q of
about 15 d, that is about −0.006, against an effect of interest near 0.12.

A duration-dependent bias in D̂ is a monotone distortion of the mark. It
changes the scale of the mark but adds no information about the future. The
remaining channels are:

- **Persistent observer offsets.** These lengthen D̂ and shorten the next
  measured wait. A04i's offset cells pass at 10.0 under C1, with paired bias
  within ±0.02.
- **Outcome-dependent observing effort.** No benchmark addresses this.
  Codex's null controls on the full forecast chain should measure the first
  two channels directly.

**What the limit does threaten:**

- **Power.** Boundary errors dilute the mark. A04i's injected-effect controls
  keep r ≈ 0.122–0.126 against the oracle's 0.129–0.132 (§3 adds the prefix
  step).
- **The physical scale of the duration coefficient.**
- **Coverage claims at other thresholds** (§1).

**Recommendation.** Do not run another benchmark cycle before A10. Add one
cheap stress diagnostic, not a gate: rerun the A10 null and positive controls
once on v4-phase. It is unqualified, but its curvature and amplitude coupling
differ from v2's. A04i did not score it.

## 3. Prefix-causal predictors

X4's retrospective end fit uses estimates up to 2.5 d past the first faint
vote. Some of those arrive after the causal confirmation, so a retrospective
duration is not available at issue time. The protocol removes them exactly:
X4 is rerun on rows observed at or before each emission (400 d lookback). The
poisoned-future-row test shows that no later row can change any ledger field.

The live-forecast rule replaces a duplicate policy keyed to truth:

- Each forecast is live until the next one is issued.
- It is scored on the next retrospectively confirmed onset if that onset comes
  first.
- Otherwise it is right-censored at the next issue time, at coverage loss
  (C1/7 d) or at the end of the block.

A repeat emission, such as a rebrightening that X4 merges retrospectively,
issues a new forecast with the merged prefix episode. Each onset scores at most
one forecast. Neither inclusion nor censoring depends on the length of the
wait.

`scripts/a10_prefix_pilot.py` (`data/simulations/a10_prefix_pilot_20261108.json`)
ran the protocol on two inputs:

- the real 1910–1959 record;
- 72 v2-phase histories on development seeds: 12 per era under the latent
  alternative and 12 per era under the null.

| Diagnostic | Real 1910–1959 | Synthetic (alternative and null) |
|---|---:|---:|
| Forecasts per year | 6.60 (330) | 6.40–6.93 |
| Without a prefix episode | 0 | 0 |
| Prefix − retrospective duration, mean absolute (d) | 0.048 | 0.05–0.07 |
| Same, 10th–90th percentile (d) | −0.11 to +0.06 | −0.16 to +0.06 |
| End-fit estimates lost, median (90th percentile) | 1 (8) | — |
| End interval width, prefix / retrospective, median (d) | 1.42 / 1.36 | — |
| Age at issue (≈ confirmation lag), median (10th–90th percentile) (d) | 1.90 (1.13–4.07) | 1.87–1.90 (1.0–4.3) |
| Outcomes: onset / coverage loss / superseded | 307 / 22 / 1 | 91% / 8% / <0.1% |
| Previous gap available and covered | 308 | — |
| Forecasts with no true event (per year) | — | 0.002 alternative, 0.010 null |

Causality is nearly free at 10.0. The confirmation arrives about 1.9 d after
the end crossing, and the end window loses a median of one estimate. Codex's
concern is therefore real in principle and negligible in practice. The prefix
construction removes it exactly in any case.

Correlations with the true following gap, on 4,004 synthetic forecasts with no
repeats:

| Duration used | Latent alternative | Null |
|---|---:|---:|
| True | 0.203 | 0.007 |
| Retrospective X4 | 0.194 | −0.001 |
| Prefix X4 | 0.197 | −0.000 |
| Partial on previous gap: true D and true previous gap | 0.113 | 0.007 |
| Partial on previous gap: prefix D and prefix previous gap | 0.127 | 0.002 |

- **Retention.** Prefix durations keep 97% of the marginal association, and
  prefix and retrospective durations are interchangeable.
- **Null.** The null stays at zero, as §2 argues, though at this size
  (SE ≈ 0.016) that is a weak check, not the control Codex will run.
- **A subtlety for interpretation.** The partial correlation is higher with
  measured previous gaps (0.127) than with true ones (0.113). A baseline built
  from noisy timing absorbs less of the shared state, which leaves more credit
  for the mark. That is incremental information beyond the measured
  changing-activity baseline, exactly as `docs/05-statistical-design.md` §3
  frames it. It is not beyond the true state, and positive controls should
  report both.
- **Development forecasts.** The real record yields 330 forecasts in
  1910–1959, 308 with a covered previous gap. That sets the development size
  used in §4.

## 4. Precision, and the decision it forces

`scripts/a10_precision.py` (`data/simulations/a10_precision_20261108.json`)
models the comparison as a standardized Gaussian. The mark adds a partial
correlation r. The models are fitted on 300 development forecasts, which is
roughly the covered 1910–1959 count, and scored on an evaluation stream, with
1,000 replicates per setting. With no censoring, dependence or missing events,
the model is optimistic.

The evaluation size of 390 is projected from the open-era rate of 6.6–6.7
forecasts per year over 58 years. No reserved events were counted.

| r | Evaluation forecasts | Mean gain, frozen (nats) | SD of block gain | P(gain > 0) | Score-test power | Slope-test power |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 390 | −0.0018 | 0.0039 | 0.32 | 0.04 | 0.06 |
| 0.09 | 390 | 0.0025 | 0.0060 | 0.73 | 0.23 | 0.58 |
| 0.12 | 390 | 0.0055 | 0.0071 | 0.83 | 0.32 | 0.77 |
| 0.13 | 390 | 0.0070 | 0.0077 | 0.86 | 0.37 | 0.82 |
| 0.12 | 1,000 | 0.0056 | 0.0049 | 0.90 | 0.57 | 0.99 |
| 0.12 | 2,000 | 0.0056 | 0.0038 | 0.94 | 0.74 | 1.00 |

Online refitting raises the mean gain slightly (0.0060 at r = 0.12, n = 390)
but not the power of the naive paired test.

**What the numbers mean:**

- **Why the score test is weak.** The per-forecast log-score difference has
  mean ≈ r²/2 and SD ≈ r. Its z-statistic therefore grows as r√n/2, half as
  fast as the slope test's r√n.
- **What that implies for SS Cyg.** On 1960–2017 alone, the forecast gain will
  very probably be positive if the association is real. Its 95% interval will
  usually include zero.
- **What it does not show.** This is not evidence against forecast skill. It
  is the precision any honest single-star forecast evaluation of an effect
  this small can reach.

**Decision for Barry.** D013 and message 2952 keep the paired forecast gain as
the primary quantity. The options are:

- **(a) Recommended.** Keep the forecast gain as the primary effect-size
  estimate, reported with its interval and this precision statement. Make the
  prespecified one-sided duration coefficient in the frozen M3 the
  confirmatory test.
- **(b)** Keep the gain as the confirmatory test, and accept about one-third
  power.
- **(c)** Defer the freeze until other stars raise the evaluation count
  towards 1,000. That is the original multi-system design; A05 audits the
  other pilot targets.

These are not exclusive: (a) now, and (c) as the extension.

## 5. For Codex

- Review the protocol, especially:
  - the episode selection (`end_hi ≥ bright_first_at − 1.15 d`);
  - the live-forecast rule;
  - the claim that a null mark cannot manufacture skill (§2).
- Build M0–M3 on the ledger, with age-conditioned, censoring-aware scoring.
- Run controls 1–4 in the protocol on fresh seeds. The prefix-step retention
  figures in §3 are development numbers, not validation.
- Record X4 at 10.0 with C1/7 d as the frozen A05 extraction before any
  1910–1959 model fit. That fit is the first real duration–gap computation, and
  it is development use of the open era under D013.

## 6. Files

- `src/dnmem/prefix_features.py`: ledger, live-forecast evidence and the
  repeat flag.
- `tests/test_prefix_features.py`: 8 tests.
- `scripts/a10_prefix_pilot.py` →
  `data/simulations/a10_prefix_pilot_20261108.json`.
- `scripts/a10_precision.py` → `data/simulations/a10_precision_20261108.json`.
- `docs/protocols/a10-prefix-causal-predictors-v1.md`.
