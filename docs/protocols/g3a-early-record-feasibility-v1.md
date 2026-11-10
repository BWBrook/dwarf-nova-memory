# G3a v1 — approved development-only feasibility execution

Codex, 10 November 2026. Implements the approved
[v0 proposal](g3a-early-record-feasibility-v0.md), with numerical qualification
details fixed before acquisition. Barry's answer in this chat, relayed with
Claude's 9 November 23:37 handoff, was exactly:
**“yes, approved as proposed. Continue.”** No additional opening is inferred.

## Authorized envelope and stopping point

Open pre-1990 native records of SS Aur, RU Peg, AR And, X Leo, TW Vir, UU Aql,
CH UMa, DX And, U Gem and IP Peg. The last two are conditional eclipse holds.
Use only validated native `Vis.` rows for scientific qualification. The
unchanged official native transport may include other bands/flags within the
same authorized dates; retain those bytes and check completeness, but never
mix them into visual analysis. No raw exports or observer identities enter Git.

No target observation, count, coverage summary or light curve at JD ≥2447892.5
is requested or inspected. SS Cyg is not a G3a target and its 2018+ boundary
stays closed. Neither an early-record pass nor this protocol authorizes G3b.
Products remain paused. Stop at a frozen qualifying set and an aggregate
feasibility report. No duration–gap association, marker coefficient or incremental
forecast-score comparison is computed before that set is frozen.

## Acquisition and immutable evidence

Commit source/configuration/tests before **any** target metadata or observation
request. `configs/g3a_feasibility.json` is the ten-name whitelist. Resolve each
exact name with `data=0` and date limits; consume only Name/AUID. Subsequent
pages must match both. No unbounded name resolver or all-history counter.

The fixed windows cover native JD [1,2447892.5): one [1,1900-01-01] window,
then decade windows to 1990. Inclusive adjacent endpoints deliberately overlap;
the final `tojd` is the immediately representable float below the split. The
ancient lower endpoint avoids discarding any accessible earlier development
record; it asserts nothing about archive completeness in ancient times.
Every returned row must lie inside its own requested window and before the
split, before any summaries. Identity/date/redirect violations stop **all**
subsequent target requests. Redirects are refused before they can lose date bounds.

The endpoint, CSV columns and parameters follow AAVSO's pinned VStar source
`6797f17fe106097fd84c1822a24d51021aea9fdd`. Importantly, its CSV2 source treats a
present `Count` as a pagination continuation marker, not proof that a short
page is complete. Follow pages under identical dates/AUID until the marker is
absent or the next page contains no Data; require progress and consistent
duplicates, with a 100-page bound. A cap-sized page without a continuation
marker triggers deterministic date bisection (maximum depth20, minimum .01d).
Keep every capped response and subsequent child window. Conflicting repeated
obsIDs, unresolved completeness or malformed CSV fail that star.

Native XML/CSV strings, limits and blank/literal-`None` uncertainty remain
unchanged. `fainterThan=1` is a magnitude lower bound, never a faint detection.
Use three bounded retries only for transport errors, with retained attempt
receipts; do not retry a scientific/access violation. Raw receipts record URL,
retrieval time, bytes/hash, windows/pages, source hash and environment. All
observations remain outside Git; public manifests/aggregates contain hashes
and counts without identities or event times. Observation-time retrospective
availability remains distinct from historical upload/revision availability.

## Frozen extraction and qualification

Thresholds come from C52's pre-existing catalogue proposals, without examining
these records: SS Aur13.5, RU Peg11.5, AR And14.5, X Leo14.0, TW Vir14.5,
UU Aql14.0, CH UMa13.5, DX And13.5, U Gem12.0 and IP Peg14.5 mag. Catalogue
passbands are provisional visual proxies, not calibrated archive thresholds.
Do not retune thresholds to improve yield in this run.

Use common decisive margin **1.0mag** throughout X5/DF. This freezes RU Peg's
preliminary .9 catalogue proposal to1.0 before data, because the current DF
chain consistently uses BAND1.0. X4's distinct .5 confirmation rule is unchanged.
All original X4/X5/R2b source bytes remain unchanged. This is transfer
feasibility, not a new demonstration of boundary recovery for each star.

A star must satisfy every approved v0 gate, operationalized as follows:

1. **At least40 timing-supported marked DF forecasts.** A finite observed
   anchor, positive decisive span, and covered previous gap must be available
   by issue. Require an eligible next-onset window or a positive-exposure
   coverage-censored working outcome; a zero-length survival term contributes
   no information and does not count. Report feature-only and outcome-supported
   totals separately. Missing prior events/gaps are not joined over.
2. **Eligible X5 windows ≥70%** of all confirmed outbursts. Report availability,
   eligibility, widths and flags separately; do not interpret eligibility as
   proven latent onset containment. Retain record-edge failures in denominators.
