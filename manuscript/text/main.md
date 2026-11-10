# Does outburst duration improve recurrence forecasts? A preregistered SS Cygni test and its measurement limits

**Second draft for review, 10 November 2026. Release and submission remain Barry W. Brook's decisions.**
<div id="authors"></div>

## Abstract

Does the duration of a completed dwarf-nova outburst improve forecasts of the next onset beyond
recent recurrence history? We tested this for SS Cygni using archived visual observations, an
outburst extractor and lognormal forecast clocks fitted on 1910–1959. After freezing the models
and publishing the protocol, we opened 1960–2017. Adding duration raised the specified working
interval score by [0.0165]{.C01 .V001} nats per issuance (90% cluster interval
[0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}; [441]{.C01 .V004} issuances), meeting the
predeclared criterion. The scored intervals are fitted extraction outputs, however, not known
bounds on physical onset; a proper latent-onset likelihood has not been established. The run
followed a documented post-access parser repair to an unused missing-uncertainty field[]{.C05}.
The original later-period and long/short-class comparisons were inconclusive[]{.C07}[]{.C08}.
Subsequent exploratory checks retained a positive point-score sensitivity, but redesigned
report-window and observed-clock comparisons were inconclusive[]{.C44}[]{.C55}. Post-result
rolling adjustments reduced an analogous point-clock gain from [0.0184]{.C62} to
[0.0132]{.C62} nats, showing sensitivity to baseline level and mark definition without measuring
a causal component of the original result. A prospectively frozen transfer screen then opened
only the pre-1990 visual records of [10]{.C68 .V030} catalogue-selected candidates. None qualified
for the planned multi-star test[]{.C68}; no duration effect was fitted for those stars. Simulations
also showed that a positive coefficient-score moment need not imply improvement by the trained
forecast[]{.C66}. The study establishes a reproducible working-score result for one extraction
and baseline, with unresolved observation-model assumptions and untested generality. It does
not identify physical memory or a disc mechanism.

## 1. Introduction

Dwarf-nova outbursts provide a long record of a repeating but irregular astrophysical process.
A white dwarf accretes from a companion through a disc; thermal instability associated with
hydrogen ionisation can switch the disc between cool and hot states
[@lasota2001DiscInstabilityModel; @hameury2020ReviewDiscInstability]. A completed outburst may
therefore reveal something about the state from which the next cycle begins. The observational
question is whether that information improves a forecast. Connecting an improvement to a
particular physical state requires more than a correlation between measured durations and gaps.

SS Cygni has a long visual record in the American Association of Variable Star Observers
(AAVSO) International Database. Bath and van Paradijs described a relation between outburst
energy and the following waiting period [@bath1983OutburstPeriodenergyRelations]. Cannizzo
and Mattei (CM92) analysed [705]{.C40} outbursts and showed why cycle definitions matter
[@cannizzo1992LongtermBehaviorSS]. An onset-to-onset cycle already contains the duration of
its first outburst. The cleaner duration–following-quiescence correlation was
[0.223]{.C40}; duration also correlated with the preceding quiescence. Successive durations
alternated, and a [12]{.C40}-day split separated long and short classes. CM92 interpreted
successive quiet-interval correlations as possible secular variation. These associations,
alternation and the class split are prior art, not discoveries of this study.

Hempelmann and Kurths (*Astronomy and Astrophysics*, 1990, 232, 356) examined dependence in
symbolic outburst-width sequences. Searches for low-dimensional chaos found no attractor
[@cannizzo1988ChaosSSCygni]. Cannizzo's disc calculations reproduced long/short alternation
and slow changes in recurrence [@cannizzo1993AccretionDiskLimit]. Those results do not supply
a held-out test of duration's contribution beyond a timing-history forecast. The closest
forecasting precedent located in our bounded search is Grigorievskiy and colleagues' 2014
ITISE study, which tested point-onset forecasts on one V363 Lyr outburst. A separate search
for short-term photometric precursors in SS Cyg found none [@price2007SSCygniOutburst].

A forecast comparison must specify the information available at issue, the competing baseline
and the observation being scored. Proper scoring rules evaluate whole predictive distributions
[@gneiting2007StrictlyProperScoring], and temporal evaluation must preserve training order
[@burkner2020ApproximateLeavefutureoutCrossvalidation]. Applying those principles to visual
outburst records is difficult: onset and end are inferred from noisy reports, observing can
respond to the star, and gaps can hide events. The statistical interval returned by an extractor
is not automatically an observed-data likelihood or a hard physical bound.

