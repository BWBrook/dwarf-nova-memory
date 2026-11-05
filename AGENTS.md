# Shared instructions for Claude, Codex and subsequent contributors

## Mission and present state

Develop a defensible, bounded astronomical study of incremental predictive
information in dwarf-nova outburst histories. Barry W. Brook is the scientific
lead. This repository is a researched starting framework, not an approved final
protocol and not a completed analysis. Read `README.md`, `docs/01-research-brief.md`,
`docs/02-literature-review.md`, `docs/05-statistical-design.md` and the coordination
files before changing scientific assumptions.

No astronomical light curves have been retrieved. Every committed photometry or
forecast table under `outputs/seed_demo/` and `data/fixtures/` is synthetic. The code
fits only M0/M1 using complete oracle cycles. It does not implement M2/M3, missed
event inference or a physical accretion-disc model. Do not imply otherwise.

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

Use `coordination/board.md` to claim bounded work and hand over evidence. Record
scientific decisions and alternatives in `coordination/decisions.md`. Use separate
branches/worktrees when concurrent edits would collide. Do not claim an agent
identity proves independence: document which inputs the reviewer saw and use an
independent derivation, fixture or simulation to check consequential results.

The scientific lead decides scope, interpretation and eventual submission.
Perform routine, reversible implementation and review autonomously. Do not send
messages, contact observers, publish a manuscript, push to a remote or choose a
public licence without the user's applicable authorization. No artificial
approval gate is needed to read, validate or improve this seed locally.

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
