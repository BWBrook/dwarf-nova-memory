# Shared task board

Updated: 8 November 2026. Discussion lives in the `dwarf-nova-memory` board
section (snapshots in `docs/correspondence/`); this table is the record of
claims and handovers.

| ID | Task | Status | Suggested owner | Acceptance / next action |
|---|---|---|---|---|
| S00 | Initial literature, data and methods framework | Seed complete | Shared | Re-audit closest sources; review access-depth limitations |
| S01 | Runnable synthetic scaffold and scientific invariants | Seed checked | Shared | See `docs/12-seed-validation.md` |
| S02 | Public repo, licences, board section, first post | Done 2026-11-07 | Claude | D011; 17/17 tests and `validate_seed.py` pass on macOS, Python 3.15.0 |
| A00 | Outcome-access partition before any real light curve is plotted | Done 2026-11-07; refinements accepted by Claude | Codex + Claude | D012; [access ledger](../docs/outcome-access-ledger.md) with both exposure entries; no real data acquired |
| A01 | Independently challenge novelty and physical framing | Done 2026-11-07 | Claude | [A01 memo](../docs/audits/2026-11-07-a01-novelty-framing.md): Gate A passes provisionally with a narrower claim; published partial r ≈ 0.13 verified; [power interpretation and D013 amended](../docs/audits/2026-11-07-a01-review-d013.md) by Codex |
| A02 | Audit code and reproduce a key probability independently | Done 2026-11-07, seed scope only | Codex | [Audit](../docs/audits/2026-11-07-code-audit.md); 22 tests, independent fixtures, 16-table numerical reproduction |
| A03 | Resolve one real target and obtain an authentic export | Native acquisition done 2026-11-07; normalization pending | Codex | [A03 receipt](../docs/audits/2026-11-07-a03-ss-cyg-acquisition.md): 3438 visual rows, 124 limits, raw hash/manifest; only 1956–1959; native time scale/reference unresolved |
| A04 | Annotate development events and coverage | Boundaries adjudicated; conditional synthetic screen complete, both candidates require repair | Claude + Codex | [A04c recovery audit](../docs/audits/2026-11-07-a04c-injection-recovery.md); 3,200 histories, effective coverage fails; original labels/candidates retained |
| A04b | Extraction and coverage candidates; open-era injection/recovery | Screen complete in A04c; qualification fails | Claude extractors, Codex harness | Both candidates retained unchanged; conditional-vs-effective coverage and 1950s null bias prevent freeze; repair and fresh validation next |
| A04d | Benchmark review, extractor repair, fresh validation | X3 proposed with training evidence; validation protocol proposed, not frozen | Claude X3 and checks; Codex benchmark v2 and validation | [A04d memo](../docs/audits/2026-11-07-a04d-observation-review-x3-repair.md), [proposed protocol](../docs/protocols/a04d-x3-validation-v1.md); v1 benchmark fails predictive checks; X3 93–95% effective coverage on training, fails v1 end coverage |
| A04f | X3 failure review and X4 repair | X4 proposed with development evidence; A04g protocol proposed, not frozen | Claude X4 and diagnosis; Codex v3 benchmark and validation | [A04f memo](../docs/audits/2026-11-08-a04f-x3-failure-review-x4.md), [proposed protocol](../docs/protocols/a04g-x4-validation-v1.md); state arm fails observer-diversity check; X4 94–98% effective coverage on development seeds of both v2 arms |
| A04h | Joint morphology and cadence targets | Proposed, not frozen | Claude targets and operator; Codex next benchmark version | [A04h memo](../docs/audits/2026-11-08-a04h-joint-morphology-targets.md), [proposed targets](../docs/protocols/a04h-joint-morphology-targets-v1.md); v3 lacks amplitude–duration coupling; v2 random passes the waveform block; all arms fail decline sampling density |
| A10a | Restriction review, prefix-causal predictors, precision | Proposed, not frozen | Claude protocol, ledger code and pilot; Codex models and controls | [A10a memo](../docs/audits/2026-11-08-a10a-prefix-predictors-review.md), [proposed protocol](../docs/protocols/a10-prefix-causal-predictors-v1.md); magnitude 10 structural (0.5 mag margins clear the peak distribution only there); causality costs ~0.05 d on real 1910–1959 rows; single-star forecast-gain test ~1/3 power at r≈0.12, estimand resolved by D018; A10b review/control evidence now available |
| A10b | Model implementation, repaired ledger and full-chain synthetic controls | Complete development pilot; reviewed in A10c | Codex with independent code/method references | D018 keeps forecast gain confirmatory; [development specification](../docs/protocols/a10b-model-controls-v1.md); no real focal fit or reserved-data access |
| A10c | Control review; forecast system, OC study and development-fit specification | Implemented and amended in A10d/A10e | Claude review/spec; Codex implementation, OC study and real 1910–1959 fit | [A10c memo](../docs/audits/2026-11-08-a10c-controls-review.md), [protocol](../docs/protocols/a10c-development-fit-v1.md), D020; fallback routing gave duration credit for missing timing; null coefficients negative (end-error coupling); directional matched M3 gives −0.0002 null, +0.0023 injected on A10b scores |
| A10d/A10e | Directional forecasts, 360-trial OC screen, first real 1910–1959 fit | Complete; reviewed in A10f | Codex | [A10d audit](../docs/audits/2026-11-08-a10d-directional-oc.md), [A10e report](../docs/audits/2026-11-08-a10e-first-development-fit.md); D021, D022; power 27.5%; real β=0.0466, P3 at zero; parameters `ce4ef8d5…` |
| A10f | Development review and evaluation protocol | Amended by Codex in A10g (D024); executed in A10i | Claude protocol; Codex runner, fixtures, rehearsal and sealed run | [A10f memo](../docs/audits/2026-11-08-a10f-development-review.md), [protocol](../docs/protocols/a10f-evaluation-v1.md), D023; real dev LR reached by 5/220 gated nulls, 12/40 injected; slow state disfavoured by lagged-mark bound; conditional power ~1/3 |
| A10g–A10i | Sealed runner, checker, rehearsal, protocol DOI and the 1960–2017 run | Complete; reviewed in A10j | Codex | [A10g freeze](../docs/audits/2026-11-08-a10g-evaluation-freeze.md), [A10h repair](../docs/audits/2026-11-08-a10h-native-format-repair.md), [A10i result](../docs/audits/2026-11-09-a10i-sealed-evaluation.md); D024–D027; +0.01653 [0.00495, 0.02812], 441 forecasts; criterion met after post-access format repair |
| A10j | Result review, exploratory decomposition, paper framing | Complete; numbers reproduced and interpretations narrowed in A10k | Claude | [A10j memo](../docs/audits/2026-11-09-a10j-result-review.md), D028, [estimands](../manuscript/estimands.md), [claims ledger](../manuscript/claims.csv); level part ≈ 1/5; information carried by long/short type; type rule hit by uncentred indicator |
| A10k | Independent claim checks, figures and document build | Complete; accepted by Claude in A10l (D030) | Codex | [A10k memo](../docs/audits/2026-11-09-a10k-claims-and-figures.md), D029; C11–C13, C20–C25 supported; four figures and brief figure |
| A10l | Source checks (CM92, Cannizzo 1993), novelty refresh, first drafts of all products | Drafts complete; reviewed in A10m | Claude | [A10l memo](../docs/audits/2026-11-09-a10l-sources-and-drafts.md), D030; C40 supported; C41 narrowed, still provisional |
| A10m | Semantic, novelty and rendered-draft review | Complete; drafts externally reviewed (A10n) | Codex | [A10m review](../docs/audits/2026-11-09-a10m-draft-review.md), D031; C41 supported as a bounded search |
| A10n | Triage of the GPT-6 Pro external review; next research round | Agreed with amendments (D033); R1 complete (D034) | Claude | [A10n triage](../docs/audits/2026-11-09-a10n-external-review-triage.md), [review package](../docs/reviews/2026-11-09-gpt6pro/), D032; censor path bounded at +0.00024; null-simulation gains ≤ 0.0005 |
| R1 | Censor audit, alternative observation scores, endpoint dose, example and simulation table | Complete (D034); C42–C46 supported by Claude review (D035) | Codex | [R1 audit](../docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md), [Claude review](../docs/audits/2026-11-09-claude-r1-review.md); point gain +0.0154; 434 missing clips traced to an X4 lower-clip bug |
| R2 | Observation target, observed clocks, timing baselines, sealed multi-star design | R2b complete (D039–D041); H1–H3 inconclusive; new claims await review | Claude R2b review / R2d design | [R2b v2](../docs/protocols/r2b-execution-v2.md); [results](../docs/audits/2026-11-09-r2b-exploratory-execution.md) |
| A05 | Audit remaining provisional pilot targets | After A03 | Split targets | One feasibility dossier per target, including failures |
| A06 | Reproduce one historical descriptive result | After A04 | Rotate implementer/reviewer | Document data/version/definition mismatches |
| A07 | Decide restricted-episode versus richer observation model | After A05/A06 | Scientific lead with agents | Gate B/C decision and revised estimand |
| A08 | Implement observational M0, then M1 | After A07 | Agent implementer + other reviewer | Censoring, boundary propagation, calibration |
| A09 | Add past-only M2/M3 and identifiability simulation | After A08 | Rotate roles | Same state architecture, no future smoothing |
| A10 | Freeze evaluation | Complete: frozen 1960–2017 comparison met its criterion (A10i); reviewed (A10j) | Scientific lead | Paper from the claims ledger; 2018+ stays closed |

