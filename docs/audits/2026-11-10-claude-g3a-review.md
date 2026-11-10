# Claude review of G3a: why the transfer failed, and what the paper should do

Claude (Opus 5.5), 10 November 2026. Reviewed Codex's
[G3a results](2026-11-10-g3a-feasibility-results.md), the
[execution audit](2026-11-10-g3a-execution-review.md), the
[sequence review](2026-11-10-g3a-sequence-review.md), protocol v1, D045 and the committed aggregates.

Script: `scripts/g3a_claude_review_checks.py`. Aggregates: `data/provenance/g3a_claude_review/checks.json`.

- Gain-free and development-only. The script reloads the retained pre-1990 native pages through the
  independent checker's audited loader, reruns the frozen DF chain, and records how many forecasts
  each requirement removes.
- For reference it runs the same chain on the already-open SS Cyg record, with the same 1990
  cutoff, threshold 10.0 and margin 1.0.
- No mark was related to any gap. No model was fitted, no forecast scored, no request made. No
  1990+ new-star or 2018+ SS Cyg information was read.

## Verdicts

| Claim | My check | Status |
|---|---|---|
| C68: no qualified cohort | Reran the frozen chain from the audited pages. All eight ordinary stars' supported counts match exactly; the holds' ordinary-route totals are consistent with their derived-stream results (U Gem 31 against 27). The empty set holds under every relaxation tried below | supported |
| C69: six-star supplement | Hash-checked recount of all 16,000 trial lines: every whole-star score and gain count reproduces; gain never rejects without score | supported |
| C70: why the transfer failed | New. Attrition, SS Cyg reference and ceilings below | provisional, for Codex |
| C71: SS Aur flag | New. Contents of the flagged run | provisional, for Codex |

My C68 check reuses the frozen feature functions, so it is a reproduction, not a second extractor.
Codex's audit already supplied the independent mask. I accept Codex's sequence review (C67): the
gain-subset property is empirical, and strong fixed-sequence control needs both tests valid under
their own full nulls.

## Findings

**1. The rules are not too strict. The candidates' records are too shallow (C70).**

Under the identical chain, SS Cyg converts 67 of its 73 confirmed 1980s outbursts (92%) into
supported forecasts. The ten candidates convert 102 of 485 (21%).

| Star | Confirmed outbursts, 1980s | Supported (frozen) | Conversion | Without history and mark | Fade-confirmation delay, median (p90), d |
|---|---:|---:|---:|---:|---|
| SS Cyg (reference) | 73 | 67 | 92% | 71 | 1.7 (3.9) |
| SS Aur | 65 | 35 | 54% | 49 | 4.7 (19.6) |
| U Gem* | 27 | 12 | 44% | 27 | 2.4 (10.9) |
| UU Aql | 31 | 13 | 42% | 25 | 3.9 (23.4) |
| RU Peg | 37 | 13 | 35% | 25 | 3.9 (9.9) |
| X Leo | 120 | 22 | 18% | 41 | 3.8 (14.8) |
| AR And | 94 | 7 | 7% | 12 | 6.0 (18.2) |
| TW Vir | 63 | 0 | 0% | 2 | 2.9 (4.5) |
| CH UMa | 20 | 0 | 0% | 7 | 3.7 (13.5) |
| DX And | 10 | 0 | 0% | 8 | 6.0 (20.5) |
| IP Peg* | 18 | 0 | 0% | 5 | 4.4 (15.8) |

*Holds. Supported counts use their frozen derived streams. The other columns use the ordinary raw-report route; on that route U Gem converts 15 of 27.

The fade-confirmation delay runs from the last bright report to the first report at least 1 mag
fainter than threshold, which anchors the DF clock. SS Cyg's quiescence (about 12 mag) is within
reach of nearly every visual observer. Most candidates' quiescence is beyond typical visual limits:
- the decisive-faint evidence that anchors fades and bounds onsets arrives late;
- it is interrupted by observing holes.

**2. The binding loss is the history covariate, not the duration mark.**

Of 822 clock-available candidate forecasts, only 280 have a covered previous gap. The other 542 lack one for these reasons:

| Reason | Forecasts |
|---|---:|
| Observing hole longer than 7 days inside the previous gap | 207 |
| Previous or current onset window ineligible | 162 |
| Previous outburst has no scheduled anchor | 88 |
| Fewer than two bright observers | 52 |
| Nonpositive gap | 20 |
| No history | 13 |

Requiring two decisive-bright epochs for the mark removes only four more forecasts.

For X Leo the DF gap itself is suspect:
- the median supported previous gap is 5.1 days, against SS Cyg's 33.6;
- the lags that bound it are 3.8 days of fade confirmation and 2.4 days of onset window;
- 12 adjacent gaps are nonpositive.

There the DF clock would partly measure when deep observations happen to arrive. Relaxing gates to
raise yield on such stars would trade a yield problem for a measurement-validity problem.

**3. No relaxation, measurement model or later split within this archive reaches the G3b gate (C70).**

