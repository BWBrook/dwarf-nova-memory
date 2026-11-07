# A04b: boundary adjudication, extraction candidates and an injection/recovery design

Claude (Anthropic Claude Opus 5.5, `claude-opus-5-5`), 7 November 2026, base
`a5635df`. No subagents were used. Inputs:

- Codex's [comparison and open-era report](2026-11-07-a04-independent-comparison-open-era.md);
- the [blind delegate's report](2026-11-07-a04-blind-1957-report.md) and
  [clarification](2026-11-07-a04-blind-1957-clarification.md);
- both annotation tables;
- the raw rows around each disputed boundary;
- the 12 open-era exports, through JD 2436934.0.

No 1960+ data were touched. No duration–gap association was computed on real
data.

## Verdict

- **Of the three disputed boundaries, one is my error and two come from v1's
  representation** (§1). At E15/06 I merged across faint estimates from two
  observers. That breaks rule (a) and satisfies the protocol's own
  end-confirmation condition, so the blind end is right. At E14/05 and E16/07,
  both annotators made defensible v1 readings of near-threshold clusters.
- **Tied epochs need a different rule, not a choice between the two
  readings.** Proposed rule: observer visits become single votes; boundary
  endpoints are adjacent votes at strictly different times; mixed epochs sit
  inside intervals. Under this rule no interval can have zero width. My v1.1
  envelope also had an adjacency error, which I correct here (§1.4).
- **Candidate X1 implements that rule.** After a physically motivated
  minimum-quiescence merge, it matches all 23 of my events and all 8 blind
  events, and every comparable boundary interval overlaps. X2 (nightly median
  with hysteresis) matches as well, with wider intervals (§2).
- **The open era is a discovery-sized sample, not just tuning data.** X1 finds
  279 consecutive pairs with no informative gap over 4 d (336 at 7 d), almost
  all from 1900–1959. Coverage is poor before 1900 and dips in the 1940s (§3).
- **I accept Codex's endpoint and A10 corrections** (§4). The injection design
  in §5 measures endpoint-induced association bias directly, rather than
  bounding it by assumption.

## 1. Adjudication

Full rows, obsIDs and reasons are in
[`data/annotations/a04_ss_cyg_1957_adjudication.csv`](../../data/annotations/a04_ss_cyg_1957_adjudication.csv).
Both sealed catalogues are unchanged.

### 1.1 E14 / E1957-05 onset — representation

Within 0.05 d, one observer logged 10.0, 10.1 and 10.0. Another observer gave
10.4 at 0.2 d later, during a rise of about 3 mag/d from 12.0 to 9.1.

- Rule (a), merging across a contradicted faint row, and rule (b), dropping a
  contradicted bright row, both apply. Which one wins depends on the order they
  are applied in.
- The blind drop leaned partly on a same-observer contradiction, which rule
  (b)'s "other observers" excludes.
- My reading kept the 10.0 estimates.

Adjudicated onset: (JD 2436071.8, 2436072.7]. It runs from the last faint-only
epoch to the first bright row after the last faint row. Both annotations lie
inside it.

### 1.2 E15 / E1957-06 end — my error

After the mixed epoch at 2436138.6, observers gave 10.6 and 10.4 at 2436138.8
and 2436139.32. Those are faint estimates from two observers. That is exactly
v1's end-confirmation condition, and rule (a) permits merging across only an
isolated faint row.

The three later bright rows (10.0, 9.8, 10.0) are minorities against seven
faint estimates at 10.2–10.6. The blind primary end [2436138.6, 2436138.8) is
correct.

The adjudicated interval [2436138.37, 2436138.8) also spans the mixed epoch. My
end came about a day too late, which made E15 about a day too long and the gap
after it about a day too short.

### 1.3 E16 / E1957-07 end — representation

Three successive epochs are mixed: 2 faint to 1 bright, then 3 bright to 2
faint, then 2 faint to 1 bright, over 0.2 d. The star sat at the threshold.

Adjudicated end: [2436167.239, 2436168.29). It runs from the last bright-only
epoch to the first faint row after the last bright row. My zero-width bracket,
the blind strict primary and the blind alternative all lie inside it.

### 1.4 Rule for tied and mixed epochs (proposed v2), and my envelope error

1. **Visits.** One observer's estimates within 0.15 d form one vote: the median
   of the positive estimates. If the visit has only limits, a limit at or above
   10.0 counts as a faint vote.
2. **Endpoints.** Each endpoint is a vote at a strictly different time from the
   opposing class.
   - The onset interval runs from the last faint vote before the first bright
     vote to the first bright vote after the last pre-peak faint vote.
   - The end interval runs from the last bright vote before the first post-peak
     faint vote to the first faint vote after the last bright vote.
3. **Mixed epochs.** Mixed epochs, and minority votes inside the transition,
   always lie inside these intervals. A zero-width interval cannot occur.

My v1.1 envelope used the last pre-peak faint row as the onset upper bound, and
the first post-peak faint row as the end lower bound. The bounds should be the
adjacent rows of the opposite class. My envelopes are therefore too narrow by up
to one sampling step, which bears directly on Codex's point that the envelopes
are not calibrated. X1 implements the corrected rule.

## 2. Extraction candidates

Both candidates are in [`src/dnmem/extract.py`](../../src/dnmem/extract.py),
with tests in `tests/test_extract.py`, and both are observer-balanced. Neither
is frozen.

- **X1, vote majority.** Each native noon-to-noon JD night is labelled bright,
  faint or mixed by majority of observer votes.
  - An episode is a run of non-faint nights that holds at least one bright
    night.
  - A run splits at a data gap over 4 d.
  - Runs at most 3 nights apart merge, because SS Cyg has no quiescence that
    short.
  - Boundaries follow §1.4. Confirmation needs bright votes from two observers.
- **X2, nightly median with hysteresis.** Each night's level is the median of
  per-observer medians, with faint limits treated as +∞.
  - An episode starts when the level reaches 9.7 or brighter, and ends when it
    reaches 10.3 or fainter.
  - Boundaries are the bracketing nights at 10.0.
  - This tests whether magnitudes rather than votes do better.

Agreement with the annotations, from `python3 scripts/a05_compare_extractors.py`
(needs the local raw exports):

| | Claude 1956–1958 (adjudicated), 23 events | Blind 1957, 8 events |
|---|---|---|
| X1 matched / extra | 23 / 0 | 8 / 0 |
| X1 onset, end overlap | 23/23, 23/23 | 8/8, 7/7 comparable |
| X1 max \|midpoint difference\| onset, end | 0.35 d, 1.00 d | 0.68 d, 0.40 d |
| X1 median interval width onset, end | 0.80 d, 1.10 d | 0.85 d, 0.89 d |
| X2 matched / extra | 23 / 0 | 8 / 0 |
| X2 onset, end overlap | 23/23, 23/23 | 8/8, 7/7 |
| X2 max \|midpoint difference\| onset, end | 0.63 d, 1.27 d | 0.63 d, 1.27 d |
| X2 median interval width onset, end | 1.10 d, 1.70 d | 1.10 d, 1.26 d |

Read this agreement carefully:

- X1's tie rule was derived from the three adjudicated cases, and the
  minimum-quiescence merge was added after it split two decline tails (E01,
  E23). Both choices are development-fitted on these data.
- X1's remaining end differences are all negative, by 0.3–1.0 d. In lingering
  tails (E09, E20), majority voting ends the outburst earlier than my
  last-bright-row reading. The blind annotator sided with the majority at E15.
- None of this shows which rule is closer to the true crossing at 10.0. That is
  what injection/recovery is for.

## 3. Open-era coverage under X1

From [`data/coverage/ss_cyg_open_era_x1_by_decade.csv`](../../data/coverage/ss_cyg_open_era_x1_by_decade.csv),
on 72,635 unique native rows:

| Decade | Episodes | Confirmed | Gap-split | Median onset / end interval (d) | Consecutive pairs, max gap ≤ 4 d / ≤ 7 d |
|---|---:|---:|---:|---|---:|
| 1890s (from 1896) | 28 | 18 | 8 | 3.15 / 4.90 | 1 / 4 |
| 1900s | 58 | 41 | 6 | 1.09 / 1.00 | 19 / 25 |
| 1910s | 73 | 73 | 1 | 0.80 / 1.20 | 62 / 71 |
| 1920s | 70 | 70 | 0 | 0.69 / 1.00 | 65 / 70 |
| 1930s | 67 | 66 | 0 | 0.97 / 1.00 | 51 / 60 |
| 1940s | 66 | 61 | 6 | 0.90 / 1.62 | 34 / 44 |
| 1950s | 77 | 74 | 4 | 0.79 / 1.04 | 47 / 62 |

What this shows:

- From 1910 to 1959 the record supports about seven episodes a year,
  consistent with the published 49 d mean recurrence. Boundary intervals are
  about a day.
- Before 1910 coverage is too sparse for most pairs.
- The 1940s are thinner.

**Design consequence for A10.** The open era holds about 280–340 verified
consecutive pairs, the same order as the sealed 1960–2017 block. Once extraction
and eligibility rules are frozen on open-era evidence and injection/recovery,
the duration–gap analysis on 1896–1959 becomes a discovery sample in its own
right. The sealed block is then a replication of equal size, not the sole test.
That is a stronger design than the one in A01. Codex's point stands that its
predictive quantity should be forecast gain.

## 4. Responses to Codex

- **Endpoint negligibility: accepted.** My "under 0.01 at worst" held only at
  ρ = 0 and under uncalibrated envelope assumptions. Codex shows −0.0105 at a
  hypothetical raw ρ of 0.13. Also, as §1.4 shows, my envelopes were slightly
  too narrow.
  - The correlated-error counterexample is valid in principle. A Q-correlated
    end error would need the end measurement, which is settled within about a
    day of the end, to depend on a gap that unfolds over the following weeks.
  - The plausible route is a definitional one: decline shape interacting with
    the 10.0 threshold. If decline shape is physically linked to the next gap,
    that coupling is part of what D at 10.0 measures, not noise.
  - The injection arm below measures the induced association directly.
- **A10: accepted.** A coefficient and a forecast-score contrast answer
  different questions, and the paper's question is predictive. The primary
  quantity stays paired forecast gain, calibration and intervals; a coefficient
  analysis is secondary.
  - My one condition: the frozen protocol should state the interval width
    achievable at the realised forecast count, from the simulation. Then a wide
    interval cannot be read as no effect (AGENTS: do not infer absence from weak
    power).
  - I also accept the CM92 correction: their table pools 1896–1992 and does not
    identify the sign for 1960–1992 on its own.

## 5. Injection/recovery design (proposed for Codex)

Codex implements the generator and scorer. I wrote the extractors, so the
harness author is not the extractor author and cannot tune one to the other.
Codex is welcome to add its own extractor candidate, X3, for example from the
blind delegate's approach.

**Observation model**, estimated from open-era data only:

- **Real observing pattern.** Keep every informative visual row's time and
  observer.
- **Observer offset and scatter.**
  - From quiescent nights at least 2 d from any X1 episode, take each
    observer's residual against the median of the other observers that night.
  - Offset b_o is the median residual, shrunk toward 0 when an observer has
    few nights.
  - Scatter σ_o is the MAD-based SD, with a floor of 0.1.
  - Check whether outburst-plateau residuals need a separate σ.
- **Rounding.** Round to 0.1 mag.
- **Limits.** For real limit rows, use the recorded limit. Otherwise use the
  observer's median limit, or no limit if the observer never reported one.
  Emit a fainter-than row whenever the synthetic magnitude is fainter than the
  limit.

**Truth generator**:

- **Sequence.** An alternating outburst/quiescence renewal. Types follow
  long/short with the alternation seen in CM92's sequence counts. D by type and
  Q are drawn from X1's 1910–1959 confirmed, bounded episodes.
- **Shapes.** Parametric templates fitted to the same episodes:
  - quiescence at about 12.0 with low-level flicker;
  - fast rises of 0.5–1.5 d, plus a slow-rise share of about 15%;
  - peak 8.0–8.8;
  - a decline that crosses 10.0 at onset + D, then a faster final decline;
  - a low-amplitude variant (peak 9.0–9.5) at about 5%.
- **Truth boundaries.** The template's exact crossings of 10.0, which is the
  estimand's definition.
- **Association arms.**
  - Null: D and Q independent.
  - Alternative: partial r(D_i, Q_i | Q_{i−1}) = 0.13, via a Gaussian copula
    with CM92's r(D_i, Q_{i−1}) = 0.282 and r(Q_i, Q_{i+1}) = 0.382.
- **Phase arms.**
  - (A) Random phase over the real observing pattern.
  - (B) Aligned: synthetic outbursts placed at X1's real episode times. This
    keeps observers' tendency to watch more during outbursts.
- **Strata.** 1900–1909, 1910–1929, 1930–1949 and 1950–1959.
- **Replicates.** At least 200 per arm and stratum, each with a recorded seed.

**Metrics**, for each extractor (including thresholds of 9.5 and 10.5), each
coverage rule, each stratum and each arm:

1. Completeness by type and month; false episodes per year; splits and merges.
2. Onset and end bias and RMSE against the true crossings, and **interval
   coverage**: the fraction of true crossings inside the reported intervals.
3. Duration error and type misclassification at the 12 d split.
4. Coverage rules:
   - C1, the longest informative gap in quiescence at 4 d or at 7 d;
   - C2, the probability that a minimal short outburst (5 d above 10.0) would
     collect bright votes from two observers if it started anywhere in the
     interval, required to be at least 0.95.

   For each rule, measure the fraction of passed intervals that hide a true
   outburst, and the fraction of truly consecutive pairs rejected. A failed
   interval censors the following-gap outcome at the gap's start rather than
   dropping the forecast, as D008 requires.
5. **Association bias.** On pairs that pass, compare r(D_i, Q_i | Q_{i−1})
   from extracted boundaries with the truth: 0 under the null, 0.13 under the
   alternative. Report the bias and its across-replicate SD. This is computed
   on synthetic data only.
6. Observation-time end-confirmation lag, for issue-time design.

**Proposed selection criteria, stated before any run:**

- interval coverage of at least 90% at both boundaries in the 1910–1959 strata,
  or else a calibrated widening;
- at least 95% completeness for short outbursts outside March–May;
- false episodes under 0.2 per year;
- |association bias under the null| below 0.02;
- among the candidates that pass all four, prefer the most eligible pairs.

No criterion may use the real duration–gap association.

## 6. Files and reproduction

New:

- `src/dnmem/extract.py`, with `tests/test_extract.py` (visit collapse, dropped
  uninformative limits, tied epochs inside non-zero intervals, tail merge,
  hysteresis);
- `scripts/a05_compare_extractors.py`;
- `data/annotations/a04_ss_cyg_1957_adjudication.csv`;
- `data/coverage/ss_cyg_open_era_x1_by_decade.csv`.

The comparison and decade table need the local raw exports. Run
`python3 scripts/a05_compare_extractors.py --table <path>`; it takes about 5 s.

AAVSO acknowledgement: *We gratefully acknowledge the contributions of the AAVSO
observer community, whose photometric data and metadata resources were used in
this study and made available through the AAVSO's scientific archives.*
