# Step 1a: working abstract

Amended after Codex's review (10 November 2026): hypothesis names and the transfer wording.

A working document for reconstructing the paper from first principles (Barry's method, 10 November
2026). It is not for submission. Every later step should be checked against it. Claim IDs in
parentheses point to `manuscript/claims.csv`; `manuscript/estimands.md` governs the wording.

## Why are we doing this?

Dwarf novae are the archetypal disc-instability system. Whether a completed outburst carries
information about the next one has been studied by in-sample correlation but, to our knowledge,
never tested with preregistered held-out forecasts (C40, C41).

## What are the aims?

**Core:** does a completed outburst's duration improve probabilistic forecasts of SS Cygni's next
onset beyond recent recurrence history?

**Sub-goals:**
- test how robust any gain is to the way outbursts are measured;
- test whether other dwarf novae can support the same test.

## What hypotheses underpin them?

- **Depletion hypothesis:** longer outbursts drain more of the disc, so at a comparable gas-supply
  rate the next quiescence lasts longer. Duration should then add forecast skill beyond recent gaps.
  (No specific following-gap prediction was found in Cannizzo 1993; the hypothesis is ours.)
- **State hypothesis:** duration tracks a slowly varying accretion state that recent gaps describe
  incompletely. This predicts added skill only if duration carries state information beyond the
  timing covariates.
- **Rival, measurement:** a shared estimated end time couples duration to the next gap without any
  physical link.

## What did we do?

- Extracted outbursts from AAVSO visual estimates.
- Fitted lognormal recurrence forecasts on 1910–1959, froze them, published the protocol, then
  scored held-out forecasts for 1960–2017.
- Afterwards: measurement-sensitivity checks, simulations, and a frozen feasibility screen of ten
  other stars.

## What did we find?

- Duration raised the held-out working score by 0.0165 nats per forecast (90% interval
  0.0049–0.0281; 441 forecasts), meeting the preregistered criterion (C01).
- Measurement redesigns were positive but inconclusive (C55).
- No other star's record qualified under our frozen rules (C68).

## What do the results mean?

In SS Cyg, duration adds a little forecast information beyond recent timing, as measured by our
working score. That is consistent with disc depletion or a slow state, but measurement coupling is not excluded,
and generality is untested.

## What is it good for, and how does it generalise?

It is a template for preregistered, frozen forecast tests on long, irregular, human-collected records
of recurrent events, such as outbursts, eruptions and outbreaks. It is also a cautionary case. The
test ran on SS Cyg's near-complete record but on none of ten candidates' records under the same rules
(C70). Separating signal from measurement needs an explicit observation model.

## What writing this exposed

- **The core result is modest.** The paper's wider value lies in the method and in what the record
  could and could not support. The structure should show that, rather than read as a list of
  sensitivity checks.
- **The depletion and state hypotheses both predict a positive gain, and the design cannot
  separate them.** The introduction
  should say so and frame the test as "is there forecast information?", not "is there memory?".
- **The measurement rival is the real competitor to both hypotheses.** The reassessment exists to
  address it, and it ends inconclusive. That is the honest centre of the discussion.
- **The transfer screen answers the second sub-goal:** the qualifying cohort was empty under the
  frozen transfer rules, and SS Cyg's 1980s record yielded far more usable forecasts per outburst
  than the candidates' (C70).
