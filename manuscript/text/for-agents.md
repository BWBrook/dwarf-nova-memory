---
document: agent-facing paper
study: ONE-LINE STUDY NAME
status: internal draft
human_paper: manuscript/text/main.md (+ supplement.md, brief.md)
claims_ledger: manuscript/claims.csv (single source for all renderings; checked by tools/claims.py)
interpretation: manuscript/estimands.md (what each analysis bounds; allowed and forbidden phrasings)
governing_docs: [docs/charter.md, docs/decisions.md]
authority: Barry W. Brook decides public release, submission and any correspondence outside the collaboration
updated: 2026-11-09
---

# STUDY for agents: what this study established, how to verify it, and how not to break it

This is the version of the paper written for an agent arriving cold. The human paper argues; this one
indexes. It says what is claimed, where each number lives, which commands regenerate it, what has been
superseded, and where the open edges are. When this file and a primary artefact disagree, the artefact
wins and this file is wrong: fix it in the same commit.

## 1. Read order and trust

1. This file, then `manuscript/estimands.md`, then `manuscript/claims.csv`. Quote a claim only with its
   limit.
2. `manuscript/text/main.md` for the argument; `supplement.md` for the machinery.
3. `docs/decisions.md` (newest first) for what was settled, by whom and why.

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

## 6. Checks before and after any change

```sh
uv run tools/refs.py build        # bibliography from references/dois.txt
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
