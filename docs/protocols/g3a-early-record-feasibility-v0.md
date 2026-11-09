# G3a v0: early-record feasibility opening for a multi-star test

Claude, 9 November 2026. A proposal for Barry's decision. Codex freezes the implementation
before any request. It follows the [R2d review](../audits/2026-11-09-claude-r2d-review.md)
(D044).

## The question it answers

Can the AAVSO archive support a sealed multi-star test of the duration association?
- R2d shows that star count dominates: about 82% power for the association claim with eight
  clean stars at 1,100 test forecasts, 66% with four.
- No new star's coverage, extraction quality or forecast yield has been measured. G3a measures
  them from development-period records only.
- It reveals nothing from the test period.

## What would be opened

- **Stars.** The eight catalogue nominees (C52): SS Aur, RU Peg, AR And, X Leo, TW Vir, UU Aql,
  CH UMa and DX And.
  - Also the two holds, U Gem and IP Peg. They are eclipsing, and qualify only under an
    eclipse-handling rule that Codex freezes before their extraction runs.
  - Excluded: Z Cam/SU UMa/WZ Sge subtypes, southern BV Cen and SS Cyg.
- **Records.** AAVSO International Database visual (`Vis.`) reports carrying the validation flag V, with
  JD < 2447892.5 (1 January 1990, 0h UT), requested through the same VSX endpoint and
  date-bounded `fromjd`/`tojd` parameters used for SS Cyg. Nothing on or after the split is
  requested, counted or summarized for any star.
- **Why 1990.**
  - Development keeps the 1970s–1980s growth in dwarf-nova monitoring, while 1990 onward stays
    sealed as test data.
  - The association test needs only the B0R base (four parameters per star) and mark
    standardization from development. A longer test period serves it better than a longer
    development period.
  - The date is chosen without reference to any star's records.
  - The test end date (2018 or later) is a G3b decision.

## Measured, all aggregate and free of gains or associations

Per star, development period only:
- reports, observer-nights per year and the faint-limit fraction;
- seasonal coverage;
- X4 confirmed outbursts at the star's threshold and margin (catalogue proposals, refinable on
  development), and X5 window availability and eligibility;
- DF-scheduled issues, decisive marks, covered previous gaps, and therefore **timing-supported
  marked development forecasts**;
- B0 convergence across declared starts;
- a morphology screen: long-plateau episodes that would suggest standstills or superoutbursts.

No duration–gap relation, β or score is computed until the qualifying set is frozen.

## Frozen rules, set before opening

**Star qualification.** All of the following on development records:
1. at least 40 timing-supported marked DF forecasts;
2. an X5 eligible-window fraction of at least 0.7 among confirmed outbursts;
3. B0 converges at every declared start, with no degenerate parameter;
4. no morphology-screen failure;
5. for U Gem and IP Peg only, the frozen eclipse rule passes.

**After qualification:**
- the qualifying set is frozen;
- base and pooled β are fitted on development;
- star thresholds, margins and all G3b choices are frozen.

**Projected test yield.** Each star's supported-forecast rate over its last ten development
years, multiplied by the test length chosen at G3b. A planning assumption, never an observed
test count.

**Go/no-go for asking Barry for G3b (test opening).** Both conditions:
- **at least six qualifying stars** (the exact sign-flip becomes possible; Codex adds six-star
  R2d cells first);
- **at least 1,100 projected supported test forecasts**, with no star above 40% weight.

Otherwise G3a is reported as an archive-feasibility result. Any extension (southern stars,
other subtypes, a later split) needs a new decision.

## Claims if it proceeds (R2d review)

Fixed sequence:
1. Whole-star association (score moment at the B0R base, guarded DF span), one-sided 5%.
2. If that rejects, D018's forecast gain, one-sided 5%.

In all 70,000 R2d trials gain never rejected without association. The sequence therefore costs
the forecast claim no power, while the association claim gets about twice the power or more. Neither claim
identifies a mechanism.

## Cost and risk

- **Cost:** one bounded data request per star window, and a day or so of Codex legwork on
  extraction and qualification.
- **Risk:**
  - it ends development-period blindness for these ten stars, which is the intended use;
  - it commits to nothing beyond reporting the feasibility result;
  - it reads no test data.
- AAVSO data are public. Observer credit follows the pending observer-credit review.
