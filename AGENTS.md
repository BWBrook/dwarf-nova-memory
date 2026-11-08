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
See the A04i report and D017. No frozen operational
extractor, normalized observation table or forecast table exists. Every committed photometry or forecast fixture
under `outputs/seed_demo/` and `data/fixtures/` is synthetic. The fitting code
still fits only M0/M1 using complete oracle cycles. It does not implement M2/M3,
missed event inference or a physical accretion-disc model. Do not imply otherwise.

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
