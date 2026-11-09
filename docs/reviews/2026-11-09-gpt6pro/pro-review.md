# Independent scientific and editorial review

**Project:** *dwarf-nova-memory* — SS Cygni completed-duration forecasting study  
**For:** Barry W. Brook, Claude and Codex  
**Review date:** 9 November 2026  
**Recommendation:** Correct the observation/score interpretation and audit the censoring edge case, then develop a more comprehensive study if impact is the priority. The current frozen comparison is a useful foundation; publication of this result alone would be scientifically incremental.

## Version, independence and boundaries

This review covers the public repository **[BWBrook/dwarf-nova-memory at commit f48f0e2c728739a97fb90fb795eddb54c98c2dc3](https://github.com/BWBrook/dwarf-nova-memory/tree/f48f0e2c728739a97fb90fb795eddb54c98c2dc3)**, committed **2026-11-08 16:00:02 UTC**, message *Snapshot the reviewed A10m draft handoff to Barry*. Its Git tree is `068b0f9d7dc3c0f628e8c5365f9f92dd53c4ccc2`. The article and brief are dated 9 November. No current manuscript attachment or separate current snapshot was available to this review; the older project seed is not the manuscript reviewed. The live branch was checked again during the review and still pointed to this commit. No later version was mixed into the assessment.

The principal documents are the 13-page article, 9-page supplement and two-page brief in `manuscript/build/`, together with their source text. Exact file hashes and the staged-source inventory accompany this report in `review-manifest.json`. In the locations below, **M** means [`manuscript/text/main.md`](https://github.com/BWBrook/dwarf-nova-memory/blob/f48f0e2c728739a97fb90fb795eddb54c98c2dc3/manuscript/text/main.md), **S** means [`supplement.md`](https://github.com/BWBrook/dwarf-nova-memory/blob/f48f0e2c728739a97fb90fb795eddb54c98c2dc3/manuscript/text/supplement.md), and **B** means [`brief.md`](https://github.com/BWBrook/dwarf-nova-memory/blob/f48f0e2c728739a97fb90fb795eddb54c98c2dc3/manuscript/text/brief.md). Line numbers refer to that commit, not a future revision.

I read the article and supplement, recorded an initial assessment, and assessed the brief separately before consulting internal review reports, the claims ledger and interpretation specification. Parallel readers independently considered the scientific literature, methods and editorial presentation. Their agreement is not used as evidence of validity. Subsequent code inspection, original-source reading and independent calculations are distinguished below from assertions carried by the project records.

**No archive request was made. No 2018-onward observations, counts, coverage summaries or light curves were requested or inspected.** The original repository was not changed, no organisation or individual was contacted, and nothing was published or posted. All additional calculations are review diagnostics using public aggregates or artificial data; they neither amend nor reconfirm the frozen primary analysis.

## Executive assessment for Barry

**This deserves further development, but I would not yet spend your focused reading time on the current draft.** There is a worthwhile, scientifically incremental paper here: a known duration–interval association has faced a more demanding forecasting comparison. It is a coherent study, not obviously salami slicing. Given your preference for impact over speed, however, I recommend using it as the foundation of a more comprehensive investigation of recurrence information, observation error and changing activity.

The paper actually asks whether one fixed rule using **measured** completed duration scores better than a particular fixed timing-history rule, at archive-defined forecast opportunities, against extracted onset brackets and censoring outcomes. Its strongest supported finding is a positive mean difference in that specified score: **0.01653 nats per forecast**, with the reported cluster interval **0.00495–0.02812**, over 441 forecasts. I independently reproduced this aggregation from the public block summaries, checked the landmark-mixture algebra and matched fallbacks on synthetic examples, and found the documented parser repair narrowly scoped. I did not reproduce the real event extraction or individual forecast scores from the original observations.

The largest unresolved issue is the bridge from that score to the astronomical question. The scored brackets are fitted uncertainty intervals, not automatically ordinary censoring intervals. Their probability mass is a well-defined comparison statistic, but calling it a proper predictive likelihood for physical onset requires an observation/coarsening argument the manuscript does not supply. Similarly, bracket containment does not by itself establish physical coverage. A second problem is already acknowledged but insufficiently integrated into the main conclusion: the measured duration can reveal endpoint error and landmark-selection information. I independently reproduced the project's positive-gain counterexample even with a fixed baseline and nonnegative duration coefficient. This is a logical possibility, not an estimate of the real artefact. The current sensitivities do not exclude it.

A small, concrete censoring audit is also needed: the code can turn a bracket crossing a censoring cutoff into survival to that cutoff. That path is demonstrable; its occurrence or influence in the six real censored outcomes is not established by the public aggregates. These concerns call for precise corrections and bounded checks, not an indiscriminate new analysis programme.

Other limitations are defensible if made prominent. The baseline is meaningful but not a comprehensive model of changing activity. Ten time clusters and a finite simulation screen do not certify uncertainty, although my single twelve-year aggregation check remains positive. The 1960–1992 evaluation years were withheld from this project's fitting but overlap the published historical evidence motivating the sign; the 1993–2017 estimate is inconclusive. Exploratory class fits cannot replace that result or the inconclusive predeclared class rule.

The manuscript's strongest editorial opportunity is to replace its audit-centred narrative with a short scientific argument. Earlier operational SS Cyg forecasts deserve acknowledgment; the brief needs a concrete magnitude example and less post-hoc detail. Section 7 proposes an integrated expansion: first distinguish measurement-driven from physical-target gains, then test whether completed-outburst marks add information beyond evolving timing state across a deliberately chosen set of comparable systems. Keep the present result intact as an anchor. Expanding the scientific question is justified; opening the reserved archive or promising a causal disc-memory discovery is not required.

## 1. What the evidence currently establishes

### 1.1 The actual question and the strongest answer

The implemented question is more specific than “does an outburst affect the next one?” It is:

> At the forecast opportunities generated by this extraction and coverage procedure in the 1960–2017 archive, does the frozen addition of measured log duration improve the average score relative to the frozen previous-gap/recent-gap model?

That is a useful predictive question. It concerns **forecast opportunities**, not necessarily 441 independent, uniquely identified physical outbursts. It is conditional on the selected visual observations, present archive validation, threshold extraction, eligibility, landmark and outcome rules. M2 and M3 share those conditions, which makes their paired comparison substantially more defensible than comparing different selected event catalogues. It does not make the conditions scientifically irrelevant. [M §§2.1–2.3; S §§S2.1–S2.5; `manuscript/estimands.md`, C01–C04.]

The reported primary statistic is internally consistent with the public aggregation inputs. The gain is **0.01653351218**, its CR1 standard error is **0.006320284834**, and the stated two-sided 90% interval, using a t distribution with nine degrees of freedom, is **[0.004947716310, 0.02811930805]**. The prespecified directional criterion is therefore met under that procedure. This is a numerical verification of the submitted block summaries, not independent recovery of every score from the observations. [Review `checks/aggregate_check.py`; M §3.1; public `fig2-gains.json`.]

The meaningful comparison is against M2, not merely against a constant clock. M2 itself reportedly gains about **0.1168 nats** over M0. Its covariates update with the available recent history even though its coefficients are fixed. It would be inaccurate to dismiss it as an entirely static or information-free baseline. Its adequacy for the broader physical inference is another matter. [M §3.1; frozen parameters; finding I1.]

### 1.2 What remains unestablished

The present result does not establish that:

- true physical duration, rather than extraction/observation information carried by measured duration, improves prediction;
- the effect represents a direct cycle-to-cycle mechanism rather than an incompletely measured activity state;
- the reported bracket-mass score is a proper score for physical onset under the actual observation process;
- the forecasts are well calibrated for physical onset, materially more accurate in days, or useful for scheduling;
- the effect persists in the later historical segment or generalises to other stars, thresholds, observation systems or future regimes.

Several of these limits are already stated well in `estimands.md`. The needed revision is not simply to append more caveats. The headline, score definition and figure labels must use the same carefully bounded object as the specification.

### 1.3 The likely sceptical referee's strongest objection

The strongest objection is **not** “the gain is only 1.7%”, “there are only ten clusters”, or “AI agents did the work”. It is: *What exactly is being predicted and scored, and could the same measurement system create a durable apparent advantage without informative physical duration?* The article must answer that before its procedural safeguards become persuasive.

My recommendation for the current claim is **major revision of interpretation and presentation, with a short targeted methods audit**. A full new physical model, a broad algorithm competition, additional stars and opening the reserved archive are not prerequisites to the narrower paper. If the desired central claim remains physical predictive information in completed duration, further evidence is needed beyond the existing sensitivities. Given Barry's subsequent emphasis on impact, §7 separately recommends a coherent expansion; those strategic ambitions should not be confused with validity conditions for the present bounded result.

## 2. Priorities at a glance

“Essential” means needed for the central claim as currently worded, not necessarily a reason to discard its numerical result. A proposed exploratory analysis never becomes a replacement confirmation.

| ID | Priority | Finding and status | Minimum adequate response |
|---|---|---|---|
| **E1** | Essential | The proper-score/physical-onset interpretation lacks an observation-model justification. **Unresolved assumption and overbroad wording.** | State the working bracket-mass estimand explicitly; justify coarsening if retaining propriety claims; relabel coverage appropriately. |
| **E2** | Essential | Positive measured-duration gain does not exclude endpoint/landmark information. **Verified logical counterexample; real contribution unresolved.** | Narrow the central claim and include the counterexample's implication. Use the specified paired synthetic diagnostic if seeking stronger interpretation. |
| **E3** | Essential audit | A bracket crossing a censor cutoff is coded as right-censored at that cutoff. **Demonstrated code path; actual occurrence unknown.** | Audit the six censored cases and any boundary-straddling cases; quantify impact separately if present. |
| **I1** | Important | Duration can compensate for omitted state or baseline level error. **Defensible limitation with an informative small extension.** | Explain what M2 controls; retain global recentering as exploratory; at most one development-defined adaptive comparator. |
| **I2** | Important | Ten-block uncertainty and the simulation screen are conditional. **Assumptions, not a demonstrated failure.** | State the dependence approximation; report per-case simulation precision and the limited aggregation diagnostic. |
| **I3** | Important | Parameter holdout and historical scientific exposure differ. **Disclosure/framing.** | Put the published-overlap distinction beside the headline and preserve inconclusive secondary results. |
| **I4** | Important | Observation, landmark and recovery qualification need a compact, self-contained account. **Methods presentation and reproducibility limit.** | Add a timeline, primary/sensitivity endpoint distinction, quantitative qualification table and explicit reproduction tiers. |
| **I5** | Important | The contribution is a modest validation of old associations; operational precedent is missing. **Literature/context correction.** | Add the original 1985 report, narrow priority wording and verify specific inaccessible older claims. |
| **I6** | Important | Effect magnitude, calibration and utility remain easy to conflate. **Presentation.** | Interpret the score precisely and add one illustrative forecast, without claiming measured accuracy or scheduling benefit. |
| **I7** | Important | Main narrative and brief give audit history and exploratory class fits too much prominence. **Editorial judgment.** | Use the outline below; move Figure 4 and most diagnostic detail to the supplement. |
| **I8** | Important for submission | AI systems are listed in the author metadata. **Concrete incompatibility with the AAS publication route.** | Use human authorship and a transparent contribution/tool statement consistent with the chosen journal. |

## 3. Essential findings

### E1. Define the scoring target before invoking proper scoring or physical calibration

**Location.** M introduction, lines 68–78 (“A proper scoring rule…”); M §2.2, lines 127–140; §3.2, lines 212–217 (“The realised sample overcovers”); S §§S2.1, S2.4 and S3.2; Figure 3 and its caption. Code: `extract_x4.py`, `_boundary`; `extract_x3.py`, `LEVEL` and crossing posterior; `forecast_calibration.py`, `coverage_class`.

**Problem and evidence.** X4 derives boundary brackets from quantiles of a fitted crossing-time posterior, with clipping to admissible boundaries. These are not self-evidently hard inspection bounds known to contain the physical crossing. Synthetic recovery qualification, even good qualification, does not turn a posterior interval into a certain censoring set. The scorer treats the next onset as lying in the extracted interval and evaluates model probability within it, conditional on survival to issue. That is an explicitly defined *working interval likelihood*. Its automatic identification with a proper observed-data likelihood for physical onset is unsupported by the methods as written.

For physical onset time $T$, observations $Y$, and forecast history $H$, an observation likelihood would have the form

$$
p_m(Y\mid H)=\int k(Y\mid t,H)f_m(t\mid H)\,dt.
$$

Replacing this by probability in a set $[L(Y),U(Y)]$ requires a suitable observation/coarsening argument. In a standard ignorable interval-censoring construction, the relevant kernel is proportional to an indicator of the observed set, with the omitted factor not changing the model comparison. A posterior credible interval alone does not provide that kernel. Survival conditioning and uncertain landmarks require corresponding care. This is the distinction addressed by coarsening theory, not a minor choice of terminology. [Heitjan & Rubin 1991, DOI [10.1214/aos/1176348396](https://doi.org/10.1214/aos/1176348396); access limits in §9.]

Even identical sets for both forecasts do not prove propriety. A minimal example makes the issue precise: let the true event be 0 or 1 with equal probability; report the set $\{0,1\}$ when it is 0 and $\{1\}$ when it is 1. Both sets contain the truth. A forecast assigning probability $q$ to 1 has expected log set-mass score $\tfrac12\log q$, maximised at $q=1$, not at the true $q=1/2$. Informative coarsening can therefore reward the wrong physical distribution. This is an illustrative mathematical construction, not a model fitted to SS Cyg.

**What this does not show.** It does not demonstrate that the reported gain is numerically wrong, that the real ordering of M2 and M3 reverses under a better observation model, or that the comparison has no value. For narrow brackets, the common width approximately cancels in a density ratio; that is a useful approximation to investigate, not a general validity proof. Dividing both probabilities by bracket width also leaves the paired contrast unchanged and does not solve informative coarsening.

**Remedy.** Choose and state one of two defensible positions:

1. **Bounded current paper:** call the quantity a *working interval log score* or *log probability assigned to the extracted onset brackets and survival outcomes*. State the hard-bracket approximation and avoid claiming demonstrated propriety for true onset. The forecasts themselves remain probabilistic; the limitation concerns evaluation of noisy outcomes.
2. **Stronger physical-outcome claim:** give an observation model or a convincing approximation argument and evaluate its consequences. A principled measurement likelihood must account for the prior if built from an extraction posterior; simply inserting that posterior as if it were a likelihood can double-use its prior.

Figure 3 can still report set compatibility. Define “contained”, “intersecting” and “disjoint” relative to extracted brackets, and say that interpreting these as bounds on physical coverage assumes the true onset lies in the reported bracket and that censoring statements are valid. The present caption already disclaims guaranteed physical coverage and population confidence intervals; retain that restraint, but replace the unconditional “sample overcovers” headline with **“high compatibility with the extracted outcome sets under the hard-bracket approximation.”** Do not imply that this alone proves overdispersed physical forecasts.

**Resolution criterion.** A reader can identify the random outcome being predicted, the observation assumption behind every likelihood term, and the exact interpretation of Figure 3 without consulting code. The abstract, discussion, brief and claims ledger must use the same scope. If the narrow position is chosen, a wholly new measurement model is not required before publication.

### E2. Shared endpoint error is an unresolved source of predictive information, not a sensitivity already disposed of

**Location.** M abstract, lines 27–29; §4.1, lines 279–308, especially “the completed outburst carries usable information”; conclusion, lines 348–355. S §S2.4, lines 105–111. Code: `directional_forecast.py`, `_mark_duration`, `_score_selected`; `ledger_forecast.py`, `_endpoint_nodes`; `scripts/a10d_design_calculations.py`, `offset_counterexample`.

**Problem and evidence.** Write true end as $E$, estimated end as $\widehat E=E+\epsilon$, duration as $D$, next quiet interval as $Q$, and issue time as $A$. With onset otherwise held fixed for this illustration,

$$
\widehat D=D+\epsilon,
\quad \widehat Q=Q-\epsilon,
\quad \widehat a=A-\widehat E.
$$

The simple negative-coupling argument addresses only part of this system. After eligibility and survival conditioning, measured duration can identify how much the clock origin is wrong. Consequently a positive coefficient is not protected merely by being opposite to the elementary unconditional error correlation.

I independently reproduced the project's finite-state counterexample using exact rational state weights and a separate likelihood implementation. Every true duration is 10. At the same estimated issue age of 2, measured duration 10 implies mean remaining wait 4.5, whereas measured duration 16 implies 12. After fitting and fixing the baseline location and scale, a nonnegative coefficient of standardised log measured duration improves the expected score by **0.08374496 nats**. Thus the counterexample survives the primary's fixed-baseline offset structure. [Review `checks/endpoint_counterexample_check.py`; original helper, lines 196–224.]

The deliberately large six-day error in this construction is not calibrated to the real archive. Its gain is **not** a real-star bias estimate or an upper bound. Conversely, reporting recovery RMSE near a day does not prove a much smaller artefact when the observed mean gain is only 0.0165. The actual contribution remains unresolved.

The five-node end sensitivity is correctly implemented as a ratio of summed event probabilities to summed survival probabilities. It varies the current end and recomputes duration using that same node. It holds onset and preceding-gap inputs fixed and is not a full measurement model. Delaying issue by two days also leaves the shared extraction structure in place. Positive results in these variants are informative stability checks, but they do not answer the counterexample. [S §S2.4; `frozen_parameters.json`; review mixture check.]

**Remedy.** Make the headline about **the extracted-duration rule**. Present three live explanation classes together: physical cycle effects, an incompletely measured physical state, and observation/endpoint information. The current physical discussion is otherwise restrained; it does not need to abandon the disc-instability context.

If a stronger interpretation is desired, the smallest informative new diagnostic is a **paired truth-target experiment in existing synthetic direct-mark-null histories**, not another unstructured threshold sweep:

1. Retain observed issue times and a common set of truth-matched, genuinely completed, still-quiescent anchors. Do not choose anchors by future resolution or score. Account separately for false, repeated and unmatched emissions.
2. Score the **same frozen calendar-time forecasts** against true next onset as well as the extracted bracket, with appropriate administrative truth censoring. An event that truly occurs before an observation-policy cutoff is an event, even if extraction missed it.
3. If gain remains, compare a separately trained and frozen synthetic oracle-end/true-duration route on the same anchors. Merely substituting truth into the measured-feature model with unchanged coefficients is not a fair oracle comparison.

The existing operating-characteristic summaries cannot supply this analysis: `oc_experiment.run_trial` discards the full truth return. Use an already retained truth cache if available; otherwise regenerate a small, declared matched set using the frozen development inputs and recorded seeds. Include partial boundary events in the truth catalogue. This does not authorise any new real archive access.

**How outcomes change interpretation.** Loss of gain on the truth target implicates extracted-outcome scoring in that setting. Gain surviving the truth target rules out bracket construction as the sole explanation but still permits correction of a noisy clock origin. Reduction under a correctly refitted oracle route supports that source of information in the synthetic setting. None of these outcomes estimates the real artefact automatically or supplies a fresh confirmation.

**Resolution criterion.** Narrow wording is essential now. The additional diagnostic is needed before claiming the existing sensitivities exclude measurement-driven information; it is not a condition for reporting a carefully bounded archive-specific score advantage.

### E3. Audit onset intervals that cross a censoring cutoff

**Location.** M §2.2, lines 127–130; S §S2.3; `src/dnmem/prefix_features.py`, `outcome_evidence`, and the parallel logic in `prefix_reference.py`.

**Problem.** The evidence builders exclude a next-onset bracket crossing the *issue time*. However, when the upper end of a bracket lies beyond a later censoring cutoff, they can emit a right-censoring outcome at that cutoff even if the bracket's lower end precedes it. Under the paper's hard-bracket interpretation, $L<C<U$ does not establish $T>C$. Agreement between the production and reference implementations cannot validate a shared evidential assumption.

This is a demonstrated reachable code path, **not yet a demonstrated error among the six real censored forecasts**. The public inventory reports **four coverage censors, one supersession censor and one record-end censor**, but supplies no candidate onset bounds for them. The branch may never have affected the primary result; that is straightforward for the agents with retained evidence to establish.

The separate review fixture makes **16 calls** across both evidence builders and before-cutoff, crossing-cutoff, after-cutoff and issue-straddle controls. Both builders classify an onset bracket $(18,22]$, issue 10 and cutoff 20 as right-censored at 20 under coverage and supersession stopping. An onset at 19 is consistent with the bracket and inconsistent with that survival assertion. This isolates the routing assumption; it does not reconstruct a physical light curve. Relevant branches are prefix_features.py lines 223–231 and prefix_reference.py lines 355–370; the scorer uses survival at the recorded cutoff in ledger_forecast.py lines 254–258. [Review checks/censor_straddle.py; primary provenance summary.]

**Smallest useful audit and remedy.** For the six primary censored cases, report the censor reason and whether any available next-onset bracket overlaps the cutoff. The emitted censor row discards that bracket, so recover the candidate from the existing frozen extraction if necessary. Do this within the already opened 1960–2017 record; do not obtain observations beyond its end. If no crossing occurs, state that and retain a synthetic edge-case check for future work. If crossings occur, preserve the frozen score, document the affected terms and their contribution, and add a separately labelled correction/sensitivity using an explicitly justified outcome rule. For example, under a hard-bracket approximation one may retain only a defensible lower bound rather than asserting survival to a point inside the bracket; the observation contract must determine the rule. Simply truncating the event interval at the cutoff would assert an equally unproved event by that time.

**Resolution criterion.** A small table establishes occurrence and the affected original paired-score contributions, or documents zero affected cases. If needed, a separately labelled sensitivity quantifies the change under a declared corrected outcome rule. The table alone does not bound the maximum change under all possible corrections. Any altered analysis remains an exploratory amendment with the original result retained. This audit belongs before a confident central claim because a few unusual log-score terms can matter to a small mean gain.

## 4. Important scientific and reporting revisions

### I1. Challenge the baseline in the one way most relevant to the interpretation

**Location.** M §2.2, lines 131–140; §3.3, lines 226–238; §4.1. S §§S2.4 and S3.5. Frozen M2/M3 parameters and the exploratory recentering calculations.

**Judgment.** M2 is a meaningful challenge: it includes the previous covered quiet gap and an earlier recent-gap mean, updates those features at each forecast, and materially improves on M0. Fixing its nuisance parameters while adding duration gives exact nesting and isolates the change in the forecast rule. I found no hidden nuisance refit in the primary comparison. It is reasonable to condition inference on the already trained forecasts; the paper need not add training-parameter uncertainty merely to compare those fixed rules.

However, the result is not “duration beyond all relevant timing information”. M2 has a fixed linear location relationship and fixed lognormal shape. Duration may improve an imperfect representation of activity, including a level shift between development and evaluation. The manuscript's exploratory global recentering shows this is not imaginary: it attributes about **0.00370 nats** to the frozen duration term's mean contribution and leaves about **0.01283 nats** in that particular recentered contrast. These are useful descriptive calculations, not a causal partition or evidence that within-period drift has been removed. [M §3.3; interpretation specification, C20.]

**Smallest useful new comparison.** If the agents undertake one targeted level-adapting comparator, use the same prefix features. For example, with $q$ the previous gap and $L$ the mean of earlier log gaps, consider a log-location model

$$
\mu=\alpha+L+\gamma(\log q-L).
$$

Its location shifts one-for-one when both historical log-gap summaries shift together. This constrains the raw log-gap coefficients to sum to one; it is not a richer model class or a guaranteed improvement over M2. Specify it now, fit its parameters and a matched duration addition using **1910–1959 only**, retain explicit development-defined handling of missing $L$ and the common fallbacks/outcomes, and assess it on the already inspected record as **exploratory**. No retrospective full-record estimate may enter an issue-time feature. This is a concrete diagnostic of level adaptation, not a claim that this model is optimal or a request for a model tournament.

If a credible, comparably performing timing model absorbs the gain, the scientific interpretation becomes “duration helps this particular historically fitted baseline”. If duration helps a stronger timing model too, the omitted-level explanation is weakened, not excluded. A poorly fitting alternative is not a useful negative control. Do not tune a sequence of models on evaluation gains until one gives the desired answer.

**Resolution criterion.** The article explicitly states what timing information and functional form M2 controls. The existing global adjustment remains visibly exploratory. A narrower baseline-relative claim can stand without the additional comparator; broader claims about residual physical state cannot rely on global recentering alone.

### I2. Explain the uncertainty assumptions and the finite screen without either dismissal or certification

**Location.** M §2.3, lines 144–150; §3.1, lines 181–196; S §§S2.5–S2.6 and S3.1. Code: oc_statistics.py, forecast_experiment.py and oc_streams.py; data/simulations/a10d_20261108/report.json.

**What I verified.** For block sizes $n_g$ and block mean paired gains $\bar d_g$, the published computation is

$$
\bar d=\frac{\sum_g n_g\bar d_g}{N},\qquad
\widehat{\mathrm{SE}}^2=
\frac{G}{G-1}\frac{\sum_g[n_g(\bar d_g-\bar d)]^2}{N^2}.
$$

I reproduced this from all ten public block summaries. I also combined adjacent blocks into **five nominal twelve-year groups**, a single exploratory check of a longer dependence scale. The mean is unchanged; the corresponding 90% t interval is **[0.00363, 0.02944]**. This is reassuring against that particular regrouping, not validation of independence or a replacement registered analysis. I did not search across block widths for a favourable result. [Review aggregate check.]

Ten groups alone do not invalidate inference. Small-group t methods have principled support under appropriate independence and approximately Gaussian group-estimate assumptions. But that does not automatically establish the validity of this issuance-weighted CR1 construction for adjacent periods of one changing star. The approximation concerns dependence in **paired score differences**, and the target is the issuance-weighted mean, not an equal-period average. The paper should explain why six-year groups are thought adequate and what remains assumed. [Ibragimov & Müller 2010, DOI [10.1198/jbes.2009.08046](https://doi.org/10.1198/jbes.2009.08046); Cameron & Miller 2015, DOI [10.3368/jhr.50.2.317](https://doi.org/10.3368/jhr.50.2.317).]

The directional rule is coherent with the registered positive alternative. A two-sided 90% interval's positive lower endpoint is equivalent to the stipulated one-sided 5% t criterion. The direction's historical motivation should be disclosed, not treated as invalid simply because it was informed by previous science. Do not turn the result into a posterior probability that the claim is true.

The finite operating-characteristic screen deserves a short per-case table:

| Nominal-null simulation family | Primary confirmations | Exact 95% binomial interval within setting |
|---|---:|---:|
| Null | 0/40 | 0–0.0881 |
| Gross contamination | 2/40 | 0.0061–0.1692 |
| Observer offset | 0/40 | 0–0.0881 |
| Adaptive effort | 0/40 | 0–0.0881 |
| Structured null | 1/40 | 0.0006–0.1316 |
| Alternative waveform null | 0/20 | 0–0.1684 |

These intervals describe confirmation probabilities within the named simulation families. Calling them false-positive probabilities additionally requires a null for the actual observed-feature score contrast; a physical direct-effect null does not suffice, as E2 illustrates. Shared streams across settings make **3/220** an unsuitable iid error-rate estimate, as the manuscript already acknowledges. The alternative setting's joint-Monte-Carlo interval coverage was **34/40 overall and 31/37 for interior fits**; passing its low-power screen does not establish nominal 90% coverage. The reported **11/40** success rate at the reference alternative is scenario-specific. These are finite diagnostics with real value, not a size certificate. The independently reset simulation blocks also do not establish robustness to a state persisting across the full evaluation record.

**Remedy and resolution criterion.** Include the per-case table and a concise assumption paragraph; retain the correct distinction between reference Monte Carlo uncertainty and exact truth. Remove the five-decimal “SE inflation failure boundary” from the main narrative. Eight positive block means and positive leave-one-block-out means are descriptive, not eight independent replications or proof that every omission retains significance. No generic bootstrap or alternative standard error is required unless it addresses a specified remaining dependence concern.

### I3. Historical exposure and inconclusive secondary analyses belong beside the headline

**Location.** M abstract; introduction, lines 46–88; §3.2, lines 200–210; §3.4; conclusion. S §§S3.3–S3.5. Interpretation specification, C06–C08 and C21–C24.

**Judgment.** Withholding 1960–2017 from this project's fitting and tuning is meaningful. It is not equivalent to choosing a question without prior knowledge of these years: the historical duration–gap result used to motivate the directional hypothesis includes observations through 1992. The original conditional forecast comparison is new even where the older aggregate association was known. It should be described as parameter-frozen retrospective evaluation, not an entirely independent rediscovery of the association.

The abstract already reports the later estimate. Improve it by explaining why **1993–2017** is a separate qualification: it is outside the CM92 record, not merely a convenient later slice. Do not call it wholly scientifically unexposed; other historical studies have examined parts of the later record for other questions.

The later estimate **0.0057 [−0.0107, 0.0221]** is compatible with zero and with a modest benefit. It neither establishes disappearance nor supplies independent confirmation. There is no prespecified era-difference test; overlapping intervals are not themselves a test of equality. The predeclared class/within-class rule, **0.0025 [−0.0022, 0.0072]**, remains inconclusive.

The subsequent class fits are interesting descriptions. A class-only fit achieving LR 14.7 versus 11.7 for continuous log duration, and a within-class increment of 0.17, do not validate the class rule, show equivalence of effects within classes, or establish a physical two-state mechanism. Equal-dimensional nonnested models are being compared on the already seen outcomes. The shared-level adjustment's improved class score is a coding/calibration lesson, not a rescue of the frozen result. The manuscript often states these qualifications correctly; the prominence of §3.4, Figure 4 and the conclusion nevertheless gives the analyses more authority than their role warrants.

**Remedy and resolution criterion.** State the published-overlap distinction adjacent to the primary result; keep both secondary outcomes in one short results subsection; move most class/lag/era refits and Figure 4 to the supplement. A reader should be able to stop after the abstract and retain the correct hierarchy: primary score advantage, later and class-rule uncertainty, then exploratory explanation.

### I4. Make the observation-to-score chain independently understandable

**Location.** M §§2.1–2.3; S §§S2.1–S2.4 and S5; Figure 1; prefix_features.py; evaluation_native.py; A04i qualification audit.

**What is sound.** Predictors use the reported-date prefix, the issue is triggered by end confirmation, and outcome evidence is kept on the scoring side. The code and selected poisoned-future tests support this separation. The primary point-end score uses survival conditioning rather than pretending that the forecast was issued exactly at the estimated end. Matched routing yields exact zero contrasts when duration cannot change the rule.

**What requires clearer explanation.**

- **Reported time is not historical availability.** Present archive validation, uploads and revisions are not known as of each historical issue. The existing limitation is correct; call this a reported-observation-time retrospective evaluation consistently. No claim of a genuinely deployable replay should be inferred from passing prefix tests.
- **The target is extraction-defined.** Current archive filtering, confirmation and coverage rules can miss events or select a different population. Common selection makes the paired comparison fairer within that population; it does not prove recovery of the next physical event. Observer behaviour can be associated with activity, brightness and duration.
- **The primary uses a point endpoint.** Give its rule explicitly before the separate five-node sensitivity. For the latter, show $\log(\sum_k w_kN_k)-\log(\sum_k w_kS_k)$ and say that onset and preceding-gap inputs stay fixed. The algebra is correct; the missing bridge between a posterior extractor and a point-end primary is a description problem.
- **Qualification is conditional.** X4 passed checks on a known waveform family; recovery on the failed source-blind benchmark was not performed. Do not describe that as either successful unseen-family validation or a failed X4 recovery test. The magnitude-9.5 failure in “later eras” refers to later **development** decades, not the 1960–2017 evaluation.

The supplement needs a small quantitative qualification table, not another assertion that checks passed. In the ordinary known-family cells, the committed audit reports onset coverage about **92.8–96.7%**, end coverage **94.6–98.0%**, and duration RMSE **0.56–1.28 days**, with onset brackets roughly **1.77–2.65 days** wide. Label these synthetic, conditional results and show the relevant setting/era definitions. They are not measured error rates in the real evaluation record. Include the failed threshold condition and the unseen-family access limitation in the same table. [A04i audit, ordinary cells and threshold-recovery section.]

**Reproducibility.** The public material supports figure rebuilding, aggregate arithmetic and code/synthetic checks. It does not presently allow an independent reader to regenerate the full real-event ledger and scores without retained archive inputs. State those tiers plainly. A DOI, hashes and a passing source manifest verify identity and consistency; they do not substitute for accessible evidence. If redistribution terms allow, a privacy-safe per-forecast table of outcomes, paired scores, censor reasons and block membership would materially improve auditability without publishing observer identities or raw archive exports. Otherwise provide a documented controlled reproduction route. Do not promise release of restricted material.

**Resolution criterion.** A timeline explains onset, estimated end, confirmation/issue, forecast age, next bracket and censor cutoff. A compact table distinguishes fit years, reported-time prefix information, scoring-only information, eligibility and fallbacks. The supplement identifies exactly what a public reader can and cannot reproduce.

### I5. Recast novelty as a scientific comparison, and add the overlooked precedent

**Location.** M introduction, lines 46–88, especially “The only held-out timing forecast…” and “the first preregistered…”; §4.1 physical context; references.

**Literature judgment.** The basic duration/following-interval association, short/long outburst distinctions, alternation and changing activity are historical topics. The useful advance is asking whether a recorded completed-duration feature improves a genuinely specified timing forecast on later data. That is scientifically more informative than a correlation, but its answer remains conditional on E1–E2.

An omitted primary report documents **SS Cyg timing predictions used for coordinated observations in 1984**: Seetha et al., *Information Bulletin on Variable Stars* **2839** (1985). It describes predicted dates with ±5-day tolerances for an IUE/Voyager/ground campaign; one approximately matched and another outburst came early. This is not a formal probabilistic benchmark, but it shows that practical recurrence forecasting predates the cited machine-learning example. Cite the original report; its circular references can be followed separately if needed. [Publisher [text](https://ibvs.konkoly.hu/pub/ibvs/2801/2839.txt) and [PDF](https://ibvs.konkoly.hu/pub/ibvs/2801/2839.pdf).]

The original Grigorievskiy et al. (2014) paper does support the manuscript's substantive distinction: chronological training/validation/test splits, **one test outburst but many rolling forecast origins**, and point-error/failure summaries. Randomised model fits are not a calibrated predictive-distribution assessment. Describe it as the closest formal held-out comparison located, without implying that operational timing forecasts were absent. [Original [ITISE paper](https://research.cs.aalto.fi/aml/Publications/Publication216.pdf), §§4–6.]

Price et al. (2007) should not appear solely as a failed short-term precursor search. Its historical analysis also relates changing outburst rate to long-term variability, providing useful context for M2 and the omitted-state question. That relationship is retrospective and smoothed, not validated forecasting. Ak, Özkan & Mattei (2002) is useful for the distinction among duration, quiescent interval and onset-to-onset cycle, and for the dangers of shared definitions. [DOIs [10.1086/524413](https://doi.org/10.1086/524413), [10.1051/0004-6361:20020600](https://doi.org/10.1051/0004-6361:20020600).]

I could not independently read CM92 Table 4, the detailed Cannizzo (1993) pages, or the original Hempelmann–Kurths paper. The repository records a prior original-page check, but that is not my verification. Before submission, preserve exact page/table support for the historical correlations, subscript direction and specific disc-model statements. This is an access limitation and a source-check task, not a discovered contradiction.

**Interest and audience.** A specialist can reasonably care that an old association yields a small increment beyond a concrete timing-history forecast, and that the increment is not yet secure in the later segment. A general astrophysicist should learn what duration can currently add to recurrence prediction and why it does not identify a disc mechanism. A planetary scientist may find the recurrent-event methodology relevant, but there is no established planetary application here. The defensible wider lesson is conditional: in changing, imperfectly observed systems, event marks can improve a forecast by tracking state or observation error. This study illustrates that identification problem; it does not establish a universal law of memory or a general superiority of one forecasting architecture.

**Resolution criterion.** Replace procedural priority with an explicit contribution statement. Add the operational precedent, keep search limitations visible in the literature record, and ensure physical claims are backed by the original pages. A discovery-style or broad-impact framing would overpromise; a careful specialist validation paper is worthwhile.

### I6. Give the effect a concrete meaning without inventing practical benefit

**Location.** M abstract; §§3.1–3.3; Figure 1; B “What we found”, item 1; fig1-illustration.json.

Exponentiating the mean paired log score gives **1.01667**: approximately **1.7% higher geometric mean probability assigned to the scored bracket/survival evidence under the working model**. It is not 1.7% less timing error, 1.7 percentage points more event probability, 1.7% more successful observations, or the fraction of disc state explained. A geometric mean ratio can arise from heterogeneous changes across forecasts. Likewise, the duration gain being about 14% of M2's gain over M0 is not variance explained. The interpretation specification gets these distinctions right; they deserve a simpler main-text explanation.

One saved, date-selected Figure 1 forecast gives an accessible illustration. Interpolating its saved CDF grid, the forecast median remaining wait changes from about **27.6 to 26.8 days**; the predicted chance of onset within 30 days changes from about **57.7% to 60.3%**. These are differences between two forecasts for one example, **not** an average accuracy improvement or a measured scheduling benefit. The near-coincident curves are scientifically appropriate and should not be stretched visually to make the effect look large.

**Remedy and resolution criterion.** Add those illustrative values to Figure 1 or the brief, with the date-selection rule. Keep exact nats and uncertainty in the result table. Make calibration a separate assessment with E1's qualification. A scheduling claim would require a specified observing decision, loss/cost and comparison; that is a future study, not an essential addition to this paper.

### I8. Correct authorship metadata while preserving a candid account of AI contributions

**Location.** manuscript/authors.yaml; rendered article byline; M “Roles of AI systems and humans”, lines 370–400; B “How this work was done”.

The metadata lists the AI systems as an author entry. Current AAS author guidance explicitly excludes AI tools from authorship and requires disclosure of their use and human responsibility. If an AAS journal is the intended route, this is a concrete publication-readiness correction, independent of the scientific quality. [Official [AAS guidance](https://journals.aas.org/author-llm-guidelines), checked 9 November 2026.]

Use an appropriate human byline and a frank contribution statement: the agents conducted much of the implementation, checking and drafting; Barry directed the science, made consequential decisions and accepts responsibility after review. Avoid reducing his role to approving release, and avoid implying that agent cross-checks constitute external scientific validation. A concise statement in the article can link to the detailed tool/work history in the repository. The science should be judged on evidence, not on whether the tools are described as collaborators.

**Resolution criterion.** The chosen journal's policy is met, actual contributions remain transparent, and human accountability is unambiguous. This requires no suppression of the agent-assisted workflow.

## 5. Execution integrity: the parser repair is documented and appears proportionate

**Location.** M §2.3, lines 151–159; §4.2, especially lines 314–316; S §§S2.7 and S4; B finding 2. Repair commit [5e39aeb772c427ef29671c1a9c80b22c05519b58](https://github.com/BWBrook/dwarf-nova-memory/commit/5e39aeb772c427ef29671c1a9c80b22c05519b58); failed and completed A10i receipts.

I inspected the actual repair, rather than inferring innocence from its description. The runtime change accepts the exact token **None**, alongside the already accepted blank value, as missing uncertainty. It preserves the native field and does not change the forecasts' selection rule to discard an observation. Numeric zero remains numeric; malformed and invalid uncertainty values remain rejected. The inspected forecasting/eligibility path does not use uncertainty values.

Comparison of the failed and completed receipt inventories identifies **evaluation_native.py as the only changed runtime source file**. The frozen parameters and protocol hashes match. The selected synthetic tests include a blank-versus-None equivalence check for the ledger, evidence and scores. These checks support the claimed narrow effect; they do not independently reconstruct the inaccessible real-data crash.

The public record places the protocol publication at **12:34:47 UTC**, first evaluation request at **12:38:28**, repair commit at **12:46:18**, renewed acquisition at **12:51:18**, and concordance/primary writing at approximately **13:06:58**, all on 8 November. These are repository attestations and commit/receipt records. I could not independently retrieve the live Zenodo record in this session and cannot certify what any participant saw outside the recorded execution.

**Judgment.** I found no evidence that this repair changed the scientific comparison or was selected after inspecting scores. It warrants a clear amendment record, not automatic rejection. Conversely, the original DOI does not timestamp the repaired parser, and the initial request had already occurred; calling the entire execution untouched would be false. The present records are unusually useful for evaluating that distinction.

**Editorial remedy.** Replace “however innocent”, “not perfectly clean” and repeated statements about permanently lost status with a precise account once in Methods, linked to the supplement. Preserve the failed attempt and full history in the repository. It is unnecessary to repeat the repair in every figure caption or make it the second scientific finding in the brief.

Suggested wording:

> The registered execution initially stopped while reading an exact missing-value token in the native uncertainty field, before producing an event ledger or forecast score. A documented parser amendment accepted that token as missing; the observation rows, forecast inputs, frozen parameters and scoring rule were unchanged. The original and amended source identities and execution receipts are retained in the supplement.

Use the last sentence's scope only as far as the recorded invariance evidence supports it. This review supports the parser/parameter claim, not a new independent certification of every raw record. **No further large repair investigation is warranted unless a concrete inconsistency emerges.**

## 6. I7 — Editorial structure, figures and replacement wording

### 6.1 The present reading experience

The opening contains the right ingredients: an accessible recurrence question, disc physics, an unusually long observational record and a historical association that deserves a harder test. It then asks the reader to absorb correlation signs, procedural labels, model codes, a qualification vocabulary, a parser amendment and several exploratory interpretations before the scientific payoff is stable.

The draft is careful but frequently reads as an internal audit translated into an article. Tables 1 and 2, repeated caveats, and several captions re-establish the same boundaries. The class-based post-hoc account receives almost as much narrative attention as the actual frozen comparison. This makes a modest result feel simultaneously overdefended and overinterpreted. The solution is a stronger hierarchy, not less methodological honesty.

**Proposed main-paper sequence:**

1. **Why ask?** Recurrence is irregular; earlier duration–interval associations do not establish incremental forecasting value; the distinction matters for interpreting recurrence and designing observations.
2. **What is compared?** A simple timeline and the two matched forecasts, with measured duration as the one primary addition.
3. **What information and outcomes are used?** Dates, archive/extraction conditions, the working score, censoring and the fit/evaluation split. Explain the published historical overlap here.
4. **What happened?** Primary gain, size, uncertainty and the later/class-rule qualifications; separate bracket-compatibility assessment.
5. **What can explain it?** Measurement information, imperfect activity-state modelling and physical recurrence remain alternatives. One brief paragraph points to exploratory fits in the supplement.
6. **What is the contribution?** A bounded comparison of a completed-duration rule, with a focused next discriminating test.

The supplement should contain full extraction/scoring definitions, the qualification and simulation tables, secondary/exploratory analyses, moved Figure 4 and a compact execution amendment. Keep project-stage identifiers, detailed correction conversations and the long tool chronology in the repository/replication guide.

### 6.2 Titles

My preferred title is **“Does measured outburst duration improve recurrence forecasts for SS Cygni?”** It keeps the scientific question, names the measured quantity and avoids implying a mechanism or operational demonstration.

Two viable alternatives are:

- **“Testing duration-based recurrence forecasts in the historical SS Cygni record”** — strongest emphasis on the actual study design.
- **“A modest forecast-score gain from measured outburst duration in SS Cygni”** — strongest emphasis on the bounded result, suitable if the working-score interpretation is retained.

“Preregistered” can appear in the abstract and methods without carrying the title's novelty argument.

### 6.3 Proposed abstract

This draft assumes the E3 audit does not materially change the reported comparison and adopts E1's bounded score interpretation. It is not a substitute for resolving those findings.

> Earlier studies of the dwarf nova SS Cygni associated outburst duration with the following quiet interval. We test whether measured duration improves prediction beyond a specified timing-history baseline. We extracted events from archived visual observations, fitted lognormal waiting-time models using 1910–1959, and froze the forecast rules before accessing the 1960–2017 evaluation record. Retrospective forecasts used observations dated before end confirmation; historical upload and revision times are unknown. Adding completed duration improved the mean paired working interval log score by 0.0165 nats across 441 forecasts (90% cluster interval 0.0049–0.0281), meeting the preregistered criterion. The score measures probability assigned to extracted onset brackets or survival outcomes; its physical interpretation depends on the observation model. The gain in 1993–2017, outside the record used by the historical association study, was inconclusive (0.0057; −0.0107 to 0.0221), as was a predeclared class-based rule. A documented missing-value parser repair preceded scoring and left the forecasting settings unchanged. The result supports a modest score advantage for the extracted-duration rule over this frozen baseline. It does not distinguish physical recurrence information from activity-state or measurement information, establish useful telescope-scheduling gains, or demonstrate generality beyond this record and extraction procedure.

**What this changes.** The abstract now says what the outcome score means, identifies why the later period matters, and removes the exploratory class-fit explanation from the result hierarchy. If a shorter abstract is needed, move the repair sentence to the registration statement before removing the later-period or measurement qualification.

### 6.4 A replacement for the pivotal interpretation paragraph

Replace M §4.1's opening and connect it to the measurement paragraph:

> The frozen rule using measured completed duration assigned slightly more probability to the extracted next-onset evidence than the specified timing-history rule. This is a result about an observable feature within one retrospective forecasting procedure. It does not determine why the feature helps. Duration may reflect the preceding disc cycle, track a slowly varying state inadequately captured by recent intervals, or contain information about errors in the estimated endpoint and forecast age. The positive score contrast distinguishes the two forecasting rules; it does not distinguish these explanations.

This permits a substantive physical discussion without placing causal or latent-state interpretation ahead of the measurement issue.

### 6.5 Figures and tables

The inspected PDFs render cleanly. The principal problem is emphasis and interpretation, not broken layout.

| Item | Recommended change | What it accomplishes |
|---|---|---|
| **Figure 1** | Retain the light curve and two forecast distributions. Add arrows for completed duration and the following quiet interval, mark end versus issue, and annotate the illustrative 30-day probabilities. Shorten the caption. | Makes the common endpoint, landmark conditioning and small forecast change intelligible before equations. |
| **Figure 2** | Put the overall and later-period estimates before the block means. Retain the frozen class-rule row in the paper, but distinguish it from the primary. | Establishes the main result and qualification before descriptive temporal detail. |
| **Figure 3** | Retain the distinction between containment/intersection ranges and sampling intervals, but apply E1's target/coverage correction. | Prevents apparent physical calibration guarantees from estimated brackets. |
| **Figure 4** | Move to the supplement. Avoid reading cross-era LR bar lengths as effect-size changes; sample sizes differ and periods overlap. | Gives exploratory explanation proportionate visual authority. |
| **Tables 1 and 2** | Merge the overlapping design/claim-limit material into one compact table or a short methods paragraph; move audit detail out of the main paper. | Removes repeated defensive framing. |
| **Supplement** | Add one compact extraction-qualification table and one per-setting simulation table. | Makes the consequential evidence visible without repository archaeology. |

A few terminology edits will reduce reader effort: use **forecast** in ordinary prose instead of repeated “issuance”; define **clock** once as the lognormal waiting-time model; explain **landmark** as the moment the forecast is made; replace bare **qualified** with the actual synthetic conditions; distinguish **quiet interval** from onset-to-onset **cycle**. None of these changes requires simplifying the mathematics.

### 6.6 The two-page brief, assessed as its own product

The brief is readable at the outset, visually clean and exactly two pages. It introduces the binary/disc system and acknowledges the observational contribution. Its closing claim about measured duration “under these rules” is better bounded than parts of the article.

It is not yet fully successful for an intelligent nonspecialist. The figure precedes the forecaster explanation; the text expects readers to interpret nats, a confidence range, geometric likelihood, a class/within-class rule and a shared-level adjustment. The parser repair is item 2 in the findings, giving a software event more prominence than the astronomical qualification.

**Specific revision instructions:**

- Use **“Can a dwarf nova's last outburst help forecast its next?”** Introduce “outburst” once and then use it consistently; repeated “flare” can suggest a different phenomenon.
- Replace “almost every clear night since 1896” with “a long, exceptionally dense observational record”. The former implies an opportunity-coverage guarantee the study does not establish.
- Explain the two forecasters before the result figure. Use only the overall and later-era rows in the brief's plot; retain exact score units in its caption.
- Replace “Not every check agreed” with **“The later years were less decisive.”** Inconclusive results are not contradictory findings.
- Remove the exploratory class-fit/level-adjustment account. It does not help this audience understand the primary result.
- Make the magnitude concrete using the Figure 1 illustration: in that example the two forecasts gave approximately 58% and 60% chances of onset within 30 days. Explicitly identify it as one example, not average accuracy.
- Move the parser repair to a short transparency note. Retain unknown historical data-arrival times and the distinction between measurement information and physical memory.
- Give human/AI contributions in two or three accurate sentences and link to the reviewed version, not only the moving repository.

A replacement result paragraph could read:

> Using the measured length of the previous outburst gave a small average improvement in the historical forecast score. In one illustrative forecast, it changed the predicted chance of another outburst within 30 days from about 58% to 60%. The later part of the record was less decisive. The study cannot yet tell whether duration helps because of the star's physical state, imperfections in the timing model, or how the outbursts were measured.

**Resolution criterion.** Without reading the article, a nonspecialist can explain the question, the small improvement, the later-period uncertainty and the unresolved physical interpretation. They should not repeat “1.7% more accurate”, think the study discovered two outburst types, or regard the parser repair as an astronomical result.

## 7. Strategic expansion: what would make this more consequential?

This section responds to Barry's additional instruction that there is no hard deadline and impact matters more than a minor increment. It is a research-design recommendation, not a new validity hurdle retrospectively imposed on the original experiment.

### 7.1 Is the present study salami slicing?

**Not on the evidence reviewed.** It asks one coherent question and reports its important qualifications; that is different from splitting a single result into several thin papers. Its weakness is scientific scope: a small, extraction-dependent increment for one star over one forecast baseline leaves the main physical and observational alternatives unresolved. A specialist validation paper is defensible, but procedural thoroughness alone will not make it broadly important.

Given Barry's stated preference, **I would develop a larger integrated paper rather than make rapid submission of this version the goal**. Keep the frozen experiment as a named component and benchmark within that study. Do not retrospectively relabel it a preregistered test of the expanded question, and do not divide the later class, state and measurement investigations into separate marginal-result papers.

### 7.2 A central question capable of carrying the larger paper

> **Which properties of a completed dwarf-nova outburst provide reproducible information about recurrence beyond evolving timing history, and how much of that apparent information survives an explicit treatment of observation and event measurement?**

This adds two scientific dimensions to the current question: **where the information comes from** and **how portable it is**. It supports useful outcomes even if duration's current advantage weakens. It remains an observational-prediction question; identifying a causal disc mechanism would require additional discriminating evidence.

The corresponding hypotheses should be explicit:

| Hypothesis | Discriminating evidence | What the result would mean |
|---|---|---|
| **Observation information** accounts for an apparent duration increment | In matched synthetic histories, distinguish the latent event target, extracted target and uncertain clock origin; compare independent boundary treatments in real data | A measurable contribution of observation/extraction to the forecast advantage; not automatically a real-star correction factor |
| **Evolving activity state** makes duration informative beyond a restricted history summary | Compare fixed timing summaries with a carefully specified evolving-state timing model, then add marks under the same observation model | Whether marks add information beyond that fuller representation of history; still conditional on the state model |
| **Residual mark information** persists across credible measurement choices and timing models | A consistent increment on matched outcomes, with uncertainty, in separately defined validation samples | Stronger evidence of reproducible recurrence information in observed outburst properties; not by itself direct causation |
| **The relationship differs across systems or activity regimes** | Estimate both shared and system-specific performance with adequate precision and predefined regime definitions | A description of where a forecast relationship transfers and where it does not, rather than a universal pooled coefficient |

### 7.3 Recommended architecture: three connected work packages

**A. Establish what is observable and scoreable.** Resolve E1–E3 first. Define the latent target precisely: an idealised optical threshold crossing is not necessarily the physical initiation of a disc instability. Make synthetic truth, the extraction target and the forecast target correspond. Develop one defensible observation-aware evaluation route, or explicitly bound the approximation used. Validate it under the endpoint/selection conditions that can mimic the reported effect, with practical error scales informed by the development qualification.

The paired truth-target experiment in E2 is the right first prototype. For the already inspected real record, compare one genuinely different boundary treatment or a modest, blinded annotation sample spanning boundary quality and outburst duration. Annotation must be blind to the subsequent interval and score. A second threshold applied to the same measurements is a sensitivity, not independent ground truth. All of this is exploratory for SS Cyg.

**B. Separate timing history, changing state and event marks within one model ladder.** Use a small interpretable sequence: the frozen benchmark; a location-adapting timing model; an evolving-state timing model; and matched additions of completed-outburst information. Give every comparator the same information cutoff and observation contract. For a latent-state model, distinguish using duration as another observation of state from adding an explicit duration-to-next-interval term. These mechanisms can be observationally confounded; predictive superiority alone will not identify which physical pathway is true.

Specify exactly what enters the state filter. If the timing baseline already ingests the completed duration, the added coefficient no longer tests total mark information beyond timing. If only the marked model gets a flexible state, adaptation and duration are confounded. A consistently available, pre-outburst quiet-brightness summary is a potentially useful separate state proxy, but it is not a measured mass-transfer rate and needs its own observation treatment.

Do not begin by adding every measurable outburst attribute. Start with the duration/class comparison already motivated by history. A further mark such as an integrated brightness measure or decline shape should enter only with a specific physical rationale and a credible measurement model. Visual magnitude, radiated energy and accreted mass are different quantities. Introducing a poorly calibrated “energy” variable would expand the claim faster than the evidence.

If a physical-model track is pursued, use forward simulations to ask which **observable conditional patterns** distinguish candidate scenarios after the actual observation process is imposed. Engage dwarf-nova expertise in specifying those scenarios before treating a flexible statistical state as a disc parameter. If plausible mechanisms are indistinguishable at the available cadence and precision, report that limit and stop the mechanism-identification track rather than manufacturing a preferred story.

**C. Test transport to a deliberately chosen cohort.** A small cohort of comparable, well-observed ordinary-outburst systems is preferable as the first extension to a mixture of physically different subclasses. Choose inclusion criteria from scientific classification and observation adequacy, not from favourable duration coefficients. Record exclusions and whether they depend on the target/mark. Select the number of systems using anticipated usable cycles, effect heterogeneity and precision planning; an arbitrary large catalogue is not a substitute for an analysable cohort.

Treat the inspected SS Cyg record as development/exploration for the enlarged model. Where genuinely uninspected records are available within the authorised historical boundary, freeze the enlarged comparison before accessing them. Prior published aggregate associations still count as historical scientific exposure. Evaluate transfer to held-out systems as well as later periods only if the sample supports it; many forecasts from a few stars are not many independent systems.

A hierarchical model can partially pool parameters, but its validation must still reveal system-specific performance. A single pooled positive mean can hide gains confined to one well-sampled star. Start within a comparable outburst class; expansion to superoutbursts or standstill behaviour is a subsequent physics question unless explicitly modelled from the outset.

Predefine both a star-balanced and an event-weighted summary, with their different target populations, so SS Cyg cannot silently dominate. A leave-system-out experiment also needs a declared initial calibration history for the new star; otherwise “transfer” is ambiguous.

The population catalogues of [Coppejans et al. (2016)](https://doi.org/10.1093/mnras/stv2921) and [Otulakowska-Hypka et al. (2016)](https://doi.org/10.1093/mnras/stw1120) help define scope and selection. They are not ready-made consecutive-event benchmarks: the former explicitly treats detected recurrence intervals as limits affected by missed events, while the latter compiles representative photometric properties from heterogeneous material. Cross-star catalogue correlations cannot replace the proposed within-star forecast comparison. For a physical simulation component, [Hameury et al. (1998)](https://doi.org/10.1111/j.1365-8711.1998.01773.x) provides an original example in which numerical resolution and boundary treatment matter; one convenient simulated light curve is not a unique physical explanation.

**The 2018-onward archive remains closed throughout this proposal.** No part of this review requests its observations, counts or coverage. The expansion is not contingent on opening it. Any new data acquisition would be a separate execution step under a specified protocol and the project's existing boundaries.

### 7.4 Stages and stopping rules

| Stage | Smallest useful deliverable | Proceed when… | If it fails or remains ambiguous… |
|---|---|---|---|
| **1. Current-result validity** | Explicit observation/score contract and six-case censor audit | The exact bounded primary claim is defensible | Correct or narrow the claim before building a larger narrative |
| **2. Observation prototype** | Paired synthetic truth-target/oracle analysis at declared settings; one independent real-boundary sensitivity on already inspected data | The evaluation can distinguish the principal measurement pathways with useful precision | Make measurement/observability the central result or improve the evaluation; do not interpret a positive bracket score as physical information |
| **3. State-versus-mark prototype** | One specified timing/state model ladder, developed on inspected data, with recoverability checks | Mark and state contributions are predictively distinguishable enough to justify testing | Limit claims to prediction; do not promise mechanistic identification |
| **4. Historical cohort protocol** | Selection rules, information cutoffs, model choices, uncertainty target, simulation-based precision plan and explicit record-exposure table | The proposed sample can answer the chosen question at meaningful precision | Reduce heterogeneity or change the target; do not add stars solely to obtain significance |
| **5. Enlarged evaluation** | Registered new comparison where possible, plus clearly separated exploratory SS Cyg evidence | Results support a precise claim about persistence, heterogeneity or observation effects | Report uncertainty or negative evidence honestly; an imprecise null is not proof that outburst memory is absent |

The first expansion sprint should end with the Stage 2 prototype and a short Stage 3–4 design document, not a polished 30-page manuscript or a broad data harvest. Runtime, annotation effort and data-access costs should be estimated after that prototype rather than invented now.

### 7.5 What would count as a substantially stronger paper?

Three outcomes could be consequential:

- **A reproducible cross-system mark increment** survives credible observation treatment and evolving timing baselines, with a clear account of where it transfers.
- **A substantial fraction of apparent mark predictability is observational**, demonstrated by forward modelling and supported by real-boundary comparisons. That would change how historical recurrence correlations are interpreted, even without a positive physical-memory finding.
- **Predictability is conditional on activity regime**, established with enough precision and a defensible regime definition to guide future physical modelling or observing strategy.

Merely adding more algorithms, more post-hoc significance tests or a larger undifferentiated star sample would not achieve those outcomes. A telescope-utility experiment is an optional final component if the predicted differences are large enough to motivate a specified decision; it should not displace the observation/state question.

My preferred expanded paper would combine **A, B and a modest C** around one scientific argument. It could interest specialists through recurrence physics and a wider natural-science audience through a demonstrated observation-and-state identification problem. Broader relevance should follow from the completed evidence, not be asserted in advance.

## 8. Checks actually performed, and the limits of verification

The package's checks are deliberately separate from the frozen analysis. They write their own outputs and make no archive requests. Their README gives dependencies, input provenance, commands and limitations.

| Item checked | What was done and found | What this does not establish |
|---|---|---|
| **Version identity** | Selected public files were pinned to the reviewed commit and checked against Git blob identities; manuscript PDF/text SHA-256 values are in the manifest | An exhaustive review of every repository file or certification of private inputs |
| **Reader-first assessment** | Article and supplement read before internal reports; initial notes recorded; brief separately assessed. Selected article text/figure pages and both brief pages visually inspected | A claim that every PDF page received a separate pixel-level audit |
| **Primary aggregation** | Independently recomputed the 441-forecast weighted mean, CR1 SE, t9 interval, geometric ratio and leave-one-block-out means from public block counts/means | Independent extraction of the 435 interval outcomes, six censoring outcomes or individual real scores |
| **Longer grouping diagnostic** | Combined adjacent groups once; 90% t4 interval remains positive | A prespecified result, proof of group independence or protection against arbitrary long dependence |
| **Landmark scoring** | Twelve synthetic interval/survival calculations agree with independent probability formulas to $4.44\times10^{-16}$ | Correctness of the real observation model or full propagation of endpoint uncertainty |
| **Fallbacks/nesting** | Four synthetic missing-input/zero-coefficient cases give exactly zero paired contrast | Independent confirmation of every real routing count |
| **Endpoint counterexample** | Independent finite-state enumeration and fixed-baseline fit reproduce a positive gain with constant true duration | The magnitude of endpoint-induced gain in SS Cyg |
| **Censor cutoff branch** | Sixteen injected-evidence calls demonstrate the shared production/reference classification | Empirical occurrence or influence among the six real censors |
| **Existing tests** | Ran 52 selected tests covering native parsing, sealed evaluation, prefix/reference extraction, X4, calibration and OC statistics; all passed | Scientific validity, a comprehensive test suite run, or a full astronomical replication |
| **Parser amendment** | Inspected exact diff, compared failed/completed source inventories, checked unchanged protocol/parameter identities and synthetic invariance | A forensic guarantee about unrecorded human/agent access or a fresh raw-data reproduction |
| **Operating-characteristic screen** | Read the selected simulation/statistics paths and committed per-case counts, coverage and stream structure | A rerun of the full simulation experiment or nominal error-rate certification |
| **Literature** | Checked original accessible sources and recorded abstract-only/inaccessible cases below | An exhaustive multilingual ADS search, or original-page verification of CM92/Cannizzo 1993 |

The selected existing-test command was run from the staged source with its test fixtures available:

    PYTHONPATH=src:tests python -m unittest test_evaluation_native test_sealed_evaluation test_prefix_features test_prefix_reference test_extract_x4 test_forecast_calibration test_oc_statistics -q

The log and the repair-inventory comparison are included as review records. All larger real-data pipelines, live archive retrieval, and any material from the reserved period were outside this review. No frozen fit was altered. The claim ledger and interpretation specification were used to locate intended meanings, not treated as proof that those meanings were justified.

## 9. Literature and source-access record

This was a targeted search of close historical/forecasting precedents and the statistical assumptions most consequential to the manuscript. “Original read” means relevant original sections were inspected; an accessible link alone is not counted as reading. Bibliographic identity is not verification of a paper's detailed empirical claims. The source table supplies exact identifiers where verified and avoids inventing missing metadata.

| Source | Identifier and primary link | Access and use in this review |
|---|---|---|
| **Seetha et al. (1985), High Speed Photometry of SS Cygni after an Outburst** | **IBVS No. 2839**; [publisher text](https://ibvs.konkoly.hu/pub/ibvs/2801/2839.txt), [original PDF](https://ibvs.konkoly.hu/pub/ibvs/2801/2839.pdf) | Publisher text read and original first page inspected. Operational timing precedent. The cited IAUC 3945 and 3971 originals were not read. |
| **Grigorievskiy et al. (2014), Forecasting the Outbursts of the Photometry Light Curve of Star V363 Lyr** | [Author/institution-hosted original](https://research.cs.aalto.fi/aml/Publications/Publication216.pdf), ITISE proceedings, pp. 520–531 | Original read, especially §§4–6. Formal point-forecast precedent. No DOI verified; inconsistent proceedings-volume/ISBN listings should be resolved before final bibliography production. |
| **Price et al. (2007), SS Cygni Outburst Predictors and Long Term Quasi-periodic Behavior** | DOI **10.1086/524413**; arXiv **0710.2937**; [original preprint](https://arxiv.org/pdf/0710.2937) | Original methods/results read. Short-term precursor null and historical changing-activity context. |
| **Ak, Özkan & Mattei (2002), Statistical analysis of the long-term visual light curve parameters of dwarf novae** | DOI **10.1051/0004-6361:20020600**; [original institutional PDF](https://nek.istanbul.edu.tr/ekos/MAKALE/M7229.pdf) | Original definitions and relevant discussion read. Distinguishes duration, quiescence and cycle; it is not new independent validation of this forecast comparison. |
| **Bath & van Paradijs (1983), Outburst period–energy relations in cataclysmic novae** | DOI **10.1038/305033a0**; [publisher](https://www.nature.com/articles/305033a0) | Publisher abstract checked in the literature review; full text unavailable and final publisher reopen failed. Historical association context only. |
| **Hempelmann & Kurths (1990), Dynamics of the outburst series of SS Cygni** | Bibcode **1990A&A...232..356H**; [author bibliography](https://www.pik-potsdam.de/members/kurths/publikationen/fruehere), [author-posted abstract](https://www.researchgate.net/publication/234184992_Dynamics_of_the_outburst_series_of_SS_Cygni) | Abstract/bibliography inspected, original unread. Specific symbolic-width construction requires an original-page check. |
| **Cannizzo & Mattei (1992), On the long-term behavior of SS Cygni** | DOI **10.1086/172092**; bibcode **1992ApJ...401..642C**; [DOI](https://doi.org/10.1086/172092) | Identity verified; original Table 4 and figure conventions inaccessible through attempted routes. Exact quoted correlations are not independently certified here. |
| **Cannizzo (1993), The Accretion Disk Limit Cycle Model: Toward an Understanding of the Long-Term Behavior of SS Cygni** | DOI **10.1086/173486**; bibcode **1993ApJ...419..318C**; [DOI](https://doi.org/10.1086/173486) | Bibliographic/abstract leads checked; original detailed model pages unread. The repository's physical-source check is an assertion of prior verification, not this review's verification. |
| **Gneiting & Raftery (2007), Strictly Proper Scoring Rules, Prediction, and Estimation** | DOI **10.1198/016214506000001437**; [author PDF](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) | Original definition/introduction consulted. Propriety concerns a specified predictive target and observation, not any statistic containing a log probability. |
| **Heitjan & Rubin (1991), Ignorability and Coarse Data** | DOI **10.1214/aos/1176348396**; [publisher](https://projecteuclid.org/journals/annals-of-statistics/volume-19/issue-4/Ignorability-and-Coarse-Data/10.1214/aos/1176348396.full), [original scan](https://people.csail.mit.edu/jrennie/trg/papers/heitjan-ignorability-91.pdf) | Original abstract/metadata checked; full scan not read successfully. Cited for the coarsening framework; E1's example and application are the review's mathematical reasoning. |
| **Ibragimov & Müller (2010), t-Statistic Based Correlation and Heterogeneity Robust Inference** | DOI **10.1198/jbes.2009.08046**; [author PDF](https://www.princeton.edu/~umueller/tstat.pdf) | Original relevant theory read, including Theorem 1. Supports a qualified small-group argument, not automatic validity of the manuscript's exact CR1 statistic. |
| **Cameron & Miller (2015), A Practitioner's Guide to Cluster-Robust Inference** | DOI **10.3368/jhr.50.2.317**; [author's July 2014 manuscript](https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2014_July_09.pdf) | Original author's manuscript, especially few-cluster section, consulted. Relevant to the independence/finite-group qualifications. |
| **Diebold & Mariano (1995), Comparing Predictive Accuracy** | DOI **10.1080/07350015.1995.10524599**; [DOI](https://doi.org/10.1080/07350015.1995.10524599) | Publisher abstract checked by the literature reviewer; full original not audited. Context for dependence in forecast-loss differences, not a prescribed replacement test. |
| **AAS author guidance on AI/LLMs** | [Official policy](https://journals.aas.org/author-llm-guidelines) | Current primary policy read on 9 November 2026. Used only for the concrete byline/disclosure issue. |
| **Coppejans et al. (2016), Statistical properties of dwarf novae-type cataclysmic variables: the outburst catalogue** | DOI **10.1093/mnras/stv2921**; arXiv **1512.03821**; [original preprint](https://arxiv.org/pdf/1512.03821) | Original methods and selection discussion read. Population/selection context for §7; no underlying survey archive or catalogue export acquired. |
| **Otulakowska-Hypka, Olech & Patterson (2016), Statistical analysis of properties of dwarf novae outbursts** | DOI **10.1093/mnras/stw1120**; arXiv **1605.02937**; [original preprint](https://arxiv.org/pdf/1605.02937) | Original event definitions and measurement approach read. The preprint is v1 from May 2016 despite a later typesetting date. No linked archive accessed. |
| **Hameury, Menou, Dubus, Lasota & Huré (1998), Accretion disc outbursts: a new version of an old model** | DOI **10.1111/j.1365-8711.1998.01773.x**; arXiv **astro-ph/9803242**; [original preprint](https://arxiv.org/pdf/astro-ph/9803242) | Original model discussion and abstract consulted for the proposed physical extension; no assertion that an implementation was obtained or validated. |
| **Hameury (2020), A review of the disc instability model for dwarf novae, soft X-ray transients and related objects** | DOI **10.1016/j.asr.2019.10.022**; arXiv **1910.01852**; [review](https://arxiv.org/pdf/1910.01852) | Abstract/introduction consulted for theoretical context only. No recent observational record used; substantive model-method advice above rests on the original model paper. |

The plain-text file **new-reference-identifiers.txt** lists identifiers for the newly proposed methodological/operational references and the relevant policy. Existing manuscript/background references also appear above because their interpretation was checked. No third-party full text is distributed in this package.

## 10. Ordered revision brief for Claude and Codex

1. **Codex: resolve the six-case censor question first.** Recover candidate bounds from the retained 1960–2017 extraction; report censor reason, bracket/cutoff relation and original paired-score contribution. Preserve the frozen result. If affected cases exist, specify and run one justified, separately versioned correction/sensitivity. Deliver a short factual audit with no new archive access.
2. **Claude and Codex: agree the observation/score contract.** Define the latent or extracted target, bracket construction, point-end primary, censor meaning and exact score. Choose the bounded working-score interpretation or supply the missing observation-model justification. Update the claims ledger and interpretation specification before prose. Deliver a one-page derivation and explicit list of changed claims.
3. **Codex: prototype the paired truth-target diagnostic.** Use a declared small synthetic set with retained/regenerated full truth and matched landmarks. Distinguish bracket scoring from endpoint-origin information; fit oracle variants on their own synthetic training data. Report precision and failures as well as mean contrasts. This is exploratory and cannot refresh confirmation on the inspected real record.
4. **Claude: prepare the expanded-study design in §7.** Give one central question, an interpretable state/mark model ladder, candidate cohort criteria, exposure boundaries, source support and a realistic work estimate informed by the prototype. Do not acquire new records or open the reserved period as part of this response to review. Identify what would discriminate hypotheses and what would remain unidentifiable.
5. **Jointly: strengthen the methods evidence already available.** Add the compact qualification and per-case simulation tables; state uncertainty assumptions; incorporate the existing longer-block review diagnostic only as exploratory. Decide whether the single level-adapting comparator answers a remaining question. Do not start an open-ended model/sensitivity sweep.
6. **Claude: revise the scientific narrative and brief.** Use §§4–6 for claim hierarchy, historical exposure, prior forecasting context, effect interpretation and figure moves. Keep exploratory class refits subordinate. Correct byline metadata for the selected publication route. Preserve the full execution/correction history in the repository.
7. **Codex, then Claude: verify the revised claim-to-evidence mapping.** Check every changed numeric and interpretive statement, including figure captions and brief; distinguish working score, calibration, physical information and utility. Record which review items are resolved, narrowed or deferred, with a reason and a link to evidence.

The agents should return **a corrected core manuscript plus a short expansion design and response matrix**, not merely a stylistic revision. If the observation prototype exposes a material problem, that finding takes precedence over polishing the existing abstract. All analyses added after inspection remain exploratory. The original primary result, protocol, failed execution and parser amendment remain intact and identifiable.

## 11. Decisions for Barry, and readiness for your focused read

Your preference for impact already supports developing the integrated study; the agents do not need to ask again whether minor copy-editing is sufficient. They can complete E1–E3, the bounded prototype and the design document without asking you to adjudicate technical wording.

Two consequential scientific judgments may then deserve your attention:

1. **How far should the enlarged paper pursue physical interpretation?** My recommendation is a rigorous observation-aware predictability study with a modest multi-system extension, supported by specialist input on the physical hypotheses. A claim to distinguish causal disc mechanisms should be a further commitment only if the prototype shows identifiable predictions.
2. **Is the proposed cohort/precision trade-off scientifically worth the resources?** Ask the agents for concrete inclusion criteria, expected analysable information from authorised prior knowledge, and simulation-based precision estimates. Decide this from the design, not from a list of attractive stars or an evaluation-period significance target. No reserved-period counts are needed.

**Before your focused read:** require the six-case audit; a corrected and self-contained score/observation definition; a consistent narrowed claim; the paired synthetic prototype or a precise explanation of its remaining input requirements; and a short, staged expansion proposal. The manuscript should then present the science in the revised hierarchy, with the two-page brief understandable on its own.

**Final recommendation:** retain and develop the work. The existing frozen comparison is a credible starting point for a more consequential study, subject to the specified observation/censoring resolutions. Do not make rapid publication of the current incremental framing the objective. Build the next round around distinguishing measurement information, changing state and reproducible mark information, while preserving the historical record and keeping the 2018-onward archive closed.
