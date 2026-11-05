# Pilot targets and sample selection

**Prepared 5 November 2026.** This is a provisional, literature-supported shortlist for a feasibility audit, not an acquired or statistically eligible sample. No light curves, current coordinates, observing counts, or event counts have been verified by this project. The machine-readable counterpart is [`configs/candidate_targets.csv`](../configs/candidate_targets.csv).

The initial scientific population is ordinary hydrogen-rich, nonmagnetic dwarf novae of the U Gem/SS Cyg family, subject to current classification and identity checks. Historical UGSS or U Gem-type labels are sufficient to nominate a target; they are not a substitute for those checks. The official [VSX type definitions](https://vsx.aavso.org/index.php?view=about.vartypes) distinguish UGSS, standstill-bearing UGZ, superoutburst-bearing UGSU, and WZ Sge systems. Avoid treating the latter classes as ordinary replicates in the first analysis.

## 1. An approximately six-target feasibility pilot

The [AAVSO Legacy CV Program](https://archive.aavso.org/index.php/aavso-legacy-cv-program) supplies historical evidence that several familiar dwarf novae attracted long-term monitoring. Its historical observing-count requirements are a reason to investigate these stars, not proof that present exports contain usable event sequences or a license to select stars on future completed cycles.

| Candidate | Provisional class evidence | Reason to investigate | Specific check before inclusion |
|---|---|---|---|
| **SS Cyg** | UGSS in the AAVSO legacy list; a prototype in VSX definitions | A well-studied reference system for establishing extraction and comparing historical analyses | Document state/regime changes and heterogeneous observer/band coverage; do not assume one stationary process over the entire archive |
| **U Gem** | UGSS prototype in VSX definitions | A second reference system for testing whether a procedure generalizes beyond SS Cyg | Confirm current identity and the practical number and coverage of usable development cycles; treat different event morphologies explicitly |
| **SS Aur** | UGSS in AAVSO legacy list; U Gem type in the cited ultraviolet study | Another ordinary-system candidate for between-target variation | Verify useful quiescent coverage and the uncertainty of rise/end boundaries |
| **RU Peg** | U Gem type in the cited ultraviolet study and an object-specific activity study | Published outburst-type variability makes it useful for checking sensitivity to morphology | Determine whether a common extraction rule handles different outburst types without post hoc relabeling |
| **BV Cen** | UGSS in AAVSO legacy list; U Gem type in Sion et al. (2007) | Southern candidate that broadens observing geography and potential survey overlap | Verify band consistency, identity, and usable cadence rather than inferring quality from its historical prominence |
| **UU Aql** | UGSS in AAVSO legacy list; U Gem type in Sion et al. (2007) | Additional candidate for a modest multi-target pilot | Verify actual coverage, depth, blending, and boundary identifiability |

These are **six candidates to audit**, not a promise of six eligible stars. Start with one or two controlled acquisitions to establish the workflow, then audit the remainder in this predeclared order. The order is a practical work queue rather than a scientific ranking. If a target fails a gate, preserve the failure and its reason.

Relevant primary literature includes *Far Ultraviolet Observations of the Dwarf Novae SS Aur and RU Peg in Quiescence* ([2004 preprint](https://arxiv.org/abs/astro-ph/0406422)); *The activity of the dwarf nova RU Pegasi with rapidly changing outburst types* ([2021 preprint](https://arxiv.org/abs/2112.03620)); and Sion et al. (2007), *FUSE Observations of the Dwarf Novae UU Aql, BV Cen, and CH UMa in Quiescence* ([preprint](https://arxiv.org/abs/0704.1133), [DOI](https://doi.org/10.1086/518829)). These papers support object/class context; none establishes the quality of a present-day export for this project.

## 2. Ordinary-system reserves

| Candidate | Provisional class evidence | Role |
|---|---|---|
| **CH UMa** | U Gem type in Sion et al. (2007) | A literature-supported reserve if an initial candidate is unusable or justified expansion is possible |
| **AR And** | UGSS in the AAVSO legacy list | Reserve for a current identity, cadence, and completeness audit |
| **DX And** | UGSS in the AAVSO legacy list | Reserve offering another ordinary-system candidate, conditional on current classification and coverage checks |

Reserve status does not indicate inferior scientific value. It limits the initial implementation workload. Do not replace a pilot target merely because its estimated effect is weak, inconvenient, or contrary to the hypothesis. Replacement should be justified by frozen population and data-quality rules and recorded before evaluation outcomes are inspected.

## 3. Separate challenge sets

These classes can be scientifically valuable but change the event taxonomy or waiting-time process. They should initially test where the first model fails, and should enter the principal analysis only through a predeclared extension.

| Candidate | Provisional subtype | Why keep it separate? |
|---|---|---|
| **Z Cam** | UGZ; class prototype | Standstills interrupt a simple alternation between ordinary outburst and quiescence; define a state process before assigning waiting times |
| **RX And** | UGZ in AAVSO legacy list and its AAVSO object description | Another standstill-bearing candidate, useful for testing state classification and observation gaps |
| **VW Hyi** | UGSU in AAVSO legacy list | Normal outbursts and superoutbursts require separate labels and potentially dependence on position in a supercycle |
| **SU UMa** | UGSU; class prototype | A taxonomy and model-extension case for normal/superoutburst sequences |
| **WZ Sge** | UGWZ; class prototype | Rare superoutbursts and long quiet intervals make a frequent-cycle pilot unsuitable; sparse events cannot support the same individual-target analysis |

Use the [VSX definitions](https://vsx.aavso.org/index.php?view=about.vartypes), [AAVSO legacy programme](https://archive.aavso.org/index.php/aavso-legacy-cv-program), and [AAVSO RX And description](https://archive.aavso.org/index.php/vsots_rxand) as starting evidence, then retrieve current object records. A catalogue class should not be assigned from its name alone except where the source explicitly identifies the prototype.

The registry deliberately does not use every historically familiar dwarf nova. In particular, do not assume that an old generic “dwarf nova” or U Gem label excludes standstills. The legacy list itself labels WW Cet UGZ. Any uncertain or revised object belongs in a pending/challenge category until the adopted class is supported. This seed does not settle the classification of CN Ori.

## 4. Selection protocol and an auditable ledger

[The decision gates](07-risks-and-decision-gates.md) are the authority for numeric thresholds, adequacy judgments, and when to freeze them. This page adds a selection workflow, not alternative cutoffs.

1. **Freeze the candidate queue and population definition.** Save the current registry before real scientific results are examined. Record additions with date, rationale, evidence, and whether any outcome was already seen.
2. **Verify identity and subtype.** Retrieve the current VSX/object information and survey crossmatches. Confirm that the adopted physical population is defensible, and quarantine unresolved identities or classes.
3. **Acquire a bounded development sample.** Choose its time range in advance, retain all relevant measurements and quality metadata, and establish a complete acquisition manifest. Review coverage and event extraction using development data.
4. **Apply development-only feasibility criteria.** Assess useful baseline, sampling and depth, boundary identifiability, passband consistency, event taxonomy, and ability to represent missing events. Follow the decision document's planning guidance; do not manufacture a universal event-count rule here.
5. **Freeze eligible targets, windows, and evaluation protocol.** State exclusions and any required state segmentation before looking at final evaluation outcomes. Preserve the distinction between deciding eligibility and scoring a forecast.
6. **Retain the evaluation denominator.** A forecast made under an eligible rule remains a forecast even if the next outburst is not observed before coverage ends. Include appropriate censoring; do not keep only stars or intervals with a conveniently completed future cycle.

The first real-data ledger should record candidate ID, verified identities and classifications, source/date, acquired date range, development/evaluation boundaries, band policy, coverage checks, event-definition review, decision, and a concrete exclusion reason if applicable. The CSV supplied here is only a shortlist and deliberately does not contain invented pass/fail fields or future observation counts.

Define eligible windows using the observability rules in the methods, not an attractive pattern in recurrence intervals. A seasonal gap can conceal events; a dense follow-up campaign after an outburst is not equivalent to equally dense quiescent monitoring. A long archive with mostly bright-state observations can be less useful than a shorter series with well-characterized opportunities and limits. Document all such decisions in terms of the process that generated the data.

## 5. Conditional expansion and stopping

An eventual sample of roughly 12–20 ordinary systems is a **conditional planning scale**, not an acquisition claim or minimum required for success. The registry contains nine provisional ordinary candidates and five distinct challenge targets; these do not add up to fourteen interchangeable primary systems. Expanding the primary sample requires a further documented catalogue/literature search and the same identity, quality, development-only, and evaluation rules.

Expand only when the initial pilot demonstrates workable observation modeling, event extraction, and prospective information flow, and when simulation indicates that additional systems or additional time meaningfully improve the intended inference. If only a few systems support a credible analysis, a carefully delimited small-sample study is preferable to silently changing the class definition or accepting poorly observed sequences. If ordinary systems prove too heterogeneous, record a principled narrower population and restart the relevant protocol freeze transparently.

A useful pilot result may be a demonstrated limit: for example, insufficient opportunity information to distinguish memory from missed events, or morphology effects that are not stable across measurement streams. Those outcomes should inform the repository's next tasks rather than be filtered out through sample selection.

## 6. Registry conventions and verification status

`target_id` is a repository-local stable slug, not an astronomical catalogue identifier. `provisional_class` preserves the nominated category; `role` distinguishes pilot, reserve, and challenge targets; `classification_source` points to the evidence used; and `verification_status` explicitly says what is still pending. A source-supported label is not a current per-object VSX verification. No precise coordinates or external object identifiers are included because those have not been checked for this seed.

All source links above were reviewed during the 5 November 2026 seed audit. Revisit them and the current object records at first acquisition. Preserve classification changes rather than overwriting the historical evidence silently.
