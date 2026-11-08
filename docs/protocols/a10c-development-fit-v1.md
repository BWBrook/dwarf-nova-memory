# A10c: forecast system, operating characteristics and the 1910–1959 development fit

Claude, 8 November 2026. Status: **proposed for Codex review**. Builds on the
[A10 predictor protocol](a10-prefix-causal-predictors-v1.md) and the
[A10b specification](a10b-model-controls-v1.md). Reasons and evidence: the
[A10c review](../audits/2026-11-08-a10c-controls-review.md). D018 is unchanged:
held-out M3−M2 forecast gain is confirmatory and the coefficient secondary.
Nothing here opens 1960+ data. The extraction stays X4 (`352a09e`) at
magnitude 10.0 with C1/7 d coverage.

The order is fixed: §1 is implemented and frozen, §2 runs on synthetic data,
and only if §2 passes does §3 touch real 1910–1959 forecasts. §4 is the
evaluation freeze, which waits for Barry.

## 1. The forecast system

### 1.1 Ledger

Keep `a10-prefix-v2` and add two fields computed from the same prefix
episodes, under the same rules:

- `previous_duration`: the prefix duration of the previous confirmed episode.
  It is unavailable when that episode is unconfirmed, begins less than 30 d
  inside the window, or has duration ≤ 0.
- `earlier_gaps`: the log quiet gaps between consecutive confirmed prefix
  episodes, both beginning more than 30 d inside the window, that end at or
  before the previous episode's onset and are covered under C1/7 d. Keep the
  six most recent at most.

**Point-order rule:** a point duration ≤ 0 makes that mark unavailable, for
the current and the previous episode alike. Nothing is clipped or dropped.

Extend the independent ledger reference to the new fields and repeat the
100-history concordance at both latencies before any score.

### 1.2 Models

Lognormal landmark clocks with the A10b likelihood: interval and censored
evidence, conditioned on survival to the landmark age. Every model is fitted
once, on development data, and then frozen.

| Model | μ of the log quiet gap | Where it applies |
|---|---|---|
| M0 | α | every forecast with a known end |
| M2 | α + γ₁q + γ₂L | forecasts with a covered previous gap; elsewhere M0 |
| M3 | M2 + βx, with **β ≥ 0** | M2's forecasts with a valid duration; elsewhere identical to M2 |
| P3 | M2 + β′x′, with **β′ ≥ 0** | M2's forecasts with a valid previous duration; elsewhere identical to M2 |

- q is the standardized log covered previous gap, as in A10b.
- L is the standardized mean of `earlier_gaps`, and 0 (the training mean)
  when there are none.
- x is the standardized log point duration of the current episode; x′ is the
  same for the previous episode.
- An unknown end gives every model the common R0 forecast, as in A10b.

**Matched routing.** Duration never enters a forecast unless the comparator's
timing covariate does. A forecast without a covered previous gap contributes
exactly zero to M3−M2.

**Nesting.** Fit M3 and P3 on M2's training rows, setting x = 0 (or x′ = 0)
where the mark is unavailable. The likelihood at β = 0 is then M2's, so a fit
at the bound reproduces M2 exactly. M1 belongs to no contrast and need not be
fitted.

The bounds use L-BFGS-B. A duration coefficient at its bound is a valid
outcome, not a failed fit; report it as `at_bound`.

### 1.3 Confirmatory statistic (D018)

The statistic is the mean per-issuance log-score gain of M3 over M2 across
every evaluation issuance, zeros included, using parameters frozen at the
1910–1959 fit. The one-sided 95% lower bound comes from cluster-robust means
over consecutive three-year calendar clusters, referred to t with
(clusters − 1) degrees of freedom. The result is **confirmed** if the bound
exceeds zero.

Because β ≥ 0, a confirmed gain means duration improves forecasts in the
published direction. If the development fit puts β at its bound, the gain is
identically zero and the test cannot confirm. That would be known before the
evaluation block is opened, and the evaluation protocol must record it.

### 1.4 Secondary analyses and diagnostics (pre-declared)

- **S1, coefficient:** the unconstrained duration coefficient fitted on the
  evaluation block alone, with its interval (D018 secondary).
- **S2, memory placebo:** compute P3−M2, and M3−P3 on forecasts where both
  marks are valid, with the §1.3 interval method. Under direct memory the
  previous outburst's duration carries little beyond the previous gap. Under a
  slowly varying shared state it predicts nearly as well as the current one.
  A confirmed M3−M2 whose M3−P3 interval includes zero does not distinguish
  memory from shared state. The report must say so.
- **S3, sensitivities:** uniform-end marks (the A10b five-node mixture, with
  the same routing and bound); the A10b comparator (q only); the 2 d issuance
  delay; the type/within-type mark.
- **Schedule and horizon:** frozen parameters; the whole remaining-wait
  distribution is scored, ending only at coverage loss, supersession or the
  end of the block.

## 2. Operating-characteristic study (synthetic; Codex)

Freeze the §1 source and use a fresh namespace, `a10c-oc|<freeze hash>`. Use
the A10b trial design: about 50 development years, then 58 evaluation years,
on an artificial timeline built from pre-1960 source-pattern strata.

| Family | Case | Trials |
|---|---|---:|
| v2-phase | independent null | 40 |
| v2-phase | serial structured, zero direct effect | 40 |
| v2-phase | slow shared state, φ = 0.9 | 40 |
| v2-phase | slow shared state, φ = 0.98 | 40 |
| v2-phase | gross reports | 40 |
| v2-phase | persistent observer offsets | 40 |
| v2-phase | adaptive observing effort | 40 |
| v2-phase | injected effect (partial 0.13) | 40 |
| v4-phase | independent null | 20 |
| v4-phase | injected effect | 20 |

Null, gross, offset and adaptive trials share random streams, as in A10b.

**Slow shared state** is a new latent mode, a fixed stress grid rather than a
fit to data:

- s_n = φ s_{n−1} + √(1−φ²) η_n;
- latent D_n = λ s_n + √(1−λ²) u_n;
- latent Q_n = λ s_n + √(1−λ²) v_n;
- λ² = 0.13, so the shared state alone produces the published partial
  correlation;
- no direct D→Q term and no other serial terms.

**Report for each case:**

- the confirmatory rejection rate with its Monte Carlo SE;
- the mean gain and its across-trial SD;
- the distribution of fitted β and the share at the bound;
- S1–S3;
- the rejection rates for P3−M2 > 0 and M3−P3 > 0.

**Conditional coverage.** For the 40 injected-effect trials and the 40
independent-null trials, score each trial's frozen models on a fresh 300-year
continuation. That gives the trial's expected gain. Report how often the
two-sided 90% block interval covers it.

**Criteria for proceeding to §3:**

1. The rejection rate is at most 0.05, within 2 MC SE, under the independent
   null, serial structured, gross, offset and adaptive cases.
2. Conditional coverage is within MC error of nominal. If three-year clusters
   fail, switch to six-year clusters, which is the only permitted change, and
   report both.

Slow-state rejection rates and placebo discrimination are reported, not
gated: they define what a positive real result can mean. If criterion 1
fails, stop and report. Do not retune the system against the study.

The power under the injected effect, with its MC SE, replaces the A10a
Gaussian figure as the precision statement.

## 3. The real 1910–1959 development fit (Codex, after §2 passes)

1. Record the freeze in `coordination/decisions.md`: X4 `352a09e`,
   magnitude 10.0, C1/7 d, `a10-prefix-v2` with the §1.1 fields, the §1.2
   models, and the source hash. This is the extraction freeze that A10
   requires before any real duration–gap computation.
2. Build the ledger for issue times in [1910-01-01, 1960-01-01) at latencies
   of 0 and 2 d. Compute evidence as of 1960-01-01 from rows before that date
   only, with unresolved outcomes censored at the cutoff.
3. Fit M0, M2, M3, P3 and the S3 variants once. Report:
   - coefficients with profile-likelihood intervals and bound status;
   - in-sample log-likelihood gains per forecast;
   - route, exclusion and fallback counts;
   - every fit diagnostic.

   Log this in the outcome-access ledger as the first real duration–gap
   computation.
4. Change nothing in the system afterwards. A failure to converge allows only
   additional deterministic starts, documented. Publish the frozen parameter
   file with its hash.

## 4. Evaluation freeze

Commit the evaluation protocol before any access. It contains:

- the frozen parameter file and scoring-code hash;
- the §1.3 test, with the cluster length §2 selected;
- the §2 precision statement;
- the S2 interpretation;
- the access mechanics for 1960–2017.

Opening that block cannot be undone for the confirmatory test, so it waits
for Barry's explicit go-ahead. 2018 onward stays reserved.
