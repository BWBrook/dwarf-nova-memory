# A04g independent X4 validation

Codex, 8 November 2026, base `4816f89`. This completes and amends Claude's
[proposal](a04g-x4-validation-v1.md) before new candidate recovery outcomes.
Candidate X4 stays byte-identical to `352a09e`; X1/X2/X3 remain unchanged.
The A04e failed validation is retained unchanged. No real duration–following-gap
association or reserved data are part of this experiment.

## Independent components and scope

The new v3 author receives neither X4/X3 source, v2 source, Claude's training
code, annotations nor raw rows. Original timing API and the existing parameter
names are available. The author implemented the new pulse family and its
focused tests before a full-suite run exposed other test names/pass statuses;
no prohibited source or recovery numbers were read. This limited subsequent
exposure is disclosed, not described as complete isolation.

The first v3 half-cosine family (`c9d51b8`) failed a morphology-only pilot:
short-event geometry steepened slopes, inducing measured slope–duration rho
−0.399. That specification and its result are retained. The candidate-source-
blind author revised it (`75f90e4`, `7212934`) to global monotone polynomial
flanks plus a flat peak. Curvature allocation preserves original D/Q,
reference crossings, independent tangent slopes and peak amplitudes. It has
no threshold join, but the curvature basis is centred on the reference
crossing; do not claim threshold-independent physical realism. Strongly
adapted shapes remain a structural limitation. The seven morphology gates
and nearby-threshold diagnostics test its observable consequences. No X4
recovery score informs these revisions. V2 waveform/noise parameters remain
byte-bound to `a04e_benchmark.json`.

A separate author repairs cadence without X4 source or training results.
The observation skeleton retains original empty native-JD bins, observer
identities, visit times within bins and limits. The initial rotating-day
repair (`ef34d42`) fixed medians but lost the low-diversity tail. A whole-event
bootstrap (`95fd7d2`) restored that tail but overlaid independent missingness
and failed morphology/median checks. Both failed prototypes are retained.
The revised rule matches whole donor episodes on calendar span, season and
epoch, without matching observer count or a following gap. Donor-missing
days create additional explicitly recorded empty days; none are faint
measurements. This is a truth-conditioned stress model on observed days,
not a model of observation initiation or reporting latency. Its exact rule is
the committed
`src/dnmem/x4_cadence.py`; fit no extraction-outcome criterion to it.

## Qualification gates and a proposal inconsistency

Apply the same seven A04e morphology checks to both families and both phases,
pooling eras within phase: three median features within 15%, slope–duration
rho within 0.15 absolute, side-slope ratio within factor 1.5, and both
positive-fit fractions within 0.15 absolute. All required fields must exist.

The repaired diverse arm must additionally reproduce, **in each era and
family**, the real X1 operator's median bright-observer count within 15% and
the share with at most two observers within 0.05. Use all X1 episodes with
finite onset_lo/end_hi and span at least 4 d, including unconfirmed episodes;
filter peaks into the era. Same operator for real and simulated rows. Real
targets independently reproduce Claude's 142/129/76 episodes, medians
14.5/16/14 and low-diversity shares 0.0211/0.1008/0.1184. Mean donor no-match
fraction must be at most 0.10.

Claude's proposed 15% gate would reject his own random-arm median 13 versus
16 in 1930–1949. Do not widen that tolerance to get a pass. The amendment is
to require diversity qualification for the repaired arm and retain random
cadence as a **mandatory conservative robustness control**, with its known
observer-cast mismatch explicitly reported. It must still pass recovery and
morphology; it is not called diversity-qualified. A random-control failure
is a robustness veto, not evidence that the real extractor fails. Neither
its effect sizes nor the family comparison establish real-era performance.
The old A04e state arm remains a non-gating reported stress.

## Calibration and independent seeds

Three distinct stages, with all failed attempts retained:

1. Morphology-only calibration: seed base `a04g-calibration-20261108`;
   two histories per era/phase. V3 finite grid: rise median {0.8,0.95,1.1},
   decline median {0.34,0.40,0.46}, noise multiplier {0.85,0.95,1.10}:
   27 configurations. Other shape parameters are committed defaults. Select
   the passing configuration minimizing the sum of normalized squared
   morphology discrepancies; exact ties choose grid order. V2 is evaluated
   once with its unchanged parameters. No X4 recovery score is computed.
   If no configuration passes, retain the failure and amend the benchmark
   before fresh qualification; validation seeds remain unused.
2. Commit the source, parameters, inputs and protocol. Fresh qualification
   base `a04g-qualification|<full-freeze-commit>`, 32 histories per
   era/phase/family. Both families and phases must pass their stated gates.
   Qualification may not access X4 recovery outcomes.
   The 32-history size is fixed before any fresh qualification, increasing
   precision for the relatively rare low-diversity episodes; there is no
   after-failure seed extension.
3. Only after qualification passes, recovery base exactly
   `a04g-validation|<full-freeze-commit>`. Task seed labels include case,
   family, stratum, phase and replicate; independent truth/measurement/cadence
   and contamination substreams derive from that seed.

