# Preliminary literature review: recurrence, memory, and changing states in dwarf novae

**Research cut-off and inspection date:** 5 November 2026. **Status:** a targeted seed review, not a systematic review or a claim of priority. No new astronomical measurements or fitted results are reported here.

The bibliography contains 25 astronomy sources and five methodological sources. The [evidence register](../references/evidence.csv) records the original source, what was actually inspected, the claim it supports, and remaining checks. The [search log](../references/search-log.md) records search scope and access gaps. `Full-text sections` means that relevant sections were inspected; it does not mean every calculation was independently audited. Two important historical articles are presently bibliography-only leads. Recent work with uncertain edition metadata is explicitly marked.

## 1. The question needs to be narrower than “do dwarf novae have memory?”

There is a substantial historical literature on the relation between outburst properties, adjacent waiting intervals, and longer changes in activity. Bath and van Paradijs associated the optical outburst energy of SS Cyg with its **following** quiescent interval; van der Woerd and van Paradijs examined the **preceding** interval and supercycle position in VW Hyi. Hempelmann and Kurths explicitly discussed short and long memory in the SS Cyg outburst sequence in 1990. A project whose novelty is simply finding serial correlation would therefore be poorly positioned. [@BathVanParadijs1983; @VanDerWoerdVanParadijs1987; @HempelmannKurths1990]

The more useful proposed question is:

> **Among adequately observed ordinary outbursts of hydrogen-rich dwarf novae, does information from completed previous outbursts improve calibrated predictions of the next outburst beyond elapsed time, each star’s baseline behaviour, slowly changing activity, and the observation process?**

This wording is a proposed research design, not a conclusion from the literature. It separates a tractable empirical objective from the more difficult physical interpretation. A positive result could constrain models of evolving disc conditions; it would not by itself establish that a particular outburst causally changed the next one.

Four distinct ideas should remain separate throughout the project:

| Meaning of “memory” | Operational question | What a positive result establishes |
|---|---|---|
| Renewal age | Does the event probability depend on time since the last event? | A nonconstant waiting-time hazard; this need not imply additional historical information. |
| Predictive history | Do earlier intervals, durations, or passband fluences improve future predictions after baseline conditioning? | Incremental predictive information under the stated information set and observation model. |
| Persistent activity state | Does an evolving common state explain several successive events? | Evidence for persistence or nonstationarity; apparent event-to-event dependence can be mediated by that state. |
| Physical or dynamical memory | Does retained disc structure, donor variability, or deterministic dynamics cause the dependence? | Requires stronger physical modelling, discriminating observables, and competing explanations. |

The distinction between ordinary dwarf-nova disc outbursts and thermonuclear classical/recurrent novae is essential. Forecasts for T CrB or RS Oph do not answer this project’s question. Subclasses within dwarf novae also need separate treatment: supercycles, standstills, and related phenomena already supply physically meaningful structure. [@Hameury2020]

## 2. What the existing literature already covers

### 2.1 Within-star relations and historical event sequences

Early SS Cyg and VW Hyi studies establish that the direction of the adjacent interval matters. A preceding interval tests a different association from a following interval. Neither is automatically an operational forecast: a useful prediction must be made at a specified time using only quantities already available then. [@BathVanParadijs1983; @VanDerWoerdVanParadijs1987]

Hempelmann and Kurths reported dependence over several successive SS Cyg outbursts and longer changes on roughly ten-cycle scales. Their original analysis must be read in full before making detailed comparisons: this seed review inspected an author-posted abstract and verified bibliographic metadata, not the complete statistical procedure. The claim establishes an important novelty constraint even without treating its interpretation as settled. Cannizzo and Mattei’s 1992 and 1998 SS Cyg papers are additional mandatory full-text retrieval tasks. [@HempelmannKurths1990; @CannizzoMattei1992; @CannizzoMattei1998]

Standardized multiobject light-curve work is also longstanding. Szkody and Mattei studied 21 dwarf novae; Ak and colleagues analysed long-term parameters for 36. Thus, adding multiple stars is useful for generalization but is not sufficient novelty. Ak and colleagues make a particularly relevant warning: recurrence intervals that contain the outburst duration can produce a mathematical correlation with that duration. [@SzkodyMattei1984; @Ak2002]

For proposed event boundaries, write

\[
D_i=t_i^{\rm off}-t_i^{\rm on},\qquad
G_i=t_{i+1}^{\rm on}-t_i^{\rm off},\qquad
R_i=t_{i+1}^{\rm on}-t_i^{\rm on}=D_i+G_i.
\]

