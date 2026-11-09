# R2a aggregate preparation evidence

These are aggregates from gain-free preparation of retained, already opened
SS Cyg observations before 2018, plus separately labelled synthetic controls.
No individual real feature, event, observer identity or new real forecast score
is included. All new claims remain provisional pending Claude's review.

Source freezes and reproductions:

- `fe6dbf4`: `scripts/r2a_observation_diagnostics.py --freeze-commit fe6dbf4 --output outputs/r2_x5_reproduction`
- `f0049dd`: `scripts/r2a_model_controls.py --freeze-commit f0049dd --output outputs/r2_models_reproduction`
- `956d33c`: `scripts/r2a_feature_preparation.py --freeze-commit 956d33c --output outputs/r2_features_reproduction`
- `scripts/check_r2a_model_controls.py --run outputs/r2_models_reproduction --output outputs/r2_model_scalar_check`
- `scripts/check_r2a_feature_counts.py --features outputs/r2_features_reproduction --output outputs/r2_population_recount.json`

Run with the project Python environment. Real-input preparation requires the
retained private acquisition/cache and is not reconstructed from public synthetic
fixtures. Output directories must be new. Receipts retain hashes of unreleased
inputs/outputs, not the inputs themselves.

`model-independent-check.json` uses joint Gaussian conditioning in place of the
candidate state recursion and independently reconstructs scores. It verifies
numerical implementation on nine synthetic histories; it does not establish
calibration or optimizer global optimality. `matched-clock-intersection.json`
checks counts/schema without evaluating real predictions. `filter-source.json`
records the verified source identity without redistributing the book.

The report in `docs/audits/2026-11-09-r2a-preparation-and-r2c-review.md` governs
interpretation, including the different populations, current/history anchor
asymmetry, recrossing/association assumptions and the absence of real R2b fits.
