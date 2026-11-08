# A10m independent support-product semantic review

Reviewer: Codex. Base: `2ec353493b941ef190b63d74267375f29e119af6` (9 November 2026).
Scope: `manuscript/text/supplement.md`, `brief.md`, `brief_figures.md` and `for-agents.md`.
The reviewer read the current interpretation specification, claims ledger, value bindings,
committed aggregate evidence, relevant source contracts and the preceding audits. This is a
semantic and contract review, not a new fit or a repeat confirmation. No raw archive reply,
observer identity, per-issuance table, live acquisition or 2018-onward information was accessed.
No manuscript, ledger, frozen source, parameter, receipt or committed result was edited.
Literature/priority verification belongs to the separate A10m literature review; statements from
those sources were checked here for agreement with the existing ledger/specification only.

The primary numbers and the main restrictions on their interpretation agree with the evidence.
There is no finding here that requires changing the frozen comparison. Seven material wording or
reproduction corrections are needed before semantic sign-off; three smaller precision points follow.

## Material findings and minimal corrections

### SR1 — Define the transformed timing predictors used in the equations (P2)

**Locations:** supplement 18–19, 82–98; guide 59.

The supplement defines `q` as the preceding quiet gap and `L` as the mean of earlier log gaps, then
uses `gamma_1 q + gamma_2 L` with the frozen standardized coefficients. In the implementation,
`q = (log(previous_gap) - previous_center) / previous_scale` and
`L = (mean(earlier_log_gaps) - earlier_center) / earlier_scale`. Only after the latter transformation
is a missing L set to zero. Raw L's training mean is about 3.671, not zero. Reading the current
definitions literally produces the wrong forecast and gives the reported slopes the wrong units.

**Evidence:** `src/dnmem/directional_forecast.py:53–100`; primary M2/M3 `centers`, `scales` and
`coefficients` in `data/fits/a10e_1910_1959/frozen_parameters.json`; C04.

**Minimal correction:** define q as “the standardized log preceding covered quiet gap” and L as
“the standardized mean of up to six earlier covered log quiet gaps; impute zero after
standardization if none.” State that both use frozen development centres/scales. Alternatively
name the raw gaps separately and give the two transformations immediately before the equations.
The guide may retain its short vocabulary entry if it points to these complete definitions.

### SR2 — Do not report an unperformed unseen-waveform recovery failure (P2)

**Location:** supplement 51–55, especially “It failed on an unseen waveform family”.

The subject is X4, making this sound like an X4 recovery benchmark that failed. The source-blind
waveform failed the morphology qualification gate before candidate recovery scoring. Consequently
X4 recovery on that family was not tested. This distinction matters: the retained known-waveform
pass is narrow, but it is not accompanied by a measured X4 recovery failure on that unseen family.

**Evidence:** `docs/audits/2026-11-08-a04g-x4-independent-validation.md:96–117,197–211`;
`docs/audits/2026-11-08-a04i-joint-validation.md:8–19,194–197`.

**Minimal correction:** “The unseen waveform family failed qualification before X4 recovery could
be tested; magnitude-9.5 diagnostics failed in later eras.” Retain the known-waveform restriction.

### SR3 — Name the different comparator for the within-class LR (P2)

**Location:** supplement 230–234.

The introductory sentence calls all three numbers statistics “against the level-only model”.
The first two are against level only; 0.17 is the extra LR from adding within-class duration to
the class model. The type-plus-within LR against level only is 14.8668, not 0.17.

**Evidence:** C21; `data/provenance/a10j_postresult_review/summary.json`,
`type_information.refits_frozen_M2_nuisance_free_level.1960-2017`:
type 14.6983554, continuous 11.6863726, type-plus-within 14.8667841,
`lr_within_given_type` 0.1684287. A direct subtraction of the committed LRs gives 0.1684287.

**Minimal correction:** “With M2's historical parameters fixed and a free common level, the
evaluation likelihood-ratio statistics are: class versus level only, 14.7; continuous log duration
versus level only, 11.7; within-class duration added to class, 0.17.”

### SR4 — The exact rounded SE multiplier 1.427 still passes (P2)

**Locations:** supplement 173–177; guide 37–39.