Here, \(D_i\) is event duration, \(G_i\) the following quiescent gap, and \(R_i\) the onset-to-onset interval. Because \(D_i\) is a component of \(R_i\), their correlation is not a clean test of a reservoir hypothesis. This is an algebraic issue even before measurement errors, missed events, or astrophysical effects enter. Store all three quantities with boundary uncertainty rather than using an ambiguous “recurrence time.”

### 2.2 Population catalogues answer a different question

Coppejans and colleagues’ catalogue describes 722 dwarf novae using CRTS light curves, while Otulakowska-Hypka and colleagues compile and examine a different set of outburst/system properties. These are distinct catalogues, not alternate names for one dataset. Their between-system relations are useful for target selection and prior plausibility, but do not establish within-system predictive memory. [@Coppejans2016; @OtulakowskaHypka2016]

The Coppejans recurrence statistic is an upper-limit estimate constrained by incomplete sampling, including the minimum observed spacing of identified outbursts. Sparse cadence, limiting depth, saturation, and selection affect the catalogue. Treating that field as a complete sequence of exact physical waiting times would be a serious misuse. Event-level analysis needs original measurements and an explicit coverage audit. [@Coppejans2016]

### 2.3 Known supercycle and state structure

Kepler observations of V1504 Cyg and V344 Lyr reveal systematic changes in normal-outburst properties through supercycles. Osaki and Kato relate activity changes to negative superhumps and tilted-disc behaviour in V1504 Cyg. These results provide useful positive controls for event extraction, but also explain why a single pooled model across ordinary U Gem and SU UMa behaviour is hard to interpret. [@Cannizzo2012; @OsakiKato2013]

Longer changes have also been studied directly. Active SU UMa supercycle evolution was examined in 2013; RU Peg’s changing outburst morphology and recurrence were investigated in 2022; later work examined quiescent brightness changes across dwarf novae. A changing-state model can be valuable, but discovering that such changes exist is not the likely contribution. [@OtulakowskaHypkaOlech2013; @Simon2022; @VogtVegaManubens2023]

Z Cam/IW And behaviour and the anomalous SS Cyg episode in 2021 further show that physical categories can contain complicated epochs. These should be labelled before predictive comparisons or designated as stress tests. Their removal only after a model performs badly would change the target of inference after seeing the outcome. [@Kato2019; @Kimura2021]

## 3. Physical context and limits of interpretation

The disc instability model provides the central physical framework: thermal and viscous behaviour associated with partial ionization produces transitions between cool and hot disc configurations. Standard implementations require choices about viscosity and may incorporate irradiation, truncation, changing mass supply, and other processes. Disc mass alone is therefore an intentionally incomplete state variable. [@Lasota2001; @Hameury2020]

A low-dimensional reservoir model can be a useful hypothesis generator: accumulated mass, imperfect depletion, and a varying input rate may all induce serial structure. However, several latent mechanisms can yield similar observed event sequences. Stochastic-viscosity modelling of Z Cam systems illustrates the importance and limits of fluctuations near instability boundaries, while two-dimensional simulations now follow complete normal/superoutburst cycles. The 2026 review by Scaringi and colleagues emphasizes unresolved accretion physics. These sources justify physical humility when interpreting a statistical state or history coefficient. [@RossLatter2017; @Jordan2024; @Scaringi2026]

Optical passband fluence is a useful observable, not a measured accreted mass or bolometric energy. Multicolour modelling includes contributions from the disc, white dwarf, hot spot, and irradiated donor, and shows colour–magnitude hysteresis. The project should therefore label its observable as a **relative passband fluence proxy**, preserve the filter and flux convention, and test sensitivity to the assumed quiescent baseline. [@HameuryHysteresis2020]

Predictive dependence should also remain separate from a claim of chaos. George and colleagues demonstrate that gaps and interpolation can materially alter correlation-dimension diagnostics. A low apparent dimension in an interpolated light curve is not sufficient evidence for deterministic dynamics. Conversely, failure of a chaos diagnostic would not establish absence of useful predictive history. [@George2015]

## 4. Closest precedents and a provisional gap matrix

The rightmost column is a proposed contribution, not a verified unoccupied niche. A structured citation search is required before using “first,” “novel,” or “previously unexplored.”

