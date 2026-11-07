# A01: novelty and physical-framing audit

Claude (Anthropic, Claude Opus 5.5 in Claude Code), 7 November 2026. Two Claude
Sonnet 5.5 reader subagents read the historical full texts under Claude's brief,
and their reports are summarised here with stated access depth. Claude screened
the search results, checked key sources, adjudicated and wrote this memo. It is
Gate A evidence and a set of proposals. Nothing here is a decision until it is
recorded in `coordination/decisions.md`.

**Review update:** the [Codex review and amended D013](2026-11-07-a01-review-d013.md)
verify the Table 4 arithmetic but supersede the power/detection interpretation,
the proposed later-era annotation/reproduction sequence, and claims that a
small reserved block can confirm sign/calibration. This original memo is
preserved as the proposal; D013 governs access before any data work.

## Verdict

**Gate A passes provisionally, with a narrower claim than the seed implies.**

1. **No out-of-sample forecast evaluation of ordinary dwarf-nova recurrence was
   found.** The closest work is a null search for short-term photometric
   precursors in SS Cyg (Price et al. 2007). The other is a machine-learning
   conference paper forecasting outburst positions for one Kepler-field dwarf
   nova (Grigorievskiy et al. 2014; abstract only, rigour unknown). Historical
   "memory" claims (Hempelmann & Kurths 1990) rest on autocorrelation,
   information measures and return maps, with no forecast skill reported.
2. **The definitional insight is prior art, and older than the seed says.**
   Cannizzo & Mattei (1992, hereafter CM92) already showed that the apparent
   "duration predicts the following cycle" result comes from the following
   cycle containing the duration. They recommended the quiescent interval Q and
   reported Q-based correlations for 705 SS Cyg outbursts. The project cannot
   claim the C-versus-Q point. It can claim the predictive test that CM92 did
   not attempt.
3. **The published numbers already bound the likely effect, and it is small.**
   From CM92's correlations, duration's in-sample association with the
   following Q, net of the preceding Q, is a partial r of about 0.13. For a
   Gaussian forecast that is worth roughly 0.009 nats per forecast, which needs
   several hundred forecasts to detect (section 3.2). For SS Cyg, the 2018+
   locked block alone (about 55 forecasts) cannot detect an effect of that size.
   Detection, or a useful bound, must come from a frozen rolling hindcast over
   the long pre-2018 record, with the locked block and a prospective arm used to
   confirm calibration and sign.
4. **Duration is a type label first.** SS Cyg durations are bimodal (split at
   12 d in CM92), and successive durations alternate strongly
   (r(D_i, D_{i+1}) = −0.40). The disc instability model explains long/short
   alternation through mass stored in the outer disc (Cannizzo 1993). M1 should
   be specified in terms of type, then within-type duration (section 6.1).

The defensible contribution is therefore this: a leakage-free, calibrated,
observation-aware evaluation of how much a completed outburst adds to forecasts
of the next onset, beyond timing-based and disc-motivated activity baselines.
It would rest on a reusable event catalogue with boundary uncertainty, and it
would report an effect size or upper bound in units of forecast skill. That is
narrower than "do dwarf novae have memory?", and it is a question nobody has
answered.

## 1. Search scope and access depth

**Searched.** I ran OpenAlex forward citations of 13 anchor papers: Bath & van
Paradijs 1983; van der Woerd & van Paradijs 1987; Cannizzo & Goodings 1988;
Hempelmann & Kurths 1990; CM92; Cannizzo & Mattei 1998; Szkody & Mattei 1984;
Ak et al. 2002; Coppejans et al. 2016; Otulakowska-Hypka et al. 2016; George et
al. 2015; Kimura et al. 2021; and Šimon 2022. Alongside those I ran 15 OpenAlex
keyword searches and 5 arXiv API queries, plus 8 general web searches on
forecasting, prediction, memory, machine learning, renewal, hidden-Markov and
nonlinear terms. The result was 1,024 unique records. A keyword screen kept
316 dwarf-nova records mentioning prediction, memory, correlation, recurrence
or nonlinear dynamics, and I screened those by title and, where available,
abstract. Reproduce with `python3 -I scripts/literature/a01_citation_map.py
<outdir>`. The screened list, without abstracts because of publisher
copyright, is `docs/audits/a01/candidates_screened.csv`.

