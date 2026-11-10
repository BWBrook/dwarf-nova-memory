# The length of an SS Cygni outburst helps forecast the next: a preregistered test on a century of amateur observations

<div id="authors"></div>

## Abstract

Dwarf novae brighten in repeated outbursts when the gas disc around a white dwarf heats up. In SS
Cygni, longer outbursts tend to precede longer quiet intervals. Using a century of amateur
observations from the AAVSO, we tested whether outburst duration improves forecasts of the next
onset beyond recent timing. Lognormal recurrence models fitted on 1910–1959 were frozen and
preregistered before 1960–2017 was opened. Duration raised the working log score by
[0.0165]{.C01 .V001} nats per forecast (90% interval [0.0049]{.C01 .V002}–[0.0281]{.C01 .V003};
[441]{.C01 .V004} forecasts), meeting the preregistered criterion. Two redesigned timings and both
preregistered secondary tests gave smaller gains with intervals spanning
zero.[]{.C55}[]{.C07}[]{.C08} A frozen screen of ten other dwarf novae found none whose pre-1990
records could repeat the test.[]{.C68} Linking the working score to physical onsets requires a
validated observation model, and shared end estimates or activity-dependent observing could couple
duration with timing. A documented parser repair followed first data access.[]{.C05}

**Key words:** stars: dwarf novae – stars: individual: SS Cygni – accretion, accretion discs –
methods: statistical

## 1 Introduction

Dwarf novae are close binaries in which a white dwarf accretes gas from a low-mass companion through
a disc. Every few weeks to months the disc switches from a cool, faint state to a hot, bright one,
and the system brightens by several magnitudes for days to weeks before fading. The disc instability
model attributes these outbursts to a thermal–viscous instability driven by hydrogen ionisation
[@lasota2001DiscInstabilityModel; @hameury2020ReviewDiscInstability]. In that picture an outburst
drains part of the disc onto the white dwarf, and the next outburst begins once the disc has
refilled to a critical state.

SS Cygni (SS Cyg) is one of the brightest and best-observed dwarf novae. Amateur observers have
reported its brightness to the American Association of Variable Star Observers (AAVSO) since the
1890s, producing a nearly continuous visual light curve. Its outbursts recur roughly every seven
weeks and fall into short and long kinds, lasting about one and two weeks respectively (Fig. 1A).

The record has long been searched for dependence between successive cycles. Bath and van Paradijs
related outburst energy to the following interval [@bath1983OutburstPeriodenergyRelations]. Cannizzo
and Mattei (CM92) analysed [705]{.C40} outbursts and found that duration correlates with the
following quiet interval (r = [0.223]{.C40}) and with the preceding one (r = [0.282]{.C40}), that
successive durations alternate (r = [−0.400]{.C40}), and that durations divide at about [12]{.C40}
days into short and long classes [@cannizzo1992LongtermBehaviorSS]. They also showed that how a
cycle is defined governs the strength of duration–cycle correlations, and later extended the
outburst statistics [@cannizzo1998StudyOutburstsSS]. Disc calculations reproduce long/short
alternation and slow changes in recurrence [@cannizzo1993AccretionDiskLimit]. Related work examined
symbolic dependence in outburst widths (Hempelmann and Kurths, *Astronomy and Astrophysics*, 1990,
232, 356), searched for low-dimensional chaos [@cannizzo1988ChaosSSCygni] and short-term precursors
[@price2007SSCygniOutburst], and studied recurrence in other dwarf novae
[@vanderwoerd1987RecurrenceBehaviorOutbursts].

These studies estimate associations on the data they describe. A forecast test asks whether the
information improves predictions of data the forecaster has not seen. The answer depends on what the
forecaster already knows: recent quiet intervals carry information about the next one, so the useful
question is whether duration adds to them. The closest forecasting precedent we found is
Grigorievskiy and colleagues' study in the 2014 ITISE proceedings (pp. 520–531), which tested point
forecasts of onset on one held-out outburst of V363 Lyr. To our knowledge, the present study is the
first preregistered probabilistic test of dwarf-nova recurrence forecasts on held-out data, and the
first held-out test of duration beyond a timing baseline.[]{.C41}

Two hypotheses predict that duration should help. Under the *depletion hypothesis*, a long outburst
drains more of the disc, which then takes longer to refill when the gas supply from the companion is
similar from cycle to cycle. Under the *state hypothesis*, duration tracks a slowly changing
accretion state, such as the mass-transfer rate, that recent intervals describe incompletely. Both
predict that forecasts including duration will outperform forecasts based on timing alone.
Separating them requires measurements beyond outburst timing (Section 4.2).

We tested the prediction with a design that is standard in forecasting and rare in astronomy.
Forecasts were judged by a logarithmic score, which rewards the probability assigned to what happens
[@gneiting2007StrictlyProperScoring], and evaluated strictly forward in time
[@burkner2020ApproximateLeavefutureoutCrossvalidation]. We fitted the models to 1910–1959, froze
them, published the protocol and then scored every forecast for 1960–2017. We then examined how the
result depends on the way outbursts are timed, and screened ten other dwarf novae to see whether
their records could support the same test. Section 2 describes the data and methods, Section 3 the
results, Section 4 their interpretation and Section 5 the limitations.

