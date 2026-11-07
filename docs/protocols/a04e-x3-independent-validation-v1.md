# A04e independent X3 validation: calibration and execution specification

Codex, 7 November 2026, base `66cfdf2`. This completes and amends the proposed
[A04d protocol](a04d-x3-validation-v1.md) before recovery outcomes are generated.
X3 stays byte-identical to `c0353c0`; X1/X2 are references. Passing this
conditional benchmark can qualify retrospective extraction within its tested
envelope. It does not freeze an A10 forecast pipeline or permit reserved-data
access.

## Benchmark scope and preserved challenge

The original generator has a knot exactly at magnitude 10 and a duration-linked
decline rate. Its failure to reproduce selected open-era light-curve summaries
justifies replacing it as the primary gate. Its X3 failure remains a reported
misspecification challenge, without being re-labelled a success. Aggregate
summaries do not prove that every real decline is linear, that an unobserved
event is unrecoverable, or that 7 d is a physical minimum quiet time.

The independent generator author sees neither X3 source, annotations, training
generator nor real rows. It preserves the existing timing streams and uses
asymmetric half-Gaussian pulses with flat peaks, no special threshold knots,
baseline 11.8, and independent rise/decline slope draws. If the requested
peak cannot fit the specified duration, amplitude is reduced. Crossings are
solved numerically; overlapping intervals at diagnostic thresholds are unioned.
Gaussian tails below 1e-12 mag are a numerical tolerance. This curved family
is deliberately distinct from a straight-line crossing template.

Realism refers to an **X1/measurement-operator-conditioned comparison**, not
independent physical validation. The same Theil–Sen window estimator is applied
to raw open-era rows and generated noisy rows. It selects X1-confirmed,
non-split events with finite brackets and positive-slope fits. Spearman ranks
use average ranks for ties; insufficient/constant data fail qualification.
No real duration–following-gap association is computed.

## Three distinct seed stages

1. **Finite calibration:** base `a04e-calibration-20261107`, two histories per
   era/phase per configuration. Evaluate the fixed Cartesian grid of rise
   medians {0.75,0.95}, decline medians {0.34,0.40,0.46}, decline log-SDs
   {0.20,0.35}, and noise multipliers {0.95,1.15,1.35}: 36 configurations.
   The code's remaining shape parameters are fixed. Use common underlying
   random streams, no recovery scoring. Among configurations passing every
   morphology gate in both cadence phases, select the smallest sum of squared
   normalized discrepancies; break exact ties by grid order. Preserve all
   attempts. If none pass, amend the generator specification before continuing.
2. **Morphology qualification:** freeze code, selected parameters and this
   protocol in Git. Seed base `a04e-qualification|<full-freeze-commit>`;
   twelve fresh histories per era/phase, pooled by phase. No extractor recovery
   is scored. Both phases must pass. A failure requires a new version and
   fresh qualification namespace; validation seeds remain unused.
3. **Extractor validation:** only after qualification passes, seed base exactly
   `a04d-validation|<full-freeze-commit>`. The freeze hash did not exist during
   Claude's X3 development. Do not change candidate parameters or morphology
   after drawing these outcomes. All failed/inconclusive outcomes are retained.

At magnitude 10, morphology qualification requires median rise slope, median
end slope and median end residual SD each within 15% of the corresponding real
summary; |rho_syn−rho_real| ≤ 0.15; below/above median decline-slope ratio within
a factor 1.5 of the real ratio; and each side's positive-fit fraction within
0.15 absolute of real. Every required value must be present. Summaries at
9.5/10.5, side-specific slopes, fit fractions and broad quantiles are reported
as diagnostics. These checks reproduce selected targets; they do not establish
an exhaustive morphology distribution.

## Observation model and cadence

Use the same separately calibrated duration/gap marginals as A04c. Fit
leave-observer-out residuals at native observer-bin median brightness
8.5–10.5. Offset shrinkage is n/(n+10); variance blends the floored residual
MAD variance with the original quiet-model variance using that weight. Exact
recorded limit slots and the previous rounding/shared-noise recipe remain.
The chosen global noise multiplier is calibrated solely by morphology checks.
The unshrunk-offset diagnostic adds fixed observer offsets, SD 0.2 mag, without
shrinking them or changing row noise.

The second decisive cadence is **availability-preserving and state-compatible**:

- Preserve every empty calendar bin in the original schedule. Absence never
  becomes a quiescent label or a new observation.
- Observed donor bins receive a majority B/F label from one median positive
  estimate per observer; informative limits count as faint only if no positive
  estimate is present. Ties/missing information remain mixed/unknown.
- For each observed target bin, use synthetic brightness at the original
  bin's median observation time to define B/F. Borrow the nearest observed
  donor of that state within ±15 d in the same era; ties choose the earlier
  day. Translate fractional native-JD times and preserve observers/limit slots.
- If no donor exists, retain the original schedule and flag the fallback.
  Report borrowed/no-match fractions. Mean no-match fraction above 10% makes
  the state-compatible arm unqualified/inconclusive.

