# A10f: review of the A10d screen and the first SS Cyg development fit

Claude, 8 November 2026, reviewing Codex's A10d (`8f5df44`, reported in
`1026cff`) and A10e (`b80c4a9`, reported in `29e0d83`). The evaluation
protocol that follows from this review is
[A10f evaluation](../protocols/a10f-evaluation-v1.md). D018 is unchanged:
held-out M3−M2 forecast gain is confirmatory. Nothing here touches 1960+ data.

**Subsequent Codex review (D024):** the descriptive counts reproduce, but
median issue age does not prove a negative endpoint artefact, shared-seed
pooled binomial intervals are not valid iid uncertainty, and the8.12
conditional frequency ratio is not whole-data model odds. The A10g protocol
also makes concordance a hard pre-score gate, implements genuine joint S1,
and specifies censoring-aware calibration and orthogonal interpretation.
The original reasoning below is retained as proposal history, with those
claims superseded. No held-out observation was opened for this review.

## Verdict

I accept A10d and A10e as executed. The screen, the development fit and their
audits are sound, and I found no defect that requires a change before the
evaluation freeze. Codex's amendments to my A10c specification were
improvements, and I accept all of them. They are:

- fitting mark offsets with M2 held fixed, so the deployed fallback is the
  fitted one;
- six-year clusters chosen before any OC outcome;
- matched 58-year reference replicas instead of a 300-year mixture;
- the explicit split between a finite screen and a size certificate, which
  Barry settled in D022.

Three development-stage findings sharpen what the evaluation can mean:

1. The real development fit lies in the upper 2% of the gated null cases'
   development fits. It is typical of the stronger third of the injected-effect
   histories.
2. The real issuance ages put SS Cyg in the regime where measurement coupling
   pushes the duration coefficient negative. The directional bound therefore
   does its job here, although it is not a general theorem.
3. With the lagged mark at its bound, the simulator disfavours a slowly varying
   shared state by about 8 to 1. A shared state that decorrelates within a
   cycle or two cannot be distinguished in this way, so mechanism remains
   unidentified.

The reproducible numbers come from `scripts/a10f_development_calibration.py`
and are written to
[the calibration output](../../data/simulations/a10f_development_calibration_20261108.json).
The script reads the 360 retained A10d trial records and the committed A10e
summary. For issue ages it also reads the real development ledger, which is
pre-1960 and already consumed.

## 1. What the screen established

All gated no-effect cases pass the accepted ≤5% observed-rate screen. Pooled
over the 220 gated null histories, the confirmatory test confirms 3 times
(1.4%; exact one-sided upper bound 3.5%). The null, gross, offset and adaptive
cases share random streams, so this pooled bound understates uncertainty. It
is still the clearest single statement of the test's size in this simulator.

Calibration under the injected effect is a little optimistic. Joint-MC
containment of the two-sided 90% interval is 34/40, and 31/37 among interior
fits. That does not affect size, which the null rejection counts measure
directly. It does mean the reported interval runs slightly narrow when
duration actually changes forecasts. The evaluation protocol states this.

## 2. Codex's positive-artefact counterexample

Codex is right, and my A10c wording overstated the protection. A nonnegative
coefficient restricts direction; it does not remove every measurement
artefact. Codex's exact construction has constant true duration and late-age
survival selection, and still yields a positive fixed-baseline offset and a
positive gain.

The question for SS Cyg is which regime the real forecasts occupy. In the
1910–1959 development ledger:

| Quantity | Value |
|---|---:|
| Median issue age | 1.9 d |
| 90th-percentile issue age | 4.0 d |
| Issuances older than 10 d | 7 of 330 |
| Median previous gap | 40 d |
| 10th-percentile previous gap | 24 d |

At ages this small against gaps this long, the selection term in
Cov(Q, ε | â) − Var(ε | â) is negligible. The coupling is therefore negative,
as A10c argued, and the bound removes it. The gated null cases agree: none
confirms more than 2/40. The counterexample describes forecasts issued late in
quiescence, which this system does not issue. I withdraw the general claim
and keep the specific one.

## 3. The real development fit against the synthetic development fits

The real fit has β = 0.0466 per SD of log duration and an in-sample
likelihood-ratio statistic of 5.19 against M2, using 330 issuances. The table
counts the synthetic histories whose own 1910–1959-style development fit was
at least as strong.

| Synthetic case | Histories | LR ≥ 5.19 | β ≥ 0.0466 | Lagged β at zero |
|---|---:|---:|---:|---:|
| v2 independent null | 40 | 0 | 1 | 19 |
| v2 structured null | 40 | 0 | 0 | 27 |
| v2 gross reports | 40 | 3 | 3 | 19 |
| v2 persistent offsets | 40 | 2 | 2 | 19 |
| v2 adaptive effort | 40 | 0 | 5 | 21 |
| v4 independent null | 20 | 0 | 0 | 6 |
| v2 slow state, φ = 0.90 | 40 | 10 | 10 | 4 |
| v2 slow state, φ = 0.98 | 40 | 4 | 5 | 6 |
| v2 injected effect | 40 | 12 | 11 | 17 |
| v4 injected effect | 20 | 5 | 4 | 5 |

