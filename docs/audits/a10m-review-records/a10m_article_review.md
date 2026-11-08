# A10m article and caption semantic review

Reviewer: Codex, 9 November 2026. Reviewed base: `2ec353493b941ef190b63d74267375f29e119af6`.

**Disposition: revise the article's interpretation, retain the frozen result and all four captions.** The main numeric result, routing population, score units, secondary inconclusiveness, access-repair disclosure and most exploratory qualifications agree with the committed aggregates. Table 2 reintroduces stronger conclusions that the governing estimands explicitly prohibit. Two discussion sentences also exceed the forecast estimand. These are prose corrections; no new fit or change to the frozen comparison is warranted.

## Scope and independence

I read `AGENTS.md`, `manuscript/text/for-agents.md`, the entire article and four captions, `manuscript/estimands.md`, every ledger row and the value bindings. I checked the result statements directly against the committed primary, summary, native audit, frozen parameters, A10j summary and A10k exploratory/secondary aggregates; I inspected relevant prefix/extraction/figure code and the original publication/failure receipts and repair audit. I knew the proposed claims and previous audit conclusions. This was an independent semantic reading and artifact comparison, not a blind audit or a new numerical derivation of all scores.

Only committed aggregates, protocols, documentation and source code were read. No archive request, new fit, raw-observation inspection, per-issuance-score inspection, or 2018-onward observation/count/coverage access occurred. I did not change manuscript, ledger, scientific code, parameters, receipts or board state. The only task outputs are this report and `outputs/a10m_article_sentences.csv`. Tests were not rerun for this output-only review.

The CSV records 234 article sentence/bullet/table-row dispositions and the four complete caption paragraphs, with source lines, governing claim/estimand and evidence paths. Author-role bullets and navigation headings are outside the result review. The source-line references below refer to the reviewed base.

## Required interpretation corrections

### R1 — Table 2 allocates predictive information to class without evidence (high priority)

**Source:** `manuscript/text/main.md:311`.

> The information is mainly long/short class

**Governing evidence:** C21; `estimands.md:93–102`; `data/provenance/a10k_independent_review/exploratory.json`, `refits.1960-2017`.

The type-only and continuous-duration models have LR 14.698 and 11.686 against a level-only fit, and adding a linear within-class term gives LR 0.168. These are conditional, nonnested, evaluation-fitted comparisons. They establish neither where most validated predictive information resides nor absence of within-class effects. A future held-out failure, listed in the table's last cell, is not the qualification missing from the present attribution. The figure-4 caption already expresses the correct interpretation.

**Minimal replacement:** “The class-only model has a larger exploratory in-sample likelihood than continuous log duration.” Replace the last cell with “No held-out allocation of information to class, or within-class absence/equivalence test.”

### R2 — Forecast gain is presented as measured disc-state information and scheduling utility (high priority)

**Sources:** `main.md:38–39`, `main.md:268–270`.

The sentence calling the gain “a measured constraint on how much of the disc's state is visible” turns a score comparison of extracted events into a physical-state measurement. No disc state, physical mechanism or observation-utility model was fitted. Endpoint coupling, informative observing and residual slow state remain possible explanations. Likewise, the 1.7% geometric likelihood ratio alone does not establish that the gain “would matter little” for a telescope schedule; that requires a forecast-decision utility analysis. The introductory “therefore” equating predictive information with how much disc state survives a cycle creates the same framing risk before any results.

**Governing rule:** `estimands.md:11–13,24–36,140–151`; C01/C02 and the working statistical models.

**Minimal replacement for lines 268–270:** “The mean score gain is small in the stated units. It quantifies incremental predictive information beyond this timing baseline; its value for observing decisions and its relation to physical disc state were not measured.”

**Minimal introductory replacement:** “Whether a completed outburst improves a next-onset forecast is a measurable predictive question; relating any gain to the surviving disc state requires a separate physical model.”

### R3 — Sensitivity to coding is upgraded to an explanation of a crippled hypothesis (medium priority)

**Sources:** `main.md:24–26`, `main.md:298–299`.

The abstract says the class rule's weak score “reflects how its class term was coded,” and the discussion says a restriction can “cripple a secondary hypothesis, as the class rule showed.” C22 establishes sensitivity to the shared evaluation-fitted level, not a unique explanation of C08. The whole class-plus-within rule could shorten short-outburst forecasts: the committed audit counts 181 of 245 such cases. The main methods at lines 243–249 correctly preserve this distinction, but these summaries overstate it.

**Governing evidence:** C08/C22; `estimands.md:53–56,103–107`; exploratory aggregate `limitations` and `level.same_best_level_type`.

**Minimal abstract replacement:** “The exploratory in-sample fit favours a class indicator, and the class rule's score is sensitive to its coding against the fixed baseline.”

