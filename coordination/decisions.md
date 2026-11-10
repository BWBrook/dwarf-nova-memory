# Decision log

The entries below document the seed author's choices. They are reviewable
proposals, not a record of approvals the user has not given.

| ID | Date | Choice and rationale | Status |
|---|---|---|---|
| D001 | 2026-11-05 | Frame the central contribution as incremental forecast information; old memory/correlation studies preclude a blanket first-discovery claim | Seed framing; revisit after full literature audit |
| D002 | 2026-11-05 | Start with ordinary dwarf novae and separate supercycles/standstills | Proposed scope |
| D003 | 2026-11-05 | Use subsequent quiescent gap, track shared endpoint uncertainty, issue forecasts only after observable completion | Proposed core definitions |
| D004 | 2026-11-05 | Use completed duration first, homogeneous optical fluence only if defensible | Proposed feature hierarchy |
| D005 | 2026-11-05 | Compare M0/M1/M2/M3; interpret M3–M2 as predictive, not uniquely mechanistic | Proposed model ladder |
| D006 | 2026-11-05 | Begin on a laptop with a small audit; expand only after feasibility and recovery | Proposed workflow |
| D007 | 2026-11-05 | Ship only synthetic runnable examples; real data and complex inference remain future work | Seed implementation boundary |
| D008 | 2026-11-05 | Preserve all eligible issued forecasts, including censoring; do not require a future completed-test count to enter sample | Proposed evaluation invariant |
| D009 | 2026-11-05 | No public licence or remote chosen; supplied Git commit has a neutral assistant author | Superseded by D011 |
| D010 | 2026-11-05 | Keep literature access depth and unknown validation details explicit, including recent precursor work | Evidence rule |

### D011 — Public repository, licences and board

- Date and decision maker: 2026-11-07, Barry W. Brook. In chat to Claude on
  7 November 2026: "Create a Git commit and a remote public repo on BWBrook
  GitHub." His standing open-by-default policy (2 November 2026) sets the
  licences: MIT for code, CC BY-SA 4.0 for text, figures and data.
- Evidence and alternatives considered: the seed left licence and remote open
  (D009). Barry's policy keeps work private only by exception; none applies.
- Choice and scientific consequence: public at
  `github.com/BWBrook/dwarf-nova-memory`; `LICENSE` (MIT) and `LICENSE-CONTENT`
  (CC BY-SA 4.0) copied from `BWBrook/open-repo-template`, with its gitleaks
  workflow. The seed commit and `seed-v0.1.0` tag are preserved unchanged.
  Third-party observations keep their own terms; raw exports stay out of Git
  until redistribution is checked. Agent discussion moves to the
  `dwarf-nova-memory` board section, exported as reviewed snapshots.
- Affected files and analyses: `README.md`, `AGENTS.md`, `LICENSE*`,
  `CITATION.cff`, `.gitignore`, `.gitleaks.toml`, `.github/workflows/gitleaks.yml`,
  `docs/correspondence/`; `LICENSE-DECISION.md` removed.
- Was evaluation data inspected before this choice? No real data exist.
- Status, review and conditions for revisiting: in force.

### D012 — Protective outcome-access boundary before acquisition

- Date and participants: 2026-11-07, proposed by Claude (board message 2920),
  boundary accepted by Codex (message 2924). This is an agent access restriction,
  not approval attributed to Barry or a final analysis protocol.
- Choice: development observations must precede 2018-01-01 00:00 UTC
  (JD 2458119.5 in that convention), for all pilot/reserve/challenge targets.
  Keep later observations reserved. Prefer date-restricted retrieval; any
  necessary full export must be partitioned before analyst inspection.
- Refinements: verify native time conventions; seal reserved counts/coverage;
  test loader paths and row times; leave boundary-crossing events unresolved;
  log releases and prior knowledge. See
  [the access ledger](../docs/outcome-access-ledger.md) for the proposed mechanics.
- Alternatives: a later or target-specific cutoff could expose more development
  material, but has not been chosen. No reserved coverage has informed this choice.
- Affected files: `configs/study_plan.json`, `docs/outcome-access-ledger.md`,
  `coordination/board.md`; future archive adapters must enforce the policy.
- Was evaluation data inspected? No real project photometry has been acquired.
  Known SS Cyg 2021 and RU Peg literature context is disclosed in the ledger.
- Status: conservative boundary in force. Codex's implementation refinements
  were reviewed and accepted by Claude on 2026-11-07 (A01 memo §6.6). The A01
  power interpretation is corrected by D013: neither sign/calibration
  confirmation nor detection power has been established for the locked block.
  That belongs in the evaluation protocol (A10), not here. No loader exists yet. Final evaluation and prospective
  forecasting remain proposals; A03 follows A01/A02 and access-policy review.

### D013 — SS Cyg tuning access and candidate historical evaluation

- Date and participants: 2026-11-07. Claude proposed 1896–1959 tuning and
  1960–2017 evaluation in A01 / board message 2931. Codex accepts the protective
  split **with amendments**, before any project photometry request. This does
  not approve a final model, power claim, sample size or paper scope.
- Access now: only SS Cyg observations before 1960-01-01 00:00 UTC are open for
  extraction development, annotation, coverage diagnostics and tuning. First
  acquisition will request a small 1956–1958 interval. Preserve native time
  metadata; unresolved conventions cannot be silently relabelled UTC.
- Keep 1960–2017 reserved as a **candidate project-time raw-data evaluation**
  block, and keep 2018 onward reserved under D012. Prefer date-restricted
  acquisition. Do not plot, annotate, count events or summarize coverage in
  either reserved block before a documented release. No 1960+ raw data have
  been inspected or retrieved by this project at this decision.
- Freeze extraction, eligibility/coverage rules, model candidates, selection,
  hyperparameters, score, horizons and update schedule before opening the
  candidate evaluation block. Prespecified online refitting/filtering may use
  only past information as evaluation progresses; model retuning may not.
- **Resolve the A01 sequencing conflict:** pre-1980/2010–2017 double annotation
  and a full 1896–1992 CM92 Table 4 reproduction cannot precede that freeze
  while retaining 1960–2017 as uninspected project data. Develop only on the
  open era and simulations. Defer the full reproduction until forecasts and
  primary evaluation are sealed. If later-era data are opened for feasibility,
  explicitly designate the opened block exploratory and amend the remaining
  evaluation before access; never restore its untouched status.
- Literature exposure: CM92 (1896–1992) and Price et al. (through 2006) have
  already influenced this design. The access ledger also records Codex's
  direct inspection of CM92 pages 645, 647 and 650 and incidental historical
  classifications in a search result. This is a literature-informed split,
  not universal ignorance of the evaluation outcomes.
- Arithmetic: partial r = 0.130012289; ideal Gaussian conditional information
  = 0.008523842 nats. About 470 forecasts makes `2*n*gain` about 8; that is
  **not** a detection guarantee or a powered sample-size calculation. Real
  score-comparison power, dependence, missing events and parameter estimation
  require simulation after development. Neither 55 nor 400 usable forecasts
  have been established. Do not promise that a small block confirms sign or
  calibration, or that richer adjustment necessarily reduces a correlation.
- Review: Claude accepted the amendments on 2026-11-07 (A04 memo §1) and
  proposed for A10 that the sealed block's pre-registered confirmatory
  quantity be the frozen-specification duration coefficient, with the
  out-of-sample score difference as the skill estimate. The proposal also
  notes that CM92 already pools 1960–1992. Not decided.
- Subsequent review: Codex's A04 audit (`8bb21cb`; board message 2948) advises
  retaining forecast gain/calibration as primary predictive quantities and
  treating a prespecified coefficient/LR test as secondary association evidence.
  The two ideal power calculations do not choose between these estimands.
  CM92's pooled 1896–1992 table includes 1960–1992; it does not establish the
  sign in that subperiod separately. No primary-outcome change is adopted.
- Resolution: Claude withdrew the primary-outcome switch in board message
  2952 (A04b §4). Paired forecast gain, calibration and intervals remain the
  primary question. The eventual freeze must quantify achievable precision;
  no forecast-model or evaluation protocol has yet been frozen.
- Status: protective restriction in force; final evaluation suitability and
  operating characteristics remain unresolved. A03 may proceed only within the
  open interval. A01's later-era annotation, reproduction and power proposals
  are superseded by this decision where they conflict.

### D014 — Conditional injection/recovery screen before extractor selection

- Date and participants: 2026-11-07. Claude proposed the screen and criteria
  in A04b §5; Codex completed its implementation in the pre-run
  [A04c protocol](../docs/protocols/a04c-injection-recovery-v1.md), `c2f6eed`,
  with guard completion and harness in `3bb2237`.
- Preserve X1/X2 unchanged and test synthetic truth at pre-1960 cadence.
  Random renewal is the independent null. Fixed-onset alignment imposes
  Q=C−D and is a sampling diagnostic only. Copula .13 is a latent-scale
  target; recovery uses each replicate's raw-scale oracle.
- Retain the proposed 90% boundary coverage, 95% short-event completeness,
  <0.2 false events/year and |null association bias|<0.02 criteria, with
  replicate-level Monte Carlo intervals and explicit undefined results.
  No extractor must win. Any post-screen repair needs fresh seeds and a
  new specification; this screen cannot authorize evaluation-block access.
- X1-conditioned calibration and fixed observing times limit generality.
  C2 measures observation opportunity, not detection probability. No fitted
  censoring-aware forecast model or real-data association is part of this work.
- Status: 3,200-history screen complete; both candidates fail qualification
  across the required strata. X1 conditionally undercovers; X2 loses effective
  coverage through non-unique/nonfinite matches. The 1950s null-bias margin is
  inconclusive. No candidate selected or frozen. See the A04c report for
  conditional coverage and observation-model limitations; any repair needs a
  separate calibration batch and fresh validation seeds.

### D015 — Independent X3 benchmark and causal confirmation validation

- Date and participants: 2026-11-07. Claude proposed X3 and a replacement
  benchmark in A04d. Codex reviewed and amended that proposal, with an
  independent source audit, before new recovery outcomes.
- Choice: replace the threshold-kinked original waveform as the primary
  qualification benchmark, while retaining its known failure as a reported
  misspecification challenge. Use an independently authored curved generator,
  finite morphology-only calibration and fresh qualification before recovery.
  Matching selected X1-conditioned summaries is not physical validation.
- Freeze: `2f7a7eca4ece7a7702fb429ec5bb4a94a2bc57d1`, the
  [A04e protocol](../docs/protocols/a04e-x3-independent-validation-v1.md),
  fixed inputs and parameters. X3 remains byte-identical to `c0353c0`.
  Both the initial `3ad0939` and amended final-hash morphology qualifications
  passed and are retained. No candidate-validation result preceded the
  amendment; parameters and generator were unchanged.
- Causal safety: X3's final confirmation can erase an earlier emission, so
  its batch field cannot establish the premature-confirmation criterion.
  Test a separately specified permanent-emission wrapper. Count ambiguous
  alongside false emissions in the <0.2/year gate; retain both separately.
  Final endpoints are not thereby established as available at emission.
- Decisive grid: independent and structured zero-mark controls, three eras,
  both cadence phases, 400 histories each. Require one global coverage rule
  to clear all twelve cells, with frozen Monte Carlo intervals and no
  per-cell switching. Preserve alternative, persistent-offset, original-v1,
  threshold and early-era diagnostics. Total: 7,600 histories, 79,200 rows.
- Evaluation boundary: no reserved photometry or real duration–following-gap
  association is part of A04e. A passing result would qualify only synthetic
  retrospective extraction within the tested envelope. A10 additionally
  needs causal features, positive-control recovery and achievable precision.
- Status: final morphology qualification passed; all 7,600 recovery histories
  completed with 79,200 rows and no extraction exceptions. Both global rules
  fail X3 qualification. State-compatible effective coverage fails in the
  1930–1949/1950–1959 cells; 1910–1929 unsafe-emission rates are inconclusive.
  All twelve C1 paired null-bias checks pass, and the original-v1 end failure
  is reproduced. No extractor selected. Results do not authorize A10 or
  reserved-data access. See the
  [A04e report](../docs/audits/2026-11-07-a04e-x3-independent-validation.md).

### D016 — Fresh X4 validation with qualified observer diversity

- Date and participants: 2026-11-08. Claude proposed A04g; Codex completes it
  with candidate-blind waveform/cadence construction, independent causal
  reimplementation and a bounded independent design/source-chain audit.
- Keep X4 byte-identical to `352a09e`, and preserve the A04e failure. Qualify
  both v2/v3 repaired diverse arms under the original 15% median and 0.05
  low-diversity-share tolerances. Do not widen those bounds. Random cadence
  remains a conservative mandatory recovery control with its known observer
  mismatch disclosed, not an empirically diversity-qualified arm.
- The cadence uses whole donor blocks matched on calendar span, season and
  epoch. Original and additional donor-missing days remain missing. Early
  failed waveform/cadence specifications and morphology-only pilots are
  preserved in Git; no X4 outcome informed their repair.
- Calibration: 27 predeclared v3 configurations, two histories per era/phase,
  source `28741bc`; only index 23 passes. V2 parameters are unchanged. Fresh
  qualification is fixed at 32 histories per era/phase/family before any
  qualification outcome. Failure stops recovery with validation seeds unused.
- The gross-error arm uses a 0.32% quiet observer-night contamination budget,
  with persistence included. It is a stress intensity, not an identified
  wrong-star probability. False/ambiguous causal signals and retrospective
  false episodes are its only decisive outcomes.
- Recovery criteria and Monte Carlo conventions remain A04e's. Prespecify
  16,600 histories, 51,800 rows, 24 ordinary and six gross-error decisive cells
  per global rule. Prefer C1 only if every cell passes; otherwise C2 only if
  every cell passes. A passing extraction screen does not freeze A10 or open
  reserved data. The
  [completed protocol](../docs/protocols/a04g-x4-independent-validation-v1.md)
  and [A04g report](../docs/audits/2026-11-08-a04g-x4-independent-validation.md)
  state exact scope and residual assumptions.
- Status: final freeze `b83d76a`; all 384 fresh qualification histories
  completed. V2 and repaired observer diversity pass. V3 diverse fails the
  slope–duration rho gate (−0.110 versus real +0.045; difference 0.155
  exceeds 0.15). Benchmark not qualified; X4 recovery not run and its
  validation namespace unused. No tolerance widening, extra seeds or
  variance search follows this failure. Independent review supports closing
  this version and a separately specified joint morphology design next.

### D017 — Joint waveform/cadence gate and bounded A04i validation

- Date and decision maker: 8 November 2026, Codex, responding to Claude A04h.
- Evidence and alternatives considered: A04h's new amplitude/duration and
  end-phase sampling discrepancies, independent predictive-gate audit and
  corrected same-era feature operator. Dense sampling can narrow fitted
  crossing intervals; undersampling ends cannot be assumed conservative.
- Choice and scientific consequence: require both the eight-feature waveform
  and four-feature cadence blocks, plus per-era observer diversity, before
  X4 recovery. Keep blockwise normal-reference p ≥0.01 and raw |z| ≤3.3;
  assert no overall 1% rejection rate. Same half-open era extraction gives
  334 real feature episodes, replacing the mismatched 335-episode target
  only for this version. Preserve the earlier result.
- Permit one fixed ten-configuration grid (one unchanged v2 plus nine v4
  waveform settings, fixed phase policy). Sixteen real-sized calibration
  vectors per configuration choose the minimum mean-discrepancy objective
  using pre-existing fixed v2-random spreads. No covariance/variance search.
  Freeze winners and the input/calibration hash chain before 150 fresh
  qualification vectors per pair. Drop failing pairs before recovery; run
  X4 on every eligible pair and retain all outcomes. If no pair qualifies,
  stop with X4 unscored. No second grid or tolerance widening this version.
- Affected files and analyses: `configs/a04i_*`, new waveform/phase modules,
  pipeline, predictive gate and joint-recovery scripts; full specification
  in `docs/protocols/a04i-joint-validation-v1.md`. X4 bytes unchanged.
- Was evaluation data inspected before this choice? No 1960+ data, new
  qualification or X4 recovery outcomes. Open-era morphology, separate D/Q
  marginals and earlier failed benchmarks informed this design. No real
  duration–following-gap correlation was computed.
- Status, review and conditions for revisiting: pre-execution decision;
  independent construction and bounded integration review. Compatibility
  remains conditional on fitted families and selected features. A04i does
  not freeze A10 or authorize reserved-data access.
- Execution: source `036c619`, evaluation freeze `939ea77`. One calibration
  grid selects v2-00/v4-05; all 900 fresh qualification histories complete.
  Independent R reproduces v2-phase as the sole eligible pair. Unchanged X4
  completes 4,800 histories and passes both global rules at magnitude 10;
  select C1/7 d by the predeclared preference. Magnitude-9.5 diagnostics fail
  in later eras and some alternative-bias intervals remain inconclusive.
  This is a conditional retrospective qualification on a previously studied
  waveform, not successful unseen-waveform or operational validation.
  Independent base R reproduces all 108 decisive metric estimates/intervals/
  statuses and both global decisions (maximum difference 6.66e−16), while
  independent integrity checks reconcile counts, keys, seeds and hashes.
  C2's structured-1950s bias upper limit 0.01929 is near the 0.02 bound;
  the preferred C1's corresponding global margin is wider. This last audit
  does not re-derive individual photometry-to-score calculations.
  Full result and limits: `docs/audits/2026-11-08-a04i-joint-validation.md`.

### D018 — Forecast gain remains confirmatory

- Date and decision maker: Barry, 8 November 2026, current chat response to
  Codex's question distinguishing predictive gain from a model coefficient.
  Exact selected reply: **“Forecast gain confirmatory (recommended)”**.
- Evidence and alternatives: A10a's Gaussian power calculation (about 32%
  score-test versus 77% coefficient-test power at r=0.12 and 390 forecasts)
  checks numerically. These are tests of different estimands. A coefficient
  fitted on evaluation outcomes is conditional association under a frozen
  specification, not a more powerful test of frozen forecast improvement.
- Choice: held-out M3–M2 forecast gain stays confirmatory, with its interval
  and expected precision; duration coefficients remain secondary. A weak
  result must not be interpreted as evidence of no predictive information.
- No reserved observations or real duration–following-gap association were
  accessed before this decision. A10 remains unfrozen.

### D019 — A10b ledger repairs and synthetic model-development envelope

- Date and decision maker: Codex, 8 November 2026, review of A10a at `5476d00`.
- Accept the magnitude-10/C1 retrospective extraction definition and unchanged
  X4 bytes at `352a09e` as the A05 reference. This does not certify an
  operational extractor or open any protected block.
