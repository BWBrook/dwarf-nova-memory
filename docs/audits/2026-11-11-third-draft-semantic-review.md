# Third-draft review: C04 verified; targeted corrections required

Codex, 11 November 2026. Review base `030c55d`, responding to thread 159/3195
and D052. The shorter article is a coherent expansion of the one-page paper.
Methods in the main text and one limitations section work. Keep that structure.
The original numerical result stands. I would return the draft for the targeted
corrections below before signing off its prose and figures.

This is a review, not a rewrite: article, captions, PDFs, estimands and frozen
analysis outputs remain unchanged. The only new calculation derives a parameter
contrast and sums already-public reference counts. No archive request, raw
observation, new fit or forecast score was used. Two bounded read-only delegates
checked C04 and figure arithmetic; the parent checked interpretations, C56's code
path and the rendered PDF. Neither agent identity nor passing tests is taken as
validation of the observation model.

## What checks out

- The primary 441-forecast gain, its interval, fallback/censor counts, baseline
  gain, era/class secondaries, saved-point sensitivity, block/deletion summaries
  and reported coverage endpoints agree with their existing evidence.
- All eleven forest estimates, intervals and counts match independent reads of
  the public aggregates. H1/H2 means and cluster SEs also reconstruct from saved
  block sufficient statistics. H3 is correctly absent from the forest.
- The selected example's feature/outcome hashes, CDF values and annotations agree
  with the saved R1 example. Figure 2's weighted block means recover the primary.
- Figure 4B's 102/485 and 67/73, derived hold streams and issue/peak landmarks
  agree. Figure 4A's SS Cyg total is **490**, with a population-label correction
  below.
- C04's new arithmetic is correct. With beta = 0.04659658037107343 and
  s = 0.38294184198218767, doubling duration changes the standardised mark by
  ln(2)/s = 1.8100586161388617 and log location by 0.08434254178326842. Thus
  exp[beta ln(2)/s] = **1.0880015159653311**, an **8.800151596533121%** increase
  in the untruncated clock median at fixed timing history. Frozen n_fit is
  **330 for M0 and 307 each for M2/M3**. These counts are verified metadata,
  not a new recount of observations.

C04's independent artifact is `data/provenance/third_draft_review/c04.json`;
`python3 scripts/check_c04_scaling.py` reproduces it using the standard library
and checks the frozen parameter hash. Its basis, evidence, reproduction pointer
and limit are updated in the ledger. The calculation describes exp(mu), not the
survival-conditioned remaining-wait median or an observed causal interval.

Suggested Results wording at main lines 224–226:

> With timing history fixed, doubling duration increases the duration model's
> untruncated median quiet-interval clock by about 9%.

The short/long doubling analogy needs its own source; C04 alone supplies no class
means. In Table 1, label the displayed sigma as M2/M3's: M0's sigma differs.

## Corrections before sign-off

| Priority | Finding and check | Required revision / owner |
|---|---|---|
| P1 | Main 260–263 and 304–305 substitute **observer-night rate** for **raw end cadence**. The 0.004278322 duration gain belongs to a B2 base containing c_end, not an observer-rate base. Two independent code traces confirm this. | Separate the two saved sensitivities in Results and Discussion; Claude. No new joint fit is needed. |
| P1 | PDF page 14 has only the Fig. 1 label; page 15's oversized image/caption pushes the caption through the footer and cuts off its ending. Confirmed visually and with page text extraction. | Resize or reflow Fig. 1 and its caption in the existing review layout, then inspect the rebuilt pages; Claude. This does not require the deferred two-column build. |
| P2 | Several sentences turn operational support into physical completeness, or a tested gain decomposition into a statement about most predictability or physical mechanisms. | Apply the precise positive replacements below; keep qualifications in Section 5. |
| P2 | Main 256's “their paired difference” and 364's “everything after” erase distinct populations and access status. | Name H3's matched fitted-end population; restrict the exploratory/reused-data sentence to SS Cyg reanalyses. G3a was frozen before opening new-star development records. |
| P2 | Fig. 1B changes lognormal dispersion between M2/M3, Fig. 1C starts UTC post-result checks late, and Fig. 4A calls all SS Cyg support “development”. | Repair model structure, chronology and reference labels as specified below; Claude. |
| P2 | Section 5/Table 2 reduce the observation premise to unconditional independence, and make independent end errors look sufficient. | Describe the required observation/measurement model and conditional CAR factorization; retain Appendix C's normalized-kernel premise. |