**Minimal discussion replacement:** “The secondary class contrast proved sensitive to indicator coding and baseline calibration, so future fixed-baseline contrasts should specify coding and intercept freedom together.”

### R4 — Other Table 2 rows blur the object calculated and the inference supported (medium priority)

**Sources:** `main.md:309–313`.

- **Line 309:** shared-endpoint coupling could undermine a physical interpretation while leaving the observed score gain for extracted onsets intact. The SE-rescaling arithmetic also does not diagnose long-range dependence. Separate the observed comparison from the uncertainty assumptions and physical meaning.
- **Line 310:** “not a level artefact alone” is broader than the global constant-mark recentering. The named recentered contrast is positive, but within-period drift remains untested.
- **Line 312:** the current later segment is inconclusive. A future reliable decline would not make the current record evidence of disappearance; decline and disappearance are different conclusions.
- **Line 313:** conditional success on synthetic waveform/cadence families does not establish that real physical onsets were measured “well enough.”

**Minimal replacement objects for the first column:**

| Line | Replacement conclusion |
|---|---|
| 309 | The frozen M3 assigns higher mean log score than M2 to the specified extracted outcomes |
| 310 | The global-mean-recentered score contrast remains positive in this exploratory calculation |
| 311 | The class-only model has a larger conditional in-sample likelihood than continuous log duration |
| 312 | The 1993–2017 gain is inconclusive |
| 313 | X4 met the specified synthetic qualification at magnitude 10 with C1/7-day coverage |

Use a final column headed “Limit” to state the remaining uncertainty directly. Do not make a future test the condition that would invalidate a present statement about insufficient evidence.

### R5 — State retrospective availability in article prose (medium priority)

**Sources:** abstract `main.md:14–16`; methods `main.md:110–112`; contrast with `figures.md:1`.

The first caption correctly says historical upload/revision times are unknown. The abstract and main methods contain no equivalent statement; “scored forecasts issued at the end of each outburst” and “information available when it is issued” can therefore read as a genuine historical operational replay. The implemented predictor cutoff uses reported observation JD, which is not evidence that the archive held that row then. Causal end confirmations also need not coincide with the estimated end itself.

**Governing rule:** C01; `estimands.md:17–23,34–36`; AGENTS' historical-availability boundary.

**Minimal abstract change:** “...then scored observation-time retrospective forecasts issued at causal end confirmations from 1960 to 2017.”

**Minimal methods addition:** “Historical upload and revision times are unknown, so this replays reported observation times rather than verified historical archive availability.”

## Small factual corrections

### R6 — Avoid double rounding and an exact claim at a rounded strict boundary

**Sources:** `main.md:178–180`, `main.md:309`.

- The uniform-end lower endpoint is `0.00444547865427204`. It rounds directly to **0.0044**, not the printed 0.0045, at four decimal places. The ledger's five-decimal 0.00445 followed by another rounding creates this discrepancy. No sign or interpretation changes.
- The strict SE failure boundary is `1.4270501885272726`, holding estimate and t critical value fixed. At exactly **1.427**, the lower bound is still `+0.000000581474`. Thus “1.427 or more” is literally false without “about.” Use “about 1.42705,” or “a 1.43 multiplier would fail.” This does not validate cluster independence or all uncertainty sources.

**Evidence:** summary `secondary.robustness.uniform_end.gain_M3_M2.lower`; secondary audit `C25_block_statistics`.

### R7 — Single-observer confirmation does not require the margin on both nights

**Source:** `main.md:100–102`.

The code requires bright observations on at least two native JD nights, **at least one** at the confirmation margin, and no contradicting other-observer faint report on those nights. “One observer on two nights well past the threshold” implies both nights must pass the margin.

**Evidence:** `src/dnmem/extract_x4.py:76–86`.

**Minimal replacement:** “...or by one observer on two nights, at least once well past the threshold, with no contradicting faint report from another observer on those nights.”

## Clarifications that would improve the draft

### R8 — Name conditional support and the alternation population explicitly

**Sources:** `main.md:218–226`, `main.md:253–257`.

The recentering paragraph already says evaluation-fitted adjustments and denies drift removal/causal partition. Its intervals should also explicitly be described as conditional on the fitted centre/level. The association paragraph properly calls its ranges “conditional support”; add that they are working-likelihood ranges with refitted M2 fixed and do not propagate baseline, dependence or measurement uncertainty. They are not calibrated confidence intervals.

The alternation paragraph already says “forecast record,” and its numbers are correct. A short parenthesis should identify the actual population: “441 positive-duration pairs at forecast issuances, including one repeat-flagged record.” This avoids treating the descriptive pairs as an independent unique-outburst catalogue; the joint association design uses a different 436-row subset. These are clarity improvements, not evidence that the current numbers are wrong.

