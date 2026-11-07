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

## New decision template

### D0xx — Short concrete title

- Date and decision maker:
- Evidence and alternatives considered:
- Choice and scientific consequence:
- Affected files and analyses:
- Was evaluation data inspected before this choice?
- Status, review and conditions for revisiting:
