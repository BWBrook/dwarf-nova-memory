# Independent R2b contract audit before scoring

Codex delegate, 9 November 2026, initial source `ced0413`. Read the v0 protocol,
Claude review and existing X5/scoring/model code. All fixtures use invented
numbers. No real observations, model fit or scientific forecast score was read
or computed. No source or board edit was made.

## Required amendments

### 1. A Fisher expansion is a local index, not a ceiling

The stated unconditional lognormal location Fisher information is algebraically
correct: with `X ~ LogNormal(mu,sigma)`, the location score is
`u(X) = [1 + (log X-mu)/sigma²]/X`, giving
`J = (1+sigma²)*exp(2sigma²-2mu)/sigma²`.
The KL expansion `KL = J*delta²/2 + o(delta²)` supplies no signed remainder
bound. It cannot license the inequality or the mechanism-exclusion rule in
v0 §7.

Independent conditional-density integration: median 40 days, sigma .4, issue
age two days and an additive positive anchor shift one day give exact
`D(P || Q_shift) = 0.00324710844901597`, versus index
`0.00312005509107365` (4.07% smaller). At shift .1 day the exact KL still exceeds
the index. At issue age zero any positive shift makes this KL direction
infinite because shifted Q has zero support on an interval where P has positive
mass. These are counterexamples to treating the quadratic as a universal KL
bound, not a fitted SS Cyg effect or a full simulated physical DGP.

Conditioning on survival also changes the location score to
`u(X)-hazard(issue_age)` and the information to its conditional variance. The
unconditional J is not generally the correct information for the issued law.
A signed history derivative can cause cancellation inside the proposed Delta;
a triangle bound would require absolute sensitivities. More importantly B0/B1
and especially B2 use older gaps. An independent direct covariance calculation
for a local-level + AR process gives weights `[.21551,.13027,.62177]` on three
past log gaps; altering the oldest by .1 shifts the next log location .02155
while the last gap stays unchanged. The one-lag Delta omits that pathway.

**Amendment:** retain a fully labelled local, one-lag lag-sensitivity index as
a descriptive calculation if useful. Report missing inputs and derivative sign.
Do not use a gain or lower limit exceeding the index to exclude cadence. A
rigorous finite-shift bound would need all-history sensitivity, actual
conditional likelihoods, support and a complete null observation model.

### 2. Raw visit supports do not prove the new containment claim

The last-upcrossing convention handles the previously supplied simple
nondecisive false start, and is a defensible target convention. Its proof needs
an actual faint witness ordered before the first qualifying decisive-bright
excursion. The raw lower endpoint is not itself such a witness.

Fixture: one observer reports `(t,m)=(0,9.5),(.05,11.5),(.10,11.5)`; its median
is faint at .05. Another exact report is decisive bright at .01, followed by
later bright reports at 1 and 2. X5 selects the faint median as quiescence,
skips the .01 bright report before that median, and emits an **eligible**
window `[0,1]` with no flags. A continuous exact light curve crosses magnitude
10 at -.1 and first reaches magnitude 9 at .01; its target is -.1, outside the
window. There is no decisive excursion before raw L=0, so the explicit v0
condition 'none before L' holds. There is a decisive excursion within the lower
visit support, which the median aggregation obscures for this selection.

This is not a contradiction if A0 is strengthened to exclude all earlier or
merged qualifying excursions through the selected faint witness, including
inside visit support. It shows that v0's abbreviated sufficient condition is
incomplete. Given a genuinely faint witness `tF >= L` before the intended first
decisive time and a bright witness `tB <= U`, continuity gives the desired
ordering. Otherwise A1 remains explicit. No claim about this fixture's real
frequency or astrophysical plausibility is made.

**Amendment:** retain the crossing convention and full A0/A1, but remove 'A1
can fail only through ...' or broaden it explicitly to aggregation/order and
association. Exact raw magnitudes plus broad supports alone do not close A1.

