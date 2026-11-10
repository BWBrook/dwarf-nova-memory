# C71: independent SS Aur threshold-run reconstruction

Codex delegate, 10 November 2026. **The numerical result reproduces; the
physical interpretation needs narrowing.** The flagged threshold-night
component contains multiple groups of decisive-bright reports, rather than
establishing a single sustained plateau. Neither those groups nor the
threshold-proximate estimates identify physical outbursts or their cause.

## Independent reconstruction and scope

`scripts/check_ss_aur_flag.py` reads only the eleven retained SS Aur XML
payloads named in the G3a native manifest. It verifies every payload hash,
target name/AUID, requested native date boundary and returned row boundary,
then deduplicates observation IDs and selects native `Vis.`/V rows. It makes
no network request. No other target, later-period row, duration–gap relation,
model fit or forecast score enters the calculation.

The delegate read Claude's review and reported aggregate values. Its checker,
the frozen morphology implementation and previously selected run membership
were not imported or used. The new script independently rebuilds each
observer's .15-day visits from native reports, taking positive medians and
preserving all-limit faint votes. It reconstructs night runs with two graph
operations: adjacent non-faint observed nights within seven days form
components; components lacking a bright-majority night are removed; retained
components within three nights are joined. Support then requires ten bright
nights, two observers and no internal informative spacing above seven days.
The longest supported component is located from this reconstruction.

Three invented graph fixtures check short-gap merging, long-gap splitting and
the removal of mixed-only components before bridging. Native and script
hashes accompany the retained public aggregate. Event times, source report
membership and observer identities remain in ignored output only.

## Reproduced quantities

| Quantity | Independent result |
|---|---:|
| Longest supported threshold-bright run | 100.9700000002 days |
| Supported threshold runs; runs at least 60 days | 111; 1 |
| Votes inside the flagged run | 258 |
| Positive observer-visit medians | 252 |
| Threshold-bright; faint votes | 213; 45 |
| Positive-magnitude quantiles, 10%, 50%, 90% | 12.5, 13.2, 13.7 |
| Nondecisive threshold-bright positive votes | 176/252 = 0.6984126984 |
| Decisive-bright nights; groups separated by more than seven days | 16; 4 |
| Nights per decisive-bright group | 1, 7, 3, 5 |
| Record-wide positive native reports fainter than threshold: median | 14.5 |

The reported start-year check also matches. The fraction's exact band is
**12.5 < m ≤ 13.5**, with denominator 252 positive observer-visit medians.
It is the nondecisive subset of threshold-bright votes. The closed band
12.5 ≤ m ≤ 13.5 instead contains 75.0%; a phrase such as “within one magnitude
brighter” leaves this boundary ambiguous. These are aggregated visit estimates,
not 252 independent photometric measurements or necessarily 252 raw reports.

## Interpretation amendments

The four groups are an algorithmic property of decisive-bright report nights.
One consists of a single night exactly at the decisive cutoff. Without an
independent annotation, this does not establish four ordinary physical
outbursts. The plot and night structure do support describing the long flag
as a component bridged by numerous reports near the chosen threshold, rather
than an independently demonstrated continuous plateau.

The record-wide 14.5 comparison is descriptive. It is conditioned on reports
being fainter than 13.5 and pools other years and observers. It is not an
observer-matched or same-era estimate of the true quiescent state. These
calculations cannot establish a comparison-sequence change, observer offset,
calibration contamination, intrinsic brightening or subtype. In particular,
“photometric rather than morphological contamination” exceeds the evidence.

C71 can be supported with the numerical definitions and these limits. The
frozen morphology failure remains part of G3a, and the run is not reclassified
or removed from that recorded result. Nothing here rescues a multi-star cohort
or authorizes new access.

## Reproduction

```sh
uv run --frozen --extra analysis python scripts/check_ss_aur_flag.py \
  --output outputs/g3a_ss_aur_audit/reproduction
```

The CLI requires a new output directory. Public evidence is
`data/provenance/g3a_review_independent/c71.json`. The ignored final plot is
`outputs/g3a_ss_aur_audit/final/ss-aur-flag.png`; its horizontal axis uses
relative days, and no observer identities are shown. An earlier definition
check is preserved in the parent output directory: its .75 fraction used a
closed lower band edge. The final artifact explicitly uses the reported
nondecisive band and retains the closed-band sensitivity.
