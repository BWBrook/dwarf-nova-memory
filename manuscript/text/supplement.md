# Supplement: methods, sensitivities and correction record

**Draft for review, 9 November 2026.**
<div id="authors"></div>

This supplement gives the machinery behind the article. Every quoted number is bound to the claims
ledger, `manuscript/claims.csv`. The interpretation specification, `manuscript/estimands.md`,
states what each analysis bounds and which phrasings are not allowed. Section and decision labels
(A04, A10, D018 and so on) refer to the project record in `docs/` and `coordination/decisions.md`.

## S1. Definitions, readings and units

| Term | Meaning |
|---|---|
| Issuance | One forecast, issued when the observation-time rule first confirms that an outburst has ended |
| Duration | Onset-to-end time of the completed outburst, from X4 run on the 400 days before issue |
| Quiet gap | End of one outburst to onset of the next; the forecast target |
| Previous-gap predictor, $q$ | Standardised log of the preceding quiet gap, used only if covered (no visit gap over seven days) |
| Recent-level predictor, $L$ | Standardised mean of up to six earlier covered log quiet gaps; zero after standardisation if none |
| Onset bracket | X4's retrospective interval for the next onset; scoring evidence only |
| Right censoring | The forecast ends at coverage loss, the next issuance, or the block end before an onset is established |
| Log score | Natural log of the probability the forecast gave to the observed bracket (or to survival, if censored), conditional on survival to issue; units are nats |
| Paired gain | M3's log score minus M2's for the same issuance |
| Geometric mean likelihood ratio | exp(mean paired gain); a [1.7]{.C02}% increase for the primary |
| Working clock scale | The median of the untruncated lognormal clock; ratios of scales are model quantities, not observed mean waits |
| Partial-identification bounds | The smallest and largest coverage consistent with bracketed or censored outcomes |

Times are Julian Dates as returned by the archive, without conversion. Durations and gaps are in
days. Log durations are standardised by the frozen development centre and scale.

## S2. Methods

### S2.1 Observations and extraction

Rows were requested in bounded annual windows, ending strictly before 2018. Responses near the
50,000-row service cap were bisected, and every response was hashed on receipt before parsing. The
analysis uses rows in the `Vis.` band with validation flag `V`. The 1960–2017 evaluation window
contains [63]{.C15} validated leaf responses. These hold [500,479]{.C15} rows after removing
[81]{.C15} duplicate identifiers, of which [249,356]{.C15} meet the analysis selector[]{.C15}.

X4 (`src/dnmem/extract_x4.py`, definition `a04f-x4-v1`) groups observer visits into candidate
episodes brighter than visual magnitude 10. For each episode it forms a posterior for the
brightening and fading threshold crossings, using a slope mixture over nearby estimates plus a
shared 0.05-mag systematic level error. That error stops intervals narrowing as the inverse square
root of the number of observers, which caused undercoverage in its predecessor. An episode is
confirmed by bright reports from two distinct observers, or from one observer on at least two
nights with a margin past the threshold and no contradicting faint report. The observation-time
confirmation rule arms only on bright evidence at least 0.5 mag past the threshold, so noise near
the threshold in a decline cannot re-arm it.

Three earlier extractors, X1 to X3, failed qualification. X4 passed a synthetic screen at magnitude
10 on the qualified phase-aligned cadence family, and the C1/7 d coverage rule was selected there.
The unseen waveform family failed benchmark qualification before X4 recovery was scored;
X4 recovery on that family was not tested. Magnitude-9.5 diagnostics failed in later eras. Those
failures are retained (A04e–A04i). The evaluation is therefore conditional on the magnitude-10
X4 extraction.

### S2.2 Issuance and predictors

Each observation-time end confirmation issues one forecast at its emission time. A two-day reporting
delay is a sensitivity. Every emission is kept, including false and repeat emissions. Predictors come
from X4 run on the rows in the 400 days up to the emission and on nothing else. A unit test inserts
poisoned rows after the emission and checks that no ledger field changes. The current episode is
the last prefix episode whose end bracket reaches the emission's bright evidence. A duration of zero
or less makes the mark unavailable; nothing is clipped. The previous gap requires the previous
episode to begin more than 30 days inside the window.