| Rule set, at 1980s rates | Ten-star conversion | 28-year projection | 36-year projection |
|---|---:|---:|---:|
| Frozen rules | 21% | 286 | 367 |
| Without history and mark requirements | 41% | 563 | 724 |
| Every confirmed outburst a supported forecast | 100% | 1,358 | 1,746 |

- **Yield.** Reaching 1,100 needs 63% conversion of all confirmed outbursts over 36 years, or 81%
  over 28. That is about three times the current rate, and above what the two best-observed
  candidates achieve (SS Aur 54%; U Gem 44–56%, depending on reduction).
- **Star count.** With the history and mark requirements removed, five stars reach 40 development
  forecasts (SS Aur, U Gem, X Leo, RU Peg, UU Aql). That is before the morphology and eclipse
  screens. CH UMa, DX And and IP Peg each have fewer than 40 confirmed outbursts in their whole
  pre-1990 record, so no measurement model can give them 40 forecasts. A sixth star would have to be
  AR And or TW Vir, whose onset windows are eligible for 31% and 12% of outbursts.
- **Estimand.** Dropping the history covariate would change it from C01's "beyond the history
  baseline" to "beyond a level-only baseline", which a persistent state explains more easily.
- **A later split** trades test years for development years. The five best stars' frozen 1980s
  rate is 95 per decade: about 342 over 1990–2025, or about 238 over 2000–2025 if development
  moves forward to 2000. Either is far below 1,100.
- **Power even if feasible.** The six-star supplement gives 77% for association and 33% for
  forecast gain at 1,100 clean forecasts (C69). Under noisy or delayed marks, which is exactly what
  a faint-quiescence measurement model would produce, those fall to 36% and 10%.

These are planning extrapolations from development rates, not test-period counts. Test-era visual
coverage may be denser than in the 1980s, but even the most permissive relaxation would need it
about 1.5 times higher and would still have five stars.

**4. The SS Aur flag is a threshold artefact, not an established plateau (C71).**

The 100.97-day supported bright run begins in 1970. It contains four separate clusters of
decisive-bright nights (more than 7 days apart), so it holds several ordinary outbursts.
- Of the positive estimates inside it, 70% lie between 12.5 and 13.5 mag, within one magnitude
  brighter than the 13.5 catalogue threshold; their median is 13.2.
- Across the record, positive estimates fainter than threshold have median 14.5.

Quiescent-level estimates were reported just brighter than the threshold in that era. Possible
causes include a comparison-sequence or observer-system offset, but I did not adjudicate the cause.
The screen did its job of flagging contamination; the contamination is photometric, not
morphological. This does not change G3a: SS Aur would be the only star to clear the count.

## Recommendation

**Stop the multi-star expansion. The SS Cyg paper should report G3a as a preregistered transfer
test that failed for a measured reason.**

- **Do not build a new visual-record measurement model for this paper.**
  - The frozen rules convert 92% of SS Cyg's outbursts, so strictness is not the problem.
  - The ceilings above show that a new model would need near-SS Cyg conversion on faint-quiescence
    stars, more stars than the record holds, and test-era coverage above the 1980s. Even if
    everything went right, forecast-gain power would stay near one in three.
  - The development records are open, so any new model would be tuned on the same records it
    qualifies, without G3a's clean preregistration.
- **The finding is a result in its own right.** SS Cyg's near-complete visual timing is the asset
  behind C01, and no other northern U Gem-type dwarf nova in the pre-1990 AAVSO visual record
  approaches it. C01 is a single-star result, and this explains why it must stay one for now.
- **The general question belongs to a separate project with deeper data.** Deep, frequent CCD
  surveys (ASAS-SN, ZTF) should reach these stars' quiescent magnitudes, which would remove the
  binding loss here. A latent-state light-curve model that treats visual limits as censored
  observations is the principled visual-only alternative. Either is a new design and a new access
  decision for Barry, not a rescue of G3a. I have not checked survey coverage of these stars.
- **Keep the G3b rules, the fixed sequence and the six-star grid as the design record.** They are
  the plan a future cohort would start from.

## What changes in the products (R2 integration)

| Product | Change |
|---|---|
| Article | A short section, "Transfer to other dwarf novae": the preregistered rules, zero of ten qualifying, the conversion contrast (92% against 21%), the history-covariate loss and the ceilings. A display item comparing conversion per star with SS Cyg. Limitations: C01 is a single-star result |
| Supplement | Full qualification table, attrition, ceilings, the SS Aur run, both eclipse screens (inconclusive), C69 and the sequence review |
| Brief | One or two sentences: we tried ten other dwarf novae under the same rules; none has a record dense enough; SS Cyg's century of near-complete amateur coverage is what made the test possible |
| Agent guide | Traps: do not relax gates to reach six; DF gaps on faint-quiescence stars measure cadence; the SS Aur flag is photometric; projections are assumptions; the hold screens were inconclusive, not failures caused by eclipses |

These go in with the R2b and R2d results in one integration pass, estimands first (now updated).

## Not checked

- The holds' derived-stream reductions and eclipse screens were not rerun; my attrition uses their
  ordinary raw-report route.
- No independent annotation of the SS Aur run, and no comparison-sequence history.
- Test-era visual coverage is unknown by design.
- Survey depth and cadence for these stars were not checked.
