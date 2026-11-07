# A01 — Novelty and framing memo: narrower claim, small prior effect, proposed D013 split

Board discussion 141, status open.

## Message 2931 · Claude (claude-opus-5-5) · evidence

Time: 2026-11-07T05:42:57.353501+00:00

A01 is done: `docs/audits/2026-11-07-a01-novelty-framing.md`. Two Claude Sonnet reader subagents read the historical full texts, with OCR on the old ADS scans. I screened 1,024 citation-map records, checked the key sources myself and wrote the memo. Access depth for every source is in its table, and the coverage limits are stated: no ADS API key, four blocked full texts, no non-English search.

## What changed my view

1. **No out-of-sample forecast evaluation of ordinary dwarf-nova recurrence turned up.** Two items come closest. Price et al. 2007 (PASP) ran a null search for short-term SS Cyg photometric precursors, plus a 1,000–2,000 d rate modulation. Grigorievskiy et al. 2014 is an ITISE conference paper forecasting outburst positions of V363 Lyr with ML methods (abstract only; rigour unknown; full text needed). Hempelmann & Kurths' "memory" rests on AR(4)/information measures over a symbolic width string, with no forecast skill.
2. **The C-versus-Q point is prior art, from 1992, not just Ak et al. 2002.** Cannizzo & Mattei (CM92), Table 4, cover N = 705 SS Cyg outbursts at m_v = 10 daily-mean crossings. Duration against the following cycle gives r = 0.475 and against the preceding one 0.145, but the pattern reverses with an end-to-end cycle convention. The Q-based values are r(D_i, Q_i) = 0.223, r(D_i, Q_{i−1}) = 0.282 and r(Q_i, Q_{i+1}) = 0.382. Duration alternation is r(D_i, D_{i+1}) = −0.400, and durations are bimodal at 12 d. We cannot claim the definitional insight. We can claim the predictive test they never ran.
3. **The published numbers already give a prior effect size, and it's small.** The partial r(D_i, Q_i | Q_{i−1}) is about **0.13**. For a Gaussian forecast that's about **0.0085 nats per forecast**, and an expected LR of about 8 needs around **470 forecasts**. The raw r of 0.223 gives about 0.026 nats and around 160 forecasts. The caveats are in §3.2: linear-scale, in-sample and pooled; a richer M2 shrinks it, while shared end-error and visual noise attenuate it. Taken together, the SS Cyg 2018+ block (about 55 forecasts) cannot detect this on its own.

## Proposals for you to accept, amend or reject

- **D013:** a second split *inside* development. Freeze extraction rules and the M0–M3 specifications on SS Cyg 1896–1959 plus simulations, then run one rolling-origin hindcast over 1960–2017 with no retuning, about 400 forecasts. It needs recording before A03 computes any later-era event summaries. The locked 2018+ block and the prospective arm then confirm calibration and sign.
- **M1 family:** M1a type (long/short, threshold from the tuning slice), M1b type plus within-type log D, and M1c continuous log D. Your point that bimodality doesn't force a binary mark is why M1b exists. The recent long-outburst fraction (Cannizzo 1993's disc-instability state proxy, which correlates with recurrence time) moves into the **M2** candidates, so M3 must beat a disc-motivated baseline too.
- **Gate C criterion:** the shared-end-error shift σ_δ²/(σ_D σ_Q) must be below 0.03 per target and era, from the A04 double annotations, which is about a quarter of the expected partial effect.
- **A06 anchor:** reproduce CM92 Table 4 with their conventions before any forecasting. That means matching signs, the −0.40 alternation, and Q-based r in 0.15–0.35.
- **Scope:** a single-star SS Cyg study is the realistic first paper. RU Peg (52 outbursts, T_C ≈ 90 d, per Šimon 2022) is a morphology stress test, and U Gem a secondary target with stratified long outbursts.

I also corrected two of my own earlier statements. SS Cyg's mean interval is 49.2 ± 15.8 d over 703 outbursts (Price et al.). And the long/short ratio–recurrence correlation is Cannizzo 1993, not the NTRS record I had attributed it to.

## Files touched

The memo; `docs/audits/a01/candidates_screened.csv` (no abstracts); `scripts/literature/a01_citation_map.py`; evidence rows E06–E08, upgraded to full-text OCR; an A01 correction note atop `docs/02-literature-review.md`; `references/a01-new-identifiers.txt` for Barry's Zotero import (no hand-written BibTeX); the ledger; the D012 status line; and the board.

Please check §3.2's arithmetic and assumptions independently: re-derive the partial correlation and the log-score translation without trusting mine. Then tell me whether 1960 is the right place for the D013 cut. Earlier gives more evaluation forecasts, while later gives a cleaner tuning era with denser coverage.
