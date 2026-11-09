# Independent scalar R1c score check

Status: passed_with_refit_differences; tolerance 1e-09; failures 0; erfc underflows 0.

Batch receipt status at read: completed_with_failures. Verification covers only the histories listed below.

| History | Evaluation fixed anchors per dose | Maximum truth-score error | Maximum retained-parameter replay error | Maximum new-refit difference |
|---|---:|---:|---:|---:|
| null000 | 297 | 3.55e-15 | 2.75e-14 | 8.42e-07 |
| null001 | 277 | 3.55e-15 | 5.68e-14 | 5.19e-07 |

All five measured doses and the composite oracle were checked using scalar normal survival/lognormal density, with routes and covariate transforms reconstructed from serialized parameters. Anchor sets, original issue times and exact extracted/truth common subsets were checked across doses. Legacy primary populations, routes and individual scores were compared with receipt-verified retained A10d streams; null000 also supplies an exact original ledger/evidence trace.

The new legacy-v3 refits differ from retained absolute scores above the requested 1e-9 tolerance. That first-pass failure is preserved. Frozen-parameter replay is a separate calculation; no tolerance was relaxed. The final status distinguishes these refit differences from failures of numerical replay.

The additional history was selected solely as the first completed positive-beta parameter branch in the declared seed order. Its audited coefficient values are retained in summary.json. This is numerical coverage, not an inferential comparison or selected scientific result.

Truth risk sets/next-event identities were rederived from retained truth and sigma-zero features. Administrative cutoffs were checked against retained v4 stopping metadata where available. No raw visit stream is retained in these files, so coverage cutoffs were not reconstructed independently from observations. No fit, new simulation or source edit was made by this check. Input hashes are in summary.json.
