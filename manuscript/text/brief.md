# Does the length of a stellar outburst help forecast the next?

Barry W. Brook (University of Tasmania), with Claude Opus 5.5 (Anthropic) and GPT-6 Codex (OpenAI). Draft of 2026-11-11; a summary of <https://github.com/BWBrook/dwarf-nova-memory>.

## A star that flares every few weeks

SS Cygni is a pair of stars in which a white dwarf pulls gas from a companion into a surrounding
disc. Every seven weeks or so the disc heats up, and the system brightens about twentyfold for
one or two weeks before fading (Figure A). Amateur astronomers have recorded its brightness by eye
for well over a century, and the American Association of Variable Star Observers (AAVSO) holds
their reports. Long and short outbursts tend to alternate, and earlier work found that longer
outbursts tend to be followed by longer quiet spells [@cannizzo1992LongtermBehaviorSS].

We asked whether knowing how long an outburst lasted improves a forecast of when the next one
starts, beyond what the recent quiet spells already tell. Two ideas suggest it could. A long
outburst may drain more of the disc, which then takes longer to refill. Or outburst length may
track a slowly changing feeding rate that recent quiet spells capture only in part.

## A forecast test fixed in advance

We built two forecasters from the 1910–1959 observations. Both use the recent quiet spells; one
also uses the length of the outburst that has just ended. Whenever the reports show that an
outburst has faded, each forecaster spreads probability over the possible start dates of the next
one. We froze both, published the protocol online, and only then opened the observations from
1960–2017. A forecast earns more credit the more probability it placed on the start window that
the later reports revealed.

## Outburst length helped

Over [441]{.C01 .V004} forecasts, the forecaster that knew outburst length gained
[0.0165]{.C01 .V001} nats of log score per forecast (90% interval [0.0049]{.C01 .V002} to
[0.0281]{.C01 .V003}), passing the success rule set beforehand. On average it gave about
[1.7]{.C02}% more probability to what happened. It expected longer waits after longer outbursts:
doubling an outburst's length moved its typical forecast wait about [9]{.C04}% later. The gain is
about a seventh of what knowing the recent quiet spells adds,[]{.C02} and it was positive in
[eight]{.C25} of the ten six-year blocks (Figure B).

After an external review, we re-timed the outbursts in other ways. Scoring against single
estimated start dates gave a similar gain, [0.0154]{.C44} nats. Start windows rebuilt directly
from observers' reports gave smaller gains, [0.0075]{.C55 .V009} and [0.0043]{.C55 .V013} nats,
with intervals that include zero.

<div id="figures"></div>

*Figure. (A) SS Cygni's nightly brightness through 1960, the first year of the test; the dotted
line is the threshold that defines an outburst. (B) The gain from knowing outburst length in each
six-year block of 1960–2017; the blue line and band show the overall gain and its 90% interval.*

## Could other stars be tested?

Before opening their early records, we froze a screen of ten other dwarf novae, the class of star
SS Cygni belongs to. None had pre-1990 records that qualified for the same test.[]{.C68} The test
needs unbroken watching across two successive cycles, and most of these stars are fainter than SS
Cygni and were watched less continuously. In the 1980s SS Cygni's record gave [67]{.C70} usable
forecasts for [73]{.C70} outbursts; the ten others together gave [102]{.C70} for [485]{.C70}.
Their later records, and automated sky surveys, may supply more.

## What would tell the two ideas apart

Both ideas fit the result. Forecasts that also include an independent measure of the disc's state,
such as its brightness between outbursts or its X-ray output, could separate them: if outburst
length stops helping once the state is known, the feeding-rate idea gains support; if it keeps
helping, the draining idea does. The frozen forecasters can also be scored on SS Cygni's
observations from 2018 onward, which remain unopened.

## Limits

- The score rewards probability placed on start windows that software estimated from the reports.
  Turning it into skill at predicting the true start needs a tested model of when observers look
  and report.
- An outburst's length and the following quiet spell share one estimated end time, and observers
  may watch more closely when the star is active. Both could tie outburst length to timing.
- The re-timing checks were designed after the result and reuse the opened data.
- A documented repair to the data reader followed the first data access, before any forecast was
  scored.[]{.C05}
- The result concerns one star.

## How this work was done

Barry Brook set the direction and access rules and decides release. GPT-6 Pro supplied the initial
ideas and an external review. Claude Opus 5.5 reviewed the literature, built the outburst finder
and drafted the current article and brief. GPT-6 Codex built and ran the forecasts and
independently checked the results, the later diagnostics and the drafts. The repository keeps the
frozen calculation, every correction and the evidence behind each claim.

## Sources

@cannizzo1992LongtermBehaviorSS analysed the historical duration–gap relation;
@cannizzo1993AccretionDiskLimit modelled the disc cycle. The protocol is archived at
<https://doi.org/10.5281/zenodo.24053338>.
