# Synthetic recovery summaries

`a04c_screening_summary_20261107.csv` contains 288 aggregate cells from 3,200
synthetic histories. Each finder/threshold/rule sees 200 histories per
phase/process/era. Estimates pool event-count denominators where applicable;
other diagnostics are means of replicate statistics. MC intervals use replicate
as the uncertainty unit. Undefined counts and gate verdicts are explicit.

`a04c_calibration_20261107.json` contains aggregate calibration diagnostics from
the open-era native stream. It includes no observer identities or raw rows.
The [receipt](../manifests/a04c_simulation_receipt_20261107.json) binds source
hashes, preparation and simulation code, input cache, seeds and result bytes.

See the [A04c report](../../docs/audits/2026-11-07-a04c-injection-recovery.md)
for the strict effective-versus-conditional coverage distinction and the aligned
arm's limitations. Neither finder qualifies under the frozen selection gate.
No real duration–gap association or forecast score is contained here.

The full per-replicate metric rows, scheduling cache and full summary JSON are
gitignored under `outputs/`. Reproduction commands are in the report; the
original hashed raw acquisitions must exist locally. Do not add the large
regenerable payloads or source observer metadata to Git.

## A04d (Claude, training only)

`a04d_morphology_check_20261107.json` compares local slopes, residual scatter
and estimates per window around X1 boundaries in real 1910–1959 rows with the
A04c v1 benchmark and Claude's training "smooth" morphology
(`scripts/a04d_morphology_check.py`). `a04d_x3_training_20261107.csv` holds
the X1/X2/X3 training batch: five conditions, 40 replicates per era, scored by
the unchanged A04c scorer (`scripts/a04d_train_x3.py`).
`a04d_x3_point_check_20261107.csv` compares X1 midpoints with X3 point
estimates (`--points`). All use training seeds disjoint from A04c and from the
future validation; none is validation evidence. Replicate rows stay in
`outputs/`.
