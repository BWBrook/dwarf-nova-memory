# A04e reviewed synthetic validation summaries

These are synthetic extraction results, not real-star forecast or association
results. Both global X3 coverage rules fail qualification; no extractor is
selected. See the [audit report](../../../docs/audits/2026-11-07-a04e-x3-independent-validation.md).

- `public_decision.csv`: all 24 decisive X3 cells (12 per global rule), with
  every frozen gate estimate, interval and verdict. `state_cadence_no_match`
  reports the diagnostic mean of `cadence_no_match_fraction`; it applies only
  to state cadence. False-plus-ambiguous causal emissions are the unsafe gate;
  pure false emissions are separately marked diagnostic.
- `public_diagnostics.csv`: 324 cells, including X1/X2, all thresholds and
  non-gating challenge arms. These additional criteria do not redefine which
  cells or candidates were decisive.
- `public_manifest.json`: completed counts, source/input/result hashes,
  global decisions and diagnostic ranges separated by candidate at magnitude
  10. The full metric/ledger hashes identify the ignored local payloads.
- `c1_7.svg`: the preferred rule's coverage, bias and first-signal criteria.
  All remaining gates, including unsafe emissions, are in the decision table.

The frozen summarizer's `smallpublicsummary.csv` is diagnostic only because it
omits the unsafe-emission gate. It is not used as the reviewed decision table.
The publication adapter copies the frozen full summary; it does not recompute
intervals or choose a different rule. Undefined estimates remain undefined.

Full run output, first-emission/pair ledgers and preview PNGs are regenerable
and excluded from Git. The reproduction commands require the retained local
input cache; the repository alone does not redistribute archive observations
or observer-level calibration inputs. Interval bounds are pointwise Monte
Carlo uncertainty under this synthetic benchmark, not real-star uncertainty.
