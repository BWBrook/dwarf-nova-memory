# Independent scalar R1c score check

Status: failed; tolerance 1e-09; failures 3052; erfc underflows 0.

| History | Evaluation fixed anchors per dose | Maximum truth-score error | Maximum legacy score difference |
|---|---:|---:|---:|
| null000 | 297 | 3.55e-15 | 8.42e-07 |
| null001 | 277 | 3.55e-15 | 5.19e-07 |

All five measured doses and the composite oracle were checked using scalar normal survival/lognormal density, with routes and covariate transforms reconstructed from serialized parameters. Anchor sets, original issue times and exact extracted/truth common subsets were checked across doses. Legacy primary populations, routes and individual scores were compared with receipt-verified retained A10d streams; null000 also supplies an exact original ledger/evidence trace.

Null000 has beta=0 throughout. Null001 was selected solely as the first completed positive-beta parameter branch; its sigma1 measured fit and composite oracle exercise the duration offset. This is numerical coverage, not an inferential comparison or selected scientific result.

Truth risk sets/next-event identities were rederived from retained truth and sigma-zero features. Administrative cutoffs were checked against retained v4 stopping metadata where available. No raw visit stream is retained in these files, so coverage cutoffs were not reconstructed independently from observations. The full grid remains in progress. No fit, new simulation or source edit was made. Input hashes are in summary.json.