### 3. Keep the rate control diagnostic

The log rate uses the duration-dependent span in its denominator and an event-
selected numerator. It is an observing-intensity proxy, not a negative control
with a proved exclusion restriction. Physical morphology may alter both
observing intensity and the future gap. A positive proxy gain therefore cannot
establish a cadence artefact, and a zero nonnegative offset cannot exclude
negative or nonlinear cadence information.

**Amendment:** call it an observing-rate sensitivity and interpret its sign
jointly with other results. Remove an automatic rule that discards DF's distinct
interpretation solely because this proxy has a positive interval.

## Scoring and inference conditions to fix before execution

- H3 is meaningful as a paired difference in **incremental working forecast
  gains**, under two separately trained clock/history models. It is not a
  causal effect of removing an end estimate. The exact issue, candidate
  association, outcome eligibility, outcome window and cutoff must be common
  to the matched pair; report full and markable populations and differing routes.
- Unsupported outcomes must remain unsupported, rather than be converted to
  quiescence. An exact prediction-identity gain can be zero without knowing its
  outcome, but any such identities need a distinct status and denominator.
- Existing scalar interval and fixed-C bounds preserve the proper distinction
  between working backoff scores and the fixed-cutoff mixed target. Do not
  claim bounds for a latent point after censoring or established CAR.
- Six- and twelve-year CR1 intervals can be descriptive sensitivities. Count
  actual nonempty clusters; do not force a fixed degrees of freedom if outcomes
  leave a cluster empty. Define the residual proxy for interval/censored data
  before inspecting it; midpoint residuals are working diagnostics, not known
  latent errors or conditional PIT residuals.
- The later 18-year/star choice is prospective but does not certify coverage.
  Two blocks within a star need not be independent. Validation must include
  plausible dependence beyond point-estimated SS Cyg values and Monte Carlo
  uncertainty. Star-only clustering still assumes independent stars and relies
  on a small number of clusters. Do not call a point estimate ≥.88 nominal 90%
  certification. Positive-coefficient conditional null rejection and overall
  null rejection are different operating characteristics; state the conditioning.
- B2 development stability must inspect all declared starts, their statuses and
  objective discrepancies, including successes at boundaries. Selecting the best
  objective does not erase multistart disagreement. Future sealed fallback must
  be based solely on the predeclared development criterion, never evaluation gain.

## Reproduction

`python scripts/r2b_contract_checks.py --output outputs/r2b_contract_reproduction`

`checks.json` contains the invented reports, exact path, source hashes, KL
quadrature errors and independent Gaussian weights. These checks test logic and
arithmetic; they do not establish actual SS Cyg observation error or power.

## Parent implementation review: `r2b_models.py`

Reviewed SHA-256
`efed121968cd167caf064dde6676a33f47f49d857921fe0f9b19fbeb512b4b19`.
No blocking implementation defect found in this version:

- development feature/outcome populations are identical and unique;
- information cutoff, support availability and exact issue alignment are checked;
- cadence enters the timing objective jointly with base parameters, using only
  development centering/scaling; missing cadence takes that center;
- mark fitting freezes the timing/cadence rule and restricts marks to usable
  timing histories;
- prediction preserves common remaining/constant fallbacks and exact zero- or
  missing-mark nesting;
- all declared optimizer attempts are retained. Stability requires every start
  to succeed, at least two successes and objective agreement within the stated
  relative tolerance. A good best start does not hide another failed start.

`model_check.py` runs 18 invented fixed-rule or mocked-optimizer probes without
running an optimizer. They verify cadence and mark shifts, exact nesting,
future cadence/rate/flux rejection, training leakage guards, and stable/failed/
disagreeing multistarts. All pass in `model-checks.json`. These probes do not
recompute a fit or establish identifiability/global optimality. Boundary optima
and B1 rank deficiency remain matters to report from actual fit metadata.
