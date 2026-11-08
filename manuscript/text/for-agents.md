---
document: agent-facing paper
study: Frozen SS Cyg forecast comparison
status: first full drafts of all products (A10l), awaiting Codex's semantic review and Barry's review
human_paper: manuscript/text/main.md (+ supplement.md, brief.md)
claims_ledger: manuscript/claims.csv (single source for all renderings; checked by tools/claims.py)
interpretation: manuscript/estimands.md (what each analysis bounds; allowed and forbidden phrasings)
governing_docs: [AGENTS.md, coordination/decisions.md, manuscript/estimands.md]
authority: Barry W. Brook decides public release, submission and any correspondence outside the collaboration
updated: 2026-11-09
---

# SS Cyg for agents: evidence, build and interpretation traps

This guide is for an agent arriving cold. The article, supplement and brief are first full drafts
(A10l). They are not released, and venue and submission are Barry's decisions. The governing
specification and ledger take priority over captions, drafts or historical review wording. When this file and a primary artefact disagree, the artefact
wins and this file is wrong: fix it in the same commit.

## 1. Read order and trust

1. This file, then `manuscript/estimands.md`, then `manuscript/claims.csv`. Quote a claim only with its
   limit.
2. `manuscript/text/main.md` for the argument; `supplement.md` for the machinery.
3. `coordination/decisions.md` (latest decision entries) for what was settled, by whom and why.

`status` is *supported* (checked against its evidence by an agent or person other than its author),
*provisional* (awaiting that check), *refuted* or *superseded*. `basis` says what kind of result it is.

## 2. The answer, as claims

- **Does the completed outburst's duration improve frozen forecasts of SS Cyg's next onset beyond
  the timing baseline?** Yes, under the predeclared rule: mean paired log-score gain
  [0.0165]{.C01 .V001} nats per issuance, 90% cluster interval [0.0049]{.C01 .V002} to
  [0.0281]{.C01 .V003}, over [441]{.C01 .V004} issuances in 1960–2017 (C01–C03). The run followed a
  post-access format repair (C05).
- **Is it robust?** Every protocol sensitivity kept a positive lower bound (C09). Eight of ten block
  means are positive, and the decision fails at an SE multiplier of [1.427]{.C25} (C25). These are
  checks of one comparison, not new confirmations.
- **Did every predeclared secondary agree?** No. 1993–2017 is inconclusive (C07), and so is the
  frozen 12-day class rule (C08). There was no era test, so do not infer disappearance.
- **What carries the information?** In exploratory post-result fits, a long/short indicator is
  favoured over continuous duration (C21). Part of the gain is a level correction (C20). The class
  rule's weakness is sensitive to its coding against the fixed baseline (C22). None of this is held-out.
- **Is it memory, or a mechanism?** Not established. Alternation (C24) and a coexisting slow state
  are both compatible (C12, C13; supplement S3.4).
- **Is it new?** The association, alternation and 12-day split are CM92's (C40). The preregistered
  probabilistic held-out test is new to our knowledge, but one held-out point-forecast study exists
  (C41, still provisional).

## 3. Vocabulary that the files use

| Term | Meaning |
|---|---|
| X4 | The frozen threshold-crossing extractor, `src/dnmem/extract_x4.py`, run at visual magnitude 10 |
| C1/7 d | Coverage rule: a visit gap over seven days ends coverage |
| Issuance | One forecast per observation-time end confirmation (`causal_confirmations`) |
| Prefix | The rows in the 400 days before an emission; the only predictor source |
| M0, M2, M3 | Constant, timing (previous gap q, recent level L) and timing-plus-duration lognormal clocks |
| P3 | Lagged-duration placebo; identical to M2 because its development coefficient is zero |
| Fallback | Rows without a covered previous gap; M0 for both models; gain exactly zero |
| Type rule | 12-day uncentred indicator plus centred within-type duration; frozen secondary |
| Blocks | Six-year calendar clusters anchored at JD 2436934.5 |
| Development, evaluation | 1910–1959 fit; 1960–2017 frozen test; 2018 onward closed |
| Clock scale | Median of the untruncated lognormal clock; not an observed wait |

## 4. Provenance map

| Result | Inputs | Code | Output | Claims |
|---|---|---|---|---|
| Frozen parameters | 1910–1959 ledger | A10e fit scripts | `data/fits/a10e_1910_1959/frozen_parameters.json` | C04, C14 |
| Primary and secondaries | Retained run `outputs/a10h_live_repair_5e39aeb` (not in Git) | `scripts/check_a10g_evaluation.py` | `data/provenance/a10i_evaluation_1960_2017/` | C01–C03, C05–C11, C15 |
| Post-result review | Same run | `scripts/a10j_postresult_review.py` | `data/provenance/a10j_postresult_review/summary.json` | C06–C10, C20–C25 |
| Independent audits | Same run | `scripts/a10k_exploratory_audit.py`, `scripts/a10k_secondary_audit.py` | `data/provenance/a10k_independent_review/` | C11–C13, C20–C25 |
| Simulations | Synthetic | A10d/A10f scripts | `data/simulations/` | C30, C31, C33 |
| Figures | Aggregates above | `manuscript/figures.py` | `manuscript/figures/`, `manuscript/figure-data/` | C01, C06–C08, C11, C21, C23 |
| Prior art | CM92 scan, search logs | none | `references/evidence.csv`, A01 and A10l memos | C40, C41 |

