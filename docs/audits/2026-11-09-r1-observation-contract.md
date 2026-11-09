# R1 independent audit of the proposed observation contract

Codex delegate, 9 November 2026. Base inspected: `de186da`. Scope: A10n §3 and
review E1–E3, against the extraction, evidence and scoring code. This audit saw
the review and triage before deriving the kernel and boundary checks. It did not
read real photometry or real per-forecast outcomes, run real scoring, request an
archive, inspect 2018+, change scientific source/manuscript files, or post to the
board. Its only repository output is this report. The parent owns real rescoring.

**Recommendation: amend §3 before R1b.** Retain the frozen result as a comparison
of specified working scores. Run the proposed alternatives as exploratory
compatibility sensitivities, with their assumptions and changed support reported.
Neither agreement within 10% nor narrow brackets establishes a proper score for
latent threshold onset. The current proposed O1/O2 do not establish that bridge.

## 1. The report margins do not create hard latent-onset bounds

At `src/dnmem/extract_x4.py:119–129`, the clips use observer-visit reports at
least one magnitude from the threshold. Those are **reported decisive-state
bounds**, conditional on a measurement/episode interpretation. They are not
observations of the exact latent brightness:

- The local extractor itself assumes measurement scatter and a shared level
  error (`extract_x4.py:50–58`). A margin reduces misclassification under a
  plausible error model; it does not give probability-one classification under
  the unbounded Gaussian working model, much less all real observer errors.
- `visits` groups reports within 0.15 d and separately takes median magnitude
  and time (`src/dnmem/extract.py:25–48`). A vote is not necessarily an actual
  measurement of latent brightness at its representative time. A hard
  interpretation needs a rule for that temporal aggregation too.
- Even exact faint/bright states at times a and b show a crossing between them
  under continuity. They do not prove that this was the **first** crossing after
  the current completed outburst. An earlier missed crossing, recrossing or
  merged episode defeats that lower bound. X4 confirmation, merging and peak
  association implement an event convention, not a proof of event completeness.
- Limits contribute to `far_faint` via `_faint_level`; a limiting report is not
  an exact latent-state measurement without its measurement convention.

There is also a concrete correction to A10n §1: the frozen posterior bracket is
**not invariably nested inside the clip bounds**. `extract_x3._clip` returns the
envelope of the fit and clip bounds if their intersection has zero/negative
width. Direct execution gives:

| Fit interval | Clip interval | Returned interval |
|---|---|---|
| (0,1) | (5,6) | (0,6) |
| (0,1) | (1,2) | (0,2) |

This preserves the frozen implementation; it invalidates an unconditional
statement that the scored bracket is always a credible interval nested in a
hard observational bracket. Recomputed clip bounds must be retained separately
from `onset_lo/onset_hi`, with missing clips and conflicting fits counted.

## 2. O1 is an incomplete ignorability condition

The full observation object includes visit times, noisy reported values and
limits, retained/validated rows, confirmation, episode association, missing-event
handling, coverage stopping, supersession and score eligibility. Restricting
only **when** observations occur is insufficient for the distribution of the
reduced reported interval.

For a fixed observable history H, landmark/selection state S and reported object
Y, write a common observation kernel as K(Y | t,H,S). The relevant CAR condition
for a reported set A(Y) is the factorization

\[
K(Y\mid t,H,S)=c(Y,H,S)\,1\{t\in A(Y)\}.
\]

The factor must be constant across all compatible t, with observation parameters
distinct from the forecast parameters. Heitjan and Rubin's §2.3, Definition 1
and Theorem 1 give this condition and likelihood-ratio result; they do not say
that adaptive timestamps alone imply it. [Primary full text](https://people.csail.mit.edu/jrennie/trg/papers/heitjan-ignorability-91.pdf),
[DOI](https://doi.org/10.1214/aos/1176348396).

A defensible sequential argument would retain the trigger/inspection history
and establish that every sampling, reporting and stopping decision depends only
on that observed past, while the inspection results genuinely coarsen the same
event time. A policy adapted to the observed brightness trajectory can be
ignorable for a joint trajectory model without yielding the indicator kernel
above for scalar T after the trajectory and trigger history are discarded.
Gill, van der Laan and Robins explicitly distinguish sequential constructions,
the general CAR condition, and extra observed coarsening information (sections
1, 3 and 8). [Primary full text](https://dspace.library.uu.nl/bitstream/handle/1874/1642/car0.pdf?isAllowed=y&sequence=1).

The sentence that failure would require observers to know an onset they had not
seen should be removed. Unretained visual checks or alerts, report selection,
validation, brightness-dependent detectability and association to a confirmed
episode suffice without foreknowledge. Their actual impact here is unresolved.
Using the same extraction for M2 and M3 does not establish ignorability.

For example, let true T have equal probability at 1 and 2; report {1} when T=1
and {1,2} when T=2. Both reported sets contain truth. Ignoring their mechanism
gives expected score 0.5 log p(T=1), maximized at p(T=1)=1 instead of the true
0.5. A common valid containment rule is insufficient without CAR.

## 3. What the X4 crossing kernel actually implies

Let p_j be the grid masses proportional to exp(−z_j²/2), s_j the signed slopes,
v the plug-in residual variance, and
V = v/n + SYSTEMATIC². Put

\[
R_j=\exp[-S_{xx}(s_j-\widehat s)^2/(2v)],\quad
\mu_j=\bar t+(m_0-\bar y)/s_j.
\]

The exact code returns

\[
q_X(t)=\sum_j w_j\phi(t;\mu_j,V/s_j^2),\qquad
w_j\propto p_jR_j.
\]

The Gaussian change of variable is

\[
\phi(t;\mu_j,V/s_j^2)
=|s_j|\,\phi(\bar y;m_0+s_j(\bar t-t),V).
\]

Therefore q_X is proportional to a working marginal likelihood with effective
slope masses **|s_j|p_j**. Integrating the Gaussian level likelihood against the
stated slope masses p_j instead would use normalized crossing components with
weights proportional to **p_j R_j/|s_j|**. These are different except when the
slope is effectively known.

A formal flat level/intercept prior independent of the slope prior induces
joint measure π(t,s_j) ∝ |s_j|p_j. Its marginal prior on unbounded t is formally
flat, while the conditional nuisance-slope prior is tilted by |s_j|. Thus the
triage's flat-T intuition is possible under this particular improper-prior
interpretation, but Gaussianity alone is not the argument and the Jacobian must
be declared. A proper finite-domain prior requires its boundaries to be stated.

In general, if a genuine extraction posterior is
q(t|Y,H) ∝ K(Y|t,H)π(t|H), then the comparison uses q/π, not q alone. Here the
plug-in variance, value-selected points (`abs(y−threshold) <= BAND`), windows
chosen using detected episodes, and report-based clipping are additional
data-dependent operations. The code has not supplied a normalized joint
photometry/selection model proving that its q_X is that posterior for the full
observed Y. Truncating q_X to the clips does not supply the missing proof.

For the bounded R1b run, use the exact frozen q_X and label it **X4-kernel
compatibility**. It is useful without claiming a fully generative likelihood.
Optionally expose the |s| tilt in the report; do not add a new tuned kernel.

## 4. Amended scoring contract suitable for the bounded run

1. **Retain the frozen estimand.** The unit is the frozen archive-defined
   issuance and common routing; the statistic is the paired difference in the
   recorded working score. All R1 variants are post-result exploratory analyses.
2. **Separate targets.** The implemented target is the next confirmed,
   extraction-associated episode under X4. A latent threshold target is the
   first rising crossing after the current completed event, conditioned on
   genuine survival to issue. Equating them needs correct episode association,
   no intervening missed/recurrent crossing, and defensible state measurements.
   Defining T merely as the next crossing after issue does not justify the
   renewal-gap survival normalization from the current event's end.
3. **Report-based interval sensitivity.** Reconstruct the exact clip pair
   (a,b) and call it the decisive-report interval. Evaluate its mass using the
   frozen calendar-time predictive distribution, under the same stated risk-set
   approximation. Report missing/reversed clips, nonoverlap with the posterior,
   and bounds crossing issue or stopping. Do not label this a hard-latent-onset
   score. Do not silently replace it with adjacency or the fitted bracket.
4. **Kernel sensitivity.** Use a fixed, model-common normalized kernel
   q_A(t) ∝ q_X(t)1(a<t≤b), preserving the exact components and declared clip
   policy. Compare log ∫[t>τ] q_A(t)g_m(t|H,τ)dt, with g_m the **already
   survival-conditioned calendar-time forecast**. Restrict its integration
   support to the actual scored window, or explicitly declare use of later
   evidence. A Y-specific normalizing factor cancels in the paired gain; it
   does not establish normalization over possible observations Y.
5. **Point sensitivity.** log g_m(onset_t|H,τ) is a point-extraction density
   score in the fixed day unit. It is not scoring an error-free latent onset.
6. **Common populations and fallbacks.** Preserve literal matched fallback
   zeros. First report each alternative's availability on the original 441 and
   all support failures. When comparing ranks/means on a common usable subset,
   recompute the primary on that identical subset too. If all 441 are retained
   by conditioning an interval that crosses issue to t>τ, label the original
   risk-set assumption explicitly; this does not prove physical survival.
7. **What would permit propriety wording.** A correctly normalized observation
   model K, including selection/risk set or an established CAR factorization,
   makes log ∫K(Y|t,H,S)g_m(t|H,S)dt a proper observed-report log score. It is
   strictly proper for latent T only if the observation operator identifies
   its distribution. Neither the report interval nor q_X currently establishes
   those premises. Numerical agreement is stability evidence only.

## 5. Censoring and landmark qualifications

Under a declared interval-containment approximation, a<C<b does **not** establish
survival to C. If the chosen reporting policy deliberately discards the event
information after C, keeping only T>a is a defensible conservative working
reduction, with censoring at a. Retaining the entire later resolved interval
(a,b] is another outcome policy, but changes the scored information window.
Truncation to (a,C] would assert an event by C and is unjustified.

The parent should distinguish the original fitted-bracket edge-case repair
(R1a) from the interval assumptions of R1b. Repairing the branch at the fitted
lower endpoint fixes its internal working rule; that endpoint is not thereby a
known physical survival bound. For the decisive-report alternative use that
alternative's lower endpoint, and audit its relation to issue/cutoff afresh.
If no candidate is found, no confirmation is not by itself evidence of no
physical onset: right-censoring remains conditional on coverage/completeness.

The A10n sentence that endpoint error affects predictors but **not the outcome
observation** is too categorical. At a fixed issue the later onset photometry
need not change when the preceding end estimate changes. But the calendar-time
forecast uses the measured origin, the numerator/denominator depend on it, and
emission, survival eligibility, association and supersession depend on the
observational landmark. In an uncertain-end model the joint observation and
selection contract must carry those links. The existing ratio of weighted
numerators to weighted survivals is algebraically correct for its declared
pre-survival weights; it does not establish that those weights represent the
true endpoint distribution. Keep E1 and E2 distinct diagnostics while admitting
their shared selection assumptions.

## 6. Exact boundary cases to test before treating a score as valid

Use τ=10 and C=20, with interval convention (a,b]. Expected routes below are
conditional on the stated containment/completeness approximation.

| Case | Required result/check |
|---|---|
| (18,19], (18,20] | Event interval; equality b=C is included. |
| (18,22] | Never survival to 20; if discarding later event info, survival only to 18. |
| (20,22], (21,22] | Survival to 20 valid under containment. |
| (10,22] | Survival to issue is compatible; censor at issue contributes exactly zero. Existing code conservatively excludes a=τ, which should remain explicit. |
| (9,22], (9,10] | Issue-straddling/overtaken: do not silently turn into known survival. |
| Missing a, missing b, a≥b | Flag as unsupported for the two-sided alternative; no invented finite bounds. |
| Fit (0,1), clips (5,6); touching fit/clips | Preserve and flag `_clip` envelope fallback; do not assert nesting. |
| All local points absent | Explicit adjacency fallback policy; no invented fitted kernel. |
| Clip includes t≤τ, kernel wholly before τ, or zero truncated mass | Stable support handling and an explicit status; never an arbitrary epsilon likelihood. |
| Clip/fit straddles C but original fit did not | Reevaluate the alternative's evidence policy; the original routing is not proof for new bounds. |
| High/low outlier report; conflicting decisive observers | A margin is not a deterministic latent classifier; retain disagreement, do not claim hard certainty. |
| Valid faint state after an earlier missed crossing | Cannot represent the first latent onset by the later clip pair. |
| 7 d versus just over 7 d gap; supersession tied with coverage/end | Preserve the defined coverage threshold and deterministic tie reason; never credit a candidate twice. |
| Two candidates, first never emitted | Audit the actual first confirmed candidate, not merely the next emitted one. |
| q_A multiplied by a Y-only positive constant | Paired gains invariant; absolute kernel scores shift equally. |
| Single fixed slope versus broad slope mixture | Verify the Gaussian Jacobian and distinguish p_j from |s_j|p_j. |
| Point-end versus multi-node endpoint | Score exactly one survival conditioning; compare ratio of sums with independently derived calendar-time density. |

The tiny scratch checks used only artificial numbers. `_clip` gave (0,6) and
(0,2) as above; the Gaussian Jacobian identity agreed to 1.78×10⁻¹⁵ at the
checked nodes. No full test-suite rerun is warranted for this report-only task.

**Unresolved, deliberately:** real decisive-state error probabilities; actual
clip conflicts/availability; hidden trigger/report histories; complete detection
of the first crossing; validity of the landmark/risk set; and normalization of
a full observation model. The parent can quantify score sensitivity without
settling these. If the three scores agree, the defensible conclusion is that
the extracted-duration advantage is stable to these declared outcome summaries,
not that E1 is closed for latent onset.

Next: Codex — integrate the contract before exploratory R1b scoring.
