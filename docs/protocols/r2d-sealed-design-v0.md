# R2d v0: sealed multi-star design after the R2b review

Claude, 9 November 2026. Proposed rules for Codex to challenge, amend and freeze as R2d v1,
before any new-star archive is opened. They follow from the
[R2b review](../audits/2026-11-09-claude-r2b-review.md) (D042). Where they conflict with
`r2b-execution-v2.md` §6, this file supersedes it for the sealed test only.

- R2b results stay exploratory.
- SS Cyg's guarded estimates inform planning and interpretation only. They cannot become a
  confirmation or select a specification.

## 1. Estimand

The sealed test targets **outburst-level** association. In each eligible star, it asks whether
the current outburst's decisive-bright span, relative to that star's recent norm, predicts the
next DF quiescent interval beyond a level-robust history baseline.

- Slow co-variation of span and recurrence is excluded from the primary by construction.
- That slow co-variation is reported as an exploratory secondary, because it is confounded with
  coverage history.
- No result identifies a physical mechanism.

## 2. Clock, outcome and mark

- **Clock and outcome.** DF clock, outcomes and coincidence handling exactly as in
  `r2b-execution-v2.md`:
  - decisive-bright abort;
  - D040 representative rule;
  - X5 eligible windows;
  - the working interval/backoff score, under the stated A0–A2 premises.
- **Mark.** z = log decisive-bright span, standardized on the star's own development rows, minus
  the mean z of that star's previous ten available marks (development included).
  - Fewer than three previous marks gives no offset.
  - A missing mark returns the exact base.

## 3. Comparator

- **Base B0R.** Refit B0 per star on development. Add a causal level correction: one Newton
  step on the location from that star's previous 20 forecasts whose outcome was resolved by the
  issue, development included. Apply it identically to both arms.
- **Why B0R.**
  - B2 fails development adequacy on SS Cyg: 13–19 nats worse than B0 with equal parameter count.
  - B0 is the simplest declared rung, and B1's development advantage is within two AIC units once
    its discount choice is counted.
  - Of the two, B0R also gives the smaller SS Cyg guarded gain, so the choice cannot be read as
    gain-seeking.
- **Recalibration** is declared because SS Cyg shows a development-to-test level shift that a
  development-only rule cannot detect. New stars' development and test periods may differ in
  coverage the same way.
- **Sensitivities, always reported:** B1R, unrecalibrated B0, and B2.

## 4. Statistics

- **Primary detection test.** A one-sided, cluster-robust score test of β = 0 for the pooled
  mark offset at B0R. The statistic is Σ z·∂ℓ/∂μ over all supported test forecasts.
  - Variance: centred, with a small-cluster correction chosen by R2d simulation for size at the
    planned cluster count. Candidates: CR2 with Bell–McCaffrey degrees of freedom, or the wild
    cluster score bootstrap of Kline and Santos
    ([10.1515/2156-6674.1006](https://doi.org/10.1515/2156-6674.1006)).
  - The uncentred score variance is a sensitivity.
- **Effect size.** The out-of-sample gain is the predictive estimand. β is pooled from all
  stars' development data, on the B0R base and the guarded mark, and the gain is reported with
  an interval under the same clustering.
  - The gain is not the detection test: when β̂ ≈ β its t statistic is about half the score
    statistic.
- **Clustering.** Star × eighteen-year blocks by default. R2d's stress envelope may require
  whole-star clustering.
- **Reporting.** Per-star gains and score statistics are reported descriptively.
  No star is dropped after unblinding.

## 5. Precision planning, for R2d to verify by simulation

- Noncentrality per forecast: δ = √(2·KL).
- Required supported forecasts for 80% one-sided power at 5%: N ≈ deff × (2.486/δ)².

| KL per forecast | δ | deff 1.25 | deff 2 | deff 3 |
|---|---:|---:|---:|---:|
| 0.004 (H2-sized) | 0.089 | ~970 | ~1,550 | ~2,320 |
| 0.0085 (SS Cyg guarded DF B2; optimistic) | 0.131 | ~450 | ~730 | ~1,090 |

The simulation must stress, jointly:
- star heterogeneity in β, including null and negative stars;
- residual level drift beyond the correction;
- persistence within star across blocks;
- missing marks;
- the realized cluster count;
- the small-cluster correction.

Following D039, it reports power and size over the envelope, not at one plug-in value. Its
output is the N required at δ = 0.089 across the envelope, for comparison with the catalogue
yield that G3a would reveal.

## 6. Decisions after R2d

- **G3a: development-only opening of the nominee stars.** Barry decides, with R2d's required N
  in hand. It reveals coverage, qualifying windows and forecast yield, not test outcomes.
- **G3b** (test opening), **SS Cyg 2018–2025** and **any specialist invitation** remain separate.
- **Products** stay paused until R2d integration revises C01's interpretation: a confirmed
  predictive gain of its frozen specification, about a third of which is an era-level correction
  in the analogous R2b analysis.