The primary result selects issue times in [2436934.5, 2458119.5), delay 0, the point-duration
marks, and all score-eligible issuances *including* the [5]{.C03} fallback zeros. Dropping the
zeros gives the joint-valid sensitivity (436 rows), not the primary. A quoted era number is a
secondary estimate, not "the result".

## 5. Traps: superseded results and known misreadings

<!-- Numbered. Each trap: the tempting misreading in bold, then why it is wrong and the claim that
governs. Add one whenever a review catches a misreading. -->

1. **A global mean is not a model for temporal drift.** The recentering contrasts leave within-period
   drift possible and reuse evaluation outcomes (C20).
2. **An in-sample class preference is not exclusive validated attribution.** C21 supports its stated
   conditional fit comparison; it supplies no absence or equivalence result for within-class effects.
3. **A component restriction is not a whole-model restriction.** The uncentred type component is zero
   for short events; its within-class companion can shorten a forecast (C08, C22).
4. **Negative net lag does not allocate mechanisms.** A slow component can coexist with stronger
   alternation. C12–C13 are conditional profiles; C24 counts forecast-record pairs, including a repeat.
5. **The SE threshold is strict.** C25's boundary is not an inclusive safe rounded multiplier, nor a
   substitute for validating block dependence.
6. **Keep score checking separate from historical source identity.** The scalar audit checks saved
   outputs without rerunning the live acquisition or its clean-source guard. The receipt binds source
   bytes at the execution snapshot. Compare those hashes to Git objects at the recorded freeze,
   and check the original forecasting files against the current checkout. Publication tooling can
   evolve outside those files. Never edit an old receipt to match a newer checkout, or rerun the
   acquisition command to reproduce scores.
7. **Metadata retrieval is not a source-level literature audit.** C40 was re-read on the original
   scan in A10l; C41 remains provisional until an independent search check.
8. **The DOI does not timestamp the repair.** Preserve the failed attempt and the post-access format
   repair in every product that reports C01 (C05).
9. **A draft is not a paper release.** Venue, submission, manuscript release and any future
   data opening remain Barry's decisions. The closed block must remain closed.
10. **"First held-out forecast" is false without qualifiers.** Grigorievskiy et al. (2014) scored
    held-out point forecasts of outburst onset for V363 Lyr. Keep "preregistered, probabilistic"
    and "known to us" (C41).
11. **Cannizzo (1993) does not predict this result.** His model explains alternation through disc
    depletion and links recurrence time with the long-to-short ratio through slow parameter changes.
    No quiescence contrast after long versus short outbursts was found in it. "Compatible with", never
    "confirms" (estimands, physical reading).
12. **The simulation reference is not a target.** The realised gain exceeds C33's model-specific
    mean, which carries Monte Carlo uncertainty. That says nothing about exceeding a known physical
    effect.

## 6. Checks before and after any change

```sh
uv run --project manuscript --frozen python tools/refs.py build  # metadata refresh; uses network
python3 manuscript/figures.py --check  # public assets; no raw observations needed
python3 scripts/check_a10g_evaluation.py --directory outputs/a10h_live_repair_5e39aeb --output outputs/a10k_saved_score_audit.json
make -C manuscript check          # claims, glyphs, makedoc lint and citation audit
make -C manuscript                # PDF and DOCX into manuscript/build/, then the brief page check
```

Invariants to assert when touching analysis code:

- The 26 qualified forecasting files and the frozen parameter bytes (SHA-256 `ce4ef8d5…`) are
  unchanged.
- The saved-score audit reports zero failures and reproduces C01 exactly.
- No archive request is made, and no 2018-onward row, count or coverage summary is read.
- The poisoned-future-row test in `tests/test_prefix_features.py` passes.

## 7. Open edges

- **Later-segment weakness (C07).** Real change, observing change and sampling are not
  distinguished. An independent photometric extraction for recent decades would separate them.
- **Class versus continuous (C21, C22).** This needs a new frozen test whose indicator coding and
  intercept freedom are defined together. The closed 2018-onward block should serve as one stratum
  of a multi-star protocol, since alone it would hold roughly 65 forecasts at earlier rates (a
  planning assumption).
- **Memory versus slow state.** P3 failed to inform (frozen at zero). A latent-state timing baseline
  is the next discriminating comparison.
- **Endpoint coupling.** Shared end-time error can create information in some constructions
  (D021). The uniform-end and delay sensitivities only probe it.
- **Bibliography.** Hempelmann & Kurths (1990) and Grigorievskiy et al. (2014) have no DOI and are
  cited as plain text until Barry adds Zotero entries. C41 awaits an independent search check.

## 8. Conduct in this repository

- Read `AGENTS.md` (or `CLAUDE.md`). Facts and citations come from sources read in the task; every DOI
  is checked against Crossref.
- To add or change a claim: edit `manuscript/claims.csv`, reverify the evidence, run
  `python3 tools/claims.py stamp manuscript/claims.csv ID`, then make every document pass the check.
- Change `manuscript/estimands.md` before changing how a result is described.
- Do not edit generated artefacts by hand: `references/refs.yaml`, marked table blocks, `figures/`,
  `build/`.