Across the 220 gated null histories, 5 reach the real statistic (2.3%; exact
95% interval 0.7–5.2%). The structured null is the most realistic of them,
because it has serial timing dependence and no direct effect. None of its 40
histories reaches the real statistic, and its largest β is 0.040.

The synthetic system has the right size. Its residual log-gap σ is 0.33–0.36
(real 0.346), its log-duration SD is 0.37–0.41 (real 0.383), and it has
320–340 development issuances (real 330). The OC study therefore describes a
forecasting problem of the scale actually faced.

The real β/σ is 0.135, against a synthetic injected-effect mean of 0.10. This
is an in-sample number, inflated by selection among fits like any development
estimate. It also comes from data inside CM92's pooled 1896–1992 sample. It is
not evidence for the confirmatory claim. It only says the frozen comparison
will not be identically zero, and that the development data look more like
the injected-effect and slow-state cases than like the nulls.

## 4. The real timing structure lies between the simulated modes

The real M2 has a previous-gap slope of 0.078 and a local-level slope of
0.051 (standardized).

| Cases | Previous-gap slope | Local-level slope |
|---|---:|---:|
| Structured and injected-effect | 0.11–0.12 (SD 0.025) | ≈ 0 (SD 0.02) |
| Slow-state | 0.02–0.03 | 0.04 |
| Real SS Cyg, 1910–1959 | 0.078 | 0.051 |

SS Cyg has more slow drift in its quiescent gaps than the v2 structured mode,
and less short-lag dependence. The slow-state cases are therefore the relevant
stress test for what a positive result can mean, not a remote one.

## 5. The lagged mark at zero

P3 fits β′ = 0 in every real variant, including the joint-valid one. Within
the simulator, I took the histories whose development M3 fit was at least
moderately strong (LR ≥ 2.71) and asked how often the lagged offset sat at
zero:

- injected effect: 11 of 21 (52%; exact 95% interval 30–74%);
- slow shared state at φ = 0.90 or 0.98: 2 of 31 (6%; 0.8–21%).

The likelihood ratio is about 8 in favour of a within-cycle link over a slow
shared state of the simulated kind (λ² = 0.13, persistence ≥ 0.9 per cycle).

That is the limit of what it shows. A common driver that decorrelates within
a cycle or two looks like direct memory in every timing statistic available
here. Physically, that is close to what disc-instability memory means anyway.
Codex's statement stands: M3−P3 cannot identify mechanism. The real P3 result
argues against a slow multi-cycle driver at this persistence. It argues
nothing beyond that, and it is development-stage evidence from a simulator
with a fixed loading.

There is one consequence for the evaluation design. Because frozen β′ = 0,
frozen P3 is identical to M2 on every evaluation forecast. The pre-declared
S2 contrasts therefore degenerate: P3−M2 is identically zero, and M3−P3
equals M3−M2 on joint-valid rows. On the evaluation block, state sensitivity
must come from the S1 refit, which estimates the current and lagged offsets
unconstrained on evaluation outcomes. The evaluation protocol says so before
access.

## 6. Precision going into the evaluation

The A10d power statement holds: 11/40 (27.5%; exact 95% interval 14.6–43.9%)
in the injected-effect case, and 6/20 for v4.

Conditioning on a development fit as strong as the real one hardly changes
it. Among v2 injected-effect histories with LR ≥ 5.19, 4 of 12 confirmed (33%;
exact 95% interval 10–65%), and among v4 histories 0 of 5. Within the v2
injected-effect case, the development LR correlates only 0.24 with held-out
gain. The honest figure is that the test has about one chance in three, at
best, of confirming an effect of the size the development data suggest.

Post-1960 visual coverage may be denser than the pre-1960 source patterns used
in the simulation, which would add forecasts. That stays unknown until access.

## 7. Spend the block now

I recommend opening 1960–2017 under the frozen protocol without further
development.

- No design change made before access can raise power materially. The limit
  is the number of SS Cyg outbursts in 58 years, not the estimator.
- Further development cannot use the block, and the development data are
  already consumed.
- The protocol fixes what each outcome means before access. That includes an
  informative negative: if the 90% upper bound falls below the injected-effect
  gain, the data disfavour an effect of the simulated size.
- 2018 onward stays reserved for replication with the same frozen system.
  More stars are the route to power (A05), and the frozen SS Cyg method is
  the template for them, each with its own development fit.

The alternative is to hold SS Cyg back and pool it with other stars later. I
judge that a worse use of the block. It would delay the first preregistered
predictive test of CM92's association for a larger project that has not been
designed yet, and it would not change the SS Cyg evidence.

## 8. Checks run

- I recomputed every per-case count in §3–5 from the 360 retained trial
  records, which match receipt `be0e25cd…`, and from the committed A10e summary
  and parameters. The real LR (5.1935) reproduces the A10e in-sample gain
  (0.00787 × 330 × 2).
- The issue-age summary uses the real 0.0 d development ledger, outside Git.
- I read but did not rerun the A10d and A10e audits. I made no change to
  forecasting, feature or extraction code.
