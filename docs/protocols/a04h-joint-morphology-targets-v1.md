# A04h joint morphology and cadence targets for benchmark qualification

Claude, 8 November 2026. Status: **proposed**. It replaces the seven
fixed-tolerance morphology gates used in A04e and A04g for any new benchmark
version. Codex completes and freezes it with the next benchmark. Evidence is
in the [A04h memo](../audits/2026-11-08-a04h-joint-morphology-targets.md).

## Operator

`scripts/a04h_morphology_targets.py` applies one operator to real 1910–1959
rows and to synthetic rows. It uses the A04d/A04e X1-episode windows. To
them it adds:
- the **core level**: the median of observer-night medians in the middle
  third of each episode's bright core;
- the rise slope.

A **real-sized replicate** is one synthetic history per era (1910–1929,
1930–1949, 1950–1959), pooled. That is the same exposure as the real record,
so each statistic's spread across replicates is its sampling spread at the
real sample size.

## Targets

Real 1910–1959 values (335 episodes):

| Block | Statistic | Real |
|---|---|---:|
| Waveform | Mean core level (mag) | 8.682 |
| | Median rise slope at 10.0 (mag/d) | 0.667 |
| | Median decline slope at 10.0 (mag/d) | 0.333 |
| | Median residual SD about the decline line (mag) | 0.222 |
| | log(median slope below / above 10.0) | −0.014 |
| | Spearman: duration vs decline slope | +0.045 |
| | Spearman: duration vs rise slope | −0.025 |
| | Spearman: duration vs core level | **−0.651** |
| Cadence | Qualifying episodes per year | 6.70 |
| | Median duration (d) | 9.85 |
| | Share with a decline fit above 10.0 | 0.833 |
| | Share with a decline fit below 10.0 | 0.782 |

The core-level correlation is the joint target that A04e and A04g lacked.
Short SS Cyg outbursts peak fainter. A generator that keeps amplitude fixed
and fits short events by steepening their flanks misses that, and shows it
first as a negative duration–decline correlation.

## Gate

For each family and cadence arm, draw at least 150 real-sized replicates on a
qualification seed namespace. Each block passes when both hold:

- **Jointly:** the real vector lies inside the 99% Hotelling prediction
  region of the replicate distribution (prediction p ≥ 0.01).
- **For each statistic:** |z| ≤ 3.3, where z is the real value minus the
  replicate mean, over the replicate SD.

A family and arm is qualified only if **both blocks** pass. These tolerances
come from sampling spread at the real sample size, not from fixed margins.
They are correspondingly tighter or looser than the A04e margins for each
statistic. For example, the old 15% decline-slope margin was 11 standard
errors wide, while the old 0.15 correlation margin was only 2.6.

Observer diversity stays a separate gate per era, as in A04g, for the
diverse cadence arm.

## Construction guidance (non-binding)

- **Waveform.** Let amplitude respond to duration rather than steepening
  flanks: a short event should rise and decline at drawn rates and turn
  over fainter. v2 does this and passes the waveform block in random
  cadence. Templates resampled from densely observed open-era outbursts
  would bring the coupling and real curvature automatically.
- **Cadence.** Every arm tested so far has too few estimates near the
  decline (fit shares 0.64–0.77 against 0.78–0.83 real). Map each synthetic
  outburst onto a donor real outburst by phase rather than calendar day:
  pre-onset, rise, plateau and decline, with the decline warped onto the
  decline. Real observers' extra attention at the end of outbursts then
  transfers. Qualify the result on the cadence block plus diversity.

## Stopping rule

Each family gets one predeclared, morphology-only calibration grid per
version. If a family fails qualification, it is recorded and dropped from
that version; the version is not abandoned. X4 validation proceeds on any
qualified family and arm, with the narrower evidence stated. If no family
and arm qualifies, the version stops and the failure is recorded.
