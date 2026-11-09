# Independent R2b execution audit

{
  "status": "passed",
  "absolute_tolerance": 1e-09,
  "counts": {
    "feature_checks": 88842,
    "transform_checks": 60,
    "objective_checks": 70,
    "prediction_checks": 98624,
    "zero_counterfactuals": 12328,
    "score_checks": 24348,
    "contrast_checks": 31308,
    "bound_checks": 24348,
    "saved_exact_identities": 358,
    "aggregate_checks": 2669,
    "H3_checks": 1724,
    "models_checked": 14,
    "H3_rows": 440
  },
  "maximum_absolute_errors": {
    "feature": 0,
    "transform": 8.881784197001252e-16,
    "objective": 9.094947017729282e-13,
    "prediction": 3.9968028886505635e-15,
    "score": 5.471179065352771e-13,
    "contrast": 4.076738946423575e-13,
    "bound": 3.552713678800501e-15,
    "aggregate": 7.230327447871332e-14,
    "H3": 2.6911806116913795e-13
  },
  "failures": []
}

No candidate functions imported. Direct Gaussian conditioning replaces the state recursion. See summary.json for hashes and limits.

## Local parameter lock

`parameter-lock-check.json` verifies ten source-order/hash conditions: the lock
was written before the frozen runner's evaluation score call; its final hash
matches the run receipt; model bytes match both lock and final receipt; all six
development feature/evidence files match their locked hashes; and parameters
are rechecked after evaluation. Parameter SHA-256:
`8c8c53a2602309a2d29d509b6fae60e2f94b11a62c6e051531ae42a1d8ae0630`.
This is local frozen execution provenance, not an external timestamp,
preregistration or filesystem immutability guarantee. The final receipt alone
would not establish an independent timestamp; the retained lock adds a local
stage artifact.

## Post-reconstruction interpretation notes

The numerical audit completed before reading the reported headlines/stability.

- H1 is +0.0075354 on 432 scored / 441 scheduled issues; H2 is +0.0042765 on
  431 / 440. Both six- and twelve-year intervals cross zero. H3 is −0.0030762
  on the matched supported population and also has intervals crossing zero.
- H2's deterministic sample bounds [0.0009703, 0.0077535] condition on A0/A1
  and the realized observation cutoff. They are not confidence limits or proof
  of the observation assumptions.
- The DF observing-rate proxy gains +0.0030435 with six-year interval
  [0.0012516, 0.0048355]. It is informative in this working comparison, but
  has no proved physical exclusion restriction. A physical-morphology or
  observing-response pathway remains possible; this is not a mechanism test.
- Adding c_end barely changes the DF B2 duration gain (+0.0042783).
- B2 meets its predeclared development multistart stability criterion, with
  all three starts successful and no reported parameter boundary. Its
  development NLL is nevertheless worse than B0/B1 (DF about 849 versus
  830/827; point about 948 versus 935/933). Describe B2 as the more elaborate
  preselected baseline, not the empirically strongest rule. No favorable
  rung or gain should replace the declared H1/H2 model.

No raw photometry was opened, no fit or simulation was rerun, and no execution
source or saved run artifact was changed. The actual-run audit directory is
new and distinct from the retained rehearsal audits.
