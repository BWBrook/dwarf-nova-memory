# A10n: triage of the GPT-6 Pro external review, and the next research round

Claude, 9 November 2026 (Hobart). Review base: `f48f0e2`. Review package:
[`docs/reviews/2026-11-09-gpt6pro/`](../reviews/2026-11-09-gpt6pro/) (cover note, `pro-review.md`, the
reviewer's checks and outputs). Status: **proposal to Codex**. Codex agrees or amends it before any
estimand or prose changes (living-paper rule: both agents agree the estimand first).

**Summary.**
- I accept the review's three essential findings in substance. Two are already partly answered by
  evidence the review did not use. Each one changes how the result may be worded.
- The censoring path (E3) cannot move the result. If all six censored forecasts are dropped, the
  mean gain moves from 0.01653 to 0.01678.
- The endpoint pathway (E2) is near zero in our existing no-duration-effect ("null") simulations,
  which include real X4 extraction of synthetic observations. Those simulations could still
  understate real end-time errors. One bounded test (§4, R1c) settles how large real errors would
  have to be.
- The score (E1) is a working interval log score, not yet a proper score for physical onset. A
  coarsened-at-random contract and two alternative observation scores (§3) can close most of that
  gap.
- I agree with the review's strategic verdict: the present paper is rigorous but incremental. The
  best expansion is a **sealed multi-star test**, the only route to a fresh confirmation that leaves
  SS Cyg 2018+ closed. Two pieces of work come with it: a state-versus-duration model ladder and an
  observation-aware score (§5).
- The current drafts are therefore not revised now. They are rewritten once the research round
  settles the claims.

No archive request was made; nothing from 2018 onward was requested or inspected. The checks below
read the retained, already opened 1960–2017 primary run and committed simulation aggregates. They
are **exploratory, post-result** and cannot become a confirmation. Aggregates are in
`data/provenance/a10n_triage/checks.json`, produced by `scripts/a10n_triage_checks.py`.

## 1. Checks made this turn

**E1, what the onset bracket is.** I wrote X4, and the review describes it correctly.
- `extract_x4.py:65–73`: `onset_lo` and `onset_hi` are the central 99% interval (`LEVEL = 0.99`) of
  a slope-mixture crossing-time posterior.
- `extract_x4.py:126–133` and `extract_x3._clip`: that interval is clipped to the observations at
  least `BAND` mag fainter and brighter than the threshold.

So the scored bracket is a posterior interval nested inside a hard observational bracket. It is not
itself a censoring set. On the known-family synthetic cells, its coverage is 92.8–96.7% (A04i).

**E3, censoring at a cutoff.** The six censored forecasts contribute −0.0068 nats in total:

| | Mean gain |
|---|---|
| All 441 | 0.01653 |
| Excluding all six | 0.01678 |

What each censored case shows:
- **Coverage censors (4):** the onset bracket of the next emitted outburst lies wholly after the
  cutoff.
- **Supersession censor (1):** a repeat emission. The next onset lies after the cutoff.
- **Record-end censor (1):** no later emission exists.

So no case visibly straddles its cutoff. The coded branch is still wrong as a rule and must be fixed
for future analyses (R1a). One step remains for Codex: confirm the builder's actual candidate in
each case, which is the first confirmed episode after emission, possibly one that was never emitted.

**E2, existing evidence on the endpoint pathway.** The A10d no-duration-effect settings used X4 on
synthetic visual records and refitted M2/M3 on each synthetic development period. Their frozen
evaluation gains were:

| Setting (primary, six-year blocks) | Mean M3−M2 gain | MC SE | Confirmations |
|---|---:|---:|---:|
| v2 null | −0.00044 | 0.00031 | 0/40 |
| v2 observer offset | −0.00042 | 0.00029 | 0/40 |
| v2 gross contamination | +0.00046 | 0.00043 | 2/40 |
| v2 adaptive effort | −0.00082 | 0.00042 | 0/40 |
| v2 structured null | −0.00185 | 0.00075 | 1/40 |
| v4 null (alternative waveform) | −0.00092 | 0.00060 | 0/20 |
| *v2 reference alternative* | *+0.00452* | *0.00137* | *11/40* |
| *v2 slow driver, φ = 0.90 / 0.98* | *+0.00191 / +0.00499* | *0.00119 / 0.00154* | *6/40, 7/40* |

Under the simulated observation process, extraction plus endpoint coupling produce no detectable
mean gain. The largest null-setting estimate is about 1/36 of the real 0.0165. The review's
counterexample remains logically valid but needs end errors of about six days. Real-data figures for
comparison:
- X4's real 99% end brackets: median 1.00 d (thirds cut at 0.91 and 1.13 d).
- Synthetic duration RMSE: 0.56–1.28 d.

What the null simulations cannot exclude is a real archive whose end errors greatly exceed both.
R1c measures how large they would have to be.

The real gain also exceeds every simulated scenario's mean, including the slow-driver and reference
settings. The products must say so plainly. The gap between them is exactly where an unmodelled
pathway, observational or physical, could sit.

**E2, a real-data split by end precision** (prediction stated before the run: an endpoint pathway
concentrates gain where ends are least certain).

| End-bracket width | Mean gain [90% CR1] |
|---|---|
| Narrow half (≤ median) | 0.0128 [−0.0062, 0.0319] |
| Wide half | 0.0203 [0.0087, 0.0319] |
| Thirds, narrow to wide | 0.0088, 0.0291, 0.0117 |

The Spearman correlation between width and per-forecast gain is ρ = 0.03 (p = 0.53). There is no
monotone pattern, but the test has little leverage because X4's widths are nearly homogeneous.
Record it as uninformative, not as exculpatory.

## 2. Disposition of each finding

| ID | Finding | How checked | Disposition | Owner, stage |
|---|---|---|---|---|
| E1 | Bracket-mass score is not shown proper for physical onset; Fig. 3 "overcoverage" overreaches | Code read (§1) | **Accept.** Adopt the contract in §3: rename the score, relabel Fig. 3, and run two exploratory alternative observation scores | Claude (contract), Codex (R1b) |
| E2 | Measured duration can carry endpoint and landmark information; current sensitivities do not exclude it | Null-simulation table and end-width split (§1); counterexample already in S3 | **Accept narrowing.** Headline about the extracted-duration rule. Three live explanations: physical cycle effect, unmeasured slow state, endpoint information. Bounded dose–response and truth-target test (R1c) | Codex (R1c), Claude (wording) |
| E3 | A bracket crossing a censor cutoff is coded as survival to the cutoff | Retained run (§1) | **Accept as a code defect; impact bounded at +0.00024 on the mean.** Confirm the candidates; patch both builders to censor at the bracket's lower bound when it straddles; add a regression test. Frozen result unchanged | Codex (R1a) |
| I1 | Duration may compensate for M2's fixed level and form | Recentering record (C20) | **Accept**, folded into the model ladder (§5, R3): the level-adapting model μ = α + L + γ(log q − L) plus one state-space timing model, each ± duration, fitted on 1910–1959 | Codex (R3) |
| I2 | Uncertainty assumptions and the finite screen need explicit treatment | Reviewer's table matches `comparisons.csv` | **Accept.** Per-setting simulation table and assumption paragraph; the 1.42705 boundary moves to the supplement; the reviewer's 12-year regrouping ([0.00363, 0.02944]) is cited as the reviewer's exploratory check | Codex (R1e), Claude (prose) |
| I3 | Fitting holdout is not freedom from prior scientific exposure | Already in estimands C06/C07 | **Accept**: placed beside the headline in all products | Claude (rewrite) |
| I4 | Observation-to-score chain is not self-contained | — | **Accept**: timeline figure, quantitative qualification table, explicit reproduction tiers. Per-forecast public table waits on the AAVSO terms review (Barry) | Claude and Codex (rewrite) |
| I5 | Novelty framed procedurally; omitted 1984 operational precedent (IBVS 2839) | Not yet checked | **Accept in principle**: read IBVS 2839 ourselves before citing; reframe novelty as a scientific comparison; add Price (2007) and Ak et al. (2002) context. CM92 and Cannizzo (1993) pages were checked in A10l, which closes the review's access gap | Claude (R2) |
| I6 | Effect magnitude is easy to misread | — | **Accept**: verify the Figure 1 illustration (median 27.6 → 26.8 d; P(onset within 30 d) 57.7% → 60.3%) and bind it as a claim | Codex (R1d) |
| I7 | Audit-centred narrative; post-hoc class fits too prominent | — | **Accept** the outline, the Fig. 4 move and the table merge. Applied in the rewrite after research | Claude |
| I8 | AI systems in byline metadata conflict with AAS policy | — | **Barry's decision**, not settled by agents | Barry |
| §5 | Parser repair: proportionate, over-repeated | Reviewer inspected the diff | **Accept**: one precise account in Methods; transparency note in the brief | Claude (rewrite) |
| §7 | Study is coherent but incremental; expand | — | **Accept direction, sharpened** (§5) | Claude (R2 design), Codex (R3) |

## 3. Proposed observation and score contract (for Codex to agree before `estimands.md` changes)

- **Target.** $T$, the next time SS Cyg's visual brightness rises through $m_{\rm vis} = 10$ after
  the forecast is issued. This is a threshold-crossing onset, not the physical start of the disc
  instability.
- **O1, coarsened at random.** Which times carry observations may depend on earlier observations
  and on history, but not on the unobserved $T$ beyond what earlier observations reveal. Alerts after
  someone sees the star bright satisfy O1. Its failure would need observers to report selectively
  according to an onset they had not yet seen.
- **O2, decisive estimates.** An estimate at least `BAND` mag fainter (brighter) than the threshold
  places the star below (above) it at that time, which gives a hard observational bracket
  $(a, b]$ (X4's clip bounds).
- **Proper observed-data score.** Under O1 and O2, $\log P_m(a < T \le b \mid T > \tau, H)$ is the
  observed-data log-likelihood up to a model-free factor (Heitjan and Rubin 1991, coarsening at
  random). It is a proper score for the forecast distribution of $T$.
- **The frozen primary is an approximation.** It scores X4's 99% posterior bracket nested in
  $(a, b]$, so it is a **working interval log score**. R1b quantifies the approximation with:
  - (i) the hard bracket $(a, b]$;
  - (ii) a kernel likelihood $\int k(t)\, f_m(t \mid H)\, dt$, using X4's crossing posterior truncated
    to $(a, b]$. Its implied prior on crossing time is approximately flat, because the location comes
    from a Gaussian level likelihood; Codex should verify that.

  Brackets of about 1–2 d are narrow against forecast spreads of about 10 d, so I predict all three
  paired gains agree within roughly 10%. A material divergence makes E1 substantive.
- **Censoring.** Survival to $C$ is asserted only when the record establishes $T > C$. A straddling
  bracket censors at $a$ (future analyses).
- **Landmark.** End-time error enters the predictors (duration, age at issue), not the outcome
  observation. That is E2, not E1.
- **Figure 3** reports compatibility with extracted brackets. Reading it as physical coverage needs
  $T$ to lie within the bracket.
- **Products** say "working interval log score" until R1b. If R1b agrees, they may say the result
  holds under the hard-bracket and kernel observation scores, as exploratory checks.

## 4. R1: bounded diagnostics (Codex next; exploratory throughout)

**a. Censor fix.**
- Confirm the actual candidate for each of the six censored forecasts.
- Patch `prefix_features.outcome_evidence` and the reference builder to censor at the lower bound of
  a straddling bracket.
- Add a regression test.
- State that the frozen primary is unchanged.

**b. Alternative observation scores** for the 441 forecasts (§3 i–ii), plus the point density at
`onset_t`. Report for each:
- the mean paired gain with its CR1 interval;
- the rank agreement of per-forecast contributions with the primary.

**c. Endpoint dose–response and truth target.** In the v2 null and structured families, at the
recorded seeds:
- Add $N(0, \sigma^2)$ jitter to each extracted end, carried consistently into duration, age at
  issue and the next forecast's previous gap, with σ ∈ {0, 1, 2, 4, 6} d.
- Refit on synthetic development and freeze.
- Score against (i) extracted brackets and (ii) the true onset with administrative censoring.
- Report the null mean gain ± MC SE against σ, and the σ at which it reaches 0.0165 (or "not by
  6 d").
- Add the reviewer's oracle route only if the σ = 0 truth target shows a gain.

Interpretation rule, fixed now:

| Null mean gain at σ ≤ 2 d (about twice the largest qualification RMSE) | Reading |
|---|---|
| Below 0.004 | The endpoint pathway is an implausible sole explanation at qualification-informed error scales |
| Reaches 0.0165 | Measured-duration gain cannot be told apart from measurement artefact, and that becomes the central finding |
| In between | The pathway is partial; report the fraction |

**d. Figure 1 illustration.** Verify the reviewer's numbers and bind them.

**e.** Per-setting simulation table (I2). Verify my §1 aggregates.

**Reply** on this triage, including amendments to §3 and §5.

## 5. The expanded study (to be designed in R2; sketch for Codex's critique)

**Question.** Does the length of a completed dwarf-nova outburst carry reproducible information
about when the next begins, beyond an evolving timing history? And how much of that apparent
information comes from how outbursts are observed and measured?

The marks stay duration and type, the historically motivated ones. Other marks enter only with a
physical rationale and a measurement model (the review's caution, which I share).

**Why multi-star.** Every SS Cyg year through 2017 is now inspected, so anything further on SS Cyg is
exploratory. Two routes would give a fresh confirmation:
- SS Cyg 2018+: closed, and too short alone;
- other stars' records, which this project has never opened.

A sealed design per star repeats what worked for SS Cyg:
1. Fix the fit/evaluation split before any access.
2. Acquire development years only, and qualify extraction on them.
3. Freeze everything.
4. Open the evaluation years once.

Several stars together also give precision that SS Cyg alone cannot.

**Model ladder,** fitted on development data, with the same information cutoff and observation
contract for all:
- M2 (the frozen benchmark);
- L1, a level-adapting model;
- S1, a local-level state-space model on log quiet intervals;
- each of these plus duration, and plus type as a secondary.

The baseline state filter takes quiet intervals only. A variant where duration enters the state as
an observation answers a different question and is labelled so.

**Cohort.**
- Inclusion: ordinary U Gem-type outbursters with long AAVSO visual records. Z Cam standstills and
  SU UMa superoutbursts are excluded in the first cohort.
- Screening uses classification and development-period observing density only, never duration
  coefficients.
- Candidates to screen include U Gem, SS Aur, RU Peg, IP Peg, AR And, X Leo and TW Vir, from
  classification catalogues.
- An exposure table per star records published duration–interval analyses, for example Ak et al.
  (2002), and which years they used.
- Summaries are both star-balanced and forecast-weighted.

**The hard part** is per-star extraction qualification. These stars are fainter in quiescence and far
less densely observed than SS Cyg, and X4's priors and threshold are SS Cyg-specific. The design must
cost this honestly. A star that cannot be qualified on development years is dropped before any
evaluation data exist.

**Gates.**

| Gate | Condition | Consequence |
|---|---|---|
| G1 | R1 shows an observational explanation | Measurement becomes the paper's centre; the cohort waits for an observation-aware score |
| G2 | R2/R3 precision plan shows the cohort cannot reach a useful SE (target to set in R2) | Fall back to a bounded SS Cyg paper with the corrected claims |
| G3 | Opening any star's evaluation records | **Barry's decision**, on a concrete protocol |

## 6. Decisions for Barry

None blocks R1 or R2. When the R2 design is ready:
1. Approve or refuse opening other stars' records under a sealed protocol. This is a one-way door,
   and the design will give the cohort, the precision plan and the costs.
2. Whether to invite a dwarf-nova specialist to check the physical hypotheses and star selection
   before the protocol freezes. I recommend it, and it is outward-facing.
3. The byline (I8), the venue, and whether SS Cyg 2018+ joins the sealed test.
