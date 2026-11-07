# A04c injection/recovery implementation freeze

Codex, 7 November 2026, starting from `4945af6`. This completes ambiguities in
Claude's A04b §5 before any production extraction/recovery run. It retains the
four proposed selection criteria. It is a conditional simulation experiment,
not a real-data forecast result or final evaluation freeze.

## Inputs and independence

Only the 12 receipt-verified open-era exports, ending at native JD 2436934.0,
are available. X1 and X2 are the unchanged candidates from `90e9661`.
The generator author receives this mathematical specification, not extractor
source, annotations or real rows. Separate delegates implement observation and
scoring modules; the parent integrates and checks them. This separates code
derivations, not model families or scientific assumptions.

The generator uses separate marginal duration/gap distributions from X1's
confirmed, bounded 1910–1959 events. Durations are restricted to 5–40 d and
gaps to 5–100 d; gap marginals require no informative spacing over 7 d.
No real duration–gap association is calculated. This calibration is
X1-conditioned and does not independently validate an X1-over-X2 ranking.
Templates are a declared family based on A04b's ranges, not a fitted physical
disc model or an exhaustive morphology distribution.

Observer offsets/scatters use leave-observer-out residuals on native JD bins
at least 2 d from X1 episodes, after reducing repeats to one observer-bin
median. Offset shrinkage is n/(n+10); scatter is MAD × 1.4826, floored at
0.1 mag (default 0.2 where unestimable). Plateau residuals are reported as a
diagnostic, without selecting a second noise model. Simulations use half the
observer variance shared within an observer-bin and half independent by row,
plus a shared bin fluctuation with SD 0.05 mag. This covariance is a scenario
assumption, not identified by the residual fit. Magnitudes are rounded to 0.1.
Source limit slots retain their limits; other slots use the observer's median
recorded limit, or no limit when unavailable. The synthetic rows supplied to
extractors contain no truth labels. Raw rows and observer metadata stay out of
Git and public result tables.

## Truth and arms

Renewal event onsets satisfy s_next = end + Q. Piecewise-linear templates
cross magnitude 10 exactly at s and end. Their peaks, rise times, slow-rise
share (15%) and low-amplitude share (5%) follow A04b's prescribed ranges.
Exact crossings are recomputed at each tested magnitude; an event that never
crosses a threshold is absent from that threshold's truth catalogue.

- **Independent null:** durations follow an empirical-quantile transform of
  a Gaussian AR(1), coefficient −0.4 to represent alternating types. Gaps use
  an independent iid empirical-quantile stream. Thus D is independent of
  both the previous and following Q in the generating process.
- **Copula alternative:** a stationary Gaussian duration/gap process has
  nominal previous-gap correlation 0.282, gap persistence 0.382, and partial
  correlation 0.13. Duration persistence is represented by a −0.4 coefficient.
  Empirical quantile transforms do not preserve Pearson correlations:
  **0.13 is a latent-scale target, not a known raw-scale effect.** Recovery
  is compared with each replicate's realized raw-scale oracle correlation.
  This limitation is reported, rather than tuning the generator to extractor
  results or claiming an exact raw-scale 0.13 alternative.
- **Random phase:** generated renewal histories sampled at the real observing
  times are decisive for null recovery.
- **Aligned diagnostic:** onsets are fixed to X1 episode anchors, with
  synthetic durations constrained to fit between them. Q then equals C−D.
  This cannot be an independent null or an exact 0.13 arm. Both generating
  streams are retained as sampling stress tests against their own realized
  truth, excluded from the independent-null selection gate.

Strata are 1900–1909, 1910–1929, 1930–1949 and 1950–1959, with the final
half-day of 1959 excluded. Run 200 replicates for every phase × process ×
stratum combination, using stable separately labelled random streams. Both
extractors see the same synthetic rows. Thresholds are 9.5, 10.0 and 10.5;
X2 hysteresis shifts by the same threshold displacement. Only 10.0 is a
selection gate; other thresholds are sensitivities against threshold-specific
truth and need not have a zero population association.

## Scoring and denominators

The reference denominator is all complete true events at least 2 d inside
the simulated window. Confirmed extracted episodes are linked by overlap of
their bright cores with true above-threshold episodes. Report false events,
splits and merges. Boundary-error calculations require unique one-to-one
matches; split/merged/missed events and absent finite brackets fail effective
coverage, rather than disappearing. Also report conditional coverage among
matched finite brackets, widths, bias/RMSE, duration/type error, and
observation-time end-confirmation lag. Short-event completeness uses all true
short events outside March–May. False events use full simulated calendar time.

Coverage rules are C1 at 4 d and 7 d, and C2 requiring at least 0.95 of possible
fully-contained 5 d starts to include observations by two distinct observers.
C2 is an exact opportunity fraction under the fixed cadence, not a noisy
detection probability. Missing events among passed adjacencies and rejection
of correctly mapped consecutive pairs are reported. Failed intervals retain a
censoring time at the first coverage loss; no forecast is silently discarded.
This is an eligibility/association diagnostic, not a fitted censoring-aware
forecast likelihood.

For each rule, report raw partial correlation r(D_i,Q_i | Q_prev) from
completed eligible triples, with undefined replicates explicitly counted.
Total bias is recovered minus oracle-all; on correctly matched consecutive
triples, decompose selection (oracle-selected minus oracle-all) and boundary
error (recovered-matched minus oracle-selected). False adjacencies remain in
the total diagnostic. Oracle and recovered values are both finite-sample
quantities; also report the null oracle mean against zero.

## Criteria and stopping

At threshold 10.0 in the 1910–1959 random-phase independent-null strata:

1. At least 90% effective coverage at **each** boundary.
2. At least 95% short-event completeness outside March–May.
3. Fewer than 0.2 false confirmed episodes per year.
4. Absolute mean null association bias below 0.02 for the chosen coverage rule.

Report point estimates and Monte Carlo uncertainty using replicate as the
uncertainty unit. Pass requires the Monte Carlo interval to clear its bound;
fail requires it to fall beyond the bound; otherwise classify inconclusive.
Undefined-correlation cells cannot pass. The 1900s and other arms remain
diagnostics. Among candidates passing all four, prefer more eligible pairs.
No widening or parameter repair is permitted using these confirmation results.
Any later repair needs a new specification and fresh random seeds.

Two hundred replicates are screening, not guaranteed precision. If a candidate
otherwise passes and the sole blocker is Monte Carlo precision, a separate
fixed 800-replicate confirmation extension may be justified. If decisive
coverage/detection failures already prevent selection, do not expand a grid
whose additional precision cannot change that conclusion. The stop condition
is an audited pass/fail/inconclusive decision, with failures retained, not a
requirement that some extractor win.
