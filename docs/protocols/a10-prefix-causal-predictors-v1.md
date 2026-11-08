# A10 prefix-causal predictors, outcome evidence and precision

Claude, 8 November 2026; reviewed by Codex in A10b. Status: **proposed, revised
for development**. Barry's D018 decision keeps forecast gain confirmatory and
the coefficient secondary. The repaired `a10-prefix-v2` and bounded model
controls are specified in [A10b](a10b-model-controls-v1.md); A10c revises the
models and sets the development fit. Evidence: the
[A10a memo](../audits/2026-11-08-a10a-prefix-predictors-review.md). This
protocol covers SS Cyg at magnitude 10.0 with X4 (`352a09e`) and the C1/7 d
coverage rule that A04i qualified. It does not freeze A10 and does not open
1960+ data.

## Issue events

Every X4 causal end confirmation (`causal_confirmations`) issues one forecast.
The issue time is τ = `emitted_at` + L, where L is a uniform reporting latency.
Every emission is retained, including false and repeat emissions, as D008
requires.

## Predictors

For each emission, `dnmem.prefix_features.forecast_features` runs X4 on the rows
with emitted_at − 400 d < JD ≤ emitted_at, and on nothing else. The current
episode is the last prefix episode whose end bracket reaches the emission's
bright evidence (`end_hi ≥ bright_first_at − 1.15 d`). The ledger records:

- emission index, issue time, latency, prefix window and last prefix JD;
- prefix onset and end: estimate, interval, method and number of fitted
  estimates; duration = end − onset;
- age at issue a = τ − end;
- confirmation type and peak magnitude (recorded, not used by primary models);
- the previous episode's end and the previous gap, both from the same prefix,
  with its longest monitoring hole and C1/7 d status. The previous episode must
  begin more than 30 d inside the window;
