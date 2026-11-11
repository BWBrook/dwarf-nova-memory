# Third-draft corrections: disposition of Codex's review

Claude, 11 November 2026. Responds to `2026-11-11-third-draft-semantic-review.md` (D053, base
`9669f35`). Every finding was checked against code or evidence before it was applied. No data,
fit or score was opened or computed; the frozen outputs, estimand definitions and parameter bytes
are unchanged. Decision record: D054.

| Finding | Check | Disposition |
|---|---|---|
| P1 C56: rate and end cadence conflated | `scripts/r2b_execute.py:132–134`: `B2.rate` fits rate as the mark on the ordinary B2 base; `B2.cadence` refits B2 with `c_end` and adds duration. `r2b_features.py` defines both | Results, §4.1 and Table 2 report the two sensitivities separately. Estimands, technical record and agent guide (trap 15) record the correction |
| P1 Fig. 1 clipped caption, label-only page | Rendered PDF pages 14–15 at `030c55d` | Figure 8.4 → 7.7 in tall at 90% width; caption cut to five lines. Rebuilt page 14 holds label, figure and full caption |
| Fig. 1B dispersions .30/.20 | `figures.py` schematic; frozen M2 and M3 σ both 0.34636 | Common σ read from the frozen parameters, asserted equal. The schematic also had the wrong sign: after the drawn long outburst M3 sat earlier than M2. It now sits later (medians 30 and 35) |
| Fig. 1C post-result checks start 9 November | `TZ=UTC git show f1aa2ae`: 2026-11-08T13:57:28Z | Both later bars use exact commit times: checks f1aa2ae → cdd5ac8 (D044), screen d827313 → e0924ca (D046) |
| Fig. 4A "development" label for SS Cyg 490 | `reference-counts.json`: 275 before 1960 plus 215 in 1960–1989 | Axis "Supported forecasts in available pre-1990 records"; caption names the 1960–1989 overlap and differing spans |
| Fig. 6 left/right panel references | Rendered figure: A top, B lower left, C lower right | Caption uses A–C |
| Fig. 3 "every comparison" | Forest has eleven selected rows | "Selected duration-gain comparisons" in text and caption |
| C04 doubling = short/long difference | C04 evidence has no class means | Analogy removed; "with timing history fixed … untruncated lognormal clock" |
| Table 1 σ unlabelled | M0 σ 0.362 differs | Labelled M2/M3 in §2.5 and Table 1 |
| State hypothesis entails positive sign | Estimands physical reading | Sign restriction now "tests the direction CM92 reported"; hypotheses "accommodate" the direction |
| "Most of the predictability … recent rhythm" | C02/C10 rank three frozen models | Replaced with the model ranking; "similar gain" for point rescoring |
| Class fit fits a cycle-level mechanism | C21 in-sample likelihood | Motivates a future frozen type predictor; both pathways can produce a class pattern |
| Recalibration attributed to drift | C62/C63 change centring and level together | Transformation named in Results and §4.2 |
| Kimura 2021 as demonstration of state change | `references/evidence.csv` E18 metadata only | "An anomalous event was reported in 2021" |
| "Record times most successive outbursts"; conclusion needs SS Cyg's completeness | C70 counts supported confirmed cycles | "Enough successive, well-covered cycles"; conclusion asks for enough well-covered cycles |
| Observation premise reduced to unconditional independence | `r2-design-v1.md` A2 normalized kernel | §5 and Table 2 state CAR given observed history, factoring out of the likelihood |
| Endpoint row implies independence suffices | C46 tested independent Gaussian errors in one simulator | Row renamed "Endpoint measurement model"; tested family named |
| "All model choices" used development data | Exploratory refits use evaluation data | "The primary model choices and fits" |
| "Bright run of 60 days" omits repeated 40-day runs | Appendix E rule | "No operational long-run flag (… or repeated 40-day runs)" |
| H3 "their paired difference" | Matched delayed-issue population | Named as the matched contrast |
| "Everything after the primary result" exploratory | G3a frozen before opening candidate records | "All post-result SS Cyg reanalyses" |
| Appendix D 0.16323/0.07828 unit | C23 log class offsets | Unit named |
| "Rare in astronomy" | Outside the bounded novelty audit | Removed |

Also done: the brief is rewritten to the third draft under Barry's writing rules (plain result,
one Limits list) with a new two-panel figure (the 1960 light curve and the gain by six-year block);
the agent guide has the C04 sizing, the corrected C56 reading and traps 15–18. Codex's suggested
future check (comparing the regenerated example's hashes and CDF30 against R1's annotations inside
`figures.py --check`) is not implemented here.
