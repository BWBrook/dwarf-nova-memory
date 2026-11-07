# A04: D013 review, native metadata check and first SS Cyg annotation

Claude (Anthropic Claude Opus 5.5, `claude-opus-5-5`), 7 November 2026, base
`04a8b69`. No subagents were used. Inputs: Codex's [D013 review](2026-11-07-a01-review-d013.md),
the [A03 receipt](2026-11-07-a03-ss-cyg-acquisition.md), AAVSO's documentation
(cited below) and the A03 native export for 1956-01-01 to 1959-01-01. No
observation at or after 1959-01-01 was retrieved or viewed. I did not open
Codex's A03 figures.

## Verdict

- **D013 as amended is accepted.** Codex's power correction is right, and the
  sequencing conflict it found in my A01 plan was real. One consequence needs
  deciding before A10. On a block of a few hundred forecasts, a pre-registered
  in-sample test of the duration term has roughly twice the power of a paired
  log-score test (§1.2).
- **Native timing is settled to the precision that matters.** The JD convention
  can shift a visual row by at most 0.006 d, against a reporting precision of
  0.1 d (§2.1). The discrepant (`T`) flag is documented and concentrated in a
  few observers. Three legacy comment codes (N, Q, X) are undocumented, and one
  observer accounts for all 463 N rows (§2.2).
- **First annotation: 23 outbursts in 1956–1958.** Boundaries are fixed to
  about a day (median onset envelope 0.76 d, end envelope 1.05 d). That precision
  shifts a duration–gap correlation by only about 0.003, or under 0.01 at worst.
  The precision threats are missed events in seasonal gaps and a single
  threshold that fragments outbursts, not endpoint error (§3).

## 1. D013 and the power correction

### 1.1 What I checked

I re-derived Codex's paired-score example. With X and E independent standard
normals, v = 1 − r², Y = rX + √v E, the score difference between N(rX, v) and
N(0, 1) is d = g + (Y² − E²)/2. Expanding Y² − E² = r²X² + 2r√v XE − r²E², all
cross-covariances vanish. Its variance is 2r⁴ + 4r²v + 2r⁴ = 4r², so Var(d) = r²
as stated. I reproduced the regression and score columns in base R; the
`Rscript` line is in §6.

My A01 sentence "about 470 forecasts for an expected likelihood ratio of 8"
described an expectation, not a power calculation. I accept the correction.

I also accept the sequencing fix. My A01 analysis table placed the full
1896–1992 CM92 reproduction and 2010–2017 double annotation before forecasting.
That would have consumed the 1960–2017 block D013 was meant to protect.

A descriptive CM92 check is still possible on the open era alone: 1896–1959,
with their m_v = 10 definitions. It can test signs and the long–short
alternation, but not match their pooled values, which include 1960–1992.

### 1.2 Design consequence for A10: which test the sealed block carries

Under the same iid Gaussian idealisation and the CM92-derived partial
r = 0.130, one-sided α = 0.05, base R gives:

| n forecasts | Frozen-specification regression test (in-sample on the block) | Known-parameter paired log-score test |
|---:|---:|---:|
| 200 | 0.58 | 0.24 |
| 400 | 0.83 | 0.37 |
| 430 | 0.86 | 0.39 |
| 1000 | 0.99 | 0.67 |

Under these assumptions, 80% power needs about 364 forecasts for the regression
test and about 1,438 for the score test. This is the general result of Inoue &
Kilian (Econometric Reviews 23, 371; working paper abstract read), who trace
the frequent disagreement between in-sample and out-of-sample predictability
tests to the lower power of out-of-sample tests.

The figures are a planning illustration, not our pipeline's power, which
Codex's caveats govern. An 80%-power score test would need about 1,438
forecasts. SS Cyg's mean recurrence is about 49 d, which allows about 430
outbursts in 1960–2017, so even the whole block falls well short.

**Proposal for A10, not a decision.**

- Freeze the full specification on the open era, as D013 requires.
- On the sealed block, make the pre-registered confirmatory quantity the
  duration term's coefficient (or likelihood ratio), estimated with that
  specification fixed.
