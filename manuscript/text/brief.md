# Can an outburst help predict the next one?

Barry W. Brook (University of Tasmania), with Claude Opus 5.5 (Anthropic) and GPT-6 Codex (OpenAI). Draft of 2026-11-09; a plain-language summary of a living research repository, <https://github.com/BWBrook/dwarf-nova-memory>.

## The puzzle

SS Cygni is a pair of stars in the constellation Cygnus. A white dwarf pulls gas from its companion
into a flat, spinning disc. Every month or two the disc flares (astronomers say "outbursts"), and the system brightens about forty
times for one to two weeks before fading back. Astronomers call it a *dwarf nova*. Amateur
astronomers have recorded these flares by eye almost every clear night since 1896, building one of
the longest continuous records of any star.

The flares come at irregular intervals, and they come in two kinds: short ones of about a week and
long ones of about two weeks, which tend to alternate. For decades people have wondered whether a
flare leaves a trace that shapes the next one. Earlier studies found that longer flares tend to be
followed by longer quiet spells. Finding a pattern in a record you have already looked at is not
the same as being able to use it to predict.

<div id="figures"></div>

*Figure. The primary forecast comparison gained [0.0165]{.C01 .V001} log-score units per forecast; its interval is above zero. The later years and the frozen long/short rule remain inconclusive. This retrospective result followed a documented format repair after data access, and does not establish physical memory.[]{.C05}[]{.C07}[]{.C08}*

## Why it is hard

Patterns found after the fact are easy to over-read, and some of the old ones turned out to come
from how the intervals were measured. We fixed the forecasting rule before seeing the test years and replayed observations by their
reported dates; their historical arrival dates are unknown. We scored the whole
forecast, not just a best guess. We used a *log score*, which rewards a forecast for putting high
probability on what actually happened.

## What we did

- **Marked flares in the archive.** We used archived visual brightness estimates from the American Association
  of Variable Star Observers (AAVSO). A method tested first on simulated records estimated the starts and ends; it does not
  guarantee finding every flare.
- **Built two forecasters on 1910–1959 only.** When recorded observations confirmed an end, the first
  forecast the next start from recent quiet spells. The second also knew how long the flare had
  lasted.
- **Locked them, published the plan, then tested.** The rules and settings were frozen and published
  with a permanent identifier before the 1960–2017 records were opened. Both forecasters were then
  scored on [441]{.C01 .V004} forecasts.

## What we found

1. **Knowing the flare's length helped, a little but measurably.** The duration-aware forecaster
   scored [0.0165]{.C01 .V001} log-score units better per forecast, with a 90% range of
   [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}. This met the success rule set in advance. This
   corresponds to about [1.7]{.C02}% higher geometric mean likelihood of the recorded outcomes.
2. **The test was not perfectly clean, and we say so.** When the data were first requested, a
   formatting quirk in a field the forecasts never use crashed the software. We fixed the reader,
   checked that the fix changed no observation, and reran. The forecasting rules did not change.
   The failed attempt is kept on record[]{.C05}.
3. **Not every check agreed.** In the later years, 1993–2017, the gain was smaller and could not be
   told apart from zero[]{.C07}. A rule built on the short/long flare types was also inconclusive[]{.C08}.
   In analyses made after seeing the result, a long/short model fitted the record better than
   one using exact log duration. Adjusting the shared forecast level also changed the class rule's score. Those analyses
   cannot count as a second test.
4. **The result does not show what causes the effect.** A long flare may drain more gas from the
   disc and so change the next cycle. Alternatively, flare length may simply track a slow change in
   the disc that the quiet spells miss. Errors in the estimated end also affect both flare length and the next quiet spell. This test
   cannot separate these causes from all measurement effects.

## What it means

For SS Cygni, measured flare length improved forecasts from the archived record under these rules.
The gain is small, and its physical cause remains open.
Whether it holds for other stars of this kind, and in the years since 2018, is open. We have kept
the post-2017 archive records unopened for a possible future test, potentially combining several stars.

## How this work was done

Barry Brook set the direction and the data boundaries, and reviews and decides on release. Claude
(Anthropic) reviewed the literature and wrote the flare-finding method and these drafts. Codex
(OpenAI) built and ran the forecasting system and independently audited the results. A third AI,
GPT-6 Pro (OpenAI), produced the first ideas. Every number traces to the public repository.

## Sources

A historical sample of [705]{.C40} outbursts was analysed by @cannizzo1992LongtermBehaviorSS, and the disc was modelled by
@cannizzo1993AccretionDiskLimit.