### S2.3 Outcomes and censoring

The outcome is the next onset found by retrospective X4 run up to an explicit cutoff. An onset
bracket that straddles issue does not establish survival, and that forecast is excluded under the
frozen rule. Here none were excluded. A forecast is scored on the onset interval if the interval is
established before the first of these events:

- coverage loss, the first visit gap longer than seven days after issue;
- supersession by the next issuance;
- the end of the block.

Otherwise the forecast is right-censored at the earliest of these events.

### S2.4 Models and likelihood

Each model is a lognormal clock for the quiet gap $Q$ after a known end $e$, with log-location
$\mu$ and log-standard deviation $\sigma$:

- M0: $\mu = \alpha$;
- M2: $\mu = \alpha + \gamma_1 q + \gamma_2 L$;
- M3: $\mu = \alpha + \gamma_1 q + \gamma_2 L + \beta x$, with $\beta \ge 0$.

Here $q = (\log Q_{\mathrm{prev}} - c_q)/s_q$. If $\ell$ is the mean of up to six earlier covered
log quiet gaps, $L = (\ell - c_L)/s_L$; set $L = 0$ if none are available. The centres and scales
are frozen development means and standard deviations. Likewise, $x$ is the standardised log
duration. At issue age $a$, an onset bracket $(l, u]$ scores
$\log P(l - e < Q \le u - e) - \log S(a)$. A censoring time $c$ scores $\log S(c - e) - \log S(a)$,
where $S$ is the survival function. Forecasts without a covered previous gap use M0 in both
models, and forecasts without a known end use a common remaining-wait forecast. Both contribute
exactly zero to the contrast.

M2 was fitted on timing-eligible 1910–1959 rows and frozen. The duration offset was then fitted on
rows with a valid mark, with M2 held fixed, so that $\beta = 0$ reproduces M2 exactly (D021).
Frozen values (C04): $\beta$ = [0.046597]{.C04} per standard deviation of log duration; previous-gap
slope [0.078016]{.C04}; recent-level slope [0.051336]{.C04}; $\sigma$ = [0.34636]{.C04}. The
parameter file's SHA-256 begins `ce4ef8d5`.

The constraint $\beta \ge 0$ and matched routing respond to a measurement coupling. The duration
and the following gap share the estimated end time, so end-time error couples them. In earlier
synthetic work that coupling pushed fitted null coefficients negative (D020). Codex then showed
that a nonnegative bound is a restriction of direction, not a theorem about the sign of the error.
An exact construction with constant true duration can yield positive information (D021). Endpoint
coupling therefore remains a stated limit. The uniform-end and two-day-delay sensitivities probe
it only partly.

### S2.5 Primary statistic and inference

The statistic is the mean paired gain over all score-eligible issuances with issue times in
JD 2436934.5 to 2458119.5. The standard error is cluster-robust, over consecutive clusters of
$6 \times 365.25$ days anchored at the window start, with the factor $G/(G-1)$ for $G$ nonempty clusters.
Inference uses Student's t with $G - 1$ degrees of freedom. The result counts as confirmed if the
one-sided 95% lower bound exceeds zero. The cluster length was chosen before any operating
characteristics were seen (D021). There is one confirmatory statistic. No subset, era, variant or
interval width may replace it.

### S2.6 Operating characteristics

Before the development fit, a finite synthetic screen checked the design (A10d). At an effect sized
to CM92's published correlations, [11]{.C30} of [40]{.C30} simulated evaluations confirmed, with exact
interval [0.146]{.C30} to [0.439]{.C30}[]{.C30}. Pooled no-effect histories gave [3]{.C31}
confirmations in [220]{.C31}. These histories share random streams, so the count is a finite
screen, not an independent error rate or a certified size. The reference injected effect gave a
mean gain of [0.0045]{.C33} nats[]{.C33}. Barry accepted the finite screen before the first real
fit (D022).

### S2.7 Access, execution and repair

| Stage (8 November 2026, UTC) | Time |
|---|---|
| Protocol published (DOI 10.5281/zenodo.24053338) | 12:34:47 |
| First attempt began; failed before any ledger or score | 12:38:28; 12:39:51 |
| Repaired acquisition began | 12:51:18 |
| Candidate and reference ledger concordance passed | 13:06:58.627 |
| Primary result written | 13:06:58.641 |

The first attempt failed when the archive's literal `uncert="None"` token for missing uncertainty
reached a strict parser. Uncertainty enters no extraction, feature, evidence, routing or score path.
The repair accepts that exact token without changing or dropping any row. Synthetic invariance
tests, independent review, the full test suite, a new full rehearsal and supported-platform CI
passed before continuation (D026). All 26 original forecasting source files, the parameter bytes
and the protocol bytes are unchanged. The repair freeze is `5e39aeb` and the execution commit
`d7151e0`. No person or agent inspected real scores, outcomes, counts or coverage summaries before
the primary file existed[]{.C05}.

Two independent ledger and evidence implementations had to agree exactly at both delays before any
score. A separate checker reproduced all 2,641 variant score rows, with a maximum discrepancy of
order $10^{-13}$, and the primary interval[]{.C01}. Claude recomputed the interval by a separate
route[]{.C01}. The primary population and routing are in C03.

## S3. Results and sensitivities

### S3.1 Primary, eras, class rule and sensitivities

**Table S1.** Frozen comparisons, mean paired log-score gain (nats per issuance) and 90% cluster
interval. Only the first row is confirmatory.

| Comparison | Issuances | Gain | Interval |
|---|---:|---:|---|
| Primary, M3 − M2, 1960–2017 | [441]{.C01 .V004} | [0.0165]{.C01 .V001} | [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003} |
| Segment 1960–1992 | [261]{.C06} | [0.0240]{.C06} | [0.0091]{.C06} to [0.0389]{.C06} |
| Segment 1993–2017 | [180]{.C07} | [0.0057]{.C07} | [−0.0107]{.C07} to [0.0221]{.C07} |
| 12-day class and within-class rule | 441 | [0.0025]{.C08} | [−0.0022]{.C08} to [0.0072]{.C08} |
| Uniform-end marks | 441 | [0.0166]{.C09} | lower [0.0044]{.C09} |
| Previous-gap-only baseline | 441 | [0.0170]{.C09} | lower [0.0054]{.C09} |
| Two-day issue delay | 441 | [0.0165]{.C09} | lower [0.0049]{.C09} |
| Joint-valid rows | 436 | [0.0167]{.C09} | lower [0.0049]{.C09} |
| Three-year clusters | 441 | as primary | lower [0.0059]{.C09} |
| Baseline M2 − M0 | 441 | [0.1168]{.C10} | [0.0663]{.C10} to [0.1672]{.C10} |

The primary interval uses ten nonempty blocks and nine degrees of freedom[]{.C01}. Eight have positive means. Leave-one-block-out means span [0.0132]{.C25} to
[0.0194]{.C25}, and [0.5397]{.C25} of individual issuance gains are positive. Holding the estimate,
critical value and blocks fixed, the strict failure boundary is approximately
[1.42705]{.C25} times the reported standard error. A 42% inflation passes and an exact 43%
fails. None of these checks validates the cluster dependence assumption.

The frozen P3 placebo equals M2, because its development lag coefficient sat at its bound of zero.
The planned memory placebo therefore carries no information.

### S3.2 Calibration

M3's nominal 50% central intervals covered between [0.546]{.C11} and [0.617]{.C11} of outcomes;
its nominal 90% intervals between [0.923]{.C11} and [0.980]{.C11}[]{.C11}. Each range runs from
definitely covered to possibly covered, given the extracted brackets and censoring, over all scored
issuances. These are realised-sample bounds, not confidence intervals for a population rate, and
they show overcoverage. Mid-CDF deciles of resolved onsets are descriptive; no uniformity test is
claimed.

### S3.3 Evaluation-only offsets

Duration offsets were fitted to the evaluation outcomes with an evaluation-refitted M2 held fixed.
The support intervals use a likelihood-ratio cutoff of 3.841, with no dependence or measurement
calibration.

| Offset | Estimate | Conditional support |
|---|---:|---|
| Current duration, separate | [0.04209]{.C12} | [0.01574]{.C12} to [0.06845]{.C12} |
| Previous duration, separate | [−0.03836]{.C12} | [−0.06489]{.C12} to [−0.01184]{.C12} |
| Current duration, joint | [0.03045]{.C13} | [−0.00063]{.C13} to [0.06152]{.C13} |
| Previous duration, joint | [−0.02213]{.C13} | [−0.05340]{.C13} to [0.00913]{.C13} |

The joint design is correlated but has full rank, with condition number [1.79]{.C13}[]{.C13}. Both
joint support intervals include zero. Correlation alone neither explains that nor makes the
coefficients nonidentifiable.

### S3.4 A slow component can hide behind negative lag signs

Negative lag signs alone cannot exclude a dominant slow driver (A10k). Take independent
unit-variance AR(1) components $S$ and $A$, with persistence 0.95 and −0.9, and set log duration
$= 0.175S + 0.350A$ and log gap $= 0.300S + 0.001A$. The lag-one duration correlation is then about
−0.53, and the lag coefficient conditional on the preceding gap is negative. Yet $S$ dominates gap
variation and the current conditional covariance. This construction is a logical counterexample, not
fitted to SS Cyg and not a rival empirical result.

### S3.5 Exploratory post-result calculations

Everything in this subsection reuses the evaluation outcomes. Each interval conditions on the fitted
adjustment it describes. None supplies a further held-out confirmation.

- **Level shift and recentring (C20).** The best common M2 log-location shift is [−0.04679]{.C20}.
  It reduces the original untruncated clock scale by about 4.57%. The frozen duration term implies a
  level shift of [−0.01108]{.C20}, because the evaluation mean standardised log duration is
  [−0.2379]{.C20}. Shifting M2 by that implied amount accounts for [0.00370]{.C20} nats
  ([0.00013]{.C20} to [0.00726]{.C20}). The contrast after recentring the duration at its evaluation
  mean is [0.01283]{.C20} ([0.00359]{.C20} to [0.02206]{.C20}). With both models at the best M2
  level, the gain is [0.01239]{.C20} ([0.00098]{.C20} to [0.02381]{.C20}). The two orderings of the
  split differ by about 0.000012 nats.
- **Class versus continuous duration (C21).** With M2's historical parameters fixed and a free
  common level, the evaluation likelihood-ratio comparisons are as follows:
  - class versus level only, [14.7]{.C21 .V005};
  - continuous log duration versus level only, [11.7]{.C21 .V006};
  - within-class duration added to class, [0.17]{.C21 .V007}.

  The class contrast corresponds to a [14]{.C21 .V008}% larger untruncated working-clock scale after
  long outbursts. In 1910–1959 the class and continuous fits were similar, with a smaller contrast[]{.C21}.
- **Shared level for the class rule (C22).** The frozen class-plus-within rule's mean offset is
  [0.01728]{.C22}. Giving both rules M2's evaluation-fitted level yields a gain of [0.00905]{.C22}
  ([0.00409]{.C22} to [0.01401]{.C22}). For 1993–2017 alone it yields [0.00761]{.C22}
  ([−0.00631]{.C22} to [0.02153]{.C22}). The uncentred type component cannot shorten short-outburst
  forecasts, but the full frozen rule does shorten [181]{.C22} of [245]{.C22} of them through its within-class term.
- **Era refits (C23).** The class contrast is [0.16323]{.C23} (statistic [13.504]{.C23}) in
  1960–1992 and [0.07828]{.C23} ([2.262]{.C23}) in 1993–2017. These are descriptive; there is no
  test of change.
- **Alternation (C24).** Across forecast-record pairs, the lag-one correlation of log duration is
  [−0.5233]{.C24} in the evaluation years and [−0.4006]{.C24} in the development years. A long
  outburst followed a long one in [0.1495]{.C24} of pairs and a short one in [0.6640]{.C24}. The
  pairs include one repeat-flagged record and are not a catalogue of unique consecutive outbursts.

### S3.6 Development fit

In 1910–1959 the duration offset was [0.0466]{.C14} per standard deviation, with likelihood-ratio
statistic [5.1935]{.C14} against M2[]{.C14}. This fit is in-sample and overlaps CM92's record, so it
is not evidence for the claim.

### S3.7 Prior art checked against the source

Claude re-read CM92's Table 4 and its Fig. 5 subscript conventions on the original scan
[@cannizzo1992LongtermBehaviorSS] []{.C40}.
For [705]{.C40} outbursts (1896–1992), the correlations are:

- duration with the following quiescence, [0.223]{.C40};
- duration with the preceding quiescence, [0.282]{.C40};
- successive durations, [−0.400]{.C40}.

Durations split at [12]{.C40} days, with [401]{.C40} shorter and [304]{.C40} longer. The correlation of duration
with the following onset-to-onset cycle is [0.475]{.C40}, against [0.145]{.C40} with the preceding cycle. For
end-to-end cycles the pattern reverses, at [0.093]{.C40} and [0.521]{.C40}. The famous relation is therefore
largely definitional, as CM92 showed.

### S3.8 Bounded independent novelty check

An independent search in A10m found no prior preregistered probabilistic held-out recurrence
evaluation, or explicit held-out comparison of duration beyond a timing-history baseline, among
the studies located and checked. This supports a bounded "to our knowledge" statement, not proof
of universal priority. The exact queries and source receipts are in
`data/provenance/a10m_novelty/`; the appraisal is
`docs/audits/2026-11-09-a10m-novelty-review.md`.

The closest precedent, [Grigorievskiy et al. (2014)](https://research.cs.aalto.fi/aml/Publications/Publication216.pdf),
uses chronological training, validation and test sets, with one test outburst of V363 Lyr. It
scores point-onset errors; no preregistration or scored predictive onset distribution is reported.
No explicit duration-addition comparison against a common timing baseline is reported. Repeated
random fits do not make the evaluated forecast a probability distribution. The independent
search included an OpenAlex citing-title screen and primary-source checks of this study and
@price2007SSCygniOutburst. ADS access failed; observer/non-English coverage is incomplete, and some
full texts, including Tsuranova et al. (2026), remain inaccessible. Their unverified methods are
not treated as exclusions. []{.C41}

## S4. Analyses superseded during review

Each entry records what was replaced, who found the problem, and where the record is.

| Earlier analysis or statement | Problem and finder | Replacement | Record |
|---|---|---|---|
| Duration predicts the following onset-to-onset cycle | Shared term with the cycle (CM92); confirmed in the A01 audit | Quiet-gap target only | A01 memo |
| Extractors X1, X2, X3 | Failed synthetic qualification (Codex and Claude reviews) | X4, qualified at magnitude 10 only | A04e–A04i |
| Unrestricted duration coefficient on all routes | End-time coupling and route mixing (Claude, D020) | $\beta \ge 0$, matched routing, local gap level | D020, D021 |
| Joint refit of M3 with M2 | Training loss not matched to deployment (Codex, D021) | Mark offsets fitted with M2 fixed | D021 |
| Candidate-authority concordance rule | Allowed mismatch deletion (Codex, D024) | Exact two-implementation concordance or abort | D024 |
| Strict parser for the uncertainty field | Failed on `None` after access (execution) | Exact-token repair, reviewed and rehearsed | D026 |

**Interpretation corrections checked in A10k.** Codex's independent audit narrowed several readings
from Claude's A10j review before the products were drafted. Claude accepted all of them (D030).

| Earlier reading | Corrected scope | Evidence |
|---|---|---|
| Global recentering isolates drift-free information | It defines an approximately additive descriptive score contrast; within-period drift remains possible |[]{.C20} |
| All predictive information is in outburst type | A class indicator has greater in-sample likelihood; within-class equivalence was not tested |[]{.C21} |
| The entire frozen class rule cannot shorten short-event forecasts | That restriction concerns its type component; the within-class component can shorten them |[]{.C08}[]{.C22} |
| Negative lag excludes a dominant slow driver | Alternation and a slow component can coexist; no mechanism allocation follows |[]{.C12}[]{.C13}[]{.C24} |
| A rounded SE boundary is a safe inclusive margin | The decision is strict; the rescaling boundary is exclusive and does not validate dependence |[]{.C25} |
| Frozen M2 forecasts are 4.6% too long | The best level shift reduces the untruncated clock scale by 4.57%; that is not a remaining-wait bias |[]{.C20} |
| The gap after a long outburst is about five days longer | A 14% clock-scale ratio; days need an explicitly chosen reference scale |[]{.C21} |

The original exploratory numbers are retained. These corrections do not alter the frozen primary
comparison, its outcomes or the predeclared class-rule result.

**Novelty wording narrowed in A10l.** The draft framing called this the first preregistered held-out
forecast test of dwarf-nova recurrence. The refreshed search found a held-out point-forecast study
of V363 Lyr by Grigorievskiy and colleagues, in the 2014 ITISE proceedings (pp. 520–531), with a single test
outburst. The claim now specifies preregistered, probabilistic and duration-based[]{.C41}.

**Draft corrections in A10m.** Semantic review corrected an overstatement of complete flare
recovery, distinguished an unseen-waveform qualification failure from unperformed X4 recovery,
defined the standardised timing predictors, and gave the within-class likelihood statistic its
proper class-model reference. The article's assumptions table now states calculated results and
current limits rather than attributing information exclusively to class or physical disc state.
The uniform-end lower bound is rounded directly from the full-precision evidence, and the SE
failure boundary is explicitly approximate when printed. Reproduction commands preserve committed
evidence and state their retained-input dependencies. The primary comparison is unchanged.

## S5. Reproduction and navigation

From the repository root, without new archive requests:

These public-only checks use the committed aggregates and figure assets:

```sh
python3 manuscript/figures.py --check
make -C manuscript check
make -C manuscript
```

Recomputing scores and exploratory fits requires the retained inputs outside Git. The saved-score
checker needs the completed evaluation run. The three subsequent analyses also need the retained
1910–1959 development inputs. Outputs below go to scratch paths; committed evidence is preserved.

```sh
python3 scripts/check_a10g_evaluation.py \
  --directory outputs/a10h_live_repair_5e39aeb \
  --output outputs/a10m_reproduction/score_audit.json
uv run --frozen --extra analysis \
  python scripts/a10j_postresult_review.py \
  --output outputs/a10m_reproduction/a10j_summary.json
uv run --frozen --extra analysis \
  python scripts/a10k_exploratory_audit.py
uv run --frozen --extra analysis \
  python scripts/a10k_secondary_audit.py
```

The retained run includes raw archive replies, observer identities and per-issuance scores. Its
archive SHA-256 and manifest are in `data/provenance/a10i_evaluation_1960_2017/archive.json`.
The committed aggregates support the ledger values, but do not replace these inputs for a full
recomputation. The published protocol is at <https://doi.org/10.5281/zenodo.24053338>.

Navigation:

- `manuscript/claims.csv`: every claim, with its status, evidence, commit, reproduction command and
  limits.
- `manuscript/estimands.md`: allowed and forbidden readings.
- `coordination/decisions.md`: D013–D030.
- `docs/audits/`: every review, including A10i (the result), A10j (Claude's review), A10k (Codex's
  audit) and A10l (sources and drafts).
- `docs/outcome-access-ledger.md`: who saw which outcomes, and when.
- `manuscript/text/for-agents.md`: the agent guide.

## References