**Read.** Access depth for each source is in the Sources table at the end.

- **Full text** (reader subagents, using OCR for scanned pages): CM92 (Table 4
  read from the page image), Hempelmann & Kurths 1990 (two-column OCR,
  sections 1–4), Cannizzo & Mattei 1998, Cannizzo & Goodings 1988, Jevtic,
  Mattei & Schweitzer 2003, Price et al. 2007, Šimon 2018, Šimon 2022 and
  Ohshima 2023.
- **Full text, read by me:** Hameury 2020, the passages relevant here.
- **Abstract or metadata only:** Bath & van Paradijs 1983 (paywalled), Cannizzo
  1993, Grigorievskiy et al. 2014, Ak & Özkan 2007, Oppenheimer et al. 1998,
  Cannizzo et al. 2012 and Wheatley et al. 2003.
- **Not re-read this turn** (publisher pages blocked our automated access, or
  timed out): Ak et al. 2002 and Szkody & Mattei 1984. The seed records
  full-text sections for both, but I could not re-check them.

**Coverage limits.** There is no ADS API key on this machine, so the
astronomy-specific citation graph was not used. OpenAlex under-indexes
citations among 1980s–1990s papers, JAAVSO, IBVS and conference proceedings, and
Semantic Scholar rate-limited the cross-check. I did not search non-English
literature (Russian, Japanese, VSNET). Absence of a precedent here is weak
evidence of absence. One ADS pass with a key, plus library access to four
blocked items (section 9), would close most of the gap cheaply.

## 2. What is already known

| Claim | Precedent and what it actually did | Implication for this project |
|---|---|---|
| Duration predicts the following interval | Bath & van Paradijs 1983 (abstract): SS Cyg acts as a relaxation oscillator, with outburst energy correlated with the following waiting period. CM92 reproduced the duration–following-cycle r ≈ 0.49–0.52, but it reverses with the cycle convention: r = 0.475 following vs 0.145 preceding for onset-to-onset C, and 0.093 vs 0.521 for end-to-end cycles. | The famous relation is largely definitional. Cite CM92, not only Ak et al. 2002, for the shared-term warning. |
| Q-based relations in SS Cyg | CM92, N = 705 (1896–1992; AAVSO daily means; m_v = 10 crossings): r(D_i, Q_i) = 0.223, r(D_i, Q_{i−1}) = 0.282, r(Q_i, Q_{i+1}) = 0.382, r(C_i, C_{i+1}) = 0.349, r(D_i, D_{i+1}) = −0.400. "No significant" following/preceding difference. Moving-average energy and duration were not noticeably correlated with cycle time. | Gives a quantitative prior (section 3.2). Q is serially correlated, so a timing-only M2 has real signal to use. |
| Long/short outburst types | CM92: bimodal durations split at 12 d; sequences LS 134, LSS 69, LLS 21, LSSS 14, LLSS 8 (89% of outbursts). Hempelmann & Kurths: split at 11.5 d. Ak & Özkan 2007 (abstract): bimodal durations in Z Cam and AH Her. | Type is a first-order feature, and the threshold is a convention set at the dip between modes. |
| "Memory" in the outburst series | Hempelmann & Kurths 1990 (OCR full text): AR(4) on a symbolic width string; short-term dependence over at least three cycles and long-range memory over about ten. Quiescent intervals looked "like a random process" in return maps. No forecast. | The memory claim exists but was never tested as forecast skill. Their ten-cycle memory sets a minimum for M2's lookback. |
| Chaos / low-dimensional dynamics | Cannizzo & Goodings 1988: no attractor in 172 outbursts (1963–85). CM92: no strange attractor in cycle-time return maps. Jevtic et al. 2003: about a 52-year quasi-period in Poincaré return times; no prediction. George et al. 2015: gaps distort correlation-dimension estimates. | Deterministic-chaos framing is a dead end. Stochastic forecasting is the right register. |
| Long-term activity modulation | Price et al. 2007: 1,000–2,000 d quasi-periodic power correlates with the binned mean interval (r = −0.356). CM92: cycle time anticorrelated with quiescent magnitude in moving averages (about flux^−4). Cannizzo 1993: recurrence time correlated with the recent long/short ratio. | M2 must include activity states on these timescales, or M3 will beat a straw man. |
| Short-term precursors | Price et al. 2007: a two-season, nearly nightly V/Ic campaign found no SS Cyg pre-outburst signal (null; a marginal colour change was not claimed). They cite an unverified Hill & Waagen 2005 poster. | Different question: a precursor in quiescent photometry rather than information from the completed outburst. Cite as complementary. |
| Fluence does not set recurrence | Šimon 2018 (GK Per, CH UMa, Aql X-1) and Šimon 2022 (RU Peg), full text: qualitative statements that fluence, width or type do not change the current recurrence time T_C. No statistics. T_C is cycle-like and contains duration. | A prior negative claim, but not rigorous. Our test would be its first quantitative version. |
| Changing intervals before state changes | Ohshima 2023, six Z Cam-type stars (full text): two typical intervals per star; shorter intervals, brighter quiescence and loss of long outbursts before standstills. Oppenheimer et al. 1998 (abstract): Z Cam plateau-outburst cycle. | Confirms keeping Z Cam-types as a separate challenge set. |
| Explicit outburst forecasting | Grigorievskiy et al. 2014 (ITISE conference, abstract only): ML methods (OP-ELM, random forest, k-NN and others) forecast outburst positions for V363 Lyr with imputation; the better method depended on the forecast start. Design, metrics and data source unknown. | The only explicit forecasting precedent found. Cite it, obtain the full text, and do not overclaim novelty against it. |
| Physical models | Cannizzo 1993: DIM light curves with short outbursts between long ones; argued mass-transfer variations cannot directly explain SS Cyg's long-term changes. Hameury 2020: recurrence time ≈ viscous time for inside-out outbursts; DIM naturally yields long/short alternation; transfer fluctuations observed but not understood. | Physical framing in section 4. |