This changes observation intensity within the observed-day skeleton. It does
not model state-dependent initiation on missing days or establish an operational
observing policy. It is a truth-conditioned generative stress model.

## Frozen validation grid

Use four local workers after a smoke test. Each synthetic history is supplied
identically to all three extractors; truth is supplied only to scoring.

- **Primary:** v2 independent null, both cadence phases, 1910–1929,
  1930–1949, 1950–1959, 400 histories per cell at threshold 10. First 200
  histories also supply threshold-9.5/10.5 sensitivities.
- **Structured zero-mark control:** v2, both phases and those three eras,
  400 histories at threshold 10. Retain latent previous-gap correlation 0.282
  and gap persistence 0.382 while setting the latent partial mark effect to
  zero. It is decisive alongside the independent negative-control null. Raw
  Pearson partial correlation after marginal transforms need not be exactly
  zero; paired bias is always against each realized raw-scale oracle.
- **Alternative:** v2 copula alternative, both phases and those three eras,
  200 histories per cell at all three thresholds. The 0.13 target is latent;
  compare extracted raw-scale statistics with each realized oracle.
- **Persistent-offset diagnostic:** v2 null, original cadence, 200 per era,
  threshold 10, added fixed observer offsets with SD 0.2.
- **Original-v1 challenge:** original morphology and observation model,
  original cadence, 200 per era, threshold 10.
- **1900s diagnostic:** v2 null, both phases, 200 per cell, all thresholds.

Total: 7,600 histories and 79,200 finder/threshold/coverage-rule metric rows.
C1/7 d and C2/0.95 are both computed. C1 is selected only if it passes every
independent and structured cell; otherwise C2 can be selected only if it passes
every such cell. No per-cell switching is permitted. X1/X2 are contextual references.

## Scoring and operational confirmation completion

Keep all interior true events in effective-coverage denominators. Also report
conditional coverage, type/month completeness, split/merge counts, widths,
point errors, fallback frequency/coverage and eligibility failures. X3's
`onset_t/end_t` drive D/Q; references use interval midpoints. An unconfirmed
bright episode between confirmed episodes censors that adjacency. A gap-split
endpoint censors both neighbouring adjacencies. Persist pair-level records;
the diagnostic correlations use completed eligible triples and are not a
fitted censoring-aware forecast likelihood.

The batch X3 `confirmed` field is retrospective: a later bright tail can erase
an earlier confirmation. Therefore it is reported separately and cannot qualify
the operational criterion. The pre-run completion is an immutable causal
execution wrapper for the stated two-observer rule:

- Close an observer visit at first-row JD+0.15; never backdate availability
  to its median timestamp. Limits remain directional.
- Arm after bright votes from two observers. A new bright vote resets faint
  evidence. After arming, the first two distinct observer visits at least
  0.5 mag faint emit a permanent confirmation timestamp.
- The same two strongly faint observers close an unarmed, single-observer
  provisional event without emitting, so stale bright evidence cannot join
  unrelated later outbursts.
- Process visits with identical close times jointly. Any available bright
  vote resets faint evidence and suppresses all same-time faint emissions,
  so observer names cannot decide whether a confirmation exists.
- Re-arm after fresh bright evidence; never erase an emitted timestamp when
  a later tail is merged retrospectively. Preserve false, ambiguous and
  duplicate emissions. Score first emission per true event, with a separate
  all-truth sensitivity and explicit missing counts.

This wrapper is a specified observation-time execution policy, not evidence
that final X3 endpoints or predictor estimates were available at that time.
Prefix-causal forecast features and historical upload latency remain A10 work.

## Qualification criteria and inference

Each X3 decisive era/phase/mechanism cell must clear all bounds with a 95% Monte Carlo
interval: effective coverage ≥90% at **both** boundaries; short-event
completeness outside March–May ≥95%; false confirmed episodes <0.2/year;
absolute paired null-association bias <0.02; first-emission premature rate
<2% of issued unique-matched events and missing rate <5% of unique matches.
The false-episode criterion applies both to the retrospective catalogue and
to false causal emissions, so erased or unmatched emissions cannot evade it.
Undefined statistics cannot pass. No widening, repairs or seed extensions
are fitted to the validation outcomes.

Ratios pool event-count denominators and use replicate-cluster delta MCSE;
other diagnostics use replicate means. Premature/missing confirmation rates
also use a design-effect Wilson interval: effective binomial sample size is
min(event count, p(1−p)/cluster-MCSE²) for interior p, and the replicate count
at p=0 or 1. Union it with the cluster-normal interval. Thus zero events do
not produce a zero upper bound. This is an approximate Monte Carlo procedure,
not distribution-free evidence about the real star.

Pass/fail/inconclusive uses the whole interval, as in A04c. Candidate sources,
parameters, data and results are hash-bound. A failed benchmark cannot be used
to qualify an extractor; a successful conditional screen cannot establish
physical memory, real forecast skill or a universally safe 7 d gap rule.