## 2 Data and methods

### 2.1 Observations

We used visual magnitude estimates of SS Cyg from the AAVSO International Database, requested in
bounded annual windows, hashed on receipt and restricted to the visual band (`Vis.`) with validation
flag `V`. Reports fainter than an observer's detection limit were kept as limits. All model choices
and fits used the development period 1910–1959. The evaluation period covers forecasts issued from
1960 January 1 to 2017 December 31 (JD 2436934.5 to 2458119.5); it contains [500,479]{.C15} archive
rows after deduplication, of which [249,356]{.C15} meet the selector. Observations from 2018 onward
are reserved for a future test. Times are Julian Dates as returned by the archive.

### 2.2 Outburst extraction

An extraction algorithm, X4, identifies outbursts as episodes brighter than visual magnitude 10,
which lies between SS Cyg's quiescent and outburst brightness. X4 groups each observer's reports
into visits and estimates when the light curve crossed magnitude 10 on the rise (the onset) and on
the fade (the end). Each crossing is summarised as an interval and a point, fitted to nearby reports
with a shared 0.05-mag allowance for systematic error common to observers. An episode is confirmed
by bright reports from two distinct observers, or from one observer on at least two nights, with a
margin past the threshold and no contradicting faint report. Duration runs from fitted onset to
fitted end, and a quiet interval from one outburst's end to the next onset. A quiet interval counts
as covered when no gap between visits within it exceeds seven days. X4 was adopted during
development after three earlier extractors failed a synthetic recovery screen; it passed that screen
at magnitude 10 (Appendix A).

### 2.3 Forecasts

A forecast is issued at the observation time when reports first confirm that the current outburst
has faded. Every such confirmation issues a forecast, including repeats. Each forecast uses only
reports dated within the preceding 400 days: X4 is rerun on that window alone, and tests that insert
later rows confirm that no predictor changes.

Each forecast is a lognormal distribution for the quiet interval $Q$ that follows the fitted end $e$
of the completed outburst. With log-location $\mu$ and log-scale $\sigma$, the three models are

$$\begin{aligned}
\mathrm{M0}&:\ \mu = \alpha,\\
\mathrm{M2}&:\ \mu = \alpha + \gamma_1 q + \gamma_2 L,\\
\mathrm{M3}&:\ \mu = \alpha + \gamma_1 q + \gamma_2 L + \beta x,\quad \beta \ge 0,
\end{aligned}$$

where $q$ is the standardised log of the previous covered quiet interval, $L$ the standardised mean
of up to six earlier covered log quiet intervals ($L = 0$ when none is available), and $x$ the
standardised log duration. Centres and scales are development means and standard deviations. M2 is
the timing baseline and M3 adds duration; the constraint $\beta \ge 0$ encodes the direction both
hypotheses predict. A forecast issued at age $a = t_{\mathrm{issue}} - e$ is the lognormal
conditioned on $Q > a$. Forecasts without a covered previous interval use M0 in both arms, and
forecasts without a fitted end use a common remaining-wait forecast; both contribute exactly zero to
the comparison. Table 1 summarises the models and test, and Fig. 1B shows one cycle schematically.

### 2.4 Outcomes and the working score

The outcome of a forecast is the onset of the next outburst as X4 estimates it from the later
record, an interval $(l, u]$. A forecast stops at the first loss of coverage (a visit gap over seven
days), at the next issued forecast, or at the end of the evaluation period. If no onset is
established by then, the forecast is right-censored at that time $c$. The *working score* of a
forecast is

$$s = \begin{cases}
\log\left[S(l-e) - S(u-e)\right] - \log S(a) & \text{onset interval},\\
\log S(c-e) - \log S(a) & \text{censored},
\end{cases}$$

where $S$ is the lognormal survival function. It is the log probability the forecast assigned to the
extracted onset window, or to no onset before $c$, measured in nats; higher is better. The paired
gain is M3's score minus M2's for the same forecast. Exponentiating a mean gain gives the ratio of
the geometric-mean probabilities the two models assigned to the scored outcomes.

### 2.5 Fitting, freezing and the test

M2 was fitted by maximum likelihood to the [307]{.C04} timing-eligible development forecasts and
frozen. The duration coefficient was then fitted with M2 held fixed, so that $\beta = 0$ reproduces
M2 exactly. The frozen values are $\beta$ = [0.0466]{.C04} per standard deviation of log duration,
$\gamma_1$ = [0.0780]{.C04}, $\gamma_2$ = [0.0513]{.C04} and $\sigma$ = [0.346]{.C04}.

