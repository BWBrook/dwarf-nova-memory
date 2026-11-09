# R1 aggregate evidence

Post-result research, not a new confirmation. The original SS Cyg evaluation,
parameters and 26 qualified forecasting sources remain unchanged. No archive
request, other-star record or SS Cyg 2018+ observation/count/coverage was used.
Native observations, event catalogues and real per-issuance tables are not
released here. The working-score and latent-onset qualifications are in
`docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md`.

| Files | Evidence |
|---|---|
| `censor-audit.json` | Actual-candidate audit; both frozen builders and prospective v4/reference checks |
| `observation-scores.json`, `clip-diagnostic.json` | Frozen-score sensitivities, availability and missing-clip explanation |
| `example-and-simulation-table.json`, `all-comparisons.csv`, `simulation-table.md` | Scalar Figure 1 calculation and all 480 previous simulation comparison rows |
| `endpoint-summary.json`, `endpoint-population-audit.json`, `dose-response.*` | Forty histories per case, five doses, fixed/ordinary populations and bounded interpretation |
| `initial-endpoint-receipt.json`, `recovery-endpoint-receipt.json`, `endpoint-combination-proof.json` | Initial 79-success/one-failure execution, same-seed recovery, all original 80 histories exactly once |
| `numerical-audit-diagnosis.json` | Gain-free diagnosis of eight adjacent-float log-history differences |
| `independent-endpoint-check.*`, `independent-recovery-check.*` | Separate scalar point/survival and retained-parameter replay audits |
| `independent-first-pass-*` | Preserved mistaken refit-equality comparison; subsequent audits distinguish refit and replay |
| `manifest.json` | Aggregate file hashes and source/input identity |

The initial dose implementation/protocol freeze is `0594146`; `93e52e6` changes
only the retained-ledger numerical audit and its preparation call. All 23 other
runner functions and 15 scientific dependencies are unchanged. An additional
outside-grid scored smoke is disclosed in `r1-execution-addendum-v1.md`.

Reproduction uses retained local inputs and never fetches data. Run the scripts
listed in the R1 audit into new output directories. A full dose rerun at
`93e52e6` performs all eighty original tasks with the bounded comparison rule.
`scripts/check_r1_endpoint.py` independently verifies completed serialized
histories. Its selected nonzero-beta case supplies numerical branch coverage,
not a selected scientific result. MC SEs quantify variation across these
simulated histories; they do not certify a population error rate or exclude
other real observation mechanisms.
