# A10m independent novelty audit of C41

Codex, 9 November 2026. Base reviewed: `2ec353493b941ef190b63d74267375f29e119af6`.
This is a bounded literature audit, not a systematic review or a proof of universal absence.
No manuscript, claims-ledger, protocol or scientific-analysis file was changed.

## Verdict and wording

**The narrow novelty candidate survives this independent search.** I found no previous
preregistered evaluation of fixed probabilistic next-outburst forecasts for dwarf novae,
and no explicit held-out comparison isolating the incremental contribution of a completed
outburst's duration beyond a timing-history baseline. That is a supported account of what
this bounded search found. It does not establish that no such work exists.

Recommended manuscript wording:

> Our literature search found a held-out point-forecast precedent for V363 Lyr
> (Grigorievskiy et al. 2014). To our knowledge, the present study is the first
> preregistered, frozen-parameter probabilistic evaluation of dwarf-nova recurrence
> forecasts on held-out observations, and the first held-out test of whether completed
> outburst duration adds forecast skill beyond a specified timing-history baseline.

Keep the existing statement that this was an observation-time retrospective evaluation
completed after a post-access format repair. Neither the protocol DOI nor this novelty
audit licenses “untouched,” operational replay, or calibration claims.

**Ledger recommendation:** C41 can become supported if its claim is explicitly the
bounded finding above, its evidence points here and to the receipts, and its limits retain
ADS failure and incomplete source/citation coverage. If C41 instead means verified priority
over the entire literature, keep it provisional. I would accept the qualified “to our
knowledge” sentence with those disclosed limits; I would reject an unqualified “first.”
The duration clause must say *held-out incremental forecast skill*: duration–interval
correlations, sequence dependence and physical explanations are established prior art.

## Independence and search scope

The supplied brief identified the V363 Lyr precedent and the proposed C41 wording. I read
the live repository instructions and began with my own searches. Twenty search queries
were issued before I read A10l section 4 and `references/search-log.md`; a preliminary
file search exposed C41 metadata, but not the full search memo. After reconciliation I
ran twenty-three further queries and inspected backward and forward leads. Thus the
source appraisal and initial query design were independent; this was not a reviewer
blinded to the candidate novelty claim.

The 43 exact queries are in
[`a10m_novelty/search_receipt.json`](../../data/provenance/a10m_novelty/search_receipt.json), dated
2026-11-09. They cover singular/plural dwarf nova, cataclysmic variable, recurrence,
waiting time, outburst prediction/forecasting, duration, machine learning, neural methods,
Gaussian processes, Bayesian forecasts, survival/hazard analysis, probabilistic forecasts,
log score and preregistration. Initial broad discovery was followed chiefly by
publication-restricted ADS/arXiv/publisher/author-repository searches. Search-engine
results were screened for primary records; secondary pages were discovery leads only.
This is not a deduplicated enumeration of all web hits.

The supplementary observer-publication search was shallow; JAAVSO, JBAA, IBVS and
non-English proceedings remain less securely covered than indexed English journal
articles. Classical/recurrent thermonuclear nova forecasting and classification of CV
subclasses were treated as adjacent work, not direct tests of the stated estimand.

## Closest independently source-checked precedent

