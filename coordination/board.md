# Shared task board

Updated: 7 November 2026. Discussion lives in the `dwarf-nova-memory` board
section (snapshots in `docs/correspondence/`); this table is the record of
claims and handovers.

| ID | Task | Status | Suggested owner | Acceptance / next action |
|---|---|---|---|---|
| S00 | Initial literature, data and methods framework | Seed complete | Shared | Re-audit closest sources; review access-depth limitations |
| S01 | Runnable synthetic scaffold and scientific invariants | Seed checked | Shared | See `docs/12-seed-validation.md` |
| S02 | Public repo, licences, board section, first post | Done 2026-11-07 | Claude | D011; 17/17 tests and `validate_seed.py` pass on macOS, Python 3.15.0 |
| A00 | Outcome-access partition before any real light curve is plotted | Done 2026-11-07; refinements accepted by Claude | Codex + Claude | D012; [access ledger](../docs/outcome-access-ledger.md) with both exposure entries; no real data acquired |
| A01 | Independently challenge novelty and physical framing | Done 2026-11-07 | Claude | [A01 memo](../docs/audits/2026-11-07-a01-novelty-framing.md): Gate A passes provisionally with a narrower claim; prior effect size from CM92 (partial r ≈ 0.13); proposed D013 tuning/evaluation split for Codex review |
| A02 | Audit code and reproduce a key probability independently | Done 2026-11-07, seed scope only | Codex | [Audit](../docs/audits/2026-11-07-code-audit.md); 22 tests, independent fixtures, 16-table numerical reproduction |
| A03 | Resolve one real target and obtain an authentic export | Ready: SS Cyg pre-2018, after D013 is agreed | Codex | Raw file + hash + provenance; no silent conventions; no later-era event summaries before D013 |
| A04 | Annotate development events and coverage | After A03 | Claude + independent Codex subset | Boundary intervals and disagreement record |
| A05 | Audit remaining provisional pilot targets | After A03 | Split targets | One feasibility dossier per target, including failures |
| A06 | Reproduce one historical descriptive result | After A04 | Rotate implementer/reviewer | Document data/version/definition mismatches |
| A07 | Decide restricted-episode versus richer observation model | After A05/A06 | Scientific lead with agents | Gate B/C decision and revised estimand |
| A08 | Implement observational M0, then M1 | After A07 | Agent implementer + other reviewer | Censoring, boundary propagation, calibration |
| A09 | Add past-only M2/M3 and identifiability simulation | After A08 | Rotate roles | Same state architecture, no future smoothing |
| A10 | Freeze evaluation | After recovery gates | Scientific lead | Cutoffs, ledger, final targets and score |

## Current blocking information

Actual target-level data access, usable cycle counts, event-boundary precision
and an untouched evaluation interval have not been established. These are
research unknowns, not missing implementation details to fill with invented data.

## Working claim format

Before starting, append the task ID, branch/worktree, files owned and intended
deliverable. On completion, link the commit and concise evidence. Do not edit
another active agent's owned file without coordinating the handoff.

## Completed tranche — A00/A02, 7 November 2026

Codex, `main`: review the provisional access policy; audit the seed, independently
check probabilities and chronological forecasts, and repair fresh-run numerical
reproducibility checks. Owns `coordination/`, a new audit/access note, the demo
comparison script and its tests, CI and relevant README/validation text. A
read-only reviewing subagent checks survival and forecast calculations using
independent fixtures. No real astronomical data retrieval in this tranche.

Evidence: the audit above records base commit `f46284a`, commands, results and
limitations. No model/generator or committed seed outputs changed. Commit
[`c46ba1c`](https://github.com/BWBrook/dwarf-nova-memory/commit/c46ba1c4d91a5d5a6fcb2fae3cea9731205cc9f2)
records the added checks and documentation. Next: Claude reviews D012,
adds their own exposure entry and completes A01. A03 remains after that review;
the highest-value next empirical step is one bounded pre-2018 acquisition.

## Completed tranche — A01 and D012 review, 7 November 2026

Claude, `main`: novelty and physical-framing audit with two read-only Claude
Sonnet reader subagents; D012 refinement review and Claude exposure entry. Owned
files: `docs/audits/2026-11-07-a01-novelty-framing.md`, `docs/audits/a01/`,
`scripts/literature/a01_citation_map.py`, `references/a01-new-identifiers.txt`,
rows E06–E08 of `references/evidence.csv`, the A01 note in
`docs/02-literature-review.md`, the Claude entries in
`docs/outcome-access-ledger.md`, and the D012 status line. No real photometry
was retrieved. Next: Codex reviews the memo, especially §3.2's prior effect
size and the proposed D013 split, then proceeds to A03 for SS Cyg.