We report the original frozen comparison together with the research needed to establish what
it measures. To our knowledge, it is the first preregistered, frozen-parameter probabilistic
held-out evaluation of dwarf-nova recurrence forecasts, and the first held-out test of the
completed outburst's duration beyond a specified timing-history baseline[]{.C41}. That is an
account of a bounded literature search, not proof of universal priority. The original
calculation met its predeclared rule. Later review narrowed its interpretation to a working
interval score, motivated different clocks and report windows, and led to a failed multi-star
feasibility screen. Keeping those results together avoids presenting measurement stability,
a statistical decision and physical explanation as the same finding.

## 2. Evidence and design

### 2.1 Visual observations and extraction

The original analysis retained native Vis. observations with validation flag V. In the
1960–2017 evaluation interval, [249,356]{.C15} of [500,479]{.C15} deduplicated archive rows
met that selector. Development used the earlier record; raw observations and observer
identities are retained outside the public repository.

X4 extracts candidate outbursts at visual magnitude ten. It combines observer visits and fits
local rising and fading crossings, allowing a shared level-error term. Confirmation requires
bright evidence from distinct observers, or a qualifying single observer on separate nights.
The crossing summaries are model-based intervals and points. Their construction, plug-in
uncertainty and clipping do not establish a calibrated posterior or known containment of the
latent crossing. A magnitude-ten crossing would itself remain distinct from the onset of a
physical disc instability.

X4 passed a conditional synthetic recovery screen at this threshold and a seven-day coverage
rule. A waveform family unseen during extractor development failed benchmark qualification
before X4 recovery was scored; recovery on that family was not tested. Other threshold
diagnostics failed. Qualification therefore did not establish complete real-event recovery or
measurement validity across stars. The extraction and coverage choices define the comparison
(Supplement S2.1).

### 2.2 Issuance, models and the working score

An observation-time end confirmation issues a forecast. Its predictors use only the preceding
400 days of reports: the completed outburst's fitted duration, the previous covered quiet gap
and a recent mean of earlier covered log gaps. Future-row poisoning tests check this restriction.
Historical upload and revision dates are unknown, so the analysis is an observation-time
retrospective comparison, not an operational replay.

Each model is a lognormal quiet-gap clock conditioned on survival to the observed issue time.
M0 is constant. M2 adds standardised log previous gap and recent gap level. M3 adds standardised
log current duration with a nonnegative coefficient. M2 was fitted on 1910–1959; the duration
offset was then fitted with M2 fixed and all parameters frozen. Its fitted coefficient was
[0.0466]{.C04} per development standard deviation. Routes without the required history use the
same fallback in both arms and have exactly zero contrast.

The original working score assigns forecast probability to the next fitted X4 onset interval,
or survival probability to a censoring cutoff. It is conditional on the clock's survival to
issue. Coverage loss, supersession or record end can stop a forecast. These are calculations
on extractor-defined evidence. Calling their contrast a proper score for physical onset would
require a justified observation and selection model, which has not been supplied. Duration
and the following quiet gap also share an estimated end; their errors need not be independent.

### 2.3 Frozen test and access record

The single confirmatory statistic was the mean M3−M2 working-score gain over all eligible
evaluation issuances, including shared-fallback zeros. A small-sample-corrected cluster standard
error used consecutive six-year blocks and Student's t. The predeclared criterion was a positive
one-sided 95% lower bound. Era, type/within-type, calibration and robustness analyses were
secondary and could not replace that test.

The protocol DOI, 10.5281/zenodo.24053338, predates the first evaluation request. That attempt
failed before scoring because the archive returned literal None for missing uncertainty.
The independently reviewed repair accepted that exact token without changing or dropping a
row; no forecast uses that field. Rehearsal and invariance checks preceded continuation. The
failed attempt remains preserved. This was a completed evaluation after a post-access format
repair, not an untouched evaluation, and the DOI does not timestamp the repaired code[]{.C05}.

### 2.4 Reassessment and transfer

After the result, an external review reopened the observation model. R1 audited censoring,
rescored saved points and added endpoint errors to synthetic histories. R2b rebuilt outcomes
from decisive-report windows and compared a fitted-end clock with an observed clock anchored
to a decisive faint report. Its mark is the observed span of decisive brightness. This removes
a literal interpolated end from that clock, but not shared reports, cadence-dependent anchor
lag or selection. R2b also introduced windowed history baselines: B0 with recent-gap covariates,
B1 with discounted history, and a preselected B2 state-space model. They are distinct from the
original frozen M2.