Two corrections to my own earlier statements on the board. SS Cyg's mean
onset interval is 49.2 ± 15.8 d over 703 outbursts (Price et al. 2007), so
"roughly 50 days" stands. And the long/short ratio–recurrence result belongs
to Cannizzo (1993), whose abstract I read, not to the NTRS record I pointed a
reader at. That record is CM92.

## 3. The additional claim this project could support

### 3.1 The claim and its boundaries

**Supportable:** for named, well-monitored ordinary dwarf novae, the information
in a completed outburst (type, then within-type duration) changes calibrated
probabilistic forecasts of the next onset by a measured amount. That amount is
expressed in log score, interval coverage and horizon-specific event
probabilities, relative to (a) a star-specific renewal baseline and (b) a
specified activity baseline. It is estimated with leakage-free issue times,
shared-endpoint uncertainty and an explicit observing-coverage rule. A precise
null with a bound is as reportable as a positive result.

**Not supportable from this design:**

- Discovering that outburst properties correlate with intervals (CM92 and
  earlier).
- Discovering long/short alternation, or memory in the descriptive sense
  (Hempelmann & Kurths).
- Showing that a completed outburst causes the next interval's length, or
  identifying disc memory versus transfer variability. That is H5, and it needs
  a joint mark–state model plus physical observables.
- Precursor detection (Price et al. 2007; Tsuranova et al. 2026).
- Any population-wide statement about dwarf novae.

The practical audience is real. Multiwavelength campaigns that must catch an
outburst from its optical rise depend on knowing roughly when it will start.
Wheatley et al. (2003) measured a 0.9–1.4 d X-ray lag after the optical onset
in SS Cyg. A calibrated "probability of onset within 7 days" is directly usable
for scheduling. Next-outburst *type* is a natural ancillary target with strong
signal, given r(D_i, D_{i+1}) = −0.40.

### 3.2 A prior effect size from published numbers

Take CM92's three linear-scale, in-sample correlations as given:
r(D_i, Q_i) = 0.223, r(D_i, Q_{i−1}) = 0.282 and r(Q_{i−1}, Q_i) = 0.382. The
partial correlation of duration with the following quiescent interval, given
the preceding one, is

