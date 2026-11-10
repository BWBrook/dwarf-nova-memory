# OJAp fit and house-style comparison

10 November 2026. Barry chose *The Open Journal of Astrophysics* (OJAp; D049).

A Claude Sonnet subagent compared the article (at `7a736d5`) with OJAp's author guidance and five
recent OJAp papers. Claude (Opus 5.5) verified the policy texts at source and confirmed each paper's
OJAp journal reference through the arXiv API. This note is the working reference for the OJAp
revision. Word counts are approximate, from `pdftotext`.

**Verdict:** a reasonable fit.
- OJAp's scope lists cataclysmic variables under astro-ph.SR.
- It publishes null and inconclusive results.
- It states no length limit.

The draft departs from house style in layout and framing, but no stated policy blocks it.

## OJAp requirements

**Stated policy** (author guidance on <https://astro.theoj.org/>; ethics page
<https://astro.theoj.org/pages/390-ethics>):

- **Route.** Post to arXiv first (CC BY), then submit through Scholastica
  (<https://app.scholasticahq.com/submissions/oja/new>). The accepted version must be on arXiv.
  Peer-reviewed, free to authors, no copy-editing.
- **Template.** A LaTeX class (`openjournal`) is linked from the journal site. It is preferred for
  the final version, not required at first submission. Any published OJAp paper's arXiv source can
  serve as a template.
- **Generative AI** (verified by Claude):
  - There is no blanket ban.
  - Use must be declared in the acknowledgments.
  - Where AI is used for calculation, analysis or data visualisation, the paper must give an account
    of how those methods were tested and validated.
  - Direct evidence of AI use, such as hallucinated references or leftover prompts, leads to
    rejection.
- **Authorship.** Authors must have contributed substantially.
- **arXiv's posted policy (2023)** says generative AI tools should not be listed as authors. OJAp
  publishes the arXiv copy, so this binds us. Verified by Claude.
- **Self-plagiarism.** The ethics page treats reuse of one's own published text as a breach. Check
  any text shared with the Zenodo protocol deposit.
- **Not stated:** length or abstract limits, keywords, the handling of supplements versus
  appendices, data-availability format, and reference style. The site links data-publication best
  practices (Chen et al. 2022).

**Inferred from practice:**
- two-column `openjournal` layout with an arXiv-style version header;
- no line numbers;
- figures inline;
- AAS-like subject headings on some papers;
- mostly AAS author-year references.

## The five comparison papers

OJAp has published no dwarf-nova or CV outburst-statistics paper that the arXiv journal-reference
search found. That search is incomplete, because it depends on authors filling in the field. These
are the nearest neighbours:

| arXiv | Year | Paper | Why comparable |
|---|---|---|---|
| 2408.06404 | 2025 | Optical spectroscopy and photometry of the X-ray bursting system UW CrB | Accreting compact binary; observational |
| 2506.20505 | 2025 | Symbiotic star candidates in Gaia DR3 | Accreting white-dwarf binaries; archive selection with a classifier |
| 2606.01496 | 2026 | Information content of quasar variability light curves | Stochastic-model inference, simulation-based precision planning, scoring rules, decades-long light curves; closest in method |
| 2512.24936 | 2026 | Searching for periodicity in FRB 20240114A | Short null-result timing paper with injection–recovery sensitivity |
| 2606.08319 | 2026 | Fast transients in archival photographic plates | Century-scale archive. Use for archive style only; the topic is contested |

## Comparison

| Dimension | Our draft (7a736d5) | Five OJAp papers |
|---|---|---|
| Layout | A4, single column, 1.25 spacing, line numbers | US letter, two columns, no line numbers |
| Length | 13 pages, about 5,100 words with references; separate 18-page supplement of about 7,000 words | 5–18 pages, 2,700–12,000 words, one self-contained PDF |
| Abstract | About 255 words | 97–245 words, two near 100 |
| Keywords | None | Subject headings (one to three terms) on three of five |
| Front matter | Draft banner under the title; AI collaborators on the byline (removed under D049) | Human authors and affiliations |
| Sections | Five numbered sections with subsections | Introduction, data, methods, results, conclusions; at most one appendix |
| Methods | About half a page in the main text; the rest in the supplement | In the main text throughout |
| Voice | About 2 "we" per 1,000 words; repeated qualifications and many "not X" constructions | 6–16 "we" per 1,000 words; similar hedge-word density (2–3 per 1,000; 6.6 in the null-result paper) |
| Figures | 4, collected at the end, one per page, long captions | 2–17, inline |
| Tables | 1 evidence-status table and 1 assumptions table | 0–6 |
| Equations | None in the main text | 0–35 numbered; the quasar-variability paper leads with equations |
| References | About 34, Chicago author-date | 14–95, AAS style |
| End matter | Methods in brief; roles of AI systems and humans; data and code | Acknowledgments; three of five add software or data sections; none has an AI statement or author-contributions section |

## Incongruities, ranked by importance for acceptance and readability

1. **AI on the byline, and where the AI statement goes.** Resolved by D049: Barry is sole author,
   and the acknowledgments hold a placeholder for the declaration. The declaration must include the
   testing and validation account.
2. **Methods in a separate supplement.** Referees read one PDF. Move the essential methods into the
   main text: the extractor, the lognormal clocks, the working score and the freeze protocol. The
   rest become appendices in the same PDF, or arXiv ancillary files.
3. **Qualification structure.** The comparison papers state a result and a limitation once, in
   plain prose. Shorten the abstract to about 200 words, and fold Table 1 (the evidence-status
   table) into the discussion.
4. **Format.** Use the `openjournal` class, figures inline and no line numbers for the arXiv
   version.
5. **References and source.** Switch to AAS author-year style. Keep the claim-binding spans, which
   do not render, out of any LaTeX source posted to arXiv. Give the two inline-only citations
   (Hempelmann and Kurths 1990; Grigorievskiy et al. 2014) verified entries.
6. **Missing conventions.** Add two or three equations defining the score and the clocks, subject
   headings, and a software and data section in house form. Consider a model schematic.
7. **Draft banner.** Remove the draft line and the release note under the title.

## Reassuring points

- Cataclysmic variables are explicitly in scope.
- Null and inconclusive results are published, and so are short papers.
- Simulation-based precision planning has direct precedent (2606.01496).
- OJAp permits generative AI with disclosure, and a public GitHub or Zenodo trail is welcome.
- None of the five papers carries an AI statement, so ours will be unusually prominent. It should
  be complete and plain.
