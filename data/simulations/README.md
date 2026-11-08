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

## A04f (Claude, development only)

`a04f_x4_development_20261108.csv` scores X3 and X4 on the A04e v2 benchmark
(diagnosis seeds) and Claude's smooth training family, both cadence arms, 40
histories per cell (`scripts/a04f_develop_x4.py`).
`a04f_observer_diversity_20261108.json` compares distinct bright observers per
X1 episode in real 1910–1959 rows with both v2 cadence arms, and counts real
episodes confirmed by X4's single-observer rule (`--diversity`). Neither is
validation evidence.

## A10a (Claude, prefix predictors and precision)

`a10_prefix_pilot_20261108.json` applies the proposed prefix-causal ledger and
live-forecast evidence rule (`src/dnmem/prefix_features.py`) to real
1910–1959 rows and to 72 v2-phase development histories (`a10-claude-dev-*`).
Real-data entries are boundary, lag and evidence-status diagnostics only; no
real duration–gap association is computed. Synthetic entries add correlation
retention for true, retrospective and prefix durations
(`scripts/a10_prefix_pilot.py`). `a10_precision_20261108.json` is the
standardized Gaussian precision model for paired forecast gain and slope tests
(`scripts/a10_precision.py`). Neither is validation evidence.

## A10c (Claude, control re-aggregation and truth check)

`a10c_reaggregated_controls_20261108.json` re-aggregates the retained A10b
repaired-run scores (outside Git) by forecast route and fitted coefficient,
and scores the proposed A10c design (matched routing, β ≥ 0) on them
(`scripts/a10c_reaggregate_controls.py`). `a10c_truth_associations_20261108.json`
gives duration–gap and gap–gap correlations in the magnitude-10 truth catalogue
for each v2/v4 timing process: six 400-year histories each, with new
`a10c-claude-truth-*` seeds (`scripts/a10c_truth_associations.py`). Neither is
validation evidence.

## A10f (Claude, development calibration)

`a10f_development_calibration_20261108.json` places the real 1910–1959
development fit among the 360 A10d synthetic development fits: likelihood
ratio, β, lagged-mark bound status and M2 slopes for each case. It also gives
held-out confirmation among development-similar histories and real issue ages
(`scripts/a10f_development_calibration.py`). The script reads the retained
A10d trial records and the A10e development ledger, both outside Git, and the
committed A10e summary. It is not validation evidence and uses no 1960+ data.

## A04h (Claude, morphology only)

`a04h_morphology_targets_20261108.json` holds the real 1910–1959 target vector
and, for v2 and v3 in random and diverse cadence, the replicate means, SDs,
z-scores and Hotelling prediction p-values for the waveform and cadence blocks
(150 real-sized replicates each; `scripts/a04h_morphology_targets.py`).
`a04h_noiseless_geometry_20261108.json` gives noiseless decline-slope and peak
geometry against duration for v2 and v3 (`--geometry`). No recovery scoring.
