# Seed validation and explicit implementation boundary

Prepared and checked on **5 November 2026**. This record concerns the delivered
research seed. It does not validate an astronomical result.

## What was executed

The standard-library core ran under Python 3.12.14 in the preparation environment.
No Python dependency installation was needed for the demo, CSV validator or
tests. The optional figure was rendered with the available Matplotlib.

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py --output outputs/seed_demo
python scripts/plot_demo.py outputs/seed_demo
python scripts/validate_photometry.py data/fixtures/synthetic_photometry.csv
python scripts/validate_seed.py
```

The seed ships the resulting explicitly synthetic outputs. To reproduce them,
use a new output directory, because overwriting an existing run is refused. The
core was also exercised from an extracted copy of the final archive. The Git
object store and clean working tree were checked during packaging.

## Meaningful software checks

**17 unit/integration tests passed.** They cover:

- Known lognormal probabilities and exact density, event/censor probability
  partitions, conditional survival and stable tail interval/conditional probabilities.
- Invalid distributions and intervals; deterministic generation and ordered,
  nonoverlapping cycles.
- Isolation of forecasts from future target values and future predictor scaling.
- Rejection of unresolved training targets, including one earlier in the training
  block, and rejection of reversed event chronology.
- Effects of seasonal observation loss, distinct detections/limits, duplicate
  source identity and unresolved or nonfinite normalized fields.
- End-to-end reproducible CSV hashes and refusal to overwrite existing outputs.

The structural validator checks local Markdown links, citation-key/evidence
consistency, simple JSON/TOML structure, unique candidate IDs and the sixteen
generated CSV hashes. It does not verify that a referenced paper's conclusion
is true, parse BibTeX fully, test live remote services or prove model adequacy.

The configured CI matrix proposes Python 3.11–3.13; only the local Python version
above was actually run in this preparation session. No remote CI run is claimed.

## Independent review and corrections

A separate reviewing agent inspected the mathematical and chronological design,
checked survival probabilities against SciPy, and ran the tests and demo. It
identified and prompted these corrections:

1. The training-outcome availability guard now checks every training row.
2. The time-convention validator rejects `unknown` even with surrounding whitespace.
3. Limiting observations are described as censored/noisy measurements, not hard
   universal bounds on a star's true brightness.
4. Score metadata states that log predictive density is averaged per held-out
   cycle, rather than describing it as a time-normalised score.
5. The conditional event-probability helper uses stable interval probabilities
   to preserve very small left-tail probabilities and rejects unsupported time
   resolution, rather than subtracting two nearly equal survival values.

The review found no generated-path leakage or contradiction in the stated oracle
scope. Agreement is not validation of an astronomical model; the independent
calculations and concrete reproductions are the useful part of that review.

## What the demo establishes

There are four generating scenarios: independent renewal cycles, a duration
effect, a shared changing state without a direct duration effect, and both.
Each has 240 simulated complete cycles under the default seed. M0/M1 are fitted
on the first 70% and scored on later cycles. Their parameter estimates stay
fixed during that evaluation. Prediction uncertainty omits parameter uncertainty.

A separate toy photometry schedule introduces an annual gap, noise and limiting
measurements. Truth membership is used to count visible events. The forecasts
are **not fitted to those photometry rows**. This package has no demonstrated
real-data event detection or correction for missed outbursts.

The latent-only example can give a useful completed-duration forecast even when
the direct duration coefficient in the generator is zero. That illustrates why
prediction and causal interpretation must be separated. The independent-null
example can give a small positive score change in one finite draw. The figure
is neither a power study nor a calibrated false-positive experiment.

## Not yet implemented or established

Real archive retrieval and adapters; current target eligibility; event extraction
from observations; interval/censored likelihood fitting; integration over shared
boundary errors; M2/M3 state inference; partial pooling; uncertainty in fitted
parameters; adaptive effort; simulation-based power/identifiability; and actual
held-out astronomical performance. The probability helpers are
building blocks, not a complete observation model.

No authors or observers were contacted, no manuscript was
submitted, and no remote repository was created. Literature and official archive
documentation were inspected through web retrieval. Some primary full texts
remain unavailable; the evidence register records those access limits.
