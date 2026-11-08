# A04i: joint benchmark qualification and X4 recovery

Codex, 8 November 2026, base `df6fc7e`. This completes the proposed A04h
targets and stopping rule before new calibration/qualification/recovery.
X4 stays byte-identical to `352a09e`. All earlier failures remain unchanged.
No real duration–following-gap association, reserved data or A10 freeze is
part of this version.

## Decision and comparison

Waveform **and cadence** compatibility are required before a pair can support
X4 recovery. Missing end-phase observations are not a safely conservative
limitation: dense observations influence interval shrinkage. A failed family
is dropped before X4 scoring; it does not veto a different qualified family.
Once eligible pairs are fixed by qualification, no pair is dropped in response
to recovery outcomes. No family receives a second tuning round in this version.

The proposed twelve features are retained, in the same eight waveform/four
cadence blocks. The real and synthetic operators now both extract within the
same half-open era windows and then pool. This corrects A04h's full-stream
real versus era-sliced synthetic mismatch: 141/123/70 = 334 real episodes,
not 335. Exposure is exactly the input stratum bounds, including the final
native stop 2436934.0. A04h's original 335-episode record remains historical.
Core level means measured middle-third brightness, not a direct true-peak or
bolometric measurement. Noiseless band dependence demonstrates that waveform
geometry contributes; it does not exclude additional selection/cadence effects.

## Predictive compatibility rule

Use 150 fresh **real-sized vectors** per selected family/pair: one history per
era, pooled. Under a multivariate-normal reference, if n vectors estimate
mean/covariance and Q is the real vector's squared Mahalanobis distance,

`n(n-p) Q / [p(n-1)(n+1)] ~ F(p,n-p)`.

Each block requires prediction p ≥0.01 and every unrounded |z| ≤3.3.
Use prediction spread, not the mean's standard error. Missing/nonfinite
features, zero variances, non-SPD or ill-conditioned covariance invalidate a
block. Direct upper-tail computation avoids subtractive cancellation. Raw
numbers decide; display rounding never changes eligibility.

These are **blockwise normal-reference predictive compatibility screens**.
Neither two blocks plus marginal caps nor calibrated nuisance parameters
carry an asserted overall 1% rejection rate. The old matched-Gaussian smoke
check is not empirical validation or an equivalence guarantee. Finite tests
against R's F reference, actual block dimensions and fail-closed cases are
provided in `tests/test_a04i_predictive_gate.py`.

Per-era observer diversity remains an additional gate: median bright-observer
count within 15% and share with ≤2 within 0.05 of the identically era-sliced
real X1 operator. Include unconfirmed finite episodes spanning at least 4 d.
Do not widen these tolerances after qualification. Preserve missing days.

## Candidate-blind construction

- V2 keeps its A04e waveform and observation-noise parameters.
- The new v4 author receives original timing interfaces and separated D/Q
  marginals, not X4/X3, v2/v3, Claude training code, annotations or raw rows.
  Its rounded-power asymmetric pulse couples amplitude to duration and reduces
  amplitude for geometric feasibility rather than steepening short events.
  The middle-third/core sanity checks are latent geometry only, not observed
  feature qualification. All amplitude interventions remain in diagnostics.
- A separate source-blind author constructs phase profiles from the same
  twelve hashed native exports. Full-stream observer pseudonyms are built
  before era filtering. Profiles retain anonymous slots, limits and phase
  anchors; raw source names, IDs and positive magnitudes stay out of the cache
  interface. Anchor-resolvable unconfirmed episodes are retained. Some sparse
  episodes cannot supply anchors; skipped counts are reported.
- Six monotone source/target anchors map padded quiet, rise, core, decline
  and post-quiet phases. Donors are selected by epoch, season, duration and
  phase geometry, never observer count or following gap. Original empty
  native-JD days stay empty. Masking, collisions, added missingness, donor
  reuse and phase stretch are recorded. This is a truth-conditioned
  generative observation model, not operational observing or upload replay.

The fixed phase policy is `PhaseCadenceConfig()`; its numerical grid is not
a tuning lever. A full-suite run after cadence implementation exposes test
names/statuses, not X4 source or recovery labels. The waveform author runs
only focused tests. Do not claim an agent name alone establishes independence.

The initial mechanical profile inventory is 398/439 full-stream X1 episodes.
By peak era, profiles/episodes are 65/86 before 1910, 142/143 in 1910–1929,
118/133 in 1930–1949 and 73/77 in 1950–1959. The missing sparse profiles,
especially in 1930–1949, remain a selection limitation tested by the hard
cadence/diversity gates. Preparation is rebuilt from a clean source commit;
its code map, native hashes, exact era cuts and 334 feature episodes are
checked downstream. Anonymous profiles and raw exports stay outside Git.

