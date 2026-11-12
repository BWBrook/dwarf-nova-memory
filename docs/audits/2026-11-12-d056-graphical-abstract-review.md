# D056 graphical abstract: one focused revision before use

Codex, 12 November 2026. Base `5d6ae69`, responding to thread 159/3255.
Review only: the graphic, its generator, brief and evidence stay unchanged.

## Verdict and what to retain

The three-step story works: binary and real light curve, competing forecasters,
then the score comparison. The shared observation-year axis makes the block
results easier to follow. Retain that structure, the direct labels, the neutral
timeline, the blue overall interval and the orange duration emphasis. Keep the
current typeface. The headline can state the result plainly under D051; label
the plotted quantity as forecast-score gain so that “better” has an object.

I would give the graphic one focused revision before using it as a standalone
journal graphic. The principal changes are chronology, the 9% quantity and print
readability. Three shorter precision edits can be made in the same pass.

## Corrections and concrete replacements

| Priority | Location in `manuscript/figures.py` | Finding and action |
|---|---|---|
| P1 | Lines 732–754, timeline/lock | “Forecasters built” over 1910–1959 and “fixed and published” at 1960 read as the dates those acts occurred. These are observation years; construction, freezing and publication happened in 2026. Label the axis **“Years of observations”**, the first segment **“Fitted using 1910–1959”**, and the lock badge **“Frozen and published in 2026, before test records were opened”**. Put the badge off the dated axis, or make its relation to the data split explicit. Retain the 1960 split and 2018 unopened boundary. |
| P1 | Lines 767–770, 9% note | “Expects a 9% longer wait” loses C04's fixed-history, untruncated-median scope. The box depicts a forecast, which is conditioned on survival to issue, while the numerical contrast describes its underlying full quiet-gap clock. **Remove the 9% note from this graphic.** The brief already gives the correct explanation. This also removes the one percentage most likely to be read as forecast accuracy. If retained, use the brief's full definition, rather than another short “wait” paraphrase. |
| P2 | Essential labels throughout | The graphic contains about **191 words**. At its actual 16.6 cm placement, the smallest meaningful text is approximately **5.8 pt**. It is sharp, but slow to read at normal print size. Aim for roughly **100–120 words** and essential labels around **8 pt**, as a design target rather than a journal rule. Cut wording and use the released space; changing the font or resolution is unnecessary. |
| P2 | Lines 610–624, 705–716, examples | The 3/4-week numbers are correct for the displayed nightly-median runs. They are display spans/gaps, not X4 fitted durations, endpoints or issued forecasts. Call the panel **“Illustrative cycles from 1960 nightly data”**. In the caption, say **“The examples illustrate the question; the test uses all 441 forecasts.”** Keep the AAVSO credit and schematic-binary description. |
| P2 | Line 801, dot key | “Each dot: six years” is false for the final dot, which covers 2014–2017. Use **“Six-year periods; final period four years. Open dots: worse.”** The headline can say **“Better overall, and in 8 of 10 periods”**. The predeclared clustering and all plotted values remain unchanged. |
| P2 | Lines 805–808, footer | “Their early records were too patchy to repeat the test” turns a rule-dependent feasibility result into a broad cause/possibility claim. SS Aur passes the count gate and fails an operational morphology gate. Use **“Ten other stars: none passed the pre-set early-record checks.”** This preserves the failed screen without making a claim about every measurement model. |

The timeline correction is especially valuable. The paper's distinction between
historical observation dates and the 2026 sealed-access experiment should be
visible in the graphical abstract itself, without needing the surrounding prose.

## Design pass

- Remove the repeated question at the bottom of the star panel: the headline and
  brief title already supply it. Retain the binary, orange spans and blue gaps.
- Remove the 9% note and the “Next” footer. The hatched 2018-onward region already
  communicates the reserved observations. Keep the shorter other-stars result if
  it fits at the larger type size.
- Shorten the result qualifier to **“Small overall gain; 90% interval above zero.
  This met the pre-set criterion.”** Label the band **“Overall mean / 90% interval”**.
  This refers to one overall interval, rather than suggesting a sequence of
  intervals that “stayed” above zero throughout the test.
- Preserve the earlier decision to avoid a giant percentage. The central message
  is that adding length improved the specified forecasts; the parameter contrast
  is a separate explanation in the brief.
- Inspect the revised brief at normal page scale as well as enlarged. A 300-dpi
  export preserves sharp edges; physical text size controls reading effort.

The current two-page brief has no clipping, and page 2 has space. Its primary
result paragraph currently breaks across pages, splitting the full-quiet-spell
definition from “the next start, by about 9%.” After simplifying the graphic,
reflow so that the main result and its definition read together. This does not
need a new manuscript structure or smaller body type.

## Numerical and provenance check

A read-only delegate independently checked the public data and arithmetic; the
parent inspected the source, standalone image and both rendered brief pages.

- Block counts sum to **441**, with **8/10** positive block means. Their weighted
  mean is **0.016533512177436503 nats**, with CR1 SE **0.006320284834306242** and
  saved 90% interval **[0.00494771630959865, 0.028119308045274356]**.
- C04's ratio is **1.0880015159653311**, or **8.800151596533121%**, and its frozen
  parameter hash agrees. It is the untruncated median clock at fixed timing history.
- The illustrated runs are days **160–168** and **189–206**, with next bright-run
  starts at **189** and **234**. The display heuristic therefore gives **21** and
  **28** days exactly. It uses nightly medians at magnitude 10 or brighter and
  splits bright runs across gaps over three days; these are not X4 fits.
- The last block lasts **1,461.5 days**, compared with **2,191.5 days** for each of
  the preceding nine. Their midpoints and plotted gains agree with the saved data.

No regeneration from native records was used. The full `--generate` path still
reads retained raw inputs; these checks used the committed public aggregates.
The PDF/PNG/source hashes and copied evidence agree in `figures.py --check`.
The brief embeds the 2,221-pixel-wide PNG at about 340 ppi, approximately 165.9 mm
wide. Scaling the 6.6-pt source labels from the standalone PDF's 533.14-pt width
gives approximately 5.82 pt in the brief. Ignored render scratch is in
`outputs/d056_review/`.

## Placement and closure

The PDF and PNG are useful delivery formats. For OJAp, I found no separate
graphical-abstract specification in the [author guidance](https://astro.theoj.org/for-authors)
reviewed today; I therefore make no journal-specific acceptance claim from the
file format or resolution. Revise the chronology and print readability before
using it as the standalone journal summary. The existing release, authorship,
licence and credit decisions remain outside this design review.

D055's two methods clarifications now match the code/observation contract, and
the linked Heitjan–Rubin entry is present in the rendered article. That review is
closed; this critique concerns the new graphical abstract.

All 580 tests, seed/manuscript/claims/render and figure/table checks pass; claims
has zero errors and seven existing uncited warnings. All 26 frozen forecasting
source hashes agree. Both GitHub workflows passed on `5d6ae69`. No archive
request or native observation was used, and no model was fitted or forecast rescored. SS Cyg 2018 onward
and candidate-star 1990 onward remain closed. Only review/coordination records
change in this turn.

Next: Claude — make this single graphic revision, inspect it at the brief's
printed size, then hand the revised brief and graphic to Barry.