3. **B0 converges at every declared start without degeneracy.** Use the existing
   B0-only multistart fit with marks stripped; no `fit_mark`, beta or gain.
   Its training likelihood is needed for this approved convergence gate, not
   an incremental forecast-score analysis. Require finite parameters, full
   active timing-design rank, stable B0/constant/remaining starts and no active
   parameter on its declared bound. Insufficient information fails the gate.
4. **No operational morphology-screen failure.** A supported threshold-bright
   run has ≥10 bright nights, ≥2 observers, and no internal observing gap >7d.
   Fail on any such run ≥60d, or ≥3 such runs ≥40d. These are conservative
   operational plateau exclusions, not a subtype diagnosis; ordinary long
   episodes can fail, and sparsity can hide anomalies. Preserve all failures.
5. **Eclipse holds pass the additional frozen guard below.** No blanket pass
   comes from having an adequate ordinary count.

## Eclipse feasibility guard

U Gem/IP Peg are evaluated under two explicitly derived observer-night streams:
median positive estimate versus brightest positive estimate (strongest bound
for all-limit nights). Each derived row is released at the **fixed night
closure** floor(nativeJD)+1, retaining its raw support; unfinished boundary
nights are omitted. A last-report time would depend on knowing no later report
arrives and is therefore not used. Frozen visit closure adds its usual .15d.
This is a new feasibility reduction, not unchanged raw-report X5 timing.

Their confirmation rule requires faint evidence on two distinct nights and
issues only when the second night is available. Never backdate to the first.
Both reductions must independently meet the same ordinary gates. Additionally:
≥90% episode matching within3d; ≥90% eligible-window agreement; at least20
matched usable spans; outcome-supported-count
relative difference ≤10%; matched decisive-span absolute discrepancy median≤1d
and90th percentile≤2d. Preserve unsupported/unmatched episodes.

A conditional, gain-free eclipse sensitivity uses the same pre-1990 timestamps
and invented trapezoid outbursts under a fixed phase grid. Periods are .17690618d
for U Gem and .15820764d for IP Peg (pre-1990 primary sources checked by the
implementation reviewer). Test widths .10/.25cycles, depths1/3mag and phase
jitter0/.03cycles, with .22mag scatter. The wider profile is a stress value,
not a claimed physical upper bound for a disc eclipse.

For each reduction require ≥20 recovered no-eclipse baseline events, ≥90%
retention of those identities under the eclipsed streams, early/ambiguous end
alerts<2%, and decisive-span error median≤1d/p90≤2d against known synthetic
truth. Baseline inadequacy is reported as inconclusive and cannot qualify.
No waveform, threshold or gate is tuned after the real cadence is opened.
Passing is conditional feasibility under this envelope, not phase correction,
removal of eclipse effects or validation on an unseen outburst family. It must
be reconciled in the later G3b observational model; it does not open test data.

## Fixed set, projections and six-star supplement

Write and hash the qualifying list before any marker fit. G3a closes with
that gain-free result; developmental association/model fitting is a later
tranche after review of qualification. A star's 1980–1989 supported issuance
count divided by10 is its planning rate. Show projections for28 and36 years
(1990–2017 or1990–2025), explicitly assumed—not observed test counts. G3b's
end date remains Barry's separate decision. Require ≥6 stars and≥1,100
projected supported issuances for the proposed horizon before asking for G3b.
Use ≤40% capped star weights and report the corresponding effective sample
size as a diagnostic, without claiming80% power. No star is added because a
favorable future count is known; no failed threshold is relaxed to get six.

Before G3b, complete the frozen eight-cell,16,000-trial six-star supplement
in `data/provenance/g3a_preparation/six-star-design.json`: clean null/effect
at1,100/2,000, persistent null/effect and delayed/noisy null/effect at1,100.
It reuses the unchanged point-Gaussian helper with a new seed namespace, at
most four local workers. Report every declared method; select none on these
outcomes. It is not window/extraction/calendar validation or a6-star global
error-rate certificate.

## Sequence interpretation agreed before new data

C67's gain-subset recount is accepted only for the retained70,000 trials.
An independent Gaussian counterexample disproves a general nesting theorem.
Accept association then forecast gain as a **proposed fixed sequence**, at5%
each, retaining both distinct claims and D018's forecast-gain endpoint. Strong
familywise control requires each test to be valid under its own full null:
stage1 under the association null; stage2 when association is real but gain≤0.
Independence is unnecessary for this sequence argument. A pooled397/8,000
oracle-null score rate screens one global-null mixture, not every scenario or
partial-null family. Zero observed power loss is not a future guarantee.
The old ≤5% observed-rate screen was exactly the finite screen Barry chose;
it was not evidence that the true rate exceeded5%. Keep its result rather
than retroactively replacing it with a pooled pass.

No claim here identifies a physical mechanism. The sequence's observational
validity, working-window assumptions, label availability and freeze remain
G3b design work. No first paper/data release, outside contact or new access
is authorized by a feasibility pass.
