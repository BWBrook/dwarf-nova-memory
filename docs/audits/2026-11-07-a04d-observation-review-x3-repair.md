# A04d: benchmark review, failure diagnosis and the X3 repair

Claude (Opus 5.5), 7 November 2026. Base `0ba1e4c`. This answers Codex's
A04c handoff: review the observation assumptions, repair the interval,
matching and confirmation rules, and specify fresh validation. All
development used training seeds (base `a04d-claude-training-20261107`),
never the A04c screen seed. No 1960+ data were opened, and no real
duration–gap association was computed.

## Verdict

- **The A04c benchmark fails three posterior predictive checks against the
  open-era light curves.** Its decline rate scales with duration, but the
  real rate does not. It puts a knot exactly at 10.0, where the synthetic
  decline doubles in speed; the real decline runs straight through. Its
  scatter at the threshold is about 20% too small. X2's near-pass rode on the
  knot: under morphology that matches the data, X2's conditional coverage
  falls to 70–83%.
- **Every X1 boundary miss is one misclassified vote.** The vote that sets
  the violated bound sits on the wrong side of 10.0 because of observer
  noise. Median errors are only 0.06–0.19 d, and misses cluster where
  sampling is densest. An adjacency bracket treats noisy classifications as
  exact. It cannot be calibrated by widening, because the miss is the bracket
  logic itself.
- **Lost matches are mostly unrecoverable or self-inflicted.** Missed events
  (1.6%) are short outbursts with a median of one vote within a day of the
  crossing. Splits (1.2%) are long outbursts cut at the 4 d gap rule. A 7 d
  rule is physically safe and cuts them to 0.2–0.3%.
- **X3** keeps X1's detection, splits only at gaps over 7 d, and replaces the
  adjacency bracket with a posterior interval for the time a local line
  crosses the threshold, with a data-estimated scatter. On the
  best-matched training condition it reaches 93–95% effective coverage at
  both boundaries in every era, against 68–79% for X1 and X2 on the same
  rows. Its point estimates halve the median error of X1's midpoints.
  **X3 fails the v1 template's end coverage (84–86%)**, because a straight
  line fitted across v1's knot predicts the crossing early. The real light
  curves have no knot, which is why the protocol gates the benchmark on the
  predictive checks before any extractor is scored.
- A fresh validation is specified in
  [`docs/protocols/a04d-x3-validation-v1.md`](../protocols/a04d-x3-validation-v1.md).
  Codex builds benchmark v2 to pass the same predictive checks, and the
  validation seeds come from Codex's freeze commit.

## 1. The benchmark against the open era

`scripts/a04d_morphology_check.py` applies one estimator to real 1910–1959
rows and to synthetic rows. Around each X1 boundary it fits a Theil–Sen line
through observer-visit estimates within 1 mag of 10.0. Results are in
`data/simulations/a04d_morphology_check_20261107.json`.

| Statistic (median unless stated) | Real 1910–1959 | A04c v1 | Claude training "smooth" |
|---|---:|---:|---:|
| End slope, mag/d (IQR) | 0.333 (0.293–0.391) | 0.444 (0.323–0.601) | 0.312 (0.267–0.365) |
| End slope, short vs long (< / ≥ 11 d) | 0.333 / 0.341 | 0.577 / 0.370 | 0.312 / 0.310 |
| Spearman, end slope vs duration | 0.04 | −0.54 | 0.02 |
| Decline slope 1 mag above / below 10.0 | 0.20 / 0.20 | 0.26 / 0.57 | 0.22 / 0.21 |
| Windows with a fit below 10.0 (of above) | 262 (279) | 317 (1,468) | 1,487 (1,627) |
| Onset slope, mag/d (q10–q90) | 0.67 (0.21–1.88) | 1.12 (0.55–1.79) | 0.64 (0.30–1.18) |
| End residual SD about the line, mag | 0.222 | 0.176 | 0.173 (0.207 at 1.25× noise) |
| Estimates per end window | 18 | 9 | 15 |

What this means:

1. **Decline rate.** Real declines through 10.0 run at about 0.33 mag/d
   whatever the outburst's length, as disc-instability theory expects.
   v1 builds the decline from the plateau end to the crossing as a fixed
   35% of the duration, so short events fall about 1.6 times as fast as
   long ones.
2. **Knot at the threshold.** v1 crossings sit on a template knot, so the
   synthetic decline doubles in speed exactly at 10.0, and few estimates land
   in the 10–11 mag band. The real decline has the same slope on both sides.
   This artefact makes the 10.0 threshold special. It also flatters X2, whose
   night-to-night interval gains from the steep segment.
3. **Rise.** Real rises through 10.0 are slower on median and much more
   varied than v1's.
4. **Scatter at the threshold.** Observer scatter calibrated from
   quiescent residuals (median 0.185 mag) understates the scatter at the
   crossing. Codex's plateau residuals (IQR ±0.2 mag) pointed the same way.
5. **Vote density.** Most of v1's shortfall in estimates near the end comes
   from the knot, not the cadence. With smooth morphology the deficit is
   about 20%, which is a plausible size for observers watching an outburst
   harder.
6. **Quiescence.** Real visual estimates in quiescence have median 11.8
   (IQR 11.6–12.0), against v1's 12.2.

The training "smooth" morphology (in `scripts/a04d_train_x3.py`) fixes items
1–3 and is my development stress test. It is not the validation benchmark,
because I wrote it and I wrote X3.

## 2. Why X1 and X2 miss

Training seeds, v1 benchmark, 180 histories in 1910–1959, magnitude 10. A
per-event diagnostic (development scratch, not committed) reproduces
Codex's screen rates: X1 81.8% / 75.3%, X2 89.3% / 91.7% effective. So does
the committed training batch (X1 80.7–81.8% / 72.5–76.4%, X2 88.3–89.6% /
91.0–92.6%).

| Outcome | X1 onset | X1 end | X2 onset | X2 end |
|---|---:|---:|---:|---:|
| Covered | 81.8% | 75.3% | 89.3% | 91.7% |
| Interval wholly before truth | 6.1% | 18.1% | 3.9% | 1.8% |
| Interval wholly after truth | 9.3% | 3.8% | 3.9% | 3.5% |
| Missed (no confirmed episode) | 1.6% | 1.6% | 1.7% | 1.7% |
| Split | 1.2% | 1.2% | 1.2% | 1.2% |

- **X1.** In every miss the bounding vote's true magnitude lies on the other
  side of 10.0. Typical end misses are an F vote at a true 9.78–9.99 that
  ends the run a few tenths of a day early (median error −0.19 d, q90
  −0.61 d). Missed intervals are narrower (median 0.5–0.7 d) than covered
  ones (0.9–1.0 d). Dense sampling puts more votes inside the band where
  noise decides the class, so the bracket is most confident exactly where it
  is most often wrong.
- **X2.** Its bounds are the median times of the faint and bright nights, so
  its intervals are about one night wide whatever the data say. Its misses
  are also small (median 0.05–0.17 d). In the training batch under smooth
  morphology with 1.25× noise, its conditional coverage falls to 78–83%
  (onset) and 70–76% (end); X1 falls to 74–78% and 69–72%.
- **Missed events** are short (median 7.5 d) and sparsely observed (median
  one vote within ±1 d of the crossing). No finder recovers them; they cap
  effective coverage near 98.4%.
- **Splits** are long (median 15 d). They come from the 4 d gap rule cutting
  an outburst at an observing gap.

## 3. X3

`src/dnmem/extract_x3.py`, tests in `tests/test_extract_x3.py`.

- **Detection** is X1's (observer-visit votes, nightly majority, runs at most
  three nights apart merged), but a run is split only at an observing gap over
  7 d. A bright night, a gap of 7 d or less and another bright night cannot
  hold the end of an outburst, a quiescence and a new rise. The shortest
  well-covered open-era quiescence in the A04c calibration is 16.3 d.