“Fails once the standard error is multiplied by 1.427 or more” is literally false. The exact
failure boundary is 1.4270501885272726 and the criterion passes strictly below it. At exactly
1.427 the lower bound remains +0.000000581474 nats. The supplement's next sentence correctly
distinguishes 42% from 43%, but it does not repair the preceding inclusive inequality. The guide's
“fails at ... 1.427” repeats the same issue. This is precisely the trap both products say they avoid.

**Evidence:** C25; `data/provenance/a10k_independent_review/secondary.json`,
`C25_block_statistics`; direct arithmetic using the committed primary estimate/SE and independently
stored t critical value. No scores were recomputed or fit.

**Minimal correction:** “The strict failure boundary is approximately 1.42705 times the standard
error; a 42% increase passes and an exact 43% increase fails.” Keep the existing fixed-estimate,
fixed-critical-value and dependence limitations. Say “approximately” beside a rounded boundary.

### SR5 — The brief claims complete flare recovery and instantaneous end knowledge (P2)

**Locations:** brief 26–29, 33–38.

“Found every flare” claims completeness that neither extraction qualification nor the real record
establishes; missed-event inference is not implemented. “At the moment each flare ended” moves
issuance to a latent endpoint, whereas the actual forecast is issued only at the later
observation-time end confirmation and conditions on survival to that landmark. The phrase “only
what was known at the time” also needs an observation-time qualifier, because historical upload
and revision availability is unknown. The retrospective caption elsewhere helps, but the methods
should not give an operational reading of the procedure.

**Evidence:** estimands 17–23,34–36; AGENTS scientific invariants; supplement 59–65,89–93;
`src/dnmem/prefix_features.py:76–120`; `src/dnmem/extract_x4.py:186–241`;
`docs/05-statistical-design.md:49–60`.

**Minimal corrections:**

- “**Marked flares in the archive.** ... A method tested first on simulated records estimated
  when the selected flares began and ended.”
- “When the observation-time rule confirmed each flare had ended, ...”
- Add a short explicit sentence: “We used the observations' recorded dates; we do not know when
  every historical report was actually available.” This need not expand the general discussion.

### SR6 — Keep the brief's post-result class reading at the fitted-model level (P2)

**Location:** brief 56–58.

“The flare's type matters more than its exact length” reads as an allocation of information to a
physical/explanatory feature. The calculation establishes greater in-sample likelihood for a
long/short indicator than for linear log duration under a specified fixed nuisance model and free
level, with no absence or equivalence test for within-class effects. “The type rule was
handicapped by how it was set up” implies the weakness was explained by coding; the common-level
calculation establishes sensitivity to level/coding, not a unique explanation. The final warning
about a second test is correct and should remain.

**Evidence:** estimands 93–107; C21/C22; A10k explanatory restrictions and exploratory aggregate
`limitations.no_within_type_equivalence_or_absence_test`,
`type_lr_comparison_is_nonnested_in_sample` and `estimated_level_and_refits_reuse_evaluation_outcomes`.

**Minimal correction:** “In analyses made after seeing the result, the long/short model fitted the
test record better than a model using exact log duration. Adjusting the shared forecast level also
changed the class rule's score. Those analyses cannot count as a second test.” This describes the
actual calculations without requiring technical detail in the brief.

### SR7 — Reproduction instructions overwrite committed evidence and understate dependencies (P2)

**Locations:** supplement 307–322; guide provenance table 71–75 and checks 124–130.

The supplement's A10j command has no `--output`, so its current default overwrites the committed
`data/provenance/a10j_postresult_review/summary.json` used by the claims ledger. This is a reproduction
instruction with an avoidable mutation of the evidence being checked. Its prose also says “The first
command needs the retained completed run”, although all of the first four commands need private
inputs; A10j and both A10k scripts additionally use retained 1910–1959 development files. These
dependencies are absent from the guide's “Same run” entries. A clone containing only public
aggregates can check the figures/claims/build but cannot reproduce these raw-dependent calculations.

**Evidence:** `scripts/a10j_postresult_review.py:113–126,240–256` (default committed output and
both private populations); `scripts/a10k_exploratory_audit.py:213–216`;
`scripts/a10k_secondary_audit.py:279–285`; `scripts/check_a10g_evaluation.py:278–304,521–530`.
The guide's saved-score checker command itself has a scratch output and makes no archive request.

**Minimal correction:** add `--output outputs/a10m_reproduction/a10j_summary.json` (or another fresh
scratch destination) to the A10j command; explicitly state that the first four commands require the
retained evaluation run and the last three of those also require the retained development run.
List the development input in the guide's A10j/A10k provenance rows. Put the public-only check/build
commands in their own runnable group or label them as such. No new acquisition is needed.