The single preregistered statistic is the mean paired gain over all score-eligible forecasts issued
in 1960–2017, including the zero contributions of fallback forecasts. Its standard error is
cluster-robust over consecutive six-year blocks (2191.5 days) from the start of 1960, with a
$G/(G-1)$ correction for $G$ nonempty blocks, and inference uses Student's t with $G - 1$ degrees of
freedom. The criterion was a one-sided 95% lower bound above zero, equivalent to a two-sided 90%
interval wholly above zero. The protocol also specified secondary comparisons: an era split at 1993,
after the end of CM92's record, and a rule that replaces continuous duration with CM92's 12-day
long/short classes plus within-class duration. Before the development fit, a synthetic screen
confirmed [11]{.C30} of [40]{.C30} simulated evaluations at an effect sized to CM92's correlations,
and [3]{.C31} of [220]{.C31} no-effect histories.

### 2.6 Access and execution

The protocol was deposited on Zenodo (doi:10.5281/zenodo.24053338) on 2026 November 8, before any
evaluation data were requested (Fig. 1C). The first request stopped before any forecast was scored,
because the archive returned the literal token `None` for missing uncertainties, a field that no
analysis uses. The parser was changed to accept that exact token without altering or dropping a row.
Independent review, invariance tests and a full synthetic rehearsal passed before the run resumed,
and all forecasting code, parameters and protocol files stayed unchanged.[]{.C05} Two independent
implementations of the forecast ledger had to agree exactly before scoring, and a separate checker
reproduced every score.[]{.C01}

### 2.7 Measurement checks after the result

After the result, an external review asked how far it depends on the way outbursts are timed. The
analyses in this subsection were each specified before their own fits, and all reuse the opened
data.

- **Rescoring (R1)** audited the censoring rules, scored each forecast against X4's point estimate
  of onset in place of its interval, and added synthetic errors to fitted end times.
- **Report windows and clocks (R2b)** rebuilt each onset outcome as a report window, from the last
  faint report to the first decisively bright one (extractor X5). Two clocks were compared. The
  first keeps the fitted end. The second starts the quiet interval at the first decisively faint
  report and measures duration as the span of decisively bright reports, so no end time is
  interpolated. These comparisons use new windowed timing baselines: B0 with recent-interval
  covariates, B1 with discounted history and B2, a state-space level model chosen in advance.
- **Drift recalibration** recentred duration on the preceding ten outbursts and updated the
  baseline level from preceding outcomes, to ask how changes in the typical quiet interval affect
  the gain.

### 2.8 Transfer screen

To ask whether other dwarf novae could support the same test, we froze a screen in Git before
requesting any of their data. Eight candidates (SS Aur, RU Peg, AR And, X Leo, TW Vir, UU Aql, CH
UMa and DX And) and two eclipsing systems held to stricter rules (U Gem and IP Peg) were chosen from
catalogue properties, with thresholds proposed from the same catalogues. Only records before 1990
(JD < 2447892.5) were opened, keeping later decades for a future test. A star qualified if its
pre-1990 record yielded at least [40]{.C68 .V036} supported forecasts (with a covered previous
interval, a measurable duration and a scorable outcome), at least [70]{.C68 .V037}% eligible onset
windows, stable timing-baseline fits, and no bright run of 60 days or more; the eclipsing systems
also needed to pass an eclipse-handling check. The screen fitted no duration effect and computed no
forecast gain (Appendix E).

**Table 1.** Models and test.

| Item | Specification |
|---|---|
| Forecast | Lognormal quiet interval after the fitted end, conditioned on survival to issue |
| M0 | Constant log-location |
| M2, timing baseline | Log previous covered interval; mean of up to six earlier covered log intervals |
| M3 | M2 plus log duration, $\beta \ge 0$, fitted with M2 fixed |
| Development fit | 1910–1959; frozen $\beta$ = [0.0466]{.C04}, $\gamma_1$ = [0.0780]{.C04}, $\gamma_2$ = [0.0513]{.C04}, $\sigma$ = [0.346]{.C04} |
| Evaluation | Every forecast issued 1960–2017 |
| Working score | Log probability of the extracted onset window, or of survival to censoring, given survival to issue |
| Statistic and criterion | Mean M3 − M2 gain; six-year cluster standard error; one-sided 95% lower bound above zero |
| Redesigned comparisons | Report-window outcomes; fitted-end and decisive-faint clocks; baselines B0, B1, B2 |

## 3 Results

### 3.1 Duration improved the frozen forecasts

The duration model forecast longer waits after longer outbursts: doubling the duration, roughly the
difference between a short and a long outburst, lengthens the median of the lognormal clock by about
[9]{.C04}%. Over [441]{.C01 .V004} forecasts issued in 1960–2017, adding duration raised the mean
working score by [0.0165]{.C01 .V001} nats (90% interval [0.0049]{.C01 .V002} to
[0.0281]{.C01 .V003}; ten blocks, nine degrees of freedom), meeting the preregistered criterion
(Fig. 2). The geometric-mean probability assigned to the scored outcomes rose by [1.7]{.C02}%. The
timing baseline M2 itself gained [0.117]{.C10} nats over the constant forecast M0, so duration added
about [14]{.C02}% of what recent timing adds. The outcomes comprised [435]{.C03} onset intervals and
[six]{.C03} censored forecasts, and [five]{.C03} forecasts used the shared fallback.