| Candidate claim | Existing precedent | What remains worth testing |
|---|---|---|
| Burst strength relates to an adjacent waiting interval | SS Cyg and VW Hyi studies in the 1980s [@BathVanParadijs1983; @VanDerWoerdVanParadijs1987] | Reproducibility with explicit event boundaries, band conventions, and uncertainty; direction-specific predictive tests. |
| Dwarf novae exhibit memory | Explicit SS Cyg dynamics study [@HempelmannKurths1990] | Whether history improves calibrated future predictions after nonstationary and observation-aware baselines. |
| Several objects share outburst-property relations | Standardized 21- and 36-object studies; later catalogues [@SzkodyMattei1984; @Ak2002; @Coppejans2016; @OtulakowskaHypka2016] | Within-star effects, between-star heterogeneity, and transfer to held-out stars without pooling these estimands. |
| Successive events change through a supercycle | Kepler and superhump work [@Cannizzo2012; @OsakiKato2013] | Positive-control recovery and incremental effects after conditioning on phase; a separate SU UMa study. |
| Activity occupies persistent regimes | RU Peg, IW And, SS Cyg’s 2021 anomaly [@Simon2022; @Kato2019; @Kimura2021] | Reproducible state definitions, useful prospective predictions, and sensitivity to gaps. |
| Long cycles imply changing donor activity | Quiescent-brightness and ER UMa studies [@VogtVegaManubens2023; @Medagangoda2026] | Red-noise, observing-window, and calibration alternatives; competing physical explanations. |
| Nonlinear signatures offer precursors | Earlier dynamics; recent fractal analysis [@HempelmannKurths1990; @George2015; @Tsuranova2026] | Leakage-free precursor definitions and held-out forecast value beyond strong simple baselines. |
| An inferred state identifies disc physics | DIM extensions and multidimensional modelling [@Hameury2020; @Jordan2024; @Scaringi2026] | Identifiability studies and observables that distinguish retained disc structure from variable input. |

Recent literature matters. The 2026 ER UMa supercycle and TESS fractal studies are relevant precedents; neither is adopted here as an independently replicated causal or forecasting result. [@Medagangoda2026; @Tsuranova2026]

## 5. Annotated reading list

Evidence IDs map directly to rows in `references/evidence.csv`. These annotations deliberately distinguish reported results from project decisions.

### Physical foundations

- **E01 — Lasota (2001)** [@Lasota2001]. Foundational DIM review. Read for the disc equations, stability picture, and historical shortcomings before assigning physical meaning to any reservoir parameter. **Inspected:** abstract and bibliographic record; full review remains a reading task.
- **E02 — Hameury (2020)** [@Hameury2020]. Modern review of the basic model and extensions. Particularly useful for defining subclasses and possible latent variables. **Inspected:** relevant full-text sections. Its discussion supports multiple mechanisms, not a uniquely identified mechanism for any future observed correlation.
- **E17 — Ross and Latter (2017)** [@RossLatter2017]. Explores stochastic viscosity near Z Cam instability boundaries. Useful as a concrete competing mechanism for variability and as a warning that reproducing some transitions need not reproduce the entire observed pattern. **Inspected:** indexed primary full-text sections.
- **E19 — Hameury et al. (2020)** [@HameuryHysteresis2020]. Models colour–magnitude hysteresis for SS Cyg and VW Hyi. Read when deciding which observables can plausibly represent disc state or outburst output. **Inspected:** primary abstract and indexed article sections.
- **E23 — Jordan et al. (2024)** [@Jordan2024]. Two-dimensional simulations of outburst cycles vary physical conditions and follow normal and superoutburst behaviour. A useful later-stage bridge from empirical sequence statistics to physical model predictions. **Inspected:** relevant full-text sections.
- **E24 — Scaringi et al. (2026)** [@Scaringi2026]. Current review organized around unresolved problems in accreting white dwarfs. Useful for positioning a modest empirical constraint without suggesting the remaining physics reduces to one fitted coefficient. **Inspected:** relevant full-text sections.

### Historical correlations and reproducibility targets

