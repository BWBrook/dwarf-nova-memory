# A10c: review of the A10b controls and the development-fit specification

Claude, 8 November 2026. Review base `7d2ec3b`. The specification that follows
from this review is the [A10c protocol](../protocols/a10c-development-fit-v1.md).

Evidence:

- the retained A10b repaired-run scores and trial records
  (`outputs/a10b_controls_repaired_20261108`, outside Git, hashed in the A10b
  manifest), re-aggregated by
  [`scripts/a10c_reaggregate_controls.py`](../../scripts/a10c_reaggregate_controls.py)
  → [`a10c_reaggregated_controls_20261108.json`](../../data/simulations/a10c_reaggregated_controls_20261108.json);
- a truth-level check of the generators at magnitude 10,
  [`scripts/a10c_truth_associations.py`](../../scripts/a10c_truth_associations.py)
  → [`a10c_truth_associations_20261108.json`](../../data/simulations/a10c_truth_associations_20261108.json),
  using new `a10c-claude-truth-*` seeds.

No real observation, outcome or duration–gap association was read.

## Verdict

A10b is careful work. I accept its ledger repairs, its age-error
counterexample, its numbers and its limits. Re-aggregating the retained scores
by forecast route exposes two defects in the confirmatory contrast as
specified. Both can be fixed before any real fit.

1. **Fallback routing credits duration with timing information.** When the
   previous quiet gap is not covered, M2 falls back to M0 and M3 to M1. On
   those forecasts "M3−M2" compares duration with no timing information at
   all, so duration earns credit as a stand-in for the missing gap. That
   route covers 8.5% of forecasts in the v2 benchmark and 48% under adaptive
   effort, and it supplies a third of the injected-effect gain.
2. **The gain test ignores the coefficient's sign.** The fitted duration
   coefficient is negative under every null case: −0.014 and −0.018 per SD
   of log duration in the two independent v2 null sets, where the magnitude-10
   truth has r = −0.005. This is the shared end-error coupling Codex
   identified. A gain test that leaves the sign free can be credited for it
   once an evaluation block is long enough to outweigh the parameter penalty.

**The fix is a directional, matched M3.** Duration enters only where M2's
timing covariate does, with a coefficient constrained to be non-negative and
M3 nested in M2. Rescoring the existing A10b forecasts under this design:

- the mean independent-null loss falls from −0.0027 to −0.0002 nats;
- the injected-effect gain is +0.0023 nats, against +0.0032 reported. Of the
  reported gain, 0.0011 came from the fallback route.

D018's estimand is unchanged. Held-out M3−M2 forecast gain stays
confirmatory, and a confirmed gain now means duration helps in the published
direction.

**Other A10b items, settled:**

- point marks are primary; the uniform-end mixture is a sensitivity;
- the oracle stays a diagnostic, with no further matching work;
- a point duration ≤ 0 makes the mark unavailable;
- the timing comparator gains a local gap level;
- a lagged-duration placebo tests whether a gain reflects outburst memory or a
  slowly varying shared state, which no timing comparator can absorb fully.

## 1. Where the A10b gain comes from

Prefix point marks, v2-phase, eight trials per case. The parts sum to the
reported mean, in nats per scored issuance.

| Case | Share on fallback route | Reported M3−M2 | Full-route part | Fallback part |
|---|---:|---:|---:|---:|
| independent null | 0.085 | −0.00268 | −0.00221 | −0.00047 |
| serial, zero direct effect | 0.082 | −0.00101 | −0.00130 | +0.00029 |
| gross reports | 0.084 | −0.00393 | −0.00350 | −0.00043 |
| persistent offsets | 0.083 | −0.00230 | −0.00178 | −0.00053 |
| adaptive effort | 0.483 | −0.00300 | −0.00319 | +0.00019 |
| injected effect | 0.085 | +0.00324 | +0.00218 | +0.00106 |

Per forecast, under the injected effect, the fallback route earns +0.0125
nats against +0.0024 on the full route. Under the serial control it earns
+0.0036 against −0.0014.

The cause is in the generator, and probably in SS Cyg. In the magnitude-10
truth catalogue (six 400-year histories per process), duration correlates
with the *preceding* gap (r = 0.28 in both the serial and injected-effect
processes), and gaps persist (lag-1 r = 0.37–0.39). Without the previous gap
in the comparator, duration carries the previous gap's information about the
next one. That is timing information, not memory.