- Prefix causality does not eliminate measurement-induced forecast information:
  shared end/age error can make a measured mark useful with constant true
  duration. The independent six-state example is retained. A10a's claim that
  waveform errors can only dilute skill is withdrawn for subsequent work.
- Repair issue-window filtering, overtaken onset assignment, coverage holes
  spanning issue, ambiguous survival and training-label cutoff leakage in
  `a10-prefix-v2`. Keep issued forecasts and explicit common exclusions;
  train only on newly extracted as-of evidence, including right censoring.
- Implement conditional M0–M3 plus common unknown-anchor R0, a shared-end
  sensitivity and type/within-type diagnostic. These are statistical
  prototypes, not an identified observation/latent-state likelihood.
- Freeze source before 100 independent short-history ledger/evidence
  comparisons at both latencies, then the fixed 56-trial synthetic development
  grid. Full specification: `docs/protocols/a10b-model-controls-v1.md`.
  Preserve failed fits and all controls. No production scores before the
  exact concordance set passes. Small trial counts do not establish final
  operating characteristics; stronger timing-only baselines, coarsening,
  complete measurement propagation and inference calibration remain A10 work.
- No raw archive access, real focal correlation, other-star acquisition or
  reserved data is part of this envelope. Barry's D018 decision is independent
  of control outcomes. An additional generator-tuning cycle is not authorized
  by this specification.
- Runtime repair: stop the initial implementation after the independent
  replay identifies nonpositive duration support in a marginal-end mixture.
  Preserve 17 completed records (8 successful, 9 failed), 39 uncompleted tasks
  and 12,408 scores as an aborted/incomplete run. Treat duration as missing
  across the whole mixture if any node is nonpositive; preserve M0/M2 timing
  and the declared mark fallback. Record geometry diagnostics. Re-freeze,
  repeat concordance, and replay all 56 tasks using the original control
  random streams. No generator, model coefficient or favorable seed is tuned.
- Execution: repaired freeze `4fc8d2e` completes all 56 trials, 105,509 scored
  variant-issuances and 1,360 fits after fresh exact concordance. Independent
  arithmetic and aggregate checks pass. The injected-effect prefix gain is
  0.00324 nats/forecast (trial SD 0.00321); all eight individual diagnostic
  intervals include zero. This is a development result, not final power or
  real-star evidence. Strict oracle matching, rare point-order failures,
  stronger timing-only comparisons and coarsening/inference calibration
  remain for A10. The L2 variant delays issuance, not training evidence.

### D020 — Directional, matched M3 and the A10c development path

- Date and decision maker: Claude, 8 November 2026, review of A10b at
  `7d2ec3b`. Proposed for Codex review. D018 is unchanged: held-out M3−M2
  forecast gain stays confirmatory and the coefficient secondary.
- Evidence: a re-aggregation of the retained A10b scores by forecast route.
  - On forecasts without a covered previous gap, M3−M2 compares M1 with M0.
    That route supplies 0.0011 of the 0.0032-nat injected-effect gain, and
    covers 8.5% of forecasts (48% under adaptive effort).
  - Fitted duration coefficients are negative under every null case
    (−0.014 and −0.018 per SD), while the magnitude-10 truth has r = −0.005.
    This is the shared end-error coupling, which enters with a negative sign
    in the measured-gap frame.
- Choice:
  - Duration enters M3 only where M2's covered previous gap does.
  - The duration coefficient is bounded at β ≥ 0, with M3 nested in M2.
  - The comparator adds a local gap level.
  - Point marks are primary. Uniform-end marks, the A10b comparator, the 2 d
    delay and the type/within-type mark are sensitivities.
  - A lagged-duration placebo (P3) is the memory diagnostic.
  - The oracle is a diagnostic only.
  - A point duration ≤ 0 makes the mark unavailable.
  - On the A10b scores this design gives −0.0002 nats under the independent
    null and +0.0023 under the injected effect.
- Next:
  - a 360-trial operating-characteristic study, with two slow shared-state
    nulls and gating criteria;
  - then the real 1910–1959 fit, the first real duration–gap computation;
  - then the evaluation protocol;
  - then Barry's go-ahead before any 1960+ access.

  Specification: `docs/protocols/a10c-development-fit-v1.md`.
- No real observation, reserved data or real duration–gap association was
  accessed. A10 remains unfrozen.

### D021 — A10c review amendments and the A10d calibration implementation

- Date and decision maker: Codex, 8 November 2026, review at `c9aab07`.
  Implements the user's requested direction/matching changes; D018 stays
  forecast gain. D020 is accepted subject to the amendments below.
- A nonnegative coefficient is a directional restriction, not an error-sign
  theorem. An independent late-age exact construction with constant true
  duration yields positive information and a positive fixed-baseline interval-
  score offset (β=0.24254, gain 0.08375 nats). It is not an SS Cyg bias estimate.
- A current mark can beat a lagged mark under a pure slow shared state. P3
  and M3−P3 are state sensitivities, not identification of direct memory.
  λ²=.13 is retained as marginal latent-rank correlation, not a partial target.
- Fit/freeze M2 on timing-eligible rows; fit only mark offsets on their valid
  rows, with literal M2 fallback. This reconciles the deployed training loss
  and gives exact β=0 nesting. M0/R0, q-only, uniform-end, delayed-issuance
  and type/within-type diagnostics are retained; no M1 contrast is used.
- `a10-prefix-v3` adds previous duration and six earlier gaps. Independent
  reference construction, exact-window indexing and full-gap coverage checks
  precede fresh 100-history qualification. Development checks are separate.
- Choose six-year clusters before OC outcomes, with three-year sensitivity.
  Use six independent matched 58-year reference replicas (348 source years)
  rather than an unequal-mixture 300-year run. Propagate reference uncertainty
  and distinguish exact-zero and interior calibration.
- Gate policy clarification is pending Barry's response to the question posed
  before outcomes: observed rejection rate ≤.05 in each relevant null as a
  finite screen, or formal upper-bound certification requiring larger counts.
  The ambiguous two-MC-SE rule is not used. Both decisions are computed, and
  no real fit occurs automatically or on an unresolved gate interpretation.
- Scope: exactly the requested 360 fresh synthetic trials and frozen inputs;
  no generator/model/inference retuning after results. First real development
  fitting remains behind the approved gate. No 1960+ access.
- Outcome: freeze `8f5df44` completes 360/360 without failures and passes the
  declared finite observed-rate/joint-MC screen. All six gated null rates are
  ≤.05; injected-effect power is 11/40 (27.5%). Joint-MC containment is 37/40
  null and 34/40 alternative, with interior checks retained. Independent
  aggregate and representative numerical audits agree. Formal size
  certification fails as anticipated from the fixed counts. The gate-policy
  question remains unanswered, so no real fit is made. See the A10d report.

### D022 — Barry accepts the finite OC screen; first real development fit authorized

- Decision maker and date: Barry W. Brook, 8 November 2026, direct reply to
  the pre-outcome gate question, received after the A10d reporting commit.
- Exact selected answer: “360-trial screen with observed rate ≤5%
  (recommended)”. The question explicitly stated that passing permits the
  pre-1960 fit but does not certify a true five-percent error rate.
- The accepted screen passed in freeze `8f5df44`: all 360 trials complete,
  every gated null observed rate ≤.05, and the predeclared finite-reference
  calibration checks pass. D021's pending interpretation is resolved; its
  formal-certification alternative is not adopted.
- Execute the first 1910–1959 development fit under
  `docs/protocols/a10e-real-development-fit-v1.md`. Freeze adapter/profile
  sources first; require all A10d model/feature/extraction bytes unchanged.
  Native acquisitions must retain their twelve accepted hashes and strict
  pre-1960 scope. Publish frozen parameters and diagnostic likelihood
  profiles, labeled according to their conditional support interpretation.
- D018 remains held-out forecast gain. This opens no 1960+ observation,
  coverage summary or evaluation block. No native record or real association
  was inspected between receiving this answer and recording this decision.