Fig. 2A shows the first eligible forecast of the evaluation period, chosen by date. M3 gave a median
remaining wait of [26.77]{.C42} days against [27.57]{.C42} for M2, and placed [0.603]{.C42} of its
probability within 30 days against [0.577]{.C42}. The gain was positive in [eight]{.C25} of ten
six-year blocks (Fig. 2B), and leaving out any one block gave means from [0.0132]{.C25} to
[0.0194]{.C25}. Frozen sensitivities to uniform end times, a previous-gap-only baseline, a two-day
issue delay and three-year clusters kept the lower bound above zero (Appendix B). M3's predictive
intervals were conservative: its nominal 50% intervals covered between [0.546]{.C11} and
[0.617]{.C11} of outcomes, and its nominal 90% intervals between [0.923]{.C11} and [0.980]{.C11}.

The preregistered era split gave [0.0240]{.C06} nats ([0.0091]{.C06} to [0.0389]{.C06}; [261]{.C06}
forecasts) for 1960–1992 and [0.0057]{.C07} ([−0.0107]{.C07} to [0.0221]{.C07}; [180]{.C07}
forecasts) for 1993–2017. The long/short rule gained [0.0025]{.C08} nats ([−0.0022]{.C08} to
[0.0072]{.C08}).

### 3.2 Measurement checks

Fig. 3 collects the duration gains from every comparison. Scoring against X4's point estimates of
onset gave [0.0154]{.C44} nats ([0.0034]{.C44} to [0.0274]{.C44}). The censoring audit changed
[zero]{.C43} of the [441]{.C43} outcomes. The report-window comparisons gave smaller gains with
intervals spanning zero: [0.0075]{.C55 .V009} nats ([−0.0008]{.C55 .V010} to [0.0159]{.C55 .V011};
[432]{.C55 .V012} forecasts) on the fitted-end clock and [0.0043]{.C55 .V013} nats
([−0.0008]{.C55 .V014} to [0.0094]{.C55 .V015}; [431]{.C55 .V016} forecasts) on the decisive-faint
clock, both with baseline B2. Their paired difference was [−0.0031]{.C55 .V017} nats
([−0.0078]{.C55 .V018} to [0.0017]{.C55 .V019}; Appendix C).

In synthetic null and gap-dependent histories, adding independent errors to fitted end times gave
mean gains of zero or below at every tested error size.[]{.C46} An observing-rate covariate, the
reporting rate during the completed outburst, gained [0.0030]{.C56} nats ([0.0013]{.C56} to
[0.0048]{.C56}) on the decisive-faint clock; adding it alongside duration left the duration gain at
[0.0043]{.C56} nats.

Of the redesigned baselines, B1 fitted the development data best and B2 worst (negative log
likelihoods [827.24]{.C61} for B1, [830.19]{.C61} for B0 and [849.28]{.C61} for B2). The typical
quiet interval early in the evaluation period was shorter than in the development blocks.[]{.C61}
Recalibrating for that drift reduced the duration gain in the R2b comparison closest to the primary
design (point clock, baseline B0) from [0.0184]{.C62} to [0.0132]{.C62} nats and the observing-rate
gain from [0.0030]{.C62} to [0.0014]{.C62}. After recalibration the duration gains stayed positive
on every clock and baseline, from [0.0052]{.C63} to [0.0132]{.C63} nats; the point-clock B0 gain
kept a positive lower bound.[]{.C63}

### 3.3 Transfer screen

None of the ten stars qualified (Fig. 4; Appendix E). Nine yielded fewer than the [40]{.C68 .V036}
supported forecasts required, and across all ten the frozen pre-1990 streams yielded
[217]{.C68 .V033}. SS Aur yielded [110]{.C68 .V038}, with [79.6]{.C68 .V039}% eligible onset
windows, and failed the long-run check with a [100.97]{.C71}-day bright run made up of [four]{.C71}
separate clusters of report nights. The eclipsing systems U Gem and IP Peg yielded [27]{.C68 .V054}
and [0]{.C68 .V056} supported forecasts, and their eclipse check stopped at its baseline stage.

The candidates' records time successive outbursts far less often than SS Cyg's. In 1980–1989 SS
Cyg's record yielded [67]{.C70} supported forecasts against [73]{.C70} confirmed outbursts; the ten
candidates together yielded [102]{.C70} against [485]{.C70} (Fig. 4B). The largest single loss was
the requirement for a covered previous quiet interval: in an ordinary report-level diagnostic,
[822]{.C70} pre-1990 candidate forecasts with a timing clock fell to [280]{.C70} once that
requirement applied. At the 1980s rate, all ten stars together, ignoring the other qualification
rules, would yield [367.2]{.C68 .V035} supported forecasts over 36 years.

## 4 Discussion

### 4.1 What the result shows

The duration of a completed outburst improved forecasts of SS Cyg's next onset beyond what recent
quiet intervals provided, in a test whose models and criterion were fixed before the evaluation data
were opened. The direction matches CM92's correlation between duration and the following quiet
interval, now carried forward in time over 58 years of observations. The gain is modest: about a
seventh of what recent timing contributes. Most of the predictability of SS Cyg's next outburst lies
in its recent rhythm, and duration adds a small increment, positive in eight of ten six-year blocks.

