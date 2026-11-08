# A10i: frozen SS Cyg forecast comparison, 1960–2017

Codex, 9 November 2026 (Hobart). **The predeclared primary rule is met.**
Across 441 forecast issuances, the frozen log-duration model improved the
log score over the specified frozen timing-only baseline by **0.01653 nats
per issuance**, with six-year-cluster **90% interval [0.00495, 0.02812]**.
The corresponding one-sided 95% lower bound is positive. There are ten
nonempty blocks (9 degrees of freedom), and the SE is 0.0063203.

This is an observational-time retrospective result for SS Cyg under the fixed
extraction, coverage and forecasting rules. The evaluation completed after
an outcome-independent **post-access native-format repair**. The first failed
attempt is preserved; the block cannot be described as untouched. Data from
2018 onward remain closed.

The later-era and functional-form qualifications belong beside the result:

| Predeclared comparison | Issuances | Gain, nats/issuance | 90% cluster interval |
|---|---:|---:|---|
| Primary, 1960–2017 | 441 | 0.01653 | [0.00495, 0.02812] |
| Secondary, 1960–1992 | 261 | 0.02398 | [0.00911, 0.03886] |
| Secondary, 1993–2017 | 180 | 0.00573 | [−0.01067, 0.02213] |
| Secondary, type/within-type rule | 441 | 0.00248 | [−0.00220, 0.00715] |

The later segment and the type/within-type rule are inconclusive. The era
intervals overlap; no change-point or interaction test was specified, so the
result does not establish a temporal disappearance. The early segment
also overlaps the record behind CM92's published association. It was held
out from this forecasting fit, while its historical association was already
known. The primary is the sole confirmatory comparison; none of the secondary
intervals replaces it or supplies an additional independent confirmation.

## What was fixed and executed

Barry chose “Zenodo first, then open (recommended)” after the implementation
and independent synthetic checks. [Protocol DOI 10.5281/zenodo.24053338](https://doi.org/10.5281/zenodo.24053338)
was published before archive access; its public file was downloaded and
verified against the approved package SHA-256. Original source freeze:
`fc409738222ded5a9bf78288c969e956b59d23f4`.

The first attempt failed before any ledger or primary result on exact native
`uncert="None"`. [D026 repair evidence](2026-11-08-a10h-native-format-repair.md)
shows that uncertainty is unused by every extraction, feature, evidence,
routing and score path. The repair accepts that exact missing-value token
without changing or dropping a row. Synthetic invariance, independent review,
344 tests, a new full rehearsal and supported-platform CI passed before
continuation. No real magnitude, outcome, event count, coverage summary,
coefficient or score informed the repair.

Repair freeze: `5e39aeb772c427ef29671c1a9c80b22c05519b58`; pushed authority
and execution commit: `d7151e0da48ce3d3f91e38d94b8bfdc656272dd0`. All 26
original forecasting source files, parameter bytes and protocol bytes remain
unchanged. Frozen parameter SHA-256:
`ce4ef8d59c6eb13c12633a4dcf1bab3cb57a1c5289d2913e03794631fcc44fb3`.
The DOI timestamps the original protocol, not its later format repair.

The saved chronology, all on 8 November 2026 UTC, is:

| Stage | UTC |
|---|---|
| Protocol published | 12:34:47 |
| Initial attempt began / failed before primary | 12:38:28 / 12:39:51 |
| Repaired acquisition began | 12:51:18 |
| Acquisition completed | 13:00:33 |
| Native verification completed | 13:00:35 |
| Candidate/reference concordance passed | 13:06:58.627 |
| Primary result written | 13:06:58.641 |
| Secondary diagnostics completed | 13:07:02 |

No person or agent inspected the real scores or intermediate outcome/count/
coverage summaries before the primary file existed. Afterward, separate
numerical, native-provenance and methodological reviews were completed.
There was no primary refitting, parameter updating, population substitution
or mismatch deletion.

## Primary verification and data scope

The independent serialized-output checker reproduces all **2,641 score rows**
across the six frozen variants, the primary interval, routing and five literal
fallback-zero issuances. Maximum score discrepancy is **1.91e-13**. It reports
zero failures and verifies all 120 receipt-bound source hashes, the exact
parameter/protocol hashes, prefix timing, populations and chronology. Both
candidate and reference ledger/evidence implementations match at both delays
before scoring. Common extraction assumptions remain; concordance does not
provide an independent physical truth catalog.

All 441 primary issuances are score-eligible: 435 interval-onset outcomes
and six right-censored outcomes (four coverage breaks, one supersession, one
record end). There are no ambiguous-survival exclusions. Timing models are
used on 436 rows and share M0 fallback on five; those zeros remain in the
primary mean. The predeclared upper-below-reference diagnostic is false. The fixed
simulation mean is 0.00451956 nats; its Monte Carlo uncertainty and model
specificity preclude a separate claim of exceeding a known physical effect
size. It was not a second confirmatory target.

The acquisition audit verifies 63 deduplicated evaluation-window leaves plus
four retained cap-parent responses. Leaf data contain 500,479 rows after
81 overlapping duplicate IDs are removed; 249,356 meet the visual-band,
V-validated analysis selector. These counts exclude the frozen pre-1960
context. That context was read for causal history; all twelve original native
hashes and the anonymous cache hash remain unchanged.

Every response hash, target identity, query bound and leaf row scope passes.
Leaves are below the 50,000-row cap (maximum 46,839); parent responses are
retained outside the analysis. A JD-only parent audit also passes every
requested bound and the strict 2018 cutoff. The last requested endpoint is
2458119.4999999995, exactly `nextafter(2458119.5,-inf)`. All headers retain
27 native columns and extra XML metadata; no time conversion is applied.
No 2018+ request or analyzed observation occurred.

## Named secondary analyses

All named diagnostics complete. Their gain intervals use the declared
construction and are secondary estimates:

| Variant | Issuances | Gain, nats/issuance | 90% interval |
|---|---:|---:|---|
| Primary: raw log duration | 441 | 0.01653 | [0.00495, 0.02812] |
| Uniform-end uncertainty | 441 | 0.01658 | [0.00445, 0.02871] |
| Previous-gap-only baseline | 441 | 0.01699 | [0.00537, 0.02862] |
| Two-day issuance delay | 441 | 0.01649 | [0.00494, 0.02805] |
| Joint-valid population | 436 | 0.01672 | [0.00490, 0.02855] |
| 12-day type and within-type | 441 | 0.00248 | [-0.00220, 0.00715] |
| Three-year clustering | 441 | 0.01653 | [0.00585, 0.02722] |

The frozen timing baseline itself improves over M0 by 0.11676 nats/issuance
[0.06633,0.16719]. This supports a comparison beyond the constant baseline.
The duration result remains specific to this measured-history M2; it does
not establish improvement over every plausible activity or latent-state model.
Frozen P3 equals M2 because its development lag coefficient is zero. The
joint-valid population removes the five fallback rows and is not a separate
confirmation.

Evaluation-only S1 fits are signed and conditional on their fixed evaluation
M2 nuisance parameters. The intervals below are working likelihood support
(LR cutoff 3.841), without dependence/measurement calibration:

| S1 offset | Estimate | Conditional support |
|---|---:|---|
| Current duration, fitted separately | 0.04209 | [0.01574,0.06845] |
| Previous duration, fitted separately | −0.03836 | [−0.06489,−0.01184] |
| Current duration, genuine joint fit | 0.03045 | [−0.00063,0.06152] |
| Previous duration, genuine joint fit | −0.02213 | [−0.05340,0.00913] |

The joint design has rank 2 and condition number 1.79; both coefficient-specific
support intervals include zero. These diagnostics do not identify memory,
causation or a unique shared-state explanation. The primary also does not
establish a within-outburst-type effect; the specified type/within-type
forecast rule has an interval spanning zero.

S5 describes absolute calibration with observational uncertainty and censoring.
M3's empirical coverage bounds are 54.6–61.7% for nominal 50% intervals and
92.3–98.0% for nominal 90% intervals. These are partial-identification bounds
for observed coverage, not confidence intervals for a population coverage
rate. They indicate overcoverage in this sample; the positive paired score
does not imply sharply calibrated operational forecasts. Selected-onset
mid-CDF deciles remain descriptive, with no PIT-uniformity test. S6's fixed
block inventory and standardized-feature summaries are retained in the
compact evidence.

## Interpretation and remaining limits

The supported claim is **incremental predictive information from the extracted
current log duration, relative to the specified frozen timing model, in this
SS Cyg retrospective evaluation**. Physical memory, a mechanism, transport to
other stars, and confirmation in the later era remain unestablished. The
period and functional-form sensitivities must stay visible in any paper.

Inference uses ten six-year clusters and assumes they adequately capture
dependence; longer nonstationarity remains possible. Three-year sensitivity
is consistent but cannot establish that assumption. The earlier finite
simulation screen did not certify a true 5% error rate; injected-case interval
containment was 85%. Historical upload/revision availability is unknown,
so this is observation-time retrospective rather than operational replay.
Selection by X4, magnitude 10, C1/7-day coverage and archived visual validation
remains part of the estimand. Informative observing, missed outbursts,
endpoint coupling and incomplete measurement-error propagation remain limits.

## Evidence and reproduction

The [primary result](../../data/provenance/a10i_evaluation_1960_2017/primary.json),
[compact aggregate summary](../../data/provenance/a10i_evaluation_1960_2017/summary.json),
[independent score audit](../../data/provenance/a10i_evaluation_1960_2017/audit.json),
[native audit](../../data/provenance/a10i_evaluation_1960_2017/native-audit.json),
[derived run receipt](../../data/provenance/a10i_evaluation_1960_2017/run-receipt.json)
and [manifest](../../data/provenance/a10i_evaluation_1960_2017/manifest.json)
are committed. Reproduce the saved-score audit against the retained completed
run, without requesting another archive period:

```bash
python3 scripts/check_a10g_evaluation.py --directory outputs/a10h_live_repair_5e39aeb --output outputs/a10i_reproduction_audit.json
```

The internally retained archive has 184 inventoried payload files plus its inventory (132,501,444
payload bytes before compression), including raw replies, source at execution, original context/
cache, complete event/score/profile outputs, environment and the failed
attempt. Whole archive SHA-256:
`8e9d626904ba5e680f76122b10de5e01ba01a19302ec2c6da3cfffacc20c5884`.
Every member and transferred archive hash was checked, with archive mode 0600.
The [archive manifest](../../data/provenance/a10i_evaluation_1960_2017/archive.json)
records this retention. No raw observations, observer identities, new event
catalog or per-issuance scores are released. No result DOI or manuscript
release is made in this turn; the published DOI is the protocol only.

Next: Claude — independently review the real result and frame the paper with
the era, type/within-type and mechanism limitations beside the headline.
