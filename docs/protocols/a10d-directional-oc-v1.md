# A10d: amended directional forecasting and finite calibration screens

Codex, 8 November 2026. Implements and reviews A10c at `c9aab07`.
D018 remains held-out forecast gain. No 1960+ access is authorized. Real
1910–1959 fitting remains conditional on the declared synthetic gate; the
requested distinction between a 360-trial screen and formal error-rate
certification has been put to Barry before outcomes exist.

## Review amendments

The nonnegative coefficient is a directional restriction, not a universal
protection against measurement-induced information. Independent exact
calculations show positive duration information and a positive conditional
lognormal coefficient with constant true duration after survival selection.
The current early-age null scenarios do not establish a general sign theorem.

The lagged-duration model is a state-sensitivity comparator. A current mark
can outpredict a previous mark under a pure slow state because it is more
recent. M3−P3 cannot identify direct physical memory, whichever way its
interval falls. The simulations report both contrasts without a causal gate.

The slow-state loading remains fixed at λ²=0.13: this is a marginal latent-
rank correlation, not the conditional correlation after q or local history.
No loading is tuned against the new outcomes. These are within-block AR
stress processes; independent source blocks retain the A10b seams.

## Feature and forecast definition

X4 and its dependencies retain bytes from `352a09e`, at magnitude 10.0.
`a10-prefix-v3` adds previous positive point duration and the six most recent
covered earlier log gaps to the v2 prefix contract. The local gaps end no
later than the previous episode's onset, excluding the current previous gap.
Both episode onsets must be over 30 d inside the 400 d lookback. Coverage
uses the existing 7 d visit-hole rule. Nonpositive duration is missing.

M0 and common R0 retain the A10b likelihood. M2 fits covered previous log
gap q and the mean of earlier log gaps L. Centers/scales are computed only
from the training rows; missing L is its training mean, and a constant term
is fixed at zero with explicit metadata.

Fit M2 once on all timing-eligible rows. Hold its intercept, q/L slopes and
scale fixed. M3 estimates only a nonnegative standardized current-log-duration
offset; P3 estimates the analogous lagged offset. Fit each offset on its
valid-mark rows. Thus deployed missing-mark fallback is the same distribution
used in fitting, rather than a different nuisance fit with x imputed to zero.
Include β=0 as an exact candidate. Missing q routes all to M0; unknown end
routes all to common R0. At β=0, route literally to M2. All issuance zeros
remain in the main mean. Failed identifiable fits are errors, not zero fits.

The S2 diagnostic fits both offsets on the joint-valid training subset and
scores their contrast on the joint-valid evaluation subset. The timing base
is unchanged. Secondary S1 is explicitly refitted on evaluation outcomes;
none of its forecasts enter the held-out score.

Sensitivities are uniform-end five-node current-end mixtures, q-only timing,
two-day issuance delay, and a type/within-type offset. The type diagnostic
has two nonnegative coefficients but does not inherit a one-dimensional
monotonicity or power claim. Previous duration remains a point mark in the
uniform-end sensitivity. L2 delays issuance, not record availability.

## Source freeze, concordance and numerical checks

Development tests and smokes use separate namespaces and are not qualification
trials. Before any full-history development score, run 100 short-history exact
candidate/reference comparisons at both delays. Before production, freeze the
whole source and repeat 100 independent comparisons bound to that commit,
including the new slow-state processes. The reference implementation does not
call candidate feature/evidence code; shared X4/visit primitives are explicit.

Preserve normalization, endpoint-node masks and joint end/age/mark offsets.
Check scalar/vector likelihoods, exact zero nesting, literal matched routing,
training evidence cutoffs and serialization. Public numerical fixtures and
independent calculators are retained separately from candidate implementation.

## Fixed operating-characteristic grid

Use exactly the A10c 360-trial grid: 40 v2 trials for null, structured,
slow_090, slow_098, gross, offset, adaptive and alternative; 20 v4 trials
for null and alternative. Use `a10c-oc|<freeze hash>` and independent replicate
seeds. Common null/stress streams retain A10b pairing. V4 is unqualified as
a realistic waveform, but its null rejection count is reported and screened
under the user's “every no-effect scenario except slow state” criterion.

Each history has the same approximately 50 training plus 58 evaluation source-
pattern years and integer translations with 30 d coverage-breaking seams.
The evaluation mix is 28 early, 20 middle and 10 late years, not equal era
weights. Keep all primary issuance rows; diagnostics identify their subsets.

**Freeze six-year clusters as primary before any OC outcomes**, with three-
year clusters reported as a sensitivity. This avoids choosing and certifying
the cluster width on the same 40 outcomes. Anchor clusters at the fixed
training cutoff, not a selected first scored event. Use the cluster sandwich
standard error and Student-t with nonempty cluster count minus one degrees of
freedom. The t(.95) lower bound defines confirmation and gives the two-sided
90% interval. Exactly identical models have zero gain and cannot confirm.

For each of the 40 v2 null and 40 alternative fitted systems, use six fresh
independent 58-year evaluation replicas (348 source-pattern years), retaining
the exact source mix and immutable last-400-day training context. This modest
extension replaces the mismatched 300-year mixture. The reference mean has
finite Monte Carlo error; propagate its replica SE with the original block
SE using a Welch–Satterthwaite difference interval. Report this as joint-MC
calibration, not coverage against known exact truth. If β=0, expected gain is
analytically exactly zero and no redundant continuation is generated; retain
the trial and its exact-identity coverage record.

Report overall and interior-only calibration separately so exact-zero fits
cannot conceal poor calibration when duration actually changes forecasts.

## Gate policies, frozen before outcomes

Calculate both of the following, without choosing a policy after seeing a
favorable result:

1. **360-trial screen:** no missing/failed trial; observed primary rejection
   fraction ≤0.05 in every non-slow no-effect case, including v4 null. This
   means at most 2/40 or 1/20. Report exact binomial intervals and MC SE;
   a pass is not proof that the population error rate is ≤0.05.
2. **Formal size certificate:** the one-sided exact 95% upper binomial bound
   is ≤0.05 in every such case. The fixed 40/20 counts cannot satisfy this
   even with zero rejections. A larger study requires an explicit new design,
   not automatic favorable additions to this grid.

Joint-MC calibration must also pass in each of v2 null and alternative:
the exact lower-tail test against nominal .90 coverage must exceed .05,
both overall and among interior fits. For 40 nondegenerate trials the former
requires at least 33 covered differences. This detects gross undercoverage;
it does not prove exact conditional coverage. Empty interior groups are
reported as untested, while exact-identity predictions remain valid zeros.

Until the gate-policy question is resolved, report both decisions and keep
the real-fit action separate. There is no automatic real-data step. A failure
is retained and stops that step. No predictor, simulator, coefficient bound
or inferential method is tuned to make this study pass. The point-estimate
screen is the recommendation put to Barry, not an inferred reply.

## Real development and later evaluation

If the approved gate passes, record the extraction/feature/model source freeze,
then build the 1910–1959 ledger and fit once, at both issuance delays, using
only rows before 1960. Preserve raw source hashes and censor unresolved
outcomes at the cutoff. Publish frozen parameters, coefficient likelihood
profiles with bound status, likelihood summaries and route diagnostics.
Do not revise the forecast system after seeing this first real association.
The 1960–2017 block still requires Barry's explicit go-ahead after an
evaluation protocol commit; 2018 onward remains reserved.