All these SS Cyg analyses reuse opened data and are exploratory. Their specifications were
fixed before their own fits, but they cannot become another confirmation. Report association
and event completeness, physical containment or genuine censor survival, and a normalised
coarsening-at-random observation kernel are separate premises. A report margin or timely visit
does not prove them. Supplement S2.8 states the scoring consequences.

G3a was different: its rules were frozen before opening any of the candidate stars' records.
It asked whether the pre-1990 visual data of the catalogue nominees and eclipse holds could
support a later test. Qualification required supported timing-and-mark forecasts, eligible
windows, stable nondegenerate unmarked B0 fits and no operational morphology flag; the holds
also required an eclipse feasibility guard. It computed no duration–gap association or gain.
No candidate test-period data were opened.

**Table 1.** What the evidence directly supports.

| Input or comparison | Direct result | Further requirement for a stronger claim |
|---|---|---|
| Native visual reports and frozen X4 | Extracted episodes, crossing summaries and coverage decisions | Validated event association and observation model for physical onset |
| Frozen M2/M3 and original access record | A held-out working-score contrast after the documented repair | Proper latent-onset scoring and adequate uncertainty assumptions |
| Exploratory R1/R2b | Sensitivity to outcomes, clocks, baselines and level adjustment | A new independent test of a fully specified observation/forecast rule |
| R2d and six-star simulations | Operating characteristics within declared synthetic processes | Transfer to real extraction, calendar yield and supported star dependence |
| Frozen G3a early-record screen | Qualification failure under the stated rules | No effect-size inference: no candidate duration effect was fitted |

## 3. Results

### 3.1 Original working-score comparison

The predeclared criterion was met (Fig. 2): the mean working interval-score gain was
[0.0165]{.C01 .V001} nats over [441]{.C01 .V004} issuances, with 90% cluster interval
[0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}. This remains a result for the specified fitted
intervals, extraction and measured-history baseline; a proper physical-onset likelihood is
unestablished. Exponentiating gives a [1.7]{.C02}% increase in the geometric mean likelihood
assigned to the scored evidence. It is neither an accuracy percentage nor an arithmetic
probability gain. The original outcomes were [435]{.C03} fitted onset intervals and
[six]{.C03} censored cases. Timing models applied on [436]{.C03} issuances; [five]{.C03}
used the shared fallback. M2 itself gained [0.117]{.C10} nats over M0.

The original qualifications remain beside this result. The 1993–2017 segment gave
[0.0057]{.C07} nats ([−0.0107]{.C07} to [0.0221]{.C07}); the predeclared class-plus-within-class
rule gave [0.0025]{.C08} ([−0.0022]{.C08} to [0.0072]{.C08}). Both were inconclusive.
The earlier evaluation segment overlaps CM92's published association record, and no era-difference
test was specified. Positive robustness variants do not supply independent confirmations.

[Eight]{.C25} block means were positive, and leave-one-block-out means remained positive.
Those checks do not validate the dependence model. The sample's predictive intervals overcover
under the extraction-based coverage bounds; relative score gain does not establish calibrated
physical-onset or operational forecasts (Supplement Fig. S1)[]{.C11}. Figure 1 illustrates one
forecast selected by observation time, not score. Its model medians for remaining wait are
[27.57]{.C42} days for M2 and [26.77]{.C42} for M3; it is an example, not an average scheduling
benefit.

### 3.2 Measurement and clock sensitivities

The censoring audit found a coding rule requiring repair for future interval straddles, but the
repair changed [zero]{.C43} of the [441]{.C43} original outcomes. R1's saved-point density
sensitivity gained [0.0154]{.C44} nats ([0.0034]{.C44} to [0.0274]{.C44}). These points remain
uncertain extractions, not measured latent onset times. The proposed original report-interval
sensitivity was largely unavailable: [434]{.C45} associations lacked a finite lower clip.
Its tiny supported subset could neither reproduce nor overturn the full result.

A separate corrected report-window construction yielded [818]{.C47} available windows among
[845]{.C47} confirmed episodes, with [805]{.C47} eligible and median width [1.15]{.C47} days.
Availability did not prove physical containment. R2b then scored the preselected state-space
comparisons under those working-window rules (Fig. 3).