[Grigorievskiy et al. (2014), author PDF](https://research.cs.aalto.fi/aml/Publications/Publication216.pdf),
printed pp. 5–12, establishes a genuine held-out point-forecast precedent. The chronological
training/validation/test split is visually clear on printed p. 6, with one validation
outburst and one test outburst. Models forecast onset positions directly or predict
photometry until a threshold crossing. Inputs are recent photometry, optionally time
since the preceding end. Hyperparameters are selected on validation data; performance
uses mean absolute timing error across origins before the test onset. The paper does
not report an explicit completed-duration addition/ablation against a common timing
baseline. Its references to probabilistic outcomes concern random model runs, whose
errors are averaged; the evaluated object is not a predictive onset distribution.
No preregistration is described. Absence of a described registration is what the source
supports; it does not prove that no external registration ever existed.

The source was retrieved as a full PDF and relevant methods, comparison, conclusions and
bibliography were read. SHA-256:
`0ff9ed5767344a5e855130ae8e9d6b7d1757359c214195d5c9cbf2c4be22f48f`.
The PDF and derived text/image are temporary scratch files, not repository payloads.

## Other source checks and citation chains

| Source | Inspection in this audit | Consequence |
|---|---|---|
| [Price et al. 2007, arXiv:0710.2937v1](https://arxiv.org/pdf/0710.2937), journal DOI [10.1086/524413](https://doi.org/10.1086/524413) | Primary full preprint; introduction, analysis, conclusions and references read. The precursor analysis folds observations by known onset; its long-term analysis associates wavelet/period features with binned intervals. | A direct predictor-search precedent, but no held-out probabilistic forecast-score comparison or duration-addition test is reported. Its Hill & Waagen 2005 poster reference remains an unverified backward lead. |
| [Tsuranova et al. 2026](https://journals.rcsi.science/0004-6299/article/view/466940), DOI 10.7868/S3034518926080062 | Official English abstract, metadata and references only. The abstract proposes prediction from a multifractal precursor in YZ Cnc. Russian full text redirects to subscription/payment login; the web tool could not read its XML endpoint. | A relevant recent precursor lead. Do not assert that it lacks held-out/probabilistic validation: those methods remain unknown. It is not identified by the accessible abstract as a completed-duration comparison. |
| [MNRAS CV machine-learning article](https://academic.oup.com/mnras/article/527/3/8633/7459939) | Indexed primary full-text classification structure inspected. | Its outcome is CV subclass classification; it does not supply a next-onset evaluation in the inspected design. No light-curve tables were extracted. |
| [Cannizzo & Mattei 1992](https://doi.org/10.1086/172092) | OpenAlex identity and citing-title screen refreshed. Historical methods/results were not independently re-read here. | The repository's earlier original-source review remains the authority for its correlations and absence of a forecast evaluation. This audit adds a current bounded citation search, not a second numerical validation. |

Backward inspection of the V363 paper's bibliography identified Kato et al. 2001,
*Outburst cycle of V363 Lyr* (IBVS 5118), as its earlier recurrence study. An author
institutional bibliography confirmed identity; ADS PDF/full routes were inaccessible.
I make no detailed methods assertion about that paper. The remaining references concern
object identification, spectral/missing-data methods and forecasting algorithms.

OpenAlex API access succeeded without a credential on 2026-11-09:

- Exact-title lookup found V363 work `W2608392576`, with `cited_by_count = 0`.
  This means no forward citations indexed in that record, not that the paper has never
  been cited. Exact-title web searches found copies/author records but no independently
  verified follow-on recurrence forecast.
- CM92 DOI lookup found `W2071470637`, with 68 indexed citing records. A
  `cites:W2071470637` query with `per-page=100` returned all 68. I screened all titles
  and identifiers, not all abstracts/full texts; the raw count includes duplicate versions.
  The clearly relevant predictor title was Price et al. 2007, read above. Two potentially
  relevant titles—Cannizzo 1994, [*On the Sequencing of Long and Short Outbursts in
  Dwarf Novae*](https://doi.org/10.1007/978-94-011-0858-4_9), and Conway 1998,
  [*Time series, neural networks and the future of the Sun*](https://doi.org/10.1016/S1387-6473(98)00041-4)—
  were followed bibliographically. Original full texts were not retrieved; neither is
  represented here as a source-verified exclusion. Other familiar recurrence/statistics
  titles remain covered by the earlier A01 audit, not newly revalidated here.

Sanitized metadata, without abstracts, are retained in
[`a10m_novelty/openalex_cm92_citers.json`](../../data/provenance/a10m_novelty/openalex_cm92_citers.json)
and the two lookup receipts. This is a complete retrieval of one current OpenAlex
query, not a complete astronomy citation graph.

## Access limits and reconciliation with A10l

The ADS web search and CM92 citations page were not accessible through the web tool.
The conventional `ADS_TOKEN`, `ADS_API_TOKEN` and `NASA_ADS_TOKEN` environment variables
were unset. I did not search credential stores, create credentials or contact anyone;
no authenticated ADS API search was run. ADS primary PDFs also failed through the web
tool for the Kato and Cannizzo conference leads. These are actual access failures,
not evidence that ADS contains no relevant work.

Aalto's PDF initially failed in the restricted shell, while the web parser exposed its
text. A permitted network retrieval then succeeded and supplied the hash and rendered
split check. Some initial OpenAlex access attempts failed, then the API returned
HTTP 200 for the retained lookups and citation query. No failed response is counted as a
negative literature result.

A10l correctly retracts “first held-out forecast.” Its description of the closest
precedent is independently confirmed, with one precision change: replace “nothing was
preregistered or probabilistic” by “no preregistration or scored probabilistic onset
distribution is reported.” A stochastic fitting algorithm is not the same object as a
probability forecast. The independent search materially improves A10l's unresolved
forward-citation check through the 68-record CM92 title screen and the explicit zero-indexed
V363 record. It does not repair OpenAlex's coverage of conference/observer literature.

The checked repository exposes A10l's narrative search summary, not an exact A10l query
export or hit table. Its reported approximate search counts are therefore inherited
statements, not independently reproduced counts. A01 and the older search log also
contain superseded, broader novelty language; current wording must cite the corrected
A10l/A10m findings. No broad “no machine-learning forecasting exists” statement survives.

## Protected-outcome boundary and stopping rule

No archive adapter, new light curve, model or AAVSO data endpoint was used. Search-engine
snippets nevertheless exposed two unsolicited SS Cyg outcome summaries: an unopened
public notebook at `biswajit1999.github.io/daily-astro-notebooks/` explicitly concerning
later data, and an unopened publisher result for the 2022 paper
[*Discovery of extreme, roughly daily superflares on the recurrent nova V2487 Oph*](https://academic.oup.com/mnras/article/512/2/1924/6540979)
containing an SS Cyg aggregate with an unspecified historical span.
Neither source's outcome values, counts or summaries are retained in these audit files.
The parent reviewer was informed of both exposure channels. Subsequent broad queries
were narrowed to publication sources and often excluded SS Cyg; no protected data access
was pursued or authorized.

Stop here: the closest forecasting source, the important precursor study and a bounded
independent synonym/citation search are enough to defend the qualified novelty candidate.
The highest-value later improvement is an ADS citation export and retrieval of the
Russian precursor paper, not more repetitions of broad web queries. These would improve
coverage; neither is necessary to state accurately what this search found.

Search and source receipts are indexed in
[`a10m_novelty/sources.json`](../../data/provenance/a10m_novelty/sources.json), with local receipt hashes in
[`a10m_novelty/sha256.json`](../../data/provenance/a10m_novelty/sha256.json). No universal negative result,
new empirical finding, publication authorization or change to the frozen comparison is
claimed.