- **Boundary interval.** Take observer-night median estimates within 1 mag
  of the threshold, inside a window 2.5 d either side of X1's bracket and on
  the correct side of the peak. Model them as m(t) = threshold + s(t − t_c).
  The slope has a log-normal prior: decline median 0.35 mag/d, log-SD 0.45;
  rise median 0.8 mag/d, log-SD 0.8. The intercept has a flat prior. The
  scatter is the residual variance shrunk towards 0.25 mag with four degrees
  of freedom. Given s, t_c is Gaussian, so the marginal for t_c is a mixture
  over a 41-point slope grid. X3 reports its central 99% interval. The level
  is the one parameter tuned on training outcomes. In 90-history
  development runs of the uncommitted prototype (the same logic) under
  smooth morphology with 1.25× noise, the 98% and 99% levels gave 94.3% and
  96.0% conditional coverage, and an earlier prototype at 95% gave about
  90%. The shortfall from nominal probably comes from correlated observer
  errors and curvature near the peak; I have not separated the two.
- **Point estimate.** `onset_t` and `end_t` are the posterior medians within
  the clipped interval. A wide, skewed interval has a poor midpoint, so D and
  Q should use these.
- **Clipping and fallback.** Votes more than 1 mag from the threshold clip
  the interval, using the same strict-time adjacency as the v2 tie rule.
  With no estimate inside the band the interval falls back to X1's bracket,
  which is then set only by far votes. About 5% of onsets and under 1% of
  ends fall back; in the 99% prototype run their coverage was 99.6% and
  98.5%.
- **Confirmation** (`confirmed`) is the time of the second distinct observer
  whose estimate or limit is at least 0.5 mag fainter than the threshold,
  after the episode's last bright vote. It uses no truth and no future
  onset. Codex's diagnostic fired before the true end in 11–19% of X1
  matches because it counted any faint vote after a noisy last-bright time.

### Training results

`scripts/a04d_train_x3.py`, 40 replicates per era (1910–1929, 1930–1949,
1950–1959) and condition, independent null, random phase, magnitude 10, C1
at 7 d. Ranges are across the three eras. Monte Carlo SEs of X3's effective
coverage are at most 0.65 points. The table is
`data/simulations/a04d_x3_training_20261107.csv`.

| Condition | X1 effective onset / end (%) | X2 effective onset / end (%) | X3 effective onset / end (%) | X3 conditional (%) | X3 mean width onset / end (d) | X3 null bias | X3 confirmation before true end |
|---|---|---|---|---|---|---|---|
| Smooth, 1.0× noise | 73.9–75.2 / 68.5–68.9 | 78.9–80.3 / 73.4–74.4 | 94.2–96.0 / 94.3–95.5 | 95.6–97.5 | 1.6–2.0 / 1.4–1.8 | −0.010 to +0.001 | 0.0–0.2% |
| **Smooth, 1.25× (nearest real scatter)** | 73.2–74.9 / 68.0–69.1 | 77.4–79.0 / 69.7–72.8 | **93.4–95.4 / 94.0–94.6** | 94.9–97.0 | 1.8–2.2 / 1.6–1.9 | −0.007 to 0.000 | 0.0–0.5% |
| Smooth, 1.5× | 72.1–73.6 / 68.8–69.4 | 75.8–76.6 / 67.1–69.8 | 92.9–94.1 / 93.3–93.6 | 93.5–96.3 | 2.0–2.3 / 1.8–2.1 | −0.008 to +0.011 | 0.2–0.8% |
| Smooth, 1.25× plus fixed offsets SD 0.2 | 71.0–71.9 / 66.2–67.7 | 73.3–75.4 / 66.0–66.9 | 91.5–93.0 / 91.1–91.4 | 91.7–94.5 | 2.0–2.4 / 1.8–2.1 | −0.014 to +0.005 | 0.4–1.1% |
| A04c v1 template | 80.7–81.8 / 72.5–76.4 | 88.3–89.6 / 91.0–92.6 | 91.3–93.1 / **84.5–86.3** | 93.4–94.3 / 85.4–88.0 | 2.2–2.6 / 2.2–2.6 | −0.013 to +0.011 | 0.0–0.2% |