All input/source/candidate bytes and calibration attempts are bound to hashes.
Check declared runtime sources both before and after execution, including
the decision script. Do not modify them during qualification/validation.

## Causal implementation and error contamination

An independent causal implementation was written and hash-recorded before
reading X4 reference source. Its first source SHA is
`a57930613ef0255d8c1e94e367fe10f5a5db64188d15750ef2d0bd184bcc5772`.
The exact pre-exposure source is archived at
`data/provenance/a04g_x4_causal_preexposure.py.txt`. Those bytes were
reconstructed after exposure and match the hash acknowledged in the parent
session before reference inspection; this is not an independently timestamped
pre-exposure Git commit.
After exposure it agreed exactly with the reference on adversarial fixtures
and 500 seeded finite fuzz histories. Every validation history must compare
canonical independent/reference emission ledgers **before recovery scoring**;
disagreement is a harness failure, not an empty or skipped candidate result.

The rule arms on strong bright evidence (0.5 mag past threshold) from two
observers or one observer on two native-JD nights; two distinct sufficiently
faint observers emit permanently. Visits become available at first JD+0.15;
equal-time visits are atomic, bright dominates faint, and unarmed faint
evidence clears stale provisional state. Later data never erase emissions.
Final X4 duration estimates are still not claimed available at first emission.

The gross-error arm replaces estimates from selected quiet observer-night
groups with a persistent magnitude drawn uniformly in 8.5–9.8 for clusters
of 1–3 consecutive available nights of the same observer. Missing days break
a cluster. Exclude true events plus 3 d on either side. The randomized integer
budget yields an expected contaminated observer-night fraction of 0.0032;
account for cluster length in that budget rather than multiplying the rate
by persistence. Repeated estimates within a night are all replaced and count
once in the contamination quota. Record actual visits/rows/clusters affected.

This adopts five times the published 0.064% bright-visit proportion as a
**stress intensity**, not an identified wrong-star rate. Those real bright
reports are not labelled wrong stars, and the observer-night quota is explicit.
Strong bright errors are intentionally much more common here than the two
real reports brighter than 9.5. The stress is not a calibrated probability
model of archive mistakes.

## Fixed recovery grid and computational envelope

Use four local workers with streaming outputs. All extractors receive the
same observations; only scoring receives truth. Reference subsets are fixed
before any outcomes and never used to select a coverage rule by cell.

| Case | Family | Cadence | Histories per era/phase | Thresholds |
|---|---|---|---:|---|
| Independent primary | v2, v3 | random, diverse | 400 | 10; v3 first 200 also 9.5/10.5 |
| Structured zero-mark | v2, v3 | random, diverse | 400 | 10 |
| Gross errors | v3 | random, diverse | 400 | 10 |
| Latent 0.13 alternative | v2, v3 | random, diverse | 200 | v3 all three; v2 10 |
| Old donor stress | v2 | legacy | 200 | 10 |
| Persistent offsets | v3 | random | 200 | 10 |
| Original-v1 challenge | v1 | random | 200 | 10 |
| Sparse 1900s | v3 | random, diverse | 200 | 10 |

Eras are 1910–1929, 1930–1949 and 1950–1959 except the 1900–1909 diagnostic.
There are 16,600 histories. X4 is scored on every history/threshold under both
C1/7 d and C2/0.95. X1/X2/X3 are descriptive references at magnitude 10 on
the first 25 histories per base cell; X3 also receives all 200 histories per
original-v1 cell. Expected metric rows: 51,800. Persist 33,200 X4 magnitude-10
pair/emission ledger records, keeping heavy arrays out of the CSV and Git.

This retains 400 histories in every decisive cell while limiting redundant
reference extraction. The alternative, offsets, old donor, original-v1,
early-era and threshold arms are diagnostics, not post hoc selection gates.

## Criteria and interpretation

Keep A04e criteria and pointwise 95% Monte Carlo conventions unchanged:
effective coverage ≥90% at both boundaries, short-event completeness outside
March–May ≥95%, retrospective false episodes and causal false-plus-ambiguous
signals each <0.2/year, paired absolute null bias <0.02, first-emission
premature <2% of issued unique matches and missing <5% of unique matches.
Missing/non-unique/nonfinite boundaries stay in effective denominators.
Undefined quantities cannot pass. Report conditional coverage, point bias,
RMSE, widths, matching losses and single-observer confirmations separately.
Use X4 `onset_t/end_t` for D/Q; keep unconfirmed/gap-split adjacency barriers.

All 24 ordinary X4 family/control/era/phase cells must pass one global rule.
Six gross-error cells are decisive for **only** the two false-signal criteria.
Thus require 30 passing cells per global rule, prefer C1 only if all pass,
otherwise C2 only if all pass; never switch by cell. All failures and
inconclusive cells remain as observed, with no post-validation repair or
seed extension. Retain the full frozen grid even when the verdict is known.

A pass qualifies only retrospective open-era extraction in this tested
envelope. It does not freeze A10, authorize reserved-data access, establish
real forecast skill or show physical memory. Prefix-causal features, a
truth-free duplicate-signal policy and prespecified positive-control
forecast recovery/precision remain separate requirements.
