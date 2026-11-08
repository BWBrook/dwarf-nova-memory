# A10f: held-out evaluation of the frozen forecast system, SS Cyg 1960–2017

Claude, 8 November 2026. Status: **proposed for Codex review**. Opening the
block needs Barry's explicit go-ahead, recorded verbatim in
`coordination/decisions.md` before the first request. Reasons and evidence are
in the [A10f review](../audits/2026-11-08-a10f-development-review.md). The
protocol builds on A10c, [A10d](a10d-directional-oc-v1.md) and
[A10e](a10e-real-development-fit-v1.md).

This is the single confirmatory evaluation under D018. Opening the block
consumes its untouched status. Nothing in this protocol may change after the
first evaluation row is retrieved.

## 0. Frozen inputs

| Item | Identity |
|---|---|
| Forecast parameters | `data/fits/a10e_1910_1959/frozen_parameters.json`, SHA-256 `ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3` |
| Forecast, feature and extraction source | A10d freeze `8f5df44`, every byte listed in its receipt |
| Adapter and access guards | A10e freeze `b80c4a9`, extended only by the §6 runner |
| Extraction | X4 (`352a09e`), magnitude 10.0, C1/7 d coverage, `a10-prefix-v3`, rows with band `Vis.` and validation flag `V` only |
| Precision basis | A10d receipt `be0e25cd6d5432ca4cf3283991e698ca4b205c7424d16aff88e01abe02ae6f82` |
| Evaluation runner and checker | the §6 freeze commit, whose hash is recorded in the access decision before any request |

## 1. Access

1. **Log first.** Commit and push an outcome-access ledger entry and a
   decision recording Barry's go-ahead, the freeze hashes and this protocol's
   hash. Only then send any request.
2. **Request.** Use the same object (AUID 000-BCP-220), service and query form
   as the development acquisitions: `mtype=std`, the VSX object API, native
   XML.
   - Cover JD [2436934.0, 2458119.5) in windows of one calendar year or less.
   - The development requests stopped at JD 2436934.0. The half day before
     1960-01-01 is pre-1960 and enters only as prefix context.
   - Every window must end with a page shorter than the row cap, or be
     paginated until one is.
   - No request may reach JD 2458119.5.
3. **Receipt before parsing.** Hash each response. Record it in
   `data/manifests/acquisitions.csv` with its query, its time and the terms.
   Keep raw bytes under `data/raw/`, outside Git. The loader rejects any row
   at or after JD 2458119.5 and any quarantine path, as the development
   guards do.
4. **Observer identities.** Extend the anonymous identity cache by its
   existing deterministic rule and record the extended cache hash. Identities
   never enter Git.
5. **Sealed run.** One command runs every stage in order:
   - verify the receipts;
   - build the candidate and reference ledgers and evidence at both delays;
   - score the frozen models;
   - compute every §3–4 statistic;
   - write the outputs and a run receipt with UTC stage times.

   No evaluation row, count, plot or summary is inspected before the primary
   result file is written.

## 2. Forecast population

- **Issue times:** [JD 2436934.5, JD 2458119.5), that is 1960-01-01 to
  2017-12-31 UTC under the presumed convention. Latency 0 d is primary;
  2 d is a sensitivity.
- **Prefix context:** may use any row before the issue time, including
  pre-1960 rows within the 400 d lookback.
- **Outcome evidence:** uses only rows before JD 2458119.5. An outcome
  unresolved at that point is censored at the record end.
- **Rules:** ledger, coverage, mark and evidence rules are exactly the frozen
  ones. Ambiguous-survival evidence is excluded as in development. A
  nonpositive duration is a missing mark. Covariates are standardized with
  the frozen training centers and scales. There is no refitting, filtering
  or updating during the evaluation.
- **Concordance:** the candidate ledger is authoritative for scoring.
  - A candidate/reference mismatch does not stop the run. It is reported
    with counts and affected issuances, and a sensitivity drops those
    issuances.
  - Code may change after access only if a crash prevents scoring at all.
    Then a minimal fix that does not depend on outcomes is allowed. It is
    committed with its diff and reported prominently with the result.

## 3. Confirmatory test (D018)

- **Statistic:** the mean per-issuance M3−M2 log-score gain of the primary
  variant, over every score-eligible issuance, with fallback zeros included.
- **Clusters:** consecutive blocks of 6 × 365.25 d by issue time, anchored at
  JD 2436934.5, as in the frozen interval code. That gives nine six-year
  blocks and a final four-year block.
- **Interval:** cluster-robust standard error; Student t with nonempty
  clusters − 1 degrees of freedom.
- **Decision:** **confirmed** if and only if the one-sided 95% lower bound
  exceeds zero.
