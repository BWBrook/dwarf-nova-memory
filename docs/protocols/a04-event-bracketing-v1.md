# A04 event-bracketing protocol, version 1

Claude (Opus 5.5), 7 November 2026. **Written and committed before Claude
plotted, tabulated or viewed any SS Cyg magnitudes from the A03 export.** Inputs
seen while writing: the A03 report, the native column names, and a metadata
profile with no time series (flag and comment-code counts, JD decimal
precision, observer count). Codex's A03 figures were not opened.

## Purpose and limits

The protocol brackets outburst onsets and ends in SS Cyg's open development
era (D013). It has three uses:

1. measure how precisely visual data fix boundaries, and how far two annotators
   disagree;
2. give a reference against which a frozen extraction algorithm can later be
   checked;
3. show whether early visual coverage supports issue-time forecasting.

It is not a frozen extraction rule, a forecast data set or an evaluation.
Nothing here touches observations at or after 1960-01-01 UTC.

## Data

- Input: `data/raw/aavso_ss_cyg_1956_1959_20261107/native.xml`, SHA-256
  `1840efeaa141ffd62899b54f6c078e823dede90437d7f44f5b7904f40c8ad87f`, read
  through `dnmem.aavso.read_native_payload`. Native rows only.
- Time: native JD, unconverted. AAVSO's visual format asks observers to convert
  UT to JD, with HJD as a separate labelled option; this export has no HJD
  column, and three quarters of its JDs carry one decimal. The heliocentric
  correction (at most 0.0058 d) and the UT–TT offset (about 0.0004 d in 1957)
  are below that reporting precision. See the A04 memo for the review.
- Interval: every event with a boundary inside JD 2435473.5–2436569.5. Runs
  touching the export's ends are censored there, never completed from outside.
- **Blind subset for the second annotator, fixed now:** JD 2435839.5–2436204.5
  (calendar 1957).

## Row classes

With threshold m\* = 10.0:

| Class | Rule |
|---|---|
| B (bright) | positive estimate (`fainterThan=0`) with mag ≤ 10.0 |
| F (faint) | positive estimate with mag > 10.0, or a fainter-than limit whose value is ≥ 10.0 |
| N (uninformative) | fainter-than limit with value < 10.0: it cannot say which side of m\* the star was |

- A fainter-than limit of value v means the star was fainter than v. Treating a
  limit below m\* as faint evidence would be a reversed-limit error.
- Rows flagged `T` (provider discrepant) are excluded from primary decisions.
  For each boundary the annotator records whether including them would change
  the bracket.
- Comment codes are kept but never used to exclude. Codes N, Q and X do not
  appear in AAVSO's current visual list; any decision resting on such a row is
  noted.
- Observer identity is the observer-name field, case-folded, so one person
  reporting through two organizations counts once; the observer code is the
  fallback. Identities are used locally and never written to committed files.

**Why 10.0.** Cannizzo & Mattei (1992) defined SS Cyg outbursts by m_v = 10
crossings of daily means over 1896–1992. The same level keeps a later
comparison possible. SS Cyg's quiescent and peak visual levels (about 12 and
8.5) sit well clear of it, so estimate scatter of a few tenths of a magnitude
should rarely flip a row's class away from transitions.

## Definitions

- **Candidate outburst:** a maximal time-ordered run of B rows with no F row
  between them. N and T rows do not break a run. Rows are ordered by JD, then
  native observation ID.
- **Confirmed outburst:** the run holds B estimates from at least two
  observers. Single-observer runs are recorded as `unconfirmed`.
- **Onset bracket** (onset_earliest, onset_latest]: onset_latest is the first B
  row's JD, onset_earliest the last F row's JD before it.
- **End bracket** [end_earliest, end_latest): end_earliest is the last B row's
  JD, end_latest the first F row's JD after it.
- **Bounds, not draws.** Duration D lies in
  [end_earliest − onset_latest, end_latest − onset_earliest]. The following
  quiescent gap Q lies in
  [next onset_earliest − end_latest, next onset_latest − end_earliest].
  The shared end bracket couples D and Q; later inference must draw boundaries
  jointly (data dictionary §3).
- **Coverage gaps:** every interval longer than 4.0 d between consecutive
  informative (B or F) V-flag rows. A short outburst could hide inside such a
  gap. Where one falls in the quiescence between events i and i+1, their
  consecutiveness is `unverified`.
- **Observation-time confirmation** (what an analyst holding every observation
  at the moment it was made would know; real availability lagged, by post):
  - `onset_detected`: JD of the first B row from a second observer;
  - `end_confirmed`: JD of the earliest F row after the run at which F rows from
    two observers have accumulated with no intervening B row.
- **Peak:** the brightest single B estimate and its JD. It is coarse.
- **Type:** CM92's 12 d split. `long` if the minimum duration is at least 12 d,
  `short` if the maximum duration is under 12 d, otherwise `ambiguous`. A slow
  rise (more than about 3 d from the last F row to near-peak, by judgement) is
  noted qualitatively.
- **Event class:** `normal`, `ambiguous`, `unconfirmed` or
  `standstill-like`.

## Annotator judgement

`scripts/a04_bracket_candidates.py` applies the rules mechanically and writes
candidates, row listings around each boundary and review figures locally. The
annotator then reviews every candidate and coverage gap. The annotator may:

- (a) merge runs split by an isolated F estimate that other observers within
  ±0.5 d contradict;
- (b) drop a run resting on an isolated B estimate that other observers
  contradict;
- (c) mark any boundary ambiguous.

Each override is written in the notes with the native observation IDs involved.
The mechanical candidates are kept beside the annotation, so every override
can be audited.

## Output

The annotation goes to `data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv`,
one row per event. Its columns follow data dictionary §3:

- identity, definition version and annotator;
- onset and end brackets, with JDs and native observation IDs;
- censoring flags;
- observation-time detection and confirmation;
- duration and following-gap bounds, and whether the next event is
  consecutive;
- peak, type, class and counts;
- the effect of T rows, any override, and notes.

Observer names and magnitudes beyond the single peak value are not committed.

## Independence for the second annotator

Codex, or a delegate it briefs, annotates the 1957 subset using only the raw
export and this file. It must not open the Claude annotation CSV, the A04
results memo, or Claude's candidate tool and its outputs. That keeps code errors
and judgements from being shared. Following these definitions is recommended,
so that disagreement isolates judgement from definition. Objections to the
protocol belong in a separate note. The comparison then reports event matches
(overlapping onset brackets), bracket overlap and midpoint differences for each
boundary, and disagreements in type and consecutiveness.
