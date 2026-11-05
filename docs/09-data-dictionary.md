# Data contracts and provenance

This is a proposed analysis contract. Original archive schemas remain unchanged
in raw storage. The implemented CSV validator checks the narrow normalized
photometry representation below. It does not validate astronomical identity,
photometric calibration, scientific eligibility or time conversion.

## 1. Normalized observations (implemented representation)

| Column | Type / semantics |
|---|---|
| `source_row_id` | Provider's row identifier, or a reproducibly generated ID tied to an immutable raw file and row |
| `target_id` | Project identifier resolved through the target/alias table |
| `time_value` | Finite numerical timestamp, retaining native convention unless a documented conversion is applied |
| `time_format` | Numerical representation, e.g. `JD`, `MJD`; demo uses `relative_demo_days` |
| `time_scale` | Explicit scale such as `UTC`, `TDB`, or demo-only `synthetic` |
| `time_reference` | Light-time/correction reference, e.g. observatory, geocentric, heliocentric or barycentric; demo uses `simulation_origin` |
| `band` | Native passband or method; visual, V, g, r and unfiltered measurements remain distinguishable |
| `magnitude` | A measured magnitude; empty for a limiting observation |
| `magnitude_error` | Reported positive uncertainty if available; empty means unknown, never zero precision |
| `is_upper_limit` | Literal `true` or `false`; “upper” refers to **flux**, not numerical magnitude |
| `limit_magnitude` | Faint limiting magnitude, present only for an upper-limit row |
| `observer_id` | Archive observer/instrument code when supplied; use explicit `unknown` if unavailable |
| `quality_flag` | Preserved or mapped flag with its mapping documented; not automatically a boolean “good” |
| `provenance_id` | Foreign key to the acquisition manifest |

The pair `(provenance_id, source_row_id)` must be unique. It is a necessary local
integrity check, not a sufficient cross-archive deduplication rule. Coincident
times do not prove duplication; repeated exports or republished original
measurements may be duplicates even under different identifiers.

Unresolved time scale, representation or reference is quarantined before
normalized analysis. Original unknown fields remain in the raw export. Do not
turn `HJD` into `BJD_TDB` by renaming a column: representation, time scale and
light-travel correction are separate choices. At day-scale recurrence, numerical
precision may be modest, but provenance must still be honest.

`limit_magnitude=14` represents a reported faint non-detection: the threshold
direction is lower flux, equivalently numerically greater magnitude. It is not
an exact quiescent magnitude of 14 or a noiseless bound on the true source flux.
A censored measurement supplies a probabilistic constraint on true flux under
the provider's noise and detection model. The toy simulator, for example,
thresholds a noisy measured magnitude. Limiting thresholds, significance levels
and errors depend on the provider and need native metadata.

The validator does not reject mixed, explicitly labelled conventions because it
does not merge them. A subsequent modelling adapter must require a coherent
time system and supported observation model. Extra native fields should be
retained in a sidecar table, not silently dropped.

## 2. Acquisitions (empty real-data manifest supplied)

`data/manifests/acquisitions.csv` has headers but no real acquisitions. Populate
one row per immutable export or well-defined acquisition batch. Record provider,
query, target, source URL, UTC retrieval timestamp, file hash, native conventions,
filters, terms URL, redistribution assessment, software version and notes.

`available_until` records the cutoff on what had been available to the analyst,
where ascertainable. An observation's time is not automatically its upload or
publication time. Without availability timestamps, the project can assess
chronological retrospective forecasting but should not claim a faithful replay
of live operational forecasting.

For many-to-many attribution, add a separate mapping from processed rows to all
contributing native rows and transformations. Store retraction/correction and
archive revision information when available.

## 3. Proposed event table (not yet an implemented extractor)

| Field group | Required information |
|---|---|
| Identity | `target_id`, `event_id`, event-definition version |
| Onset | Earliest/latest plausible onset; evidence rows; whether left-censored |
| End | Earliest/latest plausible end; evidence rows; whether right-censored |
| Detection/confirmation | First alert/detection, end confirmation time, and what information made each available |
| Marks | Band-specific duration, peak excess, optional relative fluence, uncertainty and coverage |
| Event class | Normal, candidate superoutburst, standstill transition, ambiguous, with provenance and probability where appropriate |
| Observation coverage | Coverage before/during/after, gaps, limiting sensitivity, saturation and overlap flags |
| Inference | Joint boundary/mark posterior-draw reference, not only marginal point estimates |
| Review | Annotators, reconciliation notes, agreement and version |

Duration, onset gap and quiescent gap must be derived from a consistent joint
draw of boundaries. Independently jittering their reported error bars breaks
their covariance structure. Do not assume two observed outbursts are consecutive
unless that is established or integrated over as an uncertainty.

## 4. Proposed forecast table

One row per target, issue time, model, horizon and fit/configuration version.
Record issue time, data availability cutoff, last confirmed event/end, verified
quiescent age, full predictive distribution or its reproducible representation,
event probability over each horizon, training-data hashes, model code hash,
forecast population/eligibility and parameter version. Keep forecasts immutable.

Store outcome ascertainment separately: next-event boundary interval, censoring,
potential missed events, validation evidence and observation coverage. Add
scores only after predictions are frozen. Forecasts that cannot be evaluated
remain in the denominator accounting, with an explicit reason.

## 5. Simulation truth versus observed data

`synthetic_truth.csv` contains injected onsets, ends, durations, next quiescent
gaps and latent activity. `synthetic_observations.csv` contains sampled toy
photometry. `oracle_visibility.csv` joins observations to known simulated events
to count hits; it is not an inferred real-data event table. `oracle_forecasts.csv`
uses complete truth to demonstrate M0/M1 comparisons.

The demo's last event has a simulated next gap to an unrendered sentinel onset.
This is allowed in the **oracle** experiment, but not evidence that the
photometry observes that final target. A real observation-based evaluation would
censor it at the observation horizon.

## 6. Optical marks

If a common, calibrated passband supports a relative optical-fluence proxy, a
candidate is the time integral of flux excess over a documented local quiescent
baseline. Magnitude must first be transformed to linear relative flux. The
baseline must be estimated from permitted past data for forecasting, or its
retrospective use explicitly separated. Integrating across an unobserved interval
requires a model and uncertainty; filling it by interpolation does not create
observations. Preserve colour/filter differences and upper limits.

This proxy is not bolometric energy or accreted mass. Any conversion to either
would require additional astrophysical assumptions and measurements outside
the first-paper scope. See `10-domain-primer.md` and the referenced DIM review.
