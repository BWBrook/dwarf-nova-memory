# Codex review of reconstruction steps 1–2

10 November 2026. Base `9cd8999`; board thread 159, post 3185. Review and proposed
wording only: the product drafts, estimands, scientific sources and frozen
results remain unchanged. Barry's writing directions, OJAp choice and sole
authorship are recorded in that post and D049. No new observations, fits or
scores were used.

## Overall decision

Keep the reconstruction and its single-paper structure. Gather qualifications
in one limitations passage. Define the thing measured accurately in Methods,
and state the measured result directly in Results. This needs a few changes
of object and tense, rather than more caveats.

`05-one-page-paper.md` has 641 prose words by whitespace count, excluding its
title and introductory note. `07-one-page-proposal.md` supplies a 585-word
alternative, with numeric claim bindings. The proposal preserves context,
question, two hypotheses, design, results, discussion, one limitations paragraph
and a generalising conclusion. Claude should reconcile it with the original
before step 3; it is an option, not an accepted replacement.

## 1. Accuracy of the positive statements

| Passage | Judgment and proposed treatment | Evidence / owner |
|---|---|---|
| “knowing how long one lasted improves forecasts” | Use past tense and identify the evaluated record. Suggested main message: **“The star SS Cygni repeatedly brightens; outburst length improved forecasts of its next brightening in a preregistered test against decades of visual observations.”** This states the observed result without loading the message with limitations. | C01; Claude to reconcile |
| “Longer outbursts predicted longer quiet intervals” | Accurate as the frozen model's conditional direction. Write **“The duration model predicted longer waits after longer outbursts.”** Its fitted offset was positive within a nonnegative model specification; the sentence describes that forecaster, rather than a newly estimated evaluation-period physical slope. | C04 and frozen parameters; Claude |
| “A completed outburst carries information about when the next will begin” | Replace with **“Duration improved forecasts evaluated against SS Cyg's visual record beyond the chosen timing baseline.”** Physical-state information is the interpretation being investigated. A limitations section cannot change the object of an earlier assertion. | C01, estimands; Claude |
| One-page Methods: algorithm “marked each outburst”; forecast “when an outburst ended” | Use **“identified outbursts”** and **“when reports confirmed a fade”**. These name the actual detection and issuance rules. | X4/prefix features; Claude |
| Lognormal next-onset distribution; average earlier gaps | Use lognormal **quiet-gap clocks conditioned on survival to issue**. The predictors are the previous log gap and mean log gap over up to six earlier covered intervals, with a log-duration term. The issued remaining wait is shifted/truncated. | Independent semantic check, `ledger_forecast.py:242`, `prefix_features.py:50`; fixed in proposal |
| “working score, since it treats that estimate as the true onset” | Define log probability assigned to an extracted onset window, or survival to a cutoff. An interval is neither an exact point nor a validated truth set. Put physical-onset inference in Limitations. | C01–C03; Claude |
| “1.7% more probability placed on what happened” | Use **“1.7% higher geometric mean probability assigned to the scored evidence.”** The evidence includes interval and survival outcomes. | C02–C03; Claude |
| Both redesigned comparisons “timed outbursts directly from the bracketing reports” | One retains a fitted end; the other uses an observed faint-report clock. Identify them separately. Their gains are 0.0075 and 0.0043, respectively. | C55; Claude |
| “adjusting for that drift” shrank gain | Both baseline and mark changed. Say **“Post-result duration recentering and baseline recalibration reduced an analogous gain.”** This preserves the numerical finding without allocating it uniquely to drift or C01. | C62–C63; Claude |
| “data-reading fix preceded the evaluation” | State **after first access, before scoring**. The present phrase loses the consequential access chronology. | C05; Claude |
| Conclusion: “Data, code and protocol are public” | Say **“Code, protocols and aggregate evidence are public.”** Native inputs remain outside the released repository. | Data policy and receipts; Claude |

The two physical accounts are useful hypotheses. Introduce them as such, with
comparable gas-supply rates in the depletion account. Our source audit found no
specific following-quiet-gap prediction in Cannizzo (1993). The slow-state
account needs duration to track state beyond what the timing covariates capture.
Its label alone does not entail a positive duration coefficient. Use names such
as *depletion hypothesis* and *state hypothesis*: H1–H3 already label the R2b
clock contrasts.

The short abstract's opening should specify the **incremental duration** question;
the literature already contains a held-out onset forecast. The main-message
supporting notes should call the ten-star screen a transfer assessment, rather
than an extra line confirming duration's effect. The working abstract's “only
star where this test could be run” should become “the qualifying cohort was
empty under the frozen transfer rules.”

## 2. Exact proposed replacements for the estimands rules

These replacements are proposed for agreement with Claude; the canonical file
has not yet been edited.

**Replace the D047 placement sentence:**

> State the empirical finding plainly in the headline and main message. Define
> the forecast target and working score in Methods. Present each required
> qualification once, in the dedicated limitations passage, while reporting
> the actual secondary results in Results. A standalone abstract collects its
> essential qualifications in a compact closing passage.

**Replace “Conditions beside the headline” in the C01 section:**

> Required reporting: Methods define the visual record, extraction, issue
> landmark, frozen timing baseline, working interval/survival score and
> retrospective information set. Results give the primary gain, uncertainty,
> population and predeclared decision, plus the later-period and type-rule
> outcomes. The limitations passage covers single-star scope, the unestablished
> physical-onset observation model, shared endpoint and observing pathways,
> the post-access format repair, unknown historical upload/revision times and
> exploratory recalibration. The analogous recalibration contrast changes
> model, score and population; it does not allocate a component of C01.

Definitions and result identity remain necessary wherever they make a sentence
intelligible. This revision changes placement, not evidence status or scientific
meaning. It removes the requirement to repeat all limitations beside every
primary-result sentence.

## 3. Fig. 4B and the display plan

**Yes to the panel, as an operational count-ratio comparison.** The independently
saved C70 evidence contains a coherent frozen-route ratio as well as the raw
route. Use the frozen reductions for each hold star in both numerator and
denominator; their decade peak counts happen to equal the raw counts here.
State the period separately for each panel: whole-development support in A,
1980–1989 counts in B.

Suggested axis: **“Supported issuances / confirmed episode peaks (1980–1989)”**.
Print n/d beside each point. Caption: **“Numerators count supported forecasts by
issue date; denominators count confirmed episodes by peak date within the same
decade. Hold stars use the specified derived-night streams. Ratios describe
operational yield under these rules.”** This is descriptive, so binomial
recovery-rate error bars would introduce a new inferential claim.

SS Aur needs a visible flag in panel A: it clears the count gate and fails the
long-run gate. The caption should name the other qualification gates, with the
full window/base/eclipse table in the appendix. The panel shows yield; attributing
the difference solely to depth would need additional evidence.

Two other changes improve the display plan:

- **Fig. 2B:** describe block variation and the pooled gain. Eight positive block
  means do not establish improvement in every decade. Keep the already-public
  block means rather than releasing per-issuance scores for a cumulative curve.
- **Fig. 3:** retain a grouped forest of gain comparisons, clearly labelling each
  clock, baseline and scored population. Move H3 to the appendix or a separate
  inset labelled *difference of gains*: it is not another duration-gain estimate.
  Table 1 also needs to identify the redesigned baseline used in this figure.
- **Fig. 1C:** separate observation-year splits from the 2026 freeze/deposit/access
  sequence. A picture should not imply that preregistration occurred in 1959.

A ledger follow-up before rewriting: C68's current limit again says the SS Aur
flag spans “several outbursts”. C71 supports separated report clusters; restore
that narrower wording when reconciling the products.

## 4. Suggested abstract and cuts

A proposed abstract is below. Its body has 129 words by whitespace count.

> Dwarf novae repeatedly brighten as gas accretes onto a white dwarf. We tested
> whether outburst duration adds forecast information beyond recent timing in
> SS Cygni. Lognormal models fitted on 1910–1959 were frozen and preregistered
> before 1960–2017 was opened. Duration raised the working interval score by
> 0.0165 nats per forecast (90% interval 0.0049–0.0281; 441 forecasts). Two
> redesigned comparisons and the later-period and long/short secondaries were
> inconclusive. A frozen pre-1990 feasibility screen qualified none of ten other
> stars. These results identify an incremental forecasting benefit in SS Cyg's
> visual record and document the record requirements for transferring the test.
> The working score depends on extracted onset windows; physical-onset inference
> requires a validated observation model. Measurement coupling and
> activity-dependent observing remain possible pathways. The completed
> evaluation followed a documented post-access parser repair.

The one-page proposal removes the exact flare cadence and contrast, the generic
explanation of held-out testing, the uncertain causal “quarter” allocation and
repeated restatements of the question. It keeps the larger timing-baseline gain
for scale. Lognormal clocks, observation-date issuance and incomplete follow-up
are retained as concrete methods. Reaching exactly 600 would add little.

## 5. OJAp and authorship

I agree with OJAp, Barry's sole byline and the deferred AI-declaration placeholder.
The independent venue check verified all five comparison-paper identities and
OJAp references. It did not reproduce the PDF word counts or voice statistics.
The exact official class/BST files remain unverified in this pass. Identity checks
pin [2408.06404v2](https://arxiv.org/abs/2408.06404v2),
[2506.20505v2](https://arxiv.org/abs/2506.20505v2),
[2606.01496v2](https://arxiv.org/abs/2606.01496v2),
[2512.24936v3](https://arxiv.org/abs/2512.24936v3) and
[2606.08319v4](https://arxiv.org/abs/2606.08319v4).
The parent independently read the current journal/arXiv policy text; the OJAp
text was accessible through the official-page search index, while normal open
returned no readable body.

Corrections to the comparison, based on [OJAp's author guidance](https://astro.theoj.org/for-authors):

- arXiv-first is preferred; direct submissions can be reviewed. Final publication
  uses arXiv. Submission must come from a named author.
- Disclose AI in acknowledgments and explain analytical validation; the guidance
  does not locate the entire validation account in acknowledgments.
- OJAp uses CC BY. Record the emitted article/figure licence separately from the
  repository's CC BY-SA default before release.
- The figure budget, one PDF, abstract length and AAS-like references are editorial
  choices or observed practice, rather than verified mandatory rules.

Use the [current arXiv AI policy](https://info.arxiv.org/help/moderation/index.html#policy-for-authors-use-of-generative-ai-language-tools)
for human responsibility, disclosure and AI non-authorship. The
[licence guidance](https://info.arxiv.org/help/license/index.html) distinguishes
CC BY and CC BY-SA and requires authority to grant the selected licence.

The [OJAp ethics statement](https://astro.theoj.org/pages/390-ethics-statement)
calls for attribution of reused material; overlap with our protocol is not by
itself an established breach. It also discourages public dissemination of
referee/editor correspondence. Keep any future journal correspondence outside
routine board snapshots.

## Checks

Parent checked the saved aggregates and frozen parameters. A separate delegate
verified current journal policy and comparison-paper identities, then checked
the proposed one-page, abstract and main message semantically. This was an
independent check, not a cold or blind read. Its two Methods findings (the
conditional clock and log/bounded history) are reconciled above and in the
proposal. No further semantic blocker was found.

All 580 tests and the structure validator pass. The 26 qualified forecasting
sources and parameter SHA-256 are unchanged. Numeric bindings in the proposal
pass the claims checker alongside the unchanged products. No new archive
request, real-data fit/score or product rebuild was made.

## Handoff

Claude: reconcile the proposed one-page and abstract wording, accept or amend the
two placement rules, and adjust the display plan. Then agree steps 1–2 before
expanding into the OJAp article. No further data or analysis is needed for this
reconciliation. Product drafts remain unchanged.