## Current blocking information

The requested SS Cyg stream through native JD 2436934.0 is acquired in 12
hashed exports, with 72,635 unique native IDs. Early coverage varies sharply.
The three boundary disagreements are adjudicated. A04i conditionally qualifies
X4 at magnitude 10/C1 for retrospective extraction. A10b completes a synthetic prototype/control pilot of the forecast chain; operational availability, observation/coarsening
effects, baseline architecture and final operating characteristics remain
unresolved. D018 retains forecast gain as confirmatory despite low expected
single-star power.
UT/geocentric timing is presumed; a
convention sensitivity is not a bound on historical record errors. The 1960–2017 candidate
evaluation is sealed at the raw-data level under D013, with published aggregate
exposure disclosed. These are research unknowns, not values to invent.

## Working claim format

Before starting, append the task ID, branch/worktree, files owned and intended
deliverable. On completion, link the commit and concise evidence. Do not edit
another active agent's owned file without coordinating the handoff.

## Completed tranche — A00/A02, 7 November 2026

Codex, `main`: review the provisional access policy; audit the seed, independently
check probabilities and chronological forecasts, and repair fresh-run numerical
reproducibility checks. Owns `coordination/`, a new audit/access note, the demo
comparison script and its tests, CI and relevant README/validation text. A
read-only reviewing subagent checks survival and forecast calculations using
independent fixtures. No real astronomical data retrieval in this tranche.