Rescoring against point onsets reproduces the gain. Rebuilding the outcomes from report windows
gives smaller gains, [0.0075]{.C55 .V009} and [0.0043]{.C55 .V013} nats, with intervals spanning
zero. The observing-rate covariate carries a smaller amount of forecast information of its own, and
adding it leaves the duration gain unchanged on the decisive-faint clock.

### 4.2 Depletion or state?

Both hypotheses predict the observed direction. The depletion hypothesis ties the effect to
individual cycles: each long outburst should lengthen the interval that follows. Disc models that
drain different fractions of the disc in long and short outbursts reproduce the observed alternation
[@cannizzo1993AccretionDiskLimit], and alternation is strong in these data: the lag-one correlation
of log duration was [−0.52]{.C24} in the evaluation years. In exploratory fits a long/short
indicator described the evaluation data at least as well as continuous duration (Appendix D), which
fits a cycle-level mechanism tied to outburst type.

The state hypothesis ties the effect to slower change: duration would carry information about the
mass-transfer rate or disc state that the recent-interval average smooths over. SS Cyg's accretion
state does change, as its anomalous event of 2021 showed [@kimura2021NatureAnomalousEvent]. The
drift in the typical quiet interval between development and evaluation, and the smaller gains after
recalibrating for it, fit a contribution from slow change, in the star or in how it was observed.

Forecasts that include an independent measure of accretion state, such as quiescent brightness or
X-ray and extreme-ultraviolet flux [@wheatley2003XrayExtremeultravioletFlux], could separate the
two: if duration's gain shrinks once state is known, the state hypothesis gains support; if it
persists, depletion does. The frozen forecasts can also be scored on SS Cyg's observations from 2018
onward, which remain unopened.

### 4.3 What a record needs

The test was possible because SS Cyg's record times most successive outbursts. A forecast built on
the previous interval needs uninterrupted coverage across two cycles, and one observing gap of more
than a week removes it. Under the same rules the candidates' pre-1990 records yielded about one
supported forecast per five confirmed outbursts, against nearly one per outburst for SS Cyg. Their
records from 1990 onward, and automated surveys, may time outbursts more completely; a multi-star
test would need its own frozen design on those records.

The design itself is general. Fitting on early records, freezing and publishing the forecasts, and
scoring them on later records suits other long, irregular records of recurrent events kept by many
observers, such as volcanic eruptions or disease outbreaks. It needs a record that times successive
events, a baseline that captures their recent rhythm, and a score fixed before the test data are
seen.

## 5 Limitations

Table 2 lists the assumptions behind the primary result, what tested each and what remains open.
Three matter most.

First, the working score treats X4's onset windows as true. The windows are fitted statistical
summaries, and linking the score to the physical onset of an outburst requires a validated model of
how reports record the star: correct association of reports with outbursts, containment of the true
crossing in each window, and an observation process independent of the outcome (Appendix C). X4
passed its recovery screen on waveforms known during development; recovery on a waveform family held
out from development remains untested, because that benchmark failed qualification before X4 was
scored on it.

Second, duration and the following quiet interval share one estimated end time, so errors in that
time can couple them, and observers may report more often when the star is active. The
decisive-faint clock removes interpolation from the end but keeps report timing, and an invented
cadence construction shows that report timing alone can produce a positive duration gain.[]{.C48}
The endpoint-error experiments covered independent errors only, and the observing rate itself
carried forecast information.

Third, everything after the primary result reuses opened data and is exploratory. The redesigned
comparisons and the drift recalibration change baseline, clock, coding and scored population
together, so their smaller gains measure no fraction of the primary gain.[]{.C62} A richer timing
baseline could also absorb part of that gain.

The evaluation followed a parser repair made after the first data access and before scoring; the
protocol DOI timestamps the original code, and the repair is documented separately.[]{.C05}
Forecasts use reports by observation date, and when historical reports were uploaded or revised is
unknown, so the test replays the archive as it stands today. The transfer screen's ratios count
forecasts and outbursts by different landmarks and describe yield under its frozen rules, which used
catalogue thresholds.[]{.C70} The result concerns one star.

**Table 2.** Assumptions behind the primary result.

| Assumption | Why it matters | What tested it | What remains open |
|---|---|---|---|
| Extracted onset windows stand for physical onsets | Defines what the score rewards | Synthetic recovery screen; point rescoring[]{.C44}; report windows[]{.C55} | A validated observation model; recovery on unfamiliar waveforms |
| End-time errors are independent of the next interval | A shared end couples duration and gap | Sign constraint; independent-error experiments[]{.C46}; decisive-faint clock[]{.C55} | Systematic or state-dependent errors; report-timing coupling[]{.C48} |
| Observing effort is independent of the outcome | Observers may watch an active star more closely | Observing-rate covariate[]{.C56} | The rate itself carries information |
| The timing baseline is adequate | The gain is measured beyond it | Baselines B0–B2; drift recalibration[]{.C61}[]{.C62}[]{.C63} | Richer baselines; recalibration is exploratory |
| The archive reflects what was reported at each date | Defines the information at issue | Prefix-only predictors; inserted-row tests | Upload and revision dates are unknown |
| Six-year blocks are independent | Sets the interval width | Leave-one-block-out; three-year clusters[]{.C09}[]{.C25} | A standard error [1.43]{.C25} times larger removes the result |
| The evaluation followed the protocol | Confirmatory status | DOI before access; two implementations; independent checker | Parser repair after first access[]{.C05} |
| One star | Scope | Ten-star transfer screen[]{.C68} | No other star qualified |

