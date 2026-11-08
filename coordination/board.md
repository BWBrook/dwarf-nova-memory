# Shared task board

Updated: 7 November 2026. Discussion lives in the `dwarf-nova-memory` board
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
| A10a | Restriction review, prefix-causal predictors, precision | Proposed, not frozen | Claude protocol, ledger code and pilot; Codex models and controls | [A10a memo](../docs/audits/2026-11-08-a10a-prefix-predictors-review.md), [proposed protocol](../docs/protocols/a10-prefix-causal-predictors-v1.md); magnitude 10 structural (0.5 mag margins clear the peak distribution only there); causality costs ~0.05 d on real 1910–1959 rows; single-star forecast-gain test ~1/3 power at r≈0.12, estimand decision with Barry |
| A05 | Audit remaining provisional pilot targets | After A03 | Split targets | One feasibility dossier per target, including failures |
| A06 | Reproduce one historical descriptive result | After A04 | Rotate implementer/reviewer | Document data/version/definition mismatches |
| A07 | Decide restricted-episode versus richer observation model | After A05/A06 | Scientific lead with agents | Gate B/C decision and revised estimand |
| A08 | Implement observational M0, then M1 | After A07 | Agent implementer + other reviewer | Censoring, boundary propagation, calibration |
| A09 | Add past-only M2/M3 and identifiability simulation | After A08 | Rotate roles | Same state architecture, no future smoothing |
| A10 | Freeze evaluation | Predictor ledger proposed (A10a); confirmatory estimand awaits scientific lead | Scientific lead | Cutoffs, ledger, final targets and score |

## Current blocking information

The requested SS Cyg stream through native JD 2436934.0 is acquired in 12
hashed exports, with 72,635 unique native IDs. Early coverage varies sharply.
The three boundary disagreements are adjudicated. Conditional synthetic
screening fails qualification; extraction/eligibility, confirmation, usable
forecast counts, other targets and operating characteristics remain unresolved.
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

