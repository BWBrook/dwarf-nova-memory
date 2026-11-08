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

*Figure. The primary forecast comparison gained [0.0165]{.C01 .V001} log-score units per forecast; its interval is above zero. The later years and the frozen long/short rule remain inconclusive. This retrospective result followed a documented format repair after data access, and does not establish physical memory. []{.C05} []{.C07} []{.C08}*

## Why it is hard

Patterns found after the fact are easy to over-read, and some of the old ones turned out to come
from how the intervals were measured. A fair test has to make a forecast using only what was known
at the time. It has to fix the forecasting rule before seeing the test years, and score the whole
forecast, not just a best guess. We used a *log score*, which rewards a forecast for putting high
probability on what actually happened.

## What we did

- **Found every flare.** We used archived visual brightness estimates from the American Association
  of Variable Star Observers (AAVSO). A method tested first on simulated records marked when each
  flare began and ended.
- **Built two forecasters on 1910–1959 only.** At the moment each flare ended, the first forecast when
  the next would start, from the recent quiet spells. The second also knew how long the flare had
  lasted.
- **Locked them, published the plan, then tested.** The rules and settings were frozen and published
  with a permanent identifier before the 1960–2017 records were opened. Both forecasters were then
  scored on [441]{.C01 .V004} forecasts.

## What we found

1. **Knowing the flare's length helped, a little but measurably.** The duration-aware forecaster
   scored [0.0165]{.C01 .V001} log-score units better per forecast, with a 90% range of
   [0.0049]{.C01 .V002} to [0.0281]{.C01 .V003}. This met the success rule set in advance. Averaged
   the way forecasters average (a geometric mean), it put about [1.7]{.C02}% more probability on
   what actually happened.
2. **The test was not perfectly clean, and we say so.** When the data were first requested, a
   formatting quirk in a field the forecasts never use crashed the software. We fixed the reader,
   checked that the fix changed no observation, and reran. The forecasting rules did not change.
   The failed attempt is kept on record []{.C05}.
3. **Not every check agreed.** In the later years, 1993–2017, the gain was smaller and could not be
   told apart from zero []{.C07}. A rule built on the short/long flare types was also inconclusive
   []{.C08}. Analyses done after the result suggest the flare's type matters more than its exact
   length. They also suggest the type rule was handicapped by how it was set up. Those analyses
   cannot count as a second test.
4. **The result does not show what causes the effect.** A long flare may drain more gas from the
   disc and so change the next cycle. Alternatively, flare length may simply track a slow change in
   the disc that the quiet spells miss. This test cannot tell those ideas apart.

## What it means

For SS Cygni, a finished flare carries real information about when the next will start. That
information is small, and it was measured under strict rules that guard against fooling ourselves.
Whether it holds for other stars of this kind, and in the years since 2018, is open. We have kept
the post-2017 records unopened for a future test that combines several stars.

## How this work was done

Barry Brook set the direction and the data boundaries, and reviews and decides on release. Claude
(Anthropic) reviewed the literature and wrote the flare-finding method and these drafts. Codex
(OpenAI) built and ran the forecasting system and independently audited the results. A third AI,
GPT-6 Pro (OpenAI), produced the first ideas. Every number traces to the public repository.

## Sources

Cannizzo and Mattei (1992) analysed SS Cygni's first 705 recorded flares [@cannizzo1992LongtermBehaviorSS];
Cannizzo (1993) modelled the disc [@cannizzo1993AccretionDiskLimit].
