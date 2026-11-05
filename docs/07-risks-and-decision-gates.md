# Risks, decision gates and defensible stopping points

**Status:** proposed project decisions, 5 November 2026. Quantitative pilot targets below are provisional planning values. They should be revised transparently during development and frozen before final outcome inspection.

## 1. The principal scientific risks

| Risk | Why it matters | Concrete response |
|---|---|---|
| Rediscovering an old correlation | Prior dwarf-nova work already investigates recurrence, outburst properties and “memory” | Reproduce one historical result; specify the additional predictive and observational test; do not claim the first evidence of memory |
| Mechanical variable coupling | Onset interval contains the preceding duration | Make subsequent quiescent gap the primary response and retain the arithmetic negative control |
| Shared endpoint error | An overestimated end lengthens duration and shortens the following gap | Jointly propagate the shared boundary; simulate correlated errors |
| State mistaken for direct memory | Both duration and recurrence can respond to a common unobserved process | Compare changing-activity baselines; interpret gain as predictive information; reserve direct attribution for an identifiable joint model |
| Missed events | A long observed interval may contain several real cycles | Use validated monitored episodes or a latent missing-event model; never declare every adjacent detected pair consecutive |
| Adaptive effort | Interesting behaviour attracts more observations | Separate observing regimes and simulate the observation policy; disclose what conditioning on actual timestamps establishes |
| Outcome-dependent sample selection | Requiring a complete later cycle drops long waits | Retain issued forecasts and censor them at coverage loss; define sample rules using information available at origin |
| Future information leakage | Smoothed states, final event summaries or future pooled data can improve hindcasts artificially | Freeze common-calendar splits and maintain an as-of input/forecast ledger |
| Subtype or event mixture | A broad pooled relationship can be caused by different physical populations | Begin with a narrow frequent-outburst sample; retain challenge systems separately |
| Fluence misinterpreted as energy | Passband, calibration, distance and coverage matter | Use a homogeneous optical proxy and explicit limits; start with duration |
| Many outcomes, one attractive result | Exploring dozens of features and lags can manufacture a story | One primary mark and model comparison; label ancillary searches; lock final evaluation |
| Tiny effective sample | Thousands of measurements need not imply many independent systems or cycles | Report systems and eligible forecast episodes; show per-system and leave-one-system-out results |

## 2. Stage gates

### Gate A — The contribution is distinct enough to pursue

**Work:** Read the closest papers in full where possible, trace their references, and reproduce one well-defined published relationship with documented differences in data and definitions. Check especially whether newer work already implements the proposed changing-state/forecast comparison.

**Pass:** A one-page novelty statement can specify what is already known and what the proposed test adds. The contribution is conditional on what was found in the reviewed literature, not an assertion of exhaustive priority.

**If not:** Narrow to a replication with a meaningful extension, ask a domain specialist for perspective once there is a concrete pilot, or choose a different hypothesis. Do not rename an old correlation and present it as new.

### Gate B — The archive can support the intended observations

**Work:** Retrieve and document a small sample, starting with about six provisional targets. Establish identity, band/time semantics, quality fields, limits, provenance, duplication and reuse conditions. Annotate a mix of clear events, poorly observed events and long gaps. Verify that negative/quiescent observations are available where the study requires them.

**Pass:** At least several targets have usable repeated episodes and enough pre-evaluation history to estimate a renewal baseline. A practical aspiration is roughly 30 or more useful development cycles for a target considered for individual modelling; this is a planning guide, not a data-quality definition or a final power calculation.

**If not:** Reduce the claim to the well-supported systems, alter the window or source, or make measurement/recovery the pilot result. Do not promise an expansion to 20 stars before inspecting actual records. Do not select targets based on attractive test-set effects.

### Gate C — Event measurement is sufficiently trustworthy

**Work:** Compare the extraction algorithm with documented manual annotations and injection–recovery across cadence, amplitude and duration. Examine incomplete events, shared boundary errors and seasonal losses. Resolve disagreements in event identity before testing mark effects.

**Pass:** The declared coverage rule yields tolerable missed/split/merged-event rates across the primary event range; endpoint uncertainty has reasonable calibration in simulation; residual uncertainty can be propagated or bounded. Investigate a missed-event target of about 5% or less for accepted episodes, but report its conditions and uncertainty.

