# Literature search log

**Search date and cut-off:** 2026-11-05. **Purpose:** seed a reproducible research project, identify close precedents, and prevent inflated novelty claims. This is a targeted review, not a systematic review with complete database coverage.

## Sources and strategy

General scholarly web search used two search systems, including the higher-recall system for primary-source verification and current literature. Primary journal pages, author arXiv manuscripts, original scanned papers, author institutional repositories, and primary catalogue documentation were preferred. Search-engine results were followed to the source where accessible. Indexed sections of a primary article are identified separately from a fully retrieved article.

Representative queries included:

- `"dwarf nova" "memory" outbursts SS Cyg recurrence`
- `"SS Cyg" outburst recurrence statistical long term Cannizzo`
- `"RU Peg" outburst recurrence long term analysis`
- `"dwarf novae" prediction outbursts machine learning 2025 2026`
- `"dwarf nova" "forecasting" outbursts`
- `"dwarf nova" "predicting" outbursts`
- `"dwarf nova" "forecast" OR "prediction" OR "memory"` with a recent-year filter
- `"dwarf novae" "recurrence" "2026"` with a recent-year filter
- Exact-title and author searches for the DIM reviews, both 2016 catalogues, historical SS Cyg/VW Hyi work, RU Peg, supercycle changes, and the 2026 leads.

The recent-year filters were used to find recent work, not to estimate total publication counts. Searches were expanded backward from relevant abstracts and bibliographies. No complete forward-citation enumeration, ADS query export, or deduplicated systematic-review screening table was produced. The evidence register is a list of included sources, not a count of every search hit.

## Included records and inspection labels

The seed includes 25 astronomy records and five methodological records. Each has a stable citation key and evidence row. `Full_text_sections` means relevant portions were inspected, not an independent replication of all methods or figures. Abstract-only records support only the reported abstract-level claims. Bibliographic-only records are reading tasks and do not support adopted empirical results.

The five methods entries were verified by the parallel methods-review agent using journal, author, or arXiv pages. Their evidence rows identify that provenance. No connection between those methods and established dwarf-nova practice is implied by their inclusion.

## Important access and version limitations

1. **Hempelmann and Kurths (1990):** bibliographic details were checked against the author’s institutional publication list, and the abstract against an author-uploaded record. The original ADS/scan routes did not provide readable full text during this pass. Full methods are a high-priority retrieval task; the review reports the authors’ memory claim without endorsing it.
2. **Cannizzo and Mattei (1992, 1998):** metadata checked through an author-associated AAVSO bibliography and cited scholarly records. Original articles were not retrieved. The 1998 DOI is recorded as a bibliographic lead, not as evidence of inspected content. No numerical result is imported from secondary summaries.
3. **Cannizzo et al. (2012):** a NASA-hosted earlier manuscript describes a shorter Kepler baseline than the final arXiv/journal record. Use the final record for reproduction and explicitly record a version if using the older draft. Do not mix event counts or author order between versions.
4. **Two 2016 catalogues:** Coppejans et al. (`stv2921`, 722 dwarf novae) and Otulakowska-Hypka et al. (`stw1120`) are distinct. The former’s recurrence summary is not a complete exact event sequence.
5. **Hameury review:** arXiv first submission is 2019; journal publication is 2020. **Šimon RU Peg:** arXiv first submission is 2021; journal publication is 2022. **Kato IW And:** online publication is 2018; issue year is 2019. The bibliography uses journal years.
6. **Medagangoda et al. (2026):** publisher records first online publication on 11 June 2026; search-index dates are not used as the scientific publication date.
7. **Tsuranova et al. (2026):** publisher English page labels the journal *Astronomy Reports* while giving volume 103, issue 8, pages 1135–1146 and DOI `10.7868/S3034518926080062`. The original-language and translated-edition metadata need reconciliation. The BibTeX record is deliberately `@misc` with a note, avoiding invented edition metadata. Full Russian text was not inspected.

## Follow-up search tasks before a novelty claim

- Retrieve the original historical SS Cyg articles and record extraction thresholds, date windows, hypotheses, null models, and uncertainty methods.
- Run forward/backward ADS citation chains for Bath and van Paradijs (1983), Hempelmann and Kurths (1990), Cannizzo and Mattei (1992/1998), Ak et al. (2002), and Šimon (2022).
- Search JAAVSO, JBAA, and original observer publications for event sequence analyses, recurrence changes, and forecast attempts not well indexed by broad web search.
- Include synonyms such as waiting time, relaxation oscillator, O–C, recurrence-time distribution, regime switching, nonlinear dynamics, long-term activity, transfer-rate variation, precursor, and renewal process.
- Audit predictive claims for availability of each predictor at the forecast time, smoothing leakage, event selection, time-blocked validation, calibration, and comparison with changing-rate baselines.
- Read critiques and follow-up work on superoutburst mechanisms before framing a particular model as settled.
- Verify target classifications and source overlap after the actual pilot sample is selected; classification/discovery machine learning is not equivalent to next-outburst forecasting.
- Deduplicate preprint/journal records and original-language/translation editions; maintain access status and exact versions in the evidence register.

## Exclusions and unresolved leads

Thermonuclear classical/recurrent nova forecasts were not treated as dwarf-nova forecasting evidence. Classification-only machine learning was treated as adjacent methodology. Helium accretors, magnetic systems, and specialized SU UMa/ER UMa questions were not pooled with the proposed ordinary hydrogen-rich pilot.

Useful additional leads include Ak, Ozkan, and Mattei (2001), *Solar-type cycles of the secondary stars in cataclysmic variables*, DOI `10.1051/0004-6361:20010167`; the critique/follow-up literature to Osaki and Kato’s 2013 interpretation; and recent helium-system work such as the 2026 KL Dra study. These are follow-up leads, not fully reviewed included records.

Absence from this seed is not evidence that a study does not exist. No priority or exhaustiveness claim should be based on this search alone.

## A10m independent novelty check, 9 November 2026

Codex independently checked the narrowed C41 claim after the first drafts.
The exact 43 queries and their independent/reconciliation phases are in
`data/provenance/a10m_novelty/search_receipt.json`; the source appraisal is
`docs/audits/2026-11-09-a10m-novelty-review.md`. Twenty queries preceded reading
A10l's search memo. The V363 Lyr proceedings PDF and Price preprint were
source-checked. OpenAlex returned 68 CM92 citing records, all screened by
title/identifier, with duplicate versions retained; its V363 record indexed
zero forward citations. This is not an exhaustive full-text citation screen.
ADS was inaccessible. Observer/non-English publications and several full texts,
including Tsuranova et al. (2026), remain incomplete. No unverified methods
are treated as source-verified exclusions.

The search found no prior preregistered probabilistic held-out dwarf-nova
recurrence evaluation or explicit held-out duration-addition comparison among
located and checked sources. This supports a bounded search account and a
qualified "to our knowledge" priority sentence, not universal absence. The
V363 precedent is a held-out point-forecast study; its stochastic fitting
runs are distinct from a scored predictive onset distribution. Unsolicited
outcome snippets encountered during discovery are separately disclosed in
`docs/outcome-access-ledger.md`; no new photometry was requested.
