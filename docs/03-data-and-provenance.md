# Data sources, access, and provenance

**Documentation audit: 5 November 2026.** This is an acquisition and normalization plan. No real light curves were downloaded or analyzed while preparing this seed. A documented archive is not evidence that a particular target has a usable, sufficiently complete time series. The seed acquisition manifest is deliberately empty; simulated examples are not observations.

Read [the data dictionary](09-data-dictionary.md) for the intended observation, event, and forecast contracts and [the decision gates](07-risks-and-decision-gates.md) for authoritative eligibility and validation decisions. Numeric thresholds belong in that decision document rather than being independently specified here.

**Acquisition update, 7 November 2026:** the first bounded SS Cyg native export
has now been retrieved through the official VStar route; see the
[A03 receipt and limitations](audits/2026-11-07-a03-ss-cyg-acquisition.md).
The web search works anonymously but its Export action requires sign-in.
VStar's source-supported date-restricted service succeeded without credentials.
This supplies native observations, not validated event boundaries or a normalized
time convention. D013 reserves SS Cyg data from 1960 onward.

## 1. Source priorities and verified access status

| Source | Intended role | What documentation establishes | What remains to be verified during acquisition |
|---|---|---|---|
| AAVSO International Database (AID) | Primary long-baseline photometry for familiar dwarf novae | Current search/download landing page, photometry application, observer contributions, and usage guidance exist | Target exports, current authentication requirements, programmatic API contract, limits, time conventions, quality flags, and redistribution terms |
| ASAS-SN Sky Patrol | Complementary survey photometry and a check on sampling dependence | Official Python client and survey publication describe catalog queries and light-curve retrieval | Installed client version/signatures, target coverage, forced-measurement and nondetection semantics, filtering, time scale, and current data-use terms |
| CRTS / dwarf-nova outburst catalogue | Historical comparison and possible additional photometry | HEASARC distributes the published summary catalogue | Recoverability and provenance of the actual epoch photometry; catalogue summary values do not provide an event sequence |
| ZTF through IRSA | Optional independent survey data and recent validation | Official light-curve and image APIs, release information, and pointing-history products exist | Target coverage, catalog detection selection, opportunity/depth reconstruction, and suitability/access of forced photometry |
| TESS / Kepler through MAST | Optional dense morphology and boundary checks | Mission light curves and pixels are archived publicly | Target-specific coverage, contamination, data-product processing, and suitability of short observing windows |

These are possible sources, not five mandatory integrations. Begin with one or two controlled AAVSO exports, then add a complementary survey only if it resolves a specific scientific or observation-model need.

### AAVSO: use the current application, not a remembered legacy endpoint