r = (0.223 − 0.282 × 0.382) / √((1 − 0.282²)(1 − 0.382²)) ≈ **0.13**.

For a Gaussian predictive model, the expected log-score gain from a predictor
with partial correlation r is −½ log(1 − r²). That is **≈ 0.0085 nats per
forecast** for r = 0.13, and 0.026 nats for the raw r = 0.223. The expected
likelihood-ratio statistic after n forecasts is about n·(−log(1 − r²)). Reaching
an expected value of 8 (roughly p ≈ 0.005 for one parameter) takes about **470
forecasts** at r = 0.13, and about 160 at r = 0.223.

Caveats, all material:

- These are correlations of raw values, not of logs.
- They are in-sample and pooled across 96 years and both outburst types.
- The adjustment conditions only on Q_{i−1}, a one-lag timing baseline. A
  richer M2 (ten-cycle memory, 1,000–2,000 d modulation, the long/short ratio)
  would shrink the partial further.
- Shared end-time error biases r(D_i, Q_i) downward (section 6.3), and visual
  scatter attenuates every r, so the true signal could be somewhat larger.

Despite these caveats the order of magnitude is informative. It also changes
the design in three ways:

- **The locked block cannot carry detection for SS Cyg.** About 55 SS Cyg
  forecasts in 2018+ give an expected statistic of about 0.9 at r = 0.13. Its
  role is to confirm calibration and sign. It cannot detect an effect of this
  size by itself.
- **The pre-2018 record must provide the main estimate, under a frozen
  protocol.** SS Cyg has had roughly 900 outbursts since 1896. Fix the
  extraction rules and the M0–M3 specifications using only an early slice and
  simulations. Then run a single rolling-origin hindcast over the later
  pre-2018 decades without retuning. I propose tuning on 1896–1959 and
  evaluating 1960–2017. That gives about 400 forecasts, more if early eras
  prove usable. This is honest only if the split is recorded before anyone
  computes later-era event summaries. A rolling hindcast over data we have
  inspected is not an untouched test. A rolling hindcast on a slice we have
  not yet summarised, with no retuning, is close to one.
- **Gate D's "20% median change per doubling" example should be checked
  against this prior.** It should be translated into log-score units with
  development data rather than fixed in advance.

## 4. Physical framing: where "memory" could live

The disc instability model (DIM) gives the question physical content without
promising a unique mechanism. Hameury (2020) states that, except for
high-accretion-rate outside-in outbursts, the recurrence time equals the viscous
diffusion time. It is then independent of the accretion rate and inversely
proportional to the cold-state viscosity α_c. A quiescent interval is a refill
time, so it can depend on how much the preceding outburst drained the disc and
where the remaining mass sits.

The long/short dichotomy is the sharpest version of this. Cannizzo (1993)
tuned a limit-cycle code to SS Cyg's recurrence times and durations. Its light
curves place one or more short outbursts between long ones, with the
long-to-short ratio set by viscosity and transfer rate. He also found recurrence
time strongly correlated with the recent N(L)/N(S) ratio in moving averages of
the AAVSO record. On this picture the disc's surface-density profile is the
physical memory: short outbursts leave mass in the outer disc and long ones
drain it. CM92's alternation r(D_i, D_{i+1}) = −0.40 and the dominance of LS
and LSS sequences are the observable trace of that memory.

Two other routes produce history dependence without disc memory:

- **Variable mass transfer.** Hameury notes large, poorly understood transfer
  fluctuations. CM92 interpreted SS Cyg's long-term changes as transfer
  variations of about a factor of 2. Cannizzo (1993) argued transfer variations
  cannot directly produce them. That disagreement is unresolved.
- **Irradiation feedback.** Hameury's summary table lists irradiation of the
  secondary during U Gem's long outbursts. Raised transfer after a long
  outburst would shorten the next interval, which is the opposite sign to disc
  depletion.

The sign of any duration effect is therefore physically open, and both signs
carry content. One design consequence follows. In Cannizzo's picture the
long/short mix is itself an activity state correlated with recurrence, so the
completed outburst's type is partly a state indicator even under the DIM. That
is the M3-versus-M2 interpretive trap in physical form, and the reason the
mechanism question (H5) stays out of the first paper.

## 5. Sample audit

- **SS Cyg: the first and possibly only primary target for the first
  analysis.** The pre-2018 AAVSO record supports within-star estimation without
  pooling. Its known structure should be modelled, not excluded: long/short
  types, anomalous slow-rise outbursts (a separate class in CM92 and Price et
  al.), 1,000–2,000 d rate modulation, and the cycle-time–quiescent-magnitude
  relation. Cannizzo et al. (2012, abstract) found embedded precursors in long
  outbursts of SS Cyg and U Gem in high-fidelity digital photometry. The onset
  rule must therefore say whether a precursor starts the outburst. Coverage
  regimes differ by era: early Campbell means, publication gaps around
  1934–1940, which Hempelmann & Kurths split at, and growth in observations per
  daily mean (CM92). Era is a covariate or a stratum, not noise. The 2021
  anomaly is post-boundary.
- **U Gem: a secondary target.** Its long outbursts include superhump-bearing
  and precursor-bearing events (Smak & Waagen 2004 as cited by Hameury 2020;
  Cannizzo et al. 2012), and irradiation is flagged for them. Stratify long
  outbursts. Expect roughly half SS Cyg's cycle count per year.
- **RU Peg: a stress test, not a primary target.** Šimon 2022 found 52
  outbursts with T_C ≈ 90 d. It defines duration at 12.2 mag with A/B shape
  types; outbursts longer than 12–14 d mix types. There are candidate missed
  outbursts in dense data, and fluence is not related to T_C (qualitative). The
  cycle count is too small for individual M3-versus-M2 detection at the effect
  size in section 3.2. It is valuable for testing whether one extraction rule
  survives changing morphology.
- **SS Aur, BV Cen, UU Aql:** no event-sequence literature found. Their
  suitability is an A05 data question.
- **Z Cam-types (challenge set):** Ohshima 2023 and Oppenheimer et al. 1998
  confirm two typical intervals and pre-standstill drift. Keep them separate.
- **V363 Lyr** appears only as a forecasting precedent.

Implication: a single-star SS Cyg study is the realistic first paper. The other
pilots test generality and measurement, not the headline estimate. Expanding to
12–20 stars should wait until the SS Cyg result shows an effect worth
generalising.

## 6. Challenges to the definitions and protocol

### 6.1 Duration is a type label first

Regressing log Q on continuous log D across a bimodal duration distribution
mixes a between-type contrast with any within-type slope. Proposed M1 family,
fixed before evaluation:

- **M1a:** completed outburst type (long/short, with anomalous outbursts handled
  by a declared rule). The threshold is set from the duration distribution of
  the tuning slice only. CM92's 12 d at m_v = 10 is the historical reference.
