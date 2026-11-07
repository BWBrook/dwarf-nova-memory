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
| A01 | Independently challenge novelty and physical framing | Done 2026-11-07 | Claude | [A01 memo](../docs/audits/2026-11-07-a01-novelty-framing.md): Gate A passes provisionally with a narrower claim; published partial r ≈ 0.13 verified; [power interpretation and D013 amended](../docs/audits/2026-11-07-a01-review-d013.md) by Codex |
| A02 | Audit code and reproduce a key probability independently | Done 2026-11-07, seed scope only | Codex | [Audit](../docs/audits/2026-11-07-code-audit.md); 22 tests, independent fixtures, 16-table numerical reproduction |
| A03 | Resolve one real target and obtain an authentic export | Native acquisition done 2026-11-07; normalization pending | Codex | [A03 receipt](../docs/audits/2026-11-07-a03-ss-cyg-acquisition.md): 3438 visual rows, 124 limits, raw hash/manifest; only 1956–1959; native time scale/reference unresolved |
| A04 | Annotate development events and coverage | Claude 1956–1958 done 2026-11-07; Codex blind 1957 subset next | Claude + independent Codex subset | [A04 memo](../docs/audits/2026-11-07-a04-review-and-annotation.md): 23 events, envelope boundaries about 1 d, endpoint-error shift ≈ 0.003; Codex annotates 1957 blind under [protocol v1](../docs/protocols/a04-event-bracketing-v1.md), then compares |
| A05 | Audit remaining provisional pilot targets | After A03 | Split targets | One feasibility dossier per target, including failures |
| A06 | Reproduce one historical descriptive result | After A04 | Rotate implementer/reviewer | Document data/version/definition mismatches |
| A07 | Decide restricted-episode versus richer observation model | After A05/A06 | Scientific lead with agents | Gate B/C decision and revised estimand |
| A08 | Implement observational M0, then M1 | After A07 | Agent implementer + other reviewer | Censoring, boundary propagation, calibration |
| A09 | Add past-only M2/M3 and identifiability simulation | After A08 | Rotate roles | Same state architecture, no future smoothing |
| A10 | Freeze evaluation | After recovery gates | Scientific lead | Cutoffs, ledger, final targets and score |

## Current blocking information

SS Cyg native access is established for one early interval (1956–1958).
Visual JD is presumed UT-based geocentric, bounded at 0.006 d. Boundary
precision in well-covered seasons is about a day (A04). Second-annotator
agreement, coverage in earlier decades, extraction rules, usable-cycle counts,
other targets and operating characteristics remain unresolved. The 1960–2017 candidate
evaluation is sealed at the raw-data level under D013, with published aggregate
exposure disclosed. These are research unknowns, not values to invent.

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

## Completed tranche — D013 review and A03, 7 November 2026

Codex, `main`, base `a89a084`: independently audit the A01 effect-size and power
claims, resolve the proposed SS Cyg access split before retrieving photometry,
and pursue a date-restricted authentic acquisition if the revised policy permits.
Owns a new review/calculation script and tests, D013/access/config updates,
A03 adapter/report/fixtures if supported by the native export, manifest and
status records. A read-only methodological reviewer checks the arithmetic and
holdout logic; no delegate may retrieve light curves. Reserved eras remain
uninspected. Outcome: [D013 review](../docs/audits/2026-11-07-a01-review-d013.md) and
[authentic acquisition](../docs/audits/2026-11-07-a03-ss-cyg-acquisition.md) complete.
The official web export required sign-in; the source-supported VStar route
succeeded anonymously. Native time normalization and observational fitting are
not complete. A03 raw bytes stay outside Git; the public manifest records their
hash. Current checks: 26 tests, seed validator and numerical reproduction.
Next: Claude reviews D013 and the receipt, resolves timing/flag documentation,
then begins independent pre-1960 annotation. Full CM92 reproduction is deferred
until primary evaluation is sealed.

Code, provenance and review commit: [`1428ce2`](https://github.com/BWBrook/dwarf-nova-memory/commit/1428ce27bf9ad0b47eb29f8e79d9193f437e2c26).
The handoff is board thread 142; raw exports and the local figure are not committed.

## Completed tranche — D013 review, metadata check and A04 annotation, 7 November 2026

Claude, `main`, base `04a8b69`. I accepted D013's amendments and checked native
timing and flag documentation. I then annotated SS Cyg outbursts in
1956-01-01 to 1959-01-01, using a protocol pushed (`1bfbca5`) before any
magnitudes were viewed. Owned files:

- `docs/protocols/a04-event-bracketing-v1.md`;
- `docs/audits/2026-11-07-a04-review-and-annotation.md`;
- `src/dnmem/brackets.py` and `scripts/a04_*`;
- `data/annotations/`;
- `tests/test_brackets.py` and `tests/test_a04_annotation.py`;
- the D013 review line, the status lines in AGENTS/README, and my ledger entry.

No 1959+ data were viewed. Next: Codex annotates the 1957 subset blind (memo
§4), then compares, then acquires the rest of the open era in bounded requests.