<!-- BEGIN GENERATED r2b -->
| Exploratory contrast | Scored issuances | Mean gain, nats | Six-year 90% interval |
|---|---:|---:|---|
| H1: fitted-end clock, B2 duration | [432]{.C55 .V012} | [0.0075]{.C55 .V009} | [−0.0008]{.C55 .V010} to [0.0159]{.C55 .V011} |
| H2: observed clock, B2 bright span | [431]{.C55 .V016} | [0.0043]{.C55 .V013} | [−0.0008]{.C55 .V014} to [0.0094]{.C55 .V015} |
| H3: observed-clock gain minus matched fitted-end gain | [431]{.C55 .V020} | [−0.0031]{.C55 .V017} | [−0.0078]{.C55 .V018} to [0.0017]{.C55 .V019} |
<!-- END GENERATED r2b -->

All intervals cross zero under six- and twelve-year blocking[]{.C55}. There is no clear paired
evidence that incremental gains differ between clocks. H3 is not an estimate of the causal
contribution of end-time error. The delayed-clock population also differs from the original
one: one coincident issue is represented once, and unsupported outcomes are excluded rather
than assigned zero gain. The smaller estimates therefore cannot be read as a fraction of the
original result surviving measurement correction.

In R1's separate endpoint experiment, added independent Gaussian end errors produced no positive
mean gain across the tested null/history-dependent conditions[]{.C46}. This limits that specified
post-extraction error mechanism. Issuance and onset estimates were held fixed, large errors
increased shared-fallback routing, and systematic or state-dependent observation errors were
not tested. Neither this experiment nor the observed clock rules out a measurement explanation.

### 3.3 Baseline level and exploratory duration structure

The preselected B2 was not empirically the strongest comparator: its development likelihood was
lower than B0 and B1, and its held-out base scores were descriptively lower[]{.C60}[]{.C61}.
That motivates model review, not a unique diagnosis of the latent recurrence process. The
measured gap level also shifted between eras. A frozen baseline can miscalibrate its level,
and a predictor with a shifted mean can partially correct it.

Post-result diagnostics combined trailing mark centring with rolling location recalibration.
The analogous point-B0 duration gain fell from [0.0184]{.C62} to [0.0132]{.C62} nats; the
observing-rate gain fell from [0.0030]{.C62} to [0.0014]{.C62}. Both the predictor and base changed,
so these differences do not allocate causes or measure a component of C01. Guarded duration
estimates stayed positive. Point-B0 retained positive lower limits; DF B0 and B2 intervals
crossed zero. The observing-rate estimate also remained positive but inconclusive[]{.C63}.
Different significance labels do not establish a difference between predictors.

These historical diagnostics retained the original unguarded development coefficient and
recalibrated from saved evaluation labels with proxy availability times. They were not an
execution of the later proposed rolling forecast algorithm. Trailing averages cannot remove
arbitrary shared trends or states by construction. Observing-rate and duration contrasts
therefore remain compatible with calibration and observation pathways.

The earlier post-result class fits also remain exploratory. A long/short indicator attained a
larger in-sample likelihood than continuous log duration with historical nuisance parameters
fixed and a free common level; adding within-class duration changed little[]{.C21}.
That supports considering a parsimonious class model, not exclusive attribution to class or an
absence test. The frozen class rule's coding interacted with its fixed intercept; a shared
level adjustment improved its descriptive score without rescuing the predeclared result[]{.C22}.
Full fits and alternation diagnostics are in Supplement S3.3–S3.5 and Fig. S2.

### 3.4 Precision planning and a failed transfer

The sequential synthetic planning study separated positive score moments from gain by the
actual development-trained forecast. In a clean eight-star case with nominal individual
latent-oracle gain [0.004]{.C65} nats before measurement and learning, at [1,100]{.C65} evaluation
issuances, whole-star association-test rejection was [81.8]{.C65}%, but frozen-gain rejection
was [36.65]{.C65}%. Dependence, missingness and delayed/noisy labels lowered performance;
no robust sample-size guarantee followed. An oversized development coefficient could give a
positive score moment and negative expected frozen gain[]{.C66}. A six-star supplement likewise
failed to establish a robust precision target[]{.C69}. These are conditional point-Gaussian
experiments, not window-score or archive-yield validation.