- Execution outcome: A10e adapter freeze `b80c4a9` completed all six real
  development fits and diagnostic profiles on 330 issuances. Primary
  β=.04660; P3 at zero. Parameters SHA-256
  `ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
  Qualified forecasting bytes are unchanged. No post-fit model change or
  1960+ access occurred. D018 has not yet been evaluated on held-out data.

### D023 — A10f review accepted; evaluation protocol proposed

- Date and decision maker: Claude, 8 November 2026, reviewing A10d
  (`8f5df44`) and A10e (`b80c4a9`) at `ccea39b`. Proposed for Codex review.
  Opening 1960–2017 still needs Barry's explicit go-ahead.
- Accepts D021's amendments. These are: fixed-M2 offset fitting, six-year
  clusters, matched reference replicas and the finite screen (D022). Claude
  withdraws the A10c claim that β ≥ 0 removes measurement artefacts in
  general.
- That claim does hold for the real issuance regime. The median issue age is
  1.9 d (90th percentile 4.0 d, 7/330 above 10 d) against a median previous
  gap of 40 d, so the coupling is negative there.
- Development calibration (`scripts/a10f_development_calibration.py`):
  - The real in-sample LR of 5.19 is reached by 5/220 gated null histories
    (0/40 structured), 12/40 injected-effect and 14/80 slow-state histories.
  - Among histories with a moderately strong M3 (LR ≥ 2.71), the lagged
    offset sits at zero in 11/21 injected-effect and 2/31 slow-state
    histories. A slow shared state of the simulated kind is disfavoured;
    mechanism is not identified.
  - Conditional power is 4/12 (v2) and 0/5 (v4).
- Because frozen β′ = 0, frozen P3 equals M2 on the evaluation block. State
  sensitivity there comes from the unconstrained S1 refits.
- Proposed protocol: `docs/protocols/a10f-evaluation-v1.md`. It sets out:
  - logged and sealed access to JD [2436934.0, 2458119.5);
  - the single six-year-cluster test;
  - the S1–S6 analyses and the fixed interpretation table, including an
    informative negative below 0.00452 nats and the 1960–1992/1993–2017 CM92
    split;
  - the pre-access runner, fixtures and rehearsal;
  - optional Zenodo preregistration.
- No 1960+ data accessed. The development ledger (pre-1960, consumed) was
  read for issue ages only. No forecasting code changed.

### D024 — Pre-access evaluation implementation and A10f review amendments

- Codex, 8 November 2026, reviewing A10f at `31ddd21`. D023 is accepted
  subject to these explicit pre-access amendments. D018 and all frozen
  forecast parameters/extraction/feature bytes remain unchanged.
- Require exact candidate/reference ledger AND evidence concordance before
  scoring. A mismatch aborts and preserves the run; remove candidate-authority
  and mismatch-deletion replacement rules.
- Implement the genuinely simultaneous two-offset S1 diagnostic, holding the
  same evaluation-only M2 fixed. The old `joint_marks=True` API fits separate
  offsets on common rows and is not that model. Joint rank deficiency and
  conditional-profile limits are explicit.
- Resolved-onset mid-CDF deciles are descriptive under selection. Coverage
  uses definite-covered/not-covered/undetermined classifications and partial
  identification bounds over all scored issuances, including right censoring.
- The six-year sign test stays exactly fixed. Comparison against numerical
  reference gain .004519560867443926 is a separate descriptive magnitude
  field, not a physical-r test or a replacement confirmation rule. Do not
  label every positive nonconfirmation compatible with that reference.
- Median observed issue age does not bound end-error/current-gap selection
  terms. Shared-seed 5/220 and 3/220 counts are descriptive, not iid binomial
  probabilities. The sparse conditional lag-zero ratio8.12 is not model odds.
- Receipt-before-parse bounded annual requests use finalendpoint strictly
  before2018, capped-response bisection, private identities and immutable
  source/parameter proofs. Live transport requires a committed verbatim Barry
  authorization matching freeze/protocol/parameter hashes and timestamp route.
- Authority: build/test/rehearse/freeze now. No1960–2017 archive access or
  Zenodo protocol deposit is yet approved. No2018+ request is permitted.
  Full protocol: `docs/protocols/a10g-sealed-evaluation-v1.md`.

- Rehearsal implementation correction: source freeze79b5eae completed the
  synthetic58-year primary and independent audit, but discarded R0/M0
  profiling aborted the whole S1 diagnostic. Synthetic-only diagnosis found
  required M2/M3/P3 and joint profiles succeed; no likelihood pathology or
  identification failure explains the discarded-model numerical status.
  Restrict the evaluation-only profiling call to emitted models, preserving
  every optimizer success criterion and all26 original source identities.
  Record the first run, create a new freeze/namespace, and rerun the full
  synthetic rehearsal before asking to open the later block.

- The second synthetic freeze bfb2bc6 independently passes primary scoring
  but exposes the same finite-difference line-search failure in required
  joint profiles; Linux3.11 CI also exposes it in M2 nuisance profiling.
  Adopt one evaluation-only nuisance method by dimension: bounded scalar
  with both endpoints for1D, L-BFGS-B with three-point gradients for2+D.
  Success, bounds, recomputed objective, nesting and material-improvement
  checks remain strict. No status-based retry or primary-estimator change.
  Verify analytic fixtures, the platform-exposed fixture and both preserved
  histories before the final new source/seed freeze. This amends only S1
  numerical profiling, before any later archive request.

- Execution outcome: final source freeze `fc40973` completes the full
  synthetic native-format 58-year rehearsal, every named secondary and the
  independent 2,230-row numerical audit. Both earlier attempts remain
  preserved, with their failures and separate hashes. All 342 tests,
  validator, staged scan and Python 3.11–3.13 CI pass. Parameter bytes and
  all 26 original sources remain fixed. A 697,603-byte protocol-only bundle
  and verified metadata are prepared, not deposited. Final evidence:
  `docs/audits/2026-11-08-a10g-evaluation-freeze.md`. D024 does not open the
  real evaluation block; Barry's timestamp/access decision remains pending.

### D025 — Barry authorizes Zenodo timestamp, then the sealed evaluation

- Barry W. Brook, 8 November 2026, answering the A10g access choice after
  report `b56abfd` and reviewed snapshot `7b0eb3b`.
- Verbatim selected answer: “Zenodo first, then open (recommended)”.
  The question explicitly specified publishing the prepared 0.7 MB
  protocol-only package first, then running the single sealed 1960–2017
  evaluation; 2018 onward stays closed.
- Publish the exact reviewed protocol package, SHA-256
  `9cc7c7e7203619fbb4322f43b9af6e7207b59644367b06434673be555b9cd357`,
  with checked creator metadata. Source freeze is
  `fc409738222ded5a9bf78288c969e956b59d23f4`; protocol SHA-256
  `ddfa46d14f35e213690e0d5e7d03a7a635a71b637d024a810d2f192929789232`.
  Forecast parameters retain SHA-256
  `ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
- After publication, record its DOI and this verbatim authority in the
  tracked access file, commit and push before native access or transport.
  Run the unchanged sealed command once; no pre-primary observation,
  coverage or result inspection is permitted. All mismatch/failure rules
  and the single six-year-cluster confirmatory test remain unchanged.
- No real evaluation archive has been opened at this decision checkpoint.
  This authorizes no 2018+ request, raw-data release or manuscript release.

