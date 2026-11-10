# Step 4: display items

The main message (`03-main-message.md`) rests on three lines of evidence:
- the preregistered test;
- the measurement checks;
- the ten-star screen.

A new reader also needs one context item showing what an outburst, a forecast and the test design
are.

## Budget

**Main text: four figures and two tables. Everything else goes to appendices in the same PDF.**
- With the methods folded in, the main text will run about 6,000–7,000 words. About one display
  item per thousand words is the ceiling before a single-message paper starts to buckle.
- OJAp papers carry 2–17 figures and 0–6 tables (`docs/audits/2026-11-10-ojap-style-comparison.md`).
  Six items is moderate for the journal and enough for this message.
- The current draft has 4 figures and 3 tables in the main text, and 2 figures and 4 tables in the
  supplement. Two of its main-text items are the wrong ones: the evidence-status table and the
  separate R2b table.

## Main text

| Item | Content | Purpose | Source | Change from current draft |
|---|---|---|---|---|
| **Fig. 1, context (3 panels)** | **A.** A few years of SS Cyg's real light curve, with long and short outbursts. **B.** A schematic of one cycle: duration, quiet gap, issue time, the two forecast distributions and the scored onset window. **C.** The study timeline: fit 1910–1959, freeze and publish, test 1960–2017, then the checks and the ten-star screen | Defines every term before it is used; supplies the missing methods schematic | Existing light-curve input (panel A); panels B and C are drawn, not data | **New.** It absorbs current Fig. 1's light-curve panel |
| **Fig. 2, main result (2 panels)** | **A.** One example forecast: timing-only against timing-plus-duration distributions, with the outcome. **B.** Mean gain in each six-year block across 1960–2017, with the overall mean and its 90% interval | Shows what a better forecast looks like, and that the gain holds across decades of unseen data | C01, C25, C42 | **Revised** from current Figs. 1 and 2. The secondary comparisons move to Fig. 3 |
| **Fig. 3, robustness (1 forest plot)** | One axis with the primary result as reference. Groups: the two preregistered secondaries (C07, C08); the measurement checks (point score C44; R2b H1–H3, C55); the level-adjusted diagnostics (C62, C63) | Every comparison in one place, so the reader judges robustness at a glance | C07, C08, C44, C55, C62, C63 | **Revised** from current Fig. 3 and the R2b table, which moves to an appendix |
| **Fig. 4, transfer (2 panels)** | **A.** Supported development forecasts per star against the 40-forecast gate. **B.** 1980s supported forecasts per confirmed outburst, with SS Cyg as reference | Can the test be run on other dwarf novae, and why not | C68, C70 | **Revised.** The eligible-window panel moves to an appendix; panel B is new |
| **Table 1, models and test** | M0, M2 and M3: predictors, fitting period, frozen parameters; the score; the test statistic and criterion | Methods at a glance; pairs with two or three defining equations | C01, C04, C10 | **New** |
| **Table 2, assumptions and limits** | Each assumption, why it matters, what tested it and what remains open | The backbone of the single limitations section | Estimands; current Table 2 | **Kept and expanded.** It replaces caveats scattered through the text |

The current evidence-status table ("what the evidence directly supports") is dropped. Its content
moves into the limitations section and Table 2.

## Appendices, in the same PDF

- Calibration of predictive intervals (current Fig. S1).
- Long/short-class exploration (current Fig. S2).
- Frozen comparisons in full (Table S1) and the R2b contrasts (Table S2).
- Precision simulations (Table S3).
- The full ten-star qualification (Table S4), with the eligible-window panel and the attrition
  chain.
- The eclipse screens and the SS Aur run.

## Open choices

- **A cumulative-gain curve could replace the block means in Fig. 2B.** It would show "tested on
  decades of unseen data" more vividly, but its figure data would expose per-forecast scores, which
  the repository keeps out of Git. Block means are already public. Recommendation: block means.
- **Fig. 1C or a sentence?** The timeline could be one sentence, but new readers grasp the freeze
  far faster from a picture. Recommendation: keep it.