- `episode_found` and `repeat_of_previous` (the prefix onset lies within 1 d of
  the previous forecast's).

**Contract:** no row with JD > emitted_at can change any ledger field.
`tests/test_prefix_features.py` enforces this with poisoned future rows. A
forecast without a prefix episode is kept. Its mark is missing. Missing marks
use the corresponding baseline; an unavailable end anchor uses the same
issue-anchored remaining-wait R0 forecast for every model.

## Outcome evidence

`outcome_evidence` uses retrospective X4 through an explicit as-of cutoff. It
is scoring evidence only, never a predictor. Training recomputes it at the
training cutoff, with no later rows. The next onset is assigned relative to
the emission before latency: an overtaken onset is flagged, not replaced with
a later one. A bracket straddling issue does not establish survival and is
commonly excluded, retaining its ledger entry. Eligible forecasts are scored
on the original onset interval if it is established before the first of:

- **coverage loss**: the start of the first gap longer than 7 d between visits
  after τ (C1/7 d);
- **supersession**: the next forecast's issue time. This ends a forecast whose
  window contains a repeat or false emission but no confirmed onset;
- **the end of the block**.

Otherwise the forecast is right-censored at the earliest of those times.

This truth-free duplicate policy uses the observation record and extraction
rules, never synthetic truth. Each confirmed onset scores at most one forecast.
Keep whole gaps crossing issue when applying coverage loss. These rules define
a restricted issuance estimand; they do not prove independent censoring or
physical-cycle survival. Repeat/false emissions remain observation-process
limitations. Earliest operational outcome availability is not known; the
development implementation uses conservative as-of availability and frozen
fits. See A10b for explicit exclusions and fallback rules.

## Issuance delay and reporting availability

Historical AAVSO visual estimates have no ingestion or revision dates, so every
result is an **observation-time hindcast**. The primary analysis uses L = 0. A
sensitivity analysis uses L = 2 d: the same predictors, issued 2 d later, with
age and survival conditioning shifted to match. This is an **issuance-delay
diagnostic**: A10b does not shift the availability of training records or
implement a uniformly delayed reporting stream. Forecasts whose outcome onset is
established before τ are flagged as overtaken and excluded for every model
alike. Latency that differs by observer cannot be reconstructed, so no result is
called operational.

## What every model must do

- Condition on survival to the prefix age a, using the landmark formula in
  `docs/05-statistical-design.md` §2. The baseline then already accounts for
  the confirmation lag, and a mark earns credit only for information about the
  remaining wait.
- Score the same evidence under the same coarsening for every model: interval
  probability for onsets, survival for censored forecasts.
- Use only the ledger and the outcomes of earlier forecasts whose evidence was
  complete by τ. Refitting is either frozen or follows a prespecified online
  schedule.

## Threshold

The primary threshold is 10.0. 10.5 is a secondary sensitivity: its primary
cells pass, its injected-effect bias is inconclusive, and unsafe signals reach
0.09 per year. Drop 9.5, because X4's 0.5 mag arming and confirmation margins
fall inside the peak distribution of short outbursts there (memo §1).
Retuning X4 for 9.5 would require a new candidate and fresh validation, and is
not proposed. Because amplitude and duration are coupled, any change of
threshold changes which outbursts are counted, not only how they are measured.

## Controls Codex runs before the freeze

Run on fresh seeds with the v2-phase benchmark, with the full ledger → evidence
→ model → score chain:

1. **Null and structured controls:** distinguish no true duration information
   from no direct duration effect. A measured mark can correct age error or
   proxy latent activity left in a timing-only baseline. Report the complete
   chain's gains and Monte Carlo uncertainty, including gross-error,
   persistent-offset and adaptive-effort stresses; do not equate compatibility
   with zero with proof of absence. A10b supplies the bounded development grid.
2. **Positive control:** under the latent alternative (copula 0.13), report the
   gain and its sampling SD at the evaluation block size, and compare oracle
   (true D, true end), retrospective and prefix predictors.
3. **Stress diagnostic (not a gate):** repeat 1–2 once on v4-phase, which is
   unqualified. A04i did not score it.
4. **Concordance:** an independent reimplementation reproduces the ledger and
   evidence exactly on 100 histories before any scores.

## Precision

`scripts/a10_precision.py` is a standardized Gaussian model of the mark's added
partial correlation r. It uses 300 development forecasts and 1,000 replicates,
and is optimistic: there is no censoring or dependence. At r = 0.12, near what
remains after extraction dilution, with 390 evaluation forecasts (projected
from the open-era rate, not counted):

| Statistic | Frozen parameters | Online refit |
|---|---:|---:|
| Mean paired gain (nats/forecast) | 0.0055 | 0.0060 |
| Sampling SD of the block gain | 0.0071 | 0.0063 |
| P(gain > 0) | 0.83 | 0.86 |
| Power, one-sided paired score test | 0.32 | 0.21 |
| Power, one-sided slope test | 0.77 | 0.77 |

Roughly 1,000 evaluation forecasts are needed before the paired score test
reaches about 60% power. One star's 1960–2017 block cannot be expected to make
the forecast gain statistically decisive, even if the published association
holds. Barry chose to retain forecast gain as confirmatory (D018). The
coefficient remains secondary; lower power does not authorize changing the
research question after outcomes.

## Remaining before an A10 freeze

The [A10c protocol](a10c-development-fit-v1.md) (D020, proposed) now sets
items 1–5: a directional matched M3 with a local-level comparator, a gated
operating-characteristic study, then the development fit. The list below
is kept as the A10b-era record.

1. Final inference calibration for the D018 forecast-gain estimand.
2. The A10b conditional M0–M3 prototype is implemented; settle the stronger
   timing-only comparator, point-order and oracle-matching policies.
3. A10b completes the bounded controls 1–4; a larger frozen operating-
   characteristic study and observation-process review remain necessary.
4. The development fit on 1910–1959 forecasts, the first permitted real
   duration–gap computation, after the extraction (X4, 10.0, C1/7 d) is
   recorded as frozen.
5. Horizons and update schedule.
6. The evaluation protocol commit, before any 1960+ access.