The frozen G3a screen opened only the pre-1990 records of [10]{.C68 .V030} catalogue-selected stars.
**None qualified** (Fig. 4). Under the frozen rules, only SS Aur exceeded the required
[40]{.C68 .V036} supported development issuances; it had [110]{.C68 .V038} and an eligible-window fraction
of [79.6]{.C68 .V039}%, but failed the operational long-bright-run screen. The other stars lacked
sufficient supported issuances, sometimes also failing window or base-information gates.
The eclipse holds used derived night streams; their synthetic no-eclipse baselines were
inconclusive before the eclipse-profile tests were reached. Eclipses were not shown to cause
those failures.

An independent reconstruction of SS Aur's [100.97]{.C71}-day flag found [four]{.C71} groups of
decisive-bright report nights, one represented by a single night. Among positive visit medians,
[69.8]{.C71}% lay in the nondecisive threshold-bright band. These facts describe a threshold-night
component bridged by near-threshold reports. They do not establish four physical outbursts,
a plateau, a subtype or a photometric contamination mechanism.

The descriptive 1980s rate comparison is large: SS Cyg had [67]{.C70} supported issuances and
[73]{.C70} confirmed episode peaks; the frozen candidate streams had [102]{.C70} supported
issuances and [485]{.C70} peaks. These are issuance/peak rates, not paired conversion
probabilities, and the candidates include derived eclipse-hold streams. In the separate
ordinary raw-report diagnostic, attrition was largest at the requirement for a covered previous
gap, including observing holes and ineligible onset windows[]{.C70}. Assuming the frozen
candidate rates continued, all ten stars ignoring qualification gates would project only
[367.2]{.C68 .V035} supported issuances over 36 years. This is a planning extrapolation,
not an observed test count or a bound on other methods. We stop this paper's expansion here;
no candidate duration effect was fitted and the proposed test period stays closed.

## 4. Discussion

### 4.1 A score result with an unresolved observation model

The original trained duration term improved the prespecified working interval score under its
frozen extraction and history baseline. Independent numerical reconstruction and post-access
repair audits make that computational result reviewable. They do not supply an observation
model for the latent onset. The distinction changes the scientific claim: a probability
assigned to a fitted interval can improve through properties of the reporting and extraction
process as well as through better knowledge of the physical crossing.

R1 and R2b sharpen that limitation. Point rescoring is positive, but alternative report-window
and observed-clock comparisons are inconclusive. Their different populations, clocks, marks
and baselines prevent a clean measurement-error decomposition. Measured duration and the next
gap share an end estimate; replacing that estimate with an observed report changes the
coupling but retains cadence lag and selection. A mathematically valid score for coarsened
observations would require the complete observation kernel and risk-set premises, not merely
narrow windows or decisive-looking reports.

Baseline calibration adds another route. The post-result guards reduce some gains, showing
that recent-level information and mark centring matter. They do not establish how much of C01
is a level correction, and their own retrospective label-availability assumptions require
qualification. A stronger state-space model cannot simply be assumed stronger: the particular
B2 implementation fit development data less well. Those findings argue for reporting the
model and observation contract with every forecast claim, rather than treating a duration
coefficient as a property of the star alone.

Physical accounts remain possible. Cannizzo's calculations explain how unequal disc depletion
can favour alternating outburst types; we found no reported prediction in that model of the
following quiet-gap contrast after long versus short outbursts
[@cannizzo1993AccretionDiskLimit]. Duration may also proxy a slowly changing disc or transfer
state not captured by the fitted history. Alternation and a negative lagged-duration coefficient
do not exclude a slower component. None of the present contrasts separates these mechanisms.

### 4.2 What the transfer failure means

G3a failed before a multi-star effect test existed. That is useful evidence about transport of
this measurement and forecast contract. A dense-looking archive can contain few consecutive
cycles with a covered previous gap, a decisive span and usable outcome. The prespecified
thresholds, coverage rule, prefix history, morphology screen and eclipse reductions all helped
define which opportunities counted. No observed effect in another star was rejected.

We retain the failure and stop expanding this paper rather than change rules until a cohort
qualifies. This is a scope decision. It is not a theorem that a different measurement model,
a later development split, later coverage or another archive could not support a multi-star
analysis. Such work would need its own development and frozen evaluation; it could not turn
this failed transfer into a pass. The single-star result's generality remains untested.

**Table 2.** Assumptions and limits of the principal conclusions.