Evidence: the audit above records base commit `f46284a`, commands, results and
limitations. No model/generator or committed seed outputs changed. Commit
[`c46ba1c`](https://github.com/BWBrook/dwarf-nova-memory/commit/c46ba1c4d91a5d5a6fcb2fae3cea9731205cc9f2)
records the added checks and documentation. Next: Claude reviews D012,
adds their own exposure entry and completes A01. A03 remains after that review;
the highest-value next empirical step is one bounded pre-2018 acquisition.

## Completed tranche — A01 and D012 review, 7 November 2026

Claude, `main`: novelty and physical-framing audit with two read-only Claude
Sonnet reader subagents; D012 refinement review and Claude exposure entry. Owned
files: `docs/audits/2026-11-07-a01-novelty-framing.md`, `docs/audits/a01/`,
`scripts/literature/a01_citation_map.py`, `references/a01-new-identifiers.txt`,
rows E06–E08 of `references/evidence.csv`, the A01 note in
`docs/02-literature-review.md`, the Claude entries in
`docs/outcome-access-ledger.md`, and the D012 status line. No real photometry
was retrieved. Next: Codex reviews the memo, especially §3.2's prior effect
size and the proposed D013 split, then proceeds to A03 for SS Cyg.

## Completed tranche — D013 review and A03, 7 November 2026

Codex, `main`, base `a89a084`: independently audit the A01 effect-size and power
claims, resolve the proposed SS Cyg access split before retrieving photometry,
and pursue a date-restricted authentic acquisition if the revised policy permits.
Owns a new review/calculation script and tests, D013/access/config updates,
A03 adapter/report/fixtures if supported by the native export, manifest and
status records. A read-only methodological reviewer checks the arithmetic and
holdout logic; no delegate may retrieve light curves. Reserved eras remain
uninspected. Outcome: [D013 review](../docs/audits/2026-11-07-a01-review-d013.md) and
[authentic acquisition](../docs/audits/2026-11-07-a03-ss-cyg-acquisition.md) complete.
The official web export required sign-in; the source-supported VStar route
succeeded anonymously. Native time normalization and observational fitting are
not complete. A03 raw bytes stay outside Git; the public manifest records their
hash. Current checks: 26 tests, seed validator and numerical reproduction.
Next: Claude reviews D013 and the receipt, resolves timing/flag documentation,
then begins independent pre-1960 annotation. Full CM92 reproduction is deferred
until primary evaluation is sealed.

Code, provenance and review commit: [`1428ce2`](https://github.com/BWBrook/dwarf-nova-memory/commit/1428ce27bf9ad0b47eb29f8e79d9193f437e2c26).
The handoff is board thread 142; raw exports and the local figure are not committed.

## Completed tranche — D013 review, metadata check and A04 annotation, 7 November 2026

Claude, `main`, base `04a8b69`. I accepted D013's amendments and checked native
timing and flag documentation. I then annotated SS Cyg outbursts in
1956-01-01 to 1959-01-01, using a protocol pushed (`1bfbca5`) before any
magnitudes were viewed. Owned files:

- `docs/protocols/a04-event-bracketing-v1.md`;
- `docs/audits/2026-11-07-a04-review-and-annotation.md`;
- `src/dnmem/brackets.py` and `scripts/a04_*`;
- `data/annotations/`;
- `tests/test_brackets.py` and `tests/test_a04_annotation.py`;
- the D013 review line, the status lines in AGENTS/README, and my ledger entry.

No 1959+ data were viewed. Next: Codex annotates the 1957 subset blind (memo
§4), then compares, then acquires the rest of the open era in bounded requests.

## Completed tranche — A04 independent comparison and early-era acquisition, 7 November 2026

Codex, `main`, base `7673b4a`. A fresh context-isolated delegate received only
the frozen protocol at `1bfbca5`, a hashed native 1957 subset and its input
receipt, with instructions to avoid Claude's labels, memo, tools and board
results. Parent owned comparison and review, bounded acquisition/receipt
checks, early-era profiles, manifest/status updates and handoff. A separate
read-only methodological reviewer checked endpoint and A10 claims without
contacting the blind delegate. The delegate wrote only its isolated scratch
directory. Blind labels were sealed before comparison. New requests followed
comparison: three-year windows around 1905, 1925 and 1945, then the remaining
open-era requests ending at JD 2436934.0. No 1960+ data, duration–gap
correlation or real-data forecast fit was authorized or performed in this tranche.

Outcome: blind labels sealed in `2aa9262` with LF serialization receipt `bc1222b`;
receipt-window guards in `0ece7ad`. The comparison/coverage report links the
reproduction commands, public summaries and all native hashes. No primary
label was changed after unblinding, and no consensus catalogue or scientific
estimand change was adopted. Next: Claude adjudicates boundary/tie handling,
reviews coverage/extraction candidates and the endpoint/A10 qualifications.

Results and status are committed in `8bb21cb`. Board replies 2947 (comparison
and endpoint assumptions), 2948 (A10 estimand) and 2949 (open-era acquisition)
carry the detailed handoff. Local checks: 34 tests, structural validator,
16-table numerical reproduction, native/manifest hashes, blind seals and staged
gitleaks all pass. No consensus catalogue, empirical duration–gap correlation
or real-data forecast fit was produced.

## Completed tranche — A04b adjudication and extraction candidates, 7 November 2026

Claude, `main`, base `a5635df`. I adjudicated the three disputed 1957
boundaries and proposed a rule for tied and mixed epochs. I implemented
observer-balanced candidate extractors X1 (vote majority) and X2 (nightly
median with hysteresis), scored them against both annotations, and profiled X1
over the open era. I also specified the injection/recovery design. Owned files:

- `docs/audits/2026-11-07-a04b-adjudication-extraction-candidates.md`;
- `src/dnmem/extract.py` and `tests/test_extract.py`;
- `scripts/a05_compare_extractors.py`;
- `data/annotations/a04_ss_cyg_1957_adjudication.csv`;
- `data/coverage/ss_cyg_open_era_x1_by_decade.csv`;
- the related status lines.

No 1960+ data were touched, and no real duration–gap association was computed.
Next: Codex builds the injection/recovery harness (A04b §5) independently of
the extractor code, adds an X3 candidate if it wishes, and reports against the
pre-stated selection criteria.

## Completed tranche — A04c injection/recovery, 7 November 2026

Codex, base `4945af6`, implements the synthetic generator, observation model,
independent scorer and seeded runner. The X1/X2 source remains unchanged.
Delegates own disjoint truth, observation and scoring modules; the parent owns
integration, the pre-run protocol, run receipts and interpretation.

The decisive null uses generated renewal times; fixed-onset alignment is a
sampling diagnostic because Q=C−D. Criteria stay at threshold 10.0, with
9.5/10.5 as truth-referenced sensitivities. All data inputs remain pre-1960.
No empirical real duration–gap association or real forecast fit is authorized.
The stop condition is the frozen screening grid plus independent harness review,
with explicit pass/fail/inconclusive criteria and Monte Carlo uncertainty.

Outcome: `c2f6eed` freezes implementation choices; `3bb2237` commits the
independently implemented harness before production. The 3,200-history grid
completed with 57,600 metric rows and 288 aggregate cells, no extraction
exceptions and no candidate selected. X1 conditional end coverage is 74–80%;
X2 conditional intervals perform better but effective onset coverage is
88–90%. All short-completeness and false-episode gates pass. Null bias clears
the margin in 1910–1949 and remains inconclusive in the 1950s. No post-screen
widening or extractor change was made. Detailed evidence and limitations are
in the A04c report; full payloads remain gitignored.

Local verification: 64 tests, structural validator, original sixteen-table
numerical reproduction, staged gitleaks and independent source/result audit.
CI for the harness passes on Python 3.11–3.13. Next: Claude reviews the
observation assumptions, repairs/calibrates the candidates on a separate batch
and specifies fresh validation; reserved data remain closed.

Results/receipts/figure: `20caae0`. Board message 2961 carries the screen and
repair handoff; 2962 records the A10 resolution and preserves the distinction
between candidate adjacencies and verified forecasts. Independent source and
artifact reaggregation reproduced all gates, and the production candidates
were unchanged. No fresh validation seeds have been consumed by a repair.

## Completed tranche — A04d benchmark review and X3 repair, 7 November 2026

Claude, base `0ba1e4c`. Development used training seeds only (base
`a04d-claude-training-20261107`); the A04c screen seed and 1960+ data were not
touched, and no real duration–gap association was computed.

- A posterior predictive check (`scripts/a04d_morphology_check.py`) shows the
  A04c v1 benchmark's decline rate scales with duration (Spearman −0.54; real
  0.04), its decline doubles in speed at a knot exactly at 10.0 (real slopes
  are equal on both sides), and its scatter at the threshold is about 20% low.
- Per-event diagnosis: every X1 boundary miss is a single misclassified vote at
  the bound; X2's bounds are night-median times; lost matches are 1.6% short
  sparse events and 1.2% gap splits.
- X3 (`src/dnmem/extract_x3.py`): X1 detection with a 7 d split rule, fitted
  crossing posteriors with clipping, posterior-median point estimates and an
  operational confirmation time. On training it reaches 93–95% effective
  coverage under realistic morphology; it fails v1's end coverage (84–86%)
  because of the knot.
- Proposed protocol `docs/protocols/a04d-x3-validation-v1.md`: benchmark v2
  gated on the predictive checks, state-matched cadence arm, 400 replicates
  in decisive cells, seeds from Codex's freeze commit, a fifth criterion on
  premature confirmation.

Next: Codex reviews X3 and the protocol, builds benchmark v2 independently of
X3's source, freezes the protocol and runs the validation.

## Completed tranche — A04e independent X3 validation, 7–8 November 2026

Codex, base `66cfdf2`. Review and amend the proposed A04d protocol, build a
new generator without X3 source, freeze finite morphology calibration, qualify
it on fresh seeds, then validate unchanged X3 against X1/X2. Parent owns
observation scheduling/calibration, protocol and result integration; delegates
own disjoint generator, morphology, scoring and runner modules.

The original-v1 failure is retained as a diagnostic. Morphology targets remain
X1/measurement-conditioned; state-compatible cadence preserves empty days.
The batch confirmation field cannot erase earlier emissions: a causal wrapper
and explicit premature/missing gates are tested separately. No real D–Q
association, reserved data or A10 freeze is part of this tranche. Stop with
independently audited qualification/validation evidence, including failures.

Outcome: final freeze `2f7a7ec` passed fresh morphology qualification, followed
by all 7,600 histories / 79,200 rows / 324 cells with no extraction exceptions.
X3 remains byte-identical to `c0353c0`. Both global eligibility rules fail;
state-compatible effective coverage in the 1930s–1950s is the decisive
blocker, and 1910–1929 causal unsafe emissions remain inconclusive. C1 null
bias clears ±0.02 in all twelve decisive cells. Positive-control association
recovery is close to the realized raw-scale oracle, while original-v1 end
coverage still fails at 84–86%. No outcome-driven widening or repairs were
made. Full payloads remain ignored; reviewed tables, hashes, calibration and
qualification receipts are public under `data/simulations/`.

Verification: 120 tests, seed structural validator, unchanged frozen runtime
hashes and independent artifact reaggregation. The frozen source passes CI
on Python 3.11–3.13. See D015 and the A04e report for the causal-wrapper
distinction, benchmark limitations and exact reproduction commands.

Next: Claude — review detection losses, causal false signals and benchmark
assumptions before proposing a revised eligibility/missed-event approach.
No reserved data or real duration–following-gap association was accessed.

Results/report/public tables: `f3b8fcc`. Board messages 2977 (full A04e
handoff) and 2976 (A10 boundary) record the reviewed conclusion; correspondence
snapshot refreshed at close. The independent audit reconciled all 24 decisive
cells, 4,800 primary ledger records and all published table values.

## Completed tranche — A04f X3 failure review and X4 repair, 8 November 2026

Claude, base `d687c73`. All simulations use new `a04f-claude-*` seed namespaces;
no A04e qualification or validation seeds, no 1960+ data and no real
duration–gap association.

- Diagnosis on v2 diagnosis seeds reproduces A04e (1930–1949 state X3
  88.9%/89.2%). Losses: 5.3% single-observer (unconfirmed) outbursts in the
  state arm against 2.2% in random, about 4.5% finite misses at 95%
  conditional coverage falling with fit size, and causal false emissions that
  are tail or rise re-arming within days of a true crossing.
- The state arm's nearest-donor rule copies one real day's observers across a
  synthetic outburst: median 8–9 distinct bright observers per outburst
  against 14–16 real. Real X3 unconfirmed share is 1.5% (5 of 344).
- X4: 0.05 mag shared-error floor (chosen on the smooth training family),
  uncontradicted multi-night single-observer confirmation, and causal arming
  at 0.5 mag past the threshold. Development: 94–98% effective coverage in
  every v2 and smooth cell, causal unsafe at most 0.021 per year, widths up
  6–23%.
- Proposed A04g: an unseen v3 family, a diversity-preserving decisive state
  arm qualified on observer diversity, a gross-error arm, seeds from Codex's
  freeze commit, A04e criteria unchanged.

Next: Codex reviews X4 and the A04g proposal, builds v3 and the revised state
arm independently of X4, freezes and runs the validation.

## Completed tranche — A04g benchmark qualification, 8 November 2026

Codex, base `4816f89`. Candidate-blind delegates own the new waveform and
cadence modules; an independent causal implementation is hash-recorded before
reference exposure and agrees on fixtures/fuzz. Parent owns morphology-only
calibration, protocol completion, integration and result interpretation. A
separate executor owns the new runner/summary, reusing frozen A04e scoring
conventions. Existing candidates and A04e result/source stay unchanged.

The proposed diversity tolerance is not widened. Repaired diverse arms must
meet it; the known diversity-misspecified random arm remains a conservative
mandatory recovery control, not an empirically diversity-qualified model.
No X4 recovery outcomes or validation seeds are accessed until fresh benchmark
qualification passes. Initial v3 geometry in `c9d51b8` failed a morphology-only
pilot through duration-linked slopes and is being repaired before calibration.
That failed specification is retained. No real duration–gap association,
reserved data or A10 freeze is part of the tranche.

Pre-qualification checkpoint: revised polynomial truth preserves slopes and
amplitudes; revised cadence matches calendar span/season while recording
additional missing days. The 27-configuration finite calibration has one
passing configuration (index 23), with source `28741bc`. Independent audit
verified all input/calibration/source bindings and corrected guard contracts.
Fresh qualification is fixed at 32 histories per era/phase/family, with no
tolerance widening or after-failure seed extension. D016 records the design.

Outcome: clean freeze `b83d76a` completed all 384 fresh qualification histories.
V2 passes; repaired diverse arms match the observer targets in every era.
V3 diverse fails only the slope–duration morphology gate, rho −0.110 versus
real +0.045 (difference 0.155 against tolerance 0.15). The benchmark is not
qualified, so the planned 16,600-history X4 recovery was not run and its
validation namespace remains unused. X4 has no independent recovery verdict.

The synthetic slope distribution is already broader than real; increasing
variance to mask the correlation is unsupported. The independent auditor
supports preserving this failure and revisiting joint morphology in a new
version. All failed specifications, finite attempts, hash-bound receipts and
recovered pre-exposure causal source are retained. Verification: 166 tests,
structural validator, freeze CI and staged secret scan pass; actual failed
qualification is rejected by the recovery guard before any scoring.

Next: Claude — review the benchmark failure and specify joint morphology
with distributional targets; keep X4 unchanged until a benchmark qualifies.

Closing results: `6bce5f6`. Board messages 2990 (full benchmark handoff) and
2991 (A10 boundary) record the outcome; reviewed snapshot refreshed at close.

## Completed tranche — A04h joint morphology targets, 8 November 2026

Claude, base `6518de8`. Morphology-only simulation on new `a04h-claude-*` seeds;
no X4 recovery scoring, no 1960+ data and no real duration–gap association.

- v3's failure is waveform geometry: it fixes amplitude and steepens short-event
  flanks (noiseless band-slope–duration Spearman −0.16 against v2's +0.10).
  Real SS Cyg outbursts peak fainter when short (duration–core-level Spearman
  −0.65); v3 gives about −0.25 and cores about 0.13 mag too bright.
- The A04e/A04g fixed margins ranged from 1.7 to 11 real standard errors and
  omitted amplitude.
- Proposed replacement: a real-sized predictive check (one history per era,
  at least 150 replicates) on a waveform block and a cadence block, each
  passing on Hotelling prediction p ≥ 0.01 and |z| ≤ 3.3. v2 random passes
  the waveform block (p 0.17); v2 diverse fails narrowly (0.006); v3 fails
  both arms. Every arm fails the cadence block: synthetic declines carry too
  few estimates near magnitude 10.
- Stopping rule: one calibration grid per family per version; a failed family
  is dropped and X4 validation proceeds on any qualified family and arm.

Next: Codex reviews the targets, builds a v3′ waveform with amplitude–duration
coupling (or empirical templates) and a phase-aligned cadence arm, qualifies
them on A04h, then runs X4 validation on whatever qualifies.

## Completed tranche — A04i joint benchmark and X4 recovery, 8 November 2026

Codex, base `df6fc7e`; D017 and
[`a04i-joint-validation-v1.md`](../docs/protocols/a04i-joint-validation-v1.md).
Waveform and cadence both gate eligibility; failed pairs are dropped before
recovery and any eligible pair proceeds. X4 remains unchanged at `352a09e`.
Independent source-blind delegates constructed a duration–amplitude waveform
and phase-aligned observation profiles; an independent audit checked the
predictive rule. Independence is bounded by the documented input access.

Real/synthetic feature operators now use identical half-open era cuts:
141/123/70 = 334 real episodes. One ten-configuration morphology-only grid
selects one v2 and one v4 phase pair, using fixed objective scales and no
variance search. Each selected pair then receives 150 fresh real-sized
qualification vectors. X4 scoring follows only if both predictive blocks
and all diversity gates pass. No second tuning grid is allowed this version.
Calibration, qualification and recovery have not run at this entry.
No reserved data or real duration–following-gap association is accessed.

Source/calibration update: reviewed source `036c619` is public; its tests
and gitleaks CI pass. Clean-source preparation reproduces the exact 334
features and 398 profiles. All ten configurations completed their 16
real-sized records (480 era histories). Minimum fixed-scale objectives
select unchanged `v2-00` (31.94) and `v4-05` (62.09). These are calibration
objectives, not predictive p-values or X4 results. Every attempt is hashed,
with raw feature vectors and compact summaries in
`data/simulations/a04i_calibration_20261108.json`. The selected configs and
input/calibration chain are frozen before fresh qualification.

Outcome at freeze `939ea77`: all 900 fresh qualification histories completed.
V2-phase passes waveform (p 0.0256), cadence (p 0.240) and all diversity gates;
v4-phase fails waveform and cadence. Independent R reproduces the exact
eligible set and all calibration winners. Only v2-phase enters X4 recovery.

All 4,800 X4 histories, 16,650 metric rows and 9,600 parsed ledger records
completed, with zero extraction errors and no independent/reference causal
ledger disagreement. Both C1 and C2 pass all six ordinary and three gross
decisive cells at magnitude 10; the predeclared preference selects C1/7 d.
The source-blind new waveform did not qualify, so this result uses a waveform
Claude had already studied, with fresh cadence construction and seeds.
Magnitude-9.5 onset coverage fails in later eras; some threshold and
alternative-bias diagnostics are inconclusive. These are retained, not
folded into a blanket validation claim. Independent base R reproduces all
108 decisive metric estimates/intervals/statuses and both global decisions;
maximum difference 6.66e−16. A separate integrity audit verifies all counts,
seeds, hashes and unchanged X4 source. Individual photometry-to-score
calculations were not independently re-derived in this last audit.

The [A04i report](../docs/audits/2026-11-08-a04i-joint-validation.md) links
compact public evidence and preserved R/Python audits. Full regenerable
payloads remain ignored. Final local checks: 206 tests, structural validator
and staged secret scan pass. No reserved data or real focal association was
accessed; A10 stays unfrozen.

Next: Claude — review the magnitude-10 restriction and known-waveform limit,
then specify prefix-causal predictor construction for A10.

Closing result commit: `b3741b3`; tests and gitleaks CI both pass. Board
messages 3027 (full handoff) and 3028 (A10 boundary) record the result;
the reviewed correspondence snapshot is refreshed through those posts.

## Completed tranche — A10c control review and development-fit specification, 8 November 2026

Claude, `main`, base `7d2ec3b`. Owns `scripts/a10c_reaggregate_controls.py`,
`scripts/a10c_truth_associations.py`, their two outputs in `data/simulations/`,
the [A10c memo](../docs/audits/2026-11-08-a10c-controls-review.md) and the
[A10c protocol](../docs/protocols/a10c-development-fit-v1.md), plus the status
updates. Reads the retained A10b scores (outside Git); writes no source code.

Re-aggregating the A10b scores by route shows two defects:

- forecasts without a covered previous gap turned M3−M2 into M1−M0, supplying
  0.0011 of the 0.0032-nat injected-effect gain;
- the duration coefficient is negative under every null case (shared
  end-error coupling, negative in the measured-gap frame), so the gain test
  must not leave the sign free.

D020 proposes a directional, matched M3: β ≥ 0, nested in a comparator that
adds a local gap level. Point marks are primary and P3 is a placebo for
shared slow state. Next comes a 360-trial OC study with slow-state nulls and
gating criteria, then the first real 1910–1959 fit. No real data, reserved
data or real duration–gap association was accessed.

Next: Codex — review A10c, implement §1, run the §2 study, and do the §3 fit
only if §2 passes.

## Completed tranche — A10b model and observation-process development, 8 November 2026

Codex on `main`, base `5476d00`. D018 records Barry's explicit choice to keep
forecast gain confirmatory; the coefficient is secondary. D019 and
[the development specification](../docs/protocols/a10b-model-controls-v1.md)
define this bounded tranche. Root owns integration/docs/pipeline; independent
delegates authored the ledger reference, model component and adaptive stress
controller in disjoint files. Their source access and scope are recorded in
the specification and tests. All component work is integrated.

Initial freeze `bd8fa23`: 255 tests, structural checks and numerical seed
reproduction pass; all 100 short histories match the independent ledger at
both latencies before production scores. The control run was stopped after
17/56 records (8 successful, 9 duration-domain errors). Its full partial
payload is retained; [the compact aborted-run record](../data/simulations/a10b_aborted_controls_20261108.json)
includes every returned trial and marks 39 unfinished tasks explicitly.
An independent exact replay diagnosed marginal end nodes preceding a fixed
onset despite valid point durations. The missing-mark repair retains timing
and all issuances. Re-freeze, repeat concordance and replay all 56 trials with
the original random streams; do not combine successful subsets. No real
photometry is read or real duration–following-gap association fitted here.

Outcome: repaired source `4fc8d2e` repeats all 100 independent concordance
histories at both delays, then completes the full 56-trial original-stream
replay. All 105,509 variant score rows, 272 route populations and 1,360 fits
reconcile; independent audits reproduce 132 gain groups and 36 paired
contrasts exactly. Eight previously successful trials reproduce exactly.
The [A10b memo](../docs/audits/2026-11-08-a10b-model-controls.md) links compact
public tables, independent checkers and a checksum-verified 85-file shared
payload manifest. Local checks: 257 tests, seed validator and numerical
reproduction. No real focal fit or protected-data access occurred.

Injected-effect prefix gain averages 0.00324 nats (trial SD 0.00321); all
eight individual diagnostic intervals include zero. This is recovery of
small average gain, not final power calibration. The AR-gap timing comparator
learns the serial control, but does not represent every hidden activity model.
Three evaluation prefix point-order failures use mark fallback. Strict oracle
matching leaves 25.9% of its scored rows on R0; it is not a skill-loss upper
bound. The two-day diagnostic delays issuance, not training-data availability.

Next: Claude — review these limits, settle the stronger timing-only comparator
and the next real-development-fit tranche before the evaluation freeze.

Closing result commit: `0e45fe4`; scientific-invariant CI and gitleaks both
pass. Board messages 3044 (full handoff) and 3045 (A10 estimand) record the
result; the reviewed correspondence snapshot is refreshed through those posts.


## Completed tranche — A10a, 8 November 2026

Claude, `main`, base `03cfd82`. Owns `src/dnmem/prefix_features.py`,
`tests/test_prefix_features.py`, `scripts/a10_prefix_pilot.py`,
`scripts/a10_precision.py`, their `data/simulations/a10_*` outputs, the
proposed A10 predictor protocol and the A10a memo. X4 unchanged.

Evidence: magnitude 10 qualifies because X4's 0.5 mag arming and
confirmation margins clear the outburst peak distribution only there (9.5:
13–15% of v2 and 6–8% of real outbursts peak within the margin; 10.0: 0.4% and
1–2%). Under the A10 design, waveform misspecification dilutes the mark but
cannot manufacture skill under the null (residual end-error coupling about
−0.006). Prefix X4 on real 1910–1959 rows: 330 forecasts, all with a prefix
episode, prefix − retrospective duration mean absolute 0.05 d; synthetic
retention of the duration–gap correlation 97%. Precision model: at r = 0.12
with 390 evaluation forecasts the paired forecast-gain test has 0.32 power,
the slope test 0.77. No 1960+ data; no real duration–gap association.

Next: Codex reviews the protocol, builds M0–M3 on the ledger and runs the
null/positive/stress/concordance controls; Barry decides the confirmatory
estimand.

Subsequent A10b review: D018 resolves the estimand in favor of forecast gain.
The statement above that waveform errors cannot manufacture skill is
withdrawn: shared end/age error can make a measured duration improve remaining-
time forecasts even when true duration is constant. The 0.05 d prefix versus
retrospective difference measures availability cost, not true endpoint error.



## A10d synthetic screen complete; real fit closed, 8 November 2026

Codex, base `c9aab07`: review A10c, implement a matched directional forecast
family, repeat independent concordance, run the 360-trial OC grid, and make
the first 1910–1959 fit only after the approved gate passes. 1960+ remains
closed pending Barry's explicit evaluation go-ahead. Root owns integration,
statistics, protocol, runner, resource use and eventual gated real-fit adapter.
Disjoint delegates own feature construction, independent reference extension,
model implementation, slow-state streams and source-independent score checks.
All component work is integrated; 296 tests pass. The first 100-history
development concordance and three full-history smokes complete, but their
slow-state checks are superseded: pre-freeze review caught a renewal clock
advancing with the new rather than previous episode's duration/gap. The clock
is repaired and has an exact truth-chronology regression. Source freeze
`8f5df44` repeats 100-history concordance exactly, passes all 296 tests and
green CI, and completes three corrected full-history smokes. Independent
recalculation of their 6,766 scores agrees within 1.1e-13. The forced
six-reference smoke also completes. The fixed 360-trial grid completes
without failures. Its finite screen passes: six null rates ≤.05; power
11/40 (27.5%); joint-MC containment 37/40 null and 34/40 alternative, with
interior calibration also screened. Independent auditing inventories all
823,070 variant score rows and reconciles 360 primary intervals and 80 calibration records;
22,980 representative scores independently agree within 1.14e-13.

D021 and [the amended specification](../docs/protocols/a10d-directional-oc-v1.md)
record the exact positive-age-error counterexample, the limited lagged-mark
interpretation, fixed-baseline offset fitting, six-year inference blocks chosen
before OC outcomes, and matched 58-year references with finite-MC uncertainty.
The 360-trial screen versus formal-size-certification question was put to
Barry before qualification outcomes. Both policies will be calculated without
post-result selection; no automatic real-data action is part of the runner.
No real focal computation or reserved access has occurred. The rate-screen
interpretation remains pending, so the first real fit is closed. Full outputs
are archived outside Git with checksums; compact tables and the
[A10d audit](../docs/audits/2026-11-08-a10d-directional-oc.md) are committed.
Next: Claude — review A10d, including the positive-artifact counterexample,
state sensitivity and finite-gate interpretation; Barry's policy choice is
still needed before the real development fit.


## A10e first real development fit complete, 8 November 2026

Barry explicitly accepted the finite observed≤5% screen after the A10d
report; D022 resolves the prior pending question. Adapter/profile freeze
`b80c4a9` preceded native opening at 10:49:36 UTC and the first real fit at
10:50:31 UTC. Twelve native hashes and all qualified A10d source bytes match.
Both delays give 330 issued/eligible forecasts, with exact independent
ledger/evidence concordance. All six model variants and profile diagnostics
complete; frozen parameters retain SHA-256
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.

Primary β=.04660, conditional likelihood support [.00652,.08667], in-sample
M3−M2 gain .00787 nats/issuance. P3 fits zero in all variants. Endpoint-mixture,
q-only and two-day sensitivities retain positive offsets. These are
development likelihood results, not held-out skill or physical identification.
Independent verification recomputes all 1,957 variant score rows within
7.46e-14 and reconciles routing, likelihood totals and profiles. The 310-test
suite, validator and source-freeze CI pass. Full outputs are archived outside
Git; parameters, compact profiles and the
[A10e report](../docs/audits/2026-11-08-a10e-first-development-fit.md) are committed.

No model was retuned and no 1960+ data was opened.
Next: Claude — review A10d/A10e and prepare the evaluation freeze tied to
the exact parameter hash; Barry must authorize later data access.


## A10f development review and evaluation protocol, 8 November 2026

Claude, `main`, base `ccea39b`. Owns `scripts/a10f_development_calibration.py`
and its output in `data/simulations/`, the
[A10f memo](../docs/audits/2026-11-08-a10f-development-review.md), the
[A10f evaluation protocol](../docs/protocols/a10f-evaluation-v1.md), D023 and
the status updates. Reads the retained A10d trial records and the consumed
pre-1960 development ledger (both outside Git). Writes no forecasting code.

A10d and A10e are accepted as executed, with all D021 amendments. Findings:

- Real issue ages are early (median 1.9 d against 40 d gaps). End-error
  coupling is negative here, so the directional bound does its job, although
  it is not a general theorem.
- The real development likelihood ratio (5.19) is reached by 5/220 gated null
  histories (0/40 structured), 12/40 injected-effect histories and 14/80
  slow-state histories.
- With the lagged mark at zero, the simulator disfavours a slow shared state
  by about 8 to 1. Mechanism stays unidentified, and frozen P3 equals M2 on
  the evaluation block.
- Power conditional on the development fit is 4/12, about one chance in
  three at best.

The protocol fixes sealed access, the single six-year-cluster test, S1–S6 and
the interpretation table before access. That table includes an informative
negative and the CM92 era split. Pre-access work: runner, independent checker,
adapter fixtures and a synthetic rehearsal. No 1960+ data accessed.

Next: Codex — review A10f, build the runner, checker, fixtures and rehearsal,
and freeze; then Barry's go-ahead opens 1960–2017.


## A10g evaluation freeze complete, 8 November 2026

Codex reviewed A10f and implemented the amended sealed evaluation protocol.
Final source freeze `fc409738222ded5a9bf78288c969e956b59d23f4` completes the
synthetic native-format 58-year rehearsal: 377 primary issuances, 345 joint
rows, all S1–S6 diagnostics complete. The independent checker verifies all
2,230 score rows within 6.13e-14, the primary interval, routing, chronology
and all 120 source identities. All 342 tests, validator, staged scan and
Python 3.11–3.13 CI pass on the exact source freeze.

The first two rehearsals (`79b5eae`, `bfb2bc6`) and their numerical failures
remain preserved. The final secondary-only profiler uses a fixed method by
nuisance dimension, strict optimizer success and objective/nesting checks.
Both prior streams complete under that method. No original A10d source,
frozen parameter or primary statistic changed. A10f interpretation corrections
and genuine joint association are recorded in D024 and the
[A10g report](../docs/audits/2026-11-08-a10g-evaluation-freeze.md).

Compact evidence is in `data/provenance/a10g_rehearsal_fc40973/`; full outputs
and the 697,603-byte protocol-only deposit package are verified outside Git.
The metadata/manifest are in `data/provenance/a10g_protocol_package/`.
No deposit, later-data request or live authorization has been made. The
reviewed protocol requires Barry's timestamp choice and explicit go-ahead
before opening 1960–2017. 2018 onward remains reserved.

Next: Barry — choose Zenodo first or a Git tag, then authorize the single run;
or retain the closed block.


## A10h active: authorized evaluation after native-format repair

Barry selected Zenodo first, then open (D025). The exact protocol is
published at DOI 10.5281/zenodo.24053338, public bytes verified, and authority
`6e26eba` was pushed before live transport. The first attempt failed before
any primary result on literal `None` uncertainty metadata. No outcome/count/
coverage summary was inspected; untouched status is consumed (D026).

Native adapter owner implements only exact-token missing uncertainty; an
independent reviewer confirms complete downstream non-use and synthetic
invariance. Freeze the minimal repair, rehearse and audit, then commit the
repair-bound authority and continue under the same forecast/test. No raw
release, parameter change, altered population rule or 2018+ access occurs.
The failed attempt and its receipts remain archived outside Git.

Next: Codex — complete the independently reviewed format repair and sealed run.


## A10i complete: the single frozen forecast-gain criterion is met

9 November 2026 (Hobart). Source 5e39aeb, execution d7151e0. The completed
1960–2017 comparison has 441 issuances: +0.01653 nats/issuance, 90% cluster
interval [0.00495,0.02812], 10 six-year blocks. All five fallback zeros remain.
Independent numerical verification covers 2,641 score rows within 1.91e-13;
response scope, hashes, prefix chronology and original context/cache pass.
All 344 tests, validator and supported-platform source-freeze CI pass.

The report deliberately places the later-era and type/within-type
inconclusive intervals beside the primary. Joint S1 does not identify
mechanism; predictions empirically overcover. The claim is incremental
information for SS Cyg over the specified frozen timing baseline. D027
records that interpretation, with the post-access native-format repair and
consumed status retained. No 2018+ access or model retuning occurs.

[Full result](../docs/audits/2026-11-09-a10i-sealed-evaluation.md), compact
aggregates and independent audits are committed. All raw replies, original
context/cache, source and full outputs are verified internally outside Git;
protocol DOI 10.5281/zenodo.24053338 is the only new external release. The
single-run access record is marked completed. Aggregate summaries are public; no raw-data deposit, new event catalog or
manuscript release is made.

Next: Claude — review the real result and frame the paper with the era/type
and mechanism qualifications beside the headline; keep 2018 onward closed.


## A10j: result reviewed; paper framing seeded

9 November 2026. Claude accepts A10i. The interval, every variant, the eras
and the routes reproduce from saved scores with separate code. The result
survives dropping any block (0.0132–0.0194) and an SE up to 1.43 times larger.

Exploratory, post-result:

- about a fifth of the gain is a level correction, because the frozen M2
  forecasts 1960–2017 gaps 4.6% too long;
- the information is carried by long versus short outburst type, with
  nothing detectable within type;
- the predeclared type rule scored low because its type indicator was
  uncentred under the fixed baseline, an interaction both agents missed.

The living-paper scaffold, `manuscript/estimands.md` and a 25-claim ledger
are in place. No products are drafted yet.

[A10j memo](../docs/audits/2026-11-09-a10j-result-review.md); D028.
2018 onward stays closed.

Next: Codex — independently check C11–C13 and C20–C25, review
`manuscript/estimands.md`, and set up figures and the makedoc build; Claude
then reads CM92 and Cannizzo (1993) in full and drafts the products.



## Completed A10k: independent claim checks, figures and build

Codex, base `b96bd5b`. Independent delegates own C20–C23 verification,
C11–C13/C24–C25 verification, and isolated document-build/reference plumbing.
Root owns the interpretation specification, ledger, captions, contribution
record and final visual QA; the first audit delegate subsequently owns figure
production. Frozen forecasting code/parameters/outputs and the closed
2018+ block remain unchanged.

All requested numerical calculations reproduce by separate likelihood,
quantile and block-arithmetic routes. Interpretations are narrowed before
captions: global recentering is not drift removal; in-sample type preference
is not exclusive attribution; the restriction is on the type component;
negative lag does not exclude a coexisting dominant slow component; the SE
failure boundary is exclusive. Evidence/code are anchored at `fd4f313`.

The article/supplement/brief remain clearly marked figure/build previews;
Claude owns substantive drafting after reciprocal agreement on estimands.
No paper/data release, new archive request or venue decision is made here.

All 348 tests, the repository/claims/figure checks and the three-profile
document build pass. Every preview PDF page was inspected. The original
scalar score audit still passes; all 120 historical source hashes and all
26 current qualified forecasting files were checked separately. The public
figures reproduce byte for byte. C40/C41 remain provisional for Claude's
source/novelty work. D029 and
[the A10k memo](../docs/audits/2026-11-09-a10k-claims-and-figures.md) record the
accepted calculations and interpretation corrections.

Next: Claude — review the revised estimands, finish C40/C41 source checks,
then draft the three products using the figure/build previews.

## A10l: sources checked; all products drafted

Claude, 9 November 2026. D029's narrower interpretations are accepted in
full (D030). CM92's Table 4 and Fig. 5 conventions were re-read on the
original scan, and C40 is now supported. Cannizzo (1993) was read in full. It
explains alternation through disc depletion, and links recurrence time with the
long-to-short ratio through slow parameter changes. No quiescence contrast
after long versus short outbursts was found in it, so the products say
"compatible with", never "confirms".

The novelty refresh found one held-out point-forecast precedent, Grigorievskiy
et al. (2014, V363 Lyr, a single test outburst). The claim is now qualified as
preregistered and probabilistic, and C41 stays provisional pending an
independent search check.

First full drafts of the article, supplement, brief and agent guide are in
`manuscript/text/`. Every quoted number is bound to the ledger. Endpoint
coupling is added as a stated limit. Authorship, venue and Zotero entries
for two references without DOIs remain Barry's. No archive request, retained-run
read or 2018+ access occurred.
[A10l memo](../docs/audits/2026-11-09-a10l-sources-and-drafts.md).

Next: Codex — semantic review of all four products against
`manuscript/estimands.md`, an independent C41 search check, and a
rendered-PDF check; then Barry reviews the drafts.

## Completed A10m: semantic, novelty and rendered-draft review

Codex, base `2ec3534`, 9 November 2026. Bounded independent delegates review
article/captions, supplement/brief/agent guide, and the narrowed novelty claim.
Root owns integration, interpretation/evidence adjudication and PDF visual QA.
Delegates write review evidence only; root owns manuscript edits. No archive
request or frozen-model/result change is authorised by this review. The 2018+
block remains closed. The intended handoff is corrected review drafts for Barry,
with scientific or source uncertainties made explicit.

The corrected products pass the independent changed-passage rechecks. Primary
results, qualified scientific source and parameter bytes are unchanged. C41
now supports a bounded independent search account with ADS/full-text and
indexing limits; no universal priority is asserted. The article/supplement/
brief PDFs have 13/9/2 pages. All 348 tests, claims, repository, figure and
render checks pass. See D031 and
[the A10m review](../docs/audits/2026-11-09-a10m-draft-review.md).

Next: Barry — review the drafts and decide authorship, venue and observer credit.

## A10n: external review triaged; research round reopened

Claude, base `f48f0e2`, 9 November 2026. Barry commissioned an independent
GPT-6 Pro review of the drafts. It finds the study coherent but incremental,
with three essential issues: the score's observation model (E1), endpoint
information in measured duration (E2) and a censoring branch (E3). It
recommends an expanded study. Claude accepts all three in substance.
- E3 cannot move the result: dropping all six censored forecasts gives
  0.01678 against 0.01653.
- The A10d null settings, with real X4 extraction, give mean gains of at most
  +0.00046 against 0.0165.
- A real-data split by end precision is uninformative (ρ = 0.03).
- The triage proposes an observation contract under coarsening at random,
  bounded diagnostics (R1) and a sealed multi-star expansion with a
  state-versus-duration model ladder. The drafts are not revised until the
  research settles the claims.
- No archive request; the retained 1960–2017 primary run was read for
  exploratory aggregates only; 2018+ stays closed.
[A10n triage](../docs/audits/2026-11-09-a10n-external-review-triage.md).

Next: Codex — agree or amend the triage and the §3 contract, then run R1
(censor fix, alternative observation scores, endpoint dose–response and
truth target, Figure 1 illustration, per-setting simulation table).


## Completed R1: observation contract, censoring and endpoint diagnostics

Codex, base `de186da`, 9 November 2026. D033 accepts the external review and
amends A10n before diagnostic scoring. Decisive reported states and the X4
kernel are working compatibility treatments, not established latent-onset
likelihoods. Timing-only CAR and one-day posterior widths do not prove those
stronger claims. The independent audit identifies the `_clip` conflict
envelope and kernel slope-Jacobian issue.

Bounded ownership: separate delegates implement the future-v4 censor audit,
alternative-score runner, endpoint dose grid and example/simulation table;
root integrates the contract, independent numerical checks and report. No
existing qualified forecasting file, frozen run or manuscript is rewritten.
The 2018+ and other-star archives remain closed.

Completed under D034. Protocol/implementation freeze `0594146`; audit-only
numerical recovery `93e52e6`. Censor correction changes zero original outcomes.
Point-density gain is +0.015404 [0.003443, 0.027365]; finite clips are missing
for 434 forecasts, so interval/kernel checks cannot cover the original sample.
All eighty synthetic histories are reconciled with the original pre-scoring
failure retained; no dose creates a positive all-issued mean gain. This is a
bounded fixed-simulator check, leaving the latent-onset observation model open.
Figure 1 and all 480 prior simulation comparison rows reproduce. See the
[R1 audit](../docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md)
and aggregate evidence. Claims C42–C46 await Claude review; the product texts
and PDFs were not rewritten.

Next: Claude — review R1 and the observation target before drafting the R2 cohort,
stronger-baseline and measurement design; no new archives yet.

## R2: design proposed

Claude, 9 November 2026. C42–C46 reproduce under separate code and are now
supported. The 434 missing lower clips come from an X4 bug of Claude's: the
clip searched from the previous peak, inside that outburst's bright phase. A
corrected decisive bracket (gain-free) exists for 818 of 845 confirmed SS Cyg
episodes, median width 1.16 d.

The [R2 design v0](../docs/protocols/r2-design-v0.md) proposes:

- the latent threshold crossing as the target;
- an assumption ladder: A1 bounds with no coarsening model, and the A1 + A2
  proper interval score;
- X5;
- a decoupled forecast that never uses the estimated end crossing, as the G1
  test;
- the B0–B2 baseline ladder;
- a sealed multi-star test with catalogue-only screening.

Interpretation rules are fixed in its §6 before any R2 score. R2a–R2c are
Codex's legwork; R2d integrates and brings one G3 question to Barry.

Next: Codex — amend and freeze the R2 design (v1), then run R2a (X5, gain-free
diagnostics, DF/fluence/B1/B2 implementations) and R2c (cohort screen, power
simulation); no new archives.

## R2a/c preparation completed

Codex, 9 November 2026. D036 amends v0's assumptions and freezes preparation;
D037 records the results. Sources/configuration were committed before each
batch at `fe6dbf4`, `f0049dd` and `956d33c`. See the
[R2a/c report](../docs/audits/2026-11-09-r2a-preparation-and-r2c-review.md).

X5 restores 818 available / 805 eligible confirmed report windows. Their
geometry does not establish latent containment or CAR. DF waits for its faint
anchor and retains 307 of 441 evaluation issues, with only 291 jointly markable
across the matched clocks. Twelve current/history clock discrepancies need
review. An exact-report counterexample shows that removing a fitted end does
not remove cadence information or make DF a decisive mechanism test.

B0–B2, the observed-span flux proxy and scoring bounds are implemented. Nine
finite controls and an independent Gaussian-conditioning/score reconstruction
pass. No real R2b model fit, gain or duration–gap correlation was computed.

The literature/catalogue queue contains eight nominees, two holds, five
exclusions and one opened control. None is newly qualified. The 35×2,000
score-level study gives fitted-rule power 0.711 at nominal gain .010 and
1,100 forecasts; serial-block nonidentity interval coverage falls to 0.7265.
G2 is unestablished. No new-star observations or SS Cyg 2018+ rows/counts were
accessed. Product texts and PDFs remain unchanged; new claims await review.

Next: Claude — review the preparation and settle R2b clock/history, matched
population, crossing assumptions and dependence/precision rules before real gains.

## R2b rules settled

Claude, 9 November 2026 (D038). See the
[review](../docs/audits/2026-11-09-claude-r2a-review.md) and the
[R2b rules](../docs/protocols/r2b-execution-v0.md).

- C47–C51 are supported by separate checks; C52 stays provisional.
- All 165 v1 DF aborts were caused by single reports between magnitudes 9 and 10,
  never by a decisive-bright report. Aborting only on decisive-bright reports
  schedules all 441 evaluation issues (and all 330 in development).
- Past DF gaps now run from each past emission's own anchor, so the twelve
  anchor discrepancies disappear.
- The target is the last upward threshold crossing before the first decisive-bright
  time. Under exact photometry and A0, the X5 window contains it.
- Cadence-lag artefacts have a computable ceiling: about 0.007 nats in 1960–2017.
  R2b adds that ceiling, a cadence-covariate sensitivity and a negative-control
  observing-rate mark.
- The headline contrasts H1–H3 are fixed before any score.
- The sealed test drops star × six-year clustering for star × 18-year, or star-level
  if a calibrated simulation shows under-coverage. Its primary (DF clock, B2, X5
  interval score) is fixed now.
- No fit, score, archive request or 2018+ read occurred.

Next: Codex — amend and freeze r2b-execution-v1, regenerate DF features under
the decisive-abort and harmonised-anchor rules, then fit and score R2b; no new archives.

## R2b completed: positive estimates, inconclusive state-space contrasts

Codex, 9 November 2026 (D039–D041). [Execution report](../docs/audits/2026-11-09-r2b-exploratory-execution.md),
[v2 protocol](../docs/protocols/r2b-execution-v2.md), source freeze `5fb69c6`.
The initial `939208e` gain-free preparation failure remains preserved; one exact
coincident delayed issue now has the earliest original representative. DF and
matched point therefore have 440 evaluation issues, 431 empirically scored.

H1 is +0.007535 nats on 432 cases; H2 +0.004276 on 431; H3 -0.003076.
Both six- and twelve-year 90% intervals cross zero for every headline. H2's
conditional sample bounds are not confidence limits. No second confirmation,
absent-effect or physical-memory claim follows.

B2 converges consistently but has lower observed baseline means than B0/B1
within each population: it is preselected, not empirically strongest. The
positive observing-rate secondary is a sensitivity, not a validated negative
control. The Fisher index is not an upper bound, and visit aggregation does not
prove latent containment. Frozen H1–H3 and future data boundaries are preserved.

Independent numerical reconstruction passes all fourteen models, 24,348
scores, objectives, extrema and block summaries. All 516 tests pass. Current
and historical anchors match scheduled observed anchors, with earlier-fallback
qualifications retained. New claims C53–C60 stay provisional. No new archives,
2018+ access, paper rewrite, contact or release occurred.

Next: Claude — review R2b and baseline adequacy, then settle R2d's measurement,
dependence and precision design before any G3a request or manuscript rewrite.

## R2b reviewed; R2d rules proposed

Claude, 9 November 2026 (D042). See the
[review](../docs/audits/2026-11-09-claude-r2b-review.md) and the
[R2d rules](../docs/protocols/r2d-sealed-design-v0.md).

- C53–C58 and C60 are supported by separate routes; C59 stays provisional. Claude
  withdraws the D038 ceiling and containment shortcut.
- B2 is misspecified: a random-walk level with a vague prior and no mean
  reversion, 13–19 nats worse than B0 in development. It is retired as the
  sealed comparator.
- Quiescent intervals were shorter in 1960–1983 (27.5 and 31.0 days against
  34.5–39.6), so B0/B1 over-forecast. Causal recalibration fixes most of it.
- Era-shifted marks gain by correcting that level. This explains the rate result
  and about 30% of the point-clock duration gain. The DF span barely drifts.
- Drift-guarded duration stays positive on both clocks (six-year t 1.7–2.3);
  rate falls to t 1.34. Exploratory.
- The score test is about 1.4–1.7 times stronger than the gain t on SS Cyg, as
  theory predicts. With guards, about 970–1,550 forecasts give 80% power at
  KL 0.004.
- Proposed for R2d: DF span mark, causally centred; B0R base; score-test
  primary; gain as effect size; small-cluster correction and stress envelope by
  simulation. G3a goes to Barry after R2d. Products stay paused.
- No archive request, 2018+ read or product rewrite occurred.

Next: Codex — check C61–C64, challenge and freeze R2d v1, then run the precision
stress simulation; no new archives.

## R2d independent review and precision screen completed

Codex, `main`, base `6a94c9d`. Owns the independent C61–C64 audit, additive
point-log-gap simulation helper/runner/tests, R2d v1 protocol/configuration,
interpretation/status records and resulting small aggregate evidence. Three
bounded delegates separately check arithmetic, methodological claims and the
synthetic learning chain. Their inputs and independence limits are documented.
No new archives, new-star counts, 2018+ records or paper-product edits.

C61–C64 arithmetic is reproduced; D043 narrows causal, interval and score-test
interpretations. The source/configuration freeze precedes the 35 × 2,000 trial
screen. Both gain and score procedures are reported, with no method chosen on
these outcomes. Forecast gain remains the default confirmatory claim. The
point-log-gap study cannot qualify observational extraction or calendar yield.

Outcome: freeze `67c45ab` committed before the grid and pushed; all 70,000 trials complete
without failed fits. C61–C64 arithmetic accepted with narrowed interpretations.
The dual-statistic screen does not establish a robust required N. At eight
stars/1,100 clean forecasts, whole-star score power is .818 and frozen-gain
power .3665; delayed/noisy and persistent cases are weaker. No universally
passing score procedure is selected. Original sources, parameters and R2b
outputs remain hash-preserved. C65–C66 await Claude in the
[precision report](../docs/audits/2026-11-09-r2d-precision-results.md), alongside
the [independent design review](../docs/audits/2026-11-09-r2d-design-review.md).
Paper products remain paused; all new-star and 2018+ access gates stay closed.

Next: Claude — review the R2d screen and settle the scientific claim and a
development-only feasibility proposal before any new-star access request.

## R2d reviewed; G3a early-record proposal awaits Barry

Claude, 9 November 2026 (D044). See the
[review](../docs/audits/2026-11-09-claude-r2d-review.md) and the
[G3a proposal](../docs/protocols/g3a-early-record-feasibility-v0.md).

- C65–C66 are supported (all 35 trial hashes and rejection counts reproduce),
  and D043's narrowing of C61–C64 is accepted.
- The pooled strict-null score rejection is 4.96% [4.50, 5.46]. The per-cell
  "at most 5%" screen fails an exact 5% test with probability 0.473.
- Forecast gain never rejected without the score moment (0 of 70,000; C67).
  Proposed: association first, then forecast gain, in fixed sequence. The gain
  claim's power is unchanged and the association claim's roughly doubles.
- Star count binds feasibility.
- G3a proposal:
  - pre-1990 visual records for the eight nominees plus the two eclipsing holds,
    measured gain-free;
  - qualification: at least 40 timing-supported marked development forecasts,
    X5 eligibility of at least 0.7, B0 convergence and the morphology screen;
  - G3b requested only with at least six qualifying stars and at least 1,100
    projected test forecasts.
- No observation, archive request or 2018+ read occurred.

Next: Barry — decide G3a (open pre-1990 records for the ten candidate stars).


## G3a approved tranche completed — 10 November 2026

Barry approved the ten-star pre-1990 proposal exactly: “yes, approved as proposed.
Continue.” Codex, `main`, base `9988e16`, owns source-bounded acquisition,
qualification integration, v1 protocol, source freeze and aggregate feasibility.
Three bounded delegates independently check C67/sequence logic, implement the
unmarked qualifier, and implement/review eclipse/transport guards. No delegate
is authorized to retrieve new-star records. All tests use invented fixtures.

C67's empirical counts reproduce; future power identity/FWER claims are narrowed.
G3a v1 fixes catalogue thresholds/common margin1, outcome-supported≥40,
window eligibility≥.7, unmarked B0 convergence and morphology. Both holds receive
an explicit two-reduction/two-night/synthetic-dip robustness screen. Source/config
and46focused checks precede access. Six-star cases are frozen separately within
the same tranche. No G3b or SS Cyg2018+ opening, manuscript rewrite or release.

Outcome under source freeze `d827313`: all ten acquisitions and qualification
runs complete,183,538 selected validated visual rows, zero qualified stars.
Only SS Aur reaches40 supported issuances; it fails the predeclared operational
long-bright-run exclusion. The other gates are not relaxed. All ten ignoring
every gate project367.2 issuances over36years from102 observed development
opportunities in1980–1989. G3b must not be requested under this specification.
No mark fit, duration-gap association or real forecast gain was computed.

The six-star supplement finishes16,000 trials, zero failed fits; clean1,100
association rejection is.7675 and gain.331, with weaker stressed cases.
Independent raw parsing/dedup/ordinary mask and supplemental recount find no
mismatches, with shared-API/optimizer/morphology/eclipse limits explicit.
C68–C69 await Claude in the [feasibility report](../docs/audits/2026-11-10-g3a-feasibility-results.md).
Raw bytes, records and full synthetic trials remain outside Git; later data
and manuscript products stay closed/paused.

Next: Claude — review the failed transfer and recommend the scientific next
step; preserve the failed screen and do not request G3b.

## G3a reviewed; multi-star expansion stops — 10 November 2026

Claude, `main`. [Review](../docs/audits/2026-11-10-claude-g3a-review.md), D046,
aggregates `data/provenance/g3a_claude_review/checks.json`. Gain-free rerun of the
frozen DF chain on the retained pre-1990 pages and on the open SS Cyg record; no
request, fit, score or later-period information.

- C68 and C69 supported. The eight ordinary stars' counts and all 16,000 six-star
  trial lines reproduce.
- C70 (provisional): conversion of confirmed 1980s outbursts into supported
  forecasts is 92% for SS Cyg against 21% for the ten candidates.
  - 542 of 822 clocked candidate forecasts lack a covered previous gap. The mark
    requirement removes four.
  - Without history and mark requirements: 41% conversion, 724 over 36 years,
    five stars with 40 forecasts.
  - A later split does not help.
- C71 (provisional): SS Aur's 101-day run is four outbursts bridged by estimates
  near the 13.5 threshold. It is not a plateau.
- Recommendation: stop the expansion. Report G3a in the SS Cyg paper as a
  preregistered transfer test that failed for a measured reason. A generality
  study with deep CCD surveys would be a new project for Barry to decide.

Next: Codex — check C70–C71 by a separate route, then begin R2 integration with
estimands first.

## R2/G3a manuscript integration complete — 10 November 2026

Codex, `main`, base `93c48cf`; integrated drafts `c29c607`, evidence stamps
`ed20258`, decision D047. C70–C71 are supported with narrowed definitions and
scope; independent lattice/native-parser routes and parent reruns agree.
[Integration report](../docs/audits/2026-11-10-r2-paper-integration.md) records
checks and limits. Article 13 pages, supplement 18 including cover/references/
figure section, brief 2 A4 pages, guide updated. New figures/tables use aggregates;
original sources, parameters and figure bytes remain intact. A separate semantic
review's effect-input and false-rearming wording corrections are resolved.

580 tests, structure/claims checks, saved-score reconstruction, generated assets,
makedoc build and staged secrets scans pass. No new request, observational fit or
score. Candidate 1990+ and SS Cyg 2018+ remain closed. No release follows.
Board handoff: thread 153, post 3174; reviewed snapshot exported.

Next: Claude — review the integrated drafts and narrowed claims, then send Barry
reviewed products. No further archive work is proposed for this paper.

## Integrated drafts reviewed; products to Barry — 10 November 2026

Claude, `main`. [Review](../docs/audits/2026-11-10-claude-integrated-draft-review.md), D048.
- The drafts are faithful to the estimands and the ledger. An independent Sonnet check of the
  supplement and guide found five minor issues, all fixed.
- Codex's C70–C71 corrections are accepted.
- Edits: a plainer article abstract and §4.2 SS Cyg contrast, brief units and transfer contrast,
  roles, and the agent guide's raw-input boundary.
- Checks pass. Brief 2 pages, article 13, supplement 18.
- Open for Barry: release decisions, and two inline citations that still need verified entries.

Next: Barry — review the article, supplement, brief and agent guide.

## Reconstruction from first principles begun — 10 November 2026

Claude, `main`. Barry's method for revising a first draft. Step 1 (working abstract, abstract,
main message, display plan) and step 2 (the one-page paper) are drafts in `manuscript/reconstruction/`.
Barry decided OJAp as the target, sole authorship with an AI-declaration placeholder (D049) and a
writing rule: plain positive statements, with limitations gathered in one section. Discussion is on
board thread 159.

Next: Codex — review steps 1–2 on thread 159.



## Reconstruction review complete; reconciliation before step 3 — 10 November 2026

Codex, `main`, base `9cd8999`; review/proposals `be25a7a`, D050 (proposed).
Thread 159 post 3188 answers all five questions. The review supplies exact
estimands placement replacements, a 585-word one-page alternative, a 129-word
abstract and a 23-word main message. Counts, conditional direction and R2 clock
identity match the existing evidence. A separate semantic check's conditional
clock and log/bounded-history corrections are resolved in the proposal.

Fig. 4B is supported as a descriptive issuance/peak count ratio under named
streams and dates; H3 needs a separate contrast label/panel. OJAp policy and
five comparison-paper identities are independently checked; exact official
class/BST retrieval remains open. Product texts, canonical estimands and frozen
scientific sources/results stay unchanged. No observations, fits, scores or
archive requests. All 580 tests, structure/claims checks, frozen-source hashes
and staged secrets scan pass. Reviewed board snapshot exported at close.

Next: Claude — reconcile steps 1–2 and the proposed rules/display plan before
expanding the OJAp article. No Barry approval is needed for that reconciliation.


## Third-draft semantic review complete — 11 November 2026

Review commit `81e5a75`; board thread 159 post 3207.

Codex, `main`, base `030c55d`, thread 159/3195. Review:
`docs/audits/2026-11-11-third-draft-semantic-review.md`, with a 38-group
sentence/caption audit in `data/provenance/third_draft_review/`.

C04 arithmetic is supported: 330/307/307 metadata counts; a duration doubling
scales exp(mu) by 1.0880015159653311 at fixed timing history. SS Cyg reference 490
is also correct, comprising 275 before 1960 and 215 in1960–1989. Ledger evidence,
limits and reproduction are updated, preserving every fitted value/source.

Corrections before sign-off: C56 prose conflates observer-night rate with raw
end-cadence; Figure 1's caption clips; its schematic changes sigma between models
and its UTC post-check chronology starts late; Figure 4A mislabels all pre-1990
reference support as development. Other targeted fixes concern the matched H3
population, G3a versus exploratory SS Cyg status, completeness/mechanism language
and the conditional observation-model premise. D051's concentrated limitations
remain the writing rule. The main result and numerical forest values reproduce.

580 tests, structure, claims, generated-asset and makedoc checks pass; these do
not detect the semantic and PDF defects. Product sources/PDFs, canonical
estimands, all 26 qualified sources, parameters and outcomes remain unchanged.
No new archive request, observation, fit or score. Literature retrieval was
Kimura bibliographic metadata only; no post-2017 curve or later archive summary.

Next: Claude — repair the targeted text/figure/layout issues and rebuild, then
align the brief and guide with the corrected article and return a focused diff.

## Third-draft corrections applied; brief and guide aligned — 11 November 2026

Claude, `main`, `7da81c8` (C05 restamped `e11c5e7`), thread 159/3211. Dispositions:
`docs/audits/2026-11-11-third-draft-corrections.md` (D054).

Every D053 finding was checked against code or evidence, then applied. C56 now reports the
rate-replacement mark and the duration gain over an end-cadence-adjusted B2 separately.
Fig. 1B uses the common frozen sigma and, correcting a sign error the review missed, places the
duration forecast later after the drawn long outburst. Fig. 1C uses exact UTC commit times, and
label, figure and caption now share one page. Fig. 4A carries the available-pre-1990 label.
The brief is rewritten to the third draft with a new two-panel figure; the agent guide gains
traps 15–18. Article 20 pages, technical record 6, brief 2. 580 tests, claims, lint, render,
figure and table checks pass. No data opened, no fit or score.

Next: Codex — review the D054 diff (C56 wording, new brief, Fig. 1B).

## D054 diff reviewed; brief wording remains — 11 November 2026

Codex, `main`, base `e7d6c6b`; review:
`docs/audits/2026-11-11-d054-diff-review.md`, thread 159.

Article, technical record, agent-guide and figure corrections accepted. C56's
rate replacement and cadence-adjusted duration comparison are separate and
correct. Figure 1B now has the common frozen spread and the positive direction;
its full caption fits. The revised reference label and UTC timeline match their
evidence; both brief pages render legibly.

Three brief consistency corrections remain: define C04's 9% as the fixed-history
full quiet-clock contrast (and omit the ambiguous 1.7% transformation), and
restore the inconclusive predeclared C07/C08 outcomes plus baseline adequacy and
unknown upload/revision dates (the latter in the existing Limits list).
The review supplies exact copy. No new analysis or design change is
needed. Product texts, PDFs, estimands and claims are unchanged this turn.
580 tests, manuscript/seed/render checks and frozen hashes pass; no new data,
fit or score. Protected later records stay closed.

Next: Claude — apply the three brief corrections, inspect the rebuilt two-page
PDF, then hand the products to Barry.

## Brief corrections applied; products to Barry — 11 November 2026

Claude, `main`, responding to `docs/audits/2026-11-11-d054-diff-review.md` (thread 159). The
brief now defines the 9% contrast as the model's median full quiet spell with timing history held
fixed, reports the inconclusive 1993–2017 and long/short secondaries (C07, C08), and lists timing-
baseline adequacy and unknown historical upload dates among its limits. Codex's wording, with the
dashes replaced by commas. Still two pages. Claims, lint, render and brief checks pass. No data,
fit or score.

Next: Barry — the article, technical record, brief and agent guide are ready for his review.

## Step 4 (final detailing) complete — 11 November 2026

Claude, `main`, `438c4b4` (C05 restamped `08aa51c`), thread 159/3226 (D055). References verified
and added (two manual entries for the inline-only citations; seven new works with specific uses);
AAS author-year style; hard edit with the main message restated in different words; captions lead
with their messages; abstract corrected on the secondary tests (the 1960–1992 half was not
inconclusive). A Sonnet cold read informed the text-only clarity pass: internal labels out of the
main text and Fig. 3, terms defined at first use. Article 20 pages, brief 2. All checks pass. No
data, fit or score.

Next: Codex — semantic check of the step-4 diff.

## Step-4 semantic review — 11 November 2026

Codex, `main`, base `4471a6c`, thread 159/3226. Review:
`docs/audits/2026-11-11-d055-semantic-review.md`.

The revised abstract, C04 size, B2 preselection, planning comparison, retained
brief corrections and numerical/contrast identities are accepted. Figure
relabeling changes no values or populations, and the current PDFs render well.

Two methods clauses need correction: catalogue confirmation must be separated
from the stricter causal issuance rule, and the CAR premise must cover the full
reporting/selection process, rather than reporting times alone. The new
Heitjan–Rubin entry also needs a citation key; its literal prose mention leaves
it absent from the rendered References. Exact copy is in the review. Product
files, estimands, claims and scientific outputs are unchanged this turn.

All 580 tests, seed/manuscript/claims/render checks and frozen hashes pass.
No new observations, real fits, forecast scores or archive requests. Protected
later records remain closed.

Next: Claude — apply the two methods clarifications and citation link, rebuild
and inspect the affected pages, then hand the products to Barry.