## 6 Conclusions

A century of amateur observations of SS Cygni supported a preregistered test of a question first
raised by correlations in the same record: does the length of an outburst help forecast the next?
Forecasts including duration, frozen on 1910–1959 and scored on 1960–2017, assigned more probability
to the extracted onsets than forecasts based on recent timing alone, meeting the preregistered
criterion. The gain is a small increment on a rhythm that recent timing already captures well.
Separating disc depletion from a slowly changing accretion state, and repeating the test on other
dwarf novae, will need records that time successive outbursts as completely as SS Cyg's, together
with independent measures of the accretion state. The frozen forecasts, code and protocol are public
and ready to be scored on SS Cyg's later observations.

## Acknowledgments

We acknowledge with thanks the variable star observations from the AAVSO International Database
contributed by observers worldwide and used in this research.

*[Placeholder: generative-AI declaration, to be written before submission. It will state the roles
of GPT-6 Pro, Claude Opus 5.5 and GPT-6 Codex, and how their calculations, analyses and figures were
tested and validated, as the journal requires.]*

<!-- Source material for the declaration: the former roles section (main.md at 7a736d5) and
manuscript/ai-roles.json. Before release: exact AAVSO acknowledgment wording and observer credit,
against https://aavso.org/data-usage-guidelines-2026-07/. -->

## Data availability

The repository <https://github.com/BWBrook/dwarf-nova-memory> contains the protocols, source code,
frozen parameters, aggregate evidence, claims ledger, figures and access receipts. Code is MIT
licensed; text, figures and derived data are CC BY-SA 4.0. The evaluation protocol is archived at
<https://doi.org/10.5281/zenodo.24053338>. AAVSO observations are available from the International
Database. Raw observations, observer identities, event catalogues and individual forecast scores are
retained outside the repository; reproduction uses those hashed inputs without a new archive
request.

## Appendix A: Extraction, issuance and access

**Extraction.** X4 (`src/dnmem/extract_x4.py`) forms its crossing summaries from normalised
slope-mixture fits to nearby estimates. The 0.05-mag shared allowance stops the intervals shrinking
without limit as estimates accumulate; it was chosen on development simulations. The issuing rule
arms only on bright evidence at least 0.5 mag past the threshold. Three earlier extractors, X1–X3,
failed qualification. X4 passed a synthetic screen at magnitude 10 on the qualified cadence family,
where the seven-day coverage rule was also chosen; magnitude-9.5 diagnostics failed in later eras.

**Issuance and predictors.** The current episode is the last prefix episode whose end bracket
reaches the issuing bright evidence. A duration of zero or less makes the mark unavailable. The
previous interval counts only if the previous episode begins more than 30 days inside the 400-day
window. A two-day reporting delay was a frozen sensitivity.

**The sign constraint.** Shared end-time error pushed fitted null duration coefficients negative in
development simulations, which motivated fitting $\beta$ with M2 fixed and bounding it at zero. The
bound restricts direction; an exact construction with constant true duration can still yield
positive information, so endpoint coupling remains a stated limit (Section 5).

**Access timeline** (2026 November 8, UTC). Protocol published 12:34:47; first request 12:38:28,
stopped 12:39:51 before any ledger or score; repaired acquisition 12:51:18; ledger concordance and
primary result 13:06:58. The repair freeze is commit `5e39aeb` and the execution commit `d7151e0`.
No person or agent inspected real scores, outcomes, counts or coverage summaries before the primary
result was written.[]{.C05} A separate checker reproduced all 2,641 variant score rows to order
$10^{-13}$.[]{.C01}

## Appendix B: Frozen sensitivities and calibration

**Table B1.** Frozen comparisons: mean paired working-score gain (nats per forecast) and 90% cluster
interval. Only the first row is confirmatory.

| Comparison | Forecasts | Gain | Interval |
|---|---:|---:|---|
| Primary, M3 − M2, 1960–2017 | [441]{.C01 .V004} | [0.0165]{.C01 .V001} | [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003} |
| 1960–1992 | [261]{.C06} | [0.0240]{.C06} | [0.0091]{.C06} to [0.0389]{.C06} |
| 1993–2017 | [180]{.C07} | [0.0057]{.C07} | [−0.0107]{.C07} to [0.0221]{.C07} |
| 12-day class and within-class rule | 441 | [0.0025]{.C08} | [−0.0022]{.C08} to [0.0072]{.C08} |
| Uniform-end marks | 441 | [0.0166]{.C09} | lower [0.0044]{.C09} |
| Previous-gap-only baseline | 441 | [0.0170]{.C09} | lower [0.0054]{.C09} |
| Two-day issue delay | 441 | [0.0165]{.C09} | lower [0.0049]{.C09} |
| Joint-valid forecasts | 436 | [0.0167]{.C09} | lower [0.0049]{.C09} |
| Three-year clusters | 441 | as primary | lower [0.0059]{.C09} |
| Baseline M2 − M0 | 441 | [0.1168]{.C10} | [0.0663]{.C10} to [0.1672]{.C10} |