- **M1b:** type plus within-type centred log duration.
- **M1c:** continuous log duration (the seed's M1), kept for comparison with
  earlier work.

A disc-motivated activity covariate available at issue time is the recent
long-outburst fraction, or the number of short outbursts since the last long
one. It belongs in M2, so M3's added value is information beyond the disc-state
proxy as well as beyond timing. Codex's point stands: bimodality alone does not
force a binary mark. M1b keeps continuous information while respecting the
modes.

### 6.2 Q is right, and CM92 already showed why

CM92's own table shows the cycle convention flipping the apparent
duration–interval asymmetry (section 2), and their Q-based correlations are
modest and nearly symmetric. Their published numbers should become the
historical anchor reproduction (A06). Using AAVSO daily means and m_v = 10
crossings over 1896–1992, reproduce Table 4 and document differences arising
from archive revisions. Agreement in signs and approximate magnitudes, especially
the −0.40 alternation, validates our extraction against a published standard
before any forecasting.

### 6.3 Shared endpoint error: bound it before modelling it

With an end-time error δ of variance σ_δ² shared by D and Q, the induced shift in
their correlation is approximately −σ_δ²/(σ_D σ_Q) when σ_δ is small relative to
both. It can be estimated from the double annotations of A04 before any
forecasting. Given the prior in section 3.2, I propose a per-target, per-era
criterion for Gate C: **the induced shift must be below 0.03, about a quarter of
the expected partial effect**. Otherwise propagate endpoint uncertainty
explicitly in the likelihood or restrict to eras where the criterion holds.
Illustration only: σ_δ = 1 d, σ_D = 4 d and σ_Q = 15 d give −0.017, which
passes. σ_δ = 2 d with σ_D = 3 d gives −0.09, which fails.

### 6.4 Issue time and confirmation delay

Onsets are sharp and watched for; ends are gradual. CM92 note that onset
coverage was sparse enough to preclude rise-time study in early eras, so
"sharp" is era-dependent too. The forecast issue time is the first moment the
end is confirmed by observations then available. The distribution of that
confirmation lag, measured per era, sets the landmark age a in the conditional
survival forecast. Price et al. required onsets at least 20 d after the
previous onset and dropped a poorly covered stretch because ignoring gaps
favours short intervals. That is the observation-process problem stated by an
earlier group, and a reason to adopt the seed's censor-at-coverage-loss rule
rather than discarding gaps.

### 6.5 A fair changing-activity baseline

M2 needs at least these, each computable from information available at issue
time:

- a discounted renewal fit;
- an autoregression on past log Q with a lookback of at least ten cycles
  (Hempelmann & Kurths);
- an activity state on the 1,000–2,000 d scale (Price et al.), such as a
  rolling mean of recent Q;
- the recent long-outburst fraction (Cannizzo 1993);
- the recent quiescent magnitude where it is measurable (CM92).

Select among these on the tuning slice only, and use the same state
architecture in M3, as the seed requires.

### 6.6 D012 and the prospective arm

I confirm D012 and Codex's five refinements: the date-restricted request,
preserving native time conventions, sealed counts, loader checks on row times,
boundary-crossing events left unresolved, and release logging. Two
consequences of section 3.2 belong in the eventual protocol (A10), not in
D012:

- The locked block's job for SS Cyg is calibration and sign confirmation.
- The prospective arm is worth starting as soon as Gate C passes. Its
  independence is self-evident, and it accumulates slowly: about 7 SS Cyg
  forecasts a year.

Codex is right that it does not by itself fix observation bias or sample size.

## 7. Smallest viable first analysis

One star, development era only, four steps, each with a stop rule fixed now.

| Step | Work (owner) | Pass | If it fails |
|---|---|---|---|
| 1. Acquire | Pre-2018 AAVSO SS Cyg, visual and V, through a date-restricted request under D012 (Codex, A03) | Raw bytes, hash, terms and time convention recorded | Report the access requirement and use another documented route |
| 2. Annotate | Two eras, about three seasons each (one visual-only before 1980, one 2010–2017 with CCD V). Blind double annotation with brackets, precursor rule and type (Claude + Codex, A04) | Section 6.3 shift < 0.03; type agreement ≥ 90%; confirmation-lag distribution measured | Restrict to passing eras, or propagate endpoints explicitly |
| 3. Anchor | Reproduce CM92 Table 4 on 1896–1992 with their conventions (A06, implementer and reviewer rotate) | Signs and approximate magnitudes reproduced (alternation near −0.4; Q-based r in 0.15–0.35) | Reconcile definitions before any forecasting; a failure here means our extraction differs from the published standard |
| 4. Frozen hindcast | Freeze extraction and M0, M1a–c, M2 and M3 on 1896–1959 plus simulations. Run one rolling-origin hindcast over 1960–2017 with paired log scores, horizon probabilities and coverage | Effect estimate with uncertainty from a block bootstrap by decade | A gain consistent with zero and a CI excluding about 0.01 nats is a useful bound and a paper. A CI spanning both is underpowered: add stars or eras before claiming anything |

Steps 2 and 3 can run in parallel once step 1 exists. None of them touches the
2018+ block.

## 8. Recommendations

1. **Record the tuning/evaluation split inside development** (1896–1959 tune,
   1960–2017 frozen hindcast, proposed) as D013 before A03 computes any event
   summaries. Codex to accept or amend. *Both.*
2. **Specify M1 as the M1a/M1b/M1c family**, and move the long-outburst fraction
   into the M2 candidate set. Update `docs/05-statistical-design.md` when agreed.
   *Claude drafts; Codex reviews.*
3. **Adopt the section 6.3 criterion for Gate C** in place of the generic
   precision requirement. *Both.*
4. **Make CM92 Table 4 the A06 anchor reproduction.** *Rotating.*
5. **Correct the literature review.** CM92 is the origin of the shared-term
   warning; add Price et al. 2007, Cannizzo 1993, Grigorievskiy et al. 2014,
   Jevtic et al. 2003, Ohshima 2023, Šimon 2018 and Cannizzo et al. 2012.
   New identifiers for Barry's Zotero import are in
   `references/a01-new-identifiers.txt`. *Claude, this turn: note added to the
   review; bibliography import awaits Barry's Zotero step.*
6. **Add next-outburst type as a secondary forecast target**, labelled
   exploratory until frozen. *Proposal.*
7. **Close the search gaps** in section 9 when access allows.

## 9. Unresolved questions

- **Grigorievskiy et al. 2014 full text:** data source, target, validation
  design and metrics. It is the only explicit forecasting precedent, and its
  rigour sets how carefully we phrase novelty.
- **Ak et al. 2002 and Szkody & Mattei 1984 full texts** (blocked this turn),
  and the 1995 conference paper "Detecting correlations in the light curves of
  dwarf novae", whose authors were not identified.
- **Bath & van Paradijs 1983 full text:** whether their "quiescent waiting
  period" was Q or a cycle. CM92 treats it as a cycle containing the outburst.
- **An ADS forward-citation pass** for CM92, Hempelmann & Kurths and Price et
  al., plus JAAVSO, IBVS and VSNET coverage.
- **The Hill & Waagen 2005 pre-outburst brightening poster**, cited only via
  Price et al.
- **Whether the Q serial correlation (0.38) reflects slow activity drift or
  type alternation.** The answer decides which M2 component matters most, and
  the tuning slice can settle it.

## Sources

Access depth: F = full text read (subagent unless marked), S = relevant sections
or OCR with gaps, A = abstract or metadata only.

| Source | Identifier | Access |
|---|---|---|
| Bath & van Paradijs 1983, Nature 305, 33 | 10.1038/305033a0 | A |
| Cannizzo & Goodings 1988, ApJ 334, L31 | 10.1086/185306 | F |
| Hempelmann & Kurths 1990, A&A 232, 356 | ADS 1990A&A...232..356H | S (OCR) |
| Cannizzo & Mattei 1992, ApJ 401, 642 | 10.1086/172092 | F (OCR; Table 4 from page image) |
| Cannizzo 1993, ApJ 419, 318 | 10.1086/173486 | A (read by Claude) |
| Cannizzo & Mattei 1998, ApJ 505, 344 | 10.1086/306165 | F |
| Jevtic, Mattei & Schweitzer 2003, JAAVSO 31, 138 | ADS 2003JAVSO..31..138J | S (OCR) |
| Wheatley, Mauche & Mattei 2003, MNRAS 345, 49 | 10.1046/j.1365-8711.2003.06936.x | A (read by Claude) |
| Ak & Özkan 2007, JAAVSO 35, 144 | JAAVSO abstract | A |
| Oppenheimer, Kenyon & Mattei 1998, AJ 115, 1175 | 10.1086/300250 | A |
| Price et al. 2007, PASP 119, 1361 | 10.1086/524413; arXiv:0710.2937 | F |
| Cannizzo et al. 2012, ApJ 757, 174 | 10.1088/0004-637X/757/2/174 | A (read by Claude) |
| Grigorievskiy et al. 2014, ITISE 2014, vol. 2, 520–531 | conference proceedings | A |
| Šimon 2018, PoS(GOLDEN2017)035 | 10.22323/1.315.0035 | F |
| Hameury 2020, Adv. Space Res. 66, 1004 | 10.1016/j.asr.2019.10.022 | S (read by Claude) |
| Šimon 2022, MNRAS 510, 3430 | 10.1093/mnras/stab3577 | F |
| Ohshima 2023, arXiv:2301.08579 | arXiv:2301.08579 | F |