## Smaller precision points

**SP1 — Future protocol is a proposal, not a settled design.** Brief 67–68 says the unopened records
are being kept “for a future test that combines several stars”; guide 144–147 says the block “should
serve” as a multi-star stratum. The latter is a recommendation; the brief sounds decided. Estimands
155–157 says this milestone makes no future protocol/data-opening decision. Use “a possible future
test, potentially combining several stars” or “we propose ...”. The roughly 65 forecasts in the
guide are correctly labelled a planning assumption and were not checked against later data.

**SP2 — An independent extraction will not by itself distinguish temporal change, observing change
and sampling.** Guide 142–143 says it “would separate them”. It would test sensitivity to extraction
and observing data; deciding between changes in the star, the observation process and sampling
requires further assumptions/design. Replace with “would test how sensitive the later-segment
result is to the extraction and observing record.” No new comparison is authorized by this wording.

**SP3 — Clusters are fixed-length day blocks.** Guide 63 calls them “six-year calendar clusters”.
The code and supplement use `6 * 365.25` days from the fixed origin, not exact calendar boundaries.
Use “six-year (6 × 365.25-day) blocks anchored at ...”. This does not change any reported value.

## Sentence/paragraph disposition inventory

Line numbers below refer to base `2ec3534`. Every result-bearing paragraph, table block or
methodological assertion in the four assigned products is covered. Adjacent sentences sharing
one calculation are grouped; different estimands or dispositions are separated. “Pass” means
the sentence's object and scope agree with the listed evidence, not that all underlying physical
assumptions have been validated. “Source handoff” means that primary-literature checking is
owned by the other A10m reviewer.

Evidence abbreviations:

- **E1:** `data/provenance/a10i_evaluation_1960_2017/primary.json` and `summary.json`.
- **E2:** `data/provenance/a10j_postresult_review/summary.json`.
- **E3:** `data/provenance/a10k_independent_review/exploratory.json`.
- **E4:** `data/provenance/a10k_independent_review/secondary.json`.
- **E5:** `data/fits/a10e_1910_1959/frozen_parameters.json` (primary variant).
- **E6:** `data/provenance/a10i_evaluation_1960_2017/native-audit.json`, `archive.json`;
  A10i audit chronology/provenance and D025–D027.
- **E7:** `data/simulations/a10f_development_calibration_20261108.json` and
  `data/simulations/a10d_20261108/report.json`.
- **X:** the prefix/extractor/directional-forecast source contracts explicitly cited above.
- **B:** `manuscript/figure-data/claim-values.csv`, `manuscript/value-bindings.csv`, figure manifest.
- **L:** C40/C41, `references/evidence.csv`, A10l source audit and estimands 126–153.

### Supplement