- Report the out-of-sample paired score difference as the forecast-skill
  estimate, with its interval, rather than as a significance gate.

Freezing the specification before access is what protects the holdout. That
protection survives estimating one pre-declared coefficient on the block.

**A second qualification.** CM92's Table 4 already pools 1896–1992. So the sign
of the partial association is published for 1960–1992, and a confirmatory sign
test is fresh only on 1993–2017. Incremental forecast skill is fresh for every
era, because nobody has scored it. The final protocol should state which
quantity is confirmatory on which years.

Barry should see this choice at A10. It changes what the paper can claim.

### 1.3 Other D013 points

These are all accepted as Codex wrote them:

- the literature-informed label;
- the full endpoint-error formula (`Corr(D+δ, Q−δ)` with the denominator
  inflated);
- the point that double annotation cannot identify shared bias;
- excluding the focal mark from any recent-type M2 summary;
- the narrower novelty wording.

A04 now quantifies the endpoint question directly from bracket widths, so it
does not rely on annotator agreement (§3.3).

## 2. Native timing and flag metadata

### 2.1 Time

- AAVSO's visual file format tells observers to "convert all times from UT" to
  JD, with HJD as a separate, labelled option
  ([visual format](https://www.aavso.org/aavso-visual-file-format), read via the
  `mintaka.aavso.org` mirror).
- The [data-file description](https://www.aavso.org/format-data-file) lists JD
  and HJD as separate fields.
- An AAVSO staff reply ([forum](https://www.aavso.org/index.php/node/79206))
  confirms the following for HJD submissions: WebObs keeps the submitted HJD and
  also stores a converted JD.
- The VSX API export carries only `JD`.

For visual data, the native column is therefore UT-based geocentric JD, by
AAVSO's documented convention. The 1956–1958 rows were digitised from paper
reports, so their individual handling is unverified.

The size of any error is bounded:

- 2561 of 3438 JDs carry one decimal, 658 carry two and 219 carry three;
- a heliocentric correction would be at most 0.0058 d;
- UT versus TT is about 0.0004 d (ΔT ≈ 32 s in 1957);
- UTC did not yet exist, and its difference from UT is negligible.

**Recommendation.** For visual rows, record `time_scale = UT (presumed,
AAVSO visual convention)` and `time_reference = geocentric (presumed)`, with a
0.006 d bound. Add a 0.01 d guard band at any access cutoff. Later CCD rows can
arrive as HJD and need the HJD field; the VSX `api.object` export does not
supply it.

### 2.2 Flags, codes and observers

- **`T` (discrepant).** This means "flagged discrepant and should be used with
  extreme caution" ([data-file description](https://www.aavso.org/format-data-file)).
  AAVSO staff add that only examined values are flagged; the rest are left to
  the researcher ([forum](https://www.aavso.org/node/83369)).
  - The 62 T rows come from 19 observers, 36 of them from one observer.
  - In the light curve they are mostly bright estimates during quiescence, plus
    a few faint estimates inside outbursts.
  - Excluding them changed no bracket. Including them would only create
    one-row spurious runs in quiescence: 10 such rows across five quiescent
    intervals.
- **Comment codes.** AAVSO's current visual list covers B, U, W, L, D, Y, K, S,
  Z, I and V. N (463 rows), Q (15) and X (11) are not on it.
  - All 463 N rows belong to one observer, who logs several estimates within
    about an hour: 90 groups, median spread 0.2 mag, maximum 0.9.
  - K (48 rows, one observer) means a non-AAVSO chart.
  - The protocol counts observers, not rows, so the repeat estimates do not
    inflate confirmation. Any daily-mean or rate statistic must first collapse
    repeated estimates by the same observer within a night.
- **BAA rows.** Eighteen rows come from one BAA-VSS observer, none duplicating
  an AAVSO row within 0.05 d.
- **No uncertainties** are reported, and magnitudes are quantised at 0.1.

## 3. Independent annotation of 1956–1958

### 3.1 Procedure and independence

I wrote [protocol v1](../protocols/a04-event-bracketing-v1.md) and pushed it as
`1bfbca5` before plotting or tabulating any magnitudes. It defines:

- outbursts as runs of estimates at or brighter than m\* = 10.0, CM92's level;
- fainter-than limits by direction;
- `T` rows as excluded;
- confirmation as needing two observers;
- coverage gaps as anything over 4 d.

It also fixes the 1957 blind subset for Codex in advance.

The mechanical pass (`scripts/a04_bracket_candidates.py`) produced 58 candidate
runs. I reviewed each one on light-curve panels and row listings. I merged 33
fragments into events under rule (a) and overruled two isolated bright
estimates under rule (b): obsIDs 50673917 and 50676069, each contradicted by
three or four observers at the same JD.

Those decisions are in
[`data/annotations/a04_ss_cyg_1956_1958_claude_v1_decisions.csv`](../../data/annotations/a04_ss_cyg_1956_1958_claude_v1_decisions.csv).
`scripts/a04_build_annotation.py` computes the
[annotation](../../data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv) from
them and the raw export.

### 3.2 Changes after viewing (v1.1)

These were made after seeing the data and are labelled as such:

1. **Envelope intervals.** In dense data the v1 bracket measures only sampling:
   E07's end bracket is 0.02 d wide while estimates straddle 10.0 for 1.9 d.
   - The onset envelope runs from the last faint row before the first bright
     row to the last faint row before the peak.
   - The end envelope runs from the first faint row after the peak to the first
     faint row after the last bright row.
   - These are the uncertainty to use. The v1 brackets are kept as well.
2. **Missed-event rule.** An inter-event gap is marked `possible` when it is at
   least as long as the shortest faint-to-faint span of any confirmed outburst
   in the sample, which is 7.0 d (E12).
3. **Tied JDs.** At 0.1 d precision, a bright and a faint row can share a JD.
   E16's v1 end bracket has zero width for this reason; its envelope does not.

### 3.3 Results

`python3 scripts/a04_summarize_annotation.py data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv`
reproduces these from the committed table alone.

| Quantity | Value |
|---|---|
| Events | 23: 21 normal, 2 unconfirmed (single observer) |
| CM92 type (v1 bounds) | 9 long, 11 short, 3 ambiguous |
| Mechanical fragments merged | 33, from 12 events with bright and faint estimates interleaved at transitions |
| Onset envelope width, 20 clean events | median 0.76 d, max 3.20 d |
| End envelope width | median 1.05 d, max 3.10 d |
| End-time SD (uniform within envelope) | 0.38 d (onset 0.34 d) |
| SD of duration and following gap (midpoints) | 3.79 d and 13.37 d (16 gap pairs) |
| Shared end-error shift in Corr(D, Q) at r₀ = 0 | −0.003 (worst case, error at envelope ends: −0.008; if SD were 1 d: −0.019) |
| Median lag from first bright row to second-observer detection | 0.20 d (max 1.73) |
| Median lag from first faint row to end confirmation | 0.36 d (max 2.58) |
| Inter-event intervals with a gap over 4 d | 10 of 22 |
| Intervals that could hide a short outburst | 4 of 22: E02–E03 and E03–E04 (March–May 1956), E11–E12 (March 1957), E18–E19 (March–May 1958) |

What this shows:

- **Endpoint error is not the threat at this density.** Even the worst-case
  shift is under a tenth of the 0.13 effect. The 0.03 sensitivity candidate is
  comfortably met in well-covered seasons. Whether that holds in sparse decades
  is open.
- **Missed events and seasonal gaps are the threat.** The two unconfirmed
  events (March and April 1956) and all four intervals that could hide an
  outburst fall in March–May. SS Cyg passes the Sun's right ascension in
  mid-February and is poorly placed for evening observers through spring.
  E18's onset lies inside a 20.9 d gap. Forecast eligibility
  will need an explicit coverage rule, and that rule must be frozen on the open
  era.
- **A single threshold applied to single estimates fragments outbursts.** In
  more than half the events, visual scatter of 0.2–0.3 mag, in 0.1 mag steps,
  is as large as the day-to-day change on the final decline near 10.0. Frozen
  extraction candidates should include:
  - collapsing each observer's estimates to one per night before taking a
    multi-observer nightly median;
  - a hysteresis band;
  - envelope-based boundary intervals.
- **Morphology.** Three outbursts are noteworthy:
  - E08 has a slow rise, brightening from about 11.7 to 10.0 over roughly 6 d;
  - E15 also rises slowly, over about 2 d;
  - E23 is low amplitude, peaking near 9.0 with a plateau around 9.1–9.9, so
    its boundaries depend on the threshold.

  CM92's 12 d split separates the rest, but long outbursts reach down to it:
  E01 lasts 12.0–15.0 d by v1 (11.1 d minimum by envelope), and E10 lasts
  12.7–14.3 d. That supports M1b (type plus
  within-type duration) as a candidate. It does not select it.

I deliberately computed **no duration–gap correlation**. The focal estimand
stays unexamined while extraction and eligibility rules are being fixed. With
16 pairs it would be noise in any case.

## 4. Blind subset for Codex

Annotate JD 2435839.5–2436204.5 (calendar 1957) from the raw export and
[protocol v1](../protocols/a04-event-bracketing-v1.md), plus the §3.2 changes
if wanted. That covers E10–E17 in my numbering, which the annotator should not
know in advance. Write your own tooling.

**Do not open:**

- `data/annotations/`;
- this memo beyond this section;
- `scripts/a04_*`;
- the board posts about A04.

The board relays closing messages between agents, so Codex's own session will
already have seen my summary. **The blind labels must therefore come from a
context-isolated delegate.** Give it only:

- the raw export path;
- the protocol file;
- the adapter `src/dnmem/aavso.py`.

Record exactly what it was given. Commit its labels first, then compare:

- event matches;
- bracket overlap;
- envelope midpoint differences;
- type and consecutiveness disagreements.

## 5. Next steps

1. **Codex:** the blind 1957 annotation (§4), then the comparison.
2. **Codex, A03 continuation:** acquire the rest of the open era (1896–1955,
   plus 1959 through JD 2436934.0) in bounded requests. Start with small
   windows around 1905, 1925 and 1945 to check coverage before the bulk pull.
   Early decades are likely sparser, which bears on whether the open era can
   support development (D013's stated contingency).
3. **A06:** implement two or three frozen-candidate extraction rules (§3.3) and
   score them against both annotations. Include a nightly-collapse step for
   repeat estimates.
4. **A10:** the confirmatory-quantity question (§1.2), for Barry.

## 6. Files, reproduction and acknowledgement

New:

- `docs/protocols/a04-event-bracketing-v1.md` (pushed before viewing, `1bfbca5`);
- `src/dnmem/brackets.py`;
- `scripts/a04_bracket_candidates.py`, `scripts/a04_build_annotation.py`,
  `scripts/a04_summarize_annotation.py`;
- `data/annotations/` (decisions, annotation, README);
- `tests/test_brackets.py` (limit direction, run bracketing and confirmation);
- `tests/test_a04_annotation.py` (bracket order within and between events).

Review figures stay local and gitignored, under
`outputs/a04_ss_cyg_1956_1958_candidates/`.

```bash
python3 scripts/a04_build_annotation.py data/raw/aavso_ss_cyg_1956_1959_20261107/native.xml \
  data/annotations/a04_ss_cyg_1956_1958_claude_v1_decisions.csv --annotator "Claude Opus 5.5" \
  --output /tmp/a04_check.csv && cmp /tmp/a04_check.csv data/annotations/a04_ss_cyg_1956_1958_claude_v1.csv
Rscript -e 'a<-0.223;b<-0.282;c<-0.382;r<-(a-b*c)/sqrt((1-b^2)*(1-c^2));g<- -0.5*log(1-r^2);for(n in c(200,400,430,1000)){df<-n-3;ncp<-r*sqrt(df/(1-r^2));cat(n,1-pt(qt(0.95,df),df,ncp),pnorm(g*sqrt(n)/abs(r)-qnorm(0.95)),"\n")}'
```

AAVSO acknowledgement, per the July 2026 guidelines: *We gratefully acknowledge
the contributions of the AAVSO observer community, whose photometric data and
metadata resources were used in this study and made available through the
AAVSO's scientific archives.*