### R9 — Soften the unsupported prospective power assertion

**Source:** `main.md:319–324`.

The roughly 65 forecasts are explicitly a planning extrapolation and do not breach the closed-data boundary. But “too few to test this effect alone” is a categorical power/design judgment without a stated target, effect scenario, cluster design or operating-characteristic calculation for that projected sample. The existing 11/40 result describes one simulator at its own evaluation size.

**Minimal replacement:** “That projected sample is unlikely to support a precise stand-alone test; a new design study should evaluate its power as part of a multi-star protocol.” Similarly, line 328's independent photometry would **help distinguish** observing and physical changes; it cannot promise to separate them uniquely.

## Findings accepted without a scientific change

- **Primary:** 441 issuances; mean `0.016533512177436503`; 90% interval `[0.00494771630959865,0.028119308045274356]`; 10 clusters/df9. 436 timing routes and five shared M0 fallback zeros; 435 onset brackets and six censored outcomes. The printed headline, geometric likelihood translation and baseline-gain ratio have the correct units and population.
- **Secondaries:** 1960–1992 and 1993–2017 estimates/counts, C08's class-plus-within rule and C09's sensitivity definitions agree with the aggregates. The later segment and class rule remain explicitly inconclusive. No additional confirmation or disappearance inference is warranted or required.
- **Recentring:** the main result paragraph correctly names a global recentering, untruncated scale change and approximately additive descriptive split, and explicitly retains within-period drift and interaction. The table needs the narrowing in R4.
- **Class fits:** the detailed subsection correctly states historical M2 nuisance is fixed, a level is free, the fits are nonnested, within-class absence was not tested, and the 14% is an untruncated working-clock scale contrast. The class-component/whole-rule distinction at lines 243–249 is correct.
- **Calibration/association:** observed overcoverage is conditional partial identification, not confidence for population coverage; the profile estimates and zero-crossing joint support agree with the committed audit. No mechanism separation follows from the signs.
- **Repair:** publication at `12:34:47 UTC` precedes the first acquisition at `12:38:28 UTC`; the first attempt stopped before scoring. The draft preserves the failure, outcome-independent exact-token repair, consumed untouched status, original DOI versus later repair and closed 2018+ boundary.
- **Captions:** all four are semantically sound. Figure 1 is an illustration selected by earliest eligible observation-time issue, with display groups split by issue and limits correctly described. Figure 2 distinguishes descriptive blocks from the single primary interval and inconclusive secondaries. Figure 3 describes sample partial-identification bounds. Figure 4 explicitly prohibits exclusive attribution, equivalence and new held-out confirmation, and uses the right model-scale units.

## External-source checks pending parallel review

This review does not independently certify external astronomy facts or novelty. The following manuscript assertions must be reconciled with the source-review agent's evidence:

- Abstract lines 8–11 and introduction lines 41–65: continuity since 1896, northern-sky brightness, historical cycle convention, CM92 correlations/type split, Hempelmann–Kurths dependence, chaos result and Cannizzo model details.
- Lines 32–37 and 272–280: DIM description, disc depletion/alternation, long-to-short recurrence covariation and the absence of a reported following-quiescence contrast in Cannizzo (1993).
- Lines 67–83: claims that all predecessors are in-sample, that the single V363 Lyr point-forecast study is the only held-out precedent found, the Price precursor result and both qualified priority clauses. C41 remains provisional until the independent search disposition; qualifiers alone do not prove the search complete.
- Line 324: the literature-based 2021 stress-case description. Reading that published event description would not authorize any closed archive access.

The CSV labels these statements `source_pending` rather than treating earlier review prose or bibliographic metadata as proof. This reviewer did not repeat the parallel literature search.

## Source identity

SHA-256 of reviewed inputs:

| File | SHA-256 |
|---|---|
| `manuscript/text/main.md` | `51e981d96722aadaed3e8232c94c25cfbdb86fe2e395ad809b1f25563f205b60` |
| `manuscript/text/figures.md` | `c8204ffcdbc48a93f6ed692df86a20f306650dd92452a015d3a3efc61b81e297` |
| `manuscript/estimands.md` | `1ca19feffc947024139ae4b028345a242d5cc09886bfe53f7ff8062be9615ca4` |
| `manuscript/claims.csv` | `d3fe8926c60c9cee35274318746719f7a5beb71703fb8973b0d2682c804a7859` |
| `manuscript/value-bindings.csv` | `1c1d36ff14293e0d4c2ccdbe456e3ac4e1e142330f6f8b7ed5be0754db1f8d28` |

Next: Codex — integrate the article corrections with the independent source review.
