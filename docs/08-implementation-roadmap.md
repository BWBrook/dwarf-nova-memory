# Implementation roadmap and acceptance criteria

These work packages are ordered by dependency. Time estimates are intentionally
omitted: data access and event ambiguity, rather than compute speed, determine
the early schedule. Complete a small, reviewable deliverable before broadening.

## Phase 0 — Audit this seed

**P0.1 Scientific framing.** Independently read the closest historical papers and
recent forecasting/state-change literature. Verify the bibliography and evidence
statuses. Produce a one-page overlap assessment: existing result, proposed
extension, evidence needed, and what would invalidate the claim to novelty.

**P0.2 Software.** Run all documented commands in a clean environment. Confirm
the demo's truth-based evaluation is not being mistaken for observation-based
inference. Independently check one survival probability and one chronological
forecast. Do not fit the seed's oracle model to real event tables yet.

**Acceptance:** sources support the question; limitations are understood; no
incorrect time/flux/interval semantics survive into data work. Record unresolved
questions, not just a “pass”.

## Phase 1 — Acquire and understand one star

**P1.0 Outcome-access partition.** Before plotting target histories, declare an
initial development window and keep candidate future evaluation observations
out of exploratory views. Log outcomes already known from papers or prior
inspection. The final protocol may be refined later, but an inspected interval
cannot then become an untouched test merely by assigning it a new label. If a
whole-history acquisition is necessary, separate or quarantine the later rows
before plotting or computing event summaries. Audit later coverage metadata only
under a declared policy that avoids revealing event outcomes.

**P1.1 Archive adapter.** Obtain a modest authentic export through a documented
route; begin with one benchmark that has adequate history. Save the native file,
source request, retrieval date and hash. An authorized manual export is acceptable
if a programmatic route is unavailable. Do not scrape undocumented authenticated
endpoints, infer observer identities or distribute credentials.

**P1.2 Identity and conventions.** Resolve aliases and classification; inspect
the actual native column meanings, flags, limiting measurements, time basis and
passbands. Do not silently replace a missing uncertainty or unknown time scale.
An adapter must fail or quarantine ambiguous rows and report why.

**P1.3 Visual audit.** On the designated development data, produce plots by band, observer/instrument and season,
including limiting measurements, time gaps, saturation indicators and duplicates.
Check for archive overlap rather than treating two exports as independent data.

**P1.4 Hand-labelled events.** Independently review a modest development interval.
Define onset/end operationally, annotate plausible boundary intervals and
ambiguous events, and compare two reviewers. Keep both annotations and the
reconciliation. Do not use later data to calibrate a historical forecast origin.

**Acceptance:** a reproducible raw-to-normalized conversion, documented source
semantics and a small event set with defensible boundaries. A light curve plot
alone does not meet this milestone.

## Phase 2 — Establish feasibility across the provisional pilot

Build the dossiers in `docs/04-pilot-targets.md`. Count *independent usable
development cycles*, not photometric points. Keep Phase 1–3 exploratory plots,
event counts, fitting and reproduction within the declared development access
boundary. Measure seasonal coverage and baseline
quiescent sensitivity. Record saturation and blending, unexpected behaviour,
inferred detection reliability and how many forecast origins can be issued.

Reproduce one published descriptive relation or event summary on an appropriate
historical interval, with any data/version mismatch explicitly stated. A modern
extension need not match published counts if the archive has been corrected;
reconcile the difference rather than tuning until it matches.

**Acceptance:** the sample and estimand survive the observation audit. Decide
whether the project supports an initial conditional-coverage benchmark, needs
a richer event model, or should narrow to fewer systems.

## Phase 3 — Build the first observation-based analysis

Implement a conservative event/boundary representation and define coverage
eligibility without examining the target value or forecast error. For the first
analysis, prefer intervals with demonstrably adequate surveillance. Explain that
this changes the target population to those intervals; it does not solve missing
events elsewhere. Carry uncertainty in endpoints and marks through the fit.

Implement a star-specific renewal baseline with appropriate right censoring and
entry conditions. Compare at least one alternative gap-distribution family or
a regularized empirical baseline. Add completed duration before a large feature
set. Propagate uncertainty in the forecast distribution, including parameters.

Add a past-only changing-activity comparator, initially simple enough to audit.
If latent-state inference is adopted, test filtered forecasts separately from
retrospective smoothed states. A new output table must state its information set.

**Acceptance:** known signals and known nulls behave acceptably under realistic
simulation. A single synthetic example with the desired result is insufficient.

## Phase 4 — Freeze and evaluate

Choose the scientific question, target cohort, development windows, score,
evaluation windows, horizons and exclusion rules before accessing evaluation
outcomes. Store a signed-off configuration and Git commit. If any part changes
after inspection, retain the change history and designate fresh validation or
label the analysis exploratory. Do not manufacture a preregistration date.

Use chronological held-out blocks, appropriate uncertainty across stars and
temporally dependent cycles, calibration, and paired score differences. Weight
stars intentionally. Report the coverage-conditioned target population and
where the data cannot verify an outcome. Run declared observation/boundary
sensitivity analyses without cherry-picking the most favourable alternative.

**Acceptance:** reproducible evaluation tables plus simulation-calibrated
interpretation; no claims beyond effective sample size or available information.

## Phase 5 — Independent scientific review and paper

Prepare a compact pack for a domain astronomer: question, nearest papers, data
and exclusions, one event audit, predictive comparisons, simulations and the
remaining physical interpretations. The user decides whether to contact them;
no external message is sent by this seed or its agents.

Write from `manuscript/outline.md`. Separate the descriptive, predictive and
mechanistic claims. Deposit code/configuration and only data whose terms permit
it. Include an access/reproduction recipe when raw observations cannot be
redistributed. Choose venue, authorship and licence after the actual contribution
is clear; no submission is implied by this plan.

## Suggested module growth

| Module / artifact | Next responsibility | Dependency |
|---|---|---|
| `adapters/` (future) | Documented archive-specific conversion with native fixtures | P1.1/P1.2 |
| `provenance/` (future) | Immutable acquisition IDs, hashes and deduplication audit | P1.1 |
| `events/` (future) | Interval boundaries, ambiguous events, operational labels | P1.4/P2 |
| `observation/` (future) | Detection windows, sampling and missing-event sensitivities | P2/P3 |
| `models/` (future) | Observational M0–M3, parameter uncertainty and pooling | P3 |
| `evaluation/` (future) | Historical issue-time reconstruction, proper scores, calibration | P3/P4 |
| `simulation/` (future) | Configured factorial experiments and recovery summaries | P3 |

Create these modules when they acquire a real responsibility. The seed does not
ship empty implementations masquerading as a finished analysis pipeline.
