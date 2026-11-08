# Shared instructions for Claude, Codex and subsequent contributors

## Mission and present state

Develop a defensible, bounded astronomical study of incremental predictive
information in dwarf-nova outburst histories. Barry W. Brook is the scientific
lead. This repository is a researched starting framework, not an approved final
protocol and not a completed analysis. Read `README.md`, `docs/01-research-brief.md`,
`docs/02-literature-review.md`, `docs/05-statistical-design.md` and the coordination
files before changing scientific assumptions.

The requested SS Cyg native stream from 1896-01-01 through JD 2436934.0
(1959-12-31 noon under the presumed convention) is retained in 12 hashed
acquisitions outside Git; the manifest and A04 comparison report record scope.
Native visual JD is presumed UT-based and geocentric; the 0.006 d convention
sensitivity does not bound all historical record errors. A04 supplies Claude's
1956–1958 judgements and a sealed independent 1957 subset, with unresolved
boundary differences, now adjudicated (`data/annotations/`). Two candidate
extractors (`src/dnmem/extract.py`, A04b) have completed conditional synthetic
recovery screening (A04c); neither passes the frozen effective-coverage gate.
A04d found that the A04c benchmark fails predictive checks against open-era
light curves, traced every X1 boundary miss to one misclassified vote, and
proposes X3 (`src/dnmem/extract_x3.py`: fitted crossing intervals, 7 d split
rule) for fresh validation. A04e completed 7,600 histories on an independently
authored, morphology-qualified benchmark. Unchanged X3 improves conditional
coverage but fails global qualification under both coverage rules, principally
through effective coverage in state-compatible cadence. The causal wrapper's
1910–1929 unsafe-emission rate remains inconclusive. The original-v1 end
failure is retained. X3 is a tested candidate, not an accepted extractor;
see the A04e report and D015. A04f traced X3's losses to single-observer
outbursts (inflated by the state arm's donor rule, which fails an
observer-diversity check), conditional undercoverage and tail re-arming of the
causal rule, and proposes X4 (`src/dnmem/extract_x4.py`) for A04g validation
on an unseen benchmark family. A04g freeze `b83d76a` repaired observer
diversity but failed one v3 morphology gate in 384 fresh qualification
histories. X4 recovery was not run and the validation namespace is unused;
see the A04g report and D016. A04h found a v3 fixed-amplitude geometry defect
(real short outbursts have fainter measured cores; duration–core-level
Spearman −0.65) and
proposes joint waveform and cadence targets with tolerances from sampling
spread at the real sample size; every current cadence arm fails the cadence
block. A04i uses a corrected 334-episode same-era target and a finite
waveform/cadence qualification: v2 with phase-aligned cadence passes, while
the source-blind new waveform fails. Unchanged X4 then passes all decisive
magnitude-10 recovery cells in 4,800 histories under both global rules;
C1/7 d is selected by the frozen preference. Magnitude-9.5 diagnostics fail
in the later eras, and some alternative-bias comparisons are inconclusive.
This supports conditional retrospective extraction on a waveform Claude
had already studied; it is not unseen-waveform or operational validation.
See the A04i report and D017. A10a specifies prefix-causal forecast
predictors (`src/dnmem/prefix_features.py`) and a truth-free live-forecast
evidence rule. On real 1910–1959 rows, causality changes durations by about
0.05 d. A precision model gives a single-star paired forecast-gain test about
one-third power at the expected effect. Barry retained forecast gain as
confirmatory (D018), with the coefficient secondary. A10b repairs latency,
as-of evidence and invalid previous-gap handling, with an independent ledger
reference and conditional M0–M3 prototype (`ledger_forecast.py`). The timing
baseline is previous log gap, not an identified latent activity model.
Point and shared-end bracket sensitivities, common unknown-anchor fallback
and synthetic controls are development work, not full measurement/missed-event
inference. Prefix causality does not rule out measurement-induced skill.
The initial A10b run is retained as aborted/incomplete after a nonpositive
derived-mark error. Repaired freeze `4fc8d2e` repeats independent concordance
and completes all 56 trials on the original random streams: 105,509 variant
scores and 1,360 fits reconcile. Injected-effect prefix gain averages 0.00324
nats, with wide individual-history intervals. Rare point-order failures use
mark fallback. Strict oracle matching leaves 25.9% of its scored issuances on
R0, so it cannot measure skill lost through extraction. The two-day variant
delays issuance, not training-record availability. See the A10b audit; stronger
timing-only baselines and final inference calibration remain unresolved.
A10c (D020, proposed) re-aggregates the A10b scores. Forecasts lacking a covered
previous gap let duration stand in for timing, and null duration coefficients
are negative through shared end-error coupling. It specifies a directional,
matched M3 (β ≥ 0, duration only where the previous-gap term is present),
a local-level comparator, a lagged-duration placebo, a gated synthetic OC
study, and then the first real 1910–1959 fit (`docs/protocols/a10c-development-fit-v1.md`).
The later-data evaluation remains unfrozen. No operational extractor or
normalized observation release exists. Every committed photometry or seed forecast fixture
under `outputs/seed_demo/` and `data/fixtures/` is synthetic. The fitting code
in `forecast.py` still fits only M0/M1 complete oracle cycles for the seed demo;
the separate ledger prototype does not infer missed events, a filtered latent
state, parameter uncertainty or a physical accretion-disc model. Do not imply otherwise.

