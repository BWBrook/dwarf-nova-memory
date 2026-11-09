# Claude review of R2b (C53–C60): baseline adequacy, era drift and test efficiency

Claude (Opus 5.5), 9 November 2026. Reviewed Codex's
[R2b report](2026-11-09-r2b-exploratory-execution.md), the
[pre-execution review](2026-11-09-r2b-pre-execution-review.md), `r2b-execution-v2.md`, D039–D041,
`src/dnmem/r2_models.py`, `src/dnmem/r2b_features.py`, `src/dnmem/r2_scores.py` and the
aggregate evidence in `data/provenance/r2b_20261109/`.

Script: `scripts/r2b_claude_review_checks.py`. Aggregates: `data/provenance/r2b_claude_review/checks.json`.

- It reads only the retained, ignored R2b run outputs in `outputs/r2b_real_5fb69c6/`: saved base
  and marked clocks, outcome signatures, features and parameters. All are SS Cyg, before
  JD 2458119.5.
- It uses its own lognormal interval, survival and derivative code. It imports Codex's
  `TimingRule` only to regenerate development base predictions.
- No archive request was made, nothing from 2018 onward was read, and no product was rewritten.
- Everything below the verdicts is post-result exploration on already-scored evaluation data. It
  informs the sealed design and the interpretation. It is not a confirmation, and no headline is
  replaced.

## Verdicts

| Claim | My check | Result | Status |
|---|---|---|---|
| C53 Fisher index is not a ceiling; aggregation defeats the containment proof | Own quadrature of the conditional shifted lognormal; read the aggregation counterexample | KL 0.0032471084490 against the quadratic 0.0031200550911, identical to Codex. The counterexample is valid as stated | supported; I withdraw D038's "ceiling" and shortened containment argument |
| C54 populations | Recount from the feature ledgers | 330 development; 441 original and 440 DF evaluation issues; 418 DF markable; 417 jointly markable | supported |
| C55 H1–H3 | Recomputed every base and marked working score from saved clocks and outcome signatures, with own block code | Maximum score difference 0 across all 14 models. Gains and six- and twelve-year intervals reproduce | supported |
| C56 rate and DF-c secondaries | Same recompute, plus the drift decomposition below | Numbers reproduce. The positive rate result is explained by an era shift in observing rate, not a cadence pathway | supported numerically; interpretation amended (C62) |
| C57 mixed envelope | Closed-form density extrema at window ends and survival at the cutoff | 431 cases; means 0.000970279 and 0.007753455, identical | supported |
| C58 numerical reconstruction | My score recompute is a third route for the 14 normal-policy models; multistart records read, not refitted | Agrees exactly | supported for scores; optimizer claims as read |
| C59 residual dependence proxies | Not recomputed | — | provisional |
| C60 B2 has lower baseline means | Recompute, plus the diagnosis below | Means reproduce; development NLL 849.28 (B2) against 830.19 (B0) and 827.24 (B1) on DF | supported; cause identified (C61) |

**I was wrong on two points in D038.**
- The Fisher index is a local approximation, not a bound. Exact integration already exceeds it,
  and the one-lag B2 index (mean 0.0096) is larger than H2 itself. Cadence-lag correction is
  therefore not excluded as an explanation of H2.
- Per-night visit medians can hide a decisive report inside a faint visit's support.
  Codex's counterexample needs a 2.5-magnitude drop within an hour, which no dwarf nova does.
  A declared maximum latent rate (for example a few magnitudes per day), together with per-night
  aggregation, should restore containment to within a stated tolerance. I suggest A1 adopt that
  form; it is not yet proved.

## Findings

**1. B2 is misspecified for SS Cyg, and its development fit shows it.**
- B2's level is a random walk with a fixed prior variance of 1 and no mean reversion. The fitted
  level noise is 0.137 per outburst on DF. The fitted prior mean of 1.32 sits far below the
  observed log gaps (about 3.6), so with seven or so gaps in the 400-day window the forecast is
  a short local average.
- B0's fit says the opposite structure is right: strong reversion to the long-run mean, about
  0.38 per unit log previous gap, and essentially zero weight on the older-gap mean.
- B2's development NLL is 13–19 nats worse than B0's, with the same parameter count, and 15–22
  worse than B1's. A development-adequacy check would have retired it before R2b.
- It is the preselected comparator, not a strong one. H2 measures duration over a noisy base.

**2. The gap level shifted between eras, and B0/B1 cannot follow it.**
- DF quiescent intervals had geometric means of 27.5 and 31.0 days in 1960–1971 and 1972–1983,
  against 34.5–39.6 days in every twelve-year development block. They returned to 34.5–39.2
  days after 1984.
- The origin (astrophysical, coverage, or both) is not established.
- B0 and B1 keep their 1910–1959 intercept. Their mean evaluation location score is −0.59 to −0.68,
  meaning outcomes come earlier than forecast, concentrated in 1960–1983.
- A causal level recalibration fixes most of this: one Newton step from the previous 20
  forecasts already resolved by each issue.
  - It raises the B0 DF evaluation base mean from −3.6794 to −3.6642 (+0.0152 per forecast) and
    the point B0 mean by +0.0181. That is larger than any mark gain.
  - It worsens every development fit by 6–7 nats, because development contains no comparable
    shift. A development-only rule would therefore never select it.

**3. Any mark whose mean shifts between eras gains by correcting the level.** With β ≥ 0, a mark
that runs high or low in the evaluation era shifts every forecast's location. It earns a gain
whenever the base's level error has the matching sign.
- *Observing rate.* Its mean is 1.54 development SDs higher in 1960–2017, and 61% of its score
  statistic is between six-year blocks. With the drift guarded (causally centred mark at the
  recalibrated base), its gain falls from 0.0030 to 0.0014 (t 1.34).
  - Its "positive under both blockings" result is an intercept correction repeated in every
    block. That is why its interval is so narrow.
  - It neither shows nor excludes a cadence mechanism.
