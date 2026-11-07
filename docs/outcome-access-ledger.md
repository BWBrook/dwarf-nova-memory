# Outcome access and prior knowledge

Recorded 7 November 2026, before any project acquisition of real photometry.
This protects against project-time outcome inspection and tuning. It cannot
establish that a historical series was absent from an agent's training data.

## Provisional protective boundary (D012)

Development observations must precede **2018-01-01 00:00 UTC**, equivalent to
JD 2458119.5 in that time convention. This applies to all pilot, reserve and
challenge targets. The boundary is exclusive: observations at or after it
remain reserved. Claude proposed the boundary in board message 2920; Codex
agreed in message 2924 with the implementation refinements below. Claude
reviewed and accepted all six refinements on 7 November 2026 (A01 memo, section
6.6). The conservative restriction applies now;
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

### Claude, 7 November 2026 (written before this turn's literature search)

Inputs seen in the project: the ideation record, seed documents, synthetic
outputs, code and tests, Codex's audit and board messages 2919–2928. No real
light curve, archive export or target-level coverage summary has been retrieved.
Beyond the project, my training data include astronomy literature and
observer-community reports up to roughly mid-2026. I cannot inventory what that
contains. Below is what I can recall as of this entry, written from memory before
looking anything up. Vague or unchecked recollections are marked as such.

| Target | Outcome knowledge recalled before acquisition and before A01 reading |
|---|---|
| SS Cyg | An anomalous 2021 episode in which the normal outburst pattern gave way for months to a standstill-like or low-amplitude state, reported as unprecedented in its long record. I do not recall its exact dates, when normal outbursts resumed, or any post-2018 outburst timings or durations. Pre-boundary generic knowledge: a mean recurrence of order 50 days, and a long/short outburst dichotomy (unchecked; A01 checks it). |
| U Gem | Nothing post-2018 recalled. Pre-boundary generic knowledge: a recurrence of roughly 100+ days and at least one historically anomalous long outburst (1985, unchecked). |
| SS Aur, RU Peg, BV Cen, UU Aql | Nothing post-2018 recalled beyond the seed's RU Peg morphology summary. |
| CH UMa, AR And, DX And | Nothing post-2018 recalled. |
| Z Cam, RX And | Generic standstill behaviour only. A vague, unchecked recollection that Z Cam was in or near a long standstill at some point in the late 2010s; I could not date it. |
| VW Hyi, SU UMa | Generic supercycle behaviour only; nothing post-2018 recalled. |
| WZ Sge | Superoutbursts in 1913, 1946, 1978 and 2001 (unchecked). I recall no superoutburst after 2001, which is itself weak post-boundary knowledge of an absence. |

**Exposure from A01 itself.** The novelty search must read papers published
after 2018, and some will describe post-boundary behaviour of pilot targets.
I read them for methods and claims, and I do not extract post-2018 outburst
timings, durations or recurrence statistics for any target. Any post-boundary
target fact I meet is appended below with its source, before data work starts.

#### Claude A01 exposure addendum, 7 November 2026

Completed after the A01 search. The reader subagents were told not to report
post-2018 numbers for pilot targets, and none appeared in their reports.

- **SS Cyg:** no post-2018 outburst information met. Titles seen: Kimura et al.
  2021, already disclosed, and a 2022 PASJ paper simulating the light curve of
  the 2021 anomalous event (title only, not read).
- **RU Peg:** Šimon 2022's data span is not stated. Its O–C epochs run to about
  E = +20 from JD 2456237 with T_C ≈ 90 d, which ends roughly in late 2017, so
  it may touch the boundary. I saw only a qualitative summary: fluence is not
  related to T_C, candidate missed outbursts exist, and a long gap in dense data
  means no outburst or one at least 2 mag fainter. No dated post-2018 events.
- **Z Cam, RX And (challenge set):** Ohshima 2023 covers 1995–2022. I now know
  that Z Cam has two typical intervals (about 22 and 33 d), RX And has two
  (about 13 and 17 d), and intervals shorten before standstills. This partly
  spans the reserved period.
- **Other targets:** nothing post-2018.
- **Pre-boundary knowledge gained:** CM92's 1896–1992 correlations and Price et
  al.'s 1904–2006 SS Cyg statistics. Both are development-era and affect no
  reserved block, but they are prior knowledge of the development data. Steps
  1–3 of the A01 memo's first analysis use them as anchors, not as tuning
  targets for the frozen hindcast.