Other X3 results in every condition: unique completeness 96.8–99.9%, false
confirmed episodes at most 0.02 per year, and as many C1-eligible pairs as
X1 (104.3 against 104.5 per history). Median confirmation lag is 1.7–2.1 d
under smooth morphology, and confirmation is missing for under 1% of
matched events.

Point accuracy (`data/simulations/a04d_x3_point_check_20261107.csv`,
36 further training histories, smooth morphology, 1.25× noise):

| Matched events | Median absolute error (d) | RMSE (d) | 5th–95th percentile (d) |
|---|---:|---:|---:|
| X1 onset midpoint | 0.266 | 0.721 | −0.86 to +1.02 |
| X3 onset estimate | 0.146 | 0.670 | −0.59 to +0.50 |
| X1 end midpoint | 0.401 | 0.910 | −1.26 to +1.10 |
| X3 end estimate | 0.187 | 0.508 | −0.61 to +0.57 |

What the table shows:

- X3 clears 90% effective coverage with margin wherever the benchmark
  matches the data. The real residual scatter (0.222 mag) lies between the
  1.25× (0.207) and 1.5× conditions, and X3 gives 92.9–95.4% in both.
- The fixed-offset arm is X3's weakest case (91–93%). That arm has more
  scatter than the real data, but correlated errors from a
  biased observer watching several nights are the threat to model-based
  intervals. The protocol asks Codex to calibrate the offset share at
  outburst brightness rather than in quiescence.
- Under realistic morphology X1 and X2 do worse than in A04c, not better.
  The v1 knot had been helping them.
- X3's v1 end failure is a real limitation. If real declines bent at 10.0,
  X3 would undercover. The check in section 1 finds equal slopes on either
  side, from about 270 windows each, which excludes a break of v1's size.
- The end estimate enters D_i with one sign and Q_i with the other. With
  an RMSE of about 0.5 d and SDs of D and Q near 4 and 15 d, that shared
  error induces a correlation of order −0.004, small against the ±0.02
  margin.

## 4. Responses to Codex

- *"Calibrate X1's conditional intervals."* Calibration by widening cannot
  fix a bracket whose bound is a misclassified vote. X3 replaces the bracket
  with a model interval; the 0.99 level is the calibration, done on a
  separate training batch as you asked.
- *"Address X2's lost matches."* Of the 2.8% lost, 1.2 points are splits,
  which the 7 d rule cuts to 0.2–0.3 points, and 1.6 points are short events the data do not
  sample; no finder recovers those. They remain in the effective-coverage
  denominator, so X3 must clear 90% with them counted.
- *"The confirmation definition."* Now part of the extractor, operational
  and scored (criterion 5 in the protocol).
- *1950s null bias.* Under C1 at 7 d, X3's null bias ranges from −0.014 to
  +0.011 across conditions and eras. At 40 replicates the 1950s SE is
  0.012–0.015, so the training batch cannot settle your inconclusive 1950s
  cells. On my training seeds X1's v1 1950s bias is +0.007 ± 0.015, which
  is consistent with your +0.0197 [0.0085, 0.0309]. The protocol raises the
  decisive cells to 400 replicates and adds two eligibility rules aimed at
  your unmatched-subset remainder: an unconfirmed bright episode censors
  its quiet interval, and an internal gap over 7 d censors both
  neighbours.
- *Benchmark independence.* I wrote X3 and the training morphology, so my
  training numbers are development evidence only. Validation needs your
  benchmark, built to the predictive checks, with seeds from your freeze
  commit.

## 5. Files

- `src/dnmem/extract_x3.py`, `tests/test_extract_x3.py`: X3 and eight tests.
- `scripts/a04d_morphology_check.py`,
  `data/simulations/a04d_morphology_check_20261107.json`: benchmark
  predictive check.
- `scripts/a04d_train_x3.py`, `data/simulations/a04d_x3_training_20261107.csv`:
  training batch (40 replicates per era and condition, five conditions);
  `data/simulations/a04d_x3_point_check_20261107.csv`: point-estimate
  check (`--points`).
- `docs/protocols/a04d-x3-validation-v1.md`: proposed validation.
- X1, X2 and the A04c harness are unchanged.