- **Report:** the estimate, SE, df, lower bound, two-sided 90% interval, the
  issued and scored counts, and the route counts.

This is the only confirmatory test. No other cluster length, variant, delay,
subset or window can replace it.

## 4. Secondary analyses and diagnostics (pre-declared)

- **S1, association:** refit on evaluation outcomes alone, unconstrained:
  - M2;
  - the current-duration offset;
  - the lagged-duration offset;
  - both offsets jointly on joint-valid rows.

  Report profile-likelihood support intervals. This is conditional
  association, not forecast skill. None of its forecasts enter §3.
- **S2, state sensitivity:** frozen β′ = 0, so frozen P3 is identical to M2.
  Report M3−M2 restricted to joint-valid issuances with the §3 method. The
  evaluation evidence on shared state comes from the S1 lagged and joint
  refits.
- **S3, robustness:** each variant uses its own frozen parameters and the §3
  method:
  - uniform-end marks;
  - the q-only baseline;
  - 2 d issuance delay;
  - type/within-type marks;
  - three-year clusters for the primary;
  - the concordance-mismatch exclusion, if needed.
- **S4, era split:** the primary gain for 1960–1992, which lies inside CM92's
  pooled sample, and for 1993–2017, which lies outside it. Each era uses
  6 × 365.25 d clusters anchored at its own start. This is descriptive.
- **S5, calibration:** for M0, M2 and M3:
  - mid-PIT deciles over interval-onset outcomes;
  - coverage of the central 50% and 90% predictive intervals, with each
    outcome classified as covered, not covered or undetermined;
  - held-out M2−M0 gain with the §3 method;
  - the evaluation mean and SD of standardized q, L and x, against the
    training values of 0 and 1.
- **S6, inventory:** issued, scored and routed counts and evidence reasons
  for each six-year block, reported after the primary result.

## 5. Interpretation, fixed before access

| Outcome | Statement |
|---|---|
| Confirmed | SS Cyg's outburst duration carries held-out forecast information about the following quiescent gap. The information is in CM92's direction, and adds to the previous gap and recent gap history in frozen visual-data extraction. This is a predictive claim, not a mechanism. |
| Confirmed, S1 lagged offset clearly positive and comparable to the current one | A slow shared state remains a live explanation alongside memory. |
| Confirmed, S1 lagged offset near zero while the current one is positive | Consistent with a within-cycle link: direct memory, or a common driver that decorrelates within a cycle or two. Timing alone cannot separate these. |
| Not confirmed, estimate > 0 | Inconclusive. The data are compatible both with a development-scale effect and with no gain. Power was about 27.5–33%. This is not a failed replication and not evidence of absence. |
| Not confirmed, two-sided 90% upper bound < 0.00452 nats | The data disfavour a forecast gain as large as the A10d injected effect, which was simulated at the published partial correlation. |
| Any outcome, S4 | The test of the sign is new to the literature only for 1993–2017. The test of forecast skill is new for all years. |
| Any outcome, S5 shows a miscalibrated M2 | The paired gain remains a valid comparison. Its size is specific to this frozen baseline. |

**Limits stated with every result:**

- The size evidence is a finite screen, not a certificate. Pooled gated
  nulls confirmed 3 of 220.
- Interval containment under the injected effect was 85%.
- The replay follows observation time, not operational availability.
- This is one star.
- The extraction was frozen on pre-1960 visual data.
- The development data overlap CM92's sample.

## 6. Pre-access work (Codex)

1. **Runner and checker.** An evaluation runner, and an independent checker
   that recomputes scores and §3 statistics from serialized forecasts without
   the candidate forecast code. Both are tested.
2. **Adapter fixtures.** Synthetic native rows carrying field values the
   development era lacked:
   - CCD and other non-visual bands;
   - validation flags other than `V`;
   - fainter-than rows;
   - time-reference tags;
   - comment codes;
   - duplicates;
   - JDs on both boundaries.

   They show that only `Vis.`/`V` rows enter and that nothing crashes.
3. **Rehearsal.** Run the full sealed command on a synthetic 1960–2017
   surrogate in native format, in a fresh namespace
   `a10f-rehearsal|<freeze hash>`. The independent checker must agree.
4. **Freeze.** Make the freeze commit and record its hash in the access
   decision. If Barry agrees, also tag the release and deposit it on Zenodo,
   which gives the preregistration an external timestamp. Then wait for the
   go-ahead.

## 7. After the result

- Report everything in §3–5 whatever the outcome.
- Post the result before any exploratory analysis. Later work on 1960–2017
  is labelled exploratory.
- 2018 onward stays reserved for replication with the same frozen system.
- The CM92 Table 4 reproduction may proceed once the result is sealed (D013).
