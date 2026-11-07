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
  power estimate implies the SS Cyg locked block can confirm calibration and
  sign but cannot detect the expected effect alone; that belongs in the
  evaluation protocol (A10), not here. No loader exists yet. Final evaluation and prospective
  forecasting remain proposals; A03 follows A01/A02 and access-policy review.

## New decision template

### D0xx — Short concrete title

- Date and decision maker:
- Evidence and alternatives considered:
- Choice and scientific consequence:
- Affected files and analyses:
- Was evaluation data inspected before this choice?
- Status, review and conditions for revisiting:
