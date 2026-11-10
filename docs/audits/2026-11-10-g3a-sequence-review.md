# G3a: independent C67 recount and fixed-sequence conditions

Codex, 10 November 2026. Reads Claude's R2d review and the retained synthetic
JSONL files; no observation, archive request or new Monte Carlo trial. The
implementation is `scripts/check_g3a_sequence.py`; its small aggregate receipt
is `data/provenance/g3a_preparation/sequence-check.json`.

## Verdict

C67's arithmetic is supported. Its general power and familywise-error wording
needs narrowing before the G3b design is frozen. Recommend: **the sequence
preserved every forecast-gain rejection in the retained screen; strong
familywise control requires both marginal tests to control their respective
nulls, including the partial-null configuration.** This does not establish
zero future power cost or finite-sample validity of CR1/t on real records.

## Independent route and results

The checker validates every retained file against its receipt, all six frozen
source hashes against `git show 67c45ab`, the published/retained summary and
receipt bytes, and all expected case/replicate/seed identities. It recomputes
rejections from each saved estimate, SE and independent Student-t critical
value rather than trusting the saved rejection flags. Binomial intervals use
tail inversion; the screen-failure calculation uses an elementary PMF
recurrence. Neither Claude's checker nor the candidate/runner is imported.

- All 35 cases and 70,000 distinct successful trials reproduce; no failure.
- Gain without score rejection: **0/70,000** for both whole-star and star-half
  CR1/t. Every case therefore has the same observed stand-alone gain and
  fixed-sequence gain rejection counts.
- Clean eight-star N=1,100: whole-star gain and joint rejection are both
  **733/2,000 = 0.3665**; score rejection is 1,636/2,000 = 0.818.
- Strict-oracle whole-star score counts, in clean/persistent order: four-star
  **93, 96** and eight-star **97, 111**. Pool: **397/8,000 = 0.049625**;
  binomial-reference MC95 interval **[0.0449685, 0.0546130]**.
- An exactly 5% procedure exceeds 100 rejections in 2,000 independent trials
  with probability **0.473429061459**. At least one of four independent cells
  does so with probability **0.923117491160**. Those calculations reproduce
  Claude's values; they are not evidence that a systematically excessive size
  should be tolerated.

Pooling estimates the equal-weight average over these four settings. It does
not establish a per-setting maximum or certify real-data size. The quoted
exact binomial interval assumes a common Bernoulli probability; with different
cell probabilities it is a binomial-reference interval. All per-cell intervals
are retained in the aggregate.

Current source drift is one explicitly recorded CI-only test change:
`tests/test_r2d_simulation.py` now compares floating permutation fields within
1e-12 while retaining exact labels and counts. All functional sources match
the original freeze. The first precision run is unchanged.

## The fixed-sequence proof, including partial nulls

Let R1 be rejection of the association null at alpha, and R2 the stand-alone
forecast-gain rejection at alpha. The procedure rejects association on R1 and
gain only on R1 intersect R2. The order and both claims must be fixed before
sealed scores. No independence between the tests is required.

| True nulls | Event producing any false claim | Required bound |
|---|---|---|
| Association and gain | R1 | P(R1) <= alpha |
| Association only | R1 | P(R1) <= alpha; this configuration may be absent in particular models |
| Gain only; association is real | R1 intersect R2 | <= P(R2) <= alpha |
| Neither | Empty event | 0 |

Thus strong FWER is at most alpha **if each marginal test is valid across its
own full null, including nuisance/partial-null configurations and the declared
development/cohort selection**. Conditional calibration of stage two after
stage-one rejection is not needed for this proof. It is incorrect to say
general FWER equals the pooled association size. Equality to the association
rejection probability holds when the association null itself is true.

The development-overshoot scenario illustrates the gain-only null concern:
all 2,000 trials have positive predictable score and nonpositive predictable
gain. Mean predictable gain is -0.02871574; whole-star association rejects
1,497 times while gain/joint rejects once. This is a useful specific stress,
not certification over every gain-null configuration or over conditional
subsets of random paths.

## Zero observed power cost is not an algebraic implication

For Gaussian rows with frozen b=1, the identity is
gain_i = score_i - information_i/2. It does not force an ordering of CR1/t
statistics because their SEs differ. An invented four-star example has six
identical rows per star, variance one, information `[0.1,0.1,0.1,20]`, and gains
`[0.09,0.10,0.11,0.10]`. Set z to square-root information and choose the
residual so the Gaussian identity holds. This is algebra, not an extra grid.

| Clustering | Gain t | Score t | One-sided 5% critical |
|---|---:|---:|---:|
| Whole star | 24.4949 | 1.0603 | 2.3534 |
| Star halves | 37.4166 | 1.6196 | 1.8946 |

Gain rejects and score does not under both rules. C67 must retain its empirical
qualification. The fixed sequence can lose gain rejections outside the tested
grid; it still controls multiplicity under the conditions above.

## Six-star preparation, deliberately unrun

`data/provenance/g3a_preparation/six-star-design.json` and
`scripts/g3a_six_star_precision.py` prepare eight cases, 2,000 trials each:
clean null/effect at N=1,100 and 2,000; persistent and common-delayed
null/effect at N=1,100. They change only star count and case IDs from the named
eight-star R2d cases, use a fresh seed namespace, reuse frozen R2d methods,
and add joint-sequence counts. Execution requires an explicit source freeze;
none was run during this review.

The eight cells do not include a six-star strict-oracle null. If six-star
type-I behavior is needed, add its clean/persistent oracle controls before
freezing. The supplement remains a point-log-gap study, with no X5 or real
calendar-yield guarantee. G3a development access does not authorize G3b or
SS Cyg 2018 onward.
