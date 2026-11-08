# A10m support-product follow-up

Codex, 9 November 2026. Checked the working-tree corrections relative to base
`2ec353493b941ef190b63d74267375f29e119af6`.

**Verdict: SR1–SR7 and SP1–SP3 are resolved. No semantic blocker remains in the changed
support-product passages.** The changes preserve the frozen primary comparison and distinguish
it from exploratory calculations, mechanism claims, physical-onset calibration and future work.

This follow-up read only the changed support drafts, the corresponding ledger/specification
changes, the local A10m novelty audit/receipt metadata, relevant existing source contracts and
committed aggregates. It did not repeat the literature search or the primary-source appraisal.
No new fit, raw-data reproduction, live acquisition or 2018-onward access was performed.

| Finding | Current passage | Recheck and disposition |
|---|---|---|
| SR1: transformed timing covariates | Supplement 18–19, 83–96; guide 59, 122–123 | Resolved. q and L are standardized; explicit formulas use frozen development centres/scales, with missing L imputed to zero after transformation. Sigma is now correctly called a log-standard deviation. |
| SR2: unseen-waveform status | Supplement 51–56; guide 124–125; estimands measurement qualification | Resolved. The failed gate is benchmark qualification, and X4 recovery on that family is explicitly untested. No complete real-event recovery claim remains. |
| SR3: within-class LR comparator | Supplement 234–238; guide 126–127 | Resolved. Class/continuous LRs compare to level only; LR 0.17 adds within-class duration to the class model. |
| SR4: rounded SE boundary | Supplement 177–181; guide 37–39; C25 | Resolved. Approximately 1.42705 is no longer an inclusive literal failing multiplier; the 42%/43% distinction and dependence limitation remain. The ledger now retains the exact aggregate boundary 1.4270501885272726. |
| SR5: completeness, issue time and historical availability | Brief 26–38 | Resolved. The brief explicitly disclaims complete flare recovery, issues at end confirmation and says historical arrival dates are unknown. The primary remains a retrospective evaluation. |
| SR6: class attribution/coding explanation | Brief 53–57 | Resolved. The text reports post-result model fit and shared-level sensitivity rather than allocating information exclusively to type or uniquely explaining the original weakness. It retains “cannot count as a second test”. |
| SR7: retained inputs and evidence-preserving reproduction | Supplement 339–369; guide 73–74, 130–131, 139–143; A10j reproduction commands in ledger | Resolved. Public checks/builds are separated from private-input recalculations. Evaluation and development inputs are required explicitly. A10j writes to an explicit scratch path; the other printed analysis/checker outputs are also under ignored outputs. Existing script contracts create output parent directories. |
| SP1: future multi-star protocol | Brief 67–68; guide 158–161 | Resolved. The brief says “possible” and “potentially”; the guide remains an explicit recommendation with a planning count rather than a future-data observation or settled opening decision. |
| SP2: independent extraction discrimination | Guide 156–157 | Resolved. It now proposes a sensitivity check rather than claiming one extraction separates real temporal change from observing changes and sampling. |
| SP3: block definition | Guide 63 | Resolved. It states fixed 6×365.25-day blocks anchored at the specified JD. |

## Other changed assertions

- **C09 rounding:** the ledger's uniform-end lower bound
  `0.00444547865427204` equals the saved `summary.json` value exactly. Rounding directly to four
  decimal places gives the supplement's 0.0044, avoiding the earlier double rounding through 0.00445.
- **C22:** the revised “class-plus-within rule's mean offset” correctly names the whole offset.
  `scripts/a10j_postresult_review.py:212–223` includes both the type and within-class terms in that
  mean. The added 181-of-245 binding agrees with the committed independent exploratory aggregate.
- **Brief gain units:** “higher geometric mean likelihood of the recorded outcomes” now names
  the C02 object precisely. The brief's revised closing sentence is conditional on measured
  length, the archived record and the stated rules; its mechanism paragraph now retains endpoint
  error as an unresolved alternative.
- **C41 and new supplement S3.8:** the supported object is the finding from a bounded independent
  search, not universal priority. The new text says “among the studies located and checked”,
  retains “to our knowledge”, does not claim inaccessible studies were excluded, and reports
  source-access/indexing gaps. The V363 statements use “no ... is reported” rather than asserting
  an external preregistration could never have existed. This matches the local novelty audit's
  recommendation and limitations. Receipt metadata contain 43 query entries and 68 retained CM92
  citing records, as the updated ledger says. This is reconciliation with the separate review,
  not another independent literature search or full-text check.
- **Correction record and new guide traps:** they describe the accepted corrections without
  changing the primary or converting diagnostic calculations into confirmations. The guide's
  C41 summary and draft status agree with the current review stage; Barry's release/data decisions
  remain explicit.

## Verification

The following checks passed on the revised working tree:

```sh
python3 tools/claims.py check manuscript/claims.csv manuscript/text/supplement.md manuscript/text/brief.md manuscript/text/brief_figures.md manuscript/text/for-agents.md
python3 manuscript/figures.py --check
```

The ledger check reported 26 supported claims, zero errors and zero warnings. The public figure
check reported five figures and ten assets without requiring private inputs. Exact comparisons
against committed aggregate JSON also confirmed C09 and C25's newly retained precision. No
recalculation command printed in the manuscript was executed for this review.

Only this assigned follow-up report was written. The parent A10m reviewer owns integration,
rendered-product verification and the final handoff.
