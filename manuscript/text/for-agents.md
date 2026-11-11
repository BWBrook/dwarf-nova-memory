---
document: agent-facing paper
study: SS Cyg working-score result and measurement/transfer reassessment
status: step-4 detailed draft (D055) after the third draft and review corrections (D052–D054); Barry reviews before release
human_paper: manuscript/text/main.md (article with appendices; + supplement.md technical record, brief.md)
claims_ledger: manuscript/claims.csv
interpretation: manuscript/estimands.md
governing_docs: [AGENTS.md, coordination/decisions.md, manuscript/estimands.md]
authority: Barry W. Brook decides release, submission and any new protected-data opening
updated: 2026-11-11
---

# SS Cyg for agents: evidence, reproduction and interpretation

This is the entry point for an agent arriving cold. Read `manuscript/estimands.md` before quoting
any result. The article (methods, results, one limitations section and appendices A–G), the
technical record (`supplement.md`: superseded analyses and reproduction) and the brief are
detailed drafts, not a paper release. The article uses AAS author-year references
(`manuscript/csl/the-astrophysical-journal.csl`, locally restricted to print publishers only for
books); its main text names the report-window comparisons and drift recalibration in words, while
the evidence files keep the labels R1, R2b, H1–H3 and "guarded".
The original frozen calculation is preserved. Later work changes what we can infer from it;
it does not replace it with a more favourable result. An evidence file and its receipt outrank
this guide: reconcile any disagreement rather than modifying a historical receipt.

## 1. What the study found

- **Original frozen decision.** Adding fitted duration raised the specified working interval
  score by [0.0165]{.C01 .V001} nats per issuance (90% six-year cluster interval
  [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}; [441]{.C01 .V004} issuances). This met the
  sole predeclared criterion. With timing history fixed, doubling duration lengthens M3's
  untruncated median clock by about [9]{.C04}% (exp(beta ln 2 / s) = 1.088; C04). The X4 intervals are fitted extraction summaries, not known bounds
  on physical onset; a proper latent-onset observation likelihood is not established.
  The run followed a post-access parser repair (C05). The later segment and the frozen class
  rule were inconclusive (C07–C08).
- **Post-result reassessment.** Point rescoring stays positive (C44). New report windows and
  clocks produce positive but inconclusive working gains: H1 [0.0075]{.C55 .V009} and H2
  [0.0043]{.C55 .V013} nats. These change the baseline, population and observation assumptions;
  they are exploratory, not replication or a causal decomposition. On the DF clock an
  observer-night rate used *in place of* duration gained [0.0030]{.C56} nats; separately, the
  duration gain over a B2 base refitted with raw end cadence stayed at [0.0043]{.C56} (C56).
  Rolling guards (duration recentring plus baseline-level recalibration) attenuate an analogous
  point-clock gain without measuring a fraction of C01 (C62–C63).
- **Precision.** Simulations distinguish a positive residual score moment from improved
  predictions by a development-trained forecast (C65–C67). More association power is not more
  forecast-gain power, and a test sequence needs validity under both full nulls.
- **Transfer.** A prospectively frozen pre-1990 feasibility screen qualified [0]{.C68 .V031}
  of [10]{.C68 .V030} candidate stars. No candidate duration effect was fitted and no later
  candidate test data were opened. Independent diagnostics support named attrition counts
  (C70) and SS Aur's threshold-run structure (C71), not a unique cause or impossibility for all
  other methods. The multi-star expansion stops for this paper.
- **Physical interpretation and novelty.** No result identifies disc memory or another mechanism.
  CM92's duration–gap correlation, alternation and class split are prior art (C40). C41 records
  a bounded search for a preregistered probabilistic held-out duration test, not universal priority.

## 2. Information and access boundaries

| Material | Status and allowed use |
|---|---|
| SS Cyg before 1960 | Open development; original coefficients fitted here |
| SS Cyg 1960–2017 | Original test completed; later analyses must be labelled exploratory |
| SS Cyg 2018 onward | Closed: no request, row, count, coverage summary or plot |
| Ten G3a candidates before 1990 | Open development for the completed gain-free feasibility screen |
| Those candidates from 1990 onward | Closed: no G3b request follows the failed screen |
| Other archives or targets | No new access is authorized by this paper revision |

Raw acquisitions, identities, event catalogues and per-issuance outputs stay outside Git. Public
files contain small aggregates and hashes. No data or manuscript release follows from a successful
build. Authorship, venue and the AAVSO observer-credit/terms review remain release decisions.

## 3. Vocabulary and distinct estimands

| Term | Meaning |
|---|---|
| X4 | Original frozen magnitude-ten extractor; its bytes and failed benchmarks stay unchanged |
| C1/7 d | A gap longer than seven days breaks coverage |
| Original issuance | Observation-time end confirmation; predictors use only the preceding 400 days |
| M0 / M2 / M3 | Constant / timing-history / timing-plus-duration frozen lognormal clocks |
| Original fallback | Missing covered previous gap: both models use M0, hence zero gain |
| X5 window | New raw-support report window; availability alone proves neither containment nor CAR |
| DF clock | Observed decisive-faint anchor; its bright-span mark omits an interpolated end estimate |
| B0 / B1 / B2 | Windowed history / autoregressive / state-space baselines; B2 was preselected |
| H1 / H2 / H3 | Fitted-end gain / observed-clock gain / paired difference of gains |
| Guarded statistic | Post-result rolling-level and mark-centring diagnostic, not a new confirmation |
| Supported G3a issue | Satisfies the frozen timing, history, mark and outcome requirements |

Keep three premises separate: A0 association/completeness/risk set, A1 physical containment or
genuine censor survival, and A2 the complete normalized coarsening-at-random (CAR) observation
kernel. A report margin does not prove any of them. Under stated containment, resolved-event
infimum/supremum bounds are deterministic sample bounds, not confidence intervals. A censored
survival contrast has a different target. Fixed-cutoff mixed bounds and lower-bound-backoff working
scores must not share a label silently. Cluster intervals have further dependence assumptions.

DF removes a literal shared fitted end. It retains cadence-dependent anchor lag, shared reports
and selection. Retention ratios or the difference between clock gains cannot allocate causal
measurement effects. Historical upload/revision dates are unknown throughout: this is
observation-time retrospective analysis, not operational replay.

## 4. Provenance map

| Result | Reproduction route | Public evidence / claims |
|---|---|---|
| Original parameters | A10e fit, development only | `data/fits/a10e_1910_1959/frozen_parameters.json`; C04, C14 |
| Original frozen scores | `scripts/check_a10g_evaluation.py` on the retained repaired run | `data/provenance/a10i_evaluation_1960_2017/`; C01–C15 |
| Original exploratory fits | A10j / independent A10k scripts | `data/provenance/a10k_independent_review/`; C20–C25 |
| R1 observation/end diagnostics | R1 scripts and protocol, separate scratch outputs | `docs/audits/2026-11-09-r1-*.md`; C42–C46 |
| R2 preparation and fits | R2a/c and R2b protocols and execution receipts | `docs/audits/2026-11-09-r2*.md`; C47–C64 (C52 and C59 provisional) |
| Synthetic precision | Frozen R2d grid and six-star supplement | `docs/audits/2026-11-09-r2d-precision-results.md`, G3a report; C65–C69 |
| Gain-free transfer | G3a source freeze d827313, no later-data request | `docs/audits/2026-11-10-g3a-feasibility-results.md`; C68 |
| Attrition / SS Aur | Separate lattice and native-parser reconstructions | `data/provenance/g3a_review_independent/`; C70–C71 |
| Figures | `manuscript/figures.py` and normalized CSVs | `manuscript/figure-data/`, `manuscript/figures/manifest.json` |
| Prior art | Source scans and bounded search records | `references/evidence.csv`, A01/A10l/A10m memos; C40–C41 |

The ledger supplies exact evidence paths and reproduction commands. Its `basis` and `limitations`
columns matter as much as `status`. Supported can mean numerical reproduction via shared legacy
extraction APIs; it need not mean an independent observation model or source annotation.

The primary selects issue times in [2436934.5, 2458119.5), delay zero, point-duration marks, and all
eligible issues including fallback zeros. R2b has distinct scheduled and scored populations;
a coincident DF issue uses the earliest original representative. Never substitute a convenient
matched population for the original denominator.

## 5. Traps caught during review

1. **A working score is not an established physical-onset likelihood.** X4's statistical interval
   and clipping do not turn its endpoints into hard observing bounds. Put this beside C01.
2. **The DOI does not timestamp the repair.** Preserve the first failed access, exact-token repair,
   independent invariance checks and later execution authority. Do not call the run untouched.
3. **Outcome bugs do not license rewriting a freeze.** R1 preserved the missing clips; X5 fixed a
   lower-clip search in a later, explicitly exploratory analysis. The censor repair changed none
   of the saved primary forecasts, but remains a real correction (C43–C45).
4. **The iid endpoint-dose experiment is not a general error bound.** It tests that added Gaussian
   mechanism in the fixed simulator, not every shared-error or observing pathway (C46).
5. **Observation cadence is still a possible pathway.** A cadence counterexample exists (C48).
   The Fisher calculation is a local sensitivity index, not a ceiling. Rate is not a validated
   negative control. Raw-support windows still need ordered witnesses and containment.
6. **A global mean does not model drift.** Recentring and rolling guards change specified
   contrasts; they do not measure a fraction of C01 or remove arbitrary slow co-variation.
7. **The state-space baseline was preselected, not strongest.** Its worse development likelihood
   does not identify a unique failure mechanism or the true latent process (C61).
8. **Association and gain have different nulls.** A trained forecast can overshoot a real effect
   and lose score. Zero gain-without-score rejections in a grid proves no general nesting theorem.
9. **A failed transfer screen is not a null effect.** G3a fitted no candidate effect. Projections
   assume fixed early-record rates; they do not bound a new model or later archive coverage.
10. **Name reduction, period and landmark.** C70's frozen 1980s ratio uses hold reductions for
    support and raw confirmed peaks as denominator. Whole-pre-1990 fade lags are visit-clock
    differences, not physical end errors. Six mark losses before usable-outcome selection become
    four after it. Do not mix these cohorts.
11. **An operational flag is not a subtype or causal diagnosis.** C71 finds four separated bright
    report clusters, not four independently annotated ordinary outbursts. The selected pooled
    faint median is not a same-era quiescent baseline.
12. **Class fit preference is not exclusive attribution.** The type and continuous models are
    nonnested; a small extra within-class statistic is no equivalence or absence result.
13. **Round once, from evidence.** The SE failure boundary is strict, not an inclusive safe rounded
    multiplier. Counts, score differences and interval endpoints have separate value bindings.
14. **Prior work stays prior.** “First held-out forecast” is false without qualifiers; the bounded
    novelty search found an earlier held-out point forecast (C41). Cannizzo's model is compatible with,
    rather than a prediction or confirmation of, this particular duration–gap result.
15. **Rate replaced duration; cadence adjusted the base.** C56 holds two separate saved fits:
    observer-night rate as a replacement mark (0.0030), and duration above a B2 base refitted
    with raw `c_end` (0.0043). No joint rate-plus-duration fit exists. The third draft conflated
    them; D053 caught it.
16. **Supported cycles, not completeness.** C70's counts show that SS Cyg supplies enough
    supported, well-covered cycles under the frozen rules. They do not measure completeness
    against the physical event population, and a future test needs sufficient supported cycles,
    not SS Cyg's exact coverage. The Fig. 4A reference (490) spans the available pre-1990 record,
    including 215 forecasts from the 1960–1989 held-out era.
17. **Model contributions are not total predictability.** M2's gain over M0 is about seven times
    duration's (C02, C10). That ranks the frozen models; it does not decompose all available
    predictability. The class indicator's higher in-sample likelihood (C21) motivates a future
    frozen type predictor and favours no physical mechanism.
18. **H3 is a matched contrast.** It pairs DF and fitted-end gains at the same delayed issuances;
    it is not H2 minus the headline H1. The C04 doubling ratio concerns exp(mu), not the
    survival-conditioned remaining wait, and has no short/long class meaning.

## 6. Reproduce without reopening archives

```sh
python3 manuscript/figures.py --check
python3 scripts/check_a10g_evaluation.py \
  --directory outputs/a10h_live_repair_5e39aeb \
  --output outputs/reproduction/score_audit.json
python3 scripts/check_g3a_attrition.py \
  --output outputs/reproduction/c70 --evidence outputs/reproduction/c70/c70.json
uv run --frozen --extra analysis python scripts/check_ss_aur_flag.py \
  --output outputs/reproduction/c71
make -C manuscript check
make -C manuscript
```

Use fresh scratch destinations; never overwrite evidence. Raw-data checks need the retained local
payloads: `check_g3a_attrition.py` and `check_ss_aur_flag.py` read the candidates' pre-1990 pages in
`data/raw/g3a_20261110_d827313/` and the pre-1990 SS Cyg extract in `outputs/c70_safe_input/`.
Never point any script at SS Cyg records from 2018 onward or candidate records from 1990 onward,
and never edit a raw-input path to a newer window; opening those needs Barry's explicit decision. The public aggregate figure/build check needs none of those observations. Figure
regeneration (`make -C manuscript figures`) reads the retained raw SS Cyg inputs for Figs. 1 and 2
through hash-checked paths and is unnecessary for ordinary text revision.

Before committing, assert that the original 26 forecasting files and parameter bytes remain
unchanged, the saved-score audit still reconstructs C01, no protected material was accessed, and
claims, rendering and relevant tests pass. References are source-checked evidence; refresh their
metadata only deliberately. The makedoc revision is pinned by `manuscript/makedoc.lock.json`.

## 7. Extend without erasing the failure

A new archive, measurement model or qualifying design would be a separate research decision.
Preserve the failed G3a rules and outcome even if later methods succeed. A specialist review of
physical hypotheses remains useful; do not contact anyone without authorization. Do not infer
that other dwarf novae lack a duration effect, or that the SS Cyg result is unique.

Change `estimands.md` before changing interpretation. Update the single ledger, verify the evidence,
stamp changed claims with `tools/claims.py`, then rebuild every product. Do not hand-edit generated
figures, reference metadata or PDFs. Barry reviews the drafts before release.
