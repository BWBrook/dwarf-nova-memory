# G3a: the frozen multi-star expansion does not qualify

Codex, 10 November 2026; approved execution under D045 and source freeze
[`d827313`](https://github.com/BWBrook/dwarf-nova-memory/commit/d827313615ca1994070b668bffa605e6c2faee14).
All ten authorized development acquisitions and qualification runs completed.
**No star meets every frozen gate. G3b is not available under this proposal.**
This is a result about the frozen extraction/qualification transfer, not proof
that the archive cannot support any other scientific analysis.

## Access and verification

Barry approved G3a exactly: “yes, approved as proposed. Continue.” The
[authority](../../data/access/g3a_authority.json),
[execution protocol](../protocols/g3a-early-record-feasibility-v1.md) and code were
committed/pushed before any target resolver or observation request. Both
scientific-invariants and secrets checks passed on that freeze. All 580 local
tests passed, including 46 new offline tests for actual acquisition, timing,
qualification and eclipse failure modes.

The run retained **110 native payloads**: ten bounded identity responses and
100 bounded observation-window exports. There are **264,997 unique native
rows**, of which **183,538** are validated `Vis.` observations used here.
All dates/identities and native bytes were checked before scientific summaries.
Other native bands/flags stayed transport-only. No observer identity, raw row,
event catalogue or per-issuance real score is committed. Native payloads and
receipts remain under ignored `data/raw/g3a_20261110_d827313/`.

No new-star record, count or coverage information from 1990 onward was
requested. No SS Cyg archive request was made; its 2018+ records stay closed.
Native JD/limits/missing uncertainty strings remain unchanged. Historical
upload/revision availability is unknown; this is observation-time retrospective
work. Every request was source-date-limited; redirects were disabled before
they could drop those limits. Complete returned streams do not establish
complete historical observing opportunities.

The [independent execution audit](2026-11-10-g3a-execution-review.md) parsed
the retained native XML/CSV and request provenance independently, verified
source/raw hashes and deduplication, and rebuilt eight ordinary stars' X5/DF
counts using a separate mask over legacy feature/outcome APIs. It found zero
mismatches. The two holds' saved gate arithmetic was checked, without an
independent rerun of their synthetic guard. Optimizers and morphology were not
replayed independently. This is numerical/provenance concordance, not a second
extractor or validation of physical onset containment.

## Qualification result (C68, provisional for Claude)

Every star needs at least 40 outcome-supported, timing-supported marked DF
issuances, at least 70% eligible onset windows, stable nondegenerate unmarked
B0 fits, and no operational morphology failure. The two holds also need their
frozen eclipse guard. No threshold or gate was changed after seeing counts.

| Star | Supported development issuances | Eligible windows | Failed gates |
|---|---:|---:|---|
| SS Aur | 110 | 79.6% | Operational long-bright-run screen |
| RU Peg | 23 | 63.5% | Count, windows |
| AR And | 7 | 31.4% | Count, windows, base information/fit |
| X Leo | 35 | 44.0% | Count, windows |
| TW Vir | 0 | 11.6% | Count, windows, base information/fit |
| UU Aql | 15 | 80.8% | Count |
| CH UMa | 0 | 70.4% | Count, base information/fit |
| DX And | 0 | 70.8% | Count, base information/fit |
| U Gem* | 27 | 90.6% | Count, eclipse guard not qualified |
| IP Peg* | 0 | 66.7% | Count, windows, base information/fit, eclipse guard not qualified |

*The holds use the newly frozen fixed-night median stream and two-night
confirmations; they are not identical raw-report timing analyses. The brightest-
night reduction is an additional agreement gate. A base-information/fit failure
can mean insufficient usable information, not demonstrated optimizer instability
or an incorrect physical recurrence model.

SS Aur alone clears the numerical count/window/base gates. Its supported
threshold-bright run spans 100.97 days and triggers the predeclared ≥60-day
operational exclusion. That is not a diagnosis of a standstill or new subtype.
The source of this flag has not been adjudicated by independent annotation.
Even disregarding it would leave only one star clearing the count gate, far
below the approved six-star floor, so that adjudication cannot rescue G3b.

Both holds agree well between the two real-data reductions, but do not qualify.
U Gem's supported counts are 27/25, below 40. Its invented no-eclipse baseline
has median decisive-span error 2 days and 90th percentile 6 days, beyond the
frozen accuracy limits. IP Peg has zero supported marked outcomes and only
nine matched real spans; its baseline 90th-percentile span error is 2.3 days.
Both baseline synthetic screens are **inconclusive**. The 128 eclipsed profiles
were therefore not scored. Do not say that eclipse injection caused failure or
that the rule removed eclipse effects.

The aggregate/table, native hashes, details and frozen empty qualifying list are
in [`data/provenance/g3a_20261110/`](../../data/provenance/g3a_20261110/).
The acquisition manifest adds the 100 observation exports; bounded identity
payload hashes are retained in the native manifest. The independent checker
reports its shared-API and optimization/morphology limitations explicitly.

## Projected yield and stopping decision

The qualifying set is empty, so its projected yield is zero and neither the
28-year nor 36-year horizon meets the G3b request conditions. For perspective
only, **all ten stars ignoring every qualification gate** have 102 supported
issuances in 1980–1989. Assuming that rate transfers gives 285.6 over 28 years
or **367.2 over 36 years**, far below 1,100. These are planning extrapolations,
not observed future counts or a bound on a different extraction method.

Across the full development histories the current rules produce 217 supported
issuances from 1,777 confirmed episodes. This attrition includes eligibility,
covered previous gaps, decisive marks and usable outcomes, not a measured
absence of recurrence information. A star can have many reports while few
consecutive cycles have the required support. No joint duration–gap statistic,
mark coefficient or real forecast-gain comparison was computed. No pooled
effect fit follows an empty qualifying set.

The original catalogued thresholds are uncalibrated visual proxies, the full
historical record includes sparse eras, the seven-day coverage rule is strict,
and the eclipse branch deliberately delays/narrows its data. Those frozen
choices can limit transfer; the result must not be generalized to all possible
thresholds, development epochs or observation models. Changing them now to
reach six would be a new development specification, not a pass of this run.
Keep this failure intact.

## Six-star supplement (C69, provisional for Claude)

The same source freeze also precedes eight cases ×2,000 new deterministic
trials, all completed without a failed fit. No original R2d source/result was
changed. These are point-Gaussian simulations with nominal equal-count epochs,
not extraction/window-score/calendrical yield validation.

| Six-star case | Test issuances | Whole-star score rejection | Frozen-gain rejection |
|---|---:|---:|---:|
| Clean direct effect | 1,100 | 76.75% | 33.10% |
| Clean direct effect | 2,000 | 94.60% | 48.75% |
| Persistent/small development/missing marks | 1,100 | 59.40% | 21.30% |
| Common states/noisy marks/delayed labels | 1,100 | 36.15% | 10.25% |

Exact Monte Carlo intervals, nonidentity coverage, achieved predictable gains
and all procedures are in
[`six-star-summary.json`](../../data/provenance/g3a_preparation/six-star-summary.json).
Supported counts and achieved effects differ between cases. The six-star
1,100 clean association cell does not reach 80%; no robust precision guarantee
is established. The supplement contains estimated-base no-direct-effect cells,
not six-star strict-oracle size controls. Independent recount verifies all
16,000 seeds/trials and aggregates without new draws. Gain-without-score
rejections remain zero in these eight cells, an empirical property only.

## C67 and the sequence

The independent recount accepts zero gain-without-score rejections in the
original 70,000 trials, pooled strict-oracle score rejection 397/8,000 and the
binomial screen-failure calculations. My per-cell observed-rate≤5% screen was
too brittle as a calibration verdict: an exactly calibrated test passes all
four cells only about 7.7% of the time. I carried forward the point-rate rule
from Barry's earlier 360-trial screen decision; v1's attribution should not be
read as a separate user decision approving the larger R2d calibration rule.
Retain its frozen result, while using the Monte Carlo intervals to interpret
it. Pooling different cases does not certify each case or partial-null control.

An invented Gaussian counterexample has gain CR1 t=24.49 while score t=1.06;
nesting is not a theorem. Association then gain remains a sensible proposed
fixed sequence, but strong familywise control requires both marginal tests
valid under their own full nulls. The second includes real association with
nonpositive gain. No empirical-power identity is promised for the observational
study. See the [sequence review](2026-11-10-g3a-sequence-review.md).

## Handoff

**Do not request G3b.** Claude should review the failed transfer and the SS Aur
screen, then recommend whether a materially different observation/coverage
model is worth developing on the now-open early records, or whether the
SS Cyg paper should incorporate this failed expansion. Threshold/gate relaxation
is not an automatic remedy. Manuscript products stay paused pending that
scientific synthesis; no first data or paper release or outside contact occurred.

Reproduction uses new output paths, keeping all previous receipts:

```sh
python scripts/check_g3a_sequence.py --output outputs/new_g3a_sequence_check
python scripts/g3a_six_star_precision.py --freeze-commit d827313 --workers 4 --output outputs/new_g3a_sixstar
python scripts/check_g3a_execution.py --output outputs/new_g3a_execution_check
```

`scripts/g3a_report.py` regenerates the public aggregate tables from retained
run/receipt files without new requests or model fitting. Raw acquisitions
need not be repeated to reproduce qualification.
