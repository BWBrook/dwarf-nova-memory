# Claude review of R2a/c preparation (C47–C52) and the R2b rules

Claude (Opus 5.5), 9 November 2026. I reviewed Codex's
[R2a/c report](2026-11-09-r2a-preparation-and-r2c-review.md),
[design review](2026-11-09-r2-design-review.md), [R2c report](2026-11-09-r2c-cohort-power.md),
`r2-design-v1.md`, D036–D037 and the frozen sources `src/dnmem/r2_features.py`,
`src/dnmem/extract_x5.py` and `scripts/r2c_power.py`.

Script: `scripts/r2b_claude_rule_checks.py`. Aggregates: `data/provenance/r2b_claude_rules/checks.json`.

- All real-data checks read retained, already opened SS Cyg rows and R2a feature ledgers before
  JD 2458119.5.
- No model was fitted, no forecast scored and no duration–gap relation computed.
- No archive request was made, and nothing from 2018 onward was read.
- The power checks are my own implementation of the written R2c design, with my own seeds.

The resulting rules are in [r2b-execution-v0.md](../protocols/r2b-execution-v0.md).

## Verdicts

| Claim | My check | Result | Status |
|---|---|---|---|
| C47 X5 window geometry | My own selection on the frozen visit file, with all-limit visits taking their strongest limit, over the 860-episode X4 catalogue | 845 confirmed with a predecessor; 818 available; 4 with no quiescence; 23 with no bright report; median representative width 1.14775 d, identical to Codex's file. The raw-support median of 1.1495 d is arithmetic on Codex's file | supported |
| C48 cadence counterexample | Direct quadrature of the expected log-score difference over both cadence regimes | Coefficient 0.0554925, σ 0.168930, gain 0.0539543 nats | supported; real-data scale bounded below |
| C49 synthetic ladder checks | Read the checker and its evidence | The checker imports only numpy and scipy, no `dnmem`. Its maxima (score 2.49e−14, gain 4.88e−15, objective 1.71e−12) match the claim. I did not recompute B2 | supported |
| C50 precision study | My own implementation of three scenarios (4,000 replicates each) | Core power 0.704 [0.690, 0.718] vs 0.711; serial-block nonidentity coverage 0.719 vs 0.7265; null serial rejection 0.053 vs 0.052 | supported |
| C51 DF population | Recount of the v1 schedule from the decisive visits and the saved audit | 307 of 441 and 134 aborts reproduce. **All 165 aborts were triggered by reports between magnitudes 9 and 10 (median 9.9); none was decisive** | supported as an account of the v1 rule; superseded for R2b (below) |
| C52 catalogue screen | Design and caveats read; catalogue values not re-extracted | — | provisional |

## Findings that change R2b

**1. The DF population loss is a rule artefact.** v1 aborts a pending DF issue whenever any
threshold-level bright report (magnitude 10 or brighter) arrives before the faint anchor. On the
decline tail after the 0.5-mag confirmation, single reports of 9.9 are routine, and they are more
frequent the denser the observing. That produced the 134 evaluation aborts (30%) against 28 in
development. The rule therefore selected the population by cadence, the pathway C48 worries
about. Aborting only on a decisive-bright report (9 or brighter) schedules 330 of 330 development
and 441 of 441 evaluation issues. The median evaluation delay is 0.90 d, and no issue lands at or
after the next onset window. A threshold-level reset variant gives the same counts. DF and point
clocks can now be compared on the full 441, not on 291.

**2. The clock discrepancy dissolves by definition.** The 12 current-versus-historical anchor
differences arise because the historical X5 anchor is the first decisive-faint visit after the
peak, while the current anchor is the first after the last bright report. R2b measures every past
DF gap from that past emission's own scheduled anchor, so current and historical anchors are the
same object.

**3. A crossing convention closes the exact-photometry A1 failure.** The design review's path
(0, 11.5), (1, 9.5), (2, 11.5), (3, 8.5) defeats a first-crossing target. If the target is the
last upward threshold crossing before the first decisive-bright latent time, then exact
photometry plus A0 (no missed decisive excursion) imply containment in the X5 raw-support window.
A1 then fails only through A0, a decisive report wrong in sign by at least a magnitude, or
misattributed raw support. That list is shorter and more checkable. A0 and report accuracy remain
assumptions.

**4. C48 is right in principle; in the evaluation era its cadence pathway has a ceiling.** A mark
can gain from cadence only by predicting the cadence-dependent part of the anchor lag and of the
history errors. By the data-processing inequality and the small-shift Fisher approximation, that
gain is at most about J Δ²/2, where Δ bounds the shift. Under exact report ordering, the gaps
between reports straddling the threshold + 1 crossings bound Δ, and those gaps are observable at
issue:

| Quantity (days) | Development | Evaluation |
|---|---:|---:|
| Anchor cadence gap, median (90th percentile) | 0.58 (2.05) | 0.10 (0.78) |
| Onset cadence gap, median (90th percentile) | 0.67 (1.98) | 0.33 (0.93) |
| Planning ceiling, nats (frozen M2 scale) | 0.041 | **0.0071** |

The invented counterexample uses one-day and five-day lags. SS Cyg's 1960–2017 cadence gaps are
mostly hours. A DF gain well above about 0.007 there cannot come from cadence-lag correction
alone, under the stated assumptions. In the sparse development era the ceiling exceeds any
plausible effect. Other stars will have their own ceilings, and those must be computed from their
own reports. The ceiling does not cover observers responding to outburst properties, or the
order-statistic effect of many observers' scatter (planning size about 0.001). It is therefore a
bound on one pathway, not identification of physical memory.

**5. Star × six-year CR1 is not adequate for the sealed test.** In my reimplementation, coverage
falls below nominal even at modest block persistence: 0.846 at mark ICC 0.05, residual ICC 0.1 and
block AR 0.7. Only star-level clustering covers in every case examined, at a large power cost.
SS Cyg's log-mark block ICC is −0.020 to 0.013 on both clocks and in both periods, so the R2c
stress case (mark ICC 0.5) overstates the mark's persistence here. The residual persistence is
unmeasured until R2b fits.

Rule (§5.3): star × 18-year by default; star-level if R2d's simulation at the measured dependence
gives coverage below 0.88. The R2c null rejection of 0.052 under serial blocks is close to nominal
only because about half of the null fits return the identity. In my run, 2,051 of 4,000 null fits
had a positive offset. Conditional on that, the one-sided rejection rate is 0.103 for star ×
six-year blocks, twice nominal, and 0.053 for star × 18-year blocks.

**6. Fix the sealed primary before R2b.** DF clock, B2 comparator (B1 only on a pre-declared
stability failure), X5 working interval score. R2b can then inform power and interpretation but
cannot select the specification.

## Not checked

- I did not recompute B0–B2 fits, the B2 recursion or the R2a synthetic control histories. I
  checked the independent checker's scope and evidence.
- My X5 check uses representative visit times. The raw-support widths come from Codex's file.
- The cadence ceiling uses the frozen M2 scale and a planning history coefficient of 0.38. R2b
  must recompute it from each fitted base.
- The C52 catalogue values were not re-extracted from the Ritter–Kolb or Downes sources.
- My power reimplementation follows the written design, not Codex's code. Agreement checks the
  design's arithmetic, not its realism.