## One finite calibration round

`configs/a04i_grid.json` defines ten configurations before execution:

- One unchanged v2 waveform/noise configuration with the fixed phase policy.
- Nine v4 configurations: three median-rate pairs
  `(0.667,0.333)`, `(0.8,0.37)`, `(0.95,0.4)` crossed with three bounded
  `(peak level, duration coefficient, peak scatter)` triples
  `(8.32,-0.045,0.22)`, `(8.37,-0.055,0.25)`, `(8.42,-0.065,0.28)`.

V4 log-rate spreads are fixed at 0.65 rise and 0.23 decline; the latter is
anchored by the observed decline 10–90% log span (0.2315). These are starting
latent parameters, not noise-deconvolved estimates. Noise multiplier is fixed
at 0.95. Spreads/covariances are not searched to purchase a predictive pass.

Each configuration gets 16 real-sized calibration records (48 histories),
base `a04i-calibration-20261108`, with common streams across configurations
of a family. Choose one configuration per family by minimum sum of squared
mean-target discrepancies in **fixed** units: A04h v2-random replicate SDs,
recorded before this grid. Do not divide the objective by a configuration's
own covariance. Exact ties choose configuration ID. Invalid configurations
cannot win. Preserve every attempt. Calibration does not score X4.

## Fresh qualification and eligible pairs

Commit source, grid, selected configurations, input/calibration hashes and
this protocol. Qualification base is `a04i-qualification|<full-freeze-hash>`.
Each selected pair gets exactly 150 real-sized records. Both predictive
blocks and all three diversity gates must pass. There is no seed extension,
replacement of invalid records, tolerance widening or second calibration in
this version. Record and drop a failed pair. If none qualifies, stop with X4
recovery unrun and its namespace unused.

Hash every qualification attempt with its full 150 replicate vectors. Before
recovery, recompute both blocks, diversity and eligibility for every selected
pair from these hash-bound files. A passing pair cannot be marked ineligible
and silently omitted. Verify the exact runtime-source set and parse the full
two-rule history/seed ledger when summarizing completed recovery.

Eligible pair IDs are fixed by that receipt before any X4 recovery. A pass
is conditional on the selected twelve features and fitted benchmark family;
it is not independent new astronomical data, complete physical realism or
evidence of an accretion mechanism.

## Recovery on qualified pairs only

Use four local workers, streaming outputs. For **each** eligible pair:

| Case | Histories per era | Thresholds | Role |
|---|---:|---|---|
| Independent null | 400 | 10; first 200 also 9.5/10.5 | Decisive at 10 |
| Structured zero-mark | 400 | 10 | Decisive |
| Gross-error stress | 400 | 10 | Only false-signal gates |
| Latent 0.13 alternative | 200 | 9.5/10/10.5 | Diagnostic |
| Persistent offsets | 200 | 10 | Diagnostic |

Eras are 1910–1929, 1930–1949 and 1950–1959. Thus 4,800 histories,
16,650 metric rows and 9,600 X4 magnitude-10 ledger records per pair.
X4 is scored everywhere; X1/X2/X3 references receive magnitude 10 on the
first 25 histories per base case/era. Both C1/7 d and C2/0.95 are computed.
Recovery base is `a04i-validation|<full-freeze-hash>` with family/case/era/
replicate task labels and independent truth/noise/cadence substreams.

Keep A04e/A04g criteria and pointwise 95% Monte Carlo rules unchanged:
both effective boundaries ≥90%, short-event completeness outside March–May
≥95%, retrospective false episodes and causal false-plus-ambiguous signals
each <0.2/year, |paired null bias|<0.02, premature first signals <2% and
missing <5% of unique matches. Undefined cannot pass. Use X4 point estimates
for D/Q and retain missing/unconfirmed/split adjacency barriers. The
independent/reference causal ledgers must agree before recovery scoring.

Require one global rule across all six ordinary and three gross-error cells
per eligible pair. Gross cells gate only the two false-signal rates. Prefer
C1 only if all required cells pass; otherwise C2 only if all pass. Do not
drop a pair, era or criterion after outcomes. Retain failed/inconclusive
results, the full prescribed grid and positive-control diagnostics.

Passing would qualify only retrospective open-era extraction in the tested
envelope. Prefix-causal predictor construction, reporting latency, a
truth-free duplicate policy and positive-control forecast recovery/precision
remain A10 requirements. No 1960+ access follows automatically.
