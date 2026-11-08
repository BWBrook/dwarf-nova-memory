# A10e: first SS Cyg 1910–1959 development fit

Codex, 8 November 2026. Adapter/profile freeze
`b80c4a9dd52f659663345190ea9da6bb205410a0`; forecasting methods remain at
A10d freeze `8f5df44`. D022 records Barry's explicit acceptance of the finite
360-trial observed≤5% screen. That screen passed before any native row was
opened for this fit. D018 remains held-out forecast gain.

## Result

The frozen primary model fits a **positive duration offset**, β=0.04660 per
standard deviation of log duration, to 330 pre-1960 development forecasts.
Its conditional fixed-M2 likelihood-support range is [0.00652,0.08667]. The
lagged-duration offset is at its zero bound, with support [0,0.01240].

These are in-sample working-model results. They neither confirm held-out
forecast improvement nor identify direct physical memory. Mark profiles hold
estimated M2 parameters fixed, and serial dependence and measurement
uncertainty are not calibrated for these support intervals. No model choice
was changed after this fit.

| Variant | Scored issuances | Duration offset(s) | Mean in-sample M3−M2, nats |
|---|---:|---:|---:|
| Primary, q plus local history | 330 | 0.04660 | 0.00787 |
| Uniform-end mixture | 330 | 0.04943 | 0.00817 |
| Previous-gap-only baseline | 330 | 0.04450 | 0.00704 |
| Two-day issuance delay | 330 | 0.04648 | 0.00782 |
| Type and within-type offsets | 330 | 0.05053; 0.01184 | 0.00478 |
| Joint-valid current/lagged marks | 307 | 0.04660 | 0.00846 |

The lagged mark fits exactly zero in every variant. That does not distinguish
memory from state: the retained A10d pure-state simulations show that current
duration can beat its lag without a direct memory term. The type sensitivity
is a constrained two-offset model, not a selected replacement for the
continuous primary mark.

The primary baseline has intercept 3.65998, standardized previous-log-gap
slope 0.07802, local-history slope 0.05134 and residual log-gap σ=0.34636.
Its development likelihood gain over M0 is 0.03883 nats per issuance. These
are likelihood summaries on the fitting data, not forecast-skill estimates.

## Access and fit chronology

The committed D022 answer precedes raw access. The run receipt records native
opening at **2026-11-08 10:49:36 UTC**, first real fit at **10:50:31 UTC**,
and completion of all six models at **10:50:32 UTC**. All twelve existing
acquisitions retain the hashes in the frozen anonymous cache. Rows are
restricted to JD 2413559.5 through 2436934.0; no new request is made. Native
JD and band/quality handling are preserved. Pre-1910 rows supply only past
prefix context; model issuances lie in [2418672.5,2436934.5).

The candidate and independently implemented reference ledgers and evidence
match exactly at both delays before fitting. At the primary delay there are
307 interval-onset outcomes, 22 coverage-censored outcomes and one censored
at supersession. Every issued forecast is score-eligible. M2/M3 use timing
covariates on 307 rows and share M0 fallback on the remaining 23; no unknown-
end R0 fallback is needed. No real Pearson correlation is computed.

An initial CLI invocation used an abbreviated freeze ID; the clean-source
guard rejected it before native access or output-directory creation. The
full-ID invocation above is the sole fitting execution. All models are saved
before profile diagnostics, with deterministic starts and convergence records
retained. Profiles reoptimize diagnostic nuisance parameters without changing
the saved forecast system. Maximum scalar/vector objective difference is
9.1e-13, and the largest diagnostic reoptimization improvement is 8.8e-9 NLL.

The independent serialized-output audit checks all 1,957 variant score rows,
their populations/routes, likelihood totals, source windows and all profile
records without importing the candidate forecast/profile code. It reports
zero failures and maximum score discrepancy 7.46e-14. The independent
[audit summary](../../data/provenance/a10e_audit_checks.json) is committed.
The 310-test suite and validator pass; CI is green on the exact adapter
freeze. No additional starts or failed fits were needed.

## Frozen outputs and interpretation

[Frozen parameters](../../data/fits/a10e_1910_1959/frozen_parameters.json)
have SHA-256
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
The [summary](../../data/fits/a10e_1910_1959/summary.json),
[compact profiles](../../data/fits/a10e_1910_1959/profiles.json),
[run receipt](../../data/fits/a10e_1910_1959/run-receipt.json) and
[manifest](../../data/fits/a10e_1910_1959/manifest.json) are committed. Full
ledgers, evidence, profile evaluations and scores remain outside Git.
Archive `a10e-20261108-b80c4a9` contains 34 files and 4,299,028 bytes;
inventory SHA-256 is
`541e2fc90b207006240bc3a9af3bea93fe576dbf7659051eab38ec1048770216`.

Reproduction uses the retained twelve native acquisitions and the same
anonymous identity cache, in a clean checkout of the adapter freeze:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
uv run --frozen --extra analysis python scripts/a10e_real_fit.py fit --freeze-commit b80c4a9dd52f659663345190ea9da6bb205410a0 --output outputs/a10e_reproduction
uv run --frozen --extra analysis python scripts/a10e_real_fit.py profiles --freeze-commit b80c4a9dd52f659663345190ea9da6bb205410a0 --output outputs/a10e_reproduction
```

A reproduction reruns the already-consumed development sample; it does not
restore its untouched status. The reporting checkout can compact a completed
run with `scripts/report_a10e.py`. Likelihood-support bounds use the declared
3.841 LR cutoff, with clipping and fixed-parameter statuses retained; they
are not calibrated confidence intervals.

The positive development coefficient means the frozen confirmatory comparison
will not be identically zero. The A10d precision result remains modest:
27.5% power in its injected-effect scenario and a median per-history interval
half-width of 0.00975 nats. The actual evaluation result is unknown.

No 1960+ observation, coverage count or forecast has been opened. Next is
Claude's review of the development fit and an evaluation protocol tied to
this exact parameter hash, followed by Barry's explicit go-ahead before
1960–2017 access. 2018 onward remains reserved. Any eventual archival replay
uses observation time, not unrecorded historical publication availability.