- Protocol published before evaluation access as
  [10.5281/zenodo.24053338](https://doi.org/10.5281/zenodo.24053338), created
  2026-11-08 12:34:47 UTC. API reports submitted/done; unauthenticated public
  download SHA-256 matches the exact approved bundle. The public receipt is
  `data/provenance/a10g_protocol_package/publication.json`. The DOI-bound
  authorization is `coordination/evaluation_access.json`; this commit and
  push precede live transport. No evaluation observation/count has yet been
  accessed. The DOI identifies the frozen protocol, not an analysis result.

### D026 — Outcome-independent post-access native-format repair

- Codex, 8 November 2026, under the repair clause of the already authorized
  A10g protocol/D025. This is a bounded implementation repair, not a new
  scientific specification or a renewed claim of untouched evaluation data.
- First live attempt: source `fc40973`, authorization `6e26eba`, acquisition
  began 12:38:28 UTC and failed at 12:39:51 before ledger construction or
  any primary score. The native uncertainty field contained literal `None`,
  rejected by the numeric validator. Responses/receipts/log are retained;
  the append-only acquisition manifest records each completed request.
- Accept only exact blank or exact `None` as missing uncertainty metadata,
  preserving the raw string. Do not turn it into zero, drop an observation,
  accept padded/case aliases, or relax numeric invalid/nonfinite/negative
  checks. The sentinel interpretation is inferred from representation; its
  downstream non-use makes it immaterial to the forecasting estimand.
- Independent methodological code-path and synthetic-fixture review finds
  uncertainty unused by selection, extraction, causal emissions, candidate
  and reference features/evidence, routes and scoring. The persistent
  regression compares blank/None forecasts, outcomes and frozen scores.
- No outcome, event count, coverage summary or real coefficient informed the
  repair. The block's untouched status is consumed. Preserve the failed
  attempt and publish its failure receipt; label the continuation and every
  resulting claim as the frozen test after a post-access format repair.
- Freeze the narrow parser/test diff, run a fresh synthetic namespace and
  independent checker, then commit/push an updated authority citing this
  permitted repair before continuation. All original 26 forecasting source
  files, parameter bytes, protocol bytes and the confirmatory test remain
  unchanged. D025's Zenodo-first condition is already met; no new protocol
  DOI will be portrayed as predating this access. No 2018+ request is allowed.

- Repair source freeze `5e39aeb772c427ef29671c1a9c80b22c05519b58` passes
  all 344 tests, validator, staged scan and Python 3.11–3.13 CI. Its fresh
  synthetic full rehearsal completes every diagnostic, with an independent
  score/interval audit (max score discrepancy2.94e-14). The repair-bound
  access file explicitly retains the original approval/freeze, failure and
  consumed status, and cites the existing protocol repair clause. Commit and
  push this record before the labeled post-access continuation.

### D027 — Record the frozen forecast-gain result and its narrow interpretation

- Codex, 9 November 2026 (Hobart), after completed execution under D025/D026
  and independent numerical, acquisition and methodological review.
- Primary: 441 issuances, mean M3−M2 gain 0.0165335122 nats; six-year-cluster
  SE 0.0063202848, one-sided 95% lower 0.0049477163; two-sided 90% interval
  [0.0049477163,0.0281193080]. Ten blocks, 9 df. The single predeclared rule
  is met. All five fallback zeros remain; no excluded/ambiguous-survival rows.
- This confirms incremental forecast information under the fixed SS Cyg
  extraction/coverage and specified frozen timing baseline. It identifies
  neither physical memory nor a within-type mechanism, cross-star transport
  or operational forecasting.
- Keep the secondary era and functional-form results beside the primary:
  1993–2017 gain 0.00573[-0.01067,0.02213]; type/within-type
  gain 0.00248[-0.00220,0.00715]. Both are inconclusive; era intervals overlap.
  Joint conditional current/lag support intervals include zero. Predictions
  empirically overcover. Do not select a new confirmatory comparison.
- Independent checker reproduces all 2,641 scores within 1.91e-13, primary
  statistics, populations and 120 source hashes. The raw-scope audit confirms
  all response timestamps, including capped parents, are before 2018. The
  original context/cache remains unchanged; all 344 tests and source-freeze
  CI pass. No protocol/model/parameter was retuned after the result.
- Source 5e39aeb, execution d7151e0, primary saved 2026-11-08 13:06:58 UTC.
  This is a frozen evaluation after a retained post-access native-format
  repair, never a renewed untouched evaluation. Current single-run access
  status is completed; original execution authority remains in history.
- Report: `docs/audits/2026-11-09-a10i-sealed-evaluation.md`. Aggregate evidence
  only is committed; full raw/context/source/score outputs are verified in
  an internal archive. No raw-data deposit, new event-catalog release or manuscript release is made.
  The 2018+ replication block stays closed. Next is Claude's independent
  scientific framing review, not another data opening.

### D028 — A10i accepted; exploratory decomposition; paper framing seeded

- Claude, 9 November 2026, reviewing A10i (`f05803c`). Full memo:
  `docs/audits/2026-11-09-a10j-result-review.md`.
- Accept D027 and its narrow claim. The primary interval, all variant and era
  intervals, routes and outcome kinds reproduce from saved scores with
  separate interval code. Eight of ten blocks are positive. Leave-one-block-out
  gives 0.0132–0.0194. The criterion survives an SE up to 1.43 times larger.
  D026's repair is outcome-independent and correctly labelled.
- Exploratory, post-result findings (not confirmations):
  - About a fifth of the gain (0.0037) is a level correction. The frozen M2
    forecasts 1960–2017 gaps about 4.6% too long, and durations are shorter
    too. The within-era part is 0.0128 [0.0036, 0.0221].
  - The information is carried by the long/short outburst type:
    - with the frozen M2 nuisance and a free level, type LR is 14.7 against
      11.7 for continuous log duration;
    - within-type duration adds LR 0.17;
    - in 1910–1959 type and continuous duration were equivalent.
  - The predeclared type/within-type rule's weak score (0.0025) reflects an
    uncentred indicator under a fixed baseline. At a common level it gains
    0.0091 [0.0041, 0.0140]. This interaction between A01's type family and
    the A10d fixed-M2 amendment was missed by both agents. Record it in the
    paper's audit trail. Future indicator marks are centred at training means.
  - The separate negative lagged offset follows from long/short alternation
    (r = −0.52) plus a positive current-type effect. No positive lag appears,
    as a slow shared state of the simulated kind would predict. Mechanism
    remains unidentified.
- Paper framing: three products from one claims ledger.
  - `manuscript/estimands.md` (allowed and forbidden phrasings) and
    `manuscript/claims.csv` (25 claims: 13 supported, 12 provisional) are
    seeded.
  - Headline: the confirmatory duration gain with the repair, era and
    type-rule qualifications in the same paragraph. The type reading follows,
    labelled exploratory.
  - Title as scaffolded. Venue, authorship and preprint are Barry's decisions.
- 2018 onward stays closed. Recommended use: one stratum of a multi-star
  frozen protocol whose primary is a centred type rule; SS Cyg alone gives
  about 65 forecasts. A prospective public-forecast arm is outward-facing and
  needs Barry.
- Was evaluation data inspected before this choice? Yes, saved outputs after
  the sealed result, as recorded in the access ledger. No archive request and
  no 2018+ data.
- Status: Codex to check C11–C13 and C20–C25 independently and to review the
  estimands before any drafting.

### D029 — A10k numerical acceptance with narrower interpretations and figure previews

- Codex, 9 November 2026; independent audit evidence committed as `fd4f313`.
  Review: `docs/audits/2026-11-09-a10k-claims-and-figures.md`.
- C11–C13 and C20–C25 reproduce by separately implemented quantiles,
  likelihoods, optimisers, profile roots and block arithmetic. C02's derived
  arithmetic also checks. These become supported calculations; C40/C41 remain
  provisional pending Claude's source/novelty review. The primary comparison,
  forecasts, model parameters and historical receipts are unchanged.
- Narrow the interpretation clauses in D028: a global recentering is not drift
  removal; an in-sample class preference is not exclusive attribution or a
  within-class absence test; the frozen rule's type component is constrained,
  while its within-class component can shorten forecasts. The adjusted class
  result is post-result and does not replace C08. Negative net lag does not
  exclude a coexisting slow component. Clock-scale contrasts are not remaining
  waits. The strict SE failure boundary is about 1.42705; exactly 1.43 fails.
- Preserve the original A10j memo, summary and scripts. The revised estimands,
  claims ledger, supplement correction record and agent-guide traps carry these
  changes forward. Claude should agree or challenge the revised specification
  before substantive drafting; no new scientific approval gate is introduced.
- Four scientific figures plus a brief figure and isolated locked document
  tooling are complete as labelled build previews. The article, brief and
  agent-guide scientific prose are still to be drafted. Venue, authorship,
  submission and a manuscript snapshot release remain unsettled.
- Already-open saved development/evaluation outputs were inspected after the
  primary result. No archive request was made. The 2018+ block remains closed.

### D030 — D029 accepted; sources checked; first drafts of all products

- Claude, 9 November 2026. Review: `docs/audits/2026-11-09-a10l-sources-and-drafts.md`.
- Every D029 narrowing is accepted and governs the products. The estimands
  gain a source-checked physical reading of Cannizzo (1993) and a narrowed
  novelty clause.
- C40 is supported after Claude re-read CM92's Table 4 and Fig. 5 on the
  original scan. C41 is reworded because Grigorievskiy et al. (2014) made
  held-out point forecasts for V363 Lyr. It stays provisional until a
  non-Claude search check, preferably through ADS.
- C15 records the evaluation data scope. Binding V008 is added for the C21
  clock-scale percentage.
- The article, supplement, brief and agent guide are drafted against the
  revised estimands, with endpoint coupling stated as a limit. Codex's
  semantic review follows, then Barry's review. Authorship, venue, the AAVSO
  observer-credit review and any release remain Barry's.
- No archive request, retained-run read or 2018+ access occurred.

### D031 — Draft review complete; bounded novelty supported; handoff to Barry

- Codex, 9 November 2026; review base `2ec3534`. Report:
  `docs/audits/2026-11-09-a10m-draft-review.md`. Article/captions,
  supplement/brief/agent guide, and novelty were reviewed through separate
  bounded routes. Changed passages were checked again after integration.
- The original forecast comparison stands. No model, parameter, score,
  receipt or qualified forecasting source changed. Corrections concern
  interpretation, transformed-predictor definitions, qualification status,
  likelihood references, single-observer confirmation wording, direct
  rounding, observation-time availability and safe reproduction commands.
  The supplement audit trail and agent-guide traps preserve the corrections.
- C41 is supported only as a bounded independent search finding: no prior
  preregistered probabilistic held-out recurrence evaluation or explicit
  held-out duration-addition comparison was found among sources checked.
  The 2014 V363 Lyr point-forecast precedent remains explicit. ADS, indexing,
  observer/non-English and inaccessible-full-text gaps prevent universal
  priority claims; “to our knowledge” must remain.
- Final review PDFs have 13 article, 9 supplement and 2 brief pages. The
  scientific result has not changed. The drafts are handed to Barry for
  review; authorship, venue/CSL, observer credit and a later release remain
  unsettled. No new release or submission is authorised by this entry.
- No photometry or archive endpoint was requested. Two unsolicited
  outcome-related search snippets were disclosed by the novelty delegate;
  neither linked source was opened and no outcome values were passed to
  the parent. The access ledger records that incidental knowledge for
  future protocols. The 2018+ photometry archive remains closed.

### D032 — External review triaged; research round reopened before any rewrite

- Claude, 9 November 2026; proposal, pending Codex's agreement. Review:
  GPT-6 Pro on `f48f0e2` (`docs/reviews/2026-11-09-gpt6pro/`). Triage:
  `docs/audits/2026-11-09-a10n-external-review-triage.md`.
- Accepted in substance:
  - E1: the bracket-mass score is a working interval log score, not a shown
    proper score for physical onset;
  - E2: measured duration can carry endpoint information;
  - E3: a censoring branch asserts survival when a bracket straddles the
    cutoff.
- Exploratory evidence this turn:
  - E3 cannot move the result (dropping all six censored forecasts gives
    0.01678);
  - the A10d null settings with real X4 extraction give mean gains of at most
    +0.00046 against 0.0165;
  - an end-precision split is uninformative.
- Choice: the frozen SS Cyg comparison stands as the foundation and is not
  retuned. Before any rewrite:
  - adopt a coarsened-at-random observation contract (once Codex agrees);
  - run the R1 bounded diagnostics (censor fix, hard-bracket and kernel
    observation scores, endpoint dose–response with a truth target);
  - design a sealed multi-star test with a state-versus-duration model
    ladder.

  One integrated paper, not a quick revision of the incremental framing.
- Evaluation data inspected: yes, the already opened 1960–2017 primary run,
  for exploratory aggregates only. No archive request. 2018+ remains closed.
- Revisit if R1 shows an observational explanation (gate G1), or if the
  cohort cannot reach useful precision (G2). Opening any new star's
  evaluation records is Barry's decision (G3).

### D033 — R1 accepted with observation-contract and endpoint-test amendments

- Codex, 9 November 2026, responding to D032/A10n and the external review.
  Protocol: `docs/protocols/r1-observation-endpoint-diagnostics-v1.md`.
  Independent contract audit: `docs/audits/2026-11-09-r1-observation-contract.md`.
- Accept E1–E3 and the direction of one integrated expanded study. Amend
  A10n: decisive reports are not established hard latent-onset bounds;
  timing-only O1 does not prove CAR for reporting, selection and stopping;
  `_clip` can return a union envelope; an extraction posterior is not
  automatically a measurement likelihood. Alternative scores are working
  compatibility sensitivities; agreement cannot certify latent-onset propriety.
- Preserve all frozen source/run bytes. Add a separately versioned v4 working
  evidence builder and independent reference/regression tests. Audit actual
  candidates rather than substituting the next emitted episode. Do not infer
  a bound on every correction from deleting the six original censors.
- Freeze R1c's 80 retained null/structured seeds and five Gaussian error
  doses, coherent error propagation, fixed anchor populations, invalid-route
  accounting, paired extracted/truth targets and unconditional sigma-zero
  composite oracle. Use v4 for prospective extracted fits, with a legacy-v3
  sigma-zero comparator to separate the censor correction. The original
  administrative cutoff defines the truth target even when v4 backs off.
- The dose response diagnoses this added iid error mechanism under the fixed
  simulator, not a minimum real error or exclusion of all observational
  pathways. Posterior interval width is not calibrated end-error magnitude.
- R1d/e independently check the selected forecast example and all per-setting
  simulation aggregates. Report scenario means separately from individual
  histories. No manuscript rewrite until research/results are reviewed.
- Existing opened inputs may be read. No new archive, star or 2018+ data,
  outside contact, publication, byline or venue decision is authorised. R2
  may prepare a cohort/precision design; its openings remain Barry's decision.
- Status: protocol agreed for bounded exploratory execution; full synthetic
  grid starts only after implementation/tests and protocol are committed.

### D034 — R1 complete: working gain retained, observation-model issue remains open

- Codex, 9 November 2026; D033 implementation freeze `0594146`, with disclosed
  outside-grid smoke note and comparison-only numerical recovery `93e52e6`.
  Evidence: `docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md`
  and `data/provenance/r1_20261109/`.
- Both original evidence builders reproduce all primary outcomes. Actual
  candidates yield zero cutoff straddles and v4 changes zero of 441 outcomes.
  The original working-score result and all frozen sources/parameters remain.
- Saved-point density remains positive: +0.015404 [0.003443, 0.027365]. Finite
  decisive-report clips are missing for 434 forecasts. The interval/kernel
  sensitivities retain only eleven contrasts (six computed, five exact fallback
  zeros), so cannot validate the original full population or close E1.
- All eighty original null/structured histories are reconciled at five error
  doses. Their all-issued mean gains are nonpositive; no added iid-end-noise
  dose reproduces the real +0.01653 reference. Large doses also create common
  fallbacks and zero coefficients. This limits the stated fixed-simulator
  mechanism, without ruling out systematic/selection/measurement alternatives.
- The original grid's 79 successes and one pre-scoring failure are retained.
  The failed history differs only in eight one-step floating log-history
  entries. A gain-free diagnosis, bounded equality audit, regression tests and
  independent review precede the same-seed recovery. Scientific generation,
  fitting, dose and score functions are unchanged. No values are rounded.
- Figure 1's example and all 480 A10d aggregate comparison rows reproduce.
  The real gain exceeds every scenario mean, but eight individual-history
  means reach or exceed it. Finite calibration/error-rate limitations remain.
- C42–C46 are provisional pending Claude review. C01/C02 now explicitly state
  the working-score interpretation. The four manuscript products stay paused.
  R2 may develop the measurement target and stronger evolving-state comparison
  with a cohort/precision design; new archive/star openings, 2018+ SS Cyg,
  specialist contact and any paper release remain outside this authorization.

### D035 — R1 reviewed; R2 design proposed (latent target, assumption ladder, decoupled forecast, ladder, sealed cohort)

- Claude, 9 November 2026. Review: `docs/audits/2026-11-09-claude-r1-review.md`;
  design draft: `docs/protocols/r2-design-v0.md`. Pending Codex agreement or
  amendment into a frozen v1.
- C42–C46 independently checked by separate code and marked supported. C45's
  missing clips trace to an X4 bug: the lower onset clip searched from the
  previous peak, inside that outburst's bright phase. A corrected decisive
  bracket (gain-free, positive estimates only) exists for 818 of 845 confirmed
  episodes, median width 1.16 d.
- Proposed target: the latent threshold crossing, not the first report time.
  Proposed contract: A1 containment in the X5 decisive bracket gives bounds on
  the latent point-score gain with no coarsening model; A1 plus first-detection
  ignorability (A2) makes the bracket interval score proper. Working and point
  scores stay as references.
- Proposed G1 test: a decoupled forecast anchored on decisive reports, with
  bright-phase duration, which never uses the estimated end crossing; fluence,
  coverage strata and synthetic sanity as secondaries. Proposed ladder B0 (M2),
  B1 (AR(2) with evolving level), B2 (local level plus AR(1)), each with
  duration, exact nesting required.
- Proposed multi-star test: catalogue-only screen, development before 1990,
  test 1990–2025, date-bounded requests, development-only qualification,
  pooled B2 + D versus B2 under the X5 interval score, star × block CR1.
- Interpretation rules (design §6) are fixed before any R2 score. No archive
  request; nothing from 2018 onward inspected. G3 openings, SS Cyg 2018+,
  specialist contact and releases remain Barry's decisions.

### D036 — R2 preparation freeze with observation, clock and inference amendments

- Codex, 9 November 2026, amending D035's v0 under Barry's R2a/c instruction.
  `docs/protocols/r2-design-v1.md` is the preparation contract; the independent
  audit is `docs/audits/2026-11-09-r2-design-review.md`.
- Retain the latent visual target with separate A0 association/completeness and
  risk set, A1 containment/survival, and A2 full normalized CAR premises. Exact
  photometry can fail the proposed bracket through recrossings or aggregation;
  a one-magnitude error is not necessary. Visit-rate/contradiction diagnostics
  do not prove CAR or estimate failed-bracket probabilities.
- Resolved inf/sup point-score bounds are valid under containment; censored
  survival scores do not bound unknown latent point scores. Implement separate
  fixed-C mixed-functional bounds, including straddle unions, and working
  interval/backoff compatibility scores. Approximate CR1 inference is distinct
  from deterministic sample ordering.
- X5 corrects the lower-clip search without touching frozen X4. It includes
  limits and conservative raw visit supports, explicit eligibility flags and
  no faint-peak substitution. DF waits for anchor availability or aborts on
  renewed brightness. It removes numerical end reuse, not cadence/selection
  mechanisms; an exact-report counterexample demonstrates this before data.
- Prepare B0/B1/B2 on a common stricter prefix history, exact mark nesting,
  propagated filtered-state uncertainty and explicit missing-history routing.
  Real R2b fits/gains are deferred to the next reviewed execution freeze;
  this turn runs gain-free real diagnostics and synthetic checks only.
- R2c uses dated catalogue/primary-literature evidence, retaining ambiguous and
  eclipsing exclusions. Its committed thirty-five-scenario planning study uses
  explicit dependence, positive fitting, achieved gain, overall/interior
  coverage, and normalized feasible forty-percent star caps. It is not an X5
  calibration or a guarantee that 1,100 archive forecasts suffice.
- No other-star archive request, SS Cyg 2018+ observation/count/coverage,
  outside contact, product rewrite or paper release is authorized. G3 remains
  Barry's decision on the eventual concrete, reviewed multi-star protocol.
- Status: bounded R2a/c preparation accepted; source/configuration bytes must
  be committed before each real-data preparation or synthetic result batch.

### D037 — R2a/c prepared; G2 and mechanism-identification claims remain open

- Codex, 9 November 2026. Preparation/model/feature freezes `fe6dbf4`,
  `f0049dd`, `956d33c`; report
  `docs/audits/2026-11-09-r2a-preparation-and-r2c-review.md`.
- X5 supplies 818/845 confirmed onset windows, 805 eligible, median raw-support
  width 1.1495 days. Limits and temporal supports are explicit; flags and 77
  old-point/window disagreements do not calibrate latent error. Observing-rate
  and contradiction diagnostics cannot establish the A0/A1/A2 premises.
- The causal DF policy produces 302 development and 307 evaluation issues,
  versus 330/441 originals, with 134 evaluation pending-issue aborts. Only 291
  evaluation issues are jointly markable across DF and matched point clocks.
  Twelve current/history anchor discrepancies are recorded. These facts rule
  out interpreting a simple ratio to the original mean as mechanism evidence.
- New B0/B1/B2 and proxy implementations pass unit, covariance and independent
  numerical checks on nine finite controls. Availability guard defects were
  corrected before their batch; rank deficiency is reported, not hidden.
  No real-data R2b model/gain/correlation has been computed.
- The exact-report cadence counterexample yields +0.0539543 without a fitted
  end or physical-duration effect. DF removes a literal numerical estimate,
  not all observation/landmark information. The broader v0 G1 inference is
  rejected; a nonpositive proxy result also would not identify a mechanism.
- R2c records eight nominees, two eclipse/subtype holds and explicit catalogue
  source/passband/exposure limits. No new-star observation access occurred.
  The 35×2,000 score-level study gives fitted power 0.711 at nominal gain .010
  and N=1,100; serial-block nonidentity interval coverage is 0.7265. G2 is not
  established; 1,100 forecasts and star×block CR1 are not validated guarantees.
- Next review must settle the observed-clock/history convention, matched
  population, latent crossing/association assumptions and dependence/precision
  method before real exploratory R2b scores and any eventual G3 proposal.
  Original comparison/parameters and the four product texts/PDFs stay unchanged.
  New claims remain provisional pending Claude review. No new-star opening,
  SS Cyg 2018+ access, specialist contact or release is authorized.

### D038 — R2a/c reviewed; R2b clock, population, crossing and inference rules settled

- Claude, 9 November 2026. Review `docs/audits/2026-11-09-claude-r2a-review.md`;
  rules `docs/protocols/r2b-execution-v0.md`; aggregates
  `data/provenance/r2b_claude_rules/checks.json`. All gain-free; no fit, score
  or duration–gap relation; no archive request; nothing from 2018 onward read.
- C47–C51 supported by separate routes (own X5 selection with limits, quadrature,
  checker scope, own power reimplementation, schedule recount). C52 stays
  provisional (catalogue values not re-extracted).
- All 165 v1 DF aborts were triggered by threshold-level reports between
  magnitudes 9 and 10 (median 9.9), none decisive. R2b aborts only on a
  decisive-bright report: 330/330 development and 441/441 evaluation issues are
  scheduled (median evaluation delay 0.90 d). Past DF gaps run from each past
  emission's own scheduled anchor, so the 12 anchor discrepancies vanish.
- Latent target: the last upward threshold crossing before the first latent
  decisive-bright time. With exact photometry and A0 this lies in the X5
  raw-support window; A1 then fails only through A0, a sign error of at least B
  in a decisive report, or misattributed support.
- C48's cadence pathway is bounded per forecast by observable cadence gaps.
  Planning ceiling 0.0071 nats in 1960–2017 (0.041 in 1910–1959). R2b adds the
  computed ceiling, a cadence-covariate sensitivity (DF-c) and a
  negative-control observing-rate mark.
- Populations P-orig, P-DF and P-match; cross-clock contrasts only P-DF versus
  P-match, paired by issue and outcome. Headline contrasts H1–H3 fixed before
  scores. SS Cyg intervals: six-year CR1 plus twelve-year companion and
  dependence diagnostics.
- The sealed test uses star × 18-year clustering, or star-level if R2d's
  dependence-calibrated simulation gives coverage below 0.88. Star × six-year is
  dropped (coverage 0.846 at mark ICC 0.05, residual ICC 0.1, block AR 0.7).
  SS Cyg's log-mark block ICC is −0.020 to 0.013.
- The sealed primary is fixed now: DF clock, B2 (B1 only on a pre-declared
  stability failure), X5 working interval score. R2b cannot select it by gains.
- Codex amends and freezes `r2b-execution-v1.md`, then runs R2b. Barry's later
  decisions (G3a development-only opening, G3b test opening, SS Cyg 2018–2025,
  specialist) are unchanged and not yet requested.

### D039 — R2b amended contract and pre-fit execution freeze

- Codex, 9 November 2026. Accept D038's decisive-bright abort revision,
  scheduled-anchor histories, matched clocks and fixed H1–H3. Amended protocol:
  `docs/protocols/r2b-execution-v1.md`; independent invented-number review:
  `docs/audits/2026-11-09-r2b-pre-execution-review.md`.
- D038's proposed Fisher ceiling is not a bound. Exact conditional lognormal
  integration already exceeds the quadratic approximation; support changes may
  give infinite KL. Retain a local one-lag sensitivity index only, with no
  mechanism-exclusion gate and explicit older-history/conditioning omissions.
- Retain the last-upcrossing target but not the shortened containment proof:
  exact raw visit aggregation can obscure the ordering of decisive witnesses.
  A0/A1 remain assumptions. The observing-rate mark is a sensitivity, not a
  validated negative control; H3 is a paired working-gain comparison.
- Prepare common-fallback features, actual scheduled/markable counts and
  harmonized historical anchors before fitting. Reconstruct training outcomes
  only from the pre-1960 prefix; no later candidate/window calibrates them.
  Unsupported outcomes remain absent, not zero; algebraic identities are
  distinct. Working cutoffs, mixed bounds and selected-observation assumptions
  are explicitly separate.
- Preserve all optimizer starts and failures. Development stability requires
  every declared start to converge, at least two successes and objective spread
  at most 1e-6 times max(1, absolute best objective). Keep B2 headline diagnostics
  even if unstable; a future sealed fallback may depend only on development
  stability, never evaluation gain.
- Freeze sources/configuration/tests, run the synthetic raw-report rehearsal
  and independent checks, then gain-free actual preparation followed by the
  exploratory 1910–1959 fits and 1960–2017 evaluation. Save parameter hashes
  before evaluation; preserve failures and independently reconstruct scores.
- Six-/twelve-year intervals remain descriptive. The proposed later eighteen-
  year/whole-star choice requires a dependence stress envelope and Monte Carlo
  uncertainty, not a nominal-coverage claim from a single plug-in simulation.
  G2/G3 remain open. No new archive, 2018+ data, contact or release is authorized.
  Manuscript product texts and PDFs remain unchanged; new claims are provisional.

### D040 — Coincident DF issue convention before any real fit

- Codex, 9 November 2026. Source freeze `939208e` passes the synthetic raw-report
  rehearsal and independent scalar reconstruction (2,072 scores, maximum error
  1.25e-14), but gain-free actual preparation stops on one coincident pair.
  Preserve `outputs/r2b_features_939208e/receipt.json`; no real fit/score exists.
- Independent gain-free reconstruction finds 441 original evaluation records
  scheduled at only 440 distinct DF times. One weaker tail re-confirmation shares
  exactly the same faint anchor/support and delayed issue with its predecessor.
  The prior strict-order guard correctly refuses silent duplicate issuance.
- Before any gain, choose the earliest original emission as the representative
  of an EXACT coincident issue+anchor group. Later coincident originals remain
  explicit audit records linked to it, not additional forecasts. This preserves
  the original causal bright phase. It is not physical-event adjudication.
  Different-anchor ties and noncoincident inversions still fail. No general
  pending-supersession or threshold-level cancellation rule is introduced.
- Alternatives: retain all tied records with zero-exposure supersession; choose
  the latest original; reinstate threshold abort. The first adds a redundant
  issuance denominator, the second replaces the phase with a weak repeat, and
  the third restores the cadence selection D038 rejected. None was compared
  using model outcomes or gains.
- `docs/protocols/r2b-execution-v2.md` preserves all other v1 rules. P-orig keeps
  its 441 expected evaluation originals; P-DF/P-match are expected to have 440
  unique issues. Re-freeze sources/tests and repeat the rehearsal and gain-free
  preparation before actual fitting. Preserve v1 and all original A10 results.

### D041 — R2b complete: positive but inconclusive under preselected B2

- Codex, 9 November 2026. Actual source freeze `5fb69c6`, protocol v2;
  `docs/audits/2026-11-09-r2b-exploratory-execution.md` and aggregate evidence
  `data/provenance/r2b_20261109/`. Local parameter SHA-256
  `8c8c53a2602309a2d29d509b6fae60e2f94b11a62c6e051531ae42a1d8ae0630`.
- H1: +0.007535 nats on 432/441 scored/scheduled issues; six-/twelve-year
  90% intervals both cross zero. H2: +0.004276 on 431/440; six-year interval
  [-0.000848,0.009401], twelve-year [-0.002109,0.010662]. H3 paired difference
  -0.003076 also spans zero. All are exploratory, with no clear clock difference
  and no replacement of the original working C01 confirmation.
- Conditional H2 mixed sample bounds [0.000970,0.007753] are not confidence
  limits or containment validation. The observing-rate secondary is positive
  under both blockings (+0.003044), but is not a validated negative control.
  DF-c is +0.004278; this cannot rule other observation pathways out.
- All B2 starts converge with objective agreement and no parameter boundary.
  It remains the preselected comparator. It has lower descriptive baseline
  means than B0/B1 in all three populations; calling it empirically strongest
  would be false. No favorable secondary or alternative model replaces H1–H3.
- Independent direct covariance/scalar reconstruction verifies all fourteen
  models, 24,348 scores, objectives, mixed extrema, H1–H3 and block summaries.
  Local parameter lock and six development-input hashes agree. Original sources,
  parameters, receipts, products and PDFs remain preserved; 516 tests pass.
- Claims C53–C60 remain provisional for Claude. R2d must review measurement
  assumptions, baseline adequacy and a dependence/precision stress envelope.
  The planning effect is smaller and uncertain; no new N or power guarantee
  is asserted. G2/G3 remain open. No new-star or 2018+ access, outside contact,
  manuscript rewrite or first release occurred or is authorized by this result.

### D042 — R2b reviewed: B2 retired, era-drift pathway identified, R2d rules proposed

- Claude, 9 November 2026. Review `docs/audits/2026-11-09-claude-r2b-review.md`;
  proposed rules `docs/protocols/r2d-sealed-design-v0.md`; aggregates
  `data/provenance/r2b_claude_review/checks.json`. Post-result exploration of saved
  R2b clocks only; no archive request, nothing from 2018 onward, no product rewrite.
- C53–C58 and C60 supported by separate routes: own quadrature, recount, exact
  score recompute (maximum difference 0 across 14 models) and closed-form mixed
  bounds. C59 stays provisional. I withdraw D038's "ceiling" and shortened
  containment argument; Codex's counterexamples stand.
- B2 is misspecified for SS Cyg: a random-walk level with a fixed vague prior and
  no mean reversion. Its development NLL is 13–19 nats worse than B0's with equal
  parameter count. It is retired as the sealed comparator (C61).
- Quiescent intervals were shorter in 1960–1983 (geometric means 27.5 and 31.0
  days against 34.5–39.6 in development). B0/B1 over-forecast those waits. A
  causal level recalibration improves their evaluation base by 0.015–0.018 nats
  per forecast but worsens development fits (C61).
- Era-shifted marks earn gain by correcting the base level. This explains the
  positive observing-rate result (mean +1.54 SD; drift-guarded gain 0.0014, t
  1.34) and about 30% of the point-clock B0 duration gain (C62). The DF span
  barely drifts (+0.07 SD).
- Under drift guards (causally centred mark, causally recalibrated base) duration
  stays positive on both clocks: DF 0.005–0.012, point 0.010–0.016 nats, six-year
  t 1.7–2.3 (C63). Exploratory, designed after R2b; no confirmation.
- The score test of a zero mark coefficient beats the out-of-sample gain test:
  the predicted ratio of 1.41–1.74 matches SS Cyg within 0.016, model by model.
  Guards cut the centred design effect to 1.13–1.34 (C64). At an H2-sized KL of
  0.004, about 970–1,550 supported forecasts would give 80% power.
- Proposed for R2d (Codex to challenge and freeze):
  - DF clock and span mark, causally centred;
  - B0R base (B0 plus causal level recalibration), with B1R, B0 and B2 as
    sensitivities;
  - a pooled one-sided cluster-robust score test as primary detection, with a
    small-cluster correction chosen by simulation;
  - the gain as effect size;
  - a precision stress envelope.
- C01 stands as its frozen confirmatory result. Its interpretation as outburst
  memory gains the era-level qualification (estimands.md). G3a goes to Barry
  after R2d, with the required N. Products stay paused.

### D043 — Narrow the R2b review and freeze a dual-statistic R2d precision study

- Codex, 9 November 2026; base `6a94c9d`. Independent scalar truncated-normal
  and Gaussian-covariance reconstruction reproduces all fourteen reviewed
  models; guarded gains agree within 6.15e-15 and score statistics within
  7.81e-12. C61–C64 are supported only for the narrowed arithmetic in the ledger.
- Amend D042's interpretation: B2's likelihood ranking is not a predeclared
  adequacy test or unique physical diagnosis. Simultaneously changing the base
  and mark does not identify causal era attribution; C01 was not decomposed.
  The guarded rate estimate is still positive. Point-original B0 has positive
  intervals under both blockings; the contrary C63 limitation is corrected.
- Rolling guards do not exclude shared trends. A score moment and gain from a
  frozen development-trained candidate test different claims: an invented
  Gaussian example has positive score expectation and negative forecast gain.
  Keep forecast gain as the default confirmatory route under D018; simulate
  both, without approving a changed primary claim.
- Freeze `docs/protocols/r2d-sealed-design-v1.md`, the 35-case configuration,
  sequential Gaussian helper, runner and tests before the 70,000-trial grid.
  At most four local workers, deterministic per-case/per-replicate seeds,
  no redraws, report all declared methods rather than selecting on this grid.
  This is a point-log-gap learning/availability screen, not X5 or calendar yield
  validation. Strict predictive nulls, estimated-base controls and no-direct-
  effect specificity stresses have distinct labels and interpretations.
- B0R is a transparently post-R2b candidate chosen for simplicity, retaining
  B1R/B0/B2 sensitivities. Actual interval-score prefix availability remains
  unimplemented by this toy. New-star G3a/G3b, SS Cyg 2018+, outside contact
  and release remain closed. Products remain paused. Claude reviews the study
  before a concrete scientific-claim/access proposal goes to Barry.

Execution under `67c45ab`: all 70,000 trials complete, zero failures. The clean
eight-star/1,100 score cell has 81.8% rejection, but gain only 36.65%; joint
stresses are weaker. No tested core gain cell reaches 80%, and no score
procedure clears every strict-null observed-rate screen. No method is selected
and no robust N is established. Specificity/overshoot examples confirm that
guarded association, frozen forecast improvement and mechanism remain distinct.
C65–C66 are provisional for Claude; see the R2d precision report and retained
per-case Monte Carlo intervals. No new access or scope change follows.

### D044 — R2d reviewed; fixed-sequence claims; G3a early-record proposal for Barry

- Claude, 9 November 2026. Review `docs/audits/2026-11-09-claude-r2d-review.md`;
  proposal `docs/protocols/g3a-early-record-feasibility-v0.md`; aggregates
  `data/provenance/r2d_claude_review/checks.json`. Synthetic recount only; no
  observation, archive or real forecast read.
- C65 and C66 supported: all 35 trial-file hashes match the summary, and every
  gain, score and sign-flip rejection count reproduces. D043's narrowing of
  C61–C64 accepted.
- The per-cell strict-null screen (observed rate at most 5% in 2,000 trials)
  fails an exact 5% test with probability 0.473, and at least one of four cells
  with probability 0.923. The pooled whole-star score rate is 4.96%
  [4.50, 5.46]. The score procedures are at nominal size on this generator.
- In all 70,000 trials, forecast gain never rejected without the score moment
  also rejecting (C67).
  - Proposed sealed structure: association first, then D018's forecast gain,
    in fixed sequence at one-sided 5% each.
  - The gain claim keeps its full stand-alone power (36.6% in the clean
    eight-star cell), and the association claim gets 81.8%.
  - Overshoot gives "association without forecast improvement"; shared slow
    states give both. Neither identifies a mechanism.
- Star count binds: 65.6% against 81.8% score power for four against eight
  clean stars. Only development records can tell how many qualify.
- G3a proposal for Barry:
  - opening: pre-1990 (JD < 2447892.5) AAVSO visual records for the eight
    nominees plus the U Gem and IP Peg holds, behind a frozen eclipse rule;
  - measurement: gain-free coverage, extraction and support;
  - qualification: at least 40 timing-supported marked development forecasts,
    X5 eligibility of at least 0.7, B0 convergence and the morphology screen;
  - go/no-go for G3b: at least six qualifying stars and at least 1,100
    projected supported test forecasts;
  - no test-period row, count or coverage.
- Codex: check C67, contest or accept the fixed sequence, and freeze the G3a
  implementation (date-bounded requests, per-star thresholds, eclipse rule).
  Add six-star R2d cells before G3b. No request until Barry answers.

### D045 — G3a approved; freeze development acquisition and gain-free qualification

- Barry's direct chat answer on10November2026, following Claude's9November
  23:37handoff, exactly: “yes, approved as proposed. Continue.” All ten G3a
  targets' native JD<2447892.5 records may be opened; G3b, all new-star1990+
  rows/counts/coverage and SS Cyg2018+ remain closed. Immutable authority:
  `data/access/g3a_authority.json`.
- Codex independently reproduces C67: zero gain-without-score rejections in
  all70,000 retained trials under both clusterings; pooled strict-oracle score
 397/8,000. Support the empirical claim, not a general nesting theorem or
  future power identity. Accept the proposed sequence with explicit marginal
  validity conditions under both full nulls; no pooled-global-null certificate.
- Before any target metadata/observation request freeze G3a v1, the exact ten
  names/catalogue thresholds/common margin1, native date/identity/pagination
  guards, unmarked B0/coverage/morphology qualification, eclipse robustness
  branches and tests. Count is a continuation marker under pinned VStar source;
  follow invariant date-bounded pages. Any scope/identity/redirect violation
  stops all subsequent requests. Preserve every native response and failure.
- Operationalize usable≥40 as timing/mark support plus a genuine onset-window
  or positive-exposure censored outcome. Keep feature-only counts separately.
  No beta, duration-gap association or forecast-gain comparison before set freeze.
  U Gem/IP Peg require both ordinary reductions and the frozen eclipse guard;
  passing is conditional feasibility, not eclipse removal or subtype proof.
- Run the frozen eight-cell six-star supplement without changing original
  R2d sources/results. G3a closes at a frozen qualifying set, aggregate
  feasibility and28/36-year projections from1980–1989 only. Six qualifying
  stars and≥1,100 projected issuances are prerequisites for a later G3b request,
  not an automatic opening or80% power promise. Products remain paused.

## New decision template

### D0xx — Short concrete title

- Date and decision maker:
- Evidence and alternatives considered:
- Choice and scientific consequence:
- Affected files and analyses:
- Was evaluation data inspected before this choice?
- Status, review and conditions for revisiting:
