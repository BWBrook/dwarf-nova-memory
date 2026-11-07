# A04 independent comparison and open-era acquisition

Codex (GPT-6), 7 November 2026, starting from `7673b4a`. The fresh blind
annotator was a Codex subagent (`gpt-5.6-sol`, medium reasoning) with no inherited
chat history. A separate read-only methodological subagent (`gpt-5.6-sol`, high
reasoning) audited endpoint and power claims. The parent reviewed the source,
integrated the evidence and acquired the open-era data. This supplies
independently derived labels and calculations, not independent model-family
validation.

**Outcome:** the two annotators recover corresponding episodes, but disagree
at three boundaries. The requested pre-1960 stream is now acquired and hashed.
Coverage varies sharply by era. No duration–gap correlation, observational model
fit or 1960+ data access occurred.

## Blindness and sealing

The parent had seen Claude's summary and labels. The delegate received only:

- a 1957-only native subset, inclusive JD 2435839.5–2436204.5, retaining all
  columns and flags; SHA-256 `8d43dc9f4490058f1cd720fc7e3c46c12ea90896e63847dfb6b44cbe1f575311`;
- the protocol exactly as committed at `1bfbca5`; SHA-256
  `eff2a57334e2f995a923e50c8d84ff40dcd88ab66cab43292095f94fe27c77e8`;
- an input receipt with hashes and window bounds.

It was instructed not to read the repository, parent history, other agents'
outputs, board, Claude's tools/results or outside data. Its attestation and
recorded file reads support compliance; this was context isolation, not an
operating-system access barrier. It independently implemented the row classes
and candidate rules, reviewed all candidates and sealed its outputs.
Original files, code and full seal are retained under gitignored
`data/raw/a04_blind_1957_20261107/`. Public annotations contain source IDs and
judgements, with no observer identities.

Labels were committed as `2aa9262` before comparison. Git normalized their line
endings; `bc1222b` records both original sealed hashes and committed LF hashes,
with identical CSV fields. The [seal receipt](../../data/annotations/a04_ss_cyg_1957_codex_blind_seal.json)
and [delegate report](2026-11-07-a04-blind-1957-report.md) record inputs,
commands and limitations. The frozen protocol itself was not changed.

## Comparison

Reproduce with `python3 scripts/compare_a04_1957.py`. It verifies the blind
output hashes before comparison. Chronological pairing identifies eight
corresponding episodes. The protocol's strict onset-overlap criterion matches
**seven of eight**; the remaining pair shares its peak and is identified only
after sealing. Do not describe this as eight strict matches.

| Claude / blind event | Difference (blind minus Claude) | Assessment |
|---|---|---|
| E10–E13 / 01–04 | Onset and end midpoint differences 0 d | Same strict brackets and confirmation times |
| E14 / 05 | Onset +0.55 d; end 0 d | No onset overlap; different handling of isolated threshold estimates; common peak |
| E15 / 06 | End −1.05 d; confirmation −0.95 d | Blind annotator rejects late isolated bright estimates that Claude retained |
| E16 / 07 | End −0.3305 d; confirmation −0.79 d | Contradictory B/F reports at tied JDs; blind annotator marks ambiguity |
| E17 / 08 | End/type/confirmation not comparable | Blind input ends during the event; it is correctly unconfirmed and right-censored there |

Five of seven complete-event end brackets overlap. All seven complete-event
long/short calls and following-gap consecutiveness labels agree. This is
conditional agreement under the shared protocol, not proof of true endpoint
coverage or complete detection. The year-edge classification difference is
caused by unequal information windows and is not counted as disagreement.

The blind table's structured alternative for event 07 uses the literal tied
epoch, while its prose gives a strictly later-row ambiguity envelope. A
[post-seal clarification](2026-11-07-a04-blind-1957-clarification.md) distinguishes
them without changing a primary label. Neither that tied field nor Claude's
zero-width end bracket means a noiseless, exactly known end.

No labels were reconciled into a consensus catalogue. The differing merges,
outlier rejections and tied-epoch handling are material inputs to the next
protocol/extractor revision. Claude's original annotation still rebuilds byte
for byte after the receipt-loader change.

## Endpoint claim: retain a conditional sensitivity, not negligibility

The independent audit and parent reproduction confirm the A04 uniform-envelope
calculation at raw rho=0: end-error variance 0.1447005 d² gives a shift of
−0.002838. That assumes centred independent errors, true endpoints inside the
post-viewing envelopes, and plug-in duration/gap scales. Envelope coverage has
not been calibrated. Four of the 16 gap pairs used for that scale are labelled
`unverified`; the 20-event duration and 16-pair gap samples also differ.

`python3 scripts/audit_a04_endpoint_sensitivity.py` reproduces the assumptions
and examples without calculating an empirical duration–gap correlation. With
a hypothetical *raw* rho=0.13, the endpoint-extreme variance sensitivity is
−0.01050; with CM92's published raw rho=0.223 it is −0.01198. The former is
an illustration, not a substitution of a partial correlation into a raw one.
Thus “under 0.01 at worst” is not a general bound even within these plug-in
calculations.

Matching the error SD alone is insufficient: if independent true D,Q have
the stated marginal scales, an error `delta=0.3804*(Q-E[Q])/sd(Q)` yields an
induced correlation about +0.0998. This is an analytical counterexample, not
an assertion that the real errors behave that way or satisfy validated
per-event envelopes. It shows why dependence/bias assumptions matter.
Onset errors also couple duration to the previous gap; type calls and partial
coefficients need joint propagation. The blind boundary differences provide
another reason to keep that work.

The summarizer now names its endpoint-extreme calculation conditionally,
states its assumptions and reports the unverified pairs. Original labels and
numeric sensitivities are preserved. Seasonal/coverage gaps remain an immediate
problem, but endpoint uncertainty has not been shown negligible.

## A10 proposal: preserve the predictive question

The .83 versus .37 numbers reproduce the stated one-sided iid fixtures, not
our pipeline's power. A coefficient estimated on the sealed block tests
conditional association; a forecast-score contrast tests the value of issued
distributions. A mark can inform latent state without a direct coefficient,
and a significant coefficient can reflect a weak state/observation model.
The physical sign remains open, so one-sided planning needs a justification.
The parent checked the primary [Inoue–Kilian 2002 working paper](https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp195.pdf),
printed pp. 27–28; the reviewer also inspected §§3.1–3.2. Its case-specific,
asymptotic comparisons do not establish these astronomy operating characteristics
or choose our scientific estimand. This was the working-paper version, not a
fresh audit of the 2005 journal edition.

Recommendation for A10: keep paired forecast gain, calibration and uncertainty
as the primary predictive quantities. An exactly specified coefficient/LR test
can be secondary conditional-association evidence. Fitting that coefficient on
the block cannot turn a score from the same fit into an out-of-sample score.
No significance gate or primary-outcome change is adopted here; actual pipeline
simulation and the scientific lead's review still govern the freeze. CM92's
pooled table exposes aggregates spanning 1960–1992, not the sign within that
subperiod separately; choosing 1993 alone would not establish universal prior
ignorance. The documented literature-informed label remains appropriate.

## Three early coverage probes, then the remaining open-era stream

After comparison, requests covering 1904–1907, 1924–1927 and 1944–1947 succeeded.
Informative-coverage figures below exclude nonvisual bands and T flags, and count a faint limit
as informative at 10 mag only when its limit is at least 10. Native JD bins are
noon-to-noon bins, not reconstructed local observing nights.

| Request | Native rows (all bands/flags) | Informative observed JD bins / window bins | Longest internal informative gap |
|---|---:|---:|---:|
| 1904–1907 | 384 | 202 / 1,097 (18.4%) | 113.73 d |
| 1924–1927 | 5,513 | 1,062 / 1,097 (96.8%) | 3.00 d |
| 1944–1947 | 2,961 | 829 / 1,097 (75.6%) | 19.80 d |

These differences justified retaining era-specific coverage information, not
assuming a uniform century-long training set. Bounded requests then filled the
remaining query span from 1896-01-01 through **native JD 2436934.0** (1959-12-31
noon under the presumed convention). This leaves a half-day buffer before D013;
it is not an acquisition of 1960 data or the final half-day of 1959.

There are **12 retained acquisitions**, including the original and overlapping
probes: **81,502 returned rows**, **8,867 identical duplicate occurrences**, and
**72,635 unique native observation IDs**. The deduplicated stream has 72,618
visual rows, 15 unknown-band rows, one R and one CR row; bands remain distinct.
There are 3,885 fainter-than limits across the stream and 497 T flags. The
longest internal informative visual gap is 548.18 d in the 1900–1910 request.
These are properties of this returned/provider-filtered stream, not absence of
historical observing or of outbursts. Some historical products may differ.

All native bytes, headers, hashes, request windows, retrieval times and code
hashes are retained locally, outside Git; the public
[manifest](../../data/manifests/acquisitions.csv) has one entry per acquisition.
The reader now verifies each receipt hash and bounds before any summary, rejects
requests at/after 1960, and deduplicates overlap by native ID while rejecting
conflicting versions. Unknown bands are not relabelled visual. Tests cover
receipt tampering, future windows, repeated observations, limits and missing
days. No normalized observation or forecast table is emitted.

Per-request counts and gaps are in
[the coverage table](../../data/coverage/ss_cyg_open_era_profiles_20261107.csv).
Reproduce all profiles with:

```bash
python3 scripts/profile_ss_cyg_coverage.py data/raw/aavso_ss_cyg_*/native.xml
```

The raw exports are gitignored and must first exist locally; the manifest gives
their exact requests. The large gaps and early scarcity rule out treating every
adjacent detected outburst as consecutive. They do not establish detection
efficiency or the number of usable forecasts. Timing is preserved as native JD;
the A04 UT/geocentric convention is an assumption, not a 0.006 d bound on all
historical timestamp or transcription errors.

## Next tranche

Claude should review the three boundary differences and the tied-epoch encoding,
then define a small set of observer-balanced extraction and coverage candidates
using only the open era. An injection/recovery check must establish what those
rules recover before any final eligibility or power statement. Neither the
coefficient-test proposal nor a production extractor is approved by this audit.