A10d implements the amended directional offset models and independent v3
features. Source freeze `8f5df44` passes 100-history concordance and completes
all 360 synthetic OC trials; independent numerical and aggregate audits pass.
The finite observed-rate/joint-MC screen passes, with 27.5% injected-effect
power. It is not a formal five-percent size certificate. D021 records the
positive-endpoint counterexample and non-identifying lagged-mark comparator.

D022 records Barry's subsequent acceptance of the 360-trial observed≤5%
screen. A10e freeze `b80c4a9` then completes the first real 1910–1959 fit on
330 issuances at both delays, after exact candidate/reference concordance.
Primary duration offset β=.04660 is positive; P3 is at zero. These are
in-sample working-model results, not held-out skill or physical-memory
identification. Conditional fixed-M2 likelihood-support profiles are not
calibrated confidence intervals. See the A10e memo and
`data/fits/a10e_1910_1959/frozen_parameters.json`, SHA-256
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
Every qualified A10d estimator/extractor byte is unchanged. Do not retune the
forecast system after this fit. No 1960+ observation or coverage summary has
been opened; Barry's explicit evaluation go-ahead is still required.

A10f (D023, proposed) reviewed the development fit and drafted evaluation.
A10g (D024) retains its descriptive counts but corrects median-age sign proof,
pooled iid-binomial inference and model-odds wording. It implements a sealed
native-acquisition/evaluation runner, genuine joint S1, descriptive selected-
onset CDFs and censoring-aware coverage bounds, plus independent score checks.
Any ledger/evidence mismatch halts before scoring. The six-year primary test
and frozen forecasts/parameters remain unchanged. Its protocol is
`docs/protocols/a10g-sealed-evaluation-v1.md`. Source freeze `fc40973` completed a full synthetic native-format rehearsal:
377 scored issuances, all secondaries complete, independent numerical audit
passes. All 342 tests and CI on Python 3.11–3.13 pass. Two earlier numerical
S1 failures are preserved; the final evaluation-only profiler uses bounded
scalar search for one nuisance dimension and three-point gradients for larger
searches, with strict optimizer checks. The original 26 sources and parameters
are unchanged. See `docs/audits/2026-11-08-a10g-evaluation-freeze.md`. D025 records Barry's explicit “Zenodo first, then open” choice. Protocol
DOI10.5281/zenodo.24053338 is published and its public bytes verified.
The committed/pushed DOI-bound `coordination/evaluation_access.json` enables
the single frozen 1960–2017 evaluation. No 2018+ request, source retuning,
raw-data release or manuscript release is authorized. Until the primary file
is written, inspect no observation, count, coverage summary or intermediate
result. The run receipt is the authority for execution status.

## Scientific invariants

- Cite primary research or official archive documentation for external facts.
  Read the source supporting a claim; a title or abstract is insufficient for a
  detailed methods claim. Preserve abstract-only and unresolved statuses.
- Existing serial correlations and historical memory claims are prior art.
  Novelty must be established by focused forward/backward citation searching.
- Keep within-star dependence distinct from differences among stars. A sample
  selected for dense monitoring is not representative of all dwarf novae.
- Define onset, end, duration and quiescent waiting time explicitly. Onset gaps
  contain duration algebraically; end-time errors also induce shared error.
- Do not equate statistical predictability, Markov state persistence, or a fitted
  mark coefficient with proof of physical memory or a mass-transfer mechanism.
- Respect the forecast information set. No future event labels, future-fitted
  thresholds, smoothed latent states or later-reported observations in an
  ostensibly real-time forecast. If data availability dates are unknown, call
  the evaluation observational-time retrospective, not genuine operational replay.
- Raw missing data are not quiescent measurements. A magnitude limit represents
  a flux upper limit and a numerical magnitude lower bound. Event censoring,
  missed events, and uncertain boundaries are separate inferential problems.
- Sampling may respond to outbursts. Simulating only at actual timestamps is a
  useful conditional test but does not remove informative observing behaviour.
- Keep photometric bands distinct; optical relative fluence is not bolometric
  radiated energy or accreted mass. Preserve the original time convention.
- Do not infer an absent effect from weak power. Quantify estimable effect sizes
  and operating characteristics before interpreting a negative result.

## Working together

Discussion, proposals and review happen in the `dwarf-nova-memory` section of
Barry's correspondence board; reviewed snapshots are exported to
`docs/correspondence/`. The repository remains the record: use
`coordination/board.md` to claim bounded work and hand over evidence. Record
scientific decisions and alternatives in `coordination/decisions.md`. Use separate
branches/worktrees when concurrent edits would collide. Do not claim an agent
identity proves independence: document which inputs the reviewer saw and use an
independent derivation, fixture or simulation to check consequential results.

The scientific lead decides scope, interpretation and eventual submission.
Perform routine, reversible implementation and review autonomously. The
repository is public (MIT code, CC BY-SA 4.0 content; decision D011); commits
and pushes to `origin` are routine once the checks below pass, after a staged
`gitleaks` scan. Do not send messages, contact observers, publish a manuscript,
make a first data or paper release, or commit raw third-party exports without
the scientific lead's authorization. No artificial approval gate is needed to
read, validate or improve this work.

## Reproducibility and implementation

Retain raw exports unchanged and hashed; record query, dates, identifiers, source
release, units and terms in `data/manifests/acquisitions.csv`. Add downloads only
through documented adapters with tiny local fixtures. Keep secrets outside Git.

Use explicit random seeds; give every simulation replicate its own reproducible
seed. Save configuration, input hashes, code commit and environment with results.
Freeze development decisions before accessing an evaluation block. Preserve
failed specifications and negative results when they influence later choices.

Add tests for actual scientific risks: reversed limits, silent time conversion,
duplicate source observations, future leakage, censoring, missed-event behaviour,
simulation recovery and score conventions. Do not inflate test counts with tests
that merely repeat implementation. A passing suite is not validation of the
scientific model. Begin on a laptop; parallelize only a defined simulation grid.

Run `python -m unittest discover -s tests -v` and `python scripts/validate_seed.py`
after relevant changes. Update documentation and status whenever functionality
changes. Do not present planned analyses as implemented features.
