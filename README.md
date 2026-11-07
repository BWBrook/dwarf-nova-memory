# Dwarf-nova recurrence: memory, changing activity and forecast reliability

> **Status:** developed in the open as a working record. This is work in progress: contents may change, and nothing here is peer-reviewed unless stated. No real-star result exists yet.

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

### Run immediately, without downloads or package installation

Python 3.11 or newer is sufficient for the demo, validators and tests. Run these
commands from this directory:

```bash
python -m unittest discover -s tests -v
python scripts/validate_seed.py
python scripts/validate_photometry.py data/fixtures/synthetic_photometry.csv
python scripts/run_demo.py --output outputs/my_first_demo
```

Use `python3` if that is the executable on your machine. A rerun must use a new,
empty output directory. The demo deliberately refuses to overwrite a prior run.
Optional plotting requires Matplotlib:

```bash
python scripts/plot_demo.py outputs/my_first_demo
```

An installable package is also provided (`python -m pip install -e .`); that step
may obtain the build backend from the network and is unnecessary for the commands
above. With the package installed, `dnmem demo --output outputs/run_002` is equivalent.

## What is ready, and what remains research work

| Component | Seed status |
|---|---|
| Central question, hypotheses, first-paper boundaries | Written; provisional choices explicitly marked |
| Initial literature review and bibliography | Source-checked initial review; access depth recorded; not a systematic review |
| Data access and provenance plan | Official documentation inspected; no target light curves acquired |
| Candidate targets | Provisional, with classification evidence and caveats; no final eligibility asserted |
| Statistical design and simulation programme | Specified, including censoring, missing events and state alternatives |
| Runnable code | Synthetic histories, sampled toy photometry, M0/M1 oracle forecasts, probability helpers, CSV validation |
| M2/M3 latent models, real event inference and archive adapters | Not implemented; explicit next tasks |
| Observational findings | None; no real-star results or empirical power claims |
| Git | Public at [BWBrook/dwarf-nova-memory](https://github.com/BWBrook/dwarf-nova-memory); the GPT-6 Pro seed commit and `seed-v0.1.0` tag are preserved unchanged |

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

There are no secrets, downloaded papers or real observations in this repository.
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