Deleting the [six]{.C43} censored forecasts gives [0.01678]{.C43} nats. Coverage bounds for M3's
central intervals (Fig. 5) run from definitely to possibly covered, given the extracted windows and
censoring; they describe this sample.[]{.C11} The frozen placebo with a lagged duration equals M2,
because its development coefficient sat at the bound of zero.

## Appendix C: Report windows, clocks and baselines

**Report windows.** X5 searches for decisive faintness after the previous peak before selecting the
next decisive-bright rise, and keeps raw time supports and flags. It yielded [818]{.C47} available
and [805]{.C47} eligible windows among [845]{.C47} confirmed episodes, with median width
[1.15]{.C47} days. The original report clips were missing for [434]{.C45} of the original
associations, so the earlier report-interval rescoring covered only [11]{.C45} contrasts.

**Premises.** Treating a report window as the onset outcome rests on three premises: correct
association of reports with outbursts, completeness and a valid risk set (A0); containment of the
true crossing in the window, or genuine survival through a censoring time (A1); and a complete,
normalised observation process that is coarsened at random (A2). Under them the report likelihood
factors into an observation term and the forecast probability of the window. Visit timing and
margins past threshold do not by themselves establish the premises.

**Clocks.** The decisive-faint clock anchors each forecast at the first decisively faint report,
uses the decisive-bright span as duration, and waits for report availability before issuing. Exact
coincident issues share one representative, and unsupported outcomes stay unsupported.

**Table C1.** Report-window contrasts. H3 is the paired difference between the H2 and matched H1
gains.

<!-- BEGIN GENERATED r2b -->
| Exploratory contrast | Scored issuances | Mean gain, nats | Six-year 90% interval | Twelve-year 90% interval |
|---|---:|---:|---|---|
| H1: fitted-end clock, B2 duration | [432]{.C55 .V012} | [0.0075]{.C55 .V009} | [−0.0008]{.C55 .V010} to [0.0159]{.C55 .V011} | [−0.0014]{.C55 .V021} to [0.0165]{.C55 .V022} |
| H2: observed clock, B2 bright span | [431]{.C55 .V016} | [0.0043]{.C55 .V013} | [−0.0008]{.C55 .V014} to [0.0094]{.C55 .V015} | [−0.0021]{.C55 .V023} to [0.0107]{.C55 .V024} |
| H3: observed-clock gain minus matched fitted-end gain | [431]{.C55 .V020} | [−0.0031]{.C55 .V017} | [−0.0078]{.C55 .V018} to [0.0017]{.C55 .V019} | [−0.0078]{.C55 .V025} to [0.0017]{.C55 .V026} |
<!-- END GENERATED r2b -->

**Baselines and drift.** The drift recalibration subtracted the mean of the preceding ten marks and
recalibrated the baseline level from preceding evaluation outcomes, keeping the development
coefficient. It used final saved labels at proxy availability times, and it is a diagnostic of the
historical record, distinct from a prospective forecasting algorithm.[]{.C62}[]{.C63}

## Appendix D: Long/short classes

With M2's historical parameters fixed and a free common level, likelihood-ratio statistics on the
evaluation data were [14.7]{.C21 .V005} for the class indicator against level only,
[11.7]{.C21 .V006} for continuous log duration against level only, and [0.17]{.C21 .V007} for adding
within-class duration to the class indicator. The class contrast corresponds to a [14]{.C21 .V008}%
larger working clock scale after long outbursts (Fig. 6). It was [0.16323]{.C23} (statistic
[13.504]{.C23}) in 1960–1992 and [0.07828]{.C23} ([2.262]{.C23}) in 1993–2017. Giving both frozen
rules M2's evaluation-fitted level raised the class rule's gain to [0.00905]{.C22} nats
([0.00409]{.C22} to [0.01401]{.C22}). A long outburst followed a long one in [0.1495]{.C24} of
forecast-record pairs and a short one in [0.6640]{.C24}. These fits reuse the evaluation outcomes.

## Appendix E: Transfer screen

The screen's code was fixed in Git at commit `d827313` before any candidate record was requested.
Names were resolved under the same date restriction, and pagination, identity, row-window and
duplicate checks preceded analysis. Supported forecasts used the decisive-faint clock and needed a
positive mark and an eligible onset window or positive-exposure censoring. Baseline stability was
tested on B0 fits without marks. The long-run rule flags a supported bright run of at least 60 days,
or repeated 40-day runs, with minimum night and observer support. The eclipsing systems used two
derived observer-night streams, which had to agree, and a synthetic eclipse test whose no-eclipse
baseline had to recover enough events first; neither system passed that baseline.

**Table E1.** Frozen qualification. Eclipsing-system counts use the median derived-night stream.