| Lines | Result-bearing content checked | Governing evidence | Disposition |
|---|---|---|---|
| 15–17 | Issuance, completed duration, subsequent quiet-gap target | Estimands 17–23; X | Pass; issuance is the confirmation landmark |
| 18–19 | q and L definitions/missing level | C04; E5; X | **SR1**: give transformed covariates |
| 20–23 | Outcome brackets; censoring; conditional score and paired gain | X; estimands 17–23 | Pass |
| 24 | exp(mean gain), 1.7% | C02; E1; direct exponentiation | Pass; ratio is geometric likelihood, not accuracy |
| 25–29 | Untruncated clock scale; coverage bounds; JD/day/log-duration units | C11/C21; E4/E5; X | Pass |
| 35–39 | Bounded pre-2018 requests, service splitting, selector, 63/500479/81/249356 counts | C15; E6; sealed protocol | Pass; counts expressly evaluation-window only |
| 41–49 | X4 threshold/crossing mixture/systematic floor and confirmation/arming | `extract_x4.py` source; A04f/A04g | Pass as implemented method; no completeness guarantee follows |
| 51–55 | X1–X3 failures, X4 qualified family, unseen family and threshold limits | A04g/A04i qualification audits | **SR2** for unperformed unseen-waveform recovery; other restrictions pass |
| 59–65 | Emissions, delay, retained false/repeat emissions, prefix causality, nonpositive marks, prior-window margin | X; C09 | Pass; current-episode description is a concise code summary |
| 69–78 | Retrospective outcomes, survival exclusions, zero exclusions, first censoring event | X; E1; E6 | Pass; onset bracket must be before the selected censor boundary |
| 82–89 | M0/M2/M3 equations and predictor scaling | C04; E5; X | **SR1** for q/L; x and beta direction pass |
| 89–93 | Conditional likelihood and common fallback/remaining forecast zeros | X; C03; E1 | Pass |
| 95–99 | Frozen M2, offset fit with M2 fixed, coefficients and parameter prefix | C04; E5 | Pass; numeric values match primary, not delay variant |
| 101–107 | Endpoint coupling, earlier negative null coefficients, positive-information construction and sensitivity limits | D020/D021; estimands 34–36 | Pass; explicitly avoids sign theorem and claims no removal |
| 111–117 | Issue window, cluster CR1, t df, positive lower rule, one statistic | C01; E1; sealed protocol | Pass; one-sided 95% lower is the stated two-sided 90% endpoint |
| 121–127 | Finite power 11/40 and exact interval, pooled 3/220, shared streams, simulated reference mean | C30/C31/C33; E7/E1 | Pass; no iid pooled error-rate or certified-size claim |
| 131–146 | DOI, failure, repaired acquisition/concordance/primary chronology; unused field; independent repair; unchanged files | C05; E6; D025/D026 | Pass against recorded provenance; completed post-access repair is explicit |
| 148–151 | Two ledger/evidence implementations; 2641 score rows; numerical tolerance; independent CR1 recomputation | C01/C03; E6; A10i/A10j | Pass as recorded checks, not physical truth validation |
| 157–171 | Primary/era/class/sensitivity/timing-baseline table | C01/C06–C10; E1/E2; B | Pass; primary only is confirmatory; 436 joint-valid count matches E1 |
| 173–174 | Ten blocks, df9, eight positive blocks, LOO means and positive-issuance share | C01/C25; E1/E4 | Pass; LOO values are correctly called means |
| 175–177 | Literal SE failure threshold, 42/43% arithmetic, dependence limit | C25; E4 | **SR4** for rounded inclusive failure claim; rest passes |
| 179–180 | P3=M2 because development lag beta0; placebo uninformative | E5; E1 | Pass; no mechanism inference |
| 184–189 | M3 coverage bounds, denominator, partial identification, sample/population distinction, overcoverage and descriptive deciles | C11; E1/E4 | Pass; does not claim calibrated physical-onset coverage |
| 193–202 | Evaluation-refitted M2 held fixed; LR3.841 conditional supports; current/lag estimates | C12/C13; E1/E4 | Pass; not labelled calibrated CIs |
| 204–206 | Full rank, condition1.79, joint zero inclusion, no nonidentifiability | C13; E4 | Pass |
| 210–215 | Slow-state analytic counterexample coefficients/correlation/sign/dominance | E4 analytic counterexample; estimands 73–78 | Pass; explicitly not fitted to SS Cyg or a rival empirical result |
| 219–220 | Exploratory section reuses outcomes; intervals conditional; no second confirmation | C20–C25; E3 | Pass |
| 222–229 | Best level/scale reduction, mark-implied level, mean-centred score contrasts, small interaction | C20; E2/E3 | Pass; approximately additive ordering stated; not called drift-free or causal |
| 230–234 | Type/continuous/within-type LR comparison | C21; E2/E3; B | **SR3**: third LR has different reference model |
| 236–237 | 14% untruncated working-clock scale; smaller development contrast and similar fits | C21; E2/E3 | Pass; model scale, not observed/remaining gap |
| 238–242 | Frozen type mean offset; shared evaluation-fitted level; full/late gains; 181/245 short cases shorten | C22; E2/E3 | Pass; restriction correctly limited to type component |
| 243–245 | Era type contrasts/LRs; no change test | C23; E2/E3 | Pass |
| 246–249 | Log-duration lag correlations; conditional long-after-long/short proportions; repeat-record limit | C24; E2/E4 | Pass; not unique independent outburst catalog |
| 253–255 | Development beta/LR; in-sample and overlapping prior record | C14; E5/E7 | Pass |
| 259–269 | CM92 sample, correlations, split and cycle algebra | C40; L | Internal agreement/source handoff; additional cycle numbers not independently re-read here |
| 277–282 | Earlier cycle/estimator/extractor/concordance/parser analyses and their replacement | D020–D026; A04/A10 audits | Pass as historical correction record; threshold qualification remains bounded |
| 284–298 | A10k interpretation corrections and primary unchanged | C08/C12/C13/C20–C25; E3/E4; D029/D030 | Pass; note SR4 accidentally reintroduces the recorded rounded-boundary trap |
| 300–303 | Prior point-forecast precedent and narrowed novelty wording | C41; L | Internal agreement/source handoff; provisional status retained elsewhere |
| 307–323 | Reproduction commands, retained run, archive/protocol and public aggregate scope | Current CLI contracts; E6 | **SR7** for output mutation and private-input dependencies; protocol/archive identity agree |

### Brief and brief figure

| Lines | Result-bearing content checked | Governing evidence | Disposition |
|---|---|---|---|
| brief 7–11 | System geometry, brightness/timescale and monitoring history | Primary-literature/official-source assertions | Source handoff; no independent external verification here |
| brief 13–17 | Short/long classes, alternation, older duration/quiet relation; association is not forecast validation | C40; L; estimands | Internal agreement/source handoff |
| brief 21 | Primary positive interval, late/type inconclusive, retrospective post-access repair and no physical memory | C01/C05/C07/C08; E1 | Pass; appropriate limits beside figure headline |
| brief 25–29 | Interval-algebra artifacts; honest information set and log score | Estimands; X | **SR5** for unknown historical availability qualifier; score description otherwise passes |
| brief 33–35 | “Found every flare”; simulated extractor test and endpoints | A04i; X | **SR5** completeness overclaim |
| brief 36–38 | Training period, instantaneous end issuance, timing-plus-duration comparison | C04; E5; X | **SR5** issue landmark correction |
| brief 39–41 | Freeze/protocol predates evaluation requests; 441 forecasts | C01/C05; E1/E6 | Pass with the explicit repair disclosure directly below; not an untouched claim |
| brief 45–49 | Mean gain/range and rule; geometric 1.7% | C01/C02; E1; B | Pass as geometric likelihood of scored bracket/survival evidence; “likelihood of the recorded evidence” is more precise than “probability on what happened” if space allows |
| brief 50–53 | Failure on unused field, repair without observation/forecast-rule change, retained attempt | C05; E6 | Pass |
| brief 54–55 | Later smaller estimate/inconclusive; frozen type rule inconclusive | C07/C08; E1 | Pass; makes no era-difference/disappearance claim |
| brief 56–58 | Type “matters more” and rule “handicapped”; no second test | C21/C22; E2/E3 | **SR6**: describe in-sample fit and level sensitivity |
| brief 59–61 | Disc-drainage and slow-state alternatives; no mechanism discrimination | Estimands 140–151; C12/C13; E4 | Internal agreement/source handoff for model physics; no mechanism confirmation |
| brief 65–68 | Incremental SS Cyg information, no other-star generalization, future closed block | C01; estimands 32–36,155–157 | Pass for bounded SS Cyg result; **SP1** for future protocol stated as settled |
| brief 72–75 | Named human/AI roles and public traceability | Project role record, existing code/audits/ledger | Consistent with record; parent owns final model/version identity check |
| brief 79–80 | Historical 705-flare source and disc-model reference | C40; L | Internal agreement/source handoff |
| brief_figures 1 | Asset inclusion only; no independent result sentence | Figure manifest; B | Pass; public asset/aggregate checker passed |

### Agent guide

| Lines | Result-bearing content checked | Governing evidence | Disposition |
|---|---|---|---|
| 15–18,27–28 | Draft status, evidence precedence and supported/provisional meanings | D030; ledger schema | Pass |
| 32–36 | Primary answer, interval/population/date and repaired-access status | C01–C05; E1/E6; B | Pass |
| 37–39 | Protocol sensitivities, block signs and rounded SE threshold | C09/C25; E1/E4 | **SR4**; other claims pass and remain one comparison |
| 40–41 | Later/class inconclusive; no era test or disappearance | C07/C08; E1 | Pass |
| 42–44 | Exploratory class fit/level contribution/coding sensitivity; no held-out status | C20–C22; E2/E3 | Pass in context of explicit traps89–94; “favoured” means in-sample likelihood here |
| 45–46 | Mechanism not identified, alternation and slow-state compatibility | C12/C13/C24; E4 | Pass |
| 47–49 | Historical association/classes/alternation; qualified probabilistic novelty and precedent | C40/C41; L | Internal agreement/source handoff; provisional explicitly stated |
| 55–58 | X4 threshold, coverage, confirmation issue and prefix boundary | X | Pass |
| 59–62 | Model meanings, P3 equality, common fallback and type/within coding | C04/C08/C22; E5; X | Pass as short vocabulary once SR1 definitions are supplied |
| 63 | “Calendar” six-year clusters | C01; E1; inference code | **SP3**, fixed day-length blocks |
| 64–65 | Fit/evaluation/closed boundaries and untruncated model-clock meaning | Estimands; E5/E6 | Pass |
| 71–75 | Inputs/code/output provenance for fitted, primary, post-result and independent calculations | E1–E7; current scripts | **SR7**: A10j/A10k also require private development files |
| 76–77 | Figure and literature provenance | B; L | Pass as navigation; source verification separately owned |
| 79–82 | Exact selection and fallback zeros versus436 joint-valid sensitivity | C01/C03/C09; E1 | Pass on this realized population; not a different primary |
| 89–90 | Global recentering leaves drift possible and reuses evaluation | C20; E3 | Pass |
| 91–92 | In-sample class preference lacks exclusive attribution/equivalence | C21; E3 | Pass |
| 93–94 | Type component differs from whole rule restriction | C08/C22; E3 | Pass |
| 95–96 | Negative lag no mechanism allocation; conditional profiles and repeat pair | C12/C13/C24; E4 | Pass |
| 97–98 | Strict boundary and no dependence validation | C25; E4 | Pass as warning; SR4 corrects conflicting earlier summary |
| 99–104 | Saved-score audit versus historical source identity; receipt immutable; no acquisition rerun | Current checker contract; E6; A10k | Pass; independently reading the checker confirms it reads saved run files only |
| 105–106,111–113 | Metadata differs from source audit; CM92 re-read; priority qualifiers | C40/C41; L | Internal agreement/source handoff |
| 107–110 | DOI does not timestamp repair; draft/release/data opening boundaries | C05; D025/D026/D030 | Pass |
| 114–117 | Physical model does not make this forecast result; compatible rather than confirms | Estimands 140–151; L | Internal agreement/source handoff |
| 118–120 | Realized gain exceeds simulation mean; Monte Carlo/model specificity and no physical effect-size comparison | C01/C33; E1 | Pass |
| 124–130 | References refresh, public figure check, saved-score audit, claims/build instructions | Current CLIs and Makefile | Commands agree; network refresh is explicitly labelled; **SR7** for clearer public/private split |
| 134–138 | Source/parameter identity, zero-failure audit, data boundary, poisoned-future test | Source contracts, C01/C05, E5/E6 | Pass as required invariants; full suite/poisoned test not rerun by this review |
| 142–143 | Later weakness not causally allocated; independent extraction “would separate” causes | C07; estimands | **SP2** for overpromised discrimination |
| 144–147 | Future class test needs coding/intercept design; future65 as planning estimate | C21/C22; estimands155–157 | Pass as recommendation/planning assumption; align future-status language with **SP1** |
| 148–151 | P3 uninformative; latent-state comparison proposal; endpoint coupling and partial sensitivities | E5; C12/C13; D021 | Pass; no new result or authorization implied |
| 152–153 | DOI-less bibliographic entries and provisional novelty status | L; existing manual references | Source handoff; no live bibliographic lookup here |

## Verification performed

The following read-only checks passed at base `2ec3534`:

```sh
python3 tools/claims.py check manuscript/claims.csv manuscript/text/supplement.md manuscript/text/brief.md manuscript/text/brief_figures.md manuscript/text/for-agents.md
python3 manuscript/figures.py --check
```

The ledger checker reported 26 claims (25 supported, one provisional), zero errors and zero warnings.
The figure checker reported five figures, ten assets and no private-input requirement. These checks
do not detect the semantic issues above. Independent arithmetic from committed aggregates gave
1.66709% for the primary geometric likelihood increase, 13.81055% for the class clock-scale change,
4.57153% for the best-level clock-scale reduction, and the SR3/SR4 comparator/boundary checks.

The A10j/A10k scripts were inspected rather than executed: they refit saved data and A10j's default
output mutates committed evidence. No acquisition command, new fit, full test suite or raw-run
reproduction was run for this document-only review. The scope is completed by this report; the
parent A10m reviewer owns integration and any manuscript corrections.
