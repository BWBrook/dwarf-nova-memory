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

### SS Cyg inner access split (D013, 7 November 2026)

For SS Cyg, only observations before 1960-01-01 00:00 UTC are open for
development. The 1960–2017 raw-data block is reserved pending a protocol freeze;
2018 onward stays reserved under D012. This is a literature-informed,
project-time raw-data holdout. Full CM92 reproduction and later-era annotations
must wait until primary forecasts/evaluation are sealed, or the opened interval
must permanently become exploratory. See D013 in the decision log.

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

#### Codex D013 exposure addendum, 7 November 2026

Before any photometry request, I read the A01 memo and board messages 2930/2931,
including CM92's correlations and Price et al.'s aggregate statistics. I then
retrieved the CM92 original PDF from ADS and visually inspected printed pages
645 (Table 4, Figure 5 and symbolic long/short sequence), 647 (long-term
summaries) and 650 (moving-average/composite curves). These span the proposed
historical evaluation era and inform the design; they are not raw archive
inspection. An acquisition-methods search incidentally returned a published
radio-study summary classifying the 1996 and 2011 SS Cyg outbursts as short and
the 2007, 2010 and 2012 outbursts as long. These facts are now known; they cannot
be presented as unexpected evaluation discoveries. Source:
https://academic.oup.com/mnras/article/460/4/3720/2609136 . No 1960+ raw
photometry or target-level archive coverage was retrieved or summarized.

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

#### Claude A04 access entry, 7 November 2026

I viewed native SS Cyg photometry for JD 2435473.5–2436569.5
(1956-01-01 to 1959-01-01), as plots and row listings, and annotated it. This is
open development data under D013. No observation at or after 1959-01-01 was
retrieved, plotted or summarised. No duration–gap correlation was computed
on these data.

#### Codex A04 comparison and acquisition entry, 7 November 2026

The parent had read Claude's A04 summary and labels. The independent delegate
received only the frozen v1 protocol, the 1957 native subset and its receipt in
a fresh context; its labels were committed in `2aa9262` before comparison.
The comparison and qualifications are recorded in `8bb21cb` and the A04
independent-comparison report. No empirical duration–gap correlation was computed.

After comparison, I acquired and profiled the SS Cyg open-era stream from
1896-01-01 through native JD 2436934.0, presumed 1959-12-31 noon, in 12 retained
exports including overlapping probes. I viewed coverage summaries and native
plots around 1905 and 1925; the corresponding 1945 plot was generated locally.
All acquisitions are hashed and listed in the public manifest; raw data remain
outside Git. These are development inputs and cannot later be described as
unexamined. No 1960+ photometry or reserved-block coverage was retrieved or
summarised. Existing literature exposure remains as disclosed above.

The adapter and receipt/row-time guards are now implemented; the earlier
statements that no loader existed record the pre-acquisition state. Native
time is preserved, and the presumed convention does not bound all historical
timestamp errors. No new reserved astronomical outcome was learned during the
methodological reading of Inoue–Kilian's 2002 working paper.

#### Codex A04c injection/recovery access entry, 7 November 2026

I read Claude's adjudication, X1/X2 source and A04b design, then calibrated
separate open-era duration/gap marginals and an observer-noise scenario for
synthetic recovery. The calendar-window counts and native data access remain
within the already opened pre-1960 stream. The generator delegate did not
receive real rows, existing annotations or extractor code. The association
statistics in this tranche are calculated only on synthetic truth and its
extracted observations. No empirical real duration–gap association, reserved
photometry or reserved-block coverage was inspected or computed. The native
hashes, prepared-input hash and code receipts identify the experiment.

#### Codex A04e independent-X3-validation access entry, 7 November 2026

I read Claude's A04d findings and X3 source. I used the same already opened
pre-1960 native exports for outburst-brightness residual calibration and
X1-conditioned morphology summaries, including end-slope–duration Spearman
correlation with average ranks for ties. The new truth-generator delegate
received a bounded waveform brief and timing-generator interface, without
X3 source, Claude's training code, annotations or real rows. The parent and
other implementation reviewers were not blind to X3; source separation is
documented rather than inferred from agent names.

The independent benchmark was calibrated by morphology only. All recovery
associations and confirmation checks in A04e concern synthetic histories.
No empirical real duration–following-gap correlation, 1960+ photometry or
reserved-block coverage was inspected or computed. Qualification and
validation use separate namespaces derived from a pre-outcome source freeze;
the initial and amended morphology qualifications are both retained.

#### Codex A04g X4 benchmark access entry, 8 November 2026

I read Claude's A04f findings and X4 source, and reproduced the real observer-
diversity targets from the same twelve hashed pre-1960 acquisitions. No new
photometry was downloaded. Waveform and cadence authors did not read X4 source
or Claude's development code; limited test-name exposure after initial waveform
implementation is disclosed in the A04g protocol. Morphology-only failed
benchmarks were preserved and repaired before any fresh candidate recovery.

The calibration and qualification targets include end-slope–duration
association and observer diversity, not the focal duration–following-gap
association. All recovery associations concern synthetic histories. No real
duration–following-gap correlation, 1960+ photometry or reserved-block coverage
was inspected or computed in this tranche. A10 remains unfrozen.

Fresh qualification at `b83d76a` failed one v3 morphology gate after 384
histories. No X4 recovery was run and the validation namespace remains unused.
The failed batch is retained; no real focal association was computed to
diagnose it.

#### Codex A04i joint-benchmark/X4 access entry, 8 November 2026

I read Claude's A04h findings and retained X4 source. The same twelve hashed
pre-1960 exports supplied phase profiles, same-era morphology targets and
observer diversity; no new observations were downloaded. Applying identical
half-open era cuts gives 334 feature episodes rather than the prior 335.
No real duration–following-gap association was computed.

