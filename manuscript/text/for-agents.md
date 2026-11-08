---
document: agent-facing paper
study: Frozen SS Cyg forecast comparison
status: figure/build review scaffold; substantive products pending
human_paper: manuscript/text/main.md (+ supplement.md, brief.md)
claims_ledger: manuscript/claims.csv (single source for all renderings; checked by tools/claims.py)
interpretation: manuscript/estimands.md (what each analysis bounds; allowed and forbidden phrasings)
governing_docs: [AGENTS.md, coordination/decisions.md, manuscript/estimands.md]
authority: Barry W. Brook decides public release, submission and any correspondence outside the collaboration
updated: 2026-11-09
---

# SS Cyg for agents: evidence, build and interpretation traps

This is the build/evidence scaffold for an agent arriving cold. The article, supplement and brief
prose still await drafting; the figure previews do not constitute a completed paper. The governing
specification and ledger take priority over captions or historical review wording. When this file and a primary artefact disagree, the artefact
wins and this file is wrong: fix it in the same commit.

## 1. Read order and trust

1. This file, then `manuscript/estimands.md`, then `manuscript/claims.csv`. Quote a claim only with its
   limit.
2. `manuscript/text/main.md` for the argument; `supplement.md` for the machinery.
3. `coordination/decisions.md` (latest decision entries) for what was settled, by whom and why.

`status` is *supported* (checked against its evidence by an agent or person other than its author),
*provisional* (awaiting that check), *refuted* or *superseded*. `basis` says what kind of result it is.

## 2. The answer, as claims

<!-- One bullet per question, citing claim IDs and binding the key numbers. -->

## 3. Vocabulary that the files use

| Term | Meaning |
|---|---|
| | |

## 4. Provenance map

| Result | Inputs | Code | Output | Claims |
|---|---|---|---|---|
| | | | | |

<!-- Name the exact row filters that select the primary result; most misquotations drop one. -->

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
7. **Metadata retrieval is not a source-level literature audit.** C40 and C41 remain provisional.
8. **The DOI does not timestamp the repair.** Preserve the failed attempt and the post-access format
   repair in every product that reports C01 (C05).
9. **A build preview is not a paper release.** Venue, submission, manuscript release and any future
   data opening remain Barry's decisions. The closed block must remain closed.

## 6. Checks before and after any change

```sh
uv run --project manuscript --frozen python tools/refs.py build  # metadata refresh; uses network
python3 manuscript/figures.py --check  # public assets; no raw observations needed
python3 scripts/check_a10g_evaluation.py --directory outputs/a10h_live_repair_5e39aeb --output outputs/a10k_saved_score_audit.json
make -C manuscript check          # claims, glyphs, makedoc lint and citation audit
make -C manuscript                # PDF and DOCX into manuscript/build/, then the brief page check
```

<!-- Invariants worth asserting when touching the analysis code, bound to the ledger. -->

## 7. Open edges

<!-- Each open question, what would move it, and what has been tried. -->

## 8. Conduct in this repository

- Read `AGENTS.md` (or `CLAUDE.md`). Facts and citations come from sources read in the task; every DOI
  is checked against Crossref.
- To add or change a claim: edit `manuscript/claims.csv`, reverify the evidence, run
  `python3 tools/claims.py stamp manuscript/claims.csv ID`, then make every document pass the check.
- Change `manuscript/estimands.md` before changing how a result is described.
- Do not edit generated artefacts by hand: `references/refs.yaml`, marked table blocks, `figures/`,
  `build/`.