### C56: the substantive covariate error

The frozen catalogue and `comparisons.csv` distinguish:

| DF comparison | Predictor / base | Saved mean gain |
|---|---|---:|
| B2.rate | Observer-night rate replaces duration as the mark | 0.0030435210846513003 |
| B2.duration | Duration added to ordinary B2 | 0.004276497039279191 |
| B2.cadence | Duration added to separately refitted B2 with raw c_end | 0.00427832189467883 |

`scripts/r2b_execute.py:132` fits the rate replacement. Lines 133–134 refit the
base with cadence and add duration. `src/dnmem/r2b_models.py:71` reads
`cadence_end.value_days`, whereas lines 87–89 read `observer_rate.value_per_day`.
`src/dnmem/r2b_features.py:81` defines c_end from the faint anchor and preceding
eligible positive report; lines 98–114 define observer-night rate over the
bright span. The distinction is predeclared in protocol v2, lines 136–147.
No joint rate-plus-duration fit is recorded in this frozen model catalogue.
C56 itself already distinguishes the quantities correctly.

Suggested Results replacement:

> An observer-night-rate mark gained 0.0030 nats (0.0013–0.0048) over the
> decisive-faint B2 baseline when used in place of duration. Separately, adding
> the raw end-cadence gap to that baseline left the incremental duration gain
> essentially unchanged, at 0.0043 nats.

Use that same distinction in Section 4.1. The current draft's claim that rate
adjustment leaves duration unchanged is unsupported by this evidence.

### Positive findings and the flagged interpretations

- **Main 298–302:** replace “Most of the predictability ... lies in its recent
  rhythm” with **“Among the frozen models tested, timing history made the larger
  contribution to the working score.”** The 0.117-versus-0.0165 comparison is
  real; it is not a decomposition of all available predictability. Point
  rescoring gives a *similar gain*, rather than reproducing an identical value.
- **Main 268–271 and 320–324:** name **duration recentring plus baseline level
  recalibration** as the transformation. Smaller gains are compatible with slow
  variation; changing both terms does not uniquely assign the reduction to drift.
  Appendix C correctly retains the saved-label/proxy-availability qualification.
- **Main 309–316:** the class indicator has the higher conditional in-sample
  likelihood, with the stated historical nuisance parameters fixed. It motivates
  an outburst-type predictor in a future frozen comparison. Both type-dependent
  recovery and a changing state could produce a class pattern; the fitted class
  preference does not favour a physical mechanism. Keep a physical account as
  a hypothesis, rather than present the fit as a mechanism test.
- **Main 68–75 and 127–131:** the state hypothesis motivates added information,
  but does not itself entail a positive coefficient. State that the sign
  restriction tests CM92's published positive direction. The depletion account's
  similar-supply condition is already helpful. No specific following-gap
  prediction was verified in Cannizzo (1993).
- **Main 326–336:** replace “the record times most successive outbursts” with
  **“SS Cyg's record supplies enough successive, well-covered cycles for the
  frozen test.”** These counts establish operational support among confirmed
  episodes, not completeness against the unknown physical-event population.
  The conclusion should require *sufficient supported cycles*, rather than
  exactly SS Cyg's completeness.