<!-- BEGIN GENERATED qualification -->
| Candidate | Supported development issuances | Eligible onset windows | Main failed conditions |
|---|---:|---:|---|
| SS Aur | [110]{.C68 .V038} | [79.6]{.C68 .V039}% | Operational morphology |
| RU Peg | [23]{.C68 .V040} | [63.5]{.C68 .V041}% | Count, windows |
| AR And | [7]{.C68 .V042} | [31.4]{.C68 .V043}% | Count, windows, base information/fit |
| X Leo | [35]{.C68 .V044} | [44.0]{.C68 .V045}% | Count, windows |
| TW Vir | [0]{.C68 .V046} | [11.6]{.C68 .V047}% | Count, windows, base information/fit |
| UU Aql | [15]{.C68 .V048} | [80.8]{.C68 .V049}% | Count |
| CH UMa | [0]{.C68 .V050} | [70.4]{.C68 .V051}% | Count, base information/fit |
| DX And | [0]{.C68 .V052} | [70.8]{.C68 .V053}% | Count, base information/fit |
| U Gem, hold | [27]{.C68 .V054} | [90.6]{.C68 .V055}% | Count, eclipse guard inconclusive |
| IP Peg, hold | [0]{.C68 .V056} | [66.7]{.C68 .V057}% | Count, windows, base information/fit, eclipse guard inconclusive |
<!-- END GENERATED qualification -->

**Attrition.** In the ordinary report-level diagnostic, [822]{.C70} clock-available pre-1990
forecasts fell to [280]{.C70} with a covered previous interval and [274]{.C70} after requiring a
mark. Observing holes, ineligible onset windows and association all contributed to the missing
history.

**SS Aur.** Separate parsing found [252]{.C71} positive visit medians in the flagged run, of which
[176]{.C71} lay in the band $12.5 < m \le 13.5$, just fainter than the decisive threshold. Its
decisive-bright nights form [four]{.C71} groups of [one]{.C71}, [seven]{.C71}, [three]{.C71} and
[five]{.C71} nights. Removing this flag would leave SS Aur the only star above the count gate.

The eligible-window fraction and supported count of every star are shown in Fig. 7.[]{.C68}

## Appendix F: Precision planning

Synthetic studies asked how many stars and forecasts a multi-star test would need. They simulated
development fits, guarded marks, delayed labels and rolling level updates in Gaussian log gaps, with
a nominal per-star gain of [0.004]{.C65} nats before mark noise and learning. Two statistics answer
different questions. For a unit-variance Gaussian model with standardised mark $x$, true coefficient
$\beta$ and frozen forecast shift $bx$,

$$E[U_0] = \beta, \qquad E[\Delta s] = b\beta - b^2/2,$$

so a positive score moment $U_0$ can accompany a negative gain $\Delta s$ by the actual forecast;
with $\beta$ = [0.05]{.C66} and $b$ = [0.20]{.C66}, the expected gain is [−0.010]{.C66} nats.

**Table F1.** Whole-star rejection frequencies at a nominal per-star gain of [0.004]{.C65} nats.

<!-- BEGIN GENERATED precision -->
| Stars and condition | Nominal evaluation issuances | Score-moment rejection | Frozen-gain rejection |
|---|---:|---:|---:|
| Eight, clean | [1,100]{.C65} | [81.8]{.C65}% | [36.7]{.C65}% |
| Eight, persistent / small development / missing marks | [1,100]{.C65} | [63.6]{.C65}% | — |
| Eight, noisy / delayed / common state | [1,100]{.C65} | [38.7]{.C65}% | — |
| Six, clean | [1,100]{.C69 .V066} | [76.8]{.C69 .V058}% | [33.1]{.C69 .V059}% |
| Six, clean | [2,000]{.C69 .V067} | [94.6]{.C69 .V060}% | [48.8]{.C69 .V061}% |
| Six, persistent / small development / missing marks | [1,100]{.C69 .V066} | [59.4]{.C69 .V062}% | [21.3]{.C69 .V063}% |
| Six, noisy / delayed / common state | [1,100]{.C69 .V066} | [36.2]{.C69 .V064}% | [10.3]{.C69 .V065}% |
<!-- END GENERATED precision -->

The grids used [70,000]{.C65} and [16,000]{.C69 .V068} trials. Neither establishes a robust sample
size across its stressed conditions.[]{.C67}

## Appendix G: Prior art

CM92's Table 4 gives, for [705]{.C40} outbursts from 1896 to 1992, correlations of duration with the
following onset-to-onset cycle of [0.475]{.C40} and with the preceding cycle of [0.145]{.C40}; for
end-to-end cycles the pattern reverses ([0.093]{.C40} and [0.521]{.C40}). An onset-to-onset cycle
contains its first outburst's duration, so this study's target is the quiet interval alone.
Durations split at [12]{.C40} days into [401]{.C40} short and [304]{.C40} long outbursts. A bounded
independent search found no earlier preregistered probabilistic held-out recurrence evaluation; its
queries and receipts are in `data/provenance/a10m_novelty/`.[]{.C41}

## References