- *Fitted duration (point clocks).* It is 0.24 SD shorter in 1960–2017 while B0 over-forecasts
  waits. With guards, the point B0 gain falls from 0.0184 to 0.0132, so about 30% of the
  analogous point-clock gain was a level correction.
  - C01 uses the same clock and mark against frozen M2, so it probably carries a similar
    component.
- *DF span.* Its mean shift is +0.07 SD and its between-block share is 5% on B2. It is not
  materially affected.

**4. Duration's association survives the guards; observing rate's does not.**

| Clock and base | Raw gain (t6) | Guarded gain (t6, t12) | Guarded centred score z (6-yr, 12-yr) |
|---|---|---|---|
| DF, B2 (H2) | 0.0043 (1.53) | 0.0052 (1.77, 1.57) | 2.42, 2.15 |
| DF, B0 | 0.0084 (1.55) | 0.0086 (1.71, 1.58) | 2.69, 2.51 |
| DF, B1 | 0.0110 (1.71) | 0.0116 (1.95, 1.76) | 3.14, 2.86 |
| Point original, B0 | 0.0184 (2.61) | 0.0132 (2.27, 3.19) | 3.79, 5.94 |
| DF rate, B2 | 0.0030 (3.11) | 0.0014 (1.34, 1.26) | 1.54, 1.45 |

- "Guarded" means the mark minus the mean of its previous ten values, scored at the causally
  recalibrated base, with development β.
- The guards were designed after seeing the rate result, so these figures are exploratory.
- They show two things:
  - the era pathway is real (it carries rate's signal);
  - duration's outburst-level association is not explained by that pathway.
- Twelve-year centred statistics rest on five blocks and are unstable.

**5. No clock artefact is demonstrated.**
- The B0/B1 paired DF-minus-point gain differences are −0.0097 and −0.0098, which look large.
  But they are mostly the fitted-duration drift: the point B0 gain with an evaluation-centred mark
  is 0.0122, against DF 0.0099.
- Score tests crossing each clock's base with the other population's mark give 1.55–2.17 under
  six-year blocking, against 1.72–2.30 for the native pairings.
- The guarded point gains still exceed DF by about 0.004–0.005. The fitted mark may simply be the
  better duration measure.
- DF remains the right sealed clock: its anchor is observed and its mark does not drift.

**6. The out-of-sample gain is an inefficient detection test.**
- For a small location effect β and an estimate β̂ from development, the gain's t statistic is
  about √(nJ)(β − β̂/2). The score test of β = 0 has noncentrality √(nJ)β, so it is never weaker
  and twice as strong when β̂ = β.
- SS Cyg agrees model by model:
  - development β̂ is below the evaluation one-step β (0.025 against 0.043 on DF B2);
  - for the nine duration contrasts, the predicted ratio of centred score z to six-year gain t
    is 1.41–1.74, and the observed ratio differs from it by at most 0.02.
- The same logic underlies Clark and West's adjustment for nested forecast comparisons
  ([10.1016/j.jeconom.2006.05.023](https://doi.org/10.1016/j.jeconom.2006.05.023)).
- With guards, the six-year design effect of the centred score statistic is 1.13–1.34 across the
  duration contrasts. Before them it was 1.15–1.85. The era-level structure was inflating cluster
  variance as well as shifting the means.

## What this changes

- **SS Cyg's honest state.** The original working gain (C01, 0.0165) stands as the confirmatory
  result of its frozen specification. As evidence of outburst-to-outburst memory it needs
  qualifying:
  - about a third of the analogous point-clock gain is an era-level correction;
  - the guarded association is positive in every clock and base, at 0.005–0.016 nats per
    forecast, with six-year t of 1.7–2.3;
  - SS Cyg alone cannot settle it under block dependence.
  - Slow co-variation of span and recurrence exists: DF B0 block means correlate at 0.83. It is
    confounded with coverage history and must be reported separately from the memory estimand.
- **The sealed multi-star test becomes feasible**, if it uses the score test and the drift
  guards.
  - Planning noncentrality per forecast is δ = √(2·KL). At an H2-sized KL of 0.004, δ is 0.089,
    and N ≈ deff × (2.486/δ)² gives about 970 forecasts at deff 1.25 and about 1,550 at deff 2,
    for 80% power.
  - The R2c gain test at the same KL would need two to four times as many, depending on how well
    development estimates β.
  - R2d must verify this by simulation over a stress envelope, as D039 requires.
- **Rules for R2d** are proposed in [r2d-sealed-design-v0.md](../protocols/r2d-sealed-design-v0.md):
  - primary statistic: the efficient score test;
  - effect size: the gain;
  - guards: causal mark centring and causal level recalibration;
  - comparator: B0R, replacing B2;
  - clock and mark: DF clock and span, unchanged;
  - correction for small cluster counts: chosen by simulation.

## Not checked

- The origin of the 1960–1983 gap shift: physical, coverage, or both.
- C59's residual proxies. B2's recursion: I used saved clocks and regenerated development
  predictions with Codex's code.
- Recalibration resolution times use the outcome window's upper bound and ignore the 0.15-day
  report-availability lag.
- The guard parameters (ten marks, twenty forecasts) were chosen by me without tuning, but after
  seeing R2b. Other values were not tried.
- Whether the decisive-span mark or the fitted duration better measures physical duration.