The new waveform author received original timing interfaces and separated
duration/gap marginals, without X4/X3, earlier waveform source, annotations,
real photometry or recovery labels. A separate source-blind cadence author
constructed anonymous phase profiles; its subsequent full-test run exposed
test names/statuses. Parent design and selection were not blind to X4.
The new waveform failed fresh qualification. V2, which Claude had studied
before writing X4, qualified with the independently constructed phase arm.
Thus fresh seeds and cadence do not establish unseen-waveform validation.

One finite morphology-only calibration was frozen at `939ea77` before fresh
qualification and candidate recovery. Independent R reproduced both pair
decisions and calibration winners. All 4,800 X4 recovery histories completed;
both global rules pass at magnitude 10 and the frozen preference selects
C1/7 d. Magnitude-9.5 failures and inconclusive diagnostics are preserved.
Every association in candidate recovery concerns synthetic histories.
No 1960+ photometry, reserved-block coverage or real focal association was
accessed. A10 remains unfrozen and no real forecast table was created.

#### Claude A10a prefix-predictor access entry, 8 November 2026

I read Codex's A04i report, public CSVs and board posts. From the same twelve
hashed pre-1960 exports (no new downloads) I computed, for 1910–1959 only:
the share of episodes whose measured core level or brightest observer-visit
median is fainter than 9.0 and 9.5; and, for 330 causal confirmations, the
prefix-versus-retrospective boundary differences, confirmation lags, interval
widths and outcome-evidence status counts (onset, coverage loss, superseded).
No real duration–following-gap association, forecast score or wait-time
distribution was computed or written. Synthetic histories used new
`a10-claude-dev-*` seeds; correlations reported there are synthetic. No 1960+
photometry or reserved coverage was accessed. A10 remains unfrozen.


### Codex A10b model/control tranche, 8 November 2026

Read Claude's A10a memo/protocol and the retained, hashed, anonymous benchmark
cache derived from pre-1960 observations. Built and inspected synthetic
chronological controls on an artificial timeline. No native archive export,
new photometry download, real duration–following-gap fit, or 1960+ raw/cadence
summary was accessed. The first aborted run and its original-stream full
replay are development evidence, not unseen validation samples. Published
aggregate knowledge already disclosed above remains known. D018 records
Barry's explicit choice to retain forecast gain as confirmatory.


#### Claude A10c control-review access entry, 8 November 2026

I read Codex's A10b memo, specification, public tables, and the retained
synthetic score rows and trial records in `outputs/a10b_controls_repaired_20261108`.
New synthetic truth catalogues used `a10c-claude-truth-*` seeds. No native
archive export, real photometry, real duration–gap association or 1960+ data
was accessed. A10 remains unfrozen.


### Codex A10d directional calibration, 8 November 2026

Used only the retained hashed anonymous pre-1960-derived benchmark cache for
360 synthetic OC histories, independent synthetic feature concordance and
matched reference replicas. No native archive export or new photometry was
opened. The finite observed-rate/joint-MC screen passes, but D021's gate-policy
clarification remains unanswered: no first real duration–following-gap fit
was made. No 1960+ observation, coverage summary or forecast was accessed.
Generation freeze: `8f5df44b950ec5781ba1e31e074e56976909a051`. All reported
associations and scores in the A10d memo are synthetic.


### Codex A10e authorization checkpoint, 8 November 2026

After A10d reporting commit `1026cff`, Barry explicitly selected the finite
360-trial observed≤5% screen, which passed (D022). This authorizes the first
1910–1959 development fit. Before opening native rows or computing that
association, the adapter, source/window guards and profile diagnostics are
being frozen under the A10e protocol. The run receipt will record source
commit, native hashes and first-fit UTC. No 1960+ access is authorized.


### Codex A10e first real association, 8 November 2026

D022 and adapter/profile source freeze `b80c4a9` were committed before native
opening at 2026-11-08 10:49:36 UTC. The run receipt marks the first real
duration–following-gap model fit at 10:50:31 UTC. All twelve acquisition
hashes match the retained cache; every native row is before 1960. Candidate
and independent reference ledgers/evidence match at both delays. All six
fits use 330 issuances (joint-mark diagnostic scores 307); parameter file
SHA-256 is `ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
The resulting positive primary offset and in-sample likelihood gain are now
known. No real Pearson correlation or held-out forecast score was computed.
No model was changed afterwards; no 1960+ observation or coverage count was
accessed. The development association cannot be made unseen again.


#### Claude A10f review access entry, 8 November 2026

I read the A10d and A10e reports, the committed A10e summary and frozen
parameters, and the 360 retained A10d trial records. I also read the
`age_at_issue` and `previous_gap` fields of the real 0 d development ledger,
which is pre-1960 and already consumed, to summarize issue ages. No native
export was opened, and no 1960+ observation, count or coverage summary was
accessed. No forecasting code or parameter changed. The proposed evaluation
protocol requires a logged decision before any 1960+ request.


### Codex A10g pre-access implementation, 8 November 2026

Read A10f, retained synthetic trial records and already-consumed development
outputs; no later archive response, coverage count or light curve was
requested or inspected. The methodological delegate used only pre-1960
artifacts for an S1 row-shape smoke. The new native adapter and full planned
rehearsal use explicitly synthetic rows. Forecast parameters remain ce4ef8d5…

Generic official AAVSO submission-format documentation was consulted for
format/time-tag context. Its illustrative SS Cyg example rows carry 1997
dates; these are documentation examples, not a queried archive response, and
were not loaded into the evaluation or used to alter its window. This
incidental documentation exposure is recorded rather than claiming universal
outcome ignorance. The published CM92/Price exposure remains as disclosed.
No1960+ raw evaluation data access or2018+ request is authorized.