- **E03 — Bath and van Paradijs (1983)** [@BathVanParadijs1983]. SS Cyg association with the following quiescent interval is a direct precedent. Its historical interpretation should not be treated as a contemporary verdict against developed DIM models. **Inspected:** publisher abstract; full methods required before reproduction.
- **E04 — Szkody and Mattei (1984)** [@SzkodyMattei1984]. Comparable measurements across 21 systems demonstrate that multiobject outburst analysis already has deep roots. Its treatment of incomplete events and gaps is relevant to extraction choices. **Inspected:** original scanned paper sections.
- **E05 — van der Woerd and van Paradijs (1987)** [@VanDerWoerdVanParadijs1987]. VW Hyi analysis distinguishes the preceding interval and supercycle position. Useful for avoiding an undirected “fluence–recurrence correlation.” **Inspected:** publisher abstract.
- **E06 — Hempelmann and Kurths (1990)** [@HempelmannKurths1990]. The most direct historical use of the project’s memory concept. Retrieve the complete original before judging its null models, uncertainty treatment, or causal interpretation. **Inspected:** author-posted abstract plus an author-institution bibliography.
- **E07 and E08 — Cannizzo and Mattei (1992, 1998)** [@CannizzoMattei1992; @CannizzoMattei1998]. Essential SS Cyg history and event-shape references. **Inspected:** bibliographic metadata only. No numerical result from these papers is adopted in this seed. Their priority in the reading queue reflects relevance, not a completed assessment.
- **E09 — Ak et al. (2002)** [@Ak2002]. Long-term parameters across 36 dwarf novae, with an explicit warning about shared terms in interval correlations. Make its event definitions and that warning a starting point for the extraction specification. **Inspected:** original institutional PDF sections.

### Supercycles, catalogues, and observation effects

- **E10 — Cannizzo et al. (2012)** [@Cannizzo2012]. Kepler event sequences provide a positive control for known within-supercycle changes. **Inspected:** final arXiv record and relevant full text. An earlier NASA-hosted draft has a shorter observing baseline; do not silently mix its counts with the later paper.
- **E11 — Osaki and Kato (2013)** [@OsakiKato2013]. Connects negative-superhump behaviour with normal-outburst activity. Treat tilt and supercycle variables as scientifically motivated alternatives to generic history features. The paper’s strong title is not evidence that every superoutburst mechanism is settled. **Inspected:** abstract.
- **E12 — Otulakowska-Hypka and Olech (2013)** [@OtulakowskaHypkaOlech2013]. Direct precedent for changing supercycle lengths in very active SU UMa systems. The inferred secular change in mass transfer is a model-based interpretation. **Inspected:** publisher abstract and metadata.
- **E13 — Coppejans et al. (2016)** [@Coppejans2016]. Important catalogue for target reconnaissance, with explicit cadence and selection limitations. Use original light curves for the project’s event inference. **Inspected:** relevant full-text sections and catalogue metadata.
- **E14 — Otulakowska-Hypka et al. (2016)** [@OtulakowskaHypka2016]. A separate compilation examining relations among outburst and system properties. Useful context for population associations and for checking whether proposed cross-star relationships are already known. **Inspected:** abstract and selected indexed conclusions.
- **E15 — George et al. (2015)** [@George2015]. Demonstrates sensitivity of nonlinear diagnostics to missing data and interpolation. Use cadence-matched simulations when considering any complexity statistic. **Inspected:** original arXiv PDF sections.

### Persistent and changing activity

- **E16 — Kato (2019)** [@Kato2019]. Observations of IW And-type behaviour provide explicit examples of structured standstill/brightening/dip patterns. Such systems are valuable later comparisons but would complicate an initial ordinary-outburst sample. **Inspected:** full-text sections.
- **E18 — Kimura et al. (2021)** [@Kimura2021]. Multiwavelength examination of SS Cyg’s anomalous 2021 activity. It supplies a pre-existing reason to flag this epoch and examine forecast failure under change. **Inspected:** arXiv abstract and journal metadata.
- **E20 — Šimon (2022)** [@Simon2022]. RU Peg’s morphology, recurrence and activity changes are close to the intended project. Its explicit discussion of possible missed outbursts is especially useful. Reproduce descriptive relations before adding a predictive model. **Inspected:** relevant full-text sections.
- **E21 — Vogt and Vega-Manubens (2023)** [@VogtVegaManubens2023]. Studies long-term changes in quiescent brightness. The work motivates testing quiescent level as an observable and treating calibration changes as an alternative. A selected variable subset is not a prevalence estimate for all dwarf novae. **Inspected:** publisher abstract and indexed sections.
- **E22 — Medagangoda et al. (2026)** [@Medagangoda2026]. Supercycle timing in four ER UMa systems is used to argue for magnetic modulation. Compare its timing analysis with alternative slowly varying stochastic models before borrowing the physical interpretation. **Inspected:** publisher abstract and metadata.
- **E25 — Tsuranova et al. (2026)** [@Tsuranova2026]. Moving multifractal analysis of TESS YZ Cnc data suggests a pre-superoutburst signature. This concerns a high-cadence precursor in an SU UMa system, distinct from predicting ordinary recurrence from completed events. **Inspected:** English abstract; full Russian text requires subscription. Lead time, causal window placement, event counts, independent validation, and forecast skill remain unknown. Edition metadata also needs checking.