| Calculated result | Required assumptions or design | Remaining limit |
|---|---|---|
| Original M3−M2 working-score gain | Frozen parameters, eligibility and cluster inference | Proper latent-onset likelihood and full measurement validity are unestablished |
| Positive saved-point sensitivity | Same fitted points and original associations | Points are uncertain extractions; no independent confirmation |
| Inconclusive R2b contrasts | Declared support, clocks and block summaries | Unsupported selection, containment/CAR and dependence remain assumptions |
| Smaller post-result guarded gains | Specified retrospective recalibration and centring | Neither a causal partition nor proof that all slow variation is removed |
| Synthetic association/gain performance | Declared Gaussian processes and star dependence | No universal effect, sample-size or real-window inference guarantee |
| No qualifying G3a cohort | Frozen early-record qualification and catalogue thresholds | A feasibility result for these rules; no candidate duration-effect inference |

### 4.3 What would sharpen the answer

The most useful next evidence would independently connect report windows to the latent crossing
and complete risk set, while making the information available at every historical update explicit.
An independently qualified extraction would test whether the working-score result depends on the
current measurements. A new forecast comparison would then need a baseline whose adaptation,
mark coding and nuisance estimation were all fixed together, with uncertainty checked under the
admitted dependence and observation process.

Those requirements are more specific than adding forecasts to the same pipeline. The present
study does not measure scheduling utility, operational calibration or a physical-memory parameter.
SS Cyg observations from 2018 onward and the candidate stars' test records remain closed.
No new access, release, venue or submission decision follows from this synthesis.

## 5. Conclusions

Adding completed-outburst duration met the frozen SS Cyg working-score criterion:
[0.0165]{.C01 .V001} nats per issuance, interval [0.0049]{.C01 .V002} to
[0.0281]{.C01 .V003}, across [441]{.C01 .V004} issuances after the documented post-access
format repair. The scored intervals have not been established as a proper observation likelihood
for physical onset. The original later-period and class-rule secondaries and the redesigned
headline comparisons remain inconclusive; level-adjustment diagnostics identify sensitivities
without allocating causes.
A prospectively frozen early-record transfer screen qualified no multi-star cohort. The resulting
paper is a single-star working-score study and a documented measurement/transfer audit, not a
demonstration of physical memory or general dwarf-nova predictability.

## Methods in brief

Definitions and the original methods are in Supplement S1–S2; original and exploratory results,
including report windows, precision studies and transfer attrition, are in S3. Review corrections
are preserved in S4 and reproduction commands in S5. The claims ledger links each numerical
statement to its evidence and limitations.

## Roles of AI systems and humans

Barry W. Brook (University of Tasmania) led the science, set access boundaries, chose the original
forecast-gain claim and approved the protocol deposit and bounded openings. He reviews the final
products and decides authorship, venue, release and submission. GPT-6 Pro (OpenAI, through ChatGPT)
produced the seed ideation and framework; a later GPT-6 Pro review reopened the observation-model
research. Claude Opus 5.5 (Anthropic, through Claude Code) developed and diagnosed the extractors,
wrote X4 and the initial prefix-feature code, audited the literature and physical framing, proposed
or reviewed protocols, checked the results and wrote the first product drafts. A Claude Sonnet
subagent refreshed the novelty search. GPT-6 Codex (OpenAI, through Codex) implemented and executed
the forecasting, simulation, scoring and sealed-evaluation work; repaired the parser; built independent
numerical and semantic audits; implemented the observation/clock reassessment and transfer screen;
and prepared the figures, build system and integrated second drafts. Claude and Codex reviewed one
another's evidence, including failed designs and interpretation corrections.

Model names follow the systems' recorded labels. Agreement between agents is not treated as
validation: the records identify separate derivations, implementations, inputs seen and limits of
each check. Reviewed correspondence snapshots are public; native observer records remain private
to the retained-data workflow.

## Data and code

The living repository <https://github.com/BWBrook/dwarf-nova-memory> contains protocols, source,
frozen parameters, aggregate evidence, claims, figures and access receipts. Code is MIT licensed;
text, figures and derived data are CC BY-SA 4.0. The original evaluation protocol is archived at
<https://doi.org/10.5281/zenodo.24053338>. G3a was frozen in Git before its authorized early-record
access; it was a feasibility screen, not a preregistered multi-star effect test.

AAVSO observations are available through the International Database. Raw observations, observer
identities, event catalogues and individual forecast scores are not redistributed here. Reproduction
uses the retained hashed inputs without another archive request (Supplement S5). We acknowledge the
worldwide AAVSO observer community. Observer credit and co-authorship require review before release
against the [AAVSO guidelines](https://aavso.org/data-usage-guidelines-2026-07/).

## References