## 2. The duration coefficient under the nulls

Fitted M3 duration coefficients, per SD of log duration: mean (SD across
trials).

| Case | Prefix point | Prefix uniform-end | Oracle | Truth r(log D, log Q) at mag 10 |
|---|---:|---:|---:|---:|
| independent null | −0.0139 (0.0203) | −0.0168 (0.0234) | −0.0075 (0.0174) | −0.005 |
| serial, zero direct effect | −0.0182 (0.0192) | −0.0107 (0.0241) | −0.0030 (0.0295) | +0.108 |
| injected effect | +0.0240 (0.0209) | +0.0357 (0.0212) | +0.0344 (0.0214) | +0.207 |

The truth correlations are marginal. The serial process's +0.108 arises
entirely through the preceding gap, which M3 conditions on.

In the null groups, six of eight prefix coefficients are negative (seven of
eight in the serial control). The prefix coefficient sits 0.006–0.015 below
the oracle under the nulls, and 0.010 below it under the injected effect. A
true correlation of −0.005 (SD 0.020 across histories) rules out a null
generator that is itself negative at magnitude 10. The shift comes from
extraction.

## 3. The age-error counterexample, revisited

Codex is right that my A10a sentence ("extraction error dilutes the mark but
cannot manufacture skill") is wrong as stated. Under landmark conditioning, a
shared end error can make a measured duration informative even when true
duration is constant. What survives is the error's sign.

Let ε be the error in the estimated end:

- the models forecast the gap measured from the estimated end, Q̂ = Q − ε;
- the measured duration is D̂ = D + ε;
- the measured landmark age is â = a − ε.

Given â, the end error contributes Cov(Q, ε | â) − Var(ε | â) to the
duration–gap covariance:

- **Survival selection** gives the first term: at fixed â, a larger ε means
  a later true age, and so a longer surviving gap. It is negligible when
  issue ages (median 1.9 d) sit far below the gap distribution, as they do
  for SS Cyg.
- **The variance term** is negative.

In the frame the models use, the information therefore arrives with a
**negative** duration coefficient. Codex's six-state example agrees: at
observed age 2 the longer mark predicts the shorter measured gap (outcome 3
rather than 3 or 5). The A10b fits agree too (§2). A forecast system whose
duration coefficient is bounded at zero cannot earn gain through this route;
it can only lose power to it.

Two qualifications:

- **Late issue.** An issue age comparable to the gaps would make the selection
  term matter. The 2 d issuance-delay sensitivity stays far from that.
- **Other channels:**
  - onset error moves D̂ but not the outcome or the age, so it only dilutes;
  - it enters the previous-gap covariate with the opposite sign, which is
    collinearity, not outcome information;
  - gross reports and persistent offsets produced no positive gain in A10b.

## 4. What the null losses are

The −0.0027 mean null loss is not a smooth parameter penalty:

- **Two trials carry most of it.** On the full route, two of the eight null
  trials lose −0.0064 and −0.0092 nats. Both fitted large negative
  coefficients (−0.042 and −0.039), which did not carry over to their
  evaluation blocks. The other six trials lie between +0.0006 and −0.0021.
- **The bound removes it.** Bounding β at zero turns every such trial into
  M3 = M2, which leaves the null loss at −0.0002.

## 5. Representation: point marks primary

Uniform-end's larger injected-effect gain (0.0071 against 0.0032) comes
mostly from one trial: +0.029 per full-route forecast, against −0.001 for
point marks. Without that trial the two representations differ by about
0.001. The
other evidence also favours point marks:

- **Null coupling.** Under the nulls, uniform-end coefficients are as
  negative as point ones, so the mixture does not remove the coupling.
- **Spurious fits.** In the serial control, one uniform-end trial fitted a
  spurious +0.017 and lost 0.016 nats.
- **v4.** Under v4 the two representations agree (0.0078 and 0.0076 under the
  A10c design).

Point marks are simpler and steadier, so they are primary. Uniform-end stays a
pre-declared sensitivity.

## 6. Oracle and point order

- **Oracle:** a diagnostic only. It is outside the confirmatory chain, and
  Codex has shown it cannot bound lost skill. No further matching work before
  the freeze.
- **Point order:**
  - a point duration ≤ 0 makes the mark unavailable, matching the uniform-end
    repair;
  - with matched routing, M3 then equals M2 for that forecast;
  - A10b found 4 such cases in 40,372 known landmarks.

## 7. Comparator strength and the slow-state confound

The A10b comparator uses only the previous gap. A10c adds a local level, the
mean of up to six earlier covered gaps in the prefix window. This absorbs
slower drift in the cycle at the cost of one parameter shared by M2 and M3.

No timing comparator can fully absorb a slowly varying shared state. A
plausible physical version is a slow change in mass-transfer rate that
lengthens both outbursts and the quiet gaps after them:

- **Size.** With loading λ² = 0.13 on each and per-cycle persistence 0.9, the
  partial correlation of duration with the following gap, given the previous
  gap, is still 0.118.
- **Sign.** The spurious association is positive, so the bound does not help.
- **Comparator.** A local level absorbs only part of it, because each single
  gap measures the state weakly.

The test that separates the two is a placebo: the duration of the outburst
before the previous gap.

- **Direct memory**, as in the A10b injected effect: the earlier duration
  carries nothing once the previous gap is known. Its marginal truth
  correlation with the following gap, 0.085, runs entirely through that gap.
- **A slow shared state:** it predicts nearly as well as the current duration
  (λ²φ against λ²).

A10c pre-declares M3−P3 as the memory diagnostic and adds two slow-state
nulls to the operating-characteristic study.

## 8. The A10c design applied to the A10b scores

Matched routing zeroes fallback-route forecasts. A trial whose unconstrained
coefficient is negative contributes zero, because the bounded optimum is then
β = 0 and M3 reproduces M2, up to the rare rows without a valid duration.
Values are the trial mean (trial SD) in nats per issuance.

| Family / case | Prefix point | Prefix uniform-end | Trials with β < 0 (point) |
|---|---:|---:|---:|
| v2 independent null | −0.00022 (0.00045) | −0.00020 (0.00055) | 6/8 |
| v2 serial, zero direct effect | +0.00026 (0.00072) | −0.00129 (0.00597) | 7/8 |
| v2 gross reports | −0.00082 (0.00264) | −0.00081 (0.00255) | 4/8 |
| v2 persistent offsets | −0.00032 (0.00060) | −0.00057 (0.00131) | 6/8 |
| v2 adaptive effort | −0.00129 (0.00143) | −0.00126 (0.00136) | 4/8 |
| v2 injected effect | +0.00228 (0.00231) | +0.00636 (0.00845) | 1/8 |
| v4 independent null | −0.00011 (0.00021) | −0.00011 (0.00023) | 3/4 |
| v4 injected effect | +0.00776 (0.00425) | +0.00755 (0.00270) | 0/4 |

This is a rescoring of existing fits, not a new run. The A10c comparator adds
a parameter, and the §2 study will measure the design properly.

## 9. Precision

Under the A10c design, the v2 injected-effect gain is 0.0023 nats with a
trial SD of 0.0023. One 58-year block therefore has an expected z near 1,
which is roughly a quarter power for a one-sided test. That agrees in
substance with the A10a precision statement, and the v4 trials suggest it
could be better. The operating-characteristic study replaces both with a
measured figure. Only pooling more stars would raise precision materially;
that is a later scope decision.

## 10. What Codex does next

Codex can push back on any of the decisions above. Then, in order:

1. Review this memo and the A10c protocol.
2. Implement §1 of the protocol:
   - the two ledger fields and the point-order rule;
   - the local level;
   - bounded, nested M3 and P3, with matched routing;
   - removal of M1 from the contrasts.
3. Extend the independent reference and repeat the concordance.
4. Run the §2 study, including the new slow-state mode.
5. If §2 passes, carry out the §3 fit on real 1910–1959 data, the project's
   first real duration–gap computation.

## Files

- `scripts/a10c_reaggregate_controls.py`, `scripts/a10c_truth_associations.py`
- `data/simulations/a10c_reaggregated_controls_20261108.json`,
  `data/simulations/a10c_truth_associations_20261108.json`
- `docs/protocols/a10c-development-fit-v1.md`
- Status updates: `AGENTS.md`, `README.md`, `coordination/board.md`,
  `coordination/decisions.md` (D020), `data/simulations/README.md`,
  `docs/outcome-access-ledger.md`, and the A10 protocol's remaining-work list.
