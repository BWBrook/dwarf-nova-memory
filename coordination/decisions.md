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

## New decision template

### D0xx — Short concrete title

- Date and decision maker:
- Evidence and alternatives considered:
- Choice and scientific consequence:
- Affected files and analyses:
- Was evaluation data inspected before this choice?
- Status, review and conditions for revisiting:
