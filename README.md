# Dwarf-nova recurrence: memory, changing activity and forecast reliability

> **Status:** developed in the open as a working record. This is work in progress: contents may change, and nothing here is peer-reviewed unless stated. External review has reopened research on the observation model and endpoint information. The first frozen comparison is preserved; manuscript revision waits for this research round.

**A research repository led by Barry W. Brook. Seeded 5 November 2026; public from 7 November 2026.**

The proposed first paper asks: **Does information from a completed outburst
improve predictions of the next outburst beyond star-specific recurrence and
changing activity, once the observation process is accounted for?**

The working repository name is `dwarf-nova-memory`. It is a convenient label, not
a claim that physical memory has been discovered. Historical studies already
examined serial dependence and outburst–interval relationships. The candidate
contribution is a transparent, temporally held-out evaluation of their predictive
value, with realistic competing explanations and observation uncertainty.

## Start here

1. Read [the research brief](docs/01-research-brief.md) for the question, scope and hypotheses.
2. Read [the literature review](docs/02-literature-review.md) and its evidence register before claiming novelty.
3. Read [the statistical design](docs/05-statistical-design.md), especially endpoint uncertainty and forecast issue times.
4. Run the commands below; inspect the explicitly synthetic outputs.
5. Give both agents [AGENTS.md](AGENTS.md), then assign the first bounded tasks in
   [the roadmap](docs/08-implementation-roadmap.md). The first useful result is an
   audited feasibility pack, not a full population fit.

### Run the seed without package installation

Python 3.11 or newer is sufficient for the demo, validators and tests. Run these
commands from this directory:

```bash
python scripts/validate_seed.py
python scripts/check_demo_reproduction.py
python scripts/validate_photometry.py data/fixtures/synthetic_photometry.csv
python scripts/run_demo.py --output outputs/my_first_demo
```

Use `python3` if that is the executable on your machine. A rerun must use a new,
empty output directory. The demo deliberately refuses to overwrite a prior run.
Optional plotting requires Matplotlib:

```bash
python scripts/plot_demo.py outputs/my_first_demo
```

Full tests and the censoring-aware forecast prototype use the locked analysis
environment (NumPy/SciPy):

```bash
uv sync --extra analysis
uv run --frozen --extra analysis python -m unittest discover -s tests -v
```

An installable package is also provided (`python -m pip install -e .`); that step
may obtain the build backend from the network and is unnecessary for the commands
above. With the package installed, `dnmem demo --output outputs/run_002` is equivalent.

`validate_seed.py` checks the committed CSV bytes against their recorded hashes.
`check_demo_reproduction.py` regenerates all sixteen tables in a temporary
directory and compares floating columns and scenario summaries with explicit
numerical tolerances. IDs, flags, table structure and counts must match exactly.
Small floating-point differences across runtimes need not give identical hashes.

## What is ready, and what remains research work

| Component | Seed status |
|---|---|
| Central question, hypotheses, first-paper boundaries | Written; provisional choices explicitly marked |
| Initial literature review and bibliography | Source-checked initial review; access depth recorded; not a systematic review |
| Data access and provenance | 12 hashed native SS Cyg acquisitions through 1959-12-31 noon under D013; 72,635 unique native IDs after overlap removal; raw data excluded from Git |
| Candidate targets | Provisional, with classification evidence and caveats; no final eligibility asserted |
| Statistical design and simulation programme | Specified, including censoring, missing events and state alternatives |
| Runnable code | Synthetic histories, sampled toy photometry, M0/M1 oracle forecasts, probability helpers, CSV validation; X1–X4 extractors, with X4 conditionally qualified for magnitude-10 retrospective extraction; no operational extractor |
| Archive adapter | Receipt-verified bounded native VStar/AID acquisitions through 2017; reported time convention retained; X4 supplies the separate event extraction |
| M2/M3 and validated observational forecasting | [A10b](docs/audits/2026-11-08-a10b-model-controls.md) implements conditional M0–M3 and completes 56 synthetic control trials. Injected-effect prefix gain averages 0.00324 nats; individual-history intervals remain wide. AR-gap baseline, partial endpoint sensitivity and strict oracle matching remain limitations. [A10c](docs/audits/2026-11-08-a10c-controls-review.md) finds that a third of that gain came from forecasts with no previous-gap term, and that null coefficients are negative. It specifies a directional, matched M3 (null −0.0002, injected effect +0.0023 nats on the A10b scores), a placebo for shared slow state, and the path to the first real 1910–1959 fit. These historical controls precede the completed A10i retrospective result; no operational forecast claim |
| Synthetic recovery | Earlier X1/X2/X3 failures retained. A04i's 4,800-history X4 screen passes at magnitude 10 on qualified v2 phase-aligned cadence; C1/7 d selected. The unseen waveform fails qualification and magnitude-9.5 diagnostics fail in later eras. This is conditional retrospective extraction, separate from the later A10i predictive result |
| Observational findings | Independent 1957 boundary differences adjudicated; first 1910–1959 development model fit complete on 330 issuances. The A10i held-out result is complete under its fixed extraction and timing baseline |
| Git | Public at [BWBrook/dwarf-nova-memory](https://github.com/BWBrook/dwarf-nova-memory); the GPT-6 Pro seed commit and `seed-v0.1.0` tag are preserved unchanged |

[A10d](docs/protocols/a10d-directional-oc-v1.md) implements the directional
M3/P3 offsets against a fixed q-plus-local-history M2, independent v3 prefix
features, and the 360-trial operating-characteristic runner. The
[completed A10d audit](docs/audits/2026-11-08-a10d-directional-oc.md) passes
the finite observed-rate/joint-MC screen: gated null confirmations are at
most 2/40 or 0/20, and injected-effect power is 11/40 (27.5%). This does not
certify a true five-percent error rate. Barry accepted that finite screen
(D022), and the [first real development fit](docs/audits/2026-11-08-a10e-first-development-fit.md)
is complete: 330 forecasts, a positive frozen duration offset, and similar
endpoint/delay checks. This was in-sample evidence before the single 1960–2017 evaluation described below; that
evaluation is now complete and 2018 onward remains closed. The positive coefficient and
lagged-duration comparisons do not identify physical memory or universally
exclude endpoint artefacts.

[The frozen 1960–2017 evaluation](docs/audits/2026-11-09-a10i-sealed-evaluation.md)
meets its predeclared forecast-gain criterion: **+0.01653 nats per issuance,
90% interval [0.00495,0.02812], 441 forecasts**. It compares extracted current
log duration with the specified frozen previous-gap/recent-history baseline.
The 1993–2017 segment and the type/within-type variant are inconclusive.
This supports incremental predictive information in the specified working score
for SS Cyg under these rules. It is not yet an established proper score for
latent visual onset; physical memory and wider transport remain unresolved.

The [R1 audit](docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md)
preserves the original run and adds post-result diagnostics. The censoring
repair changes none of its 441 outcomes. Saved-point density gives +0.01540
nats [0.00344, 0.02736], but the proposed decisive-report interval/kernel
comparisons lack finite clips for 434 forecasts and cannot validate the full
sample. A fixed-simulator endpoint-error experiment separately checks measured
and true-onset targets. These are exploratory checks, not another confirmation.
[Claude's R1 review](docs/audits/2026-11-09-claude-r1-review.md) reproduces
these checks and traces the missing clips to a bug in X4's lower onset clip. A
corrected decisive bracket exists for almost every outburst. The
[amended R2 preparation](docs/protocols/r2-design-v1.md) separates containment,
association and CAR assumptions; a report margin does not prove them. X5 gives
818 report windows among 845 confirmed episodes, with 805 eligible. The new
observed-clock policy retains 307 of the original 441 evaluation issues, so
cross-clock comparisons require matched populations. Windowed timing baselines
and their exact mark nesting pass finite synthetic/numerical checks. No real
R2b fit or gain has been computed.

The [R2a/c report](docs/audits/2026-11-09-r2a-preparation-and-r2c-review.md)
records the completed gain-free preparation and catalogue/precision study.
An observed clock does not eliminate cadence/selection information. The
score-level power study does not establish the proposed G2 target: at nominal
gain 0.010, 1,100 forecasts give fitted-rule power about 0.71, and serial-block
dependence degrades interval coverage. Eight stars are nominated for future
development screening, not qualified. Manuscript products remain paused. No other-star archive
opening is authorized, and SS Cyg 2018 onward remains closed.

[Claude's R2a/c review](docs/audits/2026-11-09-claude-r2a-review.md) supports
those results. It finds that the observed-clock population loss came from
aborting on single near-threshold reports. With aborts only on decisive-bright
reports, all 441 evaluation issues are kept. The
[R2b rules](docs/protocols/r2b-execution-v0.md) also fix:
- the latent crossing convention;
- a ceiling on cadence artefacts (about 0.007 nats in 1960–2017);
- the headline contrasts;
- dependence-aware inference, and the sealed test's primary specification.

All of this is fixed before any R2b score.

[Claude's review](docs/audits/2026-11-09-a10j-result-review.md) reproduces the
result by a separate route. [The independent A10k review](docs/audits/2026-11-09-a10k-claims-and-figures.md)
also reproduces the exploratory and secondary numbers, with narrower interpretations:

- a global level/recentering contrast describes part of the gain, without
  removing drift within the evaluation period;
- a long/short indicator has the larger exploratory in-sample likelihood;
  this does not establish that all information is in type or that within-type
  effects are absent.

The uncentred type component and fixed baseline interact; the within-type
component can still shorten forecasts. The evaluation-fitted level adjustment
does not replace the inconclusive predeclared type rule. The paper's
[interpretation specification](manuscript/estimands.md) and
[claims ledger](manuscript/claims.csv) govern the figure captions and drafting.

Four scientific figures and a brief figure are reproducible with
`make -C manuscript figures`; `make -C manuscript` checks the public assets
and builds the PDF/DOCX previews without raw observations or archive access.
The [article](manuscript/build/manuscript.pdf),
[supplement](manuscript/build/supplement.pdf) and
[brief](manuscript/build/brief.pdf) are first full drafts
([A10l](docs/audits/2026-11-09-a10l-sources-and-drafts.md)). The [A10m semantic/source review](docs/audits/2026-11-09-a10m-draft-review.md)
corrects the draft interpretations and reproduction instructions. An independent [GPT-6 Pro review](docs/reviews/2026-11-09-gpt6pro/) followed; the [A10n triage](docs/audits/2026-11-09-a10n-external-review-triage.md) reopens the research before the products are rewritten. The bibliography
has [generated DOI metadata and a separate unresolved identifier](references/README.md).

The [protocol](https://doi.org/10.5281/zenodo.24053338) was published before
access. The first attempt failed before scoring on missing-uncertainty metadata;
a narrow independently reviewed parser repair preceded the completed run.
Untouched status is consumed, and the result is explicitly a **post-access
format-repair continuation**. Independent checks reproduce all 2,641 scores,
the interval, source identities and acquisition bounds. A10k passes all 348
local tests and the repository, claims and document checks. Native rows and full event/score outputs remain
outside Git; aggregate results are in
[`data/provenance/a10i_evaluation_1960_2017/`](data/provenance/a10i_evaluation_1960_2017/).
No 2018+ data were requested or analyzed; that replication block stays closed.

The included `outputs/seed_demo/` is an illustrative run. Its forecast evaluation
uses *true complete simulated event histories*. The observation schedule is a
separate visibility demonstration, not the input to the fitted forecasts. This
separation is intentional and must stay visible in every discussion of the seed.

## Navigation

| File | Purpose |
|---|---|
| [Research brief](docs/01-research-brief.md) | Main question, hypotheses, proposed contribution |
| [Literature review](docs/02-literature-review.md) | Prior findings, nearest competitors and novelty limits |
| [Data and provenance](docs/03-data-and-provenance.md) | Archives, access, units, flags, reuse and observation histories |
| [Pilot targets](docs/04-pilot-targets.md) | Selection rationale and provisional candidates |
| [Statistical design](docs/05-statistical-design.md) | Estimands, model ladder, likelihoods and evaluation |
| [Simulation and validation](docs/06-simulation-and-validation.md) | Recovery, falsification and operating characteristics |
| [Risks and gates](docs/07-risks-and-decision-gates.md) | Proceed, narrow or stop decisions |
| [Implementation roadmap](docs/08-implementation-roadmap.md) | Ordered, independently reviewable tasks |
| [Data dictionary](docs/09-data-dictionary.md) | Table contracts and censoring semantics |
| [Domain primer](docs/10-domain-primer.md) | Enough astrophysics to connect statistics to a physical question |
| [Workflow](docs/11-reproducibility-and-workflow.md) | Git, agents, provenance, freeze and review rules |
| [Seed validation](docs/12-seed-validation.md) | What was actually run and checked |
| [BibTeX](references/literature.bib) | Initial reference library |
| [Evidence register](references/evidence.csv) | Access depth, source links and verification |
| [Agent prompts](prompts/README.md) | Concrete kickoff and independent review instructions |
| [Manuscript outline](manuscript/outline.md) | Result-neutral paper structure and planned figures |
| [Seed ideation](docs/gpt-6-pro_ideation.md) | The Barry–GPT-6 Pro conversation that chose the topic and commissioned the seed |
| [Correspondence](docs/correspondence/INDEX.md) | Reviewed snapshots of the Claude–Codex–Barry board discussions |
| [Opening code audit](docs/audits/2026-11-07-code-audit.md) | Independent numerical checks, reproduction and remaining implementation limits |
| [A01 review and D013](docs/audits/2026-11-07-a01-review-d013.md) | Corrected power interpretation and historical access sequence |
| [First authentic acquisition](docs/audits/2026-11-07-a03-ss-cyg-acquisition.md) | Native export, provenance, observation limits and next annotation step |
| [Independent A04 comparison and open-era coverage](docs/audits/2026-11-07-a04-independent-comparison-open-era.md) | Sealed blind labels, unresolved boundaries, conditional endpoint sensitivities and 1896–1959 acquisition |
| [A04c synthetic recovery screen](docs/audits/2026-11-07-a04c-injection-recovery.md) | Frozen criteria, independent synthetic truth, failed extractor qualification and recovery diagnostics |
| [A04d benchmark review and X3 repair](docs/audits/2026-11-07-a04d-observation-review-x3-repair.md) | Predictive checks of the A04c benchmark, why X1/X2 miss, fitted-interval extractor X3, proposed fresh validation |
| [A04h joint morphology targets](docs/audits/2026-11-08-a04h-joint-morphology-targets.md) | Why v3 failed (fixed amplitude), calibrated joint waveform and cadence targets, every cadence arm short of decline sampling |
| [A04f X3 failure review and X4](docs/audits/2026-11-08-a04f-x3-failure-review-x4.md) | Why X3 failed A04e, a state-cadence observer-diversity defect, the X4 repair, proposed A04g validation |
| [A04e independent X3 validation](docs/audits/2026-11-07-a04e-x3-independent-validation.md) | Qualified independent benchmark, 7,600-history frozen validation, failed global qualification, causal confirmation and retained challenges |
| [A04g X4 benchmark qualification](docs/audits/2026-11-08-a04g-x4-independent-validation.md) | Independent waveform/cadence, retained calibration failures, repaired diversity, failed fresh benchmark gate; X4 recovery not run |
| [A04i joint qualification and X4 recovery](docs/audits/2026-11-08-a04i-joint-validation.md) | Qualified v2 phase cadence; unseen waveform rejected; 4,800-history magnitude-10 X4 pass, C1 selected, threshold failures and evidence limits retained |
| [A10a prefix-causal predictors and precision](docs/audits/2026-11-08-a10a-prefix-predictors-review.md) | Why magnitude 10 is structural, what the known-waveform limit threatens, the [proposed A10 predictor protocol](docs/protocols/a10-prefix-causal-predictors-v1.md), causality cost on real 1910–1959 rows, and single-star forecast-gain power |
| [A10c control review and development-fit specification](docs/audits/2026-11-08-a10c-controls-review.md) | Where the A10b gain comes from, the sign of end-error coupling, the directional matched M3, the slow-state placebo and the [A10c protocol](docs/protocols/a10c-development-fit-v1.md) |
| [A10f development review and evaluation protocol](docs/audits/2026-11-08-a10f-development-review.md) | The real fit placed among 360 synthetic development fits, issue ages and the sign argument, the lagged-mark evidence on shared state, conditional power, and the [proposed evaluation protocol](docs/protocols/a10f-evaluation-v1.md) |
| [A10g sealed evaluation freeze](docs/audits/2026-11-08-a10g-evaluation-freeze.md) | Implemented access guards, independent score checks, preserved numerical failures, completed synthetic rehearsal and prepared protocol-only deposit |
| [A10i real sealed evaluation](docs/audits/2026-11-09-a10i-sealed-evaluation.md) | Confirmed frozen forecast-gain comparison, post-access format repair, independent checks and visible era/type limits |
| [A10j result review](docs/audits/2026-11-09-a10j-result-review.md) | Independent recomputation, exploratory level/type decomposition, and the paper's framing, estimands and claims ledger |
| [A10k claims and figures](docs/audits/2026-11-09-a10k-claims-and-figures.md) | Independent secondary/exploratory verification, narrowed interpretations, reproducible figures and document previews |
| [A10l sources and drafts](docs/audits/2026-11-09-a10l-sources-and-drafts.md) | CM92 and Cannizzo (1993) source checks, novelty refresh, first drafts of all three products and the agent guide |
| [A10m draft review](docs/audits/2026-11-09-a10m-draft-review.md) | Codex's semantic, novelty and rendered-PDF review of the drafts |
| [A10n external review triage](docs/audits/2026-11-09-a10n-external-review-triage.md) | Disposition of the [GPT-6 Pro review](docs/reviews/2026-11-09-gpt6pro/), observation contract, bounded diagnostics and the expanded multi-star design sketch |
| [R1 observation and endpoint diagnostics](docs/audits/2026-11-09-r1-observation-endpoint-diagnostics.md) | Codex's censor audit, alternative observation scores, endpoint-error dose experiment and simulation table |
| [Claude R1 review](docs/audits/2026-11-09-claude-r1-review.md) | Independent checks of C42–C46, the X4 lower-clip bug and corrected decisive brackets |
| [R2 preparation v1](docs/protocols/r2-design-v1.md) | Amended target assumptions, mixed-score bounds, causal observed clocks, timing models and limited precision planning; v0 preserved |
| [R2a/c report](docs/audits/2026-11-09-r2a-preparation-and-r2c-review.md) | Codex's X5 diagnostics, observed-clock features, B0–B2 controls, catalogue screen and precision study |
| [Claude R2a/c review](docs/audits/2026-11-09-claude-r2a-review.md) | Checks of C47–C52, the abort-rule artefact, crossing convention, cadence ceiling and cluster coverage |
| [R2b rules v0](docs/protocols/r2b-execution-v0.md) | Clock, population, crossing, score, headline-contrast, uncertainty and sealed-primary rules for R2b |
| [A04 review and annotation](docs/audits/2026-11-07-a04-review-and-annotation.md) | D013 review, native time and flag check, first event brackets for SS Cyg 1956–1958 |
| [A04b adjudication and extraction candidates](docs/audits/2026-11-07-a04b-adjudication-extraction-candidates.md) | Three boundary disputes settled, tied-epoch rule, extractors X1/X2, open-era coverage by decade, injection/recovery design |
| [Outcome access](docs/outcome-access-ledger.md) | Provisional 2018 access boundary and prior outcome knowledge |

## How this work is done

Barry W. Brook leads the science. OpenAI GPT-6 Pro (ChatGPT) proposed the topic
among twenty candidates and built the seed: framework documents, literature
review, bibliography, evidence register and synthetic prototype
([ideation record](docs/gpt-6-pro_ideation.md)). The seed commit carries a
neutral assistant identity and is preserved unchanged. From 7 November 2026 the
work continues with Claude (Anthropic, Claude Opus 5.5 in Claude Code) and Codex
(OpenAI), who propose, implement and cross-review through Barry's correspondence
board. Reviewed snapshots of that discussion are published in
[`docs/correspondence/`](docs/correspondence/INDEX.md), and each contribution
records the system and model that made it.

No secrets, downloaded papers or raw real observations are committed.
The first authentic SS Cyg export is stored locally under gitignored `data/raw/`;
its hash, request and unresolved conventions are recorded in the manifest.
Raw archive exports stay out of Git until their redistribution terms are checked
(see [data and provenance](docs/03-data-and-provenance.md)).

## Citation

See [`CITATION.cff`](CITATION.cff). Paper-grade milestones will be tagged as
releases with a Zenodo DOI.

## Licence

Code is released under the [MIT Licence](LICENSE). Text, figures and data created
for this project are released under [CC BY-SA 4.0](LICENSE-CONTENT). Third-party
observations, papers and catalogues keep their own terms.

## Recommended first decision

Begin with a handful of well-observed ordinary dwarf novae and one documented
historical result to reproduce. Expand only after obtaining authentic light
curves, checking time/filter conventions, and demonstrating usable independently
evaluated cycles. An honest finding of weak predictability can support a paper;
an underpowered failure to detect an effect cannot establish that memory is absent.