- **Kimura 2021, main 318–320:** the source register remains abstract/metadata-only
  (`references/evidence.csv`, E18), with the 2021 anomaly already disclosed in
  the outcome-knowledge ledger. A metadata-only Crossref request verified the
  [paper identity](https://doi.org/10.1093/pasj/psab073), selecting DOI, title,
  author, publication date and type, without requesting an abstract or full text. It supports saying that an anomalous event was
  reported, rather than treating that event as a source-checked demonstration
  of a particular accretion-state change. I opened neither its full text nor any
  post-2017 curve, archive row, count or coverage summary. No later-data gate is
  changed by this citation.

These are changes to what a sentence names. They require no return to repeated
claim-by-claim caveats. The single limitations section is retained.

### Assumption and population definitions

Section 5's first paragraph can start:

> The working score evaluates extracted onset windows. Establishing physical-onset
> forecast skill requires a validated model for how the selected reports and
> observing times arise.

Use the A0–A2 premises already in Appendix C. The project's explicit A2 contract
is a normalized kernel K(Y|t,H,S) = c(Y,H,S) 1{t in A(Y)}, with separate observation
and forecast parameters (`r2-design-v1.md:39–44`). Conditional dependence on observed
history can be compatible with this factorization. “Observing effort is
independent of the outcome” is not the same statement. Likewise, independence
of true end error and true next interval does not remove the induced shared
measurement error. Label Table 2's row *Endpoint measurement model* and explain
the coupling and tested error family there.

Other short definition fixes:

- Main 94: **primary** choices and fits used development data; exploratory
  evaluation refits appear later.
- Main 202: use *no operational long-run flag*; Appendix E correctly also includes
  repeated forty-day runs.
- Main 256: **“The paired contrast between DF gain and fitted-end gain at the same
  delayed issuances was ...”** H3 is not H2 minus the displayed original-issue H1.
- Main 364: **“All post-result SS Cyg reanalyses reuse opened data and are
  exploratory.”** Keep the prospectively frozen G3a feasibility screen distinct.
- Appendix D 514–515: 0.16323 and 0.07828 are **log class offsets**, not scale
  ratios. Name the unit before those values.
- The broad “rare in astronomy” assertion is outside the bounded novelty audit.
  The explicit preregistered design and C41 already state this paper's contribution.

### Figures and PDF

1. **Fig. 1B:** `figures.py:734` uses sigma .30 for M2 and .20 for M3. Frozen
   primary M2/M3 share sigma 0.34636170156690677 and differ by location. Use a
   common log-scale dispersion, with the illustrative mark and location shift
   consistent with the stated duration direction.
2. **Fig. 1C:** `figures.py:251` dates all post-result checks from November 9,
   while labels say UTC. A10j was committed at **November 8, 13:57:28 UTC**
   (`git show -s --format=%cI f1aa2ae` gives November 9, 00:57:28 +11:00).
   Start the UTC range on November 8, or explicitly restrict the later bar to
   named later checks. The deposit/access/scoring timestamps check out.
3. **Fig. 4A:** 490 = 176 + 36 + 63 + 70 + 78 + 67. That is **275 before 1960
   plus 215 during 1960–1989**, so the reference includes part of the original
   held-out era. Use **“Supported forecasts in available pre-1990 records”** and
   say that available spans differ. Its labelled truncated reference bar is
   acceptable as a count comparison, not an exposure-adjusted quality estimate.
   `data/provenance/third_draft_review/reference-counts.json` records the sum.
4. **Fig. 6 caption:** the existing graphic has A at top, B lower-left and C
   lower-right. Replace the new left/right description with those panel labels.
5. **Fig. 3:** use *selected duration-gain comparisons* rather than *every
   comparison*; the article also reports other frozen variants.
6. **Review PDF:** shrinking or reflowing Fig. 1 should remove the label-only
   page and caption truncation. The deferred journal class is not needed to fix
   this review artifact. Other reviewed pages have no material clipping.

A future checking improvement, rather than a blocker: `figures.py --check` does
not compare the regenerated example's selected hashes/CDF30 against R1's fixed
annotations. The independent check confirms they match now.

## Audit record and checks

`data/provenance/third_draft_review/sentence-audit.csv` maps 38 result-bearing
passage/caption groups to evidence and verdicts, including Table 2 and the
appendices. A literal search of forbidden-claim terms complements that semantic
check; avoiding a phrase alone would not validate its replacement. Existing
prior-art source checks are retained, not claimed as a refreshed literature search.

The parent inspected all 21 rendered pages through contact sheets and the four
new figure assets, with the oversized caption checked separately. Figure source
arithmetic and the parameter contrast were independently reconstructed. Figures
were not regenerated and no product build was performed in this review.

All 580 tests pass. Figure/table, claims, glyph, makedoc lint and citation checks
pass; these do not catch the semantic substitution or PDF clipping. The new
C04/C70 ledger evidence records verified arithmetic only. The 26 qualified
forecasting sources, frozen parameter bytes and original outcomes remain intact.
The brief and agent guide are still awaiting alignment, as D052 states.

## Handoff

Claude: apply the targeted text/figure/layout corrections, rebuild and inspect
Fig. 1, then return a focused review diff. Retain the concise article structure
and concentrated limitations. Align the brief and guide once the corrected
article is agreed. No new data, fit or score is required for these corrections.
