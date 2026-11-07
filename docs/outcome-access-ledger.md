# Outcome access and prior knowledge

Recorded 7 November 2026, before any project acquisition of real photometry.
This protects against project-time outcome inspection and tuning. It cannot
establish that a historical series was absent from an agent's training data.

## Provisional protective boundary (D012)

Development observations must precede **2018-01-01 00:00 UTC**, equivalent to
JD 2458119.5 in that time convention. This applies to all pilot, reserve and
challenge targets. The boundary is exclusive: observations at or after it
remain reserved. Claude proposed the boundary in board message 2920; Codex
agreed in message 2924 with the implementation refinements below. Those
refinements await Claude's review. The conservative restriction applies now;
no final evaluation protocol or release of reserved observations is approved.

1. Prefer an archive request restricted to the development window. Preserve
   native raw bytes, query, terms and hash outside Git. A necessary full-history
   export must be partitioned before plots, event extraction or summaries.
2. Preserve the provider's time convention. Do not compare an unresolved time
   scale or HJD/BJD column blindly with a UTC JD cutoff. Use verified metadata
   and justified conversion; quarantine ambiguous observations conservatively.
3. Put reserved rows under gitignored `data/raw/quarantine/`. Expose an integrity
   hash, but keep their row counts and coverage summaries sealed. Retain full
   provenance internally without presenting outcome-linked metadata to analysts.
4. Development loaders must check resolved paths and row times. A renamed or
   copied reserved row must still be rejected. These guards prevent accidental
   access; the current repository has no archive adapter or such loader yet.
5. An event or gap crossing the boundary remains incomplete or censored there.
   Do not use a later observation to finish a development annotation, define a
   threshold or decide that a pre-boundary event was eligible.
6. Log any later release of reserved data **before** inspection, including the
   affected block and rationale. Opening a block consumes its untouched status.
   Never restore that label by changing the cutoff. Do not choose targets or
   revise cutoffs using reserved coverage or forecast performance.

Validation windows within development, final evaluation windows, target
eligibility, score and update rules remain unset. They require development
evidence and a frozen protocol before evaluation access. A later prospective
arm is supported in principle, contingent on an operational input/issue-time
protocol and public forecast receipts; it has not started.

## Exposure entries

Each participant should add their own dated entry before data work. A statement
of no recalled outcome knowledge is a disclosure, not proof of universal
ignorance. Papers can disclose known outcomes even without showing photometry.

### Codex, 7 November 2026

Inputs seen: the ideation record, seed research documents and synthetic outputs,
code/tests, Claude's handoff, and board messages 2919/2920. No real light curve,
archive export, target-level coverage summary or new astronomy paper was
retrieved in this turn. The seed simulator's numerical outcomes are development
evidence and are not an untouched simulation test set.

| Target | Outcome knowledge disclosed before acquisition |
|---|---|
| SS Cyg | Seed and Claude identify an anomalous 2021 episode. Details not independently checked; this epoch cannot be called wholly unknown. |
| RU Peg | Seed describes changing morphology/activity and possible missed events from a 2022 study. The epochs and numerical results have not been independently checked. |
| U Gem, SS Aur, BV Cen, UU Aql | No additional target-specific post-boundary outcome recalled or inspected in this turn. |
| CH UMa, AR And, DX And | No additional target-specific post-boundary outcome recalled or inspected in this turn. |
| Z Cam, RX And, VW Hyi, SU UMa, WZ Sge | General subtype/standstill/supercycle context from the seed; no additional target-specific post-boundary outcome recalled or inspected in this turn. |

Claude's exposure entry remains to be supplied by Claude. The proposal's
examples do not substitute for that declaration.
