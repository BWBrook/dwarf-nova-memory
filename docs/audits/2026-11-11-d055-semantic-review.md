# D055 semantic review: results accepted; two methods clarifications and a citation fix

Codex, 11 November 2026. Base `4471a6c`; step-4 text diff `f70771d..438c4b4`,
plus the preceding brief corrections `e58f447`. Responds to thread 159/3226.
This is a review: product text, PDFs, estimands, claims and scientific outputs
are unchanged. Keep the current structure and D051's concentrated limitations.

## Requested checks and accepted changes

| Check | Evidence and verdict |
|---|---|
| Abstract's era-split correction | Correct. The saved evaluation summary gives 1960–1992 mean 0.02398320867, 90% interval [0.00910883373, 0.03885758361], n=261; 1993–2017 mean 0.00573145226, interval [-0.01066656489, 0.02212946941], n=180. Naming only the latter segment and the long/short rule as inconclusive fixes the old overbroad summary. My previous review missed that summary too. This does not establish an era-difference test. |
| C04's new plain-language size | Correct: fixed timing history, median quiet interval **before conditioning** on elapsed time. The existing independent reproducer verifies 1.0880015159653311 from the frozen parameters. The brief's full-quiet-spell wording and guide's exp(mu) definition agree. |
| B2 chosen in advance | Correct. R2b execution v2 lines 165–173 fixes H1/H2 to B2 before scores. “Chosen in advance” does not imply best fit or a new confirmation; both facts remain explicit. |
| 1,100 planning forecasts | Correct as a planning comparison. G3a's saved audit derives 367.2 from the all-ten 1980s rate, ignoring qualification gates. The wording does not call 1,100 a validated power guarantee or 367.2 an observed later count. |
| C56 and H3 after relabeling | Still correct: rate replaces duration; cadence refits the base before duration is added. H3 compares gains at matched issue times. The point-clock label becomes fitted-end, preserving the anchor identity. |
| New example explanation | Consistent with the positive coefficient, shared timing base/spread and development-centred log duration: the selected example has the earlier M3 forecast. It is a single date-selected illustration. |
| Brief corrections | All retained: fixed-history full-gap contrast, C07/C08, baseline adequacy and unknown upload/revision dates. The opening answer is stated plainly and the qualifications stay together. |
| Captions and labels | Every numerical field/count/clock/baseline/evidence path in the eleven forest rows is unchanged; only labels differ. Figure 2's data likewise change only a label. Revised captions retain the contrast identities and scope. |

The revised main text defines the working score before its repeated headline
statements. The smaller report-window gains remain exploratory changes of
measurement/model/population, and the limitations still prevent causal allocation
of a fraction of C01. No new empirical result or analysis follows this review.

## Corrections

### 1. The plain-language CAR sentence restricts too little

Main lines 378–380 restrict **when** reports occur and then say that observing
factors out of the likelihood. This is not the full condition governing the
reduced onset-window observation. Report values, limits, aggregation, selection,
confirmation and stopping also belong to that model. Appendix C retains the
stronger condition, but the implication in Section 5 needs to agree with it.

This is the already-settled distinction in
`docs/audits/2026-11-09-r1-observation-contract.md:54–84` and
`docs/protocols/r2-design-v1.md:35–45`: the complete normalized observation kernel
must be constant across compatible onset times, with observation parameters
distinct from forecast parameters. Nonanticipating visits can be ignorable in
a joint light-curve model without giving that scalar-window factorization.

Replace the clause beginning “and that when observers report” with:

> and that, given the retained history and forecast state, the complete reporting and selection
> process gives the same probability of obtaining the reported window for every
> onset time it contains, with observation parameters distinct from forecast
> parameters. Under these conditions the observation term factors out of the
> likelihood (coarsening at random; [@heitjan1991IgnorabilityCoarseData]; Appendix C).

This preserves the accessible explanation and states the full premise rather
than reducing it to reporting times. It remains an unestablished requirement,
not a claim that the archive meets it. No further model fitting is requested.

### 2. Catalogue confirmation and forecast issuance are different rules

Main lines 105–107 now require decisively bright, margin-passing evidence for
catalogue confirmation from two observers. The actual catalogue accepts two
observers' ordinary bright-side visits; the stronger margin rule arms forecast
issuance. The faint-report veto also belongs only to the single-observer
catalogue branch. These definitions must remain distinct.

Checked independently by two code traces: `extract.py:24–48,77–104`,
`extract_x4.py:76–86,108–110,147–152,186–241`, and the forecast/outcome callers
in `prefix_features.py`. A parent scratch check using only synthetic reports
(two observers at magnitude 9.8 for five nights, with faint reports before and
after) finds one confirmed catalogue episode but zero operational issuances.
No real record or forecast score is involved.

Replace that catalogue sentence with:

> For catalogue confirmation, two observers need only report magnitude 10 or
> brighter; a single observer needs bright reports on at least two nights, one
> at magnitude 9.5 or brighter, without a contradictory report at magnitude 10.5
> or fainter from another observer on those nights.

At the start of Section 2.3, replace its first two sentences with:

> A separate causal rule issues forecasts: after magnitude-9.5-or-brighter
> reports from two observers, or one observer on two nights, subsequent reports
> at magnitude 10.5 or fainter from two observers confirm the fade. Every such
> confirmation issues a forecast, including repeats.

Keep the following 400-day/prefix paragraph and Appendix A. This is a prose
correction to the frozen code's identity, not a request to alter the rules.

### 3. Link the added Heitjan–Rubin entry

Main line 380 still uses literal author–year text. The bibliography entry exists,
but Heitjan–Rubin is absent from the rendered References on page 13; it appears
only in prose on page 8. Use the citation key in the replacement above. Rebuild
and confirm the entry appears, then inspect pagination and the full Figure 1
caption after the bibliography grows.

## Reference, render and verification scope

Two bounded read-only delegates checked reference support and figure/PDF
consistency; the parent checked result semantics, the code paths and the
synthetic confirmation counterexample. The delegates' findings changed the CAR
and citation verdicts and independently confirmed the catalogue/issuance split.

New reference identities and uses are consistent within the checked scope.
Cameron–Miller supports the CR1 correction and t(G−1) convention, not the assumed
independence of these six-year blocks. Its [author manuscript](https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2014_July_09.pdf)
states the distinction; Table 2 retains the unresolved dependence assumption.
The two formerly inline entries match primary/institutional records; software
identities match their official citation pages. Ak/Vogt uses were checked against
the existing source register, without opening later astronomy outcomes. The
Heitjan scan could not be freshly read through the delegate's web interface;
the detailed condition check uses the existing full-text contract audit and the
frozen mathematical specification, not a claimed new full-text verification.

Article pages 2, 5, 10 and 13–20 and both brief pages have no material layout
defect. Figure/table checks pass. The metadata-initial normalization also passes
small offline smoke checks for bare initials and full names in the manuscript's
locked environment.

All 580 tests, seed integrity/structure checks, manuscript/claims/lint/reference
checks and source/brief render checks pass. Claims has zero errors and seven
existing uncited-claim warnings. All 26 original forecasting source hashes and
the frozen parameter hash agree. Both GitHub workflows passed on `4471a6c`.

Only public aggregates, code, existing products, synthetic fixtures and bounded
reference material were used. No archive request, raw observation, real fit or
forecast score was opened/computed. SS Cyg 2018 onward and candidate-star 1990
onward remain closed; release and submission still require Barry's authority.

Next: Claude — apply these two methods clarifications and the citation link,
rebuild and inspect the affected pages, then hand the products to Barry. No new
analysis or restructuring is needed.
