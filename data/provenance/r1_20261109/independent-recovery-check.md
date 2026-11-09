# Independent structured000 recovery check

Status: passed_with_disclosed_comparison_and_refit_differences. Score tolerance remains 1e-09. Numerical failures: 0; erfc underflows: 0.

All 3504 saved M2/M3 truth scores across five measured doses plus the composite oracle agree with independent scalar erfc/log-density calculations within 3.55e-15. The 1536 retained-parameter legacy model scores agree within 3.02e-14; populations/routes agree.

The unamended exact ledger comparison flagged 8 rows. Independent comparison identifies exactly the eight previously diagnosed one-adjacent-float earlier_gaps entries, with no changed values/types elsewhere. The entire recovered sigma-zero ledger equals the pre-scoring diagnosed regenerated ledger; observation/truth/ledger digests match. The old exact-comparison failures remain explicit in summary.json and are classified only after these checks. No predictor was rounded or replaced and no score tolerance was relaxed.

Fixed anchors and extracted/truth shared subsets agree across doses. New legacy refit absolute scores differ from the retained model scores by up to 2.63e-07, reported separately from retained-parameter replay.

This history has beta=0 for every measured dose and oracle. Its check does not exercise a positive offset or certify the full-grid aggregate. No fits/new simulations/source edits were made. All inspected files are hashed in summary.json.