The official migration notice says that the old Data Download Tool and WebObs 1.0 have been retired. The current [Search and Download Data](https://aavso.org/search-and-download-data/) page directs users to the new applications, including photometry. Old `archive.aavso.org` documentation remains useful background but is not a validated current download API. Do not implement an adapter against an endpoint copied from an old forum discussion. See the [migration notice](https://aavso.org/blog/new-aavso-website-coming/).

The API documentation address `https://aavso.org/apps/api/docs` returned a forbidden response to the research fetch used for this seed. That response does **not** establish that all downloads require authentication, that access is unavailable to ordinary users, or that a particular credential format is supported. No authenticated API session was attempted. The acquisition agent should inspect the current official documentation, determine whether a manual export or supported authenticated API is appropriate, and record its exact method. Keep credentials outside version control and do not automate a login by guessing endpoints.

Consult the current [Data Usage Guidelines, July 2026](https://aavso.org/data-usage-guidelines-2026-07/) before acquiring or publishing data. The search/download page describes free personal and publication use subject to those guidelines. Preserve the requested AAVSO, database, observer, and source acknowledgments. Free access for analysis is not by itself a verified license to redistribute an entire raw export under this repository's code license. Record the terms actually applicable at retrieval, and keep raw exports outside the public repository until redistribution has been checked. Provider terms take precedence over this plan's paraphrase.

Preserve observer codes, original observation identifiers, band and technique, error estimates where supplied, quality/validation status, comments relevant to limits or transformations, and the export schema. Visual estimates, unfiltered CCD observations, and standardized photometry are different measurement streams. Do not silently treat them as interchangeable V magnitudes.

### ASAS-SN: verify client version and measurement semantics

The official [Sky Patrol repository](https://github.com/asas-sn/skypatrol) documents a Python distribution installed as `skypatrol`, imported through `pyasassn`, with `SkyPatrolClient` providing catalogue and light-curve access. The [Sky Patrol V2.0 paper](https://arxiv.org/abs/2304.03791) describes the service and catalogue-driven photometry. This seed does not install, execute, or validate a live client request.

A practical version trap was visible during this audit: the repository README uses a query mode such as `mode="download_curves"`, while the [rendered client documentation](https://asas-sn.github.io/skypatrol/) contains examples using `download=True`. Pin a tested release or commit, inspect that version's signatures and schema, and record the working call. Neither spelling is promised as a universally supported current interface by this seed.

Resolve the target to its survey identifier and inspect neighboring sources before accepting a crossmatch. A small coordinate match radius does not establish that the photometry is unblended. Retain camera, band, flux, flux error, reported magnitude and magnitude error, limit fields, and quality information where returned. Verify the definitions and units of those columns against the specific product: column names alone are insufficient. Keep V and g observations distinct. Retain finite negative flux estimates with valid uncertainties when they are genuine fixed-position measurements; converting only positive measurements into magnitudes produces selection bias.

Determine whether a query returns all relevant measurements, only detections, or a quality-filtered subset, and whether nondetection/limit rows describe measured positions at actual observing opportunities. Do not infer complete observing coverage from the existence of a downloadable light curve. The client's software license does not establish a license for the astronomical data.

### CRTS: distinguish a statistical catalogue from the underlying chronology

The official HEASARC [DNCVOBCAT](https://heasarc.gsfc.nasa.gov/w3browse/all/dncvobcat.html) page documents the Coppejans et al. (2016) *Statistical properties of dwarf novae-type cataclysmic variables: the outburst catalogue* product ([paper DOI](https://doi.org/10.1093/mnras/stv2921)). It includes properties such as outburst amplitude, duty cycle, and limits on recurrence time. Its underlying CDS catalogue identifier is `J/MNRAS/456/4441`.

Those summary columns are useful for context and sample auditing, but they are not individual onset/end times, a list of all missed events, or a complete observing-opportunity record. Do not treat a catalogue recurrence estimate as a sequence of observed recurrence intervals. The broader CRTS sample also contains non-primary classes; class filtering is necessary before use.

The [CRTS project site](https://crts.caltech.edu/) timed out in this audit. Actual epoch-light-curve retrieval was not verified. A timeout is not evidence that the archive has ceased operating. If CRTS photometry becomes useful, establish the current official retrieval route, distinguish CSS/MLS/SSS contributions and calibrations, and preserve their identifiers and observing windows. Do not fabricate an API or infer that every published table row has a currently retrievable light curve.

### ZTF and space missions: optional, question-specific additions

IRSA provides the [ZTF mission landing page](https://irsa.ipac.caltech.edu/Missions/ztf.html), [light-curve API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html), and [image API](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_api.html). Record the selected release rather than calling it simply “latest.” A matched-source catalogue light curve does not automatically include a measurement at every exposure. An absent catalogue row cannot be converted into a nondetection without exposure, location, quality, and depth information. Use the documented pointing-history products when reconstructing opportunities. Preserve band, field, detector, object identifiers, and quality flags; separate g/r/i response functions. Forced photometry may help, but its current access, eligibility, and terms were not verified here.

[MAST TESS](https://archive.stsci.edu/missions-and-data/tess), [TESS data information](https://tess.mit.edu/science/data/), and [Kepler light curves](https://archive.stsci.edu/kepler/publiclightcurves.html) offer potential checks on morphology and event boundaries. Target coverage must be checked before promising those data. Short observing sectors or campaigns are not substitutes for long-baseline recurrence coverage. Inspect pixel contamination and compare appropriate flux products: detrending designed for other science can attenuate or reshape an outburst. Preserve FITS time-reference and scale metadata rather than assuming that a mission `TIME` column is directly comparable to an archive JD column.

## 2. Identity must be established before merging photometry

The provisional names in [the pilot plan](04-pilot-targets.md) are a research shortlist. They are not validated crossmatches. Before acquisition, build a dated identity record containing the canonical name, aliases, AAVSO unique identifier and/or VSX object identifier where available, coordinates with reference frame and epoch, proper motion when relevant, classification, cited classification source, and each survey's object identifiers. Retain the resolver output or a reproducible query. Do not fill coordinates from memory.

Consult the official [VSX variability-type definitions](https://vsx.aavso.org/index.php?view=about.vartypes) and each current object record. A broad UG classification does not establish UGSS; UGZ and UGSU carry behaviors that change the event definition. A catalogue period may be an orbital period rather than an outburst recurrence time. Record what the field means, not just its numeric value. For apparent multi-object matches, inspect the image/context and resolve the ambiguity before pooling measurements.

Classifications can evolve. Keep the retrieved classification and the classification adopted for this study as separate, dated fields with a reason for any difference. A historical UGSS label supports candidacy but does not independently verify nonmagnetism, chemical composition, or present observing quality.

## 3. Immutable acquisitions and a reproducible normalized table

For each acquisition, retain the untouched provider export in a local raw-data location excluded from Git. Add a manifest entry only after a real acquisition succeeds. Record at least:

- Provider, target identity, requested object IDs or search coordinates, query parameters and date range, source URL, and retrieval time in UTC.
- Product/release version, retrieval software and version, export format, and exact original column definitions.
- Relative local file location, byte size, cryptographic checksum, and any provider-supplied record identifiers.
- Time format, reference, scale, units, band definitions, quality/limit semantics, and unresolved ambiguities.
- Applicable terms/acknowledgments, permission to redistribute if established, and the query's known completeness limits.

Keep ingestion transformations deterministic and versioned. Every normalized observation should point back to its raw source row and acquisition. The schema's `(provenance_id, source_row_id)` identity protects local row integrity; it does not prove that two different archives did not redistribute the same underlying measurement.

Cross-survey deduplication requires origin evidence: original exposure/observation identifier, provider lineage, observer/instrument, time, band, and value as appropriate. Two independent observations close in time are not duplicates merely because their timestamps or magnitudes agree. Conversely, copies of one observation are not independent evidence because they arrived in different files. Preserve both provenance records while ensuring the underlying measurement contributes once to an analysis that assumes independent measurements.

## 4. Time, passbands, uncertainty, and limits

**Keep original time values and metadata.** JD versus MJD is a representation choice; geocentric/heliocentric/barycentric reference is a separate issue; UTC, TT, and TDB are time scales. Do not repair an unexplained offset by intuition, label an unspecified time as UTC, or treat an HJD value as BJD merely by renaming a column. Perform a conversion only when the original convention and necessary location/target metadata support it, and record the software and assumptions. Unresolved records remain quarantined from analyses requiring consistent absolute time.

For comparisons at day-scale recurrence resolution, some timing differences may be numerically small, but that is a justified analysis tolerance, not permission to discard metadata. Distinguish observation time from upload/availability time. A chronological analysis can emulate use of earlier observations; it cannot claim an operational historical replay if publication/ingestion delays are unknown.

Do not apply a universal scalar offset to combine visual, V, g, unfiltered, and other bands without checking color and state dependence. Begin within a well-defined band or measurement stream, then quantify the sensitivity of event extraction to combined data. Missing uncertainties remain missing until an explicitly documented error model is applied; they are not zero. Retain quality flags before any exclusions.

A faint nondetection reported as limiting magnitude `m_lim` constrains the object toward **larger numerical magnitudes**, `m > m_lim`, or lower flux, `F < F_lim`. It is not a measured magnitude equal to the limit. In a noisy measurement model, use the provider's detection/limit convention probabilistically rather than treating the boundary as exact. A missing measurement with no established exposure and depth is neither a detection nor an upper limit. Saturation is a different censoring/quality issue and must not be encoded as an ordinary faint limit.

## 5. Observing windows are part of the science

A quiet interval is informative only to the extent that an outburst could have been detected there. Preserve actual observing opportunities, useful nondetections, seasonal visibility gaps, cadence changes, band changes, and limiting depth. Targeted follow-up may increase after an outburst begins; this makes the observation process depend on source state. The number of observations is therefore not a simple proxy for an unbiased time baseline.

Use development data to define the eligible episodes/windows and the event-extraction review protocol. Assess detection efficiency by injecting plausible outbursts into representative real observing schedules once those schedules exist. Distinguish an event missed entirely from one whose onset or end is interval-censored. Avoid bridging long unobserved gaps as though no outburst occurred. Do not select stars using the number of successfully completed cycles in future evaluation data; retain forecast opportunities with right censoring under the frozen protocol.

## 6. Concrete first acquisition deliverable

The first data work should yield a small, reviewable acquisition report: verified identities for the initial candidate(s), original export(s), populated manifest entries, a schema/metadata audit, a plot of detections and genuine limits, coverage summaries, and a manually reviewed interval containing both activity and quiescence. Report rejected/ambiguous rows and the reasons. That report establishes whether real-data event extraction is feasible; this seed does not claim it has already passed.

Only then choose the first implementable adapter and extend to the pilot set under the decision gates. If useful nondetections or observing opportunities cannot be reconstructed, narrow the claim to densely observed intervals or adopt an explicit missing-event model before drawing recurrence conclusions.

## Source record

URLs above were reviewed for this seed on 5 November 2026. No target photometry was retrieved. Current AAVSO migration and July 2026 guidelines supersede older access notes. The AAVSO API forbidden response and CRTS timeout are audit limitations, not assertions about general service availability. Provider documentation and live schemas should be revisited at the first acquisition and their versions recorded.
