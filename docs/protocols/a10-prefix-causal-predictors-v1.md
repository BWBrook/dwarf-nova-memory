# A10 prefix-causal predictors, outcome evidence and precision

Claude, 8 November 2026. Status: **proposed**. Codex reviews it and runs the
positive-control validation. Barry decides the confirmatory estimand (see
Precision). Evidence: the
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
forecast without a prefix episode is kept. Its mark is missing, and every model
must use a declared fallback for missing marks; the primary fallback is the
baseline model's forecast.

## Outcome evidence

`outcome_evidence` uses retrospective X4 on the full record. It is scoring
evidence only, never a predictor. Each forecast is live from its issue time
until the next forecast is issued. It is scored on the next retrospectively
confirmed onset after τ, as the interval [max(onset_lo, τ), onset_hi], if that
onset is established before the first of:

- **coverage loss**: the start of the first gap longer than 7 d between visits
  after τ (C1/7 d);
- **supersession**: the next forecast's issue time. This ends a forecast whose
  window contains a repeat or false emission but no confirmed onset;
- **the end of the block**.

Otherwise the forecast is right-censored at the earliest of those times.

This is the truth-free duplicate policy. It uses only the observation record
and the extraction rules, never synthetic truth. Each confirmed onset scores at
most one forecast. Whether a forecast exists, and when it ends, never depends on
the length of the wait it predicts. A repeat emission issues a new forecast with
the merged episode's prefix predictors. Sensitivity analysis: drop forecasts
flagged `repeat_of_previous`.

## Reporting latency

Historical AAVSO visual estimates have no ingestion or revision dates, so every
result is an **observation-time hindcast**. The primary analysis uses L = 0. A
sensitivity analysis uses L = 2 d: the same predictors, issued 2 d later, with
age and survival conditioning shifted to match. Forecasts whose outcome onset is
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

1. **Null and structured controls:** the mean paired gain of the mark model
   over its baseline is no greater than zero within Monte Carlo error. Repeat
   under the gross-error and persistent-offset stresses.
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
holds. The confirmatory estimand must be chosen with that known; see the A10a
memo's decision request.

## Remaining before an A10 freeze

1. The confirmatory estimand.
2. M0–M3 implemented on the ledger with censoring-aware scoring.
3. Controls 1–4.
4. The development fit on 1910–1959 forecasts, the first permitted real
   duration–gap computation, after the extraction (X4, 10.0, C1/7 d) is
   recorded as frozen.
5. Horizons and update schedule.
6. The evaluation protocol commit, before any 1960+ access.
