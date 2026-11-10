# Step 1d: display items

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
| **Fig. 1, context (3 panels)** | **A.** A few years of SS Cyg's real light curve, with long and short outbursts. **B.** A schematic of one cycle: duration, quiet gap, issue time, the two forecast distributions and the scored onset window. **C.** Two timelines on separate axes: the observation years (fit 1910–1959, test 1960–2017; candidates pre-1990 only) and the 2026 analysis sequence (freeze, Zenodo deposit, data access, parser repair, scoring, then the checks and the screen) | Defines every term before it is used; supplies the missing methods schematic. Separate axes stop the picture implying that preregistration happened in 1959 | Existing light-curve input (panel A); panels B and C are drawn, not data | **New.** It absorbs current Fig. 1's light-curve panel |
| **Fig. 2, main result (2 panels)** | **A.** One example forecast: timing-only against timing-plus-duration distributions, with the outcome. **B.** Mean gain in each six-year block across 1960–2017, with the pooled mean and its 90% interval | Shows what a better forecast looks like, and how the gain varies across decades of unseen data; the caption reports the pooled gain and the block variation | C01, C25, C42 | **Revised** from current Figs. 1 and 2. The secondary comparisons move to Fig. 3 |
| **Fig. 3, robustness (1 forest plot)** | One axis of duration gains with the primary result as reference. Groups: the two preregistered secondaries (C07, C08); the measurement checks (point score C44; the two redesigned clocks, C55); the drift-recalibrated diagnostics (C62, C63). Each row labels its clock, baseline and scored population. The paired clock difference (H3) is a difference of gains, so it goes to the appendix | Every duration-gain comparison in one place, so the reader judges robustness at a glance | C07, C08, C44, C55, C62, C63 | **Revised** from current Fig. 3 and the R2b table, which moves to an appendix |
| **Fig. 4, transfer (2 panels)** | **A.** Supported development forecasts per star (whole development period) against the 40-forecast gate, with SS Aur flagged as passing the count and failing the long-run gate; the caption names the other gates. **B.** Supported issuances / confirmed episode peaks, 1980–1989, from the frozen route for each star, with n/d printed beside each point and SS Cyg as reference; no binomial error bars | Can the test be run on other dwarf novae, and what a record needs for it | C68, C70 | **Revised.** The eligible-window panel moves to an appendix; panel B is new |
| **Table 1, models and test** | M0, M2 and M3: predictors, fitting period, frozen parameters; the redesigned baseline and clocks used in Fig. 3; the score; the test statistic and criterion | Methods at a glance; pairs with two or three defining equations | C01, C04, C10 | **New** |
| **Table 2, assumptions and limits** | Each assumption, why it matters, what tested it and what remains open | The backbone of the single limitations section | Estimands; current Table 2 | **Kept and expanded.** It replaces caveats scattered through the text |

The current evidence-status table ("what the evidence directly supports") is dropped. Its content
moves into the limitations section and Table 2.

## Appendices, in the same PDF

- Calibration of predictive intervals (current Fig. S1).
- Long/short-class exploration (current Fig. S2).
- Frozen comparisons in full (Table S1) and the R2b contrasts (Table S2), including the paired clock difference (H3).
- Precision simulations (Table S3).
- The full ten-star qualification (Table S4), with the eligible-window panel and the attrition
  chain.
- The eclipse screens and the SS Aur run.

## Fig. 4B caption (agreed with Codex, 10 November 2026)

Axis: "Supported issuances / confirmed episode peaks (1980–1989)". Caption: "Numerators count
supported forecasts by issue date; denominators count confirmed episodes by peak date within the
same decade. Hold stars use the specified derived-night streams. Ratios describe operational yield
under these rules." The panel shows yield; the prose does not attribute the difference to any single
cause such as visual depth.

## Settled choices

- **Fig. 2B uses block means, not a cumulative-gain curve.** A cumulative curve would show the
  decades of unseen data more vividly, but its figure data would expose per-forecast scores, which
  the repository keeps out of Git. Block means are already public. Codex agrees.
- **Fig. 1C stays a picture.** New readers grasp the freeze far faster from a timeline than from a
  sentence.