### Statistical tools, not astronomical evidence

- **M01 — Gneiting and Raftery (2007)** [@GneitingRaftery2007] provides proper scoring-rule foundations for probabilistic forecasts.
- **M02 — Bürkner et al. (2020)** [@Buerkner2020] develops leave-future-out comparison for Bayesian time series. The principle is relevant; its approximation is not automatically valid for every proposed event/state model.
- **M03 — Graf et al. (1999)** [@Graf1999] treats performance evaluation with censored survival data. Verify the censoring assumptions before adopting an estimator for astronomy gaps.
- **M04 — Turnbull (1976)** [@Turnbull1976] is a foundational reference for grouped, censored, and truncated observations. Event-boundary intervals and wholly missed events are different problems; a citation does not solve the latter.
- **M05 — Talts et al. (2018)** [@Talts2018] supplies simulation-based calibration for checking inference algorithms under the generative model. It does not establish that the generative model describes the real stars.

These five methodological records were verified in the parallel methods review; the evidence register identifies the handoff. They support the proposed workflow, not a claim that dwarf-nova forecast validation has already used it.

## 6. Consequences for the initial project

The following are design recommendations inferred from the literature, to be finalized in the analysis protocol before inspection of held-out outcomes.

1. **Start with one interpretable class.** Pilot ordinary outbursts in well-observed hydrogen-rich U Gem/SS Cyg systems. Treat RU Peg as a relevant comparison. Defer SU UMa supercycles and Z Cam/IW And states to separate strata or explicitly designed extensions; do not label the entire population homogeneous.
2. **Audit observations before selecting on scientific behaviour.** Predeclare coverage and event-visibility criteria. A nightly non-detection, a shallow upper limit, and no observation convey different information. Include both false splits and missed outbursts in extraction sensitivity checks.
3. **Specify the prediction landmark.** A forecast made after an outburst ends can use that completed event’s duration and fluence. A forecast made at its onset cannot. Filtered state estimates at the forecast time must not borrow future observations through retrospective smoothing.
4. **Separate associations from forecast tests.** Reproduce historical descriptive comparisons, then assess incremental forecast information on later contiguous time blocks. Report calibration and proper scores alongside scientifically interpretable effect sizes, not just a correlation or a significance threshold.
5. **Use several credible nulls.** Compare against elapsed-time/renewal, slow drift, and persistent-state alternatives. A complex history model beating a stationary exponential wait alone would be weak evidence about the physical source of dependence.
6. **Make a null result useful.** Quantify which effect sizes remain compatible with sampling, event uncertainty, and the number of independent cycles. Failure to improve forecasts is a bound on usefulness under this design, not proof that an accretion disc has no physical memory.

### Initial reproduction ladder

| Stage | Concrete task | What it establishes |
|---|---|---|
| Definition audit | Reconstruct Ak et al.’s distinction between cycle length and adjacent quiescent interval; simulate shared-term correlation. | The project’s central statistic is not produced by its own definitions. |
| Historical anchor | Obtain the 1990, 1992, and 1998 SS Cyg papers; implement one clearly specified published descriptive analysis. | The team understands the closest old baseline and can explain differences in event construction. |
| State-change anchor | Reproduce a selected RU Peg relation, including plausible missed-event alternatives. | Apparent state persistence is robust enough to warrant modelling. |
| Positive control | Recover a declared within-supercycle pattern from a suitable Kepler interval, kept separate from the ordinary-outburst sample. | Extraction can recover a known form of temporal structure. |
| New inference | Freeze eligibility, landmarks, baselines, and future blocks; evaluate the extra value of history. | A defensible answer to the sharpened research question. |

## 7. What remains unresolved in this seed review

The next research pass should obtain the complete historical SS Cyg papers, follow their forward and backward citations in ADS, and check JAAVSO and other observer publications. It should assess recent precursor claims for their forecast landmarks, smoothing, event selection, and independent validation. Exact sample overlap among catalogues and the project’s eventual targets also needs checking. The original-language/translated-edition metadata for the 2026 fractal paper must be resolved before manuscript submission.

No search here establishes an absence of prior observation-aware or out-of-time prediction work. The defensible current position is: **the broad phenomenology is well studied; a careful, reproducible assessment of conditional predictive information is a promising candidate project whose precise novelty still needs a targeted citation audit.**
