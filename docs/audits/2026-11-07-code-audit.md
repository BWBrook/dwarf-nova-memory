# A02: opening code and numerical audit

**Decision:** the seed is suitable for its stated synthetic M0/M1 demonstration.
Proceed toward development-data feasibility after A01 and the access-policy
review. This is not validation of an astronomical model or permission to fit
the oracle code to real event tables.

Codex (GPT-6) audited the repository at base commit `f46284a` on 7 November
2026. A read-only Codex subagent (`gpt-5.6-sol`, high reasoning) inspected the
same seed code, tests, design and parent context before the new checks were
added. It independently integrated a density and checked censoring and forecast
chronology. This was an independent calculation, not a blinded review or an
independent model-family replication. No astronomical observations were fetched.

## Reproduction: integrity differs from numerical agreement

The original 17 tests and both validators passed on macOS/arm64, Python 3.15.0.
The committed example was prepared with Python 3.12.14. A fresh default run
reproduced eight of sixteen CSVs byte for byte. The remaining truth/forecast
tables differed in 403 numeric cells; the largest absolute difference was
`9.094947017729282e-13`, and the largest relative difference was
`1.4575006152445337e-14`. The observations and visibility tables were identical.
This is consistent with runtime/platform floating-point differences; this
comparison does not isolate their precise library-level cause.

The committed seed bytes and hashes are preserved. A new check regenerates
the run in a temporary directory, verifies the reference hashes, and compares
all sixteen tables and the scenario summaries. Floating columns allow
`abs(a-b) <= max(1e-12, 1e-12 * max(abs(a), abs(b)))`. Headers, row order, IDs,
flags, text and integer counts must match exactly; nonfinite numbers fail.
Only Python-version metadata and the corresponding per-run hashes are excluded
from the summary comparison. These are reproduction tolerances, not model
acceptance criteria or probability-accuracy bounds.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_seed.py
python3 scripts/validate_photometry.py data/fixtures/synthetic_photometry.csv
python3 scripts/check_demo_reproduction.py
```

The revised suite has 22 tests. New tests check that substantive numeric,
categorical and structural changes fail reproduction, and preserve the two
independent numerical fixtures below. CI runs the fresh reproduction check in
its existing Python 3.11–3.13 matrix. That matrix is not a cross-platform test.
New generated runs remain gitignored; the existing seed is not rewritten.

## Independently checked mathematics and information flow

For a lognormal wait with `mu=log(20)`, `sigma=0.6`, and survival to age 20,
the event probability in the next 20 days is the density integral from 20 to
40 divided by 0.5. Independent composite Simpson integration agrees with
`conditional_event_probability` to better than `1e-12`; the probability is
approximately **0.752010011494273**. The reviewer also obtained the right-censor
probability `P(Q>60)=0.16103567984645473` for `mu=log(30), sigma=0.7` using
`statistics.NormalDist`, independently of the helper's `erfc` calculation.

A constructed chronological fixture has training `log D=2+x`,
`log Q=3+0.5*x+r`, with balanced `x=-1,+1` and orthogonal residuals `r=-0.2,+0.2`.
Its analytic M1 slope is 0.5, residual MLE sigma is 0.2, and held-out median
gap is `exp(3+0.5*x)`. The new regression test reproduces these quantities and
the held-out log-density score. It checks a complete frozen-fit forecast
against an analytic construction rather than comparing the fitter with itself.

The first 70% of default events train the models; parameters stay frozen on the
remaining 30%. Every training gap resolves before the first test origin. The
training-only mean centres duration. Exact truth gaps receive log-density scores;
the central predictive interval is 90%. No generated-path leakage was found.
All-series correlations in the summary are descriptive and inspect test
outcomes; they cannot be used to select a model and still call that simulation
an untouched test. This is fixed-split forecasting, not rolling refitting.

## Requirements carried into observational implementation

- The probability helpers use ordinary-scale differences. At `mu=0, sigma=1`,
  `age=exp(38)` and a horizon near `age*1e-12`, conditioning survival is still
  representable but the numerator underflows to zero. Log-survival and
  log-difference calculations are required for production censored log scoring.
  The bundled demo does not encounter this extreme tail.
- The oracle `Event` contract supplies exact duration and consecutive complete
  gaps. The chronology guard is not an event-table validator. Real extraction
  must establish endpoint consistency, observation availability and missing-event
  status; existing perturbation tests do not cover future leakage upstream.
- Censoring-aware fitting, shared endpoint integration, missed-event inference,
  parameter uncertainty, M2/M3, and dependence-aware score uncertainty remain
  unimplemented. The schema validator checks representation, not identity,
  physical calibration or the correctness of a time conversion.
- A larger M1 gain in the latent-only demo than in the direct-effect demo is
  an illustration under different generators/seeds, not a comparison of power
  or effect strength. A fair M2/M3 comparison needs the same state architecture.
  Direct-mechanism comparisons must let marks inform state in both models.

No change to the statistical model or synthetic generator was needed. The next
decision-relevant evidence is whether pre-2018 observations support usable
end-of-outburst landmarks, not a larger oracle simulation.