**If not:** Use a stricter monitored-episode definition with a narrower estimand, improve the observation model, or stop the memory analysis. A sophisticated time-series model cannot repair an unvalidated event catalogue automatically.

### Gate D — The relevant effects are recoverable

**Work:** Run the simulation plan on observational regimes resembling the candidate data. Include shared-state, measurement-coupling and informative-effort cases, not just data generated from the fitted model. Determine whether the intended conclusion is incremental prediction or structural mechanism; evaluate the corresponding null.

**Pass:** The design has useful precision/power for an agreed effect, calibrated predictive uncertainty, and acceptable behaviour under plausible departures. For example, test whether a 20% median-wait change for a doubling of duration is distinguishable; the scientific importance of that threshold still needs review.

**If not:** Simplify the question, improve coverage or enlarge the observational baseline. A result that shows which explanations remain indistinguishable may be worthwhile if its implications are clear; do not convert low power into evidence for absence.

### Gate E — The evaluation can honestly be locked

**Work:** Commit the target list, eligibility rule, feature definitions, model set, training/update schedule, forecast origins, primary score and sensitivity plan. Identify what outcome data have already been seen. Put the held-out ledger behind a procedural boundary that agents respect.

**Pass:** A second agent can reproduce each forecast using only the recorded permitted inputs, and perturbing future data leaves earlier forecasts unchanged. A real held-out period or prospective continuation exists; if it does not, the paper describes an exploratory hindcast honestly.

**If not:** Do not call the existing analysis preregistered or confirmatory. Either retain that status explicitly or choose untouched evaluation data before proceeding.

### Gate F — The result supports a useful manuscript

**Work:** Complete paired model comparisons and calibration, show every system, assess reliance on one influential star, and report exclusions, failed fits and sensitivity to the observation process. Relate any result to the closest physical interpretations with appropriate uncertainty.

**Pass:** The contribution is understandable as improved predictive information, a quantitative limit, a robust replication that changes interpretation, or a demonstrated identification failure with practical implications. A positive duration slope is not a prerequisite.

**If not:** Retain a reproducible pilot and its reasons for stopping. Do not expand to arbitrary lags, subclasses and transformations solely to produce a positive paper.

## 3. Conclusions the study could legitimately reach

| Possible outcome | Defensible interpretation | Overstatement to avoid |
|---|---|---|
| M1 improves on M0; M3 does not improve on M2 | Duration is informative relative to a stationary baseline, but timing adaptation accounts for the added value in the tested models | “The disc has no memory” |
| M3 improves on M2 robustly | Completed duration adds predictive information beyond the specified timing-history baseline | “An outburst causally determines the next recurrence” |
| Gain appears only in one system or observing regime | Information is heterogeneous or depends on measurement/selection | A universal dwarf-nova relationship |
| Apparent gain vanishes after boundary/cadence treatment | A reported relationship may be explained by the tested observational effects | Proof that every earlier physical interpretation is wrong |
| No useful gain, with adequate sensitivity to an agreed effect | The data constrain predictive improvement at the tested scale for the monitored sample | Evidence that all forms or timescales of memory are absent |
| Competing mechanisms remain indistinguishable | Available observations support similar predictions under multiple explanations | Selecting one mechanism because its fitted curve looks better |

## 4. What the independent reviewing agent should challenge

The reviewer should identify the strongest nearby paper, independently verify one key calculation, and try to construct a process that produces the claimed finding without its proposed explanation. Priority challenges are future-data leakage, state-as-mark confounding, shared endpoint error, missing events and selection on complete outcomes.

An agent agreeing with another agent's prose is not independent validation. Useful independence comes from a separately specified calculation, a hidden simulation truth, a different implementation of a key likelihood, or a genuine later forecast outcome. The scientific owner should decide how a disputed assumption changes the research claim, and record the decision.

## 5. Scope discipline

The first paper does not need to infer disc mass, solve the thermal-viscous equations, explain all dwarf-nova subclasses, or optimise a telescope network. It needs a clear estimand, defensible observations, honest predictions and a conclusion that matches the available evidence. Add complexity only when an observed failure or a stated scientific contrast requires it.

Read alongside [statistical design](05-statistical-design.md), [simulation and validation](06-simulation-and-validation.md), and the literature/data documents. The risk analysis and gates are proposed project judgments; source-backed antecedents are catalogued in the literature review.
