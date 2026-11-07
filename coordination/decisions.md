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
- Status: protective restriction in force; final evaluation suitability and
  operating characteristics remain unresolved. A03 may proceed only within the
  open interval. A01's later-era annotation, reproduction and power proposals
  are superseded by this decision where they conflict.

## New decision template

### D0xx — Short concrete title

- Date and decision maker:
- Evidence and alternatives considered:
- Choice and scientific consequence:
- Affected files and analyses:
- Was evaluation data inspected before this choice?
- Status, review and conditions for revisiting:
