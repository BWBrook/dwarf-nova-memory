# Shared instructions for Claude, Codex and subsequent contributors

## Mission and present state

Develop a defensible, bounded study of incremental predictive information in
dwarf-nova outburst histories. Barry W. Brook leads the science. Read
`README.md`, the brief/literature/statistical-design documents, current
protocols and coordination decisions before changing scientific assumptions.

The first frozen real SS Cyg forecast comparison is complete. Across 441
1960–2017 issuances, M3−M2 gain is 0.01653 nats, with six-year-cluster 90%
interval [0.00495,0.02812], meeting the single predeclared rule. The later
1993–2017 segment and type/within-type variant are inconclusive. This is
incremental information under a specific frozen visual extraction/timing
baseline, not physical-memory identification or a general dwarf-nova result.
See `docs/audits/2026-11-09-a10i-sealed-evaluation.md` and its aggregate
artifacts in `data/provenance/a10i_evaluation_1960_2017/`.

Protocol DOI 10.5281/zenodo.24053338 was published before access under D025.
Original source freeze fc40973; parameter SHA-256
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
The first attempt failed before scoring on literal missing uncertainty `None`.
D026's exact-token adapter repair preserves every row/string and changes an
analysis-unused field. Independent code-path/synthetic invariance review,
344 tests and a fresh full rehearsal precede repair freeze 5e39aeb and pushed
execution authority d7151e0. The run completes after this post-access format
repair; the evaluation cannot be called untouched. All original 26 forecasting
sources, parameters and protocol bytes are unchanged. Preserve every failure,
receipt and frozen output; do not retune or overwrite this comparison.

X4 at magnitude 10, C1/7-day coverage, prefix-causal features and the frozen
working lognormal models define the estimand. Retain failed X1–X3 benchmarks
and known-waveform/measurement limitations. Candidate/reference ledger AND
evidence concordance must hold before any score; independent scalar numerical
checks verify all 2,641 actual variant scores within 1.91e-13. S1 association
profiles condition on a fixed evaluation M2 and are not calibrated confidence
intervals or mechanism tests. Absolute predictions overcover in this sample.
The finite simulation screen did not certify a true 5% error rate.

Raw AAVSO acquisitions through 2017, original pre-1960 context/cache and full
outputs are hashed and retained outside Git. No raw export, observer identity,
new event catalog or per-issuance score table is released by this result.
Native visual JD is presumed UT-based/geocentric; convention sensitivity does
not bound all historical errors. Historical upload/revision availability is
unknown: call this observation-time retrospective, never operational replay.
No physical disc model or missed-event inference is implemented. Fixtures and
seed photometry remain synthetic; the committed fit/evaluation aggregates
are real and clearly labeled.

**2018 onward remains closed.** No later archive row, count, coverage summary
or light curve may be requested or inspected without a new explicit decision.
The single authorized comparison is complete; current access status is marked
completed, with the execution authority retained at d7151e0. Saved-data
reproduction and clearly labeled exploratory work cannot become a second
confirmation. Claude's A10j review accepts the result
(`docs/audits/2026-11-09-a10j-result-review.md`, D028). Codex's A10k check
reproduces its exploratory numbers and C11–C13, while narrowing their interpretation
(D029). Global recentering does not remove within-period drift. The class fit
has greater in-sample likelihood without establishing exclusive attribution
to class or excluding a slow driver. The type-component restriction is not a
restriction on the whole type/within-type rule. Paper work follows the living-paper model. `manuscript/estimands.md`
governs every phrasing, and `manuscript/claims.csv` is the single evidence
ledger, checked by `python3 tools/claims.py check manuscript/claims.csv`.
Four scientific figures and a brief figure build into explicitly labelled previews;
substantive products in `manuscript/text/` remain templates until drafted. Raw-data/manuscript releases still need
Barry's applicable authorization and the observer-credit/terms review.

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
