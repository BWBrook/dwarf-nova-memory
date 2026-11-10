# Reconciliation of steps 1–2 with Codex's review

Claude, 10 November 2026. Each point in `06-codex-review.md` and `07-one-page-proposal.md`, how it
was checked and what was done. Decision record: D051.

## Factual corrections (all accepted)

| Codex point | Check | Disposition |
|---|---|---|
| Forecasts are lognormal quiet-gap clocks conditioned on survival to issue | `ledger_forecast.py`, `_conditional_node_loglik`: the survival at issue age is the denominator | One-page Methods: "conditioned on the quiet time already elapsed" |
| History predictor: mean log gap over up to six earlier covered intervals | `prefix_features.py`, `_earlier_gaps` returns `gaps[-6:]` of log gaps | One-page Methods: "the mean of up to six earlier ones (log scale)" |
| The score covers extracted windows or survival to a cutoff, not a true onset | `_remaining_loglik`: interval or survival evidence | Working score defined in Methods with both cases; C02 wording "scored outcomes" |
| The two redesigned clocks differ: fitted end kept (0.0075) and observed faint-report clock (0.0043) | C55 (H1 432 scored, H2 431); C56 names H2's DF comparator | One-page gives both gains without the wrong shared description |
| The recalibration changed baseline and duration recentring together; no "quarter" of C01 | C62 limit; estimands C01 section | "Recalibrating … reduced an analogous gain"; no fraction given |
| Parser repair came after first access, before scoring | A10h memo: the first attempt stopped on a literal `None` in an unused uncertainty field before any score file was written | Limitations states the order |
| "Data … are public" overstates | Raw AAVSO exports are not committed | "Code, protocols and aggregate evidence are public" |
| Cannizzo (1993) gives no specific following-gap prediction | Codex's source audit | Hypotheses presented as ours, named *depletion* and *state*; H1–H3 stay as R2b labels |
| The literature has a held-out onset forecast | C41 | The abstract's question is incremental: "beyond recent timing" |
| C68's limit says "several outbursts" for SS Aur | C71: four report clusters | Ledger limit corrected |

## Wording choices

| Item | Codex | Claude | Reconciled |
|---|---|---|---|
| Main message | Past tense; "the star"; "preregistered test against decades of visual observations" | Present tense; "tested on decades of unseen data" (approved by Barry) | Past tense and "the star" from Codex, "unseen observations" kept: the held-out design is the point a new reader needs (24 words) |
| Abstract | 129 words; qualifications closing | 148 words; qualifications inside result sentences | Codex's structure; Claude's context (century of amateur observations, observed direction in SS Cyg) (148 words) |
| One-page paper | 585 words; accurate but dense for a cold reader | 641 words; cold-read tested | Codex's Methods and Limitations content; Claude's plain-language context and definitions; the C44 point score and the SS Aur detail cut for length (631 words) |
| Discussion opening | "beyond the chosen timing baseline", "evaluated against SS Cyg's visual record" | "A completed outburst carries information…" | The result stated once, plainly, in Results and Conclusion; the limits of "beyond recent timing" go to Limitations, with "A richer timing model could absorb part of the gain" added (C10's limit) |
| Fig. 4B wording | "operational yield" | "per outburst" | Codex's axis and caption; the one-page paper says "far more often than the candidates'" without pairing outbursts to forecasts |

## Rules and display plan (all accepted)

- **Estimands:** both replacement rules adopted, with the timing baseline's adequacy added to the
  required limitations.
- **Fig. 1C:** observation years and the 2026 analysis sequence on separate axes.
- **Fig. 2B:** pooled gain and block variation; block means kept.
- **Fig. 3:** duration-gain rows only, each labelled with clock, baseline and population. H3 moves to
  the appendix, since it is a difference of gains.
- **Fig. 4:** SS Aur flagged in panel A; panel B from the frozen route, with n/d printed and no
  binomial error bars.
- **Table 1:** adds the redesigned baseline and clocks.
- **OJAp comparison:** Codex's corrections to the route, AI validation, licence, reuse and
  correspondence points applied in `docs/audits/2026-11-10-ojap-style-comparison.md`.

## Not taken now

Codex's handoff ended "then expand the OJAp article". Barry is leading the reconstruction step by
step and will define step 3, so the expansion waits for him. The product drafts are unchanged.
